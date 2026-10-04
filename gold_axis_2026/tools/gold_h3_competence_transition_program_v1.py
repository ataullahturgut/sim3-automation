from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

RTE=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"
SELLR=AX/"GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv"
TIMELINE=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv"
ADV=AX/"GOLD_H3_BOCPD_HYSTERESIS_ADVERSARIAL_AUDIT_SUMMARY_2026-10-04.json"

OUT_MD=AX/"GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_RESULT_2026-10-05.md"
OUT_JSON=AX/"GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_SUMMARY_2026-10-05.json"
OUT_DRIFT=AX/"GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_DRIFT_2026-10-05.csv"
OUT_ACTIONS=AX/"GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_ACTIONS_2026-10-05.csv"

SELLR_THR=2.3677413378977423
ALPHAS=[0.02,0.05,0.075,0.10]

VIEWS={
 "INTERNAL":["h_ret_12","trend_strength","adverse_excursion","path_consistency",
             "opposite_semivar_share","session_against_trend","trend_close_location"],
 "OPTIONS_LIQ":["signed_opt_pressure","signed_d_opt_pressure","opt_total_z20","gc_volume_z20","gc_volume_accel_5"],
 "CROSS_MACRO":["core_confirmation","cross_dispersion","gold_daily_ret1","usd_ret1","tnx_chg1","ndx_ret1","vix_ret1"],
}

def num(s): return pd.to_numeric(s,errors="coerce")

