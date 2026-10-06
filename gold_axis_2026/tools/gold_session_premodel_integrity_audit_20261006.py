from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
WGC=AX/"GOLD_SESSION_LABELS_WGC2026_NY3_2023_2025.csv"
SOB=AX/"GOLD_SESSION_LABELS_SOBTI5_ET_2023_2025.csv"
OUT=AX/"SESSION_PREMODEL_INTEGRITY_AUDIT_OUT"; OUT.mkdir(exist_ok=True)

EXPECTED={
 ("WGC_2026_NY3","ASIA"):{"start":"18:00","end":"03:00","duration_h":9.0,"start_prev_date":True,"end_prev_date":False},
 ("WGC_2026_NY3","EUROPE"):{"start":"03:00","end":"08:00","duration_h":5.0,"start_prev_date":False,"end_prev_date":False},
 ("WGC_2026_NY3","US"):{"start":"08:00","end":"17:00","duration_h":9.0,"start_prev_date":False,"end_prev_date":False},
 ("SOBTI_5_ET","ASIA_MORNING_LIT"):{"start":"21:00","end":"23:30","duration_h":2.5,"start_prev_date":True,"end_prev_date":True},
 ("SOBTI_5_ET","ASIA_AFTERNOON_LIT"):{"start":"01:30","end":"03:30","duration_h":2.0,"start_prev_date":False,"end_prev_date":False},
 ("SOBTI_5_ET","EUROPE_LIT"):{"start":"03:30","end":"08:00","duration_h":4.5,"start_prev_date":False,"end_prev_date":False},
 ("SOBTI_5_ET","NY_LONDON_LIT"):{"start":"08:00","end":"14:30","duration_h":6.5,"start_prev_date":False,"end_prev_date":False},
 ("SOBTI_5_ET","US_LATE_LIT"):{"start":"14:30","end":"21:00","duration_h":6.5,"start_prev_date":False,"end_prev_date":False},
}

