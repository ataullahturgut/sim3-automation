from __future__ import annotations
"""Frozen paired audit; no training and no transport-period selection."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np

ARMS=("GPR_PIT_CURRENT8","NO_GPR_EQUAL","NO_GPR_FIXED_RECENCY")
EXPECTED_HASH="2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb"

def load(folder):
    out={}
    for arm in ARMS:
        q=Path(folder)/f"gpr_weight_{arm}.json"
        blob=q.read_bytes()
        d=json.loads(blob)
        assert d["schema"]=="GOLD_MONTHLY_CHHHO_GPR_WEIGHT_ABLATION_V1"
        assert d["arm"]==arm
        assert len(d["dev"]["rows"])==33
        assert d["data_authority"]["snapshot_payload_sha256"]==EXPECTED_HASH
        assert d["data_authority"]["feature_dimension"]==8
        assert d["data_authority"]["model"]=="CHHHO_ANFIS_UNCHANGED"
        assert not d["data_authority"]["2025_used_for_selection"]
        if arm=="GPR_PIT_CURRENT8":
            assert d["canonical_parity"]["pass"]
        d["file_sha256"]=hashlib.sha256(blob).hexdigest()
        out[arm]=d
    return out

def summarize(data):
    rows={k:{r["target"]:r for r in v["dev"]["rows"]} for k,v in data.items()}
    months=sorted(rows[ARMS[0]])
    assert len(months)==33 and months[0]=="2022-04" and months[-1]=="2024-12"
    metrics={}
    for arm in ARMS:
        assert sorted(rows[arm])==months
        ea=np.array([abs(rows[arm][t]["forecast"]-rows[arm][t]["actual"]) for t in months])
        basey=np.array([rows[arm][t]["actual"] for t in months])
        assert all(abs(rows[arm][t]["actual"]-rows[ARMS[0]][t]["actual"])<1e-10 for t in months)
        assert all(abs(rows[arm][t]["rw"]-rows[ARMS[0]][t]["rw"])<1e-10 for t in months)
        correct=sum(
            np.sign(rows[arm][t]["forecast"]-rows[arm][t]["rw"])==
            np.sign(rows[arm][t]["actual"]-rows[arm][t]["rw"])
            for t in months)
        orig=data[arm]["dev"]["metrics"]
        assert abs(float(np.sum(ea))-orig["sum_abs_error"])<1e-5
        assert correct==orig["direction_correct"]
        metrics[arm]={
            "sum_abs_error":float(ea.sum()),"mae":float(ea.mean()),
            "direction_correct":int(correct),"direction_accuracy":float(correct/33),
            "n":33,"by_year":{y:float(sum(ea[i] for i,t in enumerate(months) if t.startswith(y))) for y in ("2022","2023","2024")},
            "absolute_error_by_month":{t:float(e) for t,e in zip(months,ea)},
        }
    base=metrics[ARMS[0]]
    paired={}
    for alt in ARMS[1:]:
        improvement=np.array([metrics[alt]["absolute_error_by_month"][t]-base["absolute_error_by_month"][t] for t in months])
        years={y:metrics[alt]["by_year"][y]-base["by_year"][y] for y in ("2022","2023","2024")}
        wins=int((improvement>1e-10).sum())
        losses=int((improvement< -1e-10).sum())
        median=float(np.median(improvement))
        direction=base["direction_correct"]-metrics[alt]["direction_correct"]
        paired[alt]={
            "gpr_lower_error_by_usd":float(improvement.sum()),
            "gpr_direction_advantage_correct_months":int(direction),
            "gpr_wins":wins,"gpr_losses":losses,
            "median_monthly_gpr_advantage":median,
            "yearly_gpr_error_advantage":years,
            "gpr_better_in_2_of_3_dev_years":int(sum(v>0 for v in years.values()))>=2,
            "all_predeclared_robust_gates":bool(improvement.sum()>0 and direction>=0 and wins>=losses and median>0 and sum(v>0 for v in years.values())>=2),
        }
    return {
        "schema":"GOLD_MONTHLY_CHHHO_GPR_WEIGHT_ABLATION_PAIRED_V1",
        "status":"DEV_ONLY_NO_POST_HOC_MODEL_PROMOTION",
        "authoritative_n":33,"months":months,"metrics":metrics,
        "paired_versus_gpr":paired,"source_sha256":{arm:data[arm]["file_sha256"] for arm in ARMS},
        "readiness":{"2025":"NOT_RUN","2026":"NOT_RUN","full_out_of_sample_proof":False},
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    d=summarize(load(args.input_dir))
    Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("GPR_PAIRED_SUMMARY_GATE=PASS")
    print(json.dumps({"n":d["authoritative_n"],"metrics":{k:{x:v[x] for x in ("sum_abs_error","direction_correct")} for k,v in d["metrics"].items()},"paired":d["paired_versus_gpr"]},sort_keys=True))

if __name__=="__main__":main()
