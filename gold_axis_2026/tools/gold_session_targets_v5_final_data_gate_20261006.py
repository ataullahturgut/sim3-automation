from __future__ import annotations
import hashlib, json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_CORE_V4_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_CORE_V4_2023_2025.csv"
OUT=AX/"SESSION_TARGETS_V5_FINAL_DATA_GATE_OUT"; OUT.mkdir(exist_ok=True)

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def expected_grid(s,e):
    return pd.date_range(s, e-pd.Timedelta(minutes=15), freq="15min", tz="UTC")

def allowed_maintenance(row):
    if row["partition"]!="SOBTI_5_ET" or row["window"]!="US_LATE_LIT":
        return set()
    s=pd.Timestamp(row["start_utc"])
    ny_date=s.tz_convert("America/New_York").date()
    base=pd.Timestamp(f"{ny_date.isoformat()} 17:00", tz="America/New_York").tz_convert("UTC")
    return {base+pd.Timedelta(minutes=15*k) for k in range(4)}

def clean(df, present):
    rows=[]; exclusions=[]
    for _, r in df.iterrows():
        z=r.to_dict()
        s=pd.Timestamp(r["start_utc"]); e=pd.Timestamp(r["end_utc"])
        grid=list(expected_grid(s,e))
        missing=[t for t in grid if t not in present]
        allowed=allowed_maintenance(r)
        disallowed=[t for t in missing if t not in allowed]
        path_clean=(len(disallowed)==0)
        final_trainable=bool(r["core_trainable"]) and path_clean
        reasons=[]
        if not bool(r["core_trainable"]):
            reasons.append(str(r.get("core_exclusion_reason","")) if r.get("core_exclusion_reason","") else "V4_CORE_EXCLUDED")
        if disallowed:
            reasons.append("DISALLOWED_INTERNAL_15M_GAP")
        z.update({
            "expected_15m_slots":len(grid),
            "missing_15m_slots":len(missing),
            "allowed_maintenance_missing_slots":sum(t in allowed for t in missing),
            "disallowed_missing_slots":len(disallowed),
            "disallowed_missing_utc":"|".join(t.isoformat() for t in disallowed),
            "path_clean":bool(path_clean),
            "final_trainable":bool(final_trainable),
            "final_exclusion_reason":"|".join(dict.fromkeys(reasons))
        })
        rows.append(z)
        if not final_trainable:
            exclusions.append(z)
    return pd.DataFrame(rows), pd.DataFrame(exclusions)

def summary(df):
    out={}
    for (yr,w),g in df.groupby(["year","window"]):
        f=g[g.final_trainable]
        out[f"{yr}_{w}"]={
            "rows":int(len(g)),
            "v4_core_trainable":int(g.core_trainable.astype(bool).sum()),
            "v5_final_trainable":int(g.final_trainable.sum()),
            "path_gap_excluded_from_v4_core":int((g.core_trainable.astype(bool)&~g.path_clean).sum()),
            "up_final":int(((g.direction=="UP")&g.final_trainable).sum()),
            "down_final":int(((g.direction=="DOWN")&g.final_trainable).sum())
        }
    return out

def main():
    raw=pd.read_csv(RAW)
    raw["dt_utc"]=pd.to_datetime(raw.dt_utc,utc=True)
    present=set(raw.dt_utc)
    w,e1=clean(pd.read_csv(WGC),present)
    s,e2=clean(pd.read_csv(SOB),present)

    pw=OUT/"wgc2026_ny3_final.csv"
    ps=OUT/"sobti5_et_final.csv"
    pe=OUT/"excluded_rows.csv"
    w.to_csv(pw,index=False); s.to_csv(ps,index=False)
    pd.concat([e1,e2],ignore_index=True).to_csv(pe,index=False)

    allq=pd.concat([w,s],ignore_index=True)
    bad_final=allq[allq.final_trainable & (~allq.core_trainable.astype(bool) | ~allq.path_clean)]
    duplicate=int(allq.duplicated(["label_date","partition","window"]).sum())
    missing_direction=int(allq[allq.final_trainable].direction.isna().sum())

    out={
      "status":"FINAL_PREMODEL_SESSION_TARGET_GATE_V5",
      "raw_sha256":sha(RAW),
      "input_hashes":{"wgc_v4":sha(WGC),"sobti_v4":sha(SOB)},
      "rules":{
        "price_semantics":"start exact 15m OPEN; end CLOSE of exact final 15m bar",
        "venue_gate":"V4 core_trainable must be true",
        "internal_path":"all 15m slots required",
        "sobti_us_late_exception":"only the four 17:00,17:15,17:30,17:45 America/New_York maintenance slots may be absent",
        "friday_us_late":"remains NOT_ELIGIBLE from V3/V4",
        "imputation":"NONE"
      },
      "rows_total":int(len(allq)),
      "duplicates":duplicate,
      "final_trainable_rows":int(allq.final_trainable.sum()),
      "final_excluded_rows":int((~allq.final_trainable).sum()),
      "new_path_gap_exclusions_from_v4_core":int((allq.core_trainable.astype(bool)&~allq.path_clean).sum()),
      "invalid_final_rows":int(len(bad_final)),
      "final_rows_missing_direction":missing_direction,
      "coverage":{"WGC_2026_NY3":summary(w),"SOBTI_5_ET":summary(s)},
      "hashes":{"wgc_final":sha(pw),"sobti_final":sha(ps),"excluded":sha(pe)},
      "model_gate":"MODEL CODE MUST ASSERT final_trainable==True. No V2/V3/V4 price_trainable-only row may enter primary modelling.",
      "source_regime_guardrail":"source_regime and vendor-coverage regime fields are audit metadata only and are forbidden as predictive features."
    }
    (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    (OUT/"result.md").write_text(
      "# GOLD SESSION TARGETS V5 — FINAL PREMODEL DATA GATE\n\n"
      "- Exact start OPEN / exact final 15m CLOSE.\n"
      "- No price imputation or nearest-bar substitution.\n"
      "- V4 venue/calendar gate required.\n"
      "- Full internal 15m path required, except known 17:00-18:00 NY maintenance slots inside Sobti US_LATE.\n"
      "- Friday Sobti US_LATE remains NOT_ELIGIBLE.\n"
      "- Primary model code must assert final_trainable==True.\n"
    )
    print(json.dumps(out,indent=2))

if __name__=="__main__": main()
