from pathlib import Path
import importlib.util, json, math
import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist, binomtest

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V1=AX/"tools"/"gold_h3_handoff_competence_bocpd_v1.py"

OUT_MD=AX/"GOLD_H3_BOCPD_HYSTERESIS_ADVERSARIAL_AUDIT_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_BOCPD_HYSTERESIS_ADVERSARIAL_AUDIT_SUMMARY_2026-10-04.json"
OUT_GRID=AX/"GOLD_H3_BOCPD_HYSTERESIS_ADVERSARIAL_AUDIT_GRID_2026-10-04.csv"
OUT_ENTRY=AX/"GOLD_H3_BOCPD_HYSTERESIS_ADVERSARIAL_AUDIT_ENTRY_SHIFT_2026-10-04.csv"

EXPECTED_RUNS=[3,4,5,6,8,12]
PRES=[.55,.60,.65]
PGTS=[.75,.80,.85]
EXITS=[1,2,3]
CENTRAL=(4,.60,.80,2)
N_SIM=20000
SEED=20261004

spec=importlib.util.spec_from_file_location("v1",V1)
v1=importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)

_PGT_CACHE={}
class FastBetaBernoulliBOCPD:
    def __init__(self,expected_run):
        self.h=1.0/float(expected_run)
        self.r=np.array([1.0],float)
        self.a=np.array([0.5],float)
        self.b=np.array([0.5],float)
    def predictive(self):
        means=self.a/(self.a+self.b)
        p=float(np.dot(self.r,means))
        vals=[]
        for aa,bb in zip(self.a,self.b):
            key=(float(aa),float(bb))
            if key not in _PGT_CACHE:
                _PGT_CACHE[key]=float(1-beta_dist.cdf(.5,aa,bb))
            vals.append(_PGT_CACHE[key])
        return {"p_rescue":p,"p_theta_gt_half":float(np.dot(self.r,np.asarray(vals,float))),
                "map_run":int(np.argmax(self.r))}
    def update(self,y):
        y=int(y)
        means=self.a/(self.a+self.b)
        like=means if y==1 else (1-means)
        prior_like=.5
        new=np.zeros(len(self.r)+1,float)
        new[0]=self.h*prior_like*float(self.r.sum())
        new[1:]=(1-self.h)*self.r*like
        new/=float(new.sum())
        na=np.empty(len(self.a)+1,float); nb=np.empty(len(self.b)+1,float)
        na[0]=.5+y; nb[0]=.5+(1-y)
        na[1:]=self.a+y; nb[1:]=self.b+(1-y)
        self.r,self.a,self.b=new,na,nb

def init_model(expected_run, form):
    m=FastBetaBernoulliBOCPD(expected_run)
    for r in form.itertuples():
        m.update(int(r.competence_y))
    return m

def alarm_table():
    z=v1.build_frame()
    form=z[(z.eval_block=="FORMATION_2025")&z.handoff_alarm].copy().sort_values("feature_cutoff_date")
    test=z[z.eval_block=="STRESS_2026"].copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    if len(form)!=13 or len(test)!=191 or int(test.baseline_correct.sum())!=126:
        raise RuntimeError("authoritative V1/V4 frame mismatch")
    a=test[test.handoff_alarm].copy().sort_values("feature_cutoff_date").reset_index()
    if len(a)!=28: raise RuntimeError(f"expected 28 Handoff alarms, got {len(a)}")
    return form,test,a

