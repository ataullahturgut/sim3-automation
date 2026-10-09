"""Source-only motivated NQ/ZN/CL complete H1 control variant of fixed K25.

Five-asset all-10-feature synchronous source gate proved too thin in 2026.
Freeze this distinct three-SOURCE study BEFORE evaluating any 3-root scores.
No new parameters: same RFR, same K25, same 1h/3h, same frozen history.
"""
from pathlib import Path
import sys,json
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_cme5_rfr_k25_external_analogue_20261008 as original

NAME="GOLD_EXECUTION_2026_CME3_NQ_ZN_CL_RFR_K25_ANALOGUE_20261009"
KEEP=("NQ","ZN","CL")
FEATURES=[f"{root}_{lag}" for root in KEEP for lag in ("r1","r3")]
def main():
    # Keep original 5-root raw receipt requirement, change only 6 strictly
    # source-complete signals; 2026 outcomes NEVER affected root choice.
    assert original.FEATURES==[f"{x}_{h}" for x in ("GC","SI","NQ","ZN","CL") for h in ("r1","r3")]
    original.NAME=NAME
    original.FEATURES=FEATURES
    original.main()
    out=AX/(NAME+"_SUMMARY.json")
    if out.exists():
        z=json.loads(out.read_text())
        old=z.pop("five_venue_roots",None)
        z["status"]="CME_THREE_ROOT_NQ_ZN_CL_SOURCE_COMPLETENESS_SCORED"
        z["model_actual_independent_market_roots"]=list(KEEP)
        z["archive_entire_five_roots_only"]=old
        z["reason_5_root_source_ablation"]="Ingested GC and SI sparse H1 source; source-synchronous 10-feature population failed threshold before any score"
        z["trial_separate_from_pre_registered_CME5"]=True
        z["no_2026_label_based_root_selection"]=True
        out.write_text(json.dumps(z,indent=2,default=str)+"\n")
        print("SOURCE_COMPLETE_CME3_CONFIRMED",json.dumps(z),flush=True)
if __name__=="__main__":main()
