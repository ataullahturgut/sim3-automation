from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import gold_monthly_external_driver_residual_v1 as core

INFLATION_BLOCKS={
 "CPI_SURPRISE":["cpi_surprise_last"],
 "CORE_CPI_SURPRISE":["core_cpi_surprise_last"],
 "CPI_SURPRISE_COMBINED":["cpi_surprise_last","core_cpi_surprise_last"],
}
RISK_BLOCKS={
 "SP500_RISK_APPETITE":["sp500_logret"],
 "EQUITY_TRIAD_RISK_APPETITE":["sp500_logret","nasdaq100_logret","djia_logret"],
}

def load_rows(path):
    d=json.loads(Path(path).read_text())
    ext={}
    for r in d["rows"]:
        ext[r["origin_month"]]={k:float(v) for k,v in r.items() if k!="origin_month" and v is not None}
    return d,ext

def evaluate_family(m,ext,blocks,strict):
    out={}
    cand=[]
    for b,cols in blocks.items():
        corr=core.prequential(m["dev"],ext,cols)
        gate=core.stability_gate(m["dev"],corr)
        out[b]={
          "columns":cols,
          "diagnostics":core.diagnostic(m["dev"],ext,cols),
          "full_metrics":core.metrics(corr,"corrected_forecast"),
          "gate":gate,
          "evidence_strength":"STRICT_REPLAY" if strict else "SECONDARY_MARKET_HISTORY",
          "rows":corr
        }
        if gate.get("pass"):
            cand.append((gate["eligible_corrected"]["sum_ae"],b))
    cand.sort()
    return out,(cand[0][1] if cand else "BASE")

def apply_if_selected(m,ext,blocks,sel):
    if sel=="BASE":
        return {"selected":"BASE","metrics":core.metrics(m["tr"]),"rows":m["tr"],"fit":None}
    tr,fit=core.freeze_fit_apply(m["dev"],m["tr"],ext,blocks[sel])
    return {"selected":sel,"metrics":core.metrics(tr,"corrected_forecast"),"rows":tr,"fit":fit}

def run(chhho,deabc,inflation,risk,outdir):
    infdoc,inf=load_rows(inflation); riskdoc,rsk=load_rows(risk)
    models=[core.load_model(chhho,"ChHHO-ANFIS"),core.load_model(deabc,"DE-ABC-RBFNN")]
    result={
      "schema":"GOLD_MONTHLY_INFLATION_RISK_RESIDUAL_V1_2026-09-28",
      "authority":{
        "selection":"DEV_ONLY","2025":"FROZEN_REPORTING_ONLY","random_split":False,
        "base_models_frozen":True,"neon_reads_in_model_run":0,
        "inflation_evidence_class":infdoc["evidence_class"],
        "risk_evidence_class":riskdoc["evidence_class"],
        "risk_promotion_authority":"DIAGNOSTIC_ONLY_DUE_NO_ORIGINAL_PIT_STORAGE_PROOF"
      },
      "inflation_blocks":INFLATION_BLOCKS,"risk_blocks":RISK_BLOCKS,"models":{}
    }
    for m in models:
        infres,infsel=evaluate_family(m,inf,INFLATION_BLOCKS,True)
        riskres,risksel=evaluate_family(m,rsk,RISK_BLOCKS,False)
        result["models"][m["name"]]={
          "base_dev":core.metrics(m["dev"]),"base_2025":core.metrics(m["tr"]),
          "inflation":{"blocks":infres,"selected_on_dev":infsel,
                       "transport_2025":apply_if_selected(m,inf,INFLATION_BLOCKS,infsel)},
          "risk":{"blocks":riskres,"selected_on_dev":risksel,
                  "transport_2025":apply_if_selected(m,rsk,RISK_BLOCKS,risksel),
                  "decision":"DIAGNOSTIC_ONLY_NOT_PROMOTABLE_WITHOUT_PIT_EVIDENCE"}
        }
    result["result_sha256"]=core.sha({k:v for k,v in result.items() if k!="result_sha256"})
    d=Path(outdir); d.mkdir(parents=True,exist_ok=True)
    (d/"gold_monthly_inflation_risk_result.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    lines=["# GOLD MONTHLY INFLATION + RISK EXTERNAL RESULT",""]
    for n,m in result["models"].items():
        lines += [f"## {n}",f"- Base DEV ΣAE: {m['base_dev']['sum_ae']:.4f}",
                  f"- Inflation selected: **{m['inflation']['selected_on_dev']}**",
                  f"- Inflation frozen 2025 ΣAE: {m['inflation']['transport_2025']['metrics']['sum_ae']:.4f}",
                  f"- Risk diagnostic selected: **{m['risk']['selected_on_dev']}**",
                  f"- Risk diagnostic 2025 ΣAE: {m['risk']['transport_2025']['metrics']['sum_ae']:.4f}",""]
        for label,key in [("Inflation","inflation"),("Risk (diagnostic only)","risk")]:
            lines += [f"### {label}","| Block | Eligible DEV ΔΣAE | 2024 ΔΣAE | Gate |","|---|---:|---:|---|"]
            for b,v in m[key]["blocks"].items():
                g=v["gate"]
                if "eligible_sum_ae_improvement" in g:
                    lines.append(f"| {b} | {g['eligible_sum_ae_improvement']:.4f} | {g['y2024_sum_ae_improvement']:.4f} | {'PASS' if g['pass'] else 'FAIL'} |")
            lines.append("")
    lines += ["## Governance","- Inflation uses release-timestamp governed first-print/consensus replay data.",
              "- Risk uses later-ingested historical market prices and is diagnostic-only.",
              "- Base models unchanged; corrections trained prequentially on prior DEV residuals.",
              "- 2025 opened only after DEV block freeze.","- Neon reads during model execution: 0."]
    (d/"GOLD_MONTHLY_INFLATION_RISK_RESULT_2026-09-28.md").write_text("\n".join(lines)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({n:{
      "inflation_selected":m["inflation"]["selected_on_dev"],
      "inflation_2025":m["inflation"]["transport_2025"]["metrics"]["sum_ae"],
      "risk_selected":m["risk"]["selected_on_dev"],
      "risk_2025":m["risk"]["transport_2025"]["metrics"]["sum_ae"]
    } for n,m in result["models"].items()},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--chhho",required=True);p.add_argument("--deabc",required=True)
    p.add_argument("--inflation",required=True);p.add_argument("--risk",required=True)
    p.add_argument("--outdir",default="inflation_risk_out")
    a=p.parse_args();run(a.chhho,a.deabc,a.inflation,a.risk,a.outdir)
