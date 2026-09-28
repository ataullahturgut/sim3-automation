from __future__ import annotations
import argparse, json
from pathlib import Path
import gold_monthly_external_driver_residual_v1 as core

BLOCKS={
 "PIT_FX_CNY":["usdcny_logret"],
 "PIT_RATES":["dgs10_change","dff_change","curve_proxy_change"],
 "PIT_COMBINED":["usdcny_logret","dgs10_change","dff_change","curve_proxy_change"],
}

def load_ext(path):
    d=json.loads(Path(path).read_text())
    ext={}
    for r in d["rows"]:
        ext[r["origin_month"]]={k:float(v) for k,v in r.items() if k!="origin_month" and v is not None}
    return d,ext

def run(chhho,deabc,external,outdir):
    snap,ext=load_ext(external)
    models=[core.load_model(chhho,"ChHHO-ANFIS"),core.load_model(deabc,"DE-ABC-RBFNN")]
    out={"schema":"GOLD_MONTHLY_EXTERNAL_PIT_RESIDUAL_V1_2026-09-28",
         "external_snapshot_schema":snap["schema"],
         "evidence_class":snap["evidence_class"],
         "authority":{"selection":"DEV_ONLY","2025":"FROZEN_REPORTING_ONLY",
                      "random_split":False,"neon_reads_in_model_run":0,
                      "base_models_frozen":True},
         "blocks":BLOCKS,"models":{}}
    for m in models:
        mr={"base_dev":core.metrics(m["dev"]),"base_2025":core.metrics(m["tr"]),
            "dev_blocks":{}}
        candidates=[]
        for b,cols in BLOCKS.items():
            corr=core.prequential(m["dev"],ext,cols)
            gate=core.stability_gate(m["dev"],corr)
            mr["dev_blocks"][b]={"columns":cols,
                "diagnostics":core.diagnostic(m["dev"],ext,cols),
                "full_metrics":core.metrics(corr,"corrected_forecast"),
                "gate":gate,"rows":corr}
            if gate.get("pass"):
                candidates.append((gate["eligible_corrected"]["sum_ae"],b))
        candidates.sort()
        sel=candidates[0][1] if candidates else "BASE"
        mr["selected_on_dev"]=sel
        if sel=="BASE":
            mr["transport_2025"]={"selected":"BASE","metrics":core.metrics(m["tr"]),"rows":m["tr"],"fit":None}
        else:
            tr,fit=core.freeze_fit_apply(m["dev"],m["tr"],ext,BLOCKS[sel])
            mr["transport_2025"]={"selected":sel,"metrics":core.metrics(tr,"corrected_forecast"),"rows":tr,"fit":fit}
        out["models"][m["name"]]=mr
    out["result_sha256"]=core.sha({k:v for k,v in out.items() if k!="result_sha256"})
    d=Path(outdir);d.mkdir(parents=True,exist_ok=True)
    (d/"gold_monthly_external_pit_result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    lines=["# GOLD MONTHLY STRICT-PIT EXTERNAL RESULT",""]
    for n,m in out["models"].items():
        lines += [f"## {n}",f"- Base DEV ΣAE: {m['base_dev']['sum_ae']:.4f}",
                  f"- Selected on DEV: **{m['selected_on_dev']}**",
                  f"- Base 2025 ΣAE: {m['base_2025']['sum_ae']:.4f}",
                  f"- Frozen 2025 ΣAE: {m['transport_2025']['metrics']['sum_ae']:.4f}","",
                  "| Block | Eligible DEV ΔΣAE | 2024 ΔΣAE | Gate |","|---|---:|---:|---|"]
        for b in BLOCKS:
            g=m["dev_blocks"][b]["gate"]
            if "eligible_sum_ae_improvement" in g:
                lines.append(f"| {b} | {g['eligible_sum_ae_improvement']:.4f} | {g['y2024_sum_ae_improvement']:.4f} | {'PASS' if g['pass'] else 'FAIL'} |")
        lines.append("")
    lines += ["## Governance","- External features sourced from compact Neon replay snapshot.",
              "- Base models are unchanged.","- Prequential DEV correction uses prior residuals only.",
              "- 2025 is never used for selection or fitting decisions beyond frozen DEV fit.","- Model run performs zero Neon reads."]
    (d/"GOLD_MONTHLY_EXTERNAL_PIT_RESULT_2026-09-28.md").write_text("\n".join(lines)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({n:{"selected":m["selected_on_dev"],"base_dev":m["base_dev"]["sum_ae"],
                         "base_2025":m["base_2025"]["sum_ae"],
                         "transport_2025":m["transport_2025"]["metrics"]["sum_ae"]}
                      for n,m in out["models"].items()},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--chhho",required=True);p.add_argument("--deabc",required=True)
    p.add_argument("--external",required=True);p.add_argument("--outdir",default="external_pit_out")
    a=p.parse_args();run(a.chhho,a.deabc,a.external,a.outdir)