def sha256_file(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def sgn(r):
    if pd.isna(r): return None
    if r>0:return "UP"
    if r<0:return "DOWN"
    return "FLAT"

def main():
    x=pd.read_csv(RAW)
    x["dt_utc"]=pd.to_datetime(x.dt_utc,utc=True)
    x=x.sort_values("dt_utc").drop_duplicates("dt_utc")
    op=dict(zip(x.dt_utc,x.open.astype(float)))
    cl=dict(zip(x.dt_utc,x.close.astype(float)))

    panels=[]
    for p in [WGC,SOB]:
        q=pd.read_csv(p)
        q["source_file"]=p.name
        panels.append(q)
    z=pd.concat(panels,ignore_index=True)

    for c in ["start_utc","end_utc","start_ny","end_ny"]:
        z[c]=pd.to_datetime(z[c],utc=(c.endswith("_utc")))

    errors=[]
    audits=[]
    for i,r in z.iterrows():
        key=(r.partition,r.window)
        exp=EXPECTED[key]
        label_date=pd.Timestamp(r.label_date)
        su=pd.Timestamp(r.start_utc)
        eu=pd.Timestamp(r.end_utc)
        sny=su.tz_convert("America/New_York")
        eny=eu.tz_convert("America/New_York")
        duration=(eu-su).total_seconds()/3600.0
        start_date_expected=(label_date-pd.Timedelta(days=1)).date() if exp["start_prev_date"] else label_date.date()
        end_date_expected=(label_date-pd.Timedelta(days=1)).date() if exp.get("end_prev_date",False) else label_date.date()

        rowerrs=[]
        if label_date.weekday()>=5: rowerrs.append("LABEL_DATE_NOT_WEEKDAY")
        if sny.strftime("%H:%M")!=exp["start"]: rowerrs.append("START_NY_CLOCK_MISMATCH")
        if eny.strftime("%H:%M")!=exp["end"]: rowerrs.append("END_NY_CLOCK_MISMATCH")
        if sny.date()!=start_date_expected: rowerrs.append("START_NY_DATE_MISMATCH")
        if eny.date()!=end_date_expected: rowerrs.append("END_NY_DATE_MISMATCH")
        if abs(duration-exp["duration_h"])>1e-9: rowerrs.append("DURATION_MISMATCH")
        if su.minute%15!=0 or eu.minute%15!=0: rowerrs.append("NON_15M_BOUNDARY")

        # Recompute boundary methods and prices exactly.
        def bp(t):
            if t in op: return float(op[t]),"OPEN_AT_T"
            p=t-pd.Timedelta(minutes=15)
            if p in cl: return float(cl[p]),"PREV_15M_CLOSE_AT_T"
            return None,"MISSING"

        ps,ms=bp(su); pe,me=bp(eu)
        rr=np.nan if ps is None or pe is None else pe/ps-1.0
        dd=None if pd.isna(rr) else sgn(rr)

        if ms!=r.start_boundary_method: rowerrs.append("START_METHOD_MISMATCH")
        if me!=r.end_boundary_method: rowerrs.append("END_METHOD_MISMATCH")
        if (ps is None)!=(pd.isna(r.start_price)): rowerrs.append("START_PRICE_NULL_MISMATCH")
        if (pe is None)!=(pd.isna(r.end_price)): rowerrs.append("END_PRICE_NULL_MISMATCH")
        if ps is not None and not np.isclose(ps,float(r.start_price),rtol=0,atol=1e-9): rowerrs.append("START_PRICE_MISMATCH")
        if pe is not None and not np.isclose(pe,float(r.end_price),rtol=0,atol=1e-9): rowerrs.append("END_PRICE_MISMATCH")
        if not pd.isna(rr):
            if not np.isclose(rr,float(r["return"]),rtol=0,atol=1e-12): rowerrs.append("RETURN_MISMATCH")
            if dd!=r.direction: rowerrs.append("DIRECTION_MISMATCH")
        else:
            if not pd.isna(r["return"]): rowerrs.append("RETURN_SHOULD_BE_NULL")

        # Observe bars inside theoretical interval [start,end).
        g=x[(x.dt_utc>=su)&(x.dt_utc<eu)]
        n=int(len(g))
        first=None if g.empty else g.dt_utc.iloc[0]
        last=None if g.empty else g.dt_utc.iloc[-1]
        expected_slots=int(round(duration*4))
        missing_slots=expected_slots-n

        # Classification for unresolved rows.
        # Literature late-US cannot exist as a full 14:30->21:00 Friday
        # trading window under the historical standard GC weekly schedule.
        # This rule overrides a synthetic/24x7 vendor quote appearing after the
        # economic weekly close.
        if r.partition=="SOBTI_5_ET" and r.window=="US_LATE_LIT" and label_date.weekday()==4:
            classif="NOT_ELIGIBLE_WEEKLY_CLOSE_FRIDAY"
        elif r.coverage=="PASS":
            classif="TRAINABLE_SESSION_DIRECTION"
        else:
            if n==0:
                classif="NOT_ELIGIBLE_OR_FULL_WINDOW_CLOSED"
            else:
                # Determine whether data started late / ended early / internal gap.
                late_start=(first is not None and first>su+pd.Timedelta(minutes=15))
                early_end=(last is not None and last<eu-pd.Timedelta(minutes=30))
                if late_start and early_end:
                    classif="TRUNCATED_BOTH_ENDS_REVIEW"
                elif late_start:
                    classif="DELAYED_OPEN_OR_SOURCE_GAP_REVIEW"
                elif early_end:
                    classif="EARLY_CLOSE_OR_SOURCE_GAP_REVIEW"
                else:
                    classif="BOUNDARY_OR_INTERNAL_SOURCE_GAP_REVIEW"

        audits.append({
          "source_file":r.source_file,"label_date":r.label_date,"partition":r.partition,"window":r.window,
          "start_utc":su.isoformat(),"end_utc":eu.isoformat(),"start_ny":sny.isoformat(),"end_ny":eny.isoformat(),
          "duration_h":duration,"coverage_in_label":r.coverage,
          "recomputed_start_method":ms,"recomputed_end_method":me,
          "raw_bars_inside":n,"expected_15m_slots":expected_slots,"slot_shortfall":missing_slots,
          "first_bar_inside":None if first is None else first.isoformat(),
          "last_bar_inside":None if last is None else last.isoformat(),
          "classification":classif,"integrity_errors":"|".join(rowerrs)
        })
        if rowerrs:
            errors.append({"row":int(i),"label_date":r.label_date,"partition":r.partition,"window":r.window,"errors":rowerrs})

    a=pd.DataFrame(audits)
    a.to_csv(OUT/"row_audit.csv",index=False)

    # Duplicates / key completeness
    dup=z.duplicated(["label_date","partition","window"]).sum()
    expected_counts={}
    for (part,win),g in z.groupby(["partition","window"]):
        expected_counts[f"{part}:{win}"]={"rows":int(len(g)),"unique_dates":int(g.label_date.nunique())}

    # Missing/review dates
    issue=a[a.classification!="TRAINABLE_SESSION_DIRECTION"].copy()
    issue.to_csv(OUT/"nontrainable_or_review_rows.csv",index=False)

    class_counts=(a.groupby(["partition","window","classification"]).size().rename("n").reset_index())
    class_counts.to_csv(OUT/"classification_counts.csv",index=False)

    # Summaries by year as well
    a["year"]=pd.to_datetime(a.label_date).dt.year
    yr=(a.groupby(["year","partition","window","classification"]).size().rename("n").reset_index())
    yr.to_csv(OUT/"classification_by_year.csv",index=False)

    # Source regime boundary around 2025-04-22: compare returns just around it, no outcome-based decisions.
    # Also flag all fallback use.
    fallback=a[(a.recomputed_start_method=="PREV_15M_CLOSE_AT_T")|(a.recomputed_end_method=="PREV_15M_CLOSE_AT_T")].copy()
    fallback.to_csv(OUT/"fallback_rows.csv",index=False)

    result={
      "status":"PREMODEL_SESSION_LABEL_INTEGRITY_AUDIT",
      "raw_sha256":sha256_file(RAW),
      "label_sha256":{WGC.name:sha256_file(WGC),SOB.name:sha256_file(SOB)},
      "rows_total":int(len(z)),
      "duplicate_label_partition_window_keys":int(dup),
      "integrity_error_rows":int(len(errors)),
      "integrity_errors_sample":errors[:50],
      "expected_counts":expected_counts,
      "classification_counts":class_counts.to_dict("records"),
      "nontrainable_or_review_rows":int(len(issue)),
      "fallback_rows":int(len(fallback)),
      "guardrail":"Only TRAINABLE_SESSION_DIRECTION rows may enter the first model target panel. REVIEW/NOT_ELIGIBLE rows are excluded until separately resolved."
    }
    (OUT/"summary.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
    print(json.dumps(result,indent=2,default=str))

if __name__=="__main__":
    main()
