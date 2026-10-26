#!/usr/bin/env python3
"""V15 business intelligence: EXPLAIN unchanged BASE14/CFTC21 anomaly models.
Not a drop predictor, classifier, recalibrated signal, or trading system.
Uses historical outcomes ONLY in retrospective audit, never risk calculation.
"""
from pathlib import Path
from zipfile import ZipFile
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import IsolationForest
import research as v13
import gold_risk_cftc_v8_fixed as old

ROOT=Path(__file__).parent
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)
GROUPS={"GOLD_PRICE_TREND":range(0,5),"CROSS_METALS":[5],
        "GVZ":range(6,10),"USD":[10,11],
        "NOMINAL_YIELDS":[12,13],"CFTC":range(14,21)}
FAMS={"BASE14":list(range(14)),"CFTC21":list(range(21))}
RAW_NAMES={"BASE14":"BASE_14","CFTC21":"BASE_14_PLUS_CFTC_7"}


def sources():
    if not (v13.I/"source.zip").exists():
        with ZipFile(ROOT/"frozen_inputs.zip") as z:
            z.extractall(v13.I)
    fixed=v13.corrected_cftc()
    src,cot,_=old.load(v13.I/"source.zip",fixed)
    ref=old.make_rows(src,cot)
    _,official_daily=old.compute(ref)
    weekly=v13.cot_archives()
    panel,_=v13.build_panel(src,ref,weekly)
    return ref,pd.DataFrame(official_daily),panel


def explain_models(rows,official,panel):
    records=[]
    parameters=[]
    for yr,cut,lo,hi in [
        (2025,"2024-12-31","2025-01-01","2025-12-31"),
        (2026,"2025-12-31","2026-01-01","2026-09-21")]:
        train=[r for r in rows if r["target_mature"]<=cut]
        eval_rows=[r for r in rows if lo<=r["origin"]<=hi]
        for family,ix in FAMS.items():
            x=np.array([r["features"] for r in train],float)[:,ix]
            y=np.array([r["features"] for r in eval_rows],float)[:,ix]
            scale=RobustScaler().fit(x)
            model=IsolationForest(n_estimators=200,max_samples=min(256,len(train)),
                     contamination="auto",random_state=1701,n_jobs=1).fit(scale.transform(x))
            train_scores=-model.score_samples(scale.transform(x))
            risk=-model.score_samples(scale.transform(y))
            red=float(np.quantile(train_scores,.95))
            yellow=float(np.quantile(train_scores,.90))
            orig=official[(official.period==str(yr))&
                          (official.family==RAW_NAMES[family])].set_index("origin")
            assert len(orig)==len(eval_rows)
            target=np.array([float(orig.loc[r["origin"],"risk_score"]) for r in eval_rows])
            np.testing.assert_allclose(risk,target,atol=1e-12,rtol=1e-12)
            assert abs(red-float(orig.train_threshold_red.iloc[0]))<1e-12
            med=np.median(x,axis=0)
            iqr=np.maximum(np.quantile(x,.75,axis=0)-np.quantile(x,.25,axis=0),1e-8)
            deviations=(y-med)/iqr
            sorted_scores=np.sort(train_scores)
            whatif={}
            for group,indices in GROUPS.items():
                local=[ix.index(k) for k in indices if k in ix]
                if not local:continue
                changed=y.copy()
                changed[:,local]=med[local]
                neutral=-model.score_samples(scale.transform(changed))
                whatif[group]=risk-neutral
            for j,row in enumerate(eval_rows):
                date=row["origin"]
                expected="RED" if risk[j]>=red else ("YELLOW" if risk[j]>=yellow else "NORMAL")
                if expected!=orig.loc[date,"alert_level"]:
                    raise ValueError("ALARM_CHANGED_FOR_"+family+"_"+date)
                group_rank=sorted(whatif,key=lambda name:whatif[name][j],reverse=True)
                top=sorted(range(len(ix)),key=lambda k:abs(deviations[j,k]),reverse=True)[:4]
                daily=float(panel.loc[pd.Timestamp(date),"day_return_pct"])
                records.append(dict(origin=date,model=family,alert_level=expected,
                    risk_score=float(risk[j]),red_threshold=red,yellow_threshold=yellow,
                    distance_to_red=float(risk[j]-red),
                    training_risk_percentile=float(100*np.searchsorted(
                       sorted_scores,risk[j],side="right")/len(sorted_scores)),
                    price=float(row["gold_price_usd_oz"]),
                    gold_change_today_pct=daily,
                    gold_5day_past_logreturn_pct=float(100*panel.loc[pd.Timestamp(date),"AU_ret5"]),
                    today_price_direction="DOWN" if daily<0 else "UP" if daily>0 else "FLAT",
                    strongest_whatif_group=group_rank[0],
                    strongest_whatif_change=float(whatif[group_rank[0]][j]),
                    all_whatif_group_changes="|".join(
                      f"{k}:{whatif[k][j]:+.5f}" for k in group_rank),
                    outlying_parameters="|".join(
                      f"{old.FEATURES[ix[k]]}:{deviations[j,k]:+.2f}IQR" for k in top),
                    cftc_observed_position_date=row["cftc_observed_position_date"],
                    cftc_available_date=row["cftc_available_date"],
                    cftc_publication_status=row["cftc_publication_status"],
                    future_nextday_pct_AUDIT_ONLY=float(row["next_day_return_pct"]),
                    future_5day_min_pct_AUDIT_ONLY=float(row["next5_min_return_pct"]),
                    future_drop5_AUDIT_ONLY=bool(row["y_next5_drawdown5"]),
                    new_prediction_model=False,changes_original_alert=False,
                    numeric_first_print_PIT_verified=False))
                for k,oldidx in enumerate(ix):
                    parameters.append(dict(origin=date,model=family,
                        feature=old.FEATURES[oldidx],value=float(y[j,k]),
                        training_median=float(med[k]),training_iqr=float(iqr[k]),
                        deviation_iqr=float(deviations[j,k])))
    result=pd.DataFrame(records)
    assert len(result)==786
    for yr,reference in [(2025,[("BASE14",32,27),("CFTC21",21,17)]),
                         (2026,[("BASE14",50,40),("CFTC21",32,25)])]:
        for family,red_n,false_n in reference:
            d=result[(result.model==family)&(result.origin.str[:4]==str(yr))]
            flagged=d[d.alert_level=="RED"]
            assert len(flagged)==red_n,(yr,family,"red")
            assert int((~flagged.future_drop5_AUDIT_ONLY).sum())==false_n,(yr,family,"false")
    result.to_csv(OUT/"v15_daily_intelligence.csv",index=False)
    pd.DataFrame(parameters).to_csv(OUT/"v15_parameter_trace.csv",index=False)
    return result


