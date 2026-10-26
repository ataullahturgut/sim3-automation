#!/usr/bin/env python3
"""V14 independent early-risk candidate integrated with BASE14/CFTC21 *research replay*.

No edits to incumbents or Neon. Inputs: pinned V13 frozen repository archive.
A standalone candidate may generate risk when both incumbent alarms are absent.
No live use: retrospective numeric first-print PIT is not certified.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
import research as v13

ROOT = Path(__file__).parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
FEATURE_SETS = {
    "MACRO_METAL": ["AU_ret5", "AU_ret20", "au_vol5", "disp5", "gvz_level",
                    "gvz_dlog5", "usd_ret5", "nom10_delta5", "real10_delta5",
                    "GC_net", "GC_d1", "SI_net", "AG_ret5", "PT_ret5", "PD_ret5"],
    "NO_CFTC": ["AU_ret5", "AU_ret20", "au_vol5", "disp5", "gvz_level",
                "gvz_dlog5", "usd_ret5", "nom10_delta5", "real10_delta5",
                "AG_ret5", "PT_ret5", "PD_ret5"],
    "SMALL": ["AU_ret5", "AU_ret20", "au_vol5", "disp5", "gvz_dlog5",
              "usd_ret5", "GC_net", "GC_d1", "SI_net"],
}
QUANTILES = (0.75, 0.90, 0.95)


def prepare():
    if not (v13.I / "source.zip").exists():
        with ZipFile(ROOT / "frozen_inputs.zip") as z:
            z.extractall(v13.I)
    src, _, _ = v13.old.load(v13.I / "source.zip", v13.I / "CFTC_GC_SI_2023_2026_QUALITY_GATED.csv")
    path = v13.corrected_cftc()
    _, cot, _ = v13.old.load(v13.I / "source.zip", path)
    ref = v13.old.make_rows(src, cot)
    _, daily = v13.old.compute(ref)
    weekly = v13.cot_archives()
    panel, all_features = v13.build_panel(src, ref, weekly)
    d = pd.DataFrame(daily)
    d.origin = pd.to_datetime(d.origin)
    inc = d.pivot(index="origin", columns="family", values="alert_level")
    inc = inc.rename(columns={"BASE_14": "BASE14", "BASE_14_PLUS_CFTC_7": "CFTC21"})
    assert len(inc[inc.index.year == 2026]) == 161
    assert int(inc.loc[inc.index.year == 2026, "BASE14"].eq("RED").sum()) == 50
    assert int(inc.loc[inc.index.year == 2026, "CFTC21"].eq("RED").sum()) == 32
    return panel, inc, all_features


def train_cases_and_controls(panel, feature_cols):
    """Keep EVERY eligible pre-onset event, not just events with 2 same-year controls.

    Controls use *training* future outcomes for labels, never features. Choose
    cross-year analogues if same-year would exclude critical 2013 events.
    """
    events = v13.events(panel, "2010-01-01", "2022-12-31")
    ready = panel[feature_cols].notna().all(axis=1).to_numpy()
    end = int(panel.index.searchsorted(pd.Timestamp("2023-01-01")))
    candidate = np.zeros(len(panel), dtype=bool)
    candidate[:end] = True
    candidate &= ready
    candidate &= (panel.future_min10.to_numpy() > -0.05)
    candidate &= ~panel.y1.to_numpy(dtype=bool)
    exclusion = np.zeros(len(panel), dtype=bool)
    for e in events:
        a = max(0, int(e["first_label_i"]) - 30)
        b = min(end, int(e["window_end_i"]) + 21)
        exclusion[a:b] = True
    candidate &= ~exclusion
    allowed = np.flatnonzero(candidate)
    assert len(allowed) > 30, "INSUFFICIENT_NEGATIVE_CONTROLS"
    # Matching uses only origin-safe trend, dispersion, volatility.
    matching = ["AU_ret20", "au_vol20", "disp5"]
    fitting = panel.iloc[:end].dropna(subset=matching)
    sc = RobustScaler().fit(fitting[matching])
    transformed = sc.transform(panel[matching].fillna(fitting[matching].median()))
    available = []
    weights_by_event = []
    records = []
    selected_controls = []
    skipped = []
    for e in events:
        peak = int(e["peak_i"])
        pos = [j for j in range(max(0, peak-3), peak+1) if j < end and ready[j]]
        if not pos:
            skipped.append(dict(event_id=e["event_id"], peak=e["peak"], reason="MISSING_ASOF_FEATURES"))
            continue
        pool = [j for j in allowed if all(abs(j-k)>12 for k in selected_controls)]
        ranked = sorted(pool, key=lambda j:
                        (float(np.linalg.norm(transformed[j]-transformed[peak]))
                         + (0 if panel.index[j].year == panel.index[peak].year else 0.3),
                         abs(int(j)-peak)))
        controls = []
        for j in ranked:
            if all(abs(j-x)>12 for x in controls):
                controls.append(int(j))
            if len(controls)>=3:
                break
        # Even in a tight control market, do not silently lose real large crashes.
        if len(controls)<2:
            skipped.append(dict(event_id=e["event_id"], peak=e["peak"], reason="INSUFFICIENT_SAFE_CONTROLS"))
            continue
        selected_controls += controls
        available.append(e)
        weights_by_event.append((e,pos,controls))
    if len(available)<10:
        raise ValueError("INSUFFICIENT_EVENT_COVERAGE")
    # Weight each overlapping physical-event context cluster once.
    sorted_events=sorted(available,key=lambda x:x["onset_i"])
    cluster = {}
    current=-1
    last_end=-1
    for e in sorted_events:
        lo=int(e["onset_i"])-30
        hi=int(e["trough_i"])+10
        if current<0 or lo>last_end:
            current+=1
        last_end=max(hi,last_end)
        cluster[e["event_id"]]=current
    cluster_counts=Counter(cluster.values())
    xs=[];ys=[];weights=[]
    for e,pos,controls in weights_by_event:
        scale=1.0/cluster_counts[cluster[e["event_id"]]]
        for j in pos:
            xs.append(j);ys.append(1);weights.append(scale/len(pos))
        for j in controls:
            xs.append(j);ys.append(0);weights.append(scale/len(controls))
        records.append(dict(event_id=e["event_id"],peak=e["peak"],
                            onset_proxy=e["onset_proxy"],group=cluster[e["event_id"]],
                            positive_samples=len(pos),controls=len(controls),
                            same_year_controls=sum(panel.index[j].year==panel.index[e["peak_i"]].year for j in controls),
                            control_days="|".join(str(panel.index[j].date()) for j in controls)))
    assert all(panel.index[j].year<=2022 for j in xs)
    assert not set(j for _,p,c in weights_by_event for j in p).intersection(set(selected_controls))
    return np.array(xs,dtype=int),np.array(ys,dtype=int),np.array(weights),records,skipped,len(events),len(set(cluster.values()))


def fit_one(panel,feature_names,train_idx,y,w,kind):
    scaler=RobustScaler().fit(panel.iloc[train_idx][feature_names])
    x=scaler.transform(panel.iloc[train_idx][feature_names])
    if kind=="LOGIT":
        clf=LogisticRegression(C=0.05,max_iter=2000,random_state=1701)
    else:
        clf=GradientBoostingClassifier(n_estimators=40,max_depth=2,min_samples_leaf=12,
                                       subsample=0.8,random_state=1701)
    clf.fit(x,y,sample_weight=w)
    return scaler,clf


def serialize_row(name,kind,setname,q,policy,yr,met):
    return dict(model=name,kind=kind,features=setname,threshold_quantile=q,
                policy=policy,period=yr,**met)


def main():
    panel, incumbents, _=prepare()
    dates = incumbents.index
    assert panel.loc[dates,list(FEATURE_SETS["MACRO_METAL"])].notna().all().all()
    baseline = incumbents.BASE14.eq("RED").reindex(dates).astype(bool)
    cftc = incumbents.CFTC21.eq("RED").reindex(dates).astype(bool)
    union = baseline | cftc
    assert not any(d.year > 2026 for d in dates)
    baseline2025 = v13.metrics(panel.loc[dates[dates.year==2025]],baseline.loc[dates[dates.year==2025]])
    # Print full per-group coverage, not just training row count.
    score_rows=[]
    result_rows=[]
    freeze=[]
    audit=[]
    all_alarms = {"BASE14":baseline, "CFTC21":cftc}
    settings={}
    for family,cols in FEATURE_SETS.items():
        idx,y,w,records,skipped,n_events,n_context = train_cases_and_controls(panel,cols)
        assert any(z["peak"].startswith("2013") for z in records), "NO_2013_TRAINING"
        assert n_events>=20 and len(records)>=15, "EVENT_SAMPLE_TOO_SMALL"
        audit.append(dict(family=family,events_discovered=n_events,events_trained=len(records),
                          events_2013_trained=sum(z["peak"].startswith("2013") for z in records),
                          independent_contexts=n_context,control_count=sum(r["controls"] for r in records),
                          positives=int((y==1).sum()),negatives=int((y==0).sum()),
                          missing_events=json.dumps(skipped),first_print_verified=False))
        pd.DataFrame([dict(family=family,**z) for z in records]).to_csv(OUT/f"v14_event_control_pairs_{family}.csv",index=False)
        for kind in ("LOGIT","GBM"):
            sc,clf=fit_one(panel,cols,idx,y,w,kind)
            training=clf.predict_proba(sc.transform(panel.iloc[idx][cols]))[:,1]
            scored=clf.predict_proba(sc.transform(panel.loc[dates,cols]))[:,1]
            for q in QUANTILES:
                th=float(np.quantile(training[y==0],q))
                stand=pd.Series(scored>=th,index=dates)
                for policy,sig in (("INDEPENDENT",stand),("PLUS",union|stand),("VETO",union&stand)):
                    model=f"V14_{family}_{kind}_Q{int(q*100)}_{policy}"
                    all_alarms[model]=sig
                    settings[model]=dict(family=family,kind=kind,threshold=th,quantile=q,policy=policy,
                                         trained_before_2023=True,feature_names=cols)
                freeze.append(dict(family=family,kind=kind,quantile=q,threshold=th,
                                   train_end="2022-12-31", features=cols,first_print_verified=False))
            # Audit scores, not probability claims: sample selection biases calibration.
            score_rows.append(pd.DataFrame({"origin":dates,"model":f"{family}_{kind}","risk_score":scored}))
    pd.concat([pd.read_csv(OUT/f"v14_event_control_pairs_{family}.csv") for family in FEATURE_SETS],ignore_index=True).to_csv(OUT/"v14_event_control_pairs.csv",index=False)
    for name,s in all_alarms.items():
        for yr in (2025,2026):
            x=dates[dates.year==yr]
            result_rows.append(dict(model=name,period=yr,
                     **v13.metrics(panel.loc[x],s.loc[x])))
    # Candidate selection only from 2025, and no 2026 peek.
    v25=[r for r in result_rows if r["period"]==2025 and r["model"].startswith("V14_")]
    eligible=[r for r in v25 if r["hit1"]==r["total1"] and
              r["groups_hit"]==r["groups"] and
              r["false5"]<baseline2025["false5"]]
    winner=sorted(eligible,key=lambda r:(r["false5"],r["false_episodes"],r["model"]))[0]["model"] if eligible else None
    # An explanatory independent candidate that survives the 2025 detection gate
    # is exported separately, even if it fails the false-positive gate.
    capable=[r for r in v25 if r["model"].endswith("_INDEPENDENT")
             and r["hit1"]==r["total1"] and r["groups_hit"]==r["groups"]]
    diag=sorted(capable,key=lambda r:(r["false5"],r["false_episodes"],r["model"]))[0]["model"] if capable else None
    # Before first-print authentication, shadow_mode CANNOT write or replace live signals.
    selected=winner if winner is not None else "BASE14"
    shadow=all_alarms[selected]
    chosen=pd.DataFrame({"origin":dates.astype(str), "BASE14":baseline.values,
                         "CFTC21":cftc.values,
                         "V14_shadow":shadow.values,
                         "V14_candidate":selected,
                         "live_signals_changed":False,
                         "strict_pit_approved":False,
                         "price":panel.loc[dates,"price"].values,
                         "alarm_day_return_pct":panel.loc[dates,"day_return_pct"].values,
                         "nextday_pct":panel.loc[dates,"future_min1"].values*100,
                         "next5_min_pct":panel.loc[dates,"future_min5"].values*100})
    chosen["V14_independent_diagnostic_model"]=diag or "NONE"
    chosen["V14_independent_diagnostic_red"]=all_alarms[diag].values if diag else False
    if diag:
        parts=diag.split("_")
        label=parts[1]+"_"+parts[2] if len(parts)>2 else None
        dscore=pd.concat(score_rows,ignore_index=True)
        ds=dscore.loc[dscore.model.eq(label)].set_index("origin")["risk_score"]
        chosen["V14_independent_diagnostic_score"]=ds.reindex(dates).values
    chosen.to_csv(OUT/"v14_daily_signals.csv",index=False)
    pd.DataFrame(result_rows).to_csv(OUT/"v14_metrics_2025_2026.csv",index=False)
    pd.DataFrame(audit).to_csv(OUT/"v14_training_audit.csv",index=False)
    pd.concat(score_rows,ignore_index=True).to_csv(OUT/"v14_independent_scores.csv",index=False)
    (OUT/"v14_freeze.json").write_text(json.dumps({
        "eligible_2025":len(eligible),"selected_research_candidate":winner,
        "shadow_model":selected,"diagnostic_independent_model":diag,"live_signal_mode":"UNTOUCHED",
        "trained_on_2026":False,"selected_on_2026":False,
        "first_print_certified":False,"intraday_onset_certified":False,
        "signal_approved_for_production":False,"settings":settings,
        "thresholds":freeze},indent=2)+"\n")
    y26=[r for r in result_rows if r["period"]==2026]
    get=lambda name:next(x for x in y26 if x["model"]==name)
    b=get("BASE14");c=get("CFTC21");shadow_result=get(selected)
    diag26=get(diag) if diag else None
    note=("\n".join([
       "# V14 — Bağımsız risk katmanı entegrasyonu (GÖLGE MOD)",
       "",
       "Kapsam: 2010–2022 tarihsel öğrenim, 2025 doğrulama ve 2026 stres;",
       "**orijinal BASE14/CFTC21 ve Neon değiştirilmedi**.",
       "Bu kod, eski model kırmızı vermese de bağımsız skor üretir. Nihai alarm",
       "yalnız 2025 kapısını geçen aday varsa gölge olarak hesaplanır.",
       "",
       f"- Tarihsel olay sayısı: {audit[0]['events_discovered']}; eğitime alınan olay: {audit[0]['events_trained']}; birleştirilmiş bağlam: {audit[0]['independent_contexts']}.",
       f"- 2013 olayları eğitime alınan: {audit[0]['events_2013_trained']} olay.",
       f"- Geçerli 2025 aday: {len(eligible)}.",
       f"- Seçilen araştırma adayı: {selected}.",
       f"- Doğrulama yakalaması tam, ama yanlış alarm şartı başarısız bağımsız tanı modeli: {diag or 'yok'}.",
       "",
       "| 2026 model | Kırmızı | Ertesi gün ≥%3 | 5g risk kümesi | Yanlış alarm günü |",
       "|---|---:|---:|---:|---:|",
       f"| BASE14 | {b['red']} | {b['hit1']}/{b['total1']} | {b['groups_hit']}/{b['groups']} | {b['false5']} |",
       f"| CFTC21 | {c['red']} | {c['hit1']}/{c['total1']} | {c['groups_hit']}/{c['groups']} | {c['false5']} |",
       f"| V14 gölge | {shadow_result['red']} | {shadow_result['hit1']}/{shadow_result['total1']} | {shadow_result['groups_hit']}/{shadow_result['groups']} | {shadow_result['false5']} |",
       (f"| V14 bağımsız (reddedildi) | {diag26['red']} | {diag26['hit1']}/{diag26['total1']} | {diag26['groups_hit']}/{diag26['groups']} | {diag26['false5']} |" if diag26 else ""),
       "",
       "**Üretim kapısı kapalıdır:** ilk yayın sayısal veri vintage ve gerçek seans içi",
       "başlangıç doğrulanmadı. 2026 geçmişte görüldüğünden kör başarı kanıtı değildir.",
       "Gelişme bulunmadıysa gölge sonuç BASE14 referansını gösterir; yeni model başarılı sanılmamalıdır.",
       "Tam adaylar: outputs/v14_metrics_2025_2026.csv.",
       ""] ))
    (ROOT/"V14_REPORT_TR.md").write_text(note+"\n")
    print("V14_DONE",json.dumps({"training":audit,"selected":selected,
                              "eligible2025":len(eligible),"independent_diagnostic":diag,"independent_diagnostic_2026":diag26,"baseline2026":b,
                              "cftc2026":c,"shadow2026":shadow_result},default=str))


if __name__=="__main__":
    main()
