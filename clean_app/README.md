# 🔥 Wildfire Spread Simulator

A Streamlit app that simulates wildfire spread using Cellular Automata, accounting for wind, slope, and fuel conditions.

## Features
- Interactive controls for iterations, animation speed, and random seed
- Real-time burn statistics (% area affected, burned/burning/unburned cells)
- Animated visualization rendered in-browser
- Burn progression chart over time
- Layer preview for each input raster (wind, slope, fuel, initial fire)

## Project Structure
```
fire_spread_app/
├── app.py                        # Main Streamlit application
├── requirements.txt
├── .streamlit/
│   └── config.toml               # Theme & server config
├── simulation/
│   ├── ca_model.py               # Cellular automata logic
│   └── raster_utils.py           # Raster loading & normalization
└── data/
    └── real_demo_data/
        ├── wind.tif
        ├── slope.tif
        ├── fuel.tif
        └── initial_fire.tif
```

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud (Free)

1. Push this folder to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo
4. Set **Main file path** to `app.py`
5. Click **Deploy** — done!

> ⚠️ Make sure the `data/real_demo_data/` folder is committed to the repo (the `.tif` files must be included).

## How the Model Works

Each cell in the grid has one of three states:
- **0** — Unburned
- **1** — Burning  
- **2** — Burned

At each time step, every burning cell:
1. Transitions to "burned"
2. May ignite each unburned neighbour with probability:  
   `P = 0.1 + 0.3×wind + 0.3×slope + 0.3×fuel`

Input rasters (wind, slope, fuel) are normalized to [0, 1].