def historical_casebook(panel):
    # Existing case-control archive, retrospective only; no new learning weights.
    pairs=pd.read_csv(OUT/"v14_event_control_pairs.csv")
    pairs=pairs[pairs.family=="MACRO_METAL"]
    events=v13.events(panel,"2010-01-01","2022-12-31")
    assert len(events)==27 and len(pairs)==27
    cols=["AU_ret5","AU_ret20","disp5","gvz_level","gvz_dlog5",
          "usd_ret5","nom10_delta5","real10_delta5","GC_net","GC_d1","SI_net"]
    out=[]
    for e in events:
        control=pairs.loc[pairs.event_id==e["event_id"]]
        assert len(control)==1
        dates=[("PRE_DECLINE_PEAK",e["peak"])]
        dates += [("MATCHED_NO_DROP",x) for x in control.control_days.iloc[0].split("|")]
        for typ,date in dates:
            snap=panel.loc[pd.Timestamp(date),cols]
            out.append(dict(event_id=e["event_id"],type=typ,date=date,
                peak=e["peak"],onset_daily_proxy=e["onset_proxy"],
                trough=e["trough"],realized_drawdown_pct=e["drawdown_pct"],
                **{c:float(snap[c]) for c in cols}))
    casebook=pd.DataFrame(out)
    assert len(casebook)==108
    casebook.to_csv(OUT/"v15_historical_cases_and_controls.csv",index=False)
    desc=[]
    for c in cols:
        pos=casebook.loc[casebook.type=="PRE_DECLINE_PEAK",c]
        neg=casebook.loc[casebook.type=="MATCHED_NO_DROP",c]
        desc.append(dict(feature=c,case_count=len(pos),control_count=len(neg),
            case_median=float(pos.median()),control_median=float(neg.median()),
            case_q25=float(pos.quantile(.25)),case_q75=float(pos.quantile(.75)),
            control_q25=float(neg.quantile(.25)),control_q75=float(neg.quantile(.75)),
            comparison_only=True,not_a_forecast=True))
    pd.DataFrame(desc).to_csv(OUT/"v15_case_control_descriptive_statistics.csv",index=False)
    return casebook



