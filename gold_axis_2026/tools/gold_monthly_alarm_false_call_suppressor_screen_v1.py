from __future__ import annotations
import argparse, glob, json, os
from pathlib import Path
import numpy as np

MIN_PRIOR=6
UNIONS=["T0_STANDARD","T0_ALL_VISIBLE","ANY_VISIBLE"]

def load_json(p):
    return json.loads(Path(p).read_text())

def rows_to_map(rows):
    return {str(r["target"]):{
        "target":str(r["target"]),
        "actual":float(r["actual"]),
        "forecast":float(r["forecast"]),
        "rw":float(r.get("rw",np.nan)),
    } for r in rows}

def add_model(models,name,rows,source):
    m=rows_to_map(rows)
    if len(m)!=33:
        raise RuntimeError(f"{name}: expected 33 DEV rows, got {len(m)} from {source}")
    models[name]={"rows":m,"source":source}

def load_models(reference_rows,inputs_dir):
    models={}
    ref=load_json(reference_rows)
    for name,pack in ref["models"].items():
        add_model(models,name,pack["dev"],reference_rows)

    p=glob.glob(os.path.join(inputs_dir,"**","rbfnn_stage1_de_abc_result.json"),recursive=True)[0]
    d=load_json(p); add_model(models,"DE_ABC_RBFNN",d["dev"]["rows"],p)

    p=glob.glob(os.path.join(inputs_dir,"**","gpr_lmc2_rbf_m32_result.json"),recursive=True)[0]
    d=load_json(p); add_model(models,"LMC2_RBF_M32",d["dev"]["rows"],p)

    p=glob.glob(os.path.join(inputs_dir,"**","gold_monthly_challenger_b_pls1_v1_result.json"),recursive=True)[0]
    d=load_json(p); add_model(models,"PLS1_V1",d["dev"]["rows"],p)

    p=glob.glob(os.path.join(inputs_dir,"**","gold_monthly_svr_dwt_stage2b_representation_v1_result.json"),recursive=True)[0]
    d=load_json(p)
    for key,pack in d["results"].items():
        add_model(models,f"SVR_{key}",pack["rows"],p)

    p=glob.glob(os.path.join(inputs_dir,"**","gold_monthly_boosting_stage1_canonical_v1_result.json"),recursive=True)[0]
    d=load_json(p)
    for key,pack in d["models"].items():
        add_model(models,f"BOOST_{key}",pack["rows"],p)

    for p in sorted(glob.glob(os.path.join(inputs_dir,"**","gold_monthly_cnn_lstm_stage1a_*_v1_result.json"),recursive=True)):
        d=load_json(p)
        mid=d.get("model_id") or Path(p).stem
        add_model(models,f"SEQ_{mid}",d["dev"]["rows"],p)
    return models

