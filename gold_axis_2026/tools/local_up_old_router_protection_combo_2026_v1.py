from __future__ import annotations
import argparse, importlib.util, json, math, sys
from pathlib import Path

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m
    assert spec.loader is not None; spec.loader.exec_module(m); return m

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--v1",type=Path,required=True)
    ap.add_argument("--v2",type=Path,required=True)
    ap.add_argument("--ledger",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    base=load("base_combo",a.base)
    v1=load("local_v1_combo",a.v1)
    v2=load("local_v2_combo",a.v2)

    rows=v1.build_rows(base)
    scored=v2.run(rows,120,0.525,0.50)
    local26={r["target_date"]:r for r in scored if r["year"]==2026}

    obj=json.loads(a.ledger.read_text(encoding="utf-8"))
    led=obj["EXPANDING"]["ledger"]
    if len(led)!=173 or len(local26)!=173:
        raise RuntimeError(f"ROW_COUNT_MISMATCH ledger={len(led)} local={len(local26)}")

    wealth=100.0; buyhold=100.0; oracle=100.0
    cash_days=gold_days=0
    down_avoided=false_exits=down_exposed=up_retained=0
    rows_out=[]
    for x in led:
        td=x["target_date"]
        lr=local26.get(td)
        if lr is None:
            raise RuntimeError(f"LOCAL_ROW_MISSING:{td}")
        ret=float(x["return"])
        actual_up=int(x["actual_up"])
        high_risk=bool(x["alert"])
        old_router_up=int(x["router_up"])==1
        local_up=int(lr["pred_up"])==1

        # User-specified hybrid:
        # Local UP overrides protection -> remain GOLD.
        # Otherwise, only HIGH-RISK + old Router abstain -> CASH.
        cash = high_risk and (not old_router_up) and (not local_up)
        action="CASH" if cash else "GOLD"

        buyhold*=math.exp(ret)
        if actual_up==1:
            oracle*=math.exp(ret)
        if cash:
            cash_days+=1
            if actual_up==0: down_avoided+=1
            else: false_exits+=1
        else:
            gold_days+=1
            wealth*=math.exp(ret)
            if actual_up==0: down_exposed+=1
            else: up_retained+=1

        rows_out.append({
            "target_date":td,"return":ret,"actual_up":actual_up,
            "sqrt_high_risk":high_risk,"old_router_up":old_router_up,
            "local_router_up":local_up,"action":action,"wealth":wealth
        })

    result={
      "identity":"GOLD_CONTROL_2026_LOCAL_UP_OLD_ROUTER_PROTECTION_COMBO_V1",
      "rule":"Default GOLD. If Local Router V2=UP stay GOLD. Otherwise if SQRT=HIGH-RISK and old Router V2=ABSTAIN move to CASH. All other states GOLD.",
      "period":"2026-01-01 through 2026-08-31",
      "n_days":len(led),
      "strategy":{
        "start_value":100.0,"final_value":wealth,"return_pct":(wealth/100-1)*100,
        "cash_days":cash_days,"gold_days":gold_days,
        "down_days_avoided":down_avoided,"false_exits_on_up_days":false_exits,
        "down_days_exposed":down_exposed,"up_days_retained":up_retained
      },
      "buy_and_hold":{"final_value":buyhold,"return_pct":(buyhold/100-1)*100},
      "oracle_up_down":{"final_value":oracle,"return_pct":(oracle/100-1)*100},
      "governance":{"2026_stress_only":True,"retuning":False,"production_writes":False,"runtime_promotion":False},
      "ledger":rows_out
    }
    p=a.out/"GOLD_CONTROL_2026_LOCAL_UP_OLD_ROUTER_PROTECTION_COMBO_V1_RESULT_2026-09-24.json"
    p.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="ledger"},indent=2))

if __name__=="__main__": main()
