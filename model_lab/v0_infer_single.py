#!/usr/bin/env python3
"""
v0_infer_single.py
- Single-file inference runner for v0 threshold model
- Loads model parameters from a YAML file
- Runs on CSV input or synthetic samples
- Saves predictions to CSV
"""
from __future__ import annotations
import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    import yaml  # PyYAML
except Exception as e:
    sys.exit("PyYAML is required. Install with: pip install pyyaml")

def load_threshold_model(model_yaml: Path) -> Dict:
    cfg = yaml.safe_load(model_yaml.read_text(encoding="utf-8"))
    mv = str(cfg.get("model_version", "0.0.0"))
    params = cfg.get("params", {}) or {}
    theta_low = float(params.get("theta_low", 0.6))
    theta_high = params.get("theta_high")
    theta_high = None if theta_high is None else float(theta_high)
    # model_used: semver + short hash of file
    import hashlib
    h = hashlib.sha256(model_yaml.read_bytes()).hexdigest()[:7]
    model_used = f"threshold@{mv}#{h}"
    return {"theta_low": theta_low, "theta_high": theta_high, "model_used": model_used}

def predict(rows: List[Dict], theta_low: float, theta_high: Optional[float]) -> List[Dict]:
    out: List[Dict] = []
    for r in rows:
        x = float(r["data"])
        th = theta_low if theta_high is None else theta_high
        label = "pos" if x >= th else "neg"
        out.append({
            **r,
            "predicted": label,
            "proba": None,
        })
    return out

def load_csv(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for i, row in enumerate(rdr, start=1):
            rid = row.get("id", i)
            created_at = row.get("created_at")
            data = row.get("data")
            if data is None:
                raise ValueError("Input CSV must contain a 'data' column.")
            rows.append({"id": rid, "created_at": created_at, "data": float(data)})
    return rows

def make_synthetic(n: int = 40, seed: int = 7) -> List[Dict]:
    import random
    random.seed(seed)
    rows: List[Dict] = []
    for i in range(n):
        x = random.random()  # 0~1
        rows.append({"id": i+1, "created_at": None, "data": x})
    return rows

def save_csv(path: Path, rows: List[Dict], model_used: str) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    # Ensure model_used included as a column
    rows = [{**r, "model_used": model_used} for r in rows]
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def main():
    ap = argparse.ArgumentParser(description="Single-file v0 threshold inference")
    ap.add_argument("--model", type=str, default="./models/v0/model.yaml", help="Path to YAML model file")
    ap.add_argument("--input-csv", type=str, default=None, help="Optional CSV input with at least 'data' column")
    ap.add_argument("--output-csv", type=str, default="predictions.csv", help="Where to save predictions")
    ap.add_argument("--sample-n", type=int, default=40, help="If no CSV, generate N synthetic samples")
    args = ap.parse_args()

    model_yaml = Path(args.model).expanduser().resolve()
    if not model_yaml.exists():
        sys.exit(f"Model file not found: {model_yaml}")

    model = load_threshold_model(model_yaml)
    print(f"[LOAD] model_used={model['model_used']} theta_low={model['theta_low']} theta_high={model['theta_high']}")

    if args.input_csv:
        rows = load_csv(Path(args.input_csv).expanduser().resolve())
        print(f"[DATA] loaded {len(rows)} rows from CSV")
    else:
        rows = make_synthetic(n=args.sample_n)
        print(f"[DATA] generated {len(rows)} synthetic rows (uniform[0,1))")

    preds = predict(rows, model["theta_low"], model["theta_high"])

    out_path = Path(args.output_csv).expanduser().resolve()
    save_csv(out_path, preds, model["model_used"])
    print(f"[DONE] wrote {len(preds)} predictions → {out_path}")

if __name__ == "__main__":
    main()