def q(arr,p):
    x=np.asarray(arr,float)
    return float(np.quantile(x,p))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--matrix-v2",required=True)
    ap.add_argument("--overlap",required=True)
    ap.add_argument("--reference-rows",required=True)
    ap.add_argument("--inputs-dir",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--output-md",required=True)
    a=ap.parse_args()

    mat=load_json(a.matrix_v2)
    ov=load_json(a.overlap)
    if mat.get("schema")!="GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V2_FALSE_CALL_2026-09-30":
        raise RuntimeError(("BAD_MATRIX_SCHEMA",mat.get("schema")))
    if ov.get("schema")!="GOLD_MONTHLY_CROSS_MODEL_ERROR_OVERLAP_V1_2026-09-29":
        raise RuntimeError(("BAD_OVERLAP_SCHEMA",ov.get("schema")))

    competitive=list(ov["competitive_models"])
    models=load_models(a.reference_rows,a.inputs_dir)
    missing=[n for n in competitive if n not in models]
    if missing: raise RuntimeError(("COMPETITIVE_MODELS_MISSING",missing))

    dev_rows={r["target"]:r for r in mat["rows"] if "2022-04"<=r["target"]<="2024-12"}
    targets=sorted(dev_rows)
    if len(targets)!=33: raise RuntimeError(("DEV_ROWS",len(targets)))

    feat=[]
    for t in targets:
        vals=np.array([models[n]["rows"][t]["forecast"] for n in competitive],float)
        base=models["ChHHO_ANFIS"]["rows"][t]
        rw=float(base["rw"])
        med=float(np.median(vals))
        q25,q75=np.quantile(vals,[.25,.75])
        disp=float((q75-q25)/abs(med)*100.0) if med!=0 else np.nan
        ch=float(base["forecast"])
        devpct=float(abs(ch-med)/abs(med)*100.0) if med!=0 else np.nan
        dirs=np.sign(vals-rw)
        chdir=np.sign(ch-rw)
        up=float(np.mean(dirs>0)); down=float(np.mean(dirs<0))
        agree=float(np.mean(dirs==chdir)) if chdir!=0 else float(np.mean(dirs==0))
        feat.append({
            "target":t,
            "median_fcst":med,
            "iqr_fcst":float(q75-q25),
            "dispersion_pct":disp,
            "chhho_dev_pct":devpct,
            "rw":rw,
            "up_share":up,
            "down_share":down,
            "direction_consensus":max(up,down),
            "chhho_direction_agreement":agree,
        })

    # Expanding prior-only thresholds and vetoes.
    for i,r in enumerate(feat):
        hist=feat[:i]
        r["veto_eligible"]=bool(len(hist)>=MIN_PRIOR)
        if not r["veto_eligible"]:
            for k in ["prior_disp_q25","prior_disp_median","prior_dev_q25","prior_dev_median"]:
                r[k]=None
            for k in ["V1_TIGHT_CENTRAL","V2_STRONG_DIRECTION_CONSENSUS","V3_CENTRAL_ONLY"]:
                r[k]=False
            continue
        hdisp=[x["dispersion_pct"] for x in hist]
        hdev=[x["chhho_dev_pct"] for x in hist]
        r["prior_disp_q25"]=q(hdisp,.25)
        r["prior_disp_median"]=q(hdisp,.50)
        r["prior_dev_q25"]=q(hdev,.25)
        r["prior_dev_median"]=q(hdev,.50)
        r["V1_TIGHT_CENTRAL"]=bool(
            r["dispersion_pct"]<=r["prior_disp_q25"] and
            r["chhho_dev_pct"]<=r["prior_dev_median"]
        )
        r["V2_STRONG_DIRECTION_CONSENSUS"]=bool(
            r["chhho_direction_agreement"]>=0.80 and
            r["dispersion_pct"]<=r["prior_disp_median"]
        )
        r["V3_CENTRAL_ONLY"]=bool(r["chhho_dev_pct"]<=r["prior_dev_q25"])

    fm={r["target"]:r for r in feat}
    rows=[]
    for t in targets:
        x=dict(dev_rows[t])
        x.update(fm[t])
        rows.append(x)

    candidates=["V1_TIGHT_CENTRAL","V2_STRONG_DIRECTION_CONSENSUS","V3_CENTRAL_ONLY"]
    results={}
    dev_high_total=sum(r["severity"]=="HIGH" for r in rows)
    dev_elev_total=sum(r["severity"] in ("HIGH","MEDIUM") for r in rows)

    for union in UNIONS:
        results[union]={}
        for v in candidates:
            alarms=[r for r in rows if r[union]]
            before={
                "events":len(alarms),
                "high_hits":sum(r["severity"]=="HIGH" for r in alarms),
                "medium_hits":sum(r["severity"]=="MEDIUM" for r in alarms),
                "false_calls":sum(r["severity"]=="NORMAL" for r in alarms),
            }
            suppressed=[r for r in alarms if r["veto_eligible"] and r[v]]
            kept=[r for r in alarms if not (r["veto_eligible"] and r[v])]
            after={
                "events":len(kept),
                "high_hits":sum(r["severity"]=="HIGH" for r in kept),
                "medium_hits":sum(r["severity"]=="MEDIUM" for r in kept),
                "false_calls":sum(r["severity"]=="NORMAL" for r in kept),
            }
            results[union][v]={
                "before":before,
                "after":after,
                "suppressed_total":len(suppressed),
                "suppressed_false_calls":[r["target"] for r in suppressed if r["severity"]=="NORMAL"],
                "suppressed_high_hits":[r["target"] for r in suppressed if r["severity"]=="HIGH"],
                "suppressed_medium_hits":[r["target"] for r in suppressed if r["severity"]=="MEDIUM"],
                "suppressed_detail":[{
                    "target":r["target"],"severity":r["severity"],"ape_pct":r["ape_pct"],
                    "active_signals":r["active_signals"],
                    "dispersion_pct":r["dispersion_pct"],
                    "chhho_dev_pct":r["chhho_dev_pct"],
                    "chhho_direction_agreement":r["chhho_direction_agreement"],
                } for r in suppressed],
                "before_false_call_rate":None if before["events"]==0 else before["false_calls"]/before["events"],
                "after_false_call_rate":None if after["events"]==0 else after["false_calls"]/after["events"],
                "after_high_recall_full_dev":after["high_hits"]/dev_high_total,
                "after_elevated_recall_full_dev":(after["high_hits"]+after["medium_hits"])/dev_elev_total,
            }

    # Continuous descriptive separation, no threshold fitting.
    groups={}
    for sev in ["HIGH","MEDIUM","NORMAL"]:
        z=[r for r in rows if r["ANY_VISIBLE"] and r["severity"]==sev and r["veto_eligible"]]
        groups[sev]={
            "n":len(z),
            "median_dispersion_pct":None if not z else float(np.median([r["dispersion_pct"] for r in z])),
            "median_chhho_dev_pct":None if not z else float(np.median([r["chhho_dev_pct"] for r in z])),
            "median_direction_agreement":None if not z else float(np.median([r["chhho_direction_agreement"] for r in z])),
        }

    out={
        "schema":"GOLD_MONTHLY_ALARM_FALSE_CALL_SUPPRESSOR_SCREEN_V1_2026-09-30",
        "status":"COMPLETE",
        "scope":{"dev":"2022-04..2024-12","n":33,"competitive_models":competitive,"min_prior":MIN_PRIOR},
        "features":feat,
        "rows":rows,
        "candidate_veto_results":results,
        "continuous_group_summary":groups,
        "governance":{
            "actual_used_in_veto_features":False,
            "expanding_prior_only_thresholds":True,
            "thresholds_retuned_from_alarm_outcomes":False,
            "production_veto_authorized":False,
            "forecast_modified":False,
            "routing_tested":False,
        }
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")

    md=[]
    md.append("# GOLD MONTHLY — Alarm False-Call Suppressor Screen V1\n")
    md.append("**Scope:** DEV 2022-04..2024-12; exploratory; no production veto authorized.\n")
    md.append("## Continuous consensus features among ANY_VISIBLE alarm rows\n")
    md.append("| Outcome | n | Median dispersion % | Median ChHHO deviation % | Median direction agreement |")
    md.append("|---|---:|---:|---:|---:|")
    for sev in ["HIGH","MEDIUM","NORMAL"]:
        g=groups[sev]
        def fmt(v): return "—" if v is None else f"{v:.3f}"
        md.append(f"| {sev} | {g['n']} | {fmt(g['median_dispersion_pct'])} | {fmt(g['median_chhho_dev_pct'])} | {fmt(g['median_direction_agreement'])} |")
    md.append("\n## Candidate veto results\n")
    for union in UNIONS:
        md.append(f"### {union}")
        md.append("| Veto | False removed | HIGH wrongly removed | MEDIUM wrongly removed | False rate before | False rate after |")
        md.append("|---|---:|---:|---:|---:|---:|")
        for v in candidates:
            z=results[union][v]
            md.append(f"| {v} | {len(z['suppressed_false_calls'])} | {len(z['suppressed_high_hits'])} | {len(z['suppressed_medium_hits'])} | {100*z['before_false_call_rate']:.1f}% | {100*z['after_false_call_rate']:.1f}% |")
            if z["suppressed_detail"]:
                md.append("")
                md.append("Suppressed: "+", ".join(f"{d['target']}({d['severity']})" for d in z["suppressed_detail"]))
                md.append("")
    Path(a.output_md).write_text("\n".join(md)+"\n")

    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "continuous_group_summary":groups,
        "candidate_veto_results":results
    },sort_keys=True))

if __name__=="__main__":
    main()
