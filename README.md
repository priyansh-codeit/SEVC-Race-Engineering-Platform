# SolarMobil Heliarch

## Option 1: no install
Double-click `standalone.html` (data is embedded, works offline).

## Option 2: FastAPI backend + frontend
    pip install -r requirements.txt
    python -m uvicorn main:app --port 8001
Open http://127.0.0.1:8001  (check http://127.0.0.1:8001/api/meta shows rows: 7200)
Run the command from this folder (the one containing frontend/, data/).
