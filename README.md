# 🔥 Wildfire Spread Simulator

An interactive **wildfire propagation simulator** built with **Streamlit** and **Cellular Automata**, modeling how fire spreads across terrain using environmental factors like wind, slope, and fuel.

Designed for **real-time experimentation**, this tool allows users to dynamically control simulation parameters and visualize fire behavior step-by-step.

---

## 🚀 Live Demo

> *(http://localhost:8501)*

---

## 🧠 Core Concept

The simulation is based on a **Cellular Automata (CA)** model where each grid cell transitions between:

* 🟩 **Unburned (0)**
* 🔥 **Burning (1)**
* ⬛ **Burned (2)**

At each timestep:

* Burning cells turn into burned
* Neighboring cells ignite based on probability:

```
P = base + (wind × w₁) + (slope × w₂) + (fuel × w₃)
```

All environmental layers are normalized to `[0, 1]`.

---

## ✨ Features

### 🌤️ Weather Presets

Quickly simulate real-world scenarios:

* Calm Day
* Windy Day
* Drought Conditions
* Extreme Wildfire

---

### ⚖️ Dynamic Spread Control

Fine-tune fire behavior using sliders:

* Base ignition probability
* Wind influence
* Slope influence
* Fuel influence

---

### 🔥 Custom Ignition Point

* Select exact fire start location (row & column)
* Adjust ignition radius
* Override default fire map

---

### 🪓 Firebreak Tool

Simulate human intervention:

* Draw horizontal/vertical firebreak
* Adjustable position & thickness
* Blocks fire spread across selected region

---

### 🗺️ Live Simulation Preview

* Real-time grid preview before simulation
* Immediate visual feedback for all parameter changes

---

### 🌡️ Risk Heatmaps

* **Pre-simulation risk map** (based on weights)
* **Post-simulation spread frequency map**
  → highlights high-risk zones over time

---

### 📊 Burn Progress Visualization

```
Time →
|██████████░░░░░░░░░░|  Burning
|████████████████░░░░|  Burned
|████░░░░░░░░░░░░░░░░|  Unburned
```

* Stackplot showing fire evolution over time
* Tracks % burned, burning, and safe zones

---

### 📈 Real-time Statistics

* Grid size
* Burned area (%)
* Burning cells
* Remaining safe area

---

## 🛠️ Tech Stack

* **Frontend/UI:** Streamlit
* **Simulation Engine:** Python (NumPy, Cellular Automata)
* **Geospatial Data:** Rasterio (GeoTIFF processing)
* **Visualization:** Matplotlib
* **Deployment:** Streamlit Community Cloud

---

## 📁 Project Structure

```
fire_spread_app/
├── app.py                      # Main Streamlit app (UI + controls)
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── .gitignore                 # Ignore data & venv
├── .streamlit/
│   └── config.toml            # Theme & config
├── simulation/
│   ├── ca_model.py            # Fire spread logic (CA model)
│   └── raster_utils.py        # Raster loading & normalization
└── data/                      # ⚠️ NOT included in repo
    └── real_demo_data/
        ├── wind.tif
        ├── slope.tif
        ├── fuel.tif
        └── initial_fire.tif
```

---

## ⚠️ Dataset Setup

Due to size constraints, the dataset is not included in the repository.

### 📥 Download:

> *(Add your Google Drive / Hugging Face link here)*

### 📂 Place files in:

```
data/real_demo_data/
```

---

## 💻 Local Setup

```bash
git clone https://github.com/jayeshxgit/FIRE_spread_simulation.git
cd FIRE_spread_simulation

pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deployment (Free)

Using **Streamlit Community Cloud**:

1. Push code to GitHub
2. Go to: https://share.streamlit.io
3. Click **New App**
4. Select repo → `app.py`
5. Deploy 🚀

---

## 🎯 Key Highlights

* Interactive simulation with real-time controls
* Combines **environmental modeling + UI engineering**
* Clean separation of **logic (CA model)** and **interface (Streamlit)**
* Scalable for research, visualization, or ML integration

---

## 🧪 Future Improvements

* Satellite data integration
* Real-time weather API
* ML-based fire prediction
* Multi-region simulation
* GPU acceleration

---

## 🤝 Contributing

Contributions are welcome!
Feel free to open issues or submit pull requests.

---

## 📜 License

*(Add license if needed)*

---

## 👨‍💻 Author

**Jayesh Kapoor**

---

## 🔥 Final Note

This project combines:

* simulation
* visualization
* interactive controls

Making it a strong portfolio piece for:

* hackathons
* internships
* real-world modeling systems
