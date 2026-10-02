from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import betainc
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_relay_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

OPAL = ROOT / "gold_axis_2026" / "GOLD_H3_OPAL_V1_PREDICTIONS_2026-10-03.csv"

HAZARD = 1.0 / 20.0
MAX_RUN = 120
MIN_EVENTS = 8
ENTER_PROB = 0.90
ENTER_Q = 0.60
EXIT_PROB = 0.10
EXIT_Q = 0.40
A0 = 1.0
B0 = 1.0

SEED = 20261003
REPS = 10000
BLOCKS = [5, 10]


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y,pred)),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y,p,labels=[0,1])),
        "up_recall": float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall": float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "prediction_std": float(np.std(p)),
        "tn": int(tn),"fp": int(fp),"fn": int(fn),"tp": int(tp),
    }


class Detector:
    def __init__(self):
        self.mass=np.array([1.0],float)
        self.alpha=np.array([A0],float)
        self.beta=np.array([B0],float)
        self.runlen=np.array([0],int)
        self.n=0

    def update(self,x):
        x=int(x)
        pred_old=np.where(
            x==1,
            self.alpha/(self.alpha+self.beta),
            self.beta/(self.alpha+self.beta)
        )
        prior_pred=0.5
        growth=self.mass*(1-HAZARD)*pred_old
        cp=float(np.sum(self.mass)*HAZARD*prior_pred)

        mass=np.concatenate([[cp],growth])
        alpha=np.concatenate([[A0+x],self.alpha+x])
        beta=np.concatenate([[B0+(1-x)],self.beta+(1-x)])
        runlen=np.concatenate([[1],self.runlen+1])

        keep=runlen<=MAX_RUN
        mass,alpha,beta,runlen=mass[keep],alpha[keep],beta[keep],runlen[keep]
        mass/=mass.sum()

        self.mass,self.alpha,self.beta,self.runlen=mass,alpha,beta,runlen
        self.n+=1

    def summary(self):
        means=self.alpha/(self.alpha+self.beta)
        q=float(np.sum(self.mass*means))
        prob=float(np.sum(self.mass*(1-betainc(self.alpha,self.beta,0.5))))
        erun=float(np.sum(self.mass*self.runlen))
        cp=float(self.mass[self.runlen==1].sum()) if np.any(self.runlen==1) else 0.0
        return {
            "matured_override_events":int(self.n),
            "q_opal":q,
            "prob_opal_superior":prob,
            "expected_run_length":erun,
            "changepoint_mass":cp,
        }


def load_opal():
    x=pd.read_csv(OPAL)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        x[c]=pd.to_datetime(x[c],errors="raise")
    return x.sort_values("forecast_issue_date").reset_index(drop=True)


def build_events(g):
    x=g.copy()
    ap=(x.p_aurora>=.5).astype(int)
    op=(x.p_opal>=.5).astype(int)
    x["relative_event"]=ap!=op
    d=x[x.relative_event].copy()
    d["aurora_correct"]=(ap[x.relative_event].to_numpy()==d.y_up.to_numpy(int))
    d["opal_correct"]=(op[x.relative_event].to_numpy()==d.y_up.to_numpy(int))
    if not ((d.aurora_correct.astype(int)+d.opal_correct.astype(int))==1).all():
        raise RuntimeError("RELAY_EVENT_NOT_EXCLUSIVE")
    d["x_opal_win"]=d.opal_correct.astype(int)
    return d.sort_values(["target_end_date_h3","forecast_issue_date"]).reset_index(drop=True)


