"""Independent replay of P2 frozen 47-event FOMC as-of arithmetic and paired controls."""
import csv,json,math,datetime
from pathlib import Path
D=Path(__file__).resolve().parents[1]
def read(name):
    with (D/name).open(newline="") as f:return list(csv.DictReader(f))
def main():
    ev=read("GOLD_GPT6_P2_FOMC_EVENT_PRICE_ROWS.csv")
    scored=read("GOLD_GPT6_P2_FOMC_NEXTDAY_SCORE.csv")
    assert len(ev)==len(scored)==47
    events={e["event_date"]:e for e in ev}
    ndev=0
    wins={"pre":0,"post":0};losses={"pre":0,"post":0}
    for r in scored:
        x=events[r["event"]]
        for key,p1,p0 in (("pre","p_pre15","p_pre60"),("post","p_post45","p_pre15")):
            z=math.log(float(x[p1])/float(x[p0]))
            assert abs(z-float(x["x_"+key]))<1e-10
            assert abs(z-float(r[key]))<1e-10
            pred=int(z<0)
            assert pred==int(r["pred_"+key])
            assert int(pred==int(r["actual_up"]))==int(r["correct_"+key])
        date=datetime.date.fromisoformat(r["event"])+datetime.timedelta(days=1)
        assert date.isoformat()==r["target_date"]
        actual=math.log(float(r["target"])/float(r["entry"]))
        assert abs(actual-float(r["actual_r"]))<1e-10
        assert int(actual>0)==int(r["actual_up"])
        if int(r["year"])<=2024:
            ndev+=1
            for k in ("pre","post"):
                if int(r["correct_"+k]) and not int(r["actual_up"]):wins[k]+=1
                if not int(r["correct_"+k]) and int(r["actual_up"]):losses[k]+=1
    assert ndev==39
    results=json.loads((D/"GOLD_GPT6_P2_FOMC_RESULT.json").read_text())
    assert results["verdict"]=="REJECT_NO_PROMOTION"
    for k in ("pre","post"):
        assert results["paired"][k]["win_vs_UP"]==wins[k]
        assert results["paired"][k]["loss_vs_UP"]==losses[k]
    print("P2 PASS: 47 FOMC indexed price sets, 39 DEV decisions, 8 opened transport; no robust reversal.")
if __name__=="__main__":main()