def build_market():
    a=pd.read_csv(RTE,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date")
    d=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date")
    ac=["feature_cutoff_date"]+[c for c in set(sum(VIEWS.values(),[])) if c in a.columns]
    dc=["feature_cutoff_date"]+[c for c in set(sum(VIEWS.values(),[])) if c in d.columns and c not in ac]
    z=a[ac].merge(d[dc],on="feature_cutoff_date",how="inner",validate="one_to_one")
    z=z.sort_values("feature_cutoff_date").reset_index(drop=True)
    return z

def robust_view_score(z, cols):
    x=z[cols].apply(pd.to_numeric,errors="coerce")
    out=np.full(len(z),np.nan)
    for i in range(len(z)):
        if i<100: continue
        ref=x.iloc[max(0,i-125):i-5]
        rec=x.iloc[max(0,i-4):i+1]
        if len(ref)<80 or len(rec)<3: continue
        med=ref.median()
        mad=(ref-med).abs().median()*1.4826
        std=ref.std(ddof=0).replace(0,np.nan)
        scale=mad.replace(0,np.nan).fillna(std).replace(0,np.nan).fillna(1.0)
        shift=((rec.mean()-med)/scale).replace([np.inf,-np.inf],np.nan)
        if shift.notna().sum()<max(3,len(cols)//2): continue
        out[i]=float(np.sqrt(np.nansum(shift.to_numpy(float)**2)))
    return out

def ecdf_percentile(cal, values):
    cal=np.sort(np.asarray(cal,float))
    cal=cal[np.isfinite(cal)]
    out=[]
    for v in values:
        if not np.isfinite(v) or len(cal)==0: out.append(np.nan)
        else: out.append(float(np.searchsorted(cal,v,side="right")/(len(cal)+1)))
    return np.asarray(out,float)

def workstream_a():
    z=build_market()
    for name,cols in VIEWS.items():
        missing=[c for c in cols if c not in z.columns]
        if missing: raise RuntimeError(f"{name} missing columns {missing}")
        z[f"score_{name}"]=robust_view_score(z,cols)
    pre=(z.feature_cutoff_date<pd.Timestamp("2026-01-01"))
    calinfo={}
    for name in VIEWS:
        s=z.loc[pre,f"score_{name}"].to_numpy(float)
        s=s[np.isfinite(s)]
        q90=float(np.quantile(s,.90)); q95=float(np.quantile(s,.95))
        z[f"pct_{name}"]=ecdf_percentile(s,z[f"score_{name}"].to_numpy(float))
        z[f"q90_{name}"]=z[f"score_{name}"]>=q90
        z[f"q95_{name}"]=z[f"score_{name}"]>=q95
        calinfo[name]={"n":int(len(s)),"q90":q90,"q95":q95}
    z["n_q90"]=sum(z[f"q90_{n}"].astype(int) for n in VIEWS)
    z["n_q95"]=sum(z[f"q95_{n}"].astype(int) for n in VIEWS)
    z["BROAD2"]=z.n_q90>=2
    z["STRICT2"]=z.n_q95>=2
    fisher=np.zeros(len(z),float)
    valid=np.ones(len(z),bool)
    for name in VIEWS:
        p=z[f"pct_{name}"].to_numpy(float)
        valid &= np.isfinite(p)
        fisher += -np.log(np.clip(1-p,1e-6,1.0))
    fisher[~valid]=np.nan
    z["fisher_score"]=fisher
    fcal=z.loc[pre,"fisher_score"].dropna().to_numpy(float)
    fq99=float(np.quantile(fcal,.99))
    z["FISHER99"]=z.fisher_score>=fq99

    tl=pd.read_csv(TIMELINE,parse_dates=["feature_cutoff_date","target_end_date_h3"])
    stress=tl[tl.period=="2026_STRESS"][["feature_cutoff_date","competence_y"]].copy()
    stress["competence_y"]=stress.competence_y.astype(int)
    zz=z.merge(stress,on="feature_cutoff_date",how="left")
    evals={}
    for state in ["BROAD2","STRICT2","FISHER99"]:
        q=zz[zz.competence_y.notna()].copy()
        inside=q[q[state]]
        outside=q[~q[state]]
        evals[state]={
          "alarm_n_inside":int(len(inside)),
          "rescue_inside":int(inside.competence_y.sum()),
          "precision_inside":float(inside.competence_y.mean()) if len(inside) else None,
          "alarm_n_outside":int(len(outside)),
          "rescue_outside":int(outside.competence_y.sum()),
          "precision_outside":float(outside.competence_y.mean()) if len(outside) else None,
        }
    dates={}
    z26=z[(z.feature_cutoff_date>=pd.Timestamp("2026-01-01"))&(z.feature_cutoff_date<=pd.Timestamp("2026-09-30"))]
    for state in ["BROAD2","STRICT2","FISHER99"]:
        dd=z26.loc[z26[state],"feature_cutoff_date"].dt.strftime("%Y-%m-%d").tolist()
        dates[state]=dd
    z.to_csv(OUT_DRIFT,index=False)
    return z,{"calibration":calinfo,"fisher_q99":fq99,"handoff_enrichment":evals,"dates_2026":dates}

def timeline_data():
    tl=pd.read_csv(TIMELINE,parse_dates=["feature_cutoff_date","target_end_date_h3"])
    form=tl[tl.period=="2025_FORMATION"].copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    test=tl[tl.period=="2026_STRESS"].copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    form["target_end_date_h3"]=pd.to_datetime(form["target_end_date_h3"],errors="coerce")
    test["target_end_date_h3"]=pd.to_datetime(test["target_end_date_h3"],errors="coerce")
    sc=pd.read_csv(SELLR,parse_dates=["feature_cutoff_date"])
    keep=["feature_cutoff_date","sellr_score","baseline_pred","momentum_up"]
    form=form.merge(sc[keep],on="feature_cutoff_date",how="left",suffixes=("","_sellr"))
    test=test.merge(sc[keep],on="feature_cutoff_date",how="left",suffixes=("","_sellr"))
    for q in [form,test]:
        q["sellr_fire"]=(num(q.sellr_score)>=SELLR_THR)&(num(q.baseline_pred_sellr)==num(q.momentum_up_sellr))
    return form,test

def simulate_stcr(form,test):
    if int(form.sellr_fire.sum())!=0:
        pass
    trust=False; broken_streak=0; pending=[]; rows=[]; entry=None
    for _,r in test.iterrows():
        now=r.feature_cutoff_date
        matured=[p for p in pending if p["maturity"]<=now]
        pending=[p for p in pending if p["maturity"]>now]
        for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])):
            if p["acted"] and trust:
                if p["y"]==1: broken_streak=0
                else:
                    broken_streak+=1
                    if broken_streak>=2:
                        trust=False; broken_streak=0
        if (not trust) and bool(r.sellr_fire):
            trust=True; broken_streak=0
            if entry is None: entry=now
        acted=bool(trust)
        rows.append({"date":now,"maturity":r.target_end_date_h3,"y":int(r.competence_y),
                     "sellr_score":float(r.sellr_score) if pd.notna(r.sellr_score) else np.nan,
                     "sellr_fire":bool(r.sellr_fire),"acted":acted,
                     "baseline_pred":int(r.baseline_pred),"y_up":int(r.y_up)})
        pending.append({"origin":now,"maturity":r.target_end_date_h3,"y":int(r.competence_y),"acted":acted})
    a=pd.DataFrame(rows)
    q=a[a.acted].copy()
    rescue=int(q.y.sum()); broken=int(len(q)-rescue); net=rescue-broken
    # exact location benchmark: force the same persistence state to start at each alarm.
    def forced(idx):
        trust=False; bs=0; pend=[]; rr=[]
        for j,r in test.iterrows():
            now=r.feature_cutoff_date
            matured=[p for p in pend if p["maturity"]<=now]
            pend=[p for p in pend if p["maturity"]>now]
            for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])):
                if p["acted"] and trust:
                    if p["y"]==1:bs=0
                    else:
                        bs+=1
                        if bs>=2:trust=False;bs=0
            if j==idx and not trust:trust=True;bs=0
            act=trust
            rr.append((int(r.competence_y),act))
            pend.append({"origin":now,"maturity":r.target_end_date_h3,"y":int(r.competence_y),"acted":act})
        vals=[y for y,act in rr if act]
        return sum(1 if y else -1 for y in vals)
    nets=np.array([forced(i) for i in range(len(test))],int)
    loc_p=float(np.mean(nets>=net))
    # month deletion
    q["month"]=q.date.dt.to_period("M").astype(str)
    loo=[]
    for m in sorted(q.month.unique()):
        g=q[q.month!=m]
        rr=int(g.y.sum()); bb=int(len(g)-rr)
        loo.append({"deleted_month":m,"actions":int(len(g)),"rescue":rr,"broken":bb,"net":rr-bb})
    # update baseline confusion 67/59/41/24.
    tp,tn,fp,fn=67,59,41,24
    for r in q.itertuples():
        bp=int(r.baseline_pred); yy=int(r.y_up)
        if bp==1 and yy==0: fp-=1;tn+=1
        elif bp==0 and yy==1: fn-=1;tp+=1
        elif bp==1 and yy==1: tp-=1;fn+=1
        elif bp==0 and yy==0: tn-=1;fp+=1
    up=tp/(tp+fn); dn=tn/(tn+fp); ba=(up+dn)/2
    return a,{
      "formation_sellr_handoff_triggers":int(form.sellr_fire.sum()),
      "entry_date":None if entry is None else entry.date().isoformat(),
      "actions":int(len(q)),"rescue":rescue,"broken":broken,"net":net,
      "precision":float(rescue/len(q)) if len(q) else 0.0,
      "assisted_correct":126+net,"assisted_accuracy":float((126+net)/191),
      "assisted_confusion":{"tp":tp,"tn":tn,"fp":fp,"fn":fn,"balanced_accuracy":float(ba)},
      "entry_location_exact_p_ge_observed":loc_p,
      "entry_location_net_min":int(nets.min()),"entry_location_net_median":float(np.median(nets)),"entry_location_net_max":int(nets.max()),
      "leave_one_month_out":loo,
      "worst_leave_one_month_out_net":int(min(x["net"] for x in loo)) if loo else 0,
      "action_dates":[{"date":r.date.date().isoformat(),"outcome":"RESCUE" if int(r.y)==1 else "BROKEN","sellr_fire":bool(r.sellr_fire)} for r in q.itertuples()]
    }