def simulate_alarm_sequence(form, alarms, yseq, expected_run=4, pres=.60, pgt=.80, exit_streak=2, forced_entry_alarm=None):
    m=init_model(expected_run,form)
    trust=False; fail=0; pending=[]; acts=[]; probs=[]; first_entry=None
    forced_used=False
    for j,row in alarms.iterrows():
        now=row.feature_cutoff_date
        matured=[p for p in pending if p["maturity"]<=now]
        pending=[p for p in pending if p["maturity"]>now]
        for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])):
            m.update(int(p["y"]))
            if p["acted"] and trust:
                if int(p["y"])==1:
                    fail=0
                else:
                    fail+=1
                    if fail>=exit_streak:
                        trust=False; fail=0
        pre=m.predictive()
        entry=False
        if forced_entry_alarm is not None:
            if (not forced_used) and j==forced_entry_alarm:
                trust=True; fail=0; entry=True; forced_used=True
        else:
            if (not trust) and pre["p_rescue"]>=pres and pre["p_theta_gt_half"]>=pgt:
                trust=True; fail=0; entry=True
        act=bool(trust)
        if entry and first_entry is None:first_entry=j
        acts.append(act)
        probs.append((pre["p_rescue"],pre["p_theta_gt_half"],pre["map_run"]))
        pending.append({"maturity":row.target_end_date_h3,"origin":now,"y":int(yseq[j]),"acted":act})
    y=np.asarray(yseq,int); acts=np.asarray(acts,bool)
    rescue=int(((y==1)&acts).sum()); broken=int(((y==0)&acts).sum())
    return {"acts":acts,"rescue":rescue,"broken":broken,"net":rescue-broken,
            "precision":float(rescue/max(int(acts.sum()),1)),"actions":int(acts.sum()),
            "first_entry_idx":first_entry,"probs":probs}

def bern_ll(y):
    y=np.asarray(y,int); n=len(y)
    if n==0:return 0.0
    p=float(np.clip(y.mean(),1e-9,1-1e-9))
    return float((y*np.log(p)+(1-y)*np.log(1-p)).sum())

def best_cp(y):
    y=np.asarray(y,int); base=bern_ll(y); best=None
    for k in range(4,len(y)-3):
        gain=bern_ll(y[:k])+bern_ll(y[k:])-base
        rec={"split":k,"gain":float(gain),"pre_rate":float(y[:k].mean()),"post_rate":float(y[k:].mean())}
        if best is None or gain>best["gain"]:best=rec
    return best

