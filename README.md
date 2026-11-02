# SolarMobil Heliark - Race Engineering Dashboard

## Recommended: static deploy (no Python)
Upload ONLY index.html to your GitHub repo root. In Vercel set Framework Preset = Other, no build command. Deploy.
index.html already contains the telemetry data and all 7 views (Overview, Live Race, Digital Twin,
Track Simulator, Race Strategy, System Health, Reports). You can also just double-click it to open locally.

## Optional: FastAPI backend (API only: /api/meta, /api/state?i=N)
Put main.py, requirements.txt, heliark_telemetry_sim.csv and index.html in ONE flat folder.
Local: pip install -r requirements.txt, then python -m uvicorn main:app --port 8001
Do not mix this with the static deploy on Vercel.

## Git ignore
Rename gitignore.txt to .gitignore (optional).