def fixed_share(form,test,alpha):
    w=np.array([0.5,0.5],float) # KEEP, FLIP
    updates=0
    def update(y):
        nonlocal w,updates
        updates+=1
        eta=math.sqrt(8*math.log(2)/updates)
        loss=np.array([y,1-y],float)
        w=w*np.exp(-eta*loss)
        w=w/w.sum()
        w=(1-alpha)*w+alpha*np.array([0.5,0.5])
    for r in form.itertuples():
        update(int(r.competence_y))
    pending=[]; rows=[]
    for r in test.itertuples():
        now=r.feature_cutoff_date
        matured=[p for p in pending if p["maturity"]<=now]
        pending=[p for p in pending if p["maturity"]>now]
        for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])):
            update(p["y"])
        act=bool(w[1]>w[0])
        rows.append({"date":now,"y":int(r.competence_y),"acted":act,"flip_weight":float(w[1]),"updates":updates})
        pending.append({"origin":now,"maturity":r.target_end_date_h3,"y":int(r.competence_y)})
    a=pd.DataFrame(rows); q=a[a.acted]
    rr=int(q.y.sum()); bb=int(len(q)-rr)
    return a,{"alpha":alpha,"actions":int(len(q)),"rescue":rr,"broken":bb,"net":rr-bb,
              "precision":float(rr/len(q)) if len(q) else 0.0,
              "first_action":None if q.empty else q.iloc[0].date.date().isoformat(),
              "assisted_correct":126+(rr-bb),"assisted_accuracy":float((126+rr-bb)/191)}

