#!/usr/bin/env python3
"""V17: unbiased-for-2026, episode-first explanatory investigation and index.

2010-22: all eligible historical drop cases and 3 matched controls each.
2023-25: NOT used to pick parameters; study their independent precursors.
Feature list is the complete V13 source panel (14+7 base and additional
macro / cross-metal variables), not a preselected GVZ/CFTC narrative.
-1 is LAST observed CLOSE before the daily onset proxy. Strict first-print
PIT not certified. No regression, GBM, fit-to-return or buy/sell forecast.
"""
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd
import research as v13
import risk_v15_business_intelligence as v15

ROOT=Path(__file__).parent
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)
PHASES=(-20,-10,-5,-3,-1)
COL_ORDER=("METALS","GOLD_TREND","GVZ","USD","NOMINAL_RATES","REAL_RATES","CFTC","OTHER")
def family(c):
    if c.startswith(("AG_","PT_","PD_","corr_AU_")) or c=="disp5":return "METALS"
    if c.startswith(("AU_","au_")) or c in ("rsi14","ma20gap"):return "GOLD_TREND"
    if c.startswith("gvz"):return "GVZ"
    if c.startswith(("usd","nom","real")):return "USD" if c.startswith("usd") else "NOMINAL_RATES" if c.startswith("nom") else "REAL_RATES"
    if c.startswith(("GC_","SI_")):return "CFTC"
    return "OTHER"

def load():
    ref, orig, panel = v15.sources()
    features=json.loads((OUT/"feature_contract.json").read_text())["features"] if (OUT/"feature_contract.json").exists() else None
    if features is None:
        src, cot, _=v13.old.load(v13.I/"source.zip",OUT/"CFTC_ION_corrected.csv")
        weekly=v13.cot_archives()
        _,features=v13.build_panel(src,ref,weekly)
    assert len(features)==31,(len(features),features)
    assert len(set(features))==len(features)
    return panel,features,orig

def construct_episode_panels(panel, cols):
    episodes=v13.events(panel,"2010-01-01","2022-12-31")
    prior=pd.read_csv(OUT/"v14_event_control_pairs.csv")
    prior=prior[prior.family=="MACRO_METAL"]
    assert len(episodes)==27 and len(prior)==27
    dates=panel.index
    clusters={}
    last_end=-1
    cluster=-1
    for e in sorted(episodes,key=lambda x:x["onset_i"]):
        a=int(e["onset_i"])-30
        b=int(e["trough_i"])+10
        if a>last_end:cluster+=1
        last_end=max(last_end,b)
        clusters[e["event_id"]]=cluster
    output=[]
    for e in episodes:
        p=prior[prior.event_id==e["event_id"]]
        assert len(p)==1
        onset=int(e["onset_i"])
        peak=int(e["peak_i"])
        assert onset==peak+1
        controls=[str(x) for x in p.control_days.iloc[0].split("|")]
        assert len(controls)==3
        for role,anchor in [("DROP_EVENT",peak)]+[
              ("CONTROL",int(dates.get_loc(pd.Timestamp(c)))) for c in controls]:
            for phase in PHASES:
                j=anchor+phase+1
                if j<0 or j>=len(dates):continue
                date=dates[j]
                z=panel.iloc[j]
                if z[cols].isna().any():continue
                row=dict(event_id=e["event_id"],context_cluster=clusters[e["event_id"]],
                    role=role,phase=phase,origin=str(date.date()),
                    event_onset=e["onset_proxy"],event_peak=e["peak"],
                    event_trough=e["trough"],event_realized_drop=e["drawdown_pct"])
                row.update({c:float(z[c]) for c in cols})
                output.append(row)
    t=pd.DataFrame(output)
    t.to_csv(OUT/"v17_history_formation_windows.csv",index=False)
    return episodes,t,clusters

