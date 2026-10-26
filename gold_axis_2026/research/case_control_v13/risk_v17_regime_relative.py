#!/usr/bin/env python3
"""Regime-robust second lens of the SAME V17 experiment, NOT another predictor.

Each one of the 31 original data features yields two 100% origin-safe
descriptors: (a) today's robust deviation from its OWN prior 252 sessions,
(b) change in that deviation in past 5 sessions. No absolute yield or GVZ
regime is imposed; all 62 descriptors compete under a frozen 2010-22
case/negative-control comparison. The 2023-25 events are holdout checks.

This research metric NEVER replaces BASE14/CFTC21 RED alarms. No data or
parameter from 2026 enters selection, fitting, or evaluation.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import research as v13
import risk_v17_event_formation as prior
ROOT=Path(__file__).parent
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)
PHASES=(-20,-10,-5,-3,-1)


def relative_panel(raw,features):
    r=pd.DataFrame(index=raw.index)
    for c in features:
        x=raw[c].astype(float)
        base=x.shift(1).rolling(252,min_periods=125)
        med=base.median()
        iqr=base.quantile(.75)-base.quantile(.25)
        # Fail closed for time windows with no information / insufficient data.
        rel=((x-med)/iqr.where(iqr>1e-8)).clip(-6,6)
        r["REGIME:"+c]=rel
        r["CHANGE5:"+c]=rel-rel.shift(5)
    assert len(r.columns)==62
    return r

def context(events):
    last=-1;grp=-1;result={}
    for e in sorted(events,key=lambda z:z["onset_i"]):
        lo=int(e["onset_i"])-30;hi=int(e["trough_i"])+10
        if lo>last:grp+=1
        last=max(last,hi);result[e["event_id"]]=grp
    return result

def contrasts(raw,relative,features):
    events=v13.events(raw,"2010-01-01","2022-12-31")
    control=pd.read_csv(OUT/"v14_event_control_pairs.csv")
    control=control[control.family=="MACRO_METAL"]
    assert len(events)==27 and len(control)==27
    gp=context(events)
    rows=[];dts=raw.index
    for e in events:
        u=control[control.event_id==e["event_id"]]
        assert len(u)==1
        peak=int(e["peak_i"])
        analogs=[int(dts.get_loc(pd.Timestamp(z))) for z in u.control_days.iloc[0].split("|")]
        for role,anchor in [("EVENT",peak)]+[("NEGATIVE",i) for i in analogs]:
            for k in PHASES:
                j=anchor+k+1
                if not 0<=j<len(dts):continue
                row=dict(event_id=e["event_id"],cluster=gp[e["event_id"]],
                         kind=role,phase=k,origin=str(dts[j].date()))
                row.update({c:relative.iloc[j][c] for c in relative.columns})
                rows.append(row)
    pool=pd.DataFrame(rows)
    pool.to_csv(OUT/"v17r_historical_relative_windows.csv",index=False)
    case=pool[(pool.kind=="EVENT")&(pool.phase==-1)]
    neg=pool[(pool.kind=="NEGATIVE")&(pool.phase==-1)]
    effects=[]
    for col in relative.columns:
        diffs=[]
        for e in events:
            ce=case.loc[case.event_id==e["event_id"],col].dropna()
            co=neg.loc[neg.event_id==e["event_id"],col].dropna()
            if len(ce)!=1 or len(co)<2:continue
            diffs.append((gp[e["event_id"]],float(ce.iloc[0]-co.median())))
        if not diffs:continue
        ss=pd.DataFrame(diffs,columns=["cluster","delta"])
        m=ss.groupby("cluster").delta.median()
        sign=1 if m.median()>=0 else -1
        consistency=float((m*sign>0).mean())
        ctrl_iqr=float(neg[col].quantile(.75)-neg[col].quantile(.25))
        effect=float(m.median()/ctrl_iqr) if ctrl_iqr>1e-8 else 0
        trajectory=[]
        for k in PHASES:
            lag=pool[pool.phase==k]
            byevent=[]
            for e in events:
                ec=lag[(lag.event_id==e["event_id"])&(lag.kind=="EVENT")][col].dropna()
                nc=lag[(lag.event_id==e["event_id"])&(lag.kind=="NEGATIVE")][col].dropna()
                if len(ec)==1 and len(nc)>=2:byevent.append(float(ec.iloc[0]-nc.median()))
            trajectory.append(float(np.median(byevent)/ctrl_iqr) if len(byevent)>=10 and ctrl_iqr>1e-8 else np.nan)
        base=col.split(":",1)[1]
        effects.append(dict(metric=col,base_feature=base,kind=col.split(":")[0],
            family=prior.family(base),direction="HIGH" if sign==1 else "LOW",
            n_cases=len(ss),context_n=len(m),consistency=consistency,
            cluster_effect_IQR=effect,
            abs_effect_IQR=abs(effect),
            phase20=trajectory[0],phase10=trajectory[1],phase5=trajectory[2],
            phase3=trajectory[3],phase1=trajectory[4]))
    effects=pd.DataFrame(effects).sort_values(["consistency","abs_effect_IQR"],ascending=False)
    effects.to_csv(OUT/"v17r_all_62_metrics.csv",index=False)
    # 2010-22-only selection, no 2023-25 and no 2026 results in any fit.
    good=effects[(effects.context_n>=9)&(effects.consistency>=.67)&
                 (effects.abs_effect_IQR>=.18)]
    selected=[]
    for _,x in good.iterrows():
        if sum(t["family"]==x.family for t in selected)>=2:continue
        if any(t["base_feature"]==x.base_feature for t in selected):continue
        selected.append(x.to_dict())
        if len(selected)==6:break
    return effects,selected

def calculate_index(raw,relative,picked):
    train=relative.loc["2010-01-01":"2022-12-31"]
    score_terms=[]
    for p in picked:
        col=p["metric"]
        ref=np.sort(train[col].dropna().to_numpy(float))
        if len(ref)<250:raise ValueError("SHORT_HISTORIC_REFERENCE")
        values=relative[col].to_numpy(float)
        pct=np.searchsorted(ref,values,side="right")/len(ref)
        if p["direction"]=="LOW":pct=1-pct
        score_terms.append(np.where(np.isfinite(values),pct,np.nan))
    # Missing indicators do not spuriously imply a safe market.
    valid=np.stack(score_terms,axis=1)
    enough=np.isfinite(valid).sum(axis=1)>=max(2,int(np.ceil(.8*len(picked))))
    with np.errstate(invalid="ignore"):
        score=np.nanmean(valid,axis=1)*100
    score=np.where(enough,score,np.nan)
    result=pd.DataFrame(index=relative.index)
    result["regime_formation_index"]=score
    reference=result.loc["2010-01-01":"2022-12-31","regime_formation_index"].dropna()
    threshold=float(reference.quantile(.95))
    result["index_attention"]=result.regime_formation_index>=threshold
    return result,threshold

def evaluate(raw,relative,selection,score,threshold):
    events=v13.events(raw,"2023-01-01","2025-12-31")
    events=[e for e in events if e["peak"]>="2023-01-01" and e["trough"]<="2025-12-31"]
    scored=[]
    formation=[]
    for e in events:
        i=int(e["onset_i"])
        start=max(int(raw.index.searchsorted(pd.Timestamp("2023-01-01"))),i-20)
        t=score.iloc[start:i]
        dates=t.loc[t.index_attention.fillna(False)].index
        scored.append(dict(event_id=e["event_id"],year=e["peak"][:4],
            peak=e["peak"],onset_daily_proxy=e["onset_proxy"],trough=e["trough"],
            historical_drawdown_pct=e["drawdown_pct"],
            flagged_before_onset=bool(len(dates)),
            earliest_flag=str(dates[0].date()) if len(dates) else "",
            lead_session_count=int(i-raw.index.get_loc(dates[0])) if len(dates) else None,
            intraday_onset_not_verified=True))
        for k in PHASES:
            j=i+k
            if j<0:continue
            d=raw.index[j]
            if not "2023-01-01"<=str(d.date())<="2025-12-31":continue
            q=dict(event=e["event_id"],year=e["peak"][:4],phase=k,
                 date=str(d.date()),score=score.iloc[j].regime_formation_index,
                 flag=bool(score.iloc[j].index_attention))
            q.update({p["metric"]:relative.iloc[j][p["metric"]] for p in selection})
            formation.append(q)
    eout=pd.DataFrame(scored)
    eout.to_csv(OUT/"v17r_modern_event_timing.csv",index=False)
    pd.DataFrame(formation).to_csv(OUT/"v17r_modern_selected_metric_formation.csv",index=False)
    compare=score.loc["2023-01-01":"2025-12-31"].copy()
    compare["next5_pct_drop_AUDIT_ONLY"]=raw.loc[compare.index,"y5"].values
    compare["nextday_3pct_drop_AUDIT_ONLY"]=raw.loc[compare.index,"y1"].values
    compare=compare[(compare.index<="2025-12-22")&compare.regime_formation_index.notna()]
    compare.to_csv(OUT/"v17r_modern_daily.csv",index_label="origin")
    yearly=[]
    for year,g in compare.groupby(compare.index.year):
        s=g.index_attention.to_numpy(bool);positive=g.next5_pct_drop_AUDIT_ONLY.to_numpy(bool)
        yearly.append(dict(year=int(year),n=len(g),threshold=threshold,
            attention_days=int(s.sum()),positive_5d_days=int(positive.sum()),
            captured_positive_days=int((s&positive).sum()),
            attention_without_5d_drop_days=int((s&~positive).sum()),
            unflagged_positive_days=int((~s&positive).sum())))
    pd.DataFrame(yearly).to_csv(OUT/"v17r_modern_yearly_metrics.csv",index=False)
    return eout,yearly

def main():
    raw,features,_=prior.load()
    relative=relative_panel(raw,features)
    effects,selection=contrasts(raw,relative,features)
    sufficient=len(selection)>=3 and len({q["family"] for q in selection})>=2
    audited=dict(historical_window="2010-2022",candidate_descriptors=len(effects),
        events=27,rule_is_forecast=False,selection_uses_2023_2025=False,
        selection_uses_2026=False,original_risk_alarms_changed=False,
        numerical_first_print_PIT_certified=False,
        picked=selection,has_three_factors_across_two_families=sufficient)
    if selection:
        score,cutoff=calculate_index(raw,relative,selection)
        modern,yearly=evaluate(raw,relative,selection,score,cutoff)
        audited["historical_95pct_cutoff"]=cutoff
        audited["modern_events"]=len(modern)
        audited["modern_events_by_year"]={str(y):len(modern[modern.year==str(y)]) for y in (2023,2024,2025)}
        audited["modern_preonset_event_hits"]=int(modern.flagged_before_onset.sum())
        audited["yearly"]=yearly
    (OUT/"v17r_audit.json").write_text(json.dumps(audited,indent=2,ensure_ascii=False,default=str)+"\n")
    lines=[
      "# V17 — REJİME GÖRE NORMALLEŞTİRİLMİŞ DEĞİŞKEN İNCELEMESİ",
      "",
      "Daha önceki *mutlak* faiz/GVZ seviyelerinin 2023–2025'e taşınmadığı",
      "gözlendi. Bu yüzden AYNI 31 girdiyi kendi önceki 252 günlük",
      "medyan ve IQR'sine göre değerlendiriyor; değişimin beş günlük",
      "ivmesini ayrı kontrol ediyoruz. 31 x 2 = 62 aday ölçüm.",
      "",
      "- Tarihsel vaka/kontrol: 2010–2022",
      "- 2023–2025: sadece sonraki bağımsız dönem kontrolü",
      "- 2026: hiçbir aşamada kullanılmadı",
      "- Değerler resmî ilk-yayın PIT sertifikalı değil.",
      "- BASE14/CFTC21 hesap ve kırmızı alarmları değişmedi.",
      "",
      "## Tüm değişkenlerden tarihsel farklar — ilk 12",
      "",
      effects.head(12)[["metric","family","direction","consistency",
         "cluster_effect_IQR","phase20","phase10","phase5","phase1"]].to_markdown(index=False,floatfmt=".3f"),
      "",
      "## Endeks değişkenleri (yalnız 2010–2022 araştırmasından)",
      ""]
    for q in selection:
        lines.append("- "+q["metric"]+": "+q["direction"]+", "+q["family"]+
            ", vaka/negatif ayrımı tutarlılığı "+str(round(q["consistency"],3))+
            ", çiftli IQR farkı "+str(round(q["cluster_effect_IQR"],3)))
    if selection:
        lines += ["","## 2023–2025 yıllara göre gerçek sonuçlar","",
           pd.DataFrame(audited["yearly"]).to_markdown(index=False,floatfmt=".2f"),
           "","Modern düşüş dönemleri: "+str(audited["modern_events"])+
              "; düşüş vekil başlangıcından önce işaretlenen: "+
              str(audited["modern_preonset_event_hits"])+".",
           ""]
    lines += ["## Değerlendirme","",
      "Bu indeks parametre davranışını betimler, gelecekteki fiyat düşüş",
      "olasılığını veya işlem kararını hesaplamaz. Tüm geçmiş vaka/kontrol",
      "eşleştirmeleri araştırma amaçlıdır, ilk yayın makro verisi kesin",
      "sertifikalı değil. Başarısız testte kural/eşik 2025'e veya 2026'ya",
      "bakılarak değiştirilmedi.",
      "",
      "Kaynak dosyaları: outputs/v17r_all_62_metrics.csv,",
      "outputs/v17r_modern_selected_metric_formation.csv,",
      "outputs/v17r_modern_event_timing.csv,",
      "outputs/v17r_modern_yearly_metrics.csv, outputs/v17r_audit.json."]
    (ROOT/"V17_REGIME_RELATIVE_REVIEW_TR.md").write_text("\n".join(lines)+"\n")
    print("V17_REGIME_RELATIVE_EXECUTED",json.dumps({k:v for k,v in audited.items() if k not in ("picked","yearly")}))
if __name__=="__main__":main()
