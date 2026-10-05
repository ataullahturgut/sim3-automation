from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np
import pandas as pd
PDT_ORIG=pd.to_datetime

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"CIG_D1_SEP28_OCT2_EXTENSION_OUT"
OUT.mkdir(exist_ok=True)

os.environ.setdefault("STAK_LIVE_REF","54fdf1c8d39b7b6c7b874d0f30f784296e886044")

import gold_h3_oct5_diagnostic_nowcast as diag
import gold_h3_aurora_prospective_v1 as base
import gold_h3_clean_aurora_prospective_v1 as clean
import gold_h3_clean_v5_prospective_v1 as cv5
import gold_h3_iris_v1 as iris
import gold_h3_vega_v1 as vega

CUTOFFS=[
    pd.Timestamp("2026-09-25"),
    pd.Timestamp("2026-09-28"),
    pd.Timestamp("2026-09-29"),
    pd.Timestamp("2026-09-30"),
    pd.Timestamp("2026-10-01"),
]
FIRST=CUTOFFS[0]

def sim_ts(d):
    # 17:30 New York: after completed 16:00 bar, before next-day 08:00 issuance deadline.
    return pd.Timestamp(f"{d.date()} 17:30:00", tz="America/New_York").tz_convert("UTC")

def direction(p):
    return "UP" if float(p)>=0.5 else "DOWN"