def effect_audit(panel, cols, windows, clusters):
    peak=windows[windows.phase==-1]
    case=peak[peak.role=="DROP_EVENT"]
    ctr=peak[peak.role=="CONTROL"]
    scale=(ctr[cols].quantile(.75)-ctr[cols].quantile(.25)).replace(0,np.nan)
    reports=[]
    # Compare at all formation phases, avoiding overcounting daily bars as events.
    for col in cols:
        differences=[]
        for event,cp in case.groupby("event_id"):
            cc=ctr[ctr.event_id==event]
            if len(cc)<2:continue
            differences.append(dict(event=event,cluster=clusters[event],
                raw_delta=float(cp[col].iloc[0]-cc[col].median())))
        diff=pd.DataFrame(differences)
        if len(diff)==0:continue
        cluster_mean=diff.groupby("cluster").raw_delta.median()
        directional=np.sign(cluster_mean.replace(0,np.nan).dropna())
        stable=float(max((directional>0).mean(),(directional<0).mean())) if len(directional) else 0
        direction=1 if float(cluster_mean.median())>=0 else -1
        signed_consistency=float((direction*cluster_mean>0).mean())
        iqr=float(scale[col]) if pd.notna(scale[col]) else np.nan
        effect=float(cluster_mean.median()/iqr) if np.isfinite(iqr) and iqr>0 else 0.0
        # Median paired normalized shift and separate time sequence.
        phase_rows={}
        for lag in PHASES:
            s=windows[windows.phase==lag]
            pairs=[]
            for event,g in s[s.role=="DROP_EVENT"].groupby("event_id"):
                c=s[(s.event_id==event)&(s.role=="CONTROL")]
                if len(c)>=2:pairs.append(float(g[col].iloc[0]-c[col].median()))
            phase_rows[str(lag)]=float(np.median(pairs)/iqr) if pairs and iqr>0 else np.nan
        # Positive/negative is signed from original data, not predeclared.
        reports.append(dict(feature=col,family=family(col),direction="HIGH" if direction==1 else "LOW",
          event_rows=int(len(diff)),independent_contexts=int(len(cluster_mean)),
          consistency=signed_consistency,raw_cluster_median_difference=float(cluster_mean.median()),
          normalized_effect=effect,abs_effect=abs(effect),
          historical_case_median=float(case[col].median()),
          historical_control_median=float(ctr[col].median()),
          phase_minus20=phase_rows["-20"],phase_minus10=phase_rows["-10"],
          phase_minus5=phase_rows["-5"],phase_minus3=phase_rows["-3"],
          phase_minus1=phase_rows["-1"]))
    eff=pd.DataFrame(reports).sort_values(
        ["consistency","abs_effect"],ascending=False).reset_index(drop=True)
    eff.to_csv(OUT/"v17_all_feature_effects.csv",index=False)
    # Leave every family eligible. Select on train-only repeatability and effect.
    qualified=eff[(eff.independent_contexts>=8)&(eff.consistency>=.65)&(eff.abs_effect>=.15)]
    picked=[]
    for _,x in qualified.iterrows():
        if sum(y["family"]==x["family"] for y in picked)>=2:continue
        picked.append(x.to_dict())
        if len(picked)==6:break
    # If historical data provide no stable pattern, publish "NO_INDEX".
    sufficient=len(picked)>=3
    return eff,picked,sufficient

def index_values(panel,features,picked):
    """Historic-variable formation index: directional ECDF against all 2010-22
    eligible historical days, not estimated probability of future drop.
    No 2023-25 fitting or threshold tuning.
    """
    historical=panel.loc["2010-01-01":"2022-12-31"]
    vals=[]
    for rule in picked:
        col=rule["feature"]
        dist=np.sort(historical[col].dropna().to_numpy(dtype=float))
        if len(dist)<100:raise ValueError("HISTORIC_REFERENCE_TOO_SMALL_"+col)
        x=panel[col].to_numpy(float)
        pct=np.searchsorted(dist,x,side="right")/len(dist)
        risk=pct if rule["direction"]=="HIGH" else 1-pct
        vals.append(np.where(np.isfinite(x),risk,np.nan))
    if not vals:raise ValueError("NO_SIGNIFICANT_EVENT_FORMATION_PARAMETERS")
    scores=np.nanmean(np.stack(vals,axis=1),axis=1)*100
    out=pd.DataFrame({"origin":panel.index,"formation_index":scores}).set_index("origin")
    # Historic quantile only, not selected using 2023-25 outcomes.
    valid=out.loc["2010":"2022","formation_index"].dropna()
    threshold=float(valid.quantile(.95))
    out["formation_attention"]=out.formation_index>=threshold
    return out,threshold

