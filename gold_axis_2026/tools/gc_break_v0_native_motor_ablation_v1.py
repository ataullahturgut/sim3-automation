from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_native_motor_ablation_contract_v1.json"
DIAG_DIR = ROOT / "data_pipeline" / "audits" / "gc_break_v0_diagnostic_v1"
OUT_DIR = ROOT / "data_pipeline" / "audits" / "gc_break_v0_native_motor_ablation_v1"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def directional_event_recall(panel: pd.DataFrame, events: pd.DataFrame, signal: str, new_regime: str) -> dict:
    p = panel.reset_index(drop=True)
    event_positions = {int(r.event_id): int(p.index[p["date"].eq(r.break_date)][0]) for r in events.itertuples()}
    rows=[]
    prev_pos=-1
    for ev in events.itertuples():
        eid=int(ev.event_id)
        pos=event_positions[eid]
        if ev.new_regime == new_regime:
            seg=p.loc[prev_pos+1:pos, ["date",signal]].copy()
            pre=seg.iloc[:-1] if len(seg) else seg
            pre_hits=pre[pre[signal].fillna(False).astype(bool)]
            all_hits=seg[seg[signal].fillna(False).astype(bool)]
            rows.append({
                "event_id":eid,
                "break_date":ev.break_date,
                "new_regime":new_regime,
                "prebreak_hit":not pre_hits.empty,
                "at_or_before_hit":not all_hits.empty,
                "first_prebreak_date":pre_hits.iloc[0]["date"] if not pre_hits.empty else pd.NaT,
            })
        prev_pos=pos
    df=pd.DataFrame(rows)
    n=len(df)
    return {
        "event_scope":f"NEW_REGIME_{new_regime}",
        "events":n,
        "prebreak_recall":float(df["prebreak_hit"].mean()) if n else None,
        "at_or_before_recall":float(df["at_or_before_hit"].mean()) if n else None,
    }


def main() -> int:
    c=json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_NATIVE_MOTOR_ABLATION_SCORING":
        raise RuntimeError("ABLATION_CONTRACT_NOT_FROZEN")
    if c["governance"]["no_database_writes"] is not True:
        raise RuntimeError("NO_WRITE_GUARD_FAIL")

    diag=load_module(ROOT / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_diag_ablation")
    panel=pd.read_csv(DIAG_DIR / "gc_break_v0_origin_panel.csv", parse_dates=["date"])
    events=pd.read_csv(DIAG_DIR / "gc_break_v0_break_events.csv", parse_dates=["break_date"])

    rows=[]
    episodes=[]
    for spec in c["signals"]:
        col=spec["column"]
        if col not in panel.columns:
            raise RuntimeError(f"SIGNAL_COLUMN_MISSING:{col}")
        m,e=diag.evaluate_signal(panel, events, col)
        m.update({"motor_id":spec["id"],"role":spec["role"],"preregistered_event_scope":spec["event_scope"]})
        m["new_regime_down"] = directional_event_recall(panel,events,col,"DOWN")
        m["new_regime_up"] = directional_event_recall(panel,events,col,"UP")
        rows.append(m)
        if not e.empty:
            e=e.copy(); e["motor_id"]=spec["id"]; episodes.append(e)

    flat=[]
    for r in rows:
        x={k:v for k,v in r.items() if k not in {"new_regime_down","new_regime_up"}}
        for prefix,key in [("down","new_regime_down"),("up","new_regime_up")]:
            for k,v in r[key].items(): x[f"{prefix}_{k}"]=v
        flat.append(x)
    metrics=pd.DataFrame(flat)
    eps=pd.concat(episodes,ignore_index=True) if episodes else pd.DataFrame()

    OUT_DIR.mkdir(parents=True,exist_ok=True)
    metrics.to_csv(OUT_DIR / "gc_break_native_motor_ablation_metrics.csv",index=False)
    eps.to_csv(OUT_DIR / "gc_break_native_motor_ablation_episodes.csv",index=False)

    summary={
        "audit_id":"GC_BREAK_V0_NATIVE_MOTOR_ABLATION_V1",
        "contract_id":c["contract_id"],
        "contract_status":c["status"],
        "production_authority":False,
        "production_database_write":"NONE",
        "prospective_claim":False,
        "origins":int(len(panel)),
        "events":int(len(events)),
        "metrics":{},
        "interpretation_lock":"RETROSPECTIVE ROLE DIAGNOSTIC ONLY; no threshold, trigger, winner or weighting may be selected from this output."
    }
    for r in rows:
        summary["metrics"][r["motor_id"]]={
            "role":r["role"],
            "episodes":r["episodes"],
            "converted_episodes":r["converted_episodes"],
            "false_episodes":r["false_episodes"],
            "episode_conversion_rate":r["episode_conversion_rate"],
            "false_episodes_per_100_origins":r["false_episodes_per_100_origins"],
            "prebreak_event_recall_all":r["prebreak_event_recall"],
            "at_or_before_event_recall_all":r["at_or_before_event_recall"],
            "median_lead_observations":r["median_lead_observations"],
            "median_lead_calendar_days":r["median_lead_calendar_days"],
            "prebreak_recall_down_breaks":r["new_regime_down"]["prebreak_recall"],
            "prebreak_recall_up_breaks":r["new_regime_up"]["prebreak_recall"],
            "preregistered_event_scope":r["preregistered_event_scope"],
        }
    (OUT_DIR / "gc_break_v0_native_motor_ablation_v1_summary.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
