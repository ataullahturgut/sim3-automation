from __future__ import annotations
import argparse, json
from pathlib import Path
import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_fx_h10_residual_v1 as h10

# X5 compact candidate set; promotion remains DEV-only.\nCANDIDATES={
  "CNY_CPI":["usdcny_logret","cpi_surprise_last"],
  "CNY_RATES_CPI":["usdcny_logret","dgs10_change","dff_change","curve_proxy_change","cpi_surprise_last"],
  "H10_BROAD_CPI":["broad_usd_ret","cpi_surprise_last"],
  "H10_BROAD_RATES_CPI":["broad_usd_ret","dgs10_change","dff_change","curve_proxy_change","cpi_surprise_last"],
  "H10_MAJORS_CPI":["eur_usdstrength_ret","jpy_usdstrength_ret","gbp_usdstrength_ret","chf_usdstrength_ret","cny_usdstrength_ret","cpi_surprise_last"],
}
DIAGNOSTIC_ONLY={
  "H10_MAJORS_RATES_CPI":["eur_usdstrength_ret","jpy_usdstrength_ret","gbp_usdstrength_ret","chf_usdstrength_ret","cny_usdstrength_ret",
                           "dgs10_change","dff_change","curve_proxy_change","cpi_surprise_last"]
}

def load_snapshot(path):
    d=json.loads(Path(path).read_text())
    ext={}
    for r in d["rows"]:
        ext[r["origin_month"]]={k:float(v) for k,v in r.items() if k!="origin_month" and v is not None}
    return d,ext

def merge_ext(*dicts):
    keys=set().union(*[set(d) for d in dicts])
    out={}
    for k in keys:
        z={}
        for d in dicts:
            z.update(d.get(k,{}))
        out[k]=z
    return out

