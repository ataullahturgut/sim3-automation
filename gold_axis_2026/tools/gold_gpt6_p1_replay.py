"""P1 auditable YEAR-window XAU future-price/logreturn DST baseline, no external dependencies."""
import csv,json,math,datetime
from zoneinfo import ZoneInfo
from pathlib import Path
D=Path(__file__).resolve().parents[1]
def main():
    rows=[]
    for y in range(2020,2026):
        with (D/f"GOLD_GPT6_P1_SESSION_RET_{y}.csv").open(newline="") as f:
            for r in csv.DictReader(f):
                iso=r["issue_utc"].replace("Z","+00:00")
                r["year"]=y
                r["r"]=float(r["realized_r"])
                r["entry"]=float(r["entry"]);r["exit"]=float(r["exit"])
                r["y"]=int(r["r"]>0)
                r["dst"]=bool(datetime.datetime.fromisoformat(iso).astimezone(ZoneInfo("America/New_York")).dst())
                assert abs(math.log(r["exit"]/r["entry"])-r["r"])<1e-11
                assert (int(r["n"]),int(r["n15"]),int(r["n75"]))==((31,30,0) if r["sn"]=="DAY" else (61,59,1))
                rows.append(r)
    assert len(rows)==2740
    rows.sort(key=lambda r:(r["trade_date"],r["sn"]))
    with (D/"GOLD_GPT6_P1_SCORE_ROWS.csv").open(newline="") as f:
        scored={(r["day"],r["sn"]):r for r in csv.DictReader(f)}
    assert len(scored)==1366
    n=0
    for r in rows:
        if r["year"]<2023:continue
        history=[x for x in rows if x["sn"]==r["sn"] and x["year"]<2025 and (r["year"]==2025 or x["trade_date"]<r["trade_date"])]
        assert len(history)>=200
        expected=scored[r["trade_date"],r["sn"]]
        assert int(expected["ntrain"])==len(history)
        for k in ("BASE","DST"):
            train=[x for x in history if k=="BASE" or x["dst"]==r["dst"]]
            up=sum(x["y"] for x in train);prob=(up+2)/(len(train)+4)
            ret=sum(x["r"] for x in train)/len(train)
            got={"p":prob,"rpred":ret,"class":int(prob>=.5),"brier":(prob-r["y"])**2,
                 "logloss":-r["y"]*math.log(prob)-(1-r["y"])*math.log(1-prob),
                 "r2":(ret-r["r"])**2,"price_ae":abs(r["entry"]*math.exp(ret)-r["exit"])}
            for field,value in got.items():
                assert abs(float(expected[k+"_"+field])-value)<1e-8,(r["trade_date"],k,field)
        n+=1
    assert n==1366
    stats=json.loads((D/"GOLD_GPT6_P1_RESULT.json").read_text())
    assert stats["conclusion"]=="BASELINE_ONLY_NO_NEW_EDGE"
    print("P1 PASS: 2740 source windows, 1366 causal DST model scores; no incremental DST edge.")
if __name__=="__main__":main()