def apply_relay(g):
    events=build_events(g)
    det=Detector()
    state="AURORA_ONLY"
    processed=set()
    rows=[]
    switches=[]

    for r in g.itertuples():
        cutoff=pd.Timestamp(r.feature_cutoff_date)
        matured=events[
            (events.target_end_date_h3<=cutoff)
            & (~events.index.isin(processed))
        ].copy().sort_values(["target_end_date_h3","forecast_issue_date"])

        for idx,ev in matured.iterrows():
            det.update(int(ev.x_opal_win))
            processed.add(int(idx))

        s=det.summary()
        old=state

        if s["matured_override_events"]>=MIN_EVENTS:
            if (
                state=="AURORA_ONLY"
                and s["prob_opal_superior"]>=ENTER_PROB
                and s["q_opal"]>=ENTER_Q
            ):
                state="OPAL_TRUSTED"
            elif (
                state=="OPAL_TRUSTED"
                and s["prob_opal_superior"]<=EXIT_PROB
                and s["q_opal"]<=EXIT_Q
            ):
                state="AURORA_ONLY"

        if state!=old:
            switches.append({
                "forecast_issue_date":str(pd.Timestamp(r.forecast_issue_date).date()),
                "from":old,"to":state,**s
            })

        pa=float(r.p_aurora)
        po=float(r.p_opal)
        pout=po if state=="OPAL_TRUSTED" else pa

        rows.append({
            "feature_cutoff_date":r.feature_cutoff_date,
            "forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,
            "year":int(r.year),"month":str(r.month),
            "y_up":int(r.y_up),"target_r3":float(r.target_r3),
            "p_aurora":pa,"p_opal":po,
            "opal_override":bool(r.override),
            "relay_state":state,
            "p_relay":pout,
            **s,
        })

    return pd.DataFrame(rows),pd.DataFrame(switches),events


def score_periods(g):
    specs=[
        ("2022_H2",g.forecast_issue_date.between("2022-07-01","2022-12-31")),
        ("2023",g.year==2023),("2024",g.year==2024),
        ("2025",g.year==2025),("2026",g.year==2026),
        ("2023-2024",g.year.isin([2023,2024])),
        ("2025-2026",g.year.isin([2025,2026])),
    ]
    rows=[]
    for label,mask in specs:
        z=g[mask].copy()
        if z.empty: continue
        for model,col in [("AURORA","p_aurora"),("OPAL","p_opal"),("RELAY","p_relay")]:
            rows.append({"model":model,"period":label,**metrics(z.y_up,z[col])})
    return pd.DataFrame(rows)


def confirmation(mdf,switches):
    checks=[]; ok=True
    for yr in ["2023","2024"]:
        a=mdf[(mdf.model=="AURORA")&(mdf.period==yr)].iloc[0]
        r=mdf[(mdf.model=="RELAY")&(mdf.period==yr)].iloc[0]
        passed=bool(
            r.accuracy+.01+1e-12>=a.accuracy
            and r.brier<=a.brier+.003+1e-12
        )
        checks.append({
            "period":yr,"pass":passed,
            "aurora_accuracy":float(a.accuracy),"relay_accuracy":float(r.accuracy),
            "aurora_brier":float(a.brier),"relay_brier":float(r.brier),
        })
        ok=ok and passed

    a=mdf[(mdf.model=="AURORA")&(mdf.period=="2023-2024")].iloc[0]
    r=mdf[(mdf.model=="RELAY")&(mdf.period=="2023-2024")].iloc[0]
    agg_ok=bool(r.balanced_accuracy+.01+1e-12>=a.balanced_accuracy)
    sw_ok=len(switches)>0
    return bool(ok and agg_ok and sw_ok),checks,agg_ok,sw_ok


def state_summary(g):
    rows=[]
    for yr,z in g.groupby("year"):
        rows.append({
            "year":int(yr),
            "n":int(len(z)),
            "trusted_share":float((z.relay_state=="OPAL_TRUSTED").mean()),
            "mean_q_opal":float(z.q_opal.mean()),
            "mean_prob_opal_superior":float(z.prob_opal_superior.mean()),
            "last_matured_override_events":int(z.matured_override_events.iloc[-1]),
        })
    return pd.DataFrame(rows)