def run(chhho,deabc,pit,inflation,outdir):
    pitdoc,pitext=load_snapshot(pit)
    infdoc,infext=load_snapshot(inflation)
    h10ext,h10blocks,h10src=h10.build()
    ext=merge_ext(pitext,infext,h10ext)
    models=[core.load_model(chhho,"ChHHO-ANFIS"),core.load_model(deabc,"DE-ABC-RBFNN")]
    result={
      "schema":"GOLD_MONTHLY_EXTERNAL_COMPACT_PANEL_V1_2026-09-28",
      "authority":{
        "selection":"DEV_2022-04..2024-12_ONLY",
        "2025":"FROZEN_REPORTING_ONLY",
        "random_split":False,
        "base_models_frozen":True,
        "risk_block_excluded_from_promotion":"NO_ORIGINAL_PIT_STORAGE_PROOF",
        "commodity_block":"DATA_NOT_READY",
        "candidate_set":"PREDECLARED_FROM_X3_SINGLE_BLOCK_PASS_RESULTS",
        "min_prior_residuals":core.MIN_HISTORY,
        "ridge_alpha_fixed":core.RIDGE_ALPHA,
        "correction_cap_mult":core.CAP_MULT
      },
      "sources":{
        "pit_schema":pitdoc["schema"],
        "inflation_schema":infdoc["schema"],
        "h10":"Federal Reserve Board H.10 DDP",
        "h10_release_lag_days":h10.LAG_DAYS,
        "h10_source":h10src
      },
      "candidates":CANDIDATES,
      "diagnostic_only_candidates":DIAGNOSTIC_ONLY,
      "models":{}
    }
    for m in models:
        mr={"base_dev":core.metrics(m["dev"]),"base_2025":core.metrics(m["tr"]),"candidates":{}}
        eligible=[]
        for name,cols in CANDIDATES.items():
            corr=core.prequential(m["dev"],ext,cols)
            gate=core.stability_gate(m["dev"],corr)
            mr["candidates"][name]={
              "columns":cols,
              "full_metrics":core.metrics(corr,"corrected_forecast"),
              "gate":gate,
              "diagnostics":core.diagnostic(m["dev"],ext,cols),
              "rows":corr,
              "promotion_eligible":True
            }
            if gate.get("pass"):
                eligible.append((gate["eligible_corrected"]["sum_ae"],name))
        for name,cols in DIAGNOSTIC_ONLY.items():
            corr=core.prequential(m["dev"],ext,cols)
            gate=core.stability_gate(m["dev"],corr)
            mr["candidates"][name]={
              "columns":cols,
              "full_metrics":core.metrics(corr,"corrected_forecast"),
              "gate":gate,
              "diagnostics":core.diagnostic(m["dev"],ext,cols),
              "rows":corr,
              "promotion_eligible":False,
              "reason":"FEATURE_COUNT_TOO_HIGH_FOR_PRIMARY_SMALL_N_PROMOTION"
            }
        eligible.sort()
        selected=eligible[0][1] if eligible else "BASE"
        mr["selected_on_dev"]=selected
        if selected=="BASE":
            mr["transport_2025"]={"selected":"BASE","metrics":core.metrics(m["tr"]),"rows":m["tr"],"fit":None}
        else:
            tr,fit=core.freeze_fit_apply(m["dev"],m["tr"],ext,CANDIDATES[selected])
            mr["transport_2025"]={"selected":selected,"metrics":core.metrics(tr,"corrected_forecast"),"rows":tr,"fit":fit}
        # Tail diagnostics on final selected vs base
        if selected!="BASE":
            tr=mr["transport_2025"]["rows"]
            base=m["tr"]
            base_ae=[abs(r["forecast"]-r["actual"]) for r in base]
            new_ae=[abs(r["corrected_forecast"]-r["actual"]) for r in tr]
            mr["transport_2025"]["tail"]={
              "base_worst_ae":max(base_ae),"new_worst_ae":max(new_ae),
              "months_improved":sum(n<b for n,b in zip(new_ae,base_ae)),
              "months_worsened":sum(n>b for n,b in zip(new_ae,base_ae))
            }
        result["models"][m["name"]]=mr
    result["result_sha256"]=core.sha({k:v for k,v in result.items() if k!="result_sha256"})
    d=Path(outdir);d.mkdir(parents=True,exist_ok=True)
    (d/"gold_monthly_external_compact_panel_result.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    lines=["# GOLD MONTHLY EXTERNAL COMPACT PANEL — FINAL X5/X6 RESULT",""]
    for name,m in result["models"].items():
        lines += [f"## {name}",f"- Base DEV ΣAE: {m['base_dev']['sum_ae']:.4f}",
                  f"- DEV-selected compact panel: **{m['selected_on_dev']}**",
                  f"- Base 2025 ΣAE: {m['base_2025']['sum_ae']:.4f}",
                  f"- Frozen compact-panel 2025 ΣAE: {m['transport_2025']['metrics']['sum_ae']:.4f}","",
                  "| Candidate | Eligible DEV ΔΣAE | 2024 ΔΣAE | Gate | Promotion |",
                  "|---|---:|---:|---|---|"]
        for cand,v in m["candidates"].items():
            g=v["gate"]
            if "eligible_sum_ae_improvement" in g:
                lines.append(f"| {cand} | {g['eligible_sum_ae_improvement']:.4f} | {g['y2024_sum_ae_improvement']:.4f} | {'PASS' if g['pass'] else 'FAIL'} | {'YES' if v['promotion_eligible'] else 'NO'} |")
        if "tail" in m["transport_2025"]:
            t=m["transport_2025"]["tail"]
            lines += ["",f"- 2025 months improved: {t['months_improved']}/12",
                      f"- 2025 months worsened: {t['months_worsened']}/12",
                      f"- 2025 worst AE: {t['base_worst_ae']:.4f} -> {t['new_worst_ae']:.4f}"]
        lines.append("")
    lines += ["## Final governance",
              "- No candidate or feature was selected using 2025 outcomes.",
              "- Risk appetite excluded from promotable compact panel because original PIT storage proof is absent.",
              "- Commodity/oil remains DATA_NOT_READY.",
              "- Base ChHHO-ANFIS and DE-ABC-RBFNN are unchanged; this tests an external residual-correction layer.",
              "- 2025 is frozen transport/reporting only."]
    (d/"GOLD_MONTHLY_EXTERNAL_COMPACT_PANEL_FINAL_2026-09-28.md").write_text("\n".join(lines)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({n:{
      "selected":m["selected_on_dev"],
      "base_dev":m["base_dev"]["sum_ae"],
      "base_2025":m["base_2025"]["sum_ae"],
      "new_2025":m["transport_2025"]["metrics"]["sum_ae"],
      "direction_2025":m["transport_2025"]["metrics"]["direction_correct"],
      "tail":m["transport_2025"].get("tail")
    } for n,m in result["models"].items()},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--chhho",required=True);p.add_argument("--deabc",required=True)
    p.add_argument("--pit",required=True);p.add_argument("--inflation",required=True)
    p.add_argument("--outdir",default="external_compact_out")
    a=p.parse_args();run(a.chhho,a.deabc,a.pit,a.inflation,a.outdir)
