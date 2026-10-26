#!/usr/bin/env python3
"""Gold V18: non-forecast episode intelligence integrated with original BASE14.

Three transparent paths based on ORIGINAL IsolationForest scores and inputs:
 A volatility-dominant BASE14 RED (V15 median-neutralized effect)
 B original 14-input anomaly RED resembling 2010-2022 physical drawdown case
 C CFTC21 agrees on RED as BASE14 anomaly RISES and daily gold already softens
PLUS max one subsequent correctly-adjacent YELLOW period during continuing
negative gold return after prior DAY's confirmed BASE14 RED.

The original BASE14/CFTC21 levels are never changed or suppressed.
RED vs YELLOW is preserved alongside separate TRIAGE priority.
No logistic/GBM, no prices/probabilities forecast, no learned target labels.
Future returns only appear in retrospective QA outputs. Original CFTC
release time gates reused as provided by V13 source pack.
WARNING: historical initial numerical vintages not PIT certified.
2026 is retrospective, previously observed by the researcher.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).parent
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)
MAX_ADJACENCY_CALENDAR_DAYS=4

def apply_triage():
    bi=pd.read_csv(OUT/"v16_bi_daily.csv")
    d=bi.sort_values(["model","origin"]).copy()
    base=d[d.model=="BASE14"].sort_values("origin").reset_index(drop=True).copy()
    cftc=d[d.model=="CFTC21"].set_index("origin")
    assert len(base)==393 and len(cftc)==393
    assert set(base.origin)==set(cftc.index)
    strong=[];reason=[];yellow_continued=[];score_increase=[]
    for i,row in base.iterrows():
        prior=base.iloc[i-1] if i else None
        # Calendar-safe: only a truly adjacent scored session may establish
        # a state transition; never carry through missing days/quarantine.
        adjacent=bool(prior is not None and
            0 < (pd.Timestamp(row.origin)-pd.Timestamp(prior.origin)).days <= MAX_ADJACENCY_CALENDAR_DAYS)
        cf=cftc.loc[row.origin]
        prior_risk=float(prior.risk_score) if adjacent else np.nan
        increase=bool(adjacent and float(row.risk_score)>prior_risk)
        red=row.alert_level=="RED"
        path_a=bool(red and row.BI_gvz_dominant)
        path_b=bool(red and row.BI_crash_analogue_closer)
        # Score acceleration + gold softness, confirmed by the ORIGINAL
        # CFTC21 RED; present/past source observations only.
        path_c=bool(red and cf.alert_level=="RED" and
            float(row.gold_change_today_pct)<0 and increase)
        confirmed=path_a or path_b or path_c
        # Hysteresis: price softness while original risk nearly recedes
        # to YELLOW immediately after previous day's stronger RED.
        # Only ONE YELLOW after original RED, no transitive YELLOW->YELLOW.
        carry=bool(adjacent and row.alert_level=="YELLOW" and
            prior.BI_priority=="BI_CONFIRMED" and
            float(row.gold_change_today_pct)<0)
        paths=[]
        if path_a:paths.append("GVZ_ANOMALY")
        if path_b:paths.append("HISTORIC_CASEBOOK")
        if path_c:paths.append("CFTC_CONFIRMED_RISK_ACCELERATION")
        if carry:paths.append("ONE_SESSION_YELLOW_CONTINUATION")
        strong.append(confirmed or carry)
        reason.append("|".join(paths) if paths else ("OTHER_ORIGINAL_RED" if red else "NO_STRONG_PATH"))
        yellow_continued.append(carry)
        score_increase.append(increase)
    base["BI_strong_attention"]=strong
    base["BI_reason_three_paths"]=reason
    base["BI_hysteresis_yellow"]=yellow_continued
    base["BI_risk_score_increased_vs_previous_session"]=score_increase
    base["BI_status"]=np.where(base.BI_hysteresis_yellow,
        "CONTINUING_YELLOW",np.where(base.BI_strong_attention,
        "STRONG_REVIEW",np.where(base.alert_level=="RED","RED_REQUIRES_REVIEW","STANDARD")))
    base["BI_does_not_change_original_alert"]=True
    base["BI_current_origin_only"]=True
    base["BI_first_print_PIT_certified"]=False
    # Deliberately DO NOT overwrite 'alert_level' or 'risk_score'.
    for f in ["origin","alert_level","risk_score"]:
        np.testing.assert_array_equal(
            base[f].to_numpy(),
            d[d.model=="BASE14"].sort_values("origin")[f].to_numpy())
    assert not base.BI_strong_attention[(base.alert_level=="NORMAL")].any()
    assert base.BI_hysteresis_yellow.sum() <= base.BI_strong_attention.sum()
    base.to_csv(OUT/"v18_daily_business_intelligence.csv",index=False)
    return base

def validate(base):
    measures=[]
    for yr,frame in base.groupby(base.origin.str[:4],sort=True):
        frame=frame.reset_index(drop=True)
        y5=frame.future_drop5_AUDIT_ONLY.to_numpy(bool)
        y1=frame.future_nextday_pct_AUDIT_ONLY.to_numpy(float)<=-3
        starts=[]
        prev=None
        for i,p in enumerate(y5):
            if p:
                if prev is None or i!=prev+1:starts.append([])
                starts[-1].append(i)
                prev=i
        # Note: only consecutive target-day runs grouped, not physical
        # price-pullback identity (audited separately).
        flags={
          "BASE14_ORIGINAL_RED":frame.alert_level.eq("RED").to_numpy(bool),
          "BASE14_V16_TWO_PATH":frame.BI_priority.eq("BI_CONFIRMED").to_numpy(bool),
          "V18_THREE_PATH_RED":(frame.BI_strong_attention&
                                  frame.alert_level.eq("RED")).to_numpy(bool),
          "V18_THREE_PATH_WITH_ONE_DAY_CARRY":frame.BI_strong_attention.to_numpy(bool),
        }
        for label,mask in flags.items():
            measures.append(dict(year=int(yr),policy=label,origins=len(frame),
                marked_days=int(mask.sum()),
                nextday3_hits=int((mask&y1).sum()),nextday3_total=int(y1.sum()),
                next5_origins_hit=int((mask&y5).sum()),
                next5_origins_total=int(y5.sum()),
                five_day_label_clusters_hit=sum(bool(mask[g].any()) for g in starts),
                five_day_label_clusters_total=len(starts),
                false5_marked_days=int((mask&~y5).sum()),
                y5_precision_retro_only=round(float((mask&y5).sum())/max(1,int(mask.sum())),6)))
    m=pd.DataFrame(measures)
    m.to_csv(OUT/"v18_2025_2026_same_day_replay.csv",index=False)
    return m

def event_handoff(base):
    # Larger physical event groups from the incident casebook 2023-25;
    # 2026 event proxy derived by PREEXISTING V13 report. Neither affects
    # current origin decision flags.
    physical=pd.read_csv(OUT/"v17_2023_2025_real_drawdown_events.csv")
    historical=pd.read_csv(OUT/"event_alarm_timeline.csv")
    physical=physical[["event_id","onset_proxy","trough"]].copy()
    physical["type"]="modern_2024_2025_daily_proxy"
    historical=historical[(historical.period==2026)&
                          (historical.model=="BASE14")&
                          (historical.timing!="NOT_EVALUABLE_QUARANTINE")]
    extra=pd.DataFrame({"event_id":historical.event_id,
        "onset_proxy":historical.onset_proxy,"trough":None,
        "type":"stress_2026_daily_proxy"})
    ev=pd.concat([physical,extra],ignore_index=True)
    out=[]
    for _,e in ev.iterrows():
        onset=pd.Timestamp(e.onset_proxy)
        frame=base.copy()
        frame["dt"]=pd.to_datetime(frame.origin)
        frame=frame[(frame.dt>=onset-pd.Timedelta(days=31))&
                   (frame.dt<=onset)].sort_values("origin")
        pre=frame[frame.dt<onset]
        orig=pre[pre.alert_level=="RED"]
        priority=pre[pre.BI_strong_attention]
        at=frame[(frame.dt==onset)&(frame.BI_strong_attention)]
        out.append(dict(event=e.event_id,source=e.type,
          onset_proxy=e.onset_proxy,
          first_original_red_prior_31calendar_days=orig.origin.iloc[0] if len(orig) else "",
          first_high_attention_prior_31calendar_days=priority.origin.iloc[0] if len(priority) else "",
          attention_on_onset_close_only=bool(len(at)),
          any_attention_prior=bool(len(priority)),intraday_start_unverified=True))
    t=pd.DataFrame(out)
    t.to_csv(OUT/"v18_actual_drawdown_onset_timeline.csv",index=False)
    return t

def main():
    b=apply_triage()
    m=validate(b)
    event=event_handoff(b)
    get=lambda year,label:m[(m.year==year)&(m.policy==label)].iloc[0]
    expect={
     (2025,"BASE14_ORIGINAL_RED"):(32,27,2,3,3),
     (2025,"BASE14_V16_TWO_PATH"):(28,23,2,3,3),
     (2025,"V18_THREE_PATH_RED"):(28,23,2,3,3),
     (2025,"V18_THREE_PATH_WITH_ONE_DAY_CARRY"):(30,25,3,3,3),
     (2026,"BASE14_ORIGINAL_RED"):(50,40,4,4,4),
     (2026,"BASE14_V16_TWO_PATH"):(28,19,3,4,4),
     (2026,"V18_THREE_PATH_RED"):(32,23,4,4,4),
     (2026,"V18_THREE_PATH_WITH_ONE_DAY_CARRY"):(34,24,4,4,4)}
    for k,exp in expect.items():
        r=get(*k)
        got=(int(r.marked_days),int(r.false5_marked_days),
             int(r.nextday3_hits),int(r.five_day_label_clusters_hit),
             int(r.five_day_label_clusters_total))
        assert got==exp,(k,got,exp)
    assert len(b)==393
    correction=b[(b.origin=="2026-06-09")].iloc[0]
    assert correction.BI_strong_attention and \
       "CFTC_CONFIRMED_RISK_ACCELERATION" in correction.BI_reason_three_paths
    may=b[b.origin=="2025-05-09"].iloc[0]
    assert may.alert_level=="YELLOW" and may.BI_hysteresis_yellow
    audit=dict(scenario="THREE_EXPLANATORY_PATHS_PLUS_ONE_DAY_HYSTERESIS",
       horizon="historical event casebook 2010-22, origin decisions 2025/2026",
       trained_classifier=False,price_prediction_model=False,
       original_BASE14_CFTC21_alerts_unchanged=True,
       **{"2026_is_not_blind":True},
       previous_study_of_2026_can_bias_hypothesis=True,
       first_print_PIT_certified=False,production_promoted=False,
       "y1_2025_added_by_carry":"2025-05-09",
       "y1_2026_added_by_reversal":"2026-06-09",
       rows=len(b),metrics=m.to_dict("records"))
    (OUT/"v18_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
    cols=["year","policy","marked_days","false5_marked_days",
          "nextday3_hits","nextday3_total","five_day_label_clusters_hit",
          "five_day_label_clusters_total"]
    tx=m[cols].to_markdown(index=False)
    doc="""# V18 — ALTIN RİSK MODELİNDE ÜÇ YOLLU İŞ ZEKÂSI

