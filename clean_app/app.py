import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import streamlit.components.v1 as components

from simulation.raster_utils import load_raster, normalize
from simulation.ca_model import run_simulation

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wildfire Spread Simulator",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;
        border: 1px solid #e94560;
    }
    .main-header h1 { color: #ff6b35; margin: 0; font-size: 2.4rem; }
    .main-header p  { color: #adb5bd; margin: 0.5rem 0 0 0; font-size: 1rem; }
    .stat-card {
        background: #1e1e2e; border-radius: 8px; padding: 1rem;
        text-align: center; border: 1px solid #333;
    }
    .stat-value { font-size: 1.8rem; font-weight: 700; color: #ff6b35; }
    .stat-label { font-size: 0.8rem; color: #adb5bd; text-transform: uppercase; letter-spacing: 0.05em; }
    .section-header {
        background: #1e1e2e; border-left: 4px solid #ff6b35;
        padding: 0.6rem 1rem; border-radius: 0 8px 8px 0; margin: 1rem 0 0.5rem 0;
    }
    .section-header h3 { color: #ff6b35; margin: 0; font-size: 1rem; }
    .stButton > button {
        background: linear-gradient(135deg, #e94560, #ff6b35);
        color: white; border: none; border-radius: 8px;
        font-weight: 600; font-size: 1.1rem; width: 100%;
        padding: 0.75rem; transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔥 Wildfire Spread Simulator</h1>
    <p>Cellular Automata model — tune wind, slope, fuel weights, ignition point, firebreaks & weather presets</p>
</div>
""", unsafe_allow_html=True)

# ─── Data loading ─────────────────────────────────────────────────────────────
BASE = os.path.join(os.path.dirname(__file__), "data", "real_demo_data")

@st.cache_data
def load_data():
    wind  = normalize(load_raster(os.path.join(BASE, "wind.tif")))
    slope = normalize(load_raster(os.path.join(BASE, "slope.tif")))
    fuel  = normalize(load_raster(os.path.join(BASE, "fuel.tif")))
    grid  = load_raster(os.path.join(BASE, "initial_fire.tif"))
    return wind, slope, fuel, grid

try:
    wind, slope, fuel, initial_grid = load_data()
    data_ok = True
except Exception as e:
    st.error(f"❌ Could not load raster data: {e}")
    st.info("Make sure the `data/real_demo_data/` folder contains: wind.tif, slope.tif, fuel.tif, initial_fire.tif")
    data_ok = False

rows, cols = initial_grid.shape if data_ok else (100, 100)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── 1. Simulation basics ──────────────────────────────────────────────────
    st.markdown("## ⚙️ Simulation Controls")
    st.divider()

    iterations = st.slider("Iterations", 5, 100, 20, 5,
                           help="Number of time steps to simulate")
    interval_ms = st.slider("Animation Speed (ms/frame)", 50, 1000, 300, 50,
                            help="Lower = faster animation")
    seed = st.number_input("Random Seed", 0, 9999, 42, 1,
                           help="Same seed → same result every run")

    # ── 2. Weather Presets ────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🌤️ Weather Preset")
    preset = st.selectbox("Choose a preset (overrides weights below)", [
        "Custom", "Calm Day", "Windy Day", "Drought Conditions", "Extreme Wildfire"
    ])

    PRESETS = {
        "Calm Day":           {"base": 0.05, "wind": 0.10, "slope": 0.20, "fuel": 0.20},
        "Windy Day":          {"base": 0.10, "wind": 0.50, "slope": 0.20, "fuel": 0.20},
        "Drought Conditions": {"base": 0.15, "wind": 0.25, "slope": 0.25, "fuel": 0.55},
        "Extreme Wildfire":   {"base": 0.20, "wind": 0.45, "slope": 0.35, "fuel": 0.50},
    }

    # ── 3. Factor Weights ─────────────────────────────────────────────────────
    st.divider()
    st.markdown("### ⚖️ Spread Factor Weights")
    st.caption("These control how much each factor contributes to fire spreading.")

    if preset != "Custom":
        p = PRESETS[preset]
        w_base  = p["base"];  w_wind = p["wind"]
        w_slope = p["slope"]; w_fuel = p["fuel"]
        st.info(f"Preset **{preset}** applied. Switch to Custom to edit manually.")
    else:
        w_base  = st.slider("Base Ignition Probability", 0.0, 0.5, 0.10, 0.01,
                            help="Minimum chance fire spreads even with no wind/slope/fuel")
        w_wind  = st.slider("Wind Weight",  0.0, 1.0, 0.30, 0.05,
                            help="How much wind contributes to fire spread")
        w_slope = st.slider("Slope Weight", 0.0, 1.0, 0.30, 0.05,
                            help="How much uphill slope accelerates fire")
        w_fuel  = st.slider("Fuel Weight",  0.0, 1.0, 0.30, 0.05,
                            help="How much vegetation/fuel density affects spread")

    weights = {"base": w_base, "wind": w_wind, "slope": w_slope, "fuel": w_fuel}
    total_w = w_wind + w_slope + w_fuel
    st.caption(f"Max possible spread probability: `{min(w_base + total_w, 1.0):.2f}`")

    # ── 4. Custom Ignition Point ──────────────────────────────────────────────
    st.divider()
    st.markdown("### 🔥 Custom Ignition Point")
    use_custom_ignition = st.checkbox("Override default ignition point", value=False)
    if use_custom_ignition:
        ig_row = st.slider("Ignition Row (Y)", 1, rows - 2, rows // 2, 1)
        ig_col = st.slider("Ignition Col (X)", 1, cols - 2, cols // 2, 1)
        ig_radius = st.slider("Ignition Radius (cells)", 1, 10, 2, 1,
                              help="How many cells to set on fire initially")
    else:
        ig_row = ig_col = ig_radius = None

    # ── 5. Firebreak Tool ─────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🪓 Firebreak")
    st.caption("A firebreak is a cleared strip that blocks fire spread.")
    use_firebreak = st.checkbox("Add a firebreak", value=False)
    if use_firebreak:
        fb_orientation = st.radio("Orientation", ["Horizontal", "Vertical"])
        if fb_orientation == "Horizontal":
            fb_pos  = st.slider("Row position", 5, rows - 5, rows // 2, 1)
            fb_thickness = st.slider("Thickness (rows)", 1, 8, 3, 1)
        else:
            fb_pos  = st.slider("Column position", 5, cols - 5, cols // 2, 1)
            fb_thickness = st.slider("Thickness (cols)", 1, 8, 3, 1)
    else:
        fb_orientation = fb_pos = fb_thickness = None

    # ── 6. Layer preview ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🗺️ Layer Preview")
    preview_layer = st.selectbox("Preview input layer",
                                 ["None", "Wind", "Slope", "Fuel", "Initial Fire", "Risk Heatmap"])

    # ── 7. Legend ─────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("""
    **Legend**
    | | State |
    |-|-------|
    | 🟫 | Unburned |
    | 🔴 | Burning |
    | ⚫ | Burned |
    | 🟩 | Firebreak |
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER PREVIEW (sidebar)
# ═══════════════════════════════════════════════════════════════════════════════
if data_ok and preview_layer != "None":
    if preview_layer == "Risk Heatmap":
        # Combine layers into a risk score
        risk = w_base + w_wind * wind + w_slope * slope + w_fuel * fuel
        layer_data = np.clip(risk, 0, 1)
        cmap_prev = "hot"
        title_prev = "Fire Risk Heatmap"
    else:
        layer_map = {"Wind": wind, "Slope": slope, "Fuel": fuel, "Initial Fire": initial_grid}
        layer_data = layer_map[preview_layer]
        cmap_prev = "YlOrRd"
        title_prev = f"{preview_layer} Layer"

    fig_prev, ax_prev = plt.subplots(figsize=(4, 3.5))
    fig_prev.patch.set_facecolor("#1e1e2e")
    ax_prev.set_facecolor("#1e1e2e")
    im_p = ax_prev.imshow(layer_data, cmap=cmap_prev)
    ax_prev.set_title(title_prev, color="white", fontsize=10)
    ax_prev.axis("off")
    cb = plt.colorbar(im_p, ax=ax_prev, shrink=0.8)
    cb.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="white")
    st.sidebar.pyplot(fig_prev, use_container_width=True)
    plt.close(fig_prev)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ═══════════════════════════════════════════════════════════════════════════════
if not data_ok:
    st.stop()

# ── Build modified grid & firebreaks ──────────────────────────────────────────
def build_starting_grid():
    grid = initial_grid.copy()
    # Custom ignition point
    if use_custom_ignition and ig_row is not None:
        grid[grid == 1] = 0   # clear default fire
        for di in range(-ig_radius, ig_radius + 1):
            for dj in range(-ig_radius, ig_radius + 1):
                ni, nj = ig_row + di, ig_col + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    if di*di + dj*dj <= ig_radius*ig_radius:
                        grid[ni, nj] = 1
    return grid

def build_firebreaks():
    fb = np.zeros((rows, cols), dtype=bool)
    if use_firebreak and fb_pos is not None:
        if fb_orientation == "Horizontal":
            for t in range(fb_thickness):
                r = fb_pos + t - fb_thickness // 2
                if 0 <= r < rows:
                    fb[r, :] = True
        else:
            for t in range(fb_thickness):
                c = fb_pos + t - fb_thickness // 2
                if 0 <= c < cols:
                    fb[:, c] = True
    return fb

starting_grid = build_starting_grid()
firebreaks    = build_firebreaks()

# ── Top stat cards ────────────────────────────────────────────────────────────
n_burning = int((starting_grid == 1).sum())
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{rows}×{cols}</div><div class="stat-label">Grid Size</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{n_burning}</div><div class="stat-label">Ignition Cells</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{iterations}</div><div class="stat-label">Iterations</div></div>', unsafe_allow_html=True)
with c4:
    fb_count = int(firebreaks.sum())
    st.markdown(f'<div class="stat-card"><div class="stat-value">{fb_count}</div><div class="stat-label">Firebreak Cells</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Show current setup preview ────────────────────────────────────────────────
st.markdown("### 🗺️ Current Setup Preview")
st.caption("This updates live as you change settings — before running the simulation.")

setup_cmap = mcolors.ListedColormap(["#f5deb3", "#ff4500", "#1c1c1c", "#2ecc71"])
setup_norm = mcolors.BoundaryNorm([0, 1, 2, 3, 4], setup_cmap.N)

display_grid = starting_grid.copy().astype(float)
display_grid[firebreaks] = 3  # show firebreaks as green

fig_setup, ax_setup = plt.subplots(figsize=(6, 5))
fig_setup.patch.set_facecolor("#1e1e2e")
ax_setup.set_facecolor("#1e1e2e")
im_setup = ax_setup.imshow(display_grid, cmap=setup_cmap, norm=setup_norm)
ax_setup.set_title("Initial State (fire=red, firebreak=green)", color="white", fontsize=11)
ax_setup.axis("off")
cb_s = plt.colorbar(im_setup, ax=ax_setup, ticks=[0.5, 1.5, 2.5, 3.5], shrink=0.75)
cb_s.ax.set_yticklabels(["Unburned", "Burning", "Burned", "Firebreak"], color="white")
plt.tight_layout()
st.pyplot(fig_setup, use_container_width=True)
plt.close(fig_setup)

st.markdown("<br>", unsafe_allow_html=True)

# ── Run button ────────────────────────────────────────────────────────────────
run_col, _ = st.columns([1, 2])
with run_col:
    run_clicked = st.button("🔥 Run Simulation")

# ═══════════════════════════════════════════════════════════════════════════════
# SIMULATION + RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
if run_clicked:
    np.random.seed(int(seed))

    with st.spinner(f"Running {iterations} iterations..."):
        frames = run_simulation(
            starting_grid, wind, slope, fuel,
            iterations, weights,
            firebreaks=firebreaks if use_firebreak else None
        )

    final = frames[-1]
    total_cells   = rows * cols
    burned_cells  = int((final == 2).sum())
    burning_cells = int((final == 1).sum())
    unburned      = total_cells - burned_cells - burning_cells - int(firebreaks.sum())
    pct_affected  = round((burned_cells + burning_cells) / total_cells * 100, 1)

    st.success(f"✅ Simulation complete — {len(frames)} frames generated")

    # ── Result stat cards ─────────────────────────────────────────────────────
    st.markdown("### 📊 Final State Statistics")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{pct_affected}%</div><div class="stat-label">Area Affected</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{burned_cells:,}</div><div class="stat-label">Burned Cells</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{burning_cells:,}</div><div class="stat-label">Still Burning</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{unburned:,}</div><div class="stat-label">Unburned</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Animation ─────────────────────────────────────────────────────────────
    st.markdown("### 🎬 Fire Spread Animation")

    anim_cmap  = mcolors.ListedColormap(["#f5deb3", "#ff4500", "#1c1c1c", "#2ecc71"])
    anim_norm  = mcolors.BoundaryNorm([0, 1, 2, 3, 4], anim_cmap.N)

    # Overlay firebreaks on every frame
    anim_frames = []
    for f in frames:
        fd = f.copy().astype(float)
        if use_firebreak:
            fd[firebreaks] = 3
        anim_frames.append(fd)

    fig, ax = plt.subplots(figsize=(8, 7))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")
    img   = ax.imshow(anim_frames[0], cmap=anim_cmap, norm=anim_norm)
    title = ax.set_title("Step 0", color="white", fontsize=13, pad=10)
    ax.axis("off")

    cbar = plt.colorbar(img, ax=ax, ticks=[0.5, 1.5, 2.5, 3.5], shrink=0.75)
    cbar.ax.set_yticklabels(["Unburned", "Burning", "Burned", "Firebreak"], color="white")
    cbar.set_label("Fire Status", rotation=270, labelpad=18, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")

    def update(i):
        img.set_data(anim_frames[i])
        title.set_text(f"Step {i} / {len(anim_frames)-1}")
        return [img, title]

    ani = animation.FuncAnimation(fig, update, frames=len(anim_frames), interval=interval_ms, blit=True)
    with st.spinner("Rendering animation..."):
        html_anim = ani.to_jshtml()
    components.html(html_anim, height=880, scrolling=False)
    plt.close(fig)

    # ── Burn progression chart ────────────────────────────────────────────────
    st.markdown("### 📈 Burn Progression Over Time")

    burned_t  = [int((f == 2).sum()) for f in frames]
    burning_t = [int((f == 1).sum()) for f in frames]
    steps = list(range(len(frames)))

    fig2, ax2 = plt.subplots(figsize=(10, 3))
    fig2.patch.set_facecolor("#1e1e2e")
    ax2.set_facecolor("#1e1e2e")
    ax2.stackplot(steps, burned_t, burning_t,
                  labels=["Burned", "Burning"],
                  colors=["#1c1c1c", "#ff4500"], alpha=0.9)
    ax2.set_xlabel("Time Step", color="white")
    ax2.set_ylabel("Cells", color="white")
    ax2.tick_params(colors="white")
    for spine in ax2.spines.values():
        spine.set_edgecolor("#555")
    ax2.legend(loc="upper left", facecolor="#2a2a3e", labelcolor="white")
    plt.tight_layout()
    st.pyplot(fig2, use_container_width=True)
    plt.close(fig2)

    # ── Risk heatmap of actual spread ─────────────────────────────────────────
    st.markdown("### 🌡️ Spread Frequency Heatmap")
    st.caption("Shows which cells caught fire most consistently — brighter = higher risk area.")

    heat = np.zeros((rows, cols), dtype=float)
    for f in frames:
        heat += (f >= 1).astype(float)
    heat /= len(frames)

    fig3, ax3 = plt.subplots(figsize=(7, 6))
    fig3.patch.set_facecolor("#1e1e2e")
    ax3.set_facecolor("#1e1e2e")
    im3 = ax3.imshow(heat, cmap="hot", vmin=0, vmax=1)
    ax3.set_title("Fire Occurrence Frequency", color="white", fontsize=12)
    ax3.axis("off")
    cb3 = plt.colorbar(im3, ax=ax3, shrink=0.75)
    cb3.set_label("Fraction of steps on fire", color="white", rotation=270, labelpad=18)
    cb3.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cb3.ax.axes, "yticklabels"), color="white")
    plt.tight_layout()
    st.pyplot(fig3, use_container_width=True)
    plt.close(fig3)

else:
    st.info("👈 Configure settings in the sidebar, then click **🔥 Run Simulation** to start.")
