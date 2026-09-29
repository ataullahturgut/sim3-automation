from __future__ import annotations
import argparse, json, math, glob, os
from pathlib import Path
import numpy as np

TOP_K=8
COMPETITIVE_MULT=1.15

def rows_to_map(rows):
    out={}
    for r in rows:
        t=str(r["target"])
        out[t]={
            "target":t,
            "actual":float(r["actual"]),
            "forecast":float(r["forecast"]),
            "rw":float(r.get("rw",np.nan)),
        }
    return out

def load_json(path):
    return json.loads(Path(path).read_text())

def add_model(models,name,rows,source):
    m=rows_to_map(rows)
    if len(m)!=33:
        raise RuntimeError(f"{name}: expected 33 DEV rows, got {len(m)} from {source}")
    models[name]={"rows":m,"source":source}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--reference-rows",required=True)
    ap.add_argument("--inputs-dir",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--output-md",required=True)
    a=ap.parse_args()

    models={}

    # Cross-family exact rows already retained in repository.
    ref=load_json(a.reference_rows)
    for name,pack in ref["models"].items():
        add_model(models,name,pack["dev"],a.reference_rows)

    # RBFNN DE-ABC
    p=glob.glob(os.path.join(a.inputs_dir,"**","rbfnn_stage1_de_abc_result.json"),recursive=True)[0]
    d=load_json(p); add_model(models,"DE_ABC_RBFNN",d["dev"]["rows"],p)

    # GPR/MOGP leader
    p=glob.glob(os.path.join(a.inputs_dir,"**","gpr_lmc2_rbf_m32_result.json"),recursive=True)[0]
    d=load_json(p); add_model(models,"LMC2_RBF_M32",d["dev"]["rows"],p)

    # PLS1
    p=glob.glob(os.path.join(a.inputs_dir,"**","gold_monthly_challenger_b_pls1_v1_result.json"),recursive=True)[0]
    d=load_json(p); add_model(models,"PLS1_V1",d["dev"]["rows"],p)

    # SVR: include all five representation variants, not only leader.
    p=glob.glob(os.path.join(a.inputs_dir,"**","gold_monthly_svr_dwt_stage2b_representation_v1_result.json"),recursive=True)[0]
    d=load_json(p)
    for key,pack in d["results"].items():
        add_model(models,f"SVR_{key}",pack["rows"],p)

    # Boosting canonical structural pool.
    p=glob.glob(os.path.join(a.inputs_dir,"**","gold_monthly_boosting_stage1_canonical_v1_result.json"),recursive=True)[0]
    d=load_json(p)
    for key,pack in d["models"].items():
        add_model(models,f"BOOST_{key}",pack["rows"],p)

    # CNN/LSTM Stage-1A artifacts (six variants).
    for p in sorted(glob.glob(os.path.join(a.inputs_dir,"**","gold_monthly_cnn_lstm_stage1a_*_v1_result.json"),recursive=True)):
        d=load_json(p)
        mid=d.get("model_id") or Path(p).stem
        add_model(models,f"SEQ_{mid}",d["dev"]["rows"],p)

    targets=sorted(next(iter(models.values()))["rows"].keys())
    for name,pack in models.items():
        if sorted(pack["rows"].keys())!=targets:
            raise RuntimeError(f"target mismatch: {name}")
    # Validate actuals are identical across models.
    for t in targets:
        vals={round(pack["rows"][t]["actual"],10) for pack in models.values()}
        if len(vals)!=1:
            raise RuntimeError(f"actual mismatch {t}: {vals}")

    # Core matrices.
    names=sorted(models)
    ae={}
    se={}
    metrics={}
    top8={}
    robust_outliers={}
    for name in names:
        arr=[]
        sarr=[]
        for t in targets:
            r=models[name]["rows"][t]
            s=float(r["forecast"]-r["actual"])
            sarr.append(s); arr.append(abs(s))
        x=np.asarray(arr,float); sx=np.asarray(sarr,float)
        ae[name]=dict(zip(targets,map(float,x)))
        se[name]=dict(zip(targets,map(float,sx)))
        q1,q3=np.quantile(x,[.25,.75]); iqr=q3-q1
        ro=float(q3+1.5*iqr)
        order=np.argsort(-x)
        top8[name]=[targets[i] for i in order[:TOP_K]]
        robust_outliers[name]=[targets[i] for i,v in enumerate(x) if v>ro]
        metrics[name]={
            "sum_ae":float(x.sum()),
            "mae":float(x.mean()),
            "median_ae":float(np.median(x)),
            "rmse":float(np.sqrt(np.mean(sx*sx))),
            "worst_ae":float(x.max()),
            "worst_month":targets[int(np.argmax(x))],
            "q1_ae":float(q1),"q3_ae":float(q3),"iqr_ae":float(iqr),
            "robust_outlier_threshold":ro,
            "robust_outlier_months":robust_outliers[name],
        }

    if "ChHHO_ANFIS" not in models:
        raise RuntimeError("ChHHO_ANFIS missing")
    base="ChHHO_ANFIS"
    base_sae=metrics[base]["sum_ae"]
    competitive=[n for n in names if metrics[n]["sum_ae"]<=COMPETITIVE_MULT*base_sae]
    broad=names

    # Pairwise correlations for competitive pool.
    corr_signed={}
    corr_abs={}
    for n in competitive:
        x=np.asarray([se[base][t] for t in targets])
        y=np.asarray([se[n][t] for t in targets])
        ax=np.abs(x); ay=np.abs(y)
        corr_signed[n]=float(np.corrcoef(x,y)[0,1]) if np.std(y)>0 else None
        corr_abs[n]=float(np.corrcoef(ax,ay)[0,1]) if np.std(ay)>0 else None

    # Month consensus and rescue structure.
    base_worst=top8[base]
    month_rows=[]
    for t in targets:
        b=ae[base][t]
        alt=[n for n in competitive if n!=base]
        vals=[(ae[n][t],n) for n in alt]
        vals.sort()
        best_ae,best_model=vals[0]
        better=[n for n in alt if ae[n][t] < b]
        top_broad=sum(t in top8[n] for n in broad)
        top_comp=sum(t in top8[n] for n in competitive)
        month_rows.append({
            "target":t,
            "actual":models[base]["rows"][t]["actual"],
            "chhho_forecast":models[base]["rows"][t]["forecast"],
            "chhho_ae":b,
            "broad_top8_count":top_broad,
            "broad_top8_share":top_broad/len(broad),
            "competitive_top8_count":top_comp,
            "competitive_top8_share":top_comp/len(competitive),
            "competitive_median_ae":float(np.median([ae[n][t] for n in competitive])),
            "best_alternative_model":best_model,
            "best_alternative_ae":best_ae,
            "oracle_improvement_vs_chhho":float(b-best_ae),
            "alternatives_better_than_chhho":len(better),
            "alternatives_total":len(alt),
            "is_chhho_top8":t in base_worst,
        })

    # Fixed fallback performance restricted to ChHHO top-8 months.
    fallback=[]
    for n in competitive:
        if n==base: continue
        bsum=sum(ae[base][t] for t in base_worst)
        nsum=sum(ae[n][t] for t in base_worst)
        wins=sum(ae[n][t]<ae[base][t] for t in base_worst)
        fallback.append({
            "model":n,"chhho_worst8_sum_ae":bsum,"model_sum_ae_on_same_months":nsum,
            "improvement":float(bsum-nsum),"wins":wins,"losses":TOP_K-wins
        })
    fallback.sort(key=lambda z:(-z["improvement"],-z["wins"]))

    # Oracle ceilings.
    oracle_all=0.0
    oracle_alt_all=0.0
    chosen={}
    for t in targets:
        vals=[(ae[n][t],n) for n in competitive]
        vals.sort()
        oracle_all+=vals[0][0]
        chosen[t]=vals[0][1]
        alt=[(ae[n][t],n) for n in competitive if n!=base]
        alt.sort()
        oracle_alt_all+=min(ae[base][t],alt[0][0])
    base_worst_sum=sum(ae[base][t] for t in base_worst)
    oracle_worst8=sum(min(ae[n][t] for n in competitive) for t in base_worst)
    hybrid_worst8_total=base_sae-base_worst_sum+oracle_worst8

    # How many ChHHO worst months are also worst for most competitive models?
    shared=[]
    for t in base_worst:
        c=sum(t in top8[n] for n in competitive)
        shared.append({
            "target":t,"count":c,"share":c/len(competitive),
            "chhho_ae":ae[base][t],
            "best_alt_model":next(r["best_alternative_model"] for r in month_rows if r["target"]==t),
            "best_alt_ae":next(r["best_alternative_ae"] for r in month_rows if r["target"]==t),
            "oracle_improvement":next(r["oracle_improvement_vs_chhho"] for r in month_rows if r["target"]==t),
            "alternatives_better":next(r["alternatives_better_than_chhho"] for r in month_rows if r["target"]==t),
        })
    shared.sort(key=lambda z:-z["chhho_ae"])

    # Rank common hard months by competitive consensus.
    consensus=sorted(month_rows,key=lambda z:(-z["competitive_top8_share"],-z["competitive_median_ae"]))

    result={
      "schema":"GOLD_MONTHLY_CROSS_MODEL_ERROR_OVERLAP_V1_2026-09-29",
      "scope":{
        "dev":"2022-04..2024-12",
        "n_months":33,
        "broad_model_count":len(broad),
        "competitive_rule":f"DEV ΣAE <= {COMPETITIVE_MULT:.2f} × ChHHO ΣAE",
        "competitive_model_count":len(competitive),
        "top_error_definition":f"model-specific worst {TOP_K} of 33 months",
        "robust_outlier_definition":"AE > Q3 + 1.5×IQR for each model",
        "purpose":"test whether major forecast failures are common across models and whether a side-model/router has theoretical rescue capacity",
        "no_2025_or_2026_selection":True,
      },
      "models":metrics,
      "competitive_models":competitive,
      "top8_by_model":top8,
      "robust_outliers_by_model":robust_outliers,
      "competitive_corr_signed_error_vs_chhho":corr_signed,
      "competitive_corr_abs_error_vs_chhho":corr_abs,
      "chhho_worst8":shared,
      "fixed_fallback_on_chhho_worst8":fallback,
      "month_analysis":month_rows,
      "hard_month_consensus":consensus,
      "oracle":{
        "chhho_sum_ae":base_sae,
        "best_of_competitive_each_month_sum_ae":float(oracle_all),
        "oracle_improvement_all_months":float(base_sae-oracle_all),
        "chhho_worst8_sum_ae":float(base_worst_sum),
        "oracle_best_on_chhho_worst8_sum_ae":float(oracle_worst8),
        "hybrid_only_switch_on_chhho_worst8_total_sum_ae":float(hybrid_worst8_total),
        "hybrid_improvement_vs_chhho":float(base_sae-hybrid_worst8_total),
        "oracle_best_model_by_month":chosen,
      }
    }

    Path(a.output_json).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")

    # Report
    md=[]
    md.append("# GOLD MONTHLY — CROSS-MODEL ERROR OVERLAP / ROUTER VIABILITY V1")
    md.append("")
    md.append("**Date:** 2026-09-29  ")
    md.append("**Scope:** DEV 2022-04..2024-12 only; no 2025/2026 selection.")
    md.append("")
    md.append(f"Broad exact-row pool: **{len(broad)} models**. Competitive pool: **{len(competitive)} models**, defined before month-level conclusions as DEV ΣAE ≤ 1.15× ChHHO.")
    md.append("")
    md.append("## Competitive pool")
    md.append("")
    md.append("| Model | DEV ΣAE | Worst month | Worst AE | Signed-error corr vs ChHHO | AE corr vs ChHHO |")
    md.append("|---|---:|---|---:|---:|---:|")
    for n in sorted(competitive,key=lambda x:metrics[x]["sum_ae"]):
        md.append(f"| {n} | {metrics[n]['sum_ae']:.3f} | {metrics[n]['worst_month']} | {metrics[n]['worst_ae']:.2f} | {corr_signed[n]:.3f} | {corr_abs[n]:.3f} |")
    md.append("")
    md.append("## ChHHO worst 8 months — can another competitive model rescue them?")
    md.append("")
    md.append("| Month | ChHHO AE | Competitive top-8 consensus | Best alternative | Best alt AE | Oracle gain | # alternatives beating ChHHO |")
    md.append("|---|---:|---:|---|---:|---:|---:|")
    for z in shared:
        md.append(f"| {z['target']} | {z['chhho_ae']:.2f} | {z['count']}/{len(competitive)} | {z['best_alt_model']} | {z['best_alt_ae']:.2f} | {z['oracle_improvement']:.2f} | {z['alternatives_better']}/{len(competitive)-1} |")
    md.append("")
    md.append("## Fixed single fallback on exactly ChHHO's worst 8 months")
    md.append("")
    md.append("| Alternative | Sum AE on those 8 months | Improvement vs ChHHO | Wins / 8 |")
    md.append("|---|---:|---:|---:|")
    for z in fallback:
        md.append(f"| {z['model']} | {z['model_sum_ae_on_same_months']:.2f} | {z['improvement']:.2f} | {z['wins']}/8 |")
    md.append("")
    md.append("## Oracle ceiling (diagnostic only; not a deployable result)")
    md.append("")
    md.append(f"- ChHHO DEV ΣAE: **{base_sae:.3f}**")
    md.append(f"- Perfect hindsight best competitive model each month: **{oracle_all:.3f}** (ceiling gain **{base_sae-oracle_all:.3f}**) ")
    md.append(f"- ChHHO worst-8 contribution: **{base_worst_sum:.3f}**")
    md.append(f"- If perfect hindsight switching were allowed only on those 8 months, total DEV ΣAE would be **{hybrid_worst8_total:.3f}** (ceiling gain **{base_sae-hybrid_worst8_total:.3f}**)")
    md.append("")
    md.append("## Highest cross-model hard-month consensus")
    md.append("")
    md.append("| Month | Competitive top-8 share | ChHHO AE | Competitive median AE | Best alternative |")
    md.append("|---|---:|---:|---:|---|")
    for z in consensus[:12]:
        md.append(f"| {z['target']} | {z['competitive_top8_count']}/{len(competitive)} | {z['chhho_ae']:.2f} | {z['competitive_median_ae']:.2f} | {z['best_alternative_model']} ({z['best_alternative_ae']:.2f}) |")
    md.append("")
    md.append("## Interpretation rule")
    md.append("")
    md.append("- If ChHHO's worst months are also top-error months for nearly all competitive models and even the oracle gain is small, a side-model/router has little value.")
    md.append("- If several ChHHO worst months are materially rescued by other competitive models, there is real complementarity; the next question becomes whether that rescue can be predicted **before** the target month using origin-safe information.")
    md.append("- Oracle figures are diagnostic upper bounds only and must never be reported as a valid deployable forecast result.")
    Path(a.output_md).write_text("\n".join(md)+"\n")

    print("CROSS_MODEL_ERROR_OVERLAP_GATE=PASS")
    print(json.dumps({
      "broad_model_count":len(broad),
      "competitive_model_count":len(competitive),
      "competitive_models":competitive,
      "chhho_worst8":shared,
      "best_fixed_fallback":fallback[0] if fallback else None,
      "oracle":result["oracle"],
      "top_consensus":[{"target":z["target"],"count":z["competitive_top8_count"],"share":z["competitive_top8_share"]} for z in consensus[:10]],
    },sort_keys=True))

if __name__=="__main__": main()