**Eski BASE14/CFTC21 anormallik skorları, eşikleri, kırmızı alarm
seviyeleri ve Neon değiştirilmedi.** Tahminci değil; eski model kararlarının
bağlamını sınıflandıran ve alarm sürekliliğini koruyan bir ekran/veri eki.

## Üç orijinal-girdi temelli ekonomik yol
1. GVZ zaten BASE14 skorunu yükselten baskın nedense güçlü inceleme.
2. Mevcut 14 parametre tarihsel 2010–22 düşüş durumuna, benzer düşüşsüz
   duruma olduğundan yakınsa güçlü inceleme.
3. BASE14 RED iken CFTC21 de RED ve altın bugünkü kapanışta geriliyor,
   BASE14 skoru da önceki **bitişik** işlem gününden daha yüksekse güçlü
   inceleme (pozisyon baskısı + ivmelenen anormallik).
4. **Bir günlük devam kuralı:** Yalnız önceki bitişik BASE14 RED güçlü
   teyitliyse, bugün model YELLOW'a inmiş ve altın düşüyorsa risk
   izleme ekranında önceki güçlü durum bir gün korunur. Ertesi gün
   yeni RED yoksa tekrar YELLOW taşınamaz.
Bu kurallar yeni gelecek fiyat tahmini veya yeni geçmişten öğrenilmiş
çok değişkenli alarm modeli değildir.