def main():
    alt=diag.build_alt_prices()
    alt.to_csv(OUT/"ALT_DAILY_PRICES.csv",index=False)

    clean.OUT=OUT
    clean.configure()
    base.OUT=OUT
    base.PROSPECTIVE_MIN_FEATURE=FIRST

    price_path=OUT/"DIAG_PRICE_LEDGER.csv"
    forecast_path=OUT/"AURORA_LEDGER.csv"
    miss_path=OUT/"AURORA_MISSES.csv"
    integ_path=OUT/"INTEGRITY.csv"
    alt.to_csv(price_path,index=False)

    base.PRICE_LEDGER_FILE=price_path
    base.FORECAST_LEDGER_FILE=forecast_path
    base.MISS_LEDGER_FILE=miss_path
    base.INTEGRITY_LEDGER_FILE=integ_path

    # Replay each origin as if run just after that origin's completed daily/hourly anchor.
    for d in CUTOFFS:
        os.environ["AURORA_NOW_UTC"]=sim_ts(d).isoformat()
        base.main()

    a=pd.read_csv(forecast_path)
    a["feature_cutoff_date"]=pd.to_datetime(a.feature_cutoff_date,errors="coerce")
    got=a[a.feature_cutoff_date.isin(CUTOFFS)].copy().sort_values("feature_cutoff_date")
    if len(got)!=len(CUTOFFS):
        raise RuntimeError(f"AURORA_EXTENSION_MISSING got={len(got)} expected={len(CUTOFFS)} dates={got.feature_cutoff_date.tolist()}")

    # Same diagnostic bridge used for the Oct-5 nowcast; only source extension changes,
    # model parameters / routing rules remain frozen.
    iris.fetch_extension=diag.extend_hourly_successor
    vega.fetch_gvz=diag.diag_fetch_gvz
    cv5.OUT=OUT
    cv5.AURORA_LEDGER=forecast_path
    cv5.FIRST_FEATURE=FIRST

    def mixed_to_datetime(arg,*args,**kwargs):
        if "format" not in kwargs:
            kwargs["format"]="mixed"
        return PDT_ORIG(arg,*args,**kwargs)
    pd.to_datetime=mixed_to_datetime
    try:
        g5,md=cv5.chain(a)
    finally:
        pd.to_datetime=PDT_ORIG
    g5["feature_cutoff_date"]=pd.to_datetime(g5.feature_cutoff_date,errors="coerce")
    q=g5[g5.feature_cutoff_date.isin(CUTOFFS)].copy().sort_values("feature_cutoff_date")
    if len(q)!=len(CUTOFFS):
        raise RuntimeError(f"V5_EXTENSION_MISSING got={len(q)} expected={len(CUTOFFS)}")

    frozen=pd.read_csv(AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv")
    frozen["date"]=pd.to_datetime(frozen.date)
    px=pd.concat([frozen,alt[["date","gold","silver","platinum","palladium"]]],ignore_index=True)
    px["date"]=pd.to_datetime(px.date)
    px=px.sort_values("date").drop_duplicates("date",keep="last")
    pmap=dict(zip(px.date,px.gold.astype(float)))

    rows=[]
    for r in q.itertuples(index=False):
        d=pd.Timestamp(r.feature_cutoff_date)
        deadline,issue=base.deadline_utc(d)
        issue=pd.Timestamp(issue).tz_localize(None).normalize() if getattr(issue,"tzinfo",None) is not None else pd.Timestamp(issue).normalize()
        if d not in pmap or issue not in pmap:
            raise RuntimeError(f"PRICE_MISSING cutoff={d} issue={issue}")
        actual="UP" if pmap[issue]>pmap[d] else "DOWN"
        aur=direction(r.p_aurora)
        v5=direction(r.p_helios_v5_dce)
        rift_dir=("DOWN" if aur=="UP" else "UP") if bool(r.rift_override) else aur
        vega_dir=("DOWN" if aur=="UP" else "UP") if bool(r.vega_override) else aur

        # Frozen SAGE V2 source contract requires IFBC+LLRS. The archived frozen
        # snapshots stop at 2026-09-24. Missing source => exception FALSE => KEEP V5.
        # RuleFlow V3-TG likewise has no same-origin frozen source record here, so no
        # undocumented retrospective FLIP is created. This is a fail-closed extension.
        sage_ruleflow=v5
        source_state="FAIL_CLOSED_KEEP_V5_POST_SNAPSHOT"

        consensus = v5 if (sage_ruleflow==v5==rift_dir==vega_dir) else "UNCERTAIN"
        rows.append({
            "feature_cutoff_date":str(d.date()),
            "forecast_issue_date":str(issue.date()),
            "gold_cutoff":float(pmap[d]),
            "gold_issue":float(pmap[issue]),
            "d1_actual":actual,
            "aurora":aur,
            "sage_ruleflow":sage_ruleflow,
            "v5":v5,
            "rift":rift_dir,
            "vega":vega_dir,
            "consensus":consensus,
            "consensus_correct":"" if consensus=="UNCERTAIN" else int(consensus==actual),
            "p_aurora":float(r.p_aurora),
            "p_v5":float(r.p_helios_v5_dce),
            "rift_override":bool(r.rift_override),
            "vega_override":bool(r.vega_override),
            "candidate_reversal":bool(r.candidate_reversal),
            "opal_override":bool(r.opal_override),
            "gt_flip_share":float(r.gt_flip_share),
            "v4_route":bool(r.v4_route),
            "rge_active":bool(r.rge_active),
            "dce_exception":bool(r.dce_exception),
            "sage_ruleflow_source_state":source_state,
        })

    z=pd.DataFrame(rows)
    z.to_csv(OUT/"CIG_D1_SEP28_OCT2_EXTENSION.csv",index=False)

    cons=z[z.consensus!="UNCERTAIN"]
    summary={
        "schema":"CIG_D1_SEP28_OCT2_EXTENSION_V1",
        "status":"RETROSPECTIVE_DIAGNOSTIC_FAIL_CLOSED_SAGE_RULEFLOW",
        "historical_v5_reproduction_max_abs_diff":float(md),
        "n_days":int(len(z)),
        "consensus_n":int(len(cons)),
        "consensus_correct":int((cons.consensus==cons.d1_actual).sum()),
        "consensus_accuracy":float((cons.consensus==cons.d1_actual).mean()) if len(cons) else None,
        "coverage":float(len(cons)/len(z)) if len(z) else None,
        "uncertain_n":int((z.consensus=="UNCERTAIN").sum()),
        "rows":z.to_dict("records"),
        "governance":{
            "sage_v2":"IFBC/LLRS frozen snapshots end 2026-09-24; frozen missing-source rule => KEEP V5",
            "ruleflow_v3":"no same-origin frozen source record for these origins; no undocumented retrospective flip created",
            "evidence_class":"diagnostic extension, not prospective OOS",
        },
    }
    (OUT/"CIG_D1_SEP28_OCT2_EXTENSION.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
      "# GOLD D1 — 28 Sep to 2 Oct 2026 CIG extension","",
      "**Status:** retrospective diagnostic; SAGE/RuleFlow fail-closed where frozen source snapshots are unavailable.","",
      "| Cutoff | Issue | Actual | SAGE+RF | V5 | RIFT | VEGA | CIG | Correct |",
      "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in z.itertuples(index=False):
        lines.append(f"| {r.feature_cutoff_date} | {r.forecast_issue_date} | {r.d1_actual} | {r.sage_ruleflow} | {r.v5} | {r.rift} | {r.vega} | {r.consensus} | {r.consensus_correct} |")
    lines += ["",
      f"- days: **{len(z)}**",
      f"- 4/4 consensus: **{len(cons)}**",
      f"- correct consensus: **{int((cons.consensus==cons.d1_actual).sum())}**",
      f"- consensus accuracy: **{100*summary['consensus_accuracy']:.2f}%**" if summary["consensus_accuracy"] is not None else "- consensus accuracy: NA",
      f"- coverage: **{100*summary['coverage']:.2f}%**",
      f"- V5 full-chain historical reproduction max abs diff: **{md:.3e}**","",
      "## Governance","",
      "SAGE V2 requires both IFBC and LLRS under its frozen source contract. The archived snapshots end on 2026-09-24; the frozen missing-source policy therefore yields no exception and KEEP V5. RuleFlow V3-TG has no same-origin frozen source record for these post-snapshot origins, so this extension does not invent a retrospective RuleFlow flip. This preserves fail-closed semantics but is not equivalent to a fully reconstructed prospective source state.",
    ]
    (OUT/"CIG_D1_SEP28_OCT2_EXTENSION.md").write_text("\n".join(lines)+"\n")
    print((OUT/"CIG_D1_SEP28_OCT2_EXTENSION.md").read_text())
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
