# 🌿 Atmo Sync: Carbon Footprint & Decarbonization Platform

Atmo Sync is a mobile-responsive, beautifully designed, and data-driven Flask web application that maps global grid emissions in real-time, quantifies individual carbon output, and demonstrates the mathematical and thermodynamic foundations of climate action.

---

## 🚀 Key Features

* **🎨 Humble Nature Light Theme**: A simple, accessible, high-contrast visual design system. It uses a warm cream/beige background (`#faf8f5`), rich forest charcoal headings (`#1c2d24`), and fresh mint/emerald accents (`#10b981`). Highly readable for kids and adults alike.
* **🍁 Leaf Particle Smoke Animation**: Green leaves (`🍃`, `🌱`, `🌿`) drift smoothly upward like natural "smoke" from the circular calculator gauge, representing carbon absorption. A calculation puff is emitted on every slider change.
* **🌧️ Dynamic Weather & Rain Simulator**: Integrates an HTML5 Canvas-based real-time weather simulator in the page background. Features five distinct atmospheric presets (Sunny Glow, Windy Breeze, Misty Fog, Heavy Rain, and Severe Storm with active lightning) that can be manually overridden via a dashboard controller or toggled to **Auto Sync** mode to bind background weather dynamically to your personal carbon calculator footprint. Simulation settings are saved in `localStorage` for visual consistency across all sub-pages.
* **⚡ Live Grid Decarbonization Monitor**: Displays real-time grid intensity data (gCO₂e/kWh) and power mixes directly from the National Grid ESO.
* **🌐 Dynamic Sub-Regional Global Map**: Renders an interactive global map utilizing **Leaflet.js** and **CartoDB Dark Matter** dark tiles. Coordinates map **32 distinct regional nodes** across 10 countries (India, China, USA, France, Germany, Brazil, Japan, Australia, Nigeria, and Egypt) adjusting live country-level data from the **Green Web Foundation API** using localized scaling factors.
* **📊 Global CO₂ Atmospheric Tracker**: Displays live global CO₂ concentration (ppm) from the NOAA Mauna Loa observatory in a dashboard card, keeping users aware of the atmospheric baseline.
* **🧸 Child-Friendly Education (Learn Section)**: Educational concepts are explained using interactive kid-friendly analogies, such as "dirty footprints on a clean green lawn," "the Earth's cozy thermal blanket getting too thick," and "direct vs. indirect smoke."
* **🧮 Solutions Math Engine**: Documents the thermodynamic physics of decarbonization (COP of heat pumps, thermodynamic efficiency of ICE vs. EV, livestock enteric methane), displaying dynamic math formulas based on user inputs.

---

## 📐 Load Balancing & Production Scaling

To support high-concurrency client traffic ("audience trafficking") and ensure resilient performance under heavy load, Atmo Sync is architected with a production-grade multi-process load balancer design:

```
                  ┌───────────────────────────────┐
                  │      Incoming Web Traffic     │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │    Nginx Reverse Proxy /      │
                  │        Load Balancer          │
                  └───────────────┬───────────────┘
                                  │ (least_conn routing)
            ┌─────────────────────┼─────────────────────┐
            ▼                     ▼                     ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│  Gunicorn Worker 1    │ │  Gunicorn Worker 2    │ │  Gunicorn Worker 3    │
│  (Port 5000, App)     │ │  (Port 5000, App)     │ │  (Port 5000, App)     │
└───────────┬───────────┘ └───────────┬───────────┘ └───────────┬───────────┘
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      ▼
                      ┌───────────────────────────────┐
                      │    Thread-Safe Shared Cache   │
                      │   (Background API Scheduler)  │
                      └───────────────┬───────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │  Open-Source APIs (GWF/NOAA)  │
                      └───────────────────────────────┘
```

### 1. Request Balancing (Gunicorn WSGI)
Atmo Sync integrates `gunicorn.conf.py` to pre-fork multiple worker processes running concurrent threads. By running multiple workers, requests are automatically balanced across CPU cores:
```bash
# Optimal workers dynamically computed as: (2 * Cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
```

### 2. Upstream Proxying (Nginx Load Balancer)
We provide an `nginx.conf` template to establish an upstream load balancer pool using the `least_conn` algorithm. Nginx distributes requests to workers with the fewest active connections and handles direct static caching, shielding Flask from processing redundant static assets.

---

## ⚙️ Installation & Setup

### 1. Clone the Project
```bash
git clone https://github.com/arktrek/Atmo-Sync.git
cd Atmo-Sync
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Running the Development Server
```bash
python app.py
```

### 5. Running the Load-Balanced Production Server
To spin up the Gunicorn cluster load-balancing across multi-process workers:
```bash
gunicorn -c gunicorn.conf.py app:app
```

---

## 📊 Calculator Conversion Coefficients

Emissions coefficients conform to standard **IPCC** and **DEFRA** parameters:
* **Grid Electricity**: `0.207 kg CO₂e / kWh`
* **Natural Gas**: `0.183 kg CO₂e / kWh`
* **LPG**: `1.55 kg CO₂e / kg`
* **Car Commutes**:
  * *Petrol*: `0.17 kg CO₂e / km`
  * *Diesel*: `0.16 kg CO₂e / km`
  * *Hybrid*: `0.10 kg CO₂e / km`
  * *EV*: `0.04 kg CO₂e / km`
* **Public Transit**: `0.05 kg CO₂e / passenger-hour`
* **Flight Time**: `150 kg CO₂e / flight-hour`
* **Diet (Annual)**:
  * *Meat Lover*: `3.3 Tons CO₂e`
  * *Average*: `2.1 Tons CO₂e`
  * *Vegetarian*: `1.5 Tons CO₂e`
  * *Vegan*: `1.1 Tons CO₂e`
* **Waste**: `0.5 kg CO₂e / kg` (inversely adjusted by recycling rate).



## 🧑‍💻 Developer
* **Arpit Ramesan**
* **GitHub**: [github.com/arktrek](https://github.com/arktrek)
* **LinkedIn**: [linkedin.com/in/arpitramesan](https://www.linkedin.com/in/arpitramesan)