## 2025 ve 2026 tarihsel karşılaştırma

""" + tx + """

- 2025 Mayıs 9'da BASE14 YELLOW oldu fakat önceki gün güçlü RED ve
  fiyat yumuşaması vardı; bir günlük devam kuralı düşüşten önce
  izlemeyi korudu. BASE14'ün 2025 ertesi gün >=%3 düşüş 2/3'ü,
  V18 takip katmanında 3/3 olarak işaretleniyor.
- 2026 Haziran 9'da BASE14 ve CFTC21 RED, fiyat kapanışı negatif
  ve BASE14 anormallik skoru önceki oturuma göre yükseliyordu.
  Böylece V16'da düşük öncelikli olan **ertesi gün -%3,67 düşüş
  öncesi** anormallik tekrar yüksek incelemeye alındı.
- 2026 eski BASE14 50 RED, 40 yanlış5 gün; V18 güçlü incelenen
  RED **32 gün, 23 yanlış5 gün**. Tek oturumluk YELLOW takibi dahil
  toplam inceleme 34 gün, 24 yanlış5 gün; dört 5g risk etiket
  kümesi ve dört ertesi gün >=%3 hedef gününün tamamıyla örtüşüyor.
- Bu, **gerçek kırmızı yanlış alarmların 40'tan 24'e indiği** anlamına
  GELMEZ; orijinal 50 RED ve 40 false5 gün değişmedi. V18 ayrı
  dikkat katmanı, daha yüksek öncelikli geçmiş etiket örtüşmesidir.
