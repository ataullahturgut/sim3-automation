from __future__ import annotations
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

AX=Path(__file__).resolve().parents[1]
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
TGT=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
PRED_FILES=[
 AX/"GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv",
 AX/"GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv",
 AX/"GOLD_SESSION_SAGE_FROZEN_2025_TRANSPORT_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv",
]
OUT=AX/"SOBTI_LATE_US_LABEL_AUDIT_OUT";OUT.mkdir(exist_ok=True)
NY=ZoneInfo("America/New_York")

def asbool(s): return s.astype(str).str.lower().eq("true")

def main():
    raw=pd.read_csv(RAW)
    raw["dt_utc"]=pd.to_datetime(raw.dt_utc,utc=True,errors="raise")
    for c in ["open","high","low","close"]:
        raw[c]=pd.to_numeric(raw[c],errors="raise")
    if raw.duplicated("dt_utc").any(): raise RuntimeError("RAW_DUPLICATE")
    op=dict(zip(raw.dt_utc,raw.open.astype(float)))
    cl=dict(zip(raw.dt_utc,raw.close.astype(float)))
    present=set(raw.dt_utc)

    t=pd.read_csv(TGT)
    t=t[(t.partition=="SOBTI_5_ET")&(t.window=="US_LATE_LIT")].copy()
    t["start_utc"]=pd.to_datetime(t.start_utc,utc=True,errors="raise")
    t["end_utc"]=pd.to_datetime(t.end_utc,utc=True,errors="raise")
    t["label_date"]=pd.to_datetime(t.label_date).dt.date
    t["final_trainable_bool"]=asbool(t.final_trainable)
    t["core_trainable_bool"]=asbool(t.core_trainable)
    t["path_clean_bool"]=asbool(t.path_clean)

    rows=[]
    for r in t.itertuples(index=False):
        d=r.label_date
        s_local=pd.Timestamp(year=d.year,month=d.month,day=d.day,hour=14,minute=30,tz=NY)
        e_local=pd.Timestamp(year=d.year,month=d.month,day=d.day,hour=21,minute=0,tz=NY)
        s=s_local.tz_convert("UTC"); e=e_local.tz_convert("UTC"); ep=e-pd.Timedelta(minutes=15)
        sp=op.get(s); en=cl.get(ep)
        ret=None if sp is None or en is None else en/sp-1.0
        direction=None if ret is None else ("UP" if ret>0 else ("DOWN" if ret<0 else "FLAT"))
        grid=list(pd.date_range(s,e-pd.Timedelta(minutes=15),freq="15min",tz="UTC"))
        maint_local=[pd.Timestamp(year=d.year,month=d.month,day=d.day,hour=17,minute=0,tz=NY)+pd.Timedelta(minutes=15*k) for k in range(4)]
        maint=set(x.tz_convert("UTC") for x in maint_local)
        missing=[x for x in grid if x not in present]
        disallowed=[x for x in missing if x not in maint]
        stored_ret=float(r.return) if pd.notna(r.return) else None
        stored_sp=float(r.start_price) if pd.notna(r.start_price) else None
        stored_ep=float(r.end_price) if pd.notna(r.end_price) else None
        friday=(pd.Timestamp(d).weekday()==4)
        rows.append({
          "label_date":str(d),
          "stored_start_utc":r.start_utc.isoformat(),"expected_start_utc":s.isoformat(),
          "stored_end_utc":r.end_utc.isoformat(),"expected_end_utc":e.isoformat(),
          "start_clock_ok":r.start_utc==s,"end_clock_ok":r.end_utc==e,
          "start_ny":s.tz_convert(NY).isoformat(),"end_ny":e.tz_convert(NY).isoformat(),
          "start_offset_hours":s_local.utcoffset().total_seconds()/3600,
          "end_price_bar_open_utc":ep.isoformat(),
          "stored_start_price":stored_sp,"raw_start_open":sp,
          "start_price_ok":(stored_sp is None and sp is None) or (stored_sp is not None and sp is not None and abs(stored_sp-sp)<=1e-9),
          "stored_end_price":stored_ep,"raw_end_close":en,
          "end_price_ok":(stored_ep is None and en is None) or (stored_ep is not None and en is not None and abs(stored_ep-en)<=1e-9),
          "stored_return":stored_ret,"recomputed_return":ret,
          "return_ok":(stored_ret is None and ret is None) or (stored_ret is not None and ret is not None and abs(stored_ret-ret)<=1e-12),
          "stored_direction":None if pd.isna(r.direction) else str(r.direction),
          "recomputed_direction":direction,
          "direction_ok":(pd.isna(r.direction) and direction is None) or (not pd.isna(r.direction) and str(r.direction)==direction),
          "weekday":pd.Timestamp(d).weekday(),"friday":friday,
          "final_trainable":bool(r.final_trainable_bool),
          "friday_exclusion_ok":(not friday) or (not bool(r.final_trainable_bool)),
          "expected_slots":len(grid),"missing_slots":len(missing),
          "maintenance_missing_slots":sum(x in maint for x in missing),
          "disallowed_missing_slots":len(disallowed),
          "path_clean_stored":bool(r.path_clean_bool),
          "path_clean_recomputed":len(disallowed)==0,
          "path_clean_ok":bool(r.path_clean_bool)==(len(disallowed)==0),
          "core_trainable":bool(r.core_trainable_bool),
          "final_trainable_recomputed":bool(r.core_trainable_bool) and (len(disallowed)==0),
          "final_trainable_ok":bool(r.final_trainable_bool)==(bool(r.core_trainable_bool) and len(disallowed)==0),
        })
    a=pd.DataFrame(rows)
    a.to_csv(OUT/"target_row_audit.csv",index=False)

    target_final=t[t.final_trainable_bool].copy()
    target_final["y_up_recomputed"]=(target_final.direction=="UP").astype(int)
    pred_summary=[];pred_bad=[]
    for pf in PRED_FILES:
        if not pf.exists(): continue
        p=pd.read_csv(pf)
        if not {"partition","window","label_date","start_utc","y_up"}.issubset(p.columns): continue
        p=p[(p.partition=="SOBTI_5_ET")&(p.window=="US_LATE_LIT")].copy()
        if p.empty: continue
        p["start_utc"]=pd.to_datetime(p.start_utc,utc=True)
        p["label_date_date"]=pd.to_datetime(p.label_date).dt.date
        q=p.merge(target_final[["label_date","start_utc","direction","y_up_recomputed"]],
                  left_on=["label_date_date","start_utc"],right_on=["label_date","start_utc"],how="left",indicator=True)
        q["label_match"]=q["_merge"].eq("both") & q.y_up.astype(int).eq(q.y_up_recomputed.fillna(-1).astype(int))
        pred_summary.append({"file":pf.name,"rows":len(q),"matched_target_rows":int(q["_merge"].eq("both").sum()),
                             "y_up_exact_matches":int(q.label_match.sum()),"bad_rows":int((~q.label_match).sum())})
        bad=q[~q.label_match]
        if len(bad):
            bad=bad.copy();bad["source_file"]=pf.name;pred_bad.append(bad)
    pd.DataFrame(pred_summary).to_csv(OUT/"prediction_label_audit.csv",index=False)
    if pred_bad: pd.concat(pred_bad,ignore_index=True).to_csv(OUT/"prediction_label_mismatches.csv",index=False)

    summary={
      "status":"PASS" if (
        a.start_clock_ok.all() and a.end_clock_ok.all() and a.start_price_ok.all() and a.end_price_ok.all()
        and a.return_ok.all() and a.direction_ok.all() and a.friday_exclusion_ok.all()
        and a.path_clean_ok.all() and a.final_trainable_ok.all()
        and all(x["bad_rows"]==0 for x in pred_summary)
      ) else "FAIL",
      "target_rows":len(a),
      "target_2025_rows":int(pd.to_datetime(a.label_date).dt.year.eq(2025).sum()),
      "final_trainable_rows":int(a.final_trainable.sum()),
      "final_trainable_2025_rows":int(a[pd.to_datetime(a.label_date).dt.year.eq(2025)].final_trainable.sum()),
      "clock_mismatches":int((~a.start_clock_ok).sum()+(~a.end_clock_ok).sum()),
      "start_price_mismatches":int((~a.start_price_ok).sum()),
      "end_price_mismatches":int((~a.end_price_ok).sum()),
      "return_mismatches":int((~a.return_ok).sum()),
      "direction_mismatches":int((~a.direction_ok).sum()),
      "friday_exclusion_mismatches":int((~a.friday_exclusion_ok).sum()),
      "path_clean_mismatches":int((~a.path_clean_ok).sum()),
      "final_trainable_mismatches":int((~a.final_trainable_ok).sum()),
      "winter_examples":a[a.start_offset_hours==-5].head(3)[["label_date","start_ny","expected_start_utc","expected_end_utc","end_price_bar_open_utc"]].to_dict("records"),
      "summer_examples":a[a.start_offset_hours==-4].head(3)[["label_date","start_ny","expected_start_utc","expected_end_utc","end_price_bar_open_utc"]].to_dict("records"),
      "prediction_files":pred_summary,
      "label_definition":"Sobti Late-US = 14:30 America/New_York exact OPEN to CLOSE of the exact 20:45 America/New_York 15m bar ending at 21:00; Friday ineligible; 17:00-18:00 NY missing slots are the only registered maintenance exception."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print(json.dumps(summary,indent=2,default=str))
    if summary["status"]!="PASS": raise RuntimeError("LATE_US_LABEL_AUDIT_FAIL")

if __name__=="__main__":main()
