# SolarMobil Heliark - Race Engineering Dashboard
All files sit in ONE flat folder (no subfolders):
main.py, requirements.txt, index.html, heliark_telemetry_sim.csv, .gitignore, README.md
(standalone.html = optional offline version, double-click to open)

Local:  pip install -r requirements.txt  then  python -m uvicorn main:app --port 8001  ->  http://127.0.0.1:8001
Vercel: push these files to the repo root, import in Vercel (framework: FastAPI / Other), Deploy.
Check:  /api/meta should return rows: 7200