def examine_holdout(panel,features,idx,threshold):
    events=v13.events(panel,"2023-01-01","2025-12-31")
    events=[e for e in events if e["trough"]<="2025-12-31"
        and e["peak"]>="2023-01-01"]
    assert all(e["peak"][:4] in ("2023","2024","2025") for e in events)
    eps=[]
    phase_rows=[]
    for e in events:
        onset=int(e["onset_i"])
        before=panel.iloc[max(0,onset-20):onset]
        before=before[(before.index>="2023-01-01")&(before.index<="2026-01-01")]
        full=idx.reindex(before.index)
        match=full[full.formation_attention]
        first=str(match.index[0].date()) if len(match) else ""
        ep=dict(event_id=e["event_id"],year=e["peak"][:4],
            first_label=e["first_label"],onset_proxy=e["onset_proxy"],
            peak=e["peak"],trough=e["trough"],realized_drop_pct=e["drawdown_pct"],
            pre_onset_at_least_one_flag=bool(len(match)),
            first_attention_before_onset=first,
            lead_sessions=(onset-panel.index.get_loc(match.index[0])) if len(match) else np.nan,
            onset_does_not_establish_intraday_time=True)
        eps.append(ep)
        for lag in PHASES:
            j=onset+lag
            if j<0 or not "2023-01-01"<=str(panel.index[j].date())<="2025-12-31":continue
            date=panel.index[j]
            row=dict(event_id=e["event_id"],year=e["peak"][:4],phase=lag,
                    origin=str(date.date()),formation_index=idx.loc[date,"formation_index"],
                    flagged=bool(idx.loc[date,"formation_attention"]))
            row.update({col:float(panel.loc[date,col]) for col in features})
            phase_rows.append(row)
    eout=pd.DataFrame(eps)
    eout.to_csv(OUT/"v17_2023_2025_real_drawdown_events.csv",index=False)
    pd.DataFrame(phase_rows).to_csv(OUT/"v17_2023_2025_precursor_windows.csv",index=False)
    # All 2023-25 daily decisions, including negatives. Each alert is measured
    # only against future prices in the audit table, never in index calculation.
    day=idx.loc["2023-01-01":"2025-12-31"].copy()
    day["next5_drawdown5_AUDIT_ONLY"]=panel.loc[day.index,"y5"].values
    day["nextday_drop3_AUDIT_ONLY"]=panel.loc[day.index,"y1"].values
    day["last_observed_price"]=panel.loc[day.index,"price"].values
    day["mature_by_2025"]=day.index <= pd.Timestamp("2025-12-22")
    day=day[day.mature_by_2025 & day.formation_index.notna()]
    day.to_csv(OUT/"v17_2023_2025_daily_index.csv",index_label="origin")
    stats=[]
    for year,g in day.groupby(day.index.year):
        if len(g)<80:continue
        m=g.formation_attention.to_numpy(bool)
        y=g.next5_drawdown5_AUDIT_ONLY.to_numpy(bool)
        stats.append(dict(year=int(year),n=len(g),index95_threshold=threshold,
                          flag_days=int(m.sum()),future5pct_label_days=int(y.sum()),
                          overlap_days=int((m&y).sum()),
                          negative_flag_days=int((m&~y).sum()),
                          missed_label_days=int((~m&y).sum())))
    pd.DataFrame(stats).to_csv(OUT/"v17_2023_2025_daily_outcome_audit.csv",index=False)
    return eout,day,stats

def compare_yearly_feature_phases(windows,holdout,features):
    # Yearly variables are audited on -1 pre-onset, not selected in holdout.
    train=windows[(windows.role=="DROP_EVENT")&(windows.phase==-1)]
    rows=[]
    for year in (2023,2024,2025):
        x=holdout[(holdout.year==str(year))&(holdout.phase==-1)]
        for col in features:
            rows.append(dict(year=year,feature=col,
              early_event_count=len(x),historical_event_count=len(train),
              pre_onset_median=float(x[col].median()) if len(x) else np.nan,
              historical_event_median=float(train[col].median()),
              compatible_direction=False if len(x)==0 else bool(
                (x[col].median()-windows[(windows.role=="CONTROL")&(windows.phase==-1)][col].median())
                *(train[col].median()-windows[(windows.role=="CONTROL")&(windows.phase==-1)][col].median())>0)))
    pd.DataFrame(rows).to_csv(OUT/"v17_2023_2025_feature_direction_check.csv",index=False)