- 2026 y1 ve küme başarısı bağımsız kör test DEĞİLDİR; 2026 olayları
  araştırma sırasında daha önce görüldü, bu yüzden üçüncü yol ve
  YELLOW devamı doğrudan üretime alınamaz.

## Kabul öncesi kanıt şartları
- 2025 yalnız üç ayrı risk kümesi: istatistiksel örnek sınırlı.
- 2026 daha önce incelendi: başarı iddiası yalnız keşif.
- 2010–2022 tarihsel makro ilk sayısal yayımlanma/vintage henüz
  tam PIT doğrulanmış değil.
- Alarmların fiziksel düşüş başlamadan önce geldiğini kanıtlamak
  için intraday price onset gereklidir.
- Yön/etki değişkenlerinin önemli olduğu bağlamları doğrulamak için
  sonraki bağımsız dönem ve rejim-özgü kontrol şart.

## Dosyalar
- outputs/v18_daily_business_intelligence.csv
- outputs/v18_2025_2026_same_day_replay.csv
- outputs/v18_actual_drawdown_onset_timeline.csv
- outputs/v18_audit.json
- outputs/v18_tests.log
"""
    (ROOT/"V18_THREE_PATH_BI_EVIDENCE_TR.md").write_text(doc)
    print("V18_BI_EXECUTED",json.dumps({k:v for k,v in audit.items() if k!="metrics"}))

if __name__=="__main__":
    main()