def lookup_historical_analogues(panel,intelligence,casebook):
    """Evidence retrieval in existing 14/21-parameter space, NO prediction.
    Only compare to pre-2023 historical known drawdown/control snapshots.
    Distances are descriptive; class labels are hindsight and NOT converted into
    probabilities, weights, thresholds, or automatic signals.
    """
    hist_names=["AU_ret5","AU_ret20","rsi14","ma20gap","au_vol5","disp5",
        "gvz_level","gvz_z252","gvz_dlog5","gvz_dlog1","usd_ret5","usd_ret1",
        "nom10_delta5","nom10","GC_net","SI_net","GC_d1","GC_d4",
        "SI_d4","GC_SI_diff","GC_short"]
    assert len(hist_names)==21
    training=panel.loc[:"2022-12-31",hist_names].dropna()
    median=training.median(axis=0).to_numpy()
    scale=np.maximum((training.quantile(.75)-training.quantile(.25)).to_numpy(),1e-8)
    historical_rows=[]
    for _,x in casebook.iterrows():
        d=pd.Timestamp(x["date"])
        v=panel.loc[d,hist_names].to_numpy(dtype=float)
        if np.isfinite(v).all():
            historical_rows.append((x,v))
    assert len(historical_rows)>=85
    found=[]
    for _,q in intelligence.iterrows():
        if q["alert_level"]!="RED":continue
        d=pd.Timestamp(q["origin"])
        ix=FAMS[q["model"]]
        x=panel.loc[d,hist_names].to_numpy(dtype=float)
        assert np.isfinite(x[ix]).all()
        distances=[]
        for h,v in historical_rows:
            dist=float(np.linalg.norm((x[ix]-v[ix])/scale[ix])/np.sqrt(len(ix)))
            distances.append(dict(kind=h["type"],event_id=h["event_id"],
                reference_date=h["date"],relative_distance=dist,
                historic_event_drawdown_pct=h["realized_drawdown_pct"]))
        desc=sorted(distances,key=lambda z:z["relative_distance"])
        case=next(k for k in desc if k["kind"]=="PRE_DECLINE_PEAK")
        control=next(k for k in desc if k["kind"]=="MATCHED_NO_DROP")
        found.append(dict(origin=q["origin"],model=q["model"],
            original_alert=q["alert_level"],
            original_risk_score=q["risk_score"],
            nearest_historic_crash_date=case["reference_date"],
            nearest_historic_crash_event_id=case["event_id"],
            nearest_crash_parameter_distance=case["relative_distance"],
            historic_crash_realized_size_pct_AUDIT_ONLY=case["historic_event_drawdown_pct"],
            nearest_historic_no_crash_date=control["reference_date"],
            nearest_control_parameter_distance=control["relative_distance"],
            historical_analog_used_to_change_alarm=False,
            does_not_estimate_future_drop_probability=True))
    result=pd.DataFrame(found)
    assert len(result)>50
    result.to_csv(OUT/"v15_historical_parameter_analogues.csv",index=False)
    return result