def main():
    drift,da=workstream_a()
    form,test=timeline_data()
    stcr_rows,stcr=simulate_stcr(form,test)
    fs=[]; action_parts=[]
    for a in ALPHAS:
        rr,sm=fixed_share(form,test,a)
        fs.append(sm)
        x=rr[rr.acted].copy()
        if len(x):
            x["method"]=f"FIXED_SHARE_{a:.3f}"
            action_parts.append(x.rename(columns={"date":"feature_cutoff_date"}))
    y=stcr_rows[stcr_rows.acted].copy()
    if len(y):
        y["method"]="STCR"
        y=y.rename(columns={"date":"feature_cutoff_date"})
        action_parts.append(y)
    if action_parts:
        allact=pd.concat(action_parts,ignore_index=True,sort=False)
        allact.to_csv(OUT_ACTIONS,index=False)
    else: pd.DataFrame().to_csv(OUT_ACTIONS,index=False)

    adv=json.loads(ADV.read_text())
    bocpd_date=adv["central"]["entry_date"]
    cp_date=adv["offline_change_point"]["split_after_date"]
    sellr_date=stcr["entry_date"]
    central_fs=next(x for x in fs if abs(x["alpha"]-.05)<1e-9)
    fs_date=central_fs["first_action"]
    first_drift={}
    for state,dates in da["dates_2026"].items():
        first_drift[state]=dates[0] if dates else None
    window_start=pd.Timestamp("2026-04-01"); window_end=pd.Timestamp("2026-06-30")
    indicators={
      "offline_change_point":cp_date,
      "sellr_trigger":sellr_date,
      "bocpd_v4_entry":bocpd_date,
      "fixed_share_alpha_005_cross":fs_date,
      **{f"drift_{k}":v for k,v in first_drift.items()}
    }
    in_window={}
    for k,v in indicators.items():
        if v is None: in_window[k]=False
        else:
            d=pd.Timestamp(v); in_window[k]=bool(window_start<=d<=window_end)

    summary={
      "schema":"GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1",
      "status":"MULTI_VIEW_PROGRAM_COMPLETE",
      "workstream_a":da,
      "workstream_b_stcr":stcr,
      "workstream_c_fixed_share":fs,
      "convergence":{"indicator_dates":indicators,"apr_jun_window_hits":in_window,
                     "n_hits":int(sum(in_window.values())),"n_indicators":int(len(in_window))},
      "known_reference":{"baseline_correct":126,"baseline_accuracy":126/191,
                         "bocpd_v4_correct":132,"bocpd_v4_accuracy":132/191}
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — Competence Transition Program V1 Result","",
           "**Status:** MULTI_VIEW_PROGRAM_COMPLETE","",
           "## A. Label-free multi-view drift","",
           "| State | 2026 first alerts | Handoff inside: rescue/N | Precision | Outside precision |",
           "|---|---|---:|---:|---:|"]
    for st in ["BROAD2","STRICT2","FISHER99"]:
        dates=da["dates_2026"][st][:8]
        ev=da["handoff_enrichment"][st]
        pin="NA" if ev["precision_inside"] is None else f"{100*ev['precision_inside']:.1f}%"
        pout="NA" if ev["precision_outside"] is None else f"{100*ev['precision_outside']:.1f}%"
        lines.append(f"| {st} | {', '.join(dates) if dates else 'none'} | {ev['rescue_inside']}/{ev['alarm_n_inside']} | {pin} | {pout} |")

    lines += ["","## B. SELLR-triggered competence regime (STCR)","",
              f"- 2025 formation Handoff alarms with frozen SELLR trigger: **{stcr['formation_sellr_handoff_triggers']}**",
              f"- 2026 TRUST entry: **{stcr['entry_date']}**",
              f"- actions/rescue/broken/net: **{stcr['actions']} / {stcr['rescue']} / {stcr['broken']} / {stcr['net']:+d}**",
              f"- precision: **{100*stcr['precision']:.1f}%**",
              f"- assisted: **{stcr['assisted_correct']}/191 = {100*stcr['assisted_accuracy']:.2f}%**, BA **{100*stcr['assisted_confusion']['balanced_accuracy']:.2f}%**",
              f"- exact random-entry-location benchmark P(net >= observed): **{stcr['entry_location_exact_p_ge_observed']:.4f}**",
              f"- worst leave-one-month-out net: **{stcr['worst_leave_one_month_out_net']:+d}**","",
              "### STCR acted Handoff alarms","",
              "| Date | Outcome | Trigger origin? |","|---|---|---|"]
    for r in stcr["action_dates"]:
        lines.append(f"| {r['date']} | {r['outcome']} | {r['sellr_fire']} |")

    lines += ["","## C. Theory-fixed online expert aggregation","",
              "| Fixed-share alpha | First FLIP | Actions | Rescue | Broken | Net | Precision | Assisted accuracy |",
              "|---:|---|---:|---:|---:|---:|---:|---:|"]
    for r in fs:
        lines.append(f"| {r['alpha']:.3f} | {r['first_action'] or 'none'} | {r['actions']} | {r['rescue']} | {r['broken']} | {r['net']:+d} | {100*r['precision']:.1f}% | {100*r['assisted_accuracy']:.2f}% |")

    lines += ["","## D. Independent transition indicators","",
              "| Indicator | Date | Apr-Jun 2026? |","|---|---|---|"]
    for k,v in indicators.items():
        lines.append(f"| {k} | {v or 'none'} | {in_window[k]} |")
    lines += ["",f"Independent indicators inside Apr-Jun transition window: **{sum(in_window.values())}/{len(in_window)}**","",
              "## Interpretation discipline","",
              "- Workstream A is label-free and calibrated only on pre-2026 market geometry.",
              "- SELLR threshold was selected on 2025 before its 2026 stress, but STCR persistence is a post-hoc synthesis challenger.",
              "- Fixed-share variants are all reported; no 2026 alpha is selected.",
              "- BOCPD V4 remains post-hoc development evidence despite its robustness.",
              "- The program seeks convergence of independent mechanisms, not the maximum retrospective accuracy."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: competence-transition-program-run