def main():
    panel,features,old_orig=load()
    historical,windows,clusters=construct_episode_panels(panel,features)
    effects,rules,sufficient=effect_audit(panel,features,windows,clusters)
    state=dict(history_period="2010-2022",independent_history_contexts=len(set(clusters.values())),
      history_event_groups=len(historical),history_controls=81,
      feature_count=len(features),rules=rules,has_sufficient_stable_factors=sufficient,
      feature_method="27 event matched contrasts, aggregated to independent context cluster; complete 31-variable screening",
      no_forecast_model=True,used_2026_in_selection=False,modern_years_not_used_to_choose_variables=True,
      first_print_PIT_certified=False,model_production_updated=False,neon_updated=False)
    effects_desc=effects.head(12)[["feature","family","direction","consistency","normalized_effect",
                  "phase_minus20","phase_minus10","phase_minus5","phase_minus1"]]
    if rules:
        index,threshold=index_values(panel,features,rules)
        state["index_reference_95pct_threshold"]=threshold
        events,day,stats=examine_holdout(panel,features,index,threshold)
        hold=pd.read_csv(OUT/"v17_2023_2025_precursor_windows.csv")
        compare_yearly_feature_phases(windows,hold,features)
        state["modern_events"]=len(events)
        state["modern_events_by_year"]={str(year):len(events[events.year==str(year)]) for year in (2023,2024,2025)}
        state["modern_pre_onset_flagged_events"]=int(events.pre_onset_at_least_one_flag.sum())
        state["modern_daily_audit"]=stats
        # 2026 not used for screening, index choice, or threshold; explicitly no 2026 results produced.
    (OUT/"v17_research_audit.json").write_text(json.dumps(state,ensure_ascii=False,indent=2,default=str)+"\n")
    md=["# V17 — DÜŞÜŞLER NASIL OLUŞTU? DEĞİŞKEN TARAMASI VE OLUŞUM İNDİSİ",
      "",
      "Tahminci değil, geriye dönük olay oluşum araştırması ve açıklanabilir",
      "gösterge endeksi. Tek bir faktöre takılmadan, 31 fiyat/makro/pozisyon",
      "değişkeninin tamamı aynı olay ve kontrollerle incelendi.",
      "",
      "## Kapsam ve güvenilirlik",
      "- 2010–2022: "+str(len(historical))+" düşüş grubu, "+str(len(set(clusters.values())))+
       " örtüşmeyen bağlam; 81 benzer düşüşsüz gün.",
      "- 2023–2025: değişken öğrenimine karıştırılmadan dış dönem kontrolü.",
      "- Olayın başlangıcı fiyat kapanışlarına dayalı vekildir. İlk makro yayın",
      "  anının PIT sertifikası mevcut değil.",
      "- Endeks gelecekteki getirinin olasılığı veya bir al/sat kararı değildir.",
      "- BASE14/CFTC21 değiştirilmedi; 2026 aday seçimine sokulmadı.",
      "",
      "## 2010–2022 öncü değişken değerlendirmesi (ilk 12)",
      "",
      effects_desc.to_markdown(index=False,floatfmt=".3f"),
      "",
      "## Seçilmiş değişkenler (yalnız tarihsel kararlılık + vaka-kontrol farkı)",
      ""]
    if rules:
        for i,r in enumerate(rules,1):
            md.append(str(i)+". "+r["feature"]+" ("+r["family"]+", "+r["direction"]+
                      "), tutarlılık "+str(round(r["consistency"],3))+
                      ", medyan etkisi "+str(round(r["normalized_effect"],3))+" IQR")
    else: md.append("Yeterli tutarlılık yok; endeks oluşturulamadı.")
    md += ["","**Örüntü güven kapısı:** "+("en az üç uygun değişken bulundu" if sufficient else
          "üç güçlü/tutarlı bağımsız değişken bulunamadı; indeks sadece keşif amaçlıdır."),
          "",
          "## 2023–2025 bağımsız dönem denetimi",""]
    if rules:
        md.append(pd.DataFrame(state["modern_daily_audit"]).to_markdown(index=False,floatfmt=".2f"))
        md.append("")
        md.append("2023–2025 düşüş grubu sayısı: "+str(state["modern_events"]))
        md.append("Başlangıçtan önce indeks uyarısı görülen grup: "+str(state["modern_pre_onset_flagged_events"]))
        md.append("Uyarılar kontrol başlangıcına kadar her olay için 20 önceki işlem gününde aranmıştır.")
    else:md.append("Endeks oluşturulamayan özellik istikrarı nedeniyle sinyal kıyası yapılmadı.")
    md += ["",
      "## Denetim dosyaları",
      "- outputs/v17_all_feature_effects.csv — 31 değişken ve -20/-10/-5/-3/-1 gün örüntüsü",
      "- outputs/v17_history_formation_windows.csv — olay ve kontrol gelişim çizgileri",
      "- outputs/v17_2023_2025_real_drawdown_events.csv — tüm bağımsız olaylar",
      "- outputs/v17_2023_2025_precursor_windows.csv — modern olay parametreleri",
      "- outputs/v17_2023_2025_daily_index.csv — tüm 2023–2025 kontrol günleri",
      "- outputs/v17_research_audit.json — kapsam ve kabul kapıları",
      "",
      "## Kritik metodoloji",
      "Olaylar ve kontroller geçmişteki gerçekleşmelerle işaretlenir; **bu gelecek etiketleri",
      "endeksin günlük değerinin girdisi değildir**. Etkiler eşleştirilmiş vaka",
      "farklarıdır, nedensel ekonomik etki veya yatırım getirisi değildir.",
      "2010–2022 resmî ilk yayım sayısal PIT doğruluğu kesinleşmeden bu çalışma",
      "canlı kullanıma geçirilemez. 2000–2009 kaynağı henüz mevcut değil.",
    ]
    (ROOT/"V17_EVENT_FORMATION_VARIABLE_STUDY_TR.md").write_text("\n".join(md)+"\n")
    print("V17_COMPLETED",json.dumps({k:v for k,v in state.items() if k not in ("rules","modern_daily_audit")},ensure_ascii=False))
if __name__=="__main__":
    main()
