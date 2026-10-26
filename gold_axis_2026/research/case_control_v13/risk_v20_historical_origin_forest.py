#!/usr/bin/env python3
"""V20: real historical expansion of ORIGINAL gold anomaly equation.

Question: do 2010-2022 market examples actually IMPROVE the existing 14/21
input RobustScaler + IsolationForest model on all three later years?

No classification, label training, learned crash probabilities, changed thresholds,
or feature selection. Train models on as-of feature histories, strictly before
the calendar year being tested. Candidate windows preset: since2023,
trailing3, trailing5, since2010. All years 2024/25/26 evaluated without choosing
parameters using 2026. 2025/2026 source original signal strictly frozen.
Original dollar data have conservative H10 lag proxy, historic CFTC first print
not certified, therefore never production signal.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import IsolationForest
import risk_v15_business_intelligence as v15
import risk_v19_2024_original_replay as v19

ROOT=Path(__file__).parent
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)
FEATURES=v19.FEATURES
FAMS=v19.FAMS
CALENDAR=[2024,2025,2026]
WINDOWS=["SINCE_2023","TRAILING_3_YEARS","TRAILING_5_YEARS","SINCE_2010"]
# Factual predeclared physical swing episodes; May2025 and June2026
# nearby repeated y5 cases DO NOT count as multiple independent macro declines.
PHYSICAL=[
 ("2024_11","2024-11-06"),
 ("2025_04_MAY","2025-04-23"),
 ("2025_10","2025-10-20"),
 ("2026_01","2026-01-30"),
 ("2026_MAY_JUNE","2026-06-05"),
 ("2026_08","2026-08-26")
]
def get_original(rows):
    r24=pd.read_csv(OUT/"v19_2024_original_models.csv")
    old=pd.read_csv(OUT/"v15_daily_intelligence.csv")
    df=[]
    for _,r in r24.iterrows():
        df.append(dict(origin=r.origin,model=r.model,window="FROZEN_BASELINE",
            score=r.risk_score,red_threshold=r.red_threshold,
            original_red=r.alert_level=="RED",mark_red=r.alert_level=="RED",
            y1=bool(r.y1_AUDIT_ONLY),y5=bool(r.y5_AUDIT_ONLY),
            next1=r.next1_pct_AUDIT_ONLY,next5=r.next5_pct_AUDIT_ONLY,
            train_size=int(r.trained_origins),source="2024 original 2023-only fit"))
    for _,r in old.iterrows():
        df.append(dict(origin=r.origin,model=r.model,window="FROZEN_BASELINE",
            score=r.risk_score,red_threshold=r.red_threshold,
            original_red=r.alert_level=="RED",mark_red=r.alert_level=="RED",
            y1=bool(r.future_nextday_pct_AUDIT_ONLY<=-3),
            y5=bool(r.future_drop5_AUDIT_ONLY),
            next1=r.future_nextday_pct_AUDIT_ONLY,
            next5=r.future_5day_min_pct_AUDIT_ONLY,
            train_size=np.nan,source="2025/2026 original model unchanged"))
    return pd.DataFrame(df)

def prepare_prices(rows):
    p=pd.DataFrame([dict(origin=r["origin"],price=r["gold_price_usd_oz"]) for r in rows])
    p=p.sort_values("origin").drop_duplicates("origin").reset_index(drop=True)
    return p

def reference_early_peaks(prices):
    result=[]
    for name,onset in PHYSICAL:
        i=prices.index[prices.origin==onset]
        if len(i)!=1:raise ValueError(f"MISSING_ONSET {onset}")
        i=int(i[0])
        prior=prices.iloc[max(0,i-35):i]
        if len(prior)<25:raise ValueError(f"TOO_SHORT_PEAK_LOOKBACK {name}")
        peak=prior.loc[prior.price==prior.price.max()].iloc[-1]
        result.append(dict(event=name,year=int(onset[:4]),price_peak=peak.origin,
            peak_price=float(peak.price),V13_onset_proxy=onset,
            V13_onset_price=float(prices.iloc[i].price),
            already_down_when_proxy_pct=100*(float(prices.iloc[i].price)/float(peak.price)-1),
            peak_method="last_highest_close_of_35_prior_SCORABLE_origins",
            volatility_data_publication_PIT_certified=False))
    q=pd.DataFrame(result)
    assert len(q)==6 and q.year.value_counts().to_dict()=={2026:3,2025:2,2024:1}
    q.to_csv(OUT/"v20_physical_peak_definitions.csv",index=False)
    return q

def candidate_models(rows,panel):
    all_days=pd.DataFrame(index=panel.index)
    all_days=all_days.join(panel[FEATURES])
    scored={}
    for year in CALENDAR:
        scored[year]=[r for r in rows if f"{year}-01-01"<=r["origin"]<=
            (f"{year}-09-21" if year==2026 else f"{year}-12-31")]
        assert len(scored[year])>=155,(year,len(scored[year]))
    records=[];audit=[]
    for year in CALENDAR:
        cut=f"{year-1}-12-31"
        for window in WINDOWS:
            beg={
              "SINCE_2023":"2023-01-01",
              "TRAILING_3_YEARS":f"{year-3}-01-01",
              "TRAILING_5_YEARS":f"{year-5}-01-01",
              "SINCE_2010":"2010-01-01"}[window]
            # Exactly the same original 14/21 model inputs. Historical
            # observations must have all the respective inputs known (as
            # approximated by the documented release-lag source panel).
            selected=all_days.loc[beg:cut]
            for family,ix in FAMS.items():
                inputs=selected[[FEATURES[i] for i in ix]].dropna()
                # no future outcome features, no 2024 outcomes in 2024 train
                assert inputs.index.max()<pd.Timestamp(f"{year}-01-01")
                assert len(inputs)>=170,(year,window,family,len(inputs))
                X=inputs.to_numpy(dtype=float)
                Y=np.array([r["features"] for r in scored[year]],float)[:,ix]
                scale=RobustScaler().fit(X)
                f=IsolationForest(n_estimators=200,max_samples=min(256,len(inputs)),
                   random_state=1701,contamination="auto",n_jobs=1)
                f.fit(scale.transform(X))
                rs=-f.score_samples(scale.transform(Y))
                tr=-f.score_samples(scale.transform(X))
                p95=float(np.quantile(tr,.95))
                audit.append(dict(year=year,window=window,model=family,train_n=len(inputs),
                    training_first=str(inputs.index.min().date()),
                    training_last=str(inputs.index.max().date()),
                    score_origins=len(scored[year]),p95=p95))
                for v,risk in zip(scored[year],rs):
                    records.append(dict(origin=v["origin"],model=family,
                        window=window,score=float(risk),red_threshold=p95,
                        original_red=np.nan,mark_red=bool(risk>=p95),
                        y1=bool(v["y_nextday_drop3"]),y5=bool(v["y_next5_drawdown5"]),
                        next1=v["next_day_return_pct"],
                        next5=v["next5_min_return_pct"],
                        train_size=len(inputs),source="historic-retrained original 14/21 IsolationForest"))
    pd.DataFrame(audit).to_csv(OUT/"v20_fitting_provenance.csv",index=False)
    return pd.DataFrame(records)

def actual_metrics(day,peaks):
    metrics=[];lifecycle=[]
    for (year,window,model),group in day.groupby(
        [day.origin.str[:4], "window","model"],sort=True):
        g=group.sort_values("origin").reset_index(drop=True)
        mark=g.mark_red.to_numpy(bool)
        y1=g.y1.to_numpy(bool);y5=g.y5.to_numpy(bool)
        # Future results used in audit only; never trained.
        first=peaks[peaks.year==int(year)]
        physical=0
        for _,e in first.iterrows():
            peak=pd.Timestamp(e.price_peak)
            pre=g[(pd.to_datetime(g.origin)<=peak)&
                  (pd.to_datetime(g.origin)>=peak-pd.Timedelta(days=21))]
            flagged=pre[pre.mark_red]
            before=bool(len(flagged))
            physical+=int(before)
            lifecycle.append(dict(year=int(year),model=model,window=window,
                 event=e.event,price_peak=e.price_peak,
                 V13_onset=e.V13_onset_proxy,
                 first_red_at_or_before_true_peak=flagged.origin.iloc[0] if before else "",
                 red_before_actual_decline=before,
                 no_intraday_early_claim=True))
        positive_segments=[]
        current=[]
        for i,positive in enumerate(y5):
            if not positive:continue
            if current and i!=current[-1]+1:positive_segments.append(current);current=[]
            current.append(i)
        if current:positive_segments.append(current)
        metrics.append(dict(year=int(year),window=window,model=model,
            scored_origins=len(g),red_days=int(mark.sum()),
            false5_red_days=int((mark&~y5).sum()),y5_positive=int(y5.sum()),
            red_on_y5_positive=int((mark&y5).sum()),
            y1_positive=int(y1.sum()),red_on_y1_positive=int((mark&y1).sum()),
            y5_clusters_with_red=sum(bool(mark[q].any()) for q in positive_segments),
            y5_clusters_total=len(positive_segments),
            distinct_physical_early_peaks_found=physical,
            distinct_physical_peaks_total=len(first),
            research_only=True,first_print_PIT_certified=False))
    m=pd.DataFrame(metrics)
    t=pd.DataFrame(lifecycle)
    m.to_csv(OUT/"v20_annual_results.csv",index=False)
    t.to_csv(OUT/"v20_physical_peak_replay.csv",index=False)
    return m,t

def main():
    rows,_,panel=v15.sources()
    prices=prepare_prices(rows)
    peaks=reference_early_peaks(prices)
    original=get_original(rows)
    variants=candidate_models(rows,panel)
    daily=pd.concat([original,variants],ignore_index=True)
    assert len(daily)>6000
    daily.to_csv(OUT/"v20_all_original_model_replays.csv",index=False)
    metrics,timeline=actual_metrics(daily,peaks)
    # Frozen original historic 2025/2026 labels must match prior audit.
    for year,num in [(2024,18),(2025,32),(2026,50)]:
        g=metrics[(metrics.year==year)&(metrics.window=="FROZEN_BASELINE")&
                   (metrics.model=="BASE14")]
        assert len(g)==1 and g.red_days.iloc[0]==num,(year,"BASE_CHANGED")
    independent=metrics[(metrics.model=="BASE14")&
                        (metrics.window!="FROZEN_BASELINE")]
    audited=dict(independent_design=False,feature_set_unchanged=True,
        fitted_to_drop_outcome=False,training_window_choice_fixed_before_computation=True,
        model_2024_trained_without_2024_data=True,model_2025_trained_without_2025_data=True,
        model_2026_trained_without_2026_data=True,
        2026_stress_previously_seen=True,numerical_first_print_PIT_certified=False,
        production_models_untouched=True,
        windows_tested=WINDOWS,three_years_tested=CALENDAR,
        baseline_recall_2024_not_independently_early=True)
    (OUT/"v20_research_audit.json").write_text(json.dumps(audited,indent=2,ensure_ascii=False)+"\n")
    report=["# V20 — 2010 GEÇMİŞİNİN BASE14/CFTC21 MODELLERİNE GERÇEK KATKISI",
        "", "Tahmin modeli YOK. Mevcut RobustScaler+IsolationForest(200) ve 14/21",
        "parametreleri, eğitim q95 RED eşiği ve rastgele durum aynen.",
        "Sadece eğitim penceresi değişiyor; 2024, 2025, 2026 yıllarının",
        "her birinde o yılın hiçbir verisi eğitimde kullanılmadı.",
        "",
        "## BASE14 2024–2026 koşuları (yanlış alarm = 5 gün %5 düşüş YOK)",
        "",
        metrics[metrics.model=="BASE14"][[
          "year","window","scored_origins","red_days","false5_red_days",
          "red_on_y5_positive","y5_positive","red_on_y1_positive",
          "y1_positive","distinct_physical_early_peaks_found",
          "distinct_physical_peaks_total"]].to_markdown(index=False),
        "",
        "## CFTC21 koşuları",
        "",
        metrics[metrics.model=="CFTC21"][[
          "year","window","red_days","false5_red_days","red_on_y5_positive",
          "y5_positive","distinct_physical_early_peaks_found",
          "distinct_physical_peaks_total"]].to_markdown(index=False),
        "",
        "## Gerçek tepe vs sonradan belirlenmiş V13 olay başlangıcı",
        "",
        peaks[["event","price_peak","V13_onset_proxy","already_down_when_proxy_pct"]].to_markdown(index=False,floatfmt=".2f"),
        "",
        "## Yöntem sınırları",
        "- 2024 yeni bağımsız araştırma, 2025/2026 önceden analizi yapılmış stres dönemleri.",
        "- 2010–2022 makro veri ilk-baskı PIT sayısal vintage tam doğrulanmış değil.",
        "- FRED 10 takvim gün USD gecikmesi kaynak araştırma proxy'sidir, resmî ilk tarih kanıtı değil.",
        "- 2026 bozuk altın fiyat günü geçmiş veride karantinada tutuldu.",
        "- Gerçek fiziksel tepe: V13 olay vekilinden önceki skorlanabilir son 35 seansın en yüksek kapanışı.",
        "- Bu tanım mutlak doğru ekonomik düşüş başlangıcını ispatlamaz; 5-gün",
        "  risk etiketine kıyasla daha sıkı bir erkenlik denetimidir.",
        "- 2025 Nisan/Mayıs ve 2026 Haziran bitişik vaka etiketleri bağımsız sayılmadı.",
        "- Raporun en iyi satırına bakıp 2026 başarısı varmış gibi seçim yapmak,",
        "  aynı döneme fazla uyum riski yaratır; kıyas keşif/denetim amaçlıdır.",
        "- Orijinal BASE14/CFTC21 skor ve uyarıları canlı uygulamada değiştirilmedi.",
        "",
        "Dosyalar: outputs/v20_all_original_model_replays.csv, outputs/v20_annual_results.csv,",
        "outputs/v20_physical_peak_definitions.csv, outputs/v20_physical_peak_replay.csv,",
        "outputs/v20_fitting_provenance.csv, outputs/v20_research_audit.json"
       ]
    (ROOT/"V20_ORIGINAL_MODEL_HISTORICAL_FIT_TR.md").write_text("\n".join(report)+"\n")
    print("V20_COMPLETED",json.dumps(audited,ensure_ascii=False))
if __name__=="__main__":main()