def main():
    rows,official,panel=sources()
    intelligence=explain_models(rows,official,panel)
    cases=historical_casebook(panel)
    analogues=lookup_historical_analogues(panel,intelligence,cases)
    flags=intelligence[intelligence.alert_level=="RED"].copy()
    flags["retrospective_outcome_AUDIT_ONLY"]=np.where(
       flags.future_drop5_AUDIT_ONLY,"DROP_WITHIN_NEXT_5_DAYS","NO_DROP_WITHIN_NEXT_5_DAYS")
    flags.groupby(["model","retrospective_outcome_AUDIT_ONLY",
                   "strongest_whatif_group"]).size().reset_index(name="days").to_csv(
       OUT/"v15_retrospective_alarm_driver_audit.csv",index=False)
    intelligence[intelligence.origin.isin([
         "2025-05-09","2026-01-21","2026-01-23","2026-01-29",
         "2026-03-30","2026-06-05","2026-08-11","2026-08-21"
       ])].to_csv(OUT/"v15_example_dates.csv",index=False)
    summary=dict(status="EXPLANATION_ONLY",classifier_or_forecast_trained=False,
        math_formula="RobustScaler / IsolationForest, 200 trees, train q90/q95",
        added_alarm_rule=False,original_BASE14_CFTC21_levels_changed=False,
        historical_event_groups=27,historical_control_days=81,
        rows_daily=len(intelligence),rows_historical=len(cases),
        rows_alarm_historical_analogues=len(analogues),
        first_print_PIT_certified=False,neon_modified=False,
        provenance="V13 frozen historical source pack; corrected CFTC 2023 delay",
        interpretation="Counterfactual median group substitution is NON-ADDITIVE sensitivity, NOT SHAP, causality, probability or a calibrated drop forecast")
    (OUT/"v15_audit.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    doc="""# V15 — MEVCUT RİSK MODELLERİNE İŞ ZEKÂSI EKİ (TAHMİN DEĞİL)

Eski BASE14 / CFTC21 değiştirilmedi. Yeni regresyon, GBM, risk olasılığı
ve hedef etiketlerinden öğrenilmiş eşik yok. Yalnızca orijinal 14/21 özelliğin,
RobustScaler + IsolationForest (200 ağaç) skorunun ve eğitim dönemi %90/%95
sınırlarının **neden alarm verdiğini** gösteren tarihsel analiz katmanı var.

## Denetlenmiş sonuç
- 2026 BASE14: 50 kırmızı, 40 yanlış gün (sonraki 5 gün %5 kriteri).
- 2026 CFTC21: 32 kırmızı, 25 yanlış gün.
- 2025 BASE14: 32 kırmızı, 27 yanlış gün; CFTC21: 21 / 17.
- 2010–2022: 27 olay ve 81 kontrol gününün göstergeleri betimsel kıyaslandı.

## Dosyalar
- outputs/v15_daily_intelligence.csv: orijinal alarm, skor, eğitim eşiği,
  kırmızıya uzaklık, eğitim skor yüzdeliği, bugünkü fiyat hareketi, CFTC
  geçerli tarihleri, gösterge grubu duyarlılıkları.
- outputs/v15_parameter_trace.csv: her girdinin gerçek değeri, eğitim
  medyanı ve medyana uzaklığı (IQR).
- outputs/v15_example_dates.csv: Ocak/Haziran/Ağustos ve yanlış-alarm günleri.
- outputs/v15_historical_cases_and_controls.csv: tarihsel olay defteri.
- outputs/v15_case_control_descriptive_statistics.csv: geçmiş dağılımlar.
- outputs/v15_retrospective_alarm_driver_audit.csv: sonuç etiketleriyle
  yalnız SONRADAN yapılan yanlış/doğru alarm gruplaması.
- outputs/v15_historical_parameter_analogues.csv: her kırmızı alarm için
  mevcut 14/21 parametre uzayında en benzer tarihsel düşüş ve düşüşsüz
  dönem. Bu yalnız kayıt/kanıt aramasıdır; alarm ya da düşüş tahmini DEĞİLDİR.
- outputs/v15_audit.json: bütün koruma kontrolleri.

## Yorum sınırları
Gösterge grubu duyarlılığı: o gruptaki girdiler eğitim medyanıyla
değiştirilse mevcut IsolationForest skoru nasıl değişirdi? Bu, katkı
yüzdesi ya da nedensellik değildir; gruplar toplamı skoru vermez.
Yükseliş/düşüş bilgisi ilgili karar gününün tarihsel fiyatına aittir.
Gelecek beş günlük gerçekleşme SADECE retrospektif denetimde kullanılır,
alarm skoruna/eşiğine/kararına girmez. Günlük veriden kesin intraday
erkenlik sonucu çıkarılamaz. Geçmiş resmî ilk yayın numerik vintage
tam sertifikalı değildir. Canlı alarm, Neon ve orijinal kod dokunulmadı.
"""
    (ROOT/"V15_BUSINESS_INTELLIGENCE_TR.md").write_text(doc)
    print("V15_BI_EXECUTED",json.dumps(summary))


if __name__=="__main__":
    main()
