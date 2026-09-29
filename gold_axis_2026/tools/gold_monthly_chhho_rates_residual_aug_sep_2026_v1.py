from __future__ import annotations

import argparse, json, math, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_external_pit_residual_v1 as pit

TARGETS=("2026-08","2026-09")
COLS=pit.BLOCKS["PIT_RATES"]

def forward_x(bundle,target,gpr_history):
    p=base.month_shift(target,-1)
    pp=base.month_shift(target,-2)
    z=base.gpr_norm(gpr_history,pp)
    x=[]
    for metal in base.METALS:
        M=bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"FORWARD_FEATURE_MONTH_MISSING {metal} {target} p={p} pp={pp}")
        x.extend((math.log(M[p]/M[pp]),base.weighted_daily_return(bundle,metal,p,z)))
    return np.asarray(x,float)

def forward_samples(bundle,target):
    origin=base.month_shift(target,-1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    gh=bundle.gpr_vintages[origin]
    out={}
    for t in base.month_range("2010-03",origin):
        try:
            out[t]=base.sample_for_target(bundle,t,gh,True)
        except RuntimeError:
            continue
    x=forward_x(bundle,target,gh)
    out[target]=(x,np.zeros(4,float))
    return out

def load_ext(path):
    d=json.loads(Path(path).read_text())
    lev={r["origin_month"]:(float(r["dgs10"]),float(r["dff"])) for r in d["rows"]}
    ext={}
    for m,(dglev,dflev) in lev.items():
        y,mo=map(int,m.split("-")); z=y*12+mo-2
        p=f"{z//12:04d}-{z%12+1:02d}"
        if p not in lev: continue
        dg=dglev-lev[p][0]; df=dflev-lev[p][1]
        ext[m]={"dgs10_change":dg,"dff_change":df,"curve_proxy_change":dg-df}
    return d,ext

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho-authority",required=True)
    ap.add_argument("--pit",required=True)
    ap.add_argument("--extension",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")

    authority=json.loads(Path(a.chhho_authority).read_text())
    hist_model=core.load_model(a.chhho_authority,"ChHHO-ANFIS")
    snap,ext0=pit.load_ext(a.pit)
    exdoc,ext1=load_ext(a.extension)
    ext0.update(ext1)

    bundle=base.load_data(dsn)

    rows=[]
    for target in TARGETS:
        origin=base.month_shift(target,-1)
        rec={"target":target,"origin":origin}
        try:
            samples=forward_samples(bundle,target)
            p,n,diag=anfis.select(samples,target,"CHHHO")
            origin_price=float(bundle.core_gold[origin])
            fc=float(origin_price*math.exp(float(p[0])))
            rec.update({"status":"OK","base_forecast":fc,"origin_price":origin_price,
                        "pred_log_return_gold":float(p[0]),"train_rows":n,"diag":diag})
            if origin not in ext0:
                rec.update({"residual_status":"BLOCKED_MISSING_PIT_RATES"})
            else:
                tr,fit=core.freeze_fit_apply(hist_model["dev"],[{
                    "target":target,"origin":origin,"forecast":fc,
                    "actual":fc,"rw":origin_price
                }],ext0,COLS)
                rec.update({
                    "residual_status":"OK",
                    "rates_features":ext0[origin],
                    "correction":float(tr[0]["correction"]),
                    "corrected_forecast":float(tr[0]["corrected_forecast"]),
                    "residual_fit":fit,
                })
        except Exception as e:
            rec.update({"status":"BLOCKED","reason":f"{type(e).__name__}: {e}"})
        rows.append(rec)

    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            inv=base.authority_invariants(cur)
    if inv!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
      "schema":"GOLD_MONTHLY_CHHHO_RATES_RESIDUAL_AUG_SEP_2026_V1_2026-09-29",
      "authority":{
        "base":"current ChHHO forward protocol",
        "residual_fit":"frozen DEV-only PIT Rates Ridge",
        "2025_or_2026_residual_updating":False,
        "database_access":"READ_ONLY",
        "pit_snapshot":snap["schema"],
        "pit_extension":exdoc["schema"],
      },
      "rows":rows,
      "authority_invariants_before":bundle.invariants_before,
      "authority_invariants_after":inv,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_RATES_AUG_SEP_2026_GATE=PASS")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
