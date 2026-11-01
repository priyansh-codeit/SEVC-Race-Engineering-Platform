"""Heliarch backend: replays the telemetry CSV as a live feed and runs a digital-twin check."""
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "heliark_telemetry_sim.csv").copy()
N = len(df)
LAP_LEN = float(df.lap_distance_m.max())
SPEED_CAP = 60.0  # SEVC rulebook

# Digital twin (spec 3.5): OCV(SOC) - I*R vs measured pack voltage; speed vs commanded target
s = df.soc_pct.values / 100
ocv = 20 * (3.35 + .55 * s + .30 * s**3 - .20 * (1 - s)**4)
df["twin_v"] = ocv - df.pack_current_A * df.pack_internal_resistance_mOhm / 1000

def twin_metrics(i, w=300):
    d = df.iloc[max(0, i - w + 1): i + 1]
    ev, es = d.twin_v - d.pack_voltage_V, d.speed_target_kmph - d.speed_kmph
    a = df.iloc[:i + 1]  # R2 over the whole run so far
    ss = ((a.pack_voltage_V - a.pack_voltage_V.mean())**2).sum() or 1
    return dict(speed_mae=float(es.abs().mean()), speed_rmse=float(np.sqrt((es**2).mean())),
                volt_mae=float(ev.abs().mean()), r2=float(1 - ((a.twin_v - a.pack_voltage_V)**2).sum() / ss),
                compliant=bool((df.speed_kmph.iloc[:i + 1] <= SPEED_CAP).all()))

laps = df.groupby("lap").agg(t=("last_lap_time_s", "max"), e=("net_battery_energy_Wh", "last"),
                              soc=("soc_pct", "last"))
laps = laps[laps.t > 0]
LAP_T = float(laps.t.median()); E_LAP = float(laps.e.diff().dropna().median())
SOC_LAP = float((laps.soc.shift() - laps.soc).dropna().median())

def strategy(i):
    f = df.iloc[i]; left = max(0.0, 7200 - f.elapsed_s)
    return dict(target_lap=LAP_T, energy_lap_wh=E_LAP, finish_soc=float(f.soc_pct - SOC_LAP * left / LAP_T),
                remaining_min=float(left / 60))

SERIES = ["speed_kmph", "pack_voltage_V", "motor_phase_current_A", "motor_temp_C"]

def build_state(i, window=60):
    f = df.iloc[i]; w = df.iloc[max(0, i - window + 1): i + 1]
    fr = {k: (None if pd.isna(v) else (v.item() if hasattr(v, "item") else v)) for k, v in f.items()}
    return dict(i=i, frame=fr, track_frac=float(f.lap_distance_m / LAP_LEN),
                series={k: w[k].round(2).tolist() for k in SERIES}, twin=twin_metrics(i), strategy=strategy(i))

if __name__ != "__test__":
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    app = FastAPI(title="SolarMobil Heliarch")

    @app.get("/api/meta")
    def meta():
        return dict(rows=N, lap_len=LAP_LEN, laps=int(df.lap.max()), speed_cap=SPEED_CAP)

    @app.get("/api/state")
    def state(i: int = 0, window: int = 60):
        if not 0 <= i < N: raise HTTPException(404, "index out of range")
        return build_state(i, window)

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(ROOT / "frontend" / "index.html")

    app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="ui")