def rescue_2026(g):
    z=g[g.year==2026].copy()
    y=z.y_up.to_numpy(int)
    a=(z.p_aurora.to_numpy(float)>=.5).astype(int)
    r=(z.p_relay.to_numpy(float)>=.5).astype(int)
    aok=a==y; rok=r==y
    return {
        "n":int(len(z)),
        "aurora_accuracy":float(aok.mean()),
        "relay_accuracy":float(rok.mean()),
        "rescued":int(np.sum((~aok)&rok)),
        "broken":int(np.sum(aok&(~rok))),
        "net_rescue":int(np.sum((~aok)&rok)-np.sum(aok&(~rok))),
        "trusted_origins":int(np.sum(z.relay_state=="OPAL_TRUSTED")),
    }


def logloss_row(y,p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6); y=np.asarray(y,int)
    return -(y*np.log(p)+(1-y)*np.log(1-p))


def paired_diff(y,cand,base):
    y=np.asarray(y,int); cand=np.asarray(cand,float); base=np.asarray(base,float)
    return {
        "accuracy":((cand>=.5).astype(int)==y).astype(float)-((base>=.5).astype(int)==y).astype(float),
        "brier":(cand-y)**2-(base-y)**2,
        "logloss":logloss_row(y,cand)-logloss_row(y,base),
    }


def circular_boot(diff,block_len,rng):
    diff=np.asarray(diff,float); n=len(diff); nb=int(np.ceil(n/block_len))
    vals=np.empty(REPS,float); offs=np.arange(block_len); batch=500
    for st in range(0,REPS,batch):
        m=min(batch,REPS-st)
        starts=rng.integers(0,n,size=(m,nb))
        idx=(starts[:,:,None]+offs[None,None,:])%n
        idx=idx.reshape(m,-1)[:,:n]
        vals[st:st+m]=diff[idx].mean(axis=1)
    return vals


def inference(g):
    rows=[]; si=0
    for period,mask in {
        "2023-2024":g.year.isin([2023,2024]),
        "2025-2026":g.year.isin([2025,2026]),
        "2026":g.year==2026,
    }.items():
        z=g[mask].copy()
        for metric,d in paired_diff(z.y_up,z.p_relay,z.p_aurora).items():
            for b in BLOCKS:
                si+=1
                boot=circular_boot(d,b,np.random.default_rng(SEED+si))
                lo,hi=np.quantile(boot,[.025,.975])
                improve=float(np.mean(boot>0)) if metric=="accuracy" else float(np.mean(boot<0))
                rows.append({
                    "period":period,"metric":metric,"block_len":b,
                    "observed_diff":float(np.mean(d)),
                    "ci95_low":float(lo),"ci95_high":float(hi),
                    "bootstrap_improve_share":improve,"n":int(len(z)),
                })
    return pd.DataFrame(rows)