def main():
    form,test,alarms=alarm_table()
    y=alarms.competence_y.astype(int).to_numpy()

    central=simulate_alarm_sequence(form,alarms,y,*CENTRAL)
    if central["net"]!=6 or central["actions"]!=10 or central["rescue"]!=8 or central["broken"]!=2:
        raise RuntimeError(f"central V4 mismatch: {central}")

    # A. Sensitivity neighborhood.
    grid=[]
    for er in EXPECTED_RUNS:
        for pr in PRES:
            for pg in PGTS:
                for ex in EXITS:
                    r=simulate_alarm_sequence(form,alarms,y,er,pr,pg,ex)
                    grid.append({"expected_run":er,"p_rescue":pr,"p_gt_half":pg,"exit_streak":ex,
                                 "actions":r["actions"],"rescue":r["rescue"],"broken":r["broken"],
                                 "net":r["net"],"precision":r["precision"],
                                 "first_entry_idx":r["first_entry_idx"],
                                 "first_entry_date":None if r["first_entry_idx"] is None else alarms.iloc[r["first_entry_idx"]].feature_cutoff_date.date().isoformat(),
                                 "assisted_correct":126+r["net"],"assisted_accuracy":(126+r["net"])/191})
    g=pd.DataFrame(grid); g.to_csv(OUT_GRID,index=False)
    robust={
      "n":int(len(g)),
      "positive_fraction":float((g.net>0).mean()),
      "ge4_fraction":float((g.net>=4).mean()),
      "median_net":float(g.net.median()),
      "min_net":int(g.net.min()),"max_net":int(g.net.max()),
      "central_percentile_leq":float((g.net<=central["net"]).mean()),
      "net_counts":{str(int(k)):int(v) for k,v in g.net.value_counts().sort_index().items()}
    }

    # B. Entry perturbation around central entry.
    cidx=int(central["first_entry_idx"])
    entry_rows=[]
    for shift in range(-3,4):
        idx=max(0,min(len(alarms)-1,cidx+shift))
        r=simulate_alarm_sequence(form,alarms,y,4,.60,.80,2,forced_entry_alarm=idx)
        entry_rows.append({"shift":shift,"entry_idx":idx,"entry_date":alarms.iloc[idx].feature_cutoff_date.date().isoformat(),
                           "actions":r["actions"],"rescue":r["rescue"],"broken":r["broken"],"net":r["net"],"precision":r["precision"]})
    edf=pd.DataFrame(entry_rows); edf.to_csv(OUT_ENTRY,index=False)

    # C/D. Null simulations.
    rng=np.random.default_rng(SEED)
    stationary_nets=np.empty(N_SIM,int)
    perm_nets=np.empty(N_SIM,int)
    p0=4/13
    for i in range(N_SIM):
        ys=rng.binomial(1,p0,size=len(y))
        stationary_nets[i]=simulate_alarm_sequence(form,alarms,ys,*CENTRAL)["net"]
        yp=rng.permutation(y)
        perm_nets[i]=simulate_alarm_sequence(form,alarms,yp,*CENTRAL)["net"]
    nulls={
      "stationary_p_ge_observed":float(np.mean(stationary_nets>=central["net"])),
      "stationary_quantiles":{str(q):float(np.quantile(stationary_nets,q)) for q in [.01,.05,.25,.5,.75,.95,.99]},
      "permutation_p_ge_observed":float(np.mean(perm_nets>=central["net"])),
      "permutation_quantiles":{str(q):float(np.quantile(perm_nets,q)) for q in [.01,.05,.25,.5,.75,.95,.99]},
    }

    # E. Offline change-point with permutation maximum-gain null.
    cp=best_cp(y)
    gains=np.empty(N_SIM,float)
    for i in range(N_SIM):
        gains[i]=best_cp(rng.permutation(y))["gain"]
    cp["permutation_p_ge_gain"]=float(np.mean(gains>=cp["gain"]))
    cp["split_before_date"]=alarms.iloc[cp["split"]-1].feature_cutoff_date.date().isoformat()
    cp["split_after_date"]=alarms.iloc[cp["split"]].feature_cutoff_date.date().isoformat()

    # F. Month deletion among central acted alarms.
    acted=alarms[central["acts"]].copy()
    acted["net_unit"]=np.where(acted.competence_y.astype(int)==1,1,-1)
    acted["month"]=acted.feature_cutoff_date.dt.to_period("M").astype(str)
    month_delete=[]
    for m in sorted(acted.month.unique()):
        q=acted[acted.month!=m]
        month_delete.append({"deleted_month":m,"remaining_actions":int(len(q)),
                             "rescue":int((q.competence_y==1).sum()),"broken":int((q.competence_y==0).sum()),
                             "net":int(q.net_unit.sum())})
    worst_loo=int(min(r["net"] for r in month_delete))

    # G. Simple inference on central acted outcomes.
    k=central["rescue"]; n=central["actions"]
    bt=binomtest(k,n,p=.5,alternative="greater")
    a=.5+k; b=.5+(n-k)
    support={
      "binom_one_sided_p":float(bt.pvalue),
      "jeffreys_p_theta_gt_half":float(1-beta_dist.cdf(.5,a,b)),
      "jeffreys_ci95":[float(beta_dist.ppf(.025,a,b)),float(beta_dist.ppf(.975,a,b))]
    }

    summary={
      "schema":"GOLD_H3_BOCPD_HYSTERESIS_ADVERSARIAL_AUDIT",
      "status":"ROBUSTNESS_AUDIT_COMPLETE",
      "central":{"actions":central["actions"],"rescue":central["rescue"],"broken":central["broken"],"net":central["net"],
                 "precision":central["precision"],"entry_idx":cidx,"entry_date":alarms.iloc[cidx].feature_cutoff_date.date().isoformat(),
                 "assisted_correct":126+central["net"],"assisted_accuracy":(126+central["net"])/191},
      "parameter_neighborhood":robust,
      "entry_shift":entry_rows,
      "null_tests":nulls,
      "offline_change_point":cp,
      "month_delete":month_delete,
      "worst_leave_one_month_out_net":worst_loo,
      "statistical_support":support
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2)+"\n")

    lines=["# GOLD H3 — BOCPD Hysteresis Adversarial Audit","",
           "**Status:** ROBUSTNESS_AUDIT_COMPLETE","",
           "## Central V4 replication","",
           f"- actions **{central['actions']}**, rescue/broken **{central['rescue']}/{central['broken']}**, net **{central['net']:+d}**, precision **{100*central['precision']:.1f}%**",
           f"- entry: **{summary['central']['entry_date']}**",
           f"- assisted accuracy: **{summary['central']['assisted_correct']}/191 = {100*summary['central']['assisted_accuracy']:.2f}%**","",
           "## Parameter-neighborhood attack","",
           f"- combinations: **{robust['n']}**",
           f"- net > 0: **{100*robust['positive_fraction']:.1f}%**",
           f"- net >= +4: **{100*robust['ge4_fraction']:.1f}%**",
           f"- median net: **{robust['median_net']:+.1f}**",
           f"- min / max net: **{robust['min_net']:+d} / {robust['max_net']:+d}**",
           f"- central +6 percentile (fraction neighborhood <= +6): **{100*robust['central_percentile_leq']:.1f}%**","",
           "### Net distribution","",
           "| Net | Count |","|---:|---:|"]
    for k0,v0 in robust["net_counts"].items(): lines.append(f"| {int(k0):+d} | {v0} |")
    lines += ["","## Entry-date perturbation","",
              "| Shift (alarms) | Entry date | Actions | Rescue | Broken | Net | Precision |",
              "|---:|---|---:|---:|---:|---:|---:|"]
    for r in entry_rows:
        lines.append(f"| {r['shift']:+d} | {r['entry_date']} | {r['actions']} | {r['rescue']} | {r['broken']} | {r['net']:+d} | {100*r['precision']:.1f}% |")
    lines += ["","## Null attacks","",
              f"- stationary 2025-competence null P(net >= +6): **{nulls['stationary_p_ge_observed']:.4f}**",
              f"- chronology-permutation P(net >= +6): **{nulls['permutation_p_ge_observed']:.4f}**","",
              "## Offline change-point diagnostic","",
              f"- best split: between **{cp['split_before_date']}** and **{cp['split_after_date']}**",
              f"- pre rescue rate: **{100*cp['pre_rate']:.1f}%**",
              f"- post rescue rate: **{100*cp['post_rate']:.1f}%**",
              f"- max log-likelihood gain: **{cp['gain']:.3f}**",
              f"- permutation P(max gain >= observed): **{cp['permutation_p_ge_gain']:.4f}**","",
              "## Calendar-block deletion","",
              "| Deleted month | Remaining actions | Rescue | Broken | Net |",
              "|---|---:|---:|---:|---:|"]
    for r in month_delete:
        lines.append(f"| {r['deleted_month']} | {r['remaining_actions']} | {r['rescue']} | {r['broken']} | {r['net']:+d} |")
    lines += ["",f"Worst leave-one-month-out net: **{worst_loo:+d}**","",
              "## Statistical support for central acted set","",
              f"- one-sided exact Binomial p vs 50%: **{support['binom_one_sided_p']:.4f}**",
              f"- Jeffreys posterior P(theta>0.5): **{support['jeffreys_p_theta_gt_half']:.4f}**",
              f"- Jeffreys 95% interval: **[{100*support['jeffreys_ci95'][0]:.1f}%, {100*support['jeffreys_ci95'][1]:.1f}%]**","",
              "## Governance","",
              "This audit does not promote V4 to independent validation. V4 remains post-hoc development evidence. The purpose is falsification: assess whether the observed competence-state shift survives broad perturbations and null comparisons."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: adversarial-audit-run
