#!/usr/bin/env python3
"""Audit existing gold risk architecture with a TRULY out-of-training 2024 year.

Train original same 200-tree RobustScaler/IsolationForest on 2023 origins;
score 2024 only. 2025 & 2026 remain untouched frozen incumbent decisions.
Apply fixed V18 explanatory paths, not a new forecast. Never fit/select on
2024 outcomes. Prior price/feature values and historical 2010-22 cases are
the only BI inputs. Historical first-print numerical macro PIT is NOT certified.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
import gold_risk_cftc_v8_fixed as old
import risk_v15_business_intelligence as v15

ROOT=Path(__file__).parent
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)
FEATURES=["AU_ret5","AU_ret20","rsi14","ma20gap","au_vol5","disp5",
    "gvz_level","gvz_z252","gvz_dlog5","gvz_dlog1","usd_ret5","usd_ret1",
    "nom10_delta5","nom10","GC_net","SI_net","GC_d1","GC_d4","SI_d4",
    "GC_SI_diff","GC_short"]
GROUPS={"PRICE":[0,1,2,3,4],"METAL":[5],"GVZ":[6,7,8,9],
        "USD":[10,11],"YIELD":[12,13],"CFTC":[14,15,16,17,18,19,20]}
FAMS={"BASE14":list(range(14)),"CFTC21":list(range(21))}

def load_evidence():
    rows,original,panel=v15.sources()
    oldout=pd.read_csv(OUT/"v18_daily_business_intelligence.csv")
    # Completely locked incumbent 2025/2026 values
    assert len(oldout)==393 and oldout.origin.min()>="2025"
    return rows,panel,oldout

def original_2024(rows):
    train=[x for x in rows if x["target_mature"]<="2023-12-31"]
    scored=[x for x in rows if "2024-01-01"<=x["origin"]<="2024-12-31"]
    assert len(train)>=180,(len(train),"2023 training missing")
    assert len(scored)>=175,(len(scored),"2024 not aligned")
    records=[];params=[]
    for family,indices in FAMS.items():
        x=np.array([q["features"] for q in train],float)[:,indices]
        y=np.array([q["features"] for q in scored],float)[:,indices]
        scale=RobustScaler().fit(x)
        model=IsolationForest(n_estimators=200,max_samples=min(len(train),256),
            contamination="auto",random_state=1701,n_jobs=1)
        model.fit(scale.transform(x))
        rtrain=-model.score_samples(scale.transform(x))
        scores=-model.score_samples(scale.transform(y))
        yellow,red=np.quantile(rtrain,[.9,.95])
        med=np.median(x,axis=0)
        iqr=np.maximum(np.quantile(x,.75,axis=0)-np.quantile(x,.25,axis=0),1e-8)
        group_effect={}
        for group,indices_global in GROUPS.items():
            ix=[indices.index(j) for j in indices_global if j in indices]
            if not ix:continue
            altered=y.copy();altered[:,ix]=med[ix]
            adjusted=-model.score_samples(scale.transform(altered))
            group_effect[group]=scores-adjusted
        for j,row in enumerate(scored):
            family_groups=sorted(group_effect,key=lambda k:group_effect[k][j],reverse=True)
            level="RED" if scores[j]>=red else "YELLOW" if scores[j]>=yellow else "NORMAL"
            records.append(dict(origin=row["origin"],model=family,
                risk_score=float(scores[j]),yellow_threshold=float(yellow),
                red_threshold=float(red),alert_level=level,
                gold_price_usd_oz=row["gold_price_usd_oz"],
                cftc_observed_position_date=row["cftc_observed_position_date"],
                cftc_available_date=row["cftc_available_date"],
                cftc_publication_status=row["cftc_publication_status"],
                today_pct=np.nan, # filled from price panel later
                main_anomaly_group=family_groups[0],
                component_effects="|".join(f"{k}:{group_effect[k][j]:+.5f}" for k in family_groups),
                y1_AUDIT_ONLY=row["y_nextday_drop3"],
                y5_AUDIT_ONLY=row["y_next5_drawdown5"],
                next1_pct_AUDIT_ONLY=row["next_day_return_pct"],
                next5_pct_AUDIT_ONLY=row["next5_min_return_pct"],
                first_target=row["first_target"],target_mature=row["target_mature"],
                trained_origins=len(train),score_2024_origins=len(scored),
                original_algorithm_math_unchanged=True))
    result=pd.DataFrame(records)
    assert len(result)==2*len(scored)
    for k,name in enumerate(FEATURES):
        result["feature_"+name]=np.tile(
            np.array([r["features"][k] for r in scored],float),len(FAMS))
    result.to_csv(OUT/"v19_2024_original_models.csv",index=False)
    return result,scored,train

def asof_analogues(panel,scored,train):
    historical=pd.read_csv(OUT/"v15_historical_cases_and_controls.csv")
    assert (historical.date.str[:4].astype(int)<=2022).all()
    from datetime import datetime
    s=panel.loc[:'2022-12-31',FEATURES].dropna()
    med=s.median().to_numpy()
    iqr=np.maximum((s.quantile(.75)-s.quantile(.25)).to_numpy(),1e-8)
    candidates=[]
    for _,row in historical.iterrows():
        d=pd.Timestamp(row.date)
        x=panel.loc[d,FEATURES].to_numpy(float)
        if np.isfinite(x).all():
            candidates.append((row,x))
    assert sum(q[0]["type"]=="PRE_DECLINE_PEAK" for q in candidates)>=20
    out=[]
    for row in scored:
        orig=row["origin"]
        v=np.asarray(row["features"],float)
        for fam,ids in FAMS.items():
            dist=[]
            for sample,vector in candidates:
                x=float(np.linalg.norm((v[ids]-vector[ids])/iqr[ids])/np.sqrt(len(ids)))
                dist.append((x,sample))
            crash=min((z for z in dist if z[1]["type"]=="PRE_DECLINE_PEAK"),key=lambda t:t[0])
            ctrl=min((z for z in dist if z[1]["type"]=="MATCHED_NO_DROP"),key=lambda t:t[0])
            out.append(dict(origin=orig,model=fam,closest_case=crash[1]["date"],
                closest_negative=ctrl[1]["date"],case_dist=crash[0],
                negative_dist=ctrl[0],closer_to_case=crash[0]<ctrl[0],
                reference_through_2022=True))
    result=pd.DataFrame(out)
    result.to_csv(OUT/"v19_2024_historical_analogue.csv",index=False)
    return result

def roll_priority(y24,analog,panel):
    two=y24.merge(analog,on=["origin","model"],validate="one_to_one")
    gold=panel["day_return_pct"]
    two["today_pct"]=two.origin.map(lambda x:float(gold.loc[pd.Timestamp(x)]))
    out=[]
    for fam in FAMS:
        a=two[two.model==fam].sort_values("origin").reset_index(drop=True).copy()
        # In 2024 cannot use 2025-26's group names, identical GVZ index logic.
        a["prior_risk"]=a.risk_score.shift(1)
        a["prior_date"]=a.origin.shift(1)
        a["adjacent"]=(pd.to_datetime(a.origin)-pd.to_datetime(a.prior_date)).dt.days.between(1,4)
        a["rising_risk"]=a.adjacent&(a.risk_score>a.prior_risk)
        a["path_A_GVZ"]=a.alert_level.eq("RED")&a.main_anomaly_group.eq("GVZ")
        a["path_B_HISTORY"]=a.alert_level.eq("RED")&a.closer_to_case
        out.append(a)
    all_s=pd.concat(out,ignore_index=True)
    cf=all_s[all_s.model=="CFTC21"].set_index("origin")
    base=all_s[all_s.model=="BASE14"].sort_values("origin").reset_index(drop=True)
    base["path_C_CFTC_RISK_ACCEL"]=base.origin.map(cf.alert_level).eq("RED") & (
        base.alert_level.eq("RED") & (base.today_pct<0) & base.rising_risk)
    base["priority_RED"]=base.path_A_GVZ | base.path_B_HISTORY | base.path_C_CFTC_RISK_ACCEL
    last=base.shift(1)
    base["priority_YELLOW_CARRY"]=base.adjacent&base.alert_level.eq("YELLOW") & (
         base.today_pct<0) & last.priority_RED.fillna(False).astype(bool)
    base["BI_high_attention"]=base.priority_RED|base.priority_YELLOW_CARRY
    base["BI_reasons"]=base.apply(lambda q:"|".join(
      s for valid,s in [(q.path_A_GVZ,"GVZ_ANOMALY"),(q.path_B_HISTORY,"CASEBOOK"),
      (q.path_C_CFTC_RISK_ACCEL,"CFTC_RISK_ACCEL"),
      (q.priority_YELLOW_CARRY,"ONE_DAY_YELLOW_CARRY")] if valid),axis=1)
    base.to_csv(OUT/"v19_2024_BI_signals.csv",index=False)
    return base

def score_metrics(data,physical):
    g=data.sort_values("origin").reset_index(drop=True)
    red=g.alert_level.eq("RED").to_numpy(bool)
    high=g.BI_high_attention.to_numpy(bool)
    y1=g.y1_AUDIT_ONLY.to_numpy(bool)
    y5=g.y5_AUDIT_ONLY.to_numpy(bool)
    # Unlike arbitrary physical events, contiguous 5d target windows are
    # grouped independently and per-year counts preserved.
    groups=[];prev=None
    for i,p in enumerate(y5):
        if p:
            if prev is None or i!=prev+1:groups.append([])
            groups[-1].append(i);prev=i
    out=[]
    for name,mask in [("BASE14_ORIGINAL_RED",red),("V18_BI_THREE_PATH",high)]:
        out.append(dict(model=name,year=2024,origins=len(g),
            alerted=int(mask.sum()),false5=int((mask&~y5).sum()),
            hit5=int((mask&y5).sum()),total5=int(y5.sum()),
            hit1=int((mask&y1).sum()),total1=int(y1.sum()),
            groups_hit=sum(bool(mask[q].any()) for q in groups),groups=len(groups)))
    met=pd.DataFrame(out)
    met.to_csv(OUT/"v19_2024_replay_metrics.csv",index=False)
    drops=pd.read_csv(OUT/"v17_2023_2025_real_drawdown_events.csv")
    drops=drops[drops.year==2024]
    events=[]
    for _,evt in drops.iterrows():
        begin=pd.Timestamp(evt.onset_proxy)
        prior=g[(pd.to_datetime(g.origin)<begin)&(pd.to_datetime(g.origin)>=begin-pd.Timedelta(days=21))]
        flagged=prior[prior.BI_high_attention]
        original=prior[prior.alert_level=="RED"]
        events.append(dict(event_id=evt.event_id,peak=evt.peak,onset_proxy=evt.onset_proxy,
            trough=evt.trough,size_pct=evt.realized_drop_pct,
            first_prior_original_red=original.origin.iloc[0] if len(original) else "",
            first_prior_BI_high=flagged.origin.iloc[0] if len(flagged) else "",
            possible_early_warning=bool(len(flagged))))
    pd.DataFrame(events).to_csv(OUT/"v19_2024_physical_onset.csv",index=False)
    return met,events

def main():
    rows,panel,prior=load_evidence()
    y24,origins,train=original_2024(rows)
    analog=asof_analogues(panel,origins,train)
    output=roll_priority(y24,analog,panel)
    stats,events=score_metrics(output,panel)
    audit=dict(experiment="2024_BACKTEST_OF_EXISTING_14_21_FEATURE_MATH",
        fit_period="2023",validation="2024",prior_2025_2026_models_unchanged=True,
        fit_on_2024_outcomes=False,fit_on_2025_outcomes=False,fit_on_2026_outcomes=False,
        numeric_first_print_PIT_certified=False,run_as_research=True,
        trained_2023_origins=len(train),scored_2024_origins=len(origins),
        metrics=stats.to_dict("records"),major_2024_events=events)
    (OUT/"v19_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
    report=["# V19 — 2024 bağımsız yılını BASE14/CFTC21 asıl denklemiyle sınama",
        "", "2024 için 2023 verileriyle 200 ağaç Isolation Forest 14/21 orijinal",
        "parametrelerini 90/95 eğitim yüzdelik eşiklerini aynen hesapladık.",
        "2024 gerçek fiyat sonuçları hiçbir parametreyi değiştirmedi.",
        "V18 ekonomik yolları yalnız mevcut anormallik + 2010–2022",
        "tarihsel vaka benzerliği ve önceki oturum durumuyla yürütüldü.",
        "",stats.to_markdown(index=False),
        "","## Büyük 2024 olaylarının öncesi","",
        pd.DataFrame(events).to_markdown(index=False),
        "", "## Uyarı ve dürüstlük",
        "- Bu bir 2024 için 2023 eğitimli açıklama/anormallik gösterimi; yatırım getirisi tahmini değil.",
        "- 2025/2026 orijinal BASE14 ve CFTC21 sonuçları aynen dondurulmuştur.",
        "- 2026 önceden görülmüş olduğundan kör doğrulama değildir.",
        "- 2010–2022 makro ilk yayın sayısal vintage sertifikalı değil.",
        "- Günlük kapanış verisiyle intraday ilk düşüş başlangıcı kesin bilinmez.",
        "", "Dosyalar: outputs/v19_2024_original_models.csv,",
        "outputs/v19_2024_historical_analogue.csv,",
        "outputs/v19_2024_BI_signals.csv, outputs/v19_2024_replay_metrics.csv,",
        "outputs/v19_2024_physical_onset.csv, outputs/v19_audit.json."]
    (ROOT/"V19_2024_TRUE_OUT_OF_SAMPLE_TR.md").write_text("\n".join(report)+"\n")
    print("V19_2024_ACTUAL_AUDIT",json.dumps(audit,ensure_ascii=False))
if __name__=="__main__":main()