def main():
    opal=load_opal()
    relay,switches,events=apply_relay(opal)

    relay.to_csv(OUT/"relay_v1_predictions.csv",index=False)
    switches.to_csv(OUT/"relay_v1_switches.csv",index=False)
    events.to_csv(OUT/"relay_v1_override_events.csv",index=False)

    mdf=score_periods(relay)
    mdf.to_csv(OUT/"relay_v1_metrics.csv",index=False)

    states=state_summary(relay)
    states.to_csv(OUT/"relay_v1_state_summary.csv",index=False)

    passed,checks,agg_ok,sw_ok=confirmation(mdf,switches)
    status="MECHANISM_PASS" if passed else "NOT_PROMOTED_CONFIRM_FAIL"

    resc=rescue_2026(relay)
    pd.DataFrame([resc]).to_csv(OUT/"relay_v1_2026_rescue.csv",index=False)

    inf=inference(relay) if passed else pd.DataFrame()
    if passed: inf.to_csv(OUT/"relay_v1_inference.csv",index=False)

    summary={
        "schema":"RELAY_H3_V1",
        "status":status,
        "evidence_class":"RETROSPECTIVE_MECHANISM_VALIDATION_POST_HOC_ARCHITECTURE",
        "rule":{
            "hazard":HAZARD,"max_run":MAX_RUN,"min_events":MIN_EVENTS,
            "enter_prob":ENTER_PROB,"enter_q":ENTER_Q,
            "exit_prob":EXIT_PROB,"exit_q":EXIT_Q,
        },
        "confirmation_pass":bool(passed),
        "confirmation_checks":checks,
        "aggregate_guard":bool(agg_ok),
        "switches_present":bool(sw_ok),
        "switches":switches.to_dict(orient="records"),
        "states":states.to_dict(orient="records"),
        "rescue_2026":resc,
        "metrics":mdf.to_dict(orient="records"),
        "total_override_events":int(len(events)),
        "inference":inf.to_dict(orient="records") if passed else [],
    }
    (OUT/"relay_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# RELAY-H3 V1 — REGIME-ADAPTIVE OPTIONS-RESCUE TRUST ROUTER RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence class:** retrospective mechanism validation; architecture was motivated after OPAL historical behavior was observed.  ",
        f"**Trust BOCPD:** hazard 1/20; enter Pr>=0.90 & q>=0.60; exit Pr<=0.10 & q<=0.40.","",
        "## Period metrics","",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for period in ["2022_H2","2023","2024","2025","2026","2025-2026"]:
        for model in ["AURORA","OPAL","RELAY"]:
            q=mdf[(mdf.model==model)&(mdf.period==period)]
            if q.empty: continue
            r=q.iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    lines += ["","## Trust state by year","",
              "| Year | OPAL-trusted share | Mean q(OPAL win) | Mean Pr(OPAL superior) | Matured override events |",
              "|---:|---:|---:|---:|---:|"]
    for r in states.itertuples():
        lines.append(
            f"| {int(r.year)} | {100*r.trusted_share:.1f}% | {r.mean_q_opal:.3f} | "
            f"{r.mean_prob_opal_superior:.3f} | {int(r.last_matured_override_events)} |"
        )

    lines += ["","## Trust-state switches",""]
    if switches.empty:
        lines.append("- none")
    else:
        for _,r in switches.iterrows():
            lines.append(
                f"- {r['forecast_issue_date']}: {r['from']} -> {r['to']}; "
                f"q={r['q_opal']:.3f}; Pr={r['prob_opal_superior']:.3f}; events={int(r['matured_override_events'])}"
            )

    lines += ["","## 2026 rescue","",
              f"- AURORA accuracy: **{100*resc['aurora_accuracy']:.2f}%**",
              f"- RELAY accuracy: **{100*resc['relay_accuracy']:.2f}%**",
              f"- rescued: **{resc['rescued']}**",
              f"- broken: **{resc['broken']}**",
              f"- net rescue: **{resc['net_rescue']:+d}**",
              f"- OPAL-trusted origins: **{resc['trusted_origins']} / {resc['n']}**"]

    if passed:
        lines += ["","## Dependence-aware bootstrap",""]
        for r in inf.itertuples():
            scale=100 if r.metric=="accuracy" else 1
            unit=" pp" if r.metric=="accuracy" else ""
            lines.append(
                f"- {r.period} {r.metric} block{r.block_len}: diff={scale*r.observed_diff:+.4f}{unit}; "
                f"95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; "
                f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
            )

    lines += ["","## Governance","",
              "RELAY introduces no new tuned detector parameter; it reuses DART's frozen BOCPD hazard and symmetric trust thresholds. "
              "Only matured OPAL-vs-AURORA direction-changing events update trust. "
              "Existing frozen AURORA prospective validation is unchanged."]

    (OUT/"RELAY_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"RELAY_V1_RESULT.md").read_text())


if __name__=="__main__":
    main()
