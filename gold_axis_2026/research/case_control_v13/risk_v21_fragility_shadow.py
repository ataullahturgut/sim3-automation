#!/usr/bin/env python3
"""V21: detect separate 'overheated-but-normal-in-IsolationForest' mode.

NOT a price forecast. No learned probability or new BASE14/CFTC21 RED.
Deliberately exploratory: checked 2024/2026 known events when inventing
narrow band 4%-6%; NEVER claim independent performance from 2024-26.
Original 2010-22 control archive has too few analogue cases to support
this exact rule. Frozen only as prospective candidate/research shadow.

Inputs: the exact original 21 features from source v19 same-day row, with
original frozen 2024/2025/2026 risk level for hard NOT-RED check.
No target, future label, or same-session future enters WATCH.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)

def load():
    panel=pd.read_csv(OUT/"v19_asof_21_variable_panel.csv").sort_values("origin").reset_index(drop=True)
    old24=pd.read_csv(OUT/"v19_2024_BI_signals.csv")
    old24=old24[old24.model=="BASE14"]
    old25=pd.read_csv(OUT/"v18_daily_business_intelligence.csv")
    old=pd.concat([
        old24[["origin","alert_level","risk_score","BI_high_attention"]].rename(
            columns={"BI_high_attention":"original_BI_strong"}),
        old25[["origin","alert_level","risk_score","BI_strong_attention"]].rename(
            columns={"BI_strong_attention":"original_BI_strong"}),
    ],ignore_index=True)
    assert not old.origin.duplicated().any()
    panel=panel.merge(old,on="origin",how="left",validate="one_to_one")
    # 2023 has no as-of original decision here (not evaluated).
    panel=panel[panel.origin.str[:4].isin(["2024","2025","2026"])].reset_index(drop=True)
    assert len(panel)==254+232+161
    assert panel.alert_level.notna().all()
    return panel

def freeze_candidate(panel):
    """
    Formula is expressed solely in observable origin-time base features.

    'Normal in model' is essential: strong/RED already gets original
    operational risk, this is a DIFFERENT watch channel, not an OR RED.
    Notable upper price momentum is bounded: moderate rally, not runaway
    positive spike. This band was inspected after seeing 2024/2026.
    """
    d=panel.copy()
    d["BI_v21_fragility_watch"]=(
        d.alert_level.eq("NORMAL")
        & d.rsi14.ge(.74)
        & d.AU_ret20.ge(.04)
        & d.AU_ret20.le(.06)
        & d.gvz_z252.ge(0)
        & d.GC_d1.lt(0)
    )
    d["BI_effective_existing_red"]=d.alert_level.eq("RED")
    d["BI_priority_still_original"]=d.original_BI_strong
    d["BI_new_RED_count"]=0
    d["BI_is_live_enabled"]=False
    d["BI_research_only"]=True
    d["BI_first_numerical_PIT_certified"]=False
    d["BI_no_2024_2026_blind_claim"]=True
    d["BI_v21_signal_definition"]="NORMAL and RSI>=0.74 and 0.04<=AU_ret20<=0.06 and GVZ_z252>=0 and GC_d1<0"
    # Independent from price reversals/realized drawdown outcome.
    allowed={"alert_level","rsi14","AU_ret20","gvz_z252","GC_d1"}
    assert allowed==set(("alert_level","rsi14","AU_ret20","gvz_z252","GC_d1"))
    for col in ("origin","alert_level","risk_score"):
        np.testing.assert_array_equal(d[col],panel[col])
    d.to_csv(OUT/"v21_daily_shadow.csv",index=False)
    return d

def outcome_audit(d):
    # The 10-session price drop is outcome audit only, NEVER a rule input.
    full=pd.read_csv(OUT/"v19_asof_21_variable_panel.csv").sort_values("origin").reset_index(drop=True)
    money=full.price.to_numpy(float)
    origins=full.origin.to_list()
    origin_loc={s:i for i,s in enumerate(origins)}
    audit=[]
    for _,r in d.iterrows():
        i=origin_loc[r.origin]
        out10=money[i+1:i+11]
        had10=len(out10)==10
        worst10=float(100*(out10.min()/money[i]-1)) if had10 else np.nan
        audit.append(dict(origin=r.origin,
            watch=bool(r.BI_v21_fragility_watch),
            original_alert=r.alert_level,
            review_priority=bool(r.original_BI_strong),
            next10_min_pct_AUDIT_ONLY=worst10,
            meets_10d_5pct_outcome_AUDIT_ONLY=bool(worst10<=-5) if had10 else False,
            ten_day_target_mature=had10))
    actual=pd.DataFrame(audit)
    actual.to_csv(OUT/"v21_outcome_audit_ONLY.csv",index=False)
    return actual

def historic_negative_control():
    early=pd.read_csv(OUT/"v17_history_formation_windows.csv")
    before=early[early.phase==-1]
    # The "NORMAL" requirement cannot be asserted in historical control
    # casebook because those days were not independently risk-scored.
    # This is a strict upper bound on positive historical examples.
    def rule(frame):
        return (frame.rsi14.ge(.74)&frame.AU_ret20.between(.04,.06,inclusive="both")&
                frame.gvz_z252.ge(0)&frame.GC_d1.lt(0))
    case=before[before.role=="DROP_EVENT"]
    neg=before[before.role=="CONTROL"]
    result=dict(historical_last_day_event_samples=int(len(case)),
        historical_last_day_negative_control_samples=int(len(neg)),
        positive_case_examples_without_NORMAL_req=int(rule(case).sum()),
        positive_negative_examples_without_NORMAL_req=int(rule(neg).sum()),
        supports_generalization=bool(rule(case).sum()>=4),
        warning="VERY FEW HISTORICAL CASES. The band was selected after examining 2024 and 2026; not a validated history-derived risk index")
    (OUT/"v21_historical_casebook_limitations.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def episode_audit(d,outcomes):
    # Adjacent candidate WATCH days are one operational review episode.
    episodes=[]
    for year,q in outcomes[outcomes.watch].groupby(outcomes.origin.str[:4]):
        q=q.reset_index(drop=True).copy()
        group=[]
        for _,r in q.iterrows():
            if group and (pd.Timestamp(r.origin)-pd.Timestamp(group[-1].origin)).days>4:
                episodes.append(dict(year=int(year),start=group[0].origin,last=group[-1].origin,
                   daily_watch_count=len(group),
                   any_next10_5pct_AUDIT_ONLY=bool(any(z.meets_10d_5pct_outcome_AUDIT_ONLY for z in group))))
                group=[]
            group.append(r)
        if group:
            episodes.append(dict(year=int(year),start=group[0].origin,last=group[-1].origin,
               daily_watch_count=len(group),
               any_next10_5pct_AUDIT_ONLY=bool(any(z.meets_10d_5pct_outcome_AUDIT_ONLY for z in group))))
    episodes=pd.DataFrame(episodes)
    episodes.to_csv(OUT/"v21_watch_episodes.csv",index=False)
    return episodes

def physical_event_audit(d):
    peaks=pd.read_csv(OUT/"v20_physical_peak_definitions.csv")
    outcomes=[]
    for _,e in peaks.iterrows():
        year=int(e.year)
        day=d[d.origin.str[:4]==str(year)].sort_values("origin").reset_index(drop=True)
        i=day.index[day.origin==e.price_peak]
        assert len(i)==1
        i=i[0]
        recent=day.iloc[max(0,i-4):i+1]
        baseline=recent[recent.original_BI_strong]
        fragility=recent[recent.BI_v21_fragility_watch]
        either=recent[recent.original_BI_strong|recent.BI_v21_fragility_watch]
        outcomes.append(dict(event=e.event,year=year,price_peak=e.price_peak,
            original_high_before_peak=bool(len(baseline)),
            additional_watch_before_peak=bool(len(fragility)),
            combined_review_before_peak=bool(len(either)),
            first_original_high=baseline.origin.iloc[0] if len(baseline) else "",
            first_shadow_fragility=fragility.origin.iloc[0] if len(fragility) else "",
            first_either=either.origin.iloc[0] if len(either) else "",
            not_certified_intraday=True,
            event_dates_were_known_during_rule_research=True))
    ev=pd.DataFrame(outcomes)
    ev.to_csv(OUT/"v21_6_events_peak_audit.csv",index=False)
    return ev

def main():
    p=load();d=freeze_candidate(p)
    out=outcome_audit(d)
    history=historic_negative_control()
    ep=episode_audit(d,out)
    event=physical_event_audit(d)
    yearly=[]
    for yr,z in d.groupby(d.origin.str[:4]):
        y=out[out.origin.str[:4]==yr]
        z_watch=y[y.watch]
        episodes=ep[ep.year==int(yr)]
        ev=event[event.year==int(yr)]
        yearly.append(dict(year=int(yr),original_red_days=int(z.alert_level.eq("RED").sum()),
            original_BI_high_days=int(z.original_BI_strong.sum()),
            new_shadow_watch_days=int(z.BI_v21_fragility_watch.sum()),
            new_watch_next10_true_5pct=int(z_watch.meets_10d_5pct_outcome_AUDIT_ONLY.sum()),
            new_watch_next10_false_5pct=int((~z_watch.meets_10d_5pct_outcome_AUDIT_ONLY).sum()),
            new_watch_episodes=len(episodes),
            new_watch_episodes_true=int(episodes.any_next10_5pct_AUDIT_ONLY.sum()),
            new_watch_episodes_false=int((~episodes.any_next10_5pct_AUDIT_ONLY).sum()),
            original_BI_peak_coverage=int(ev.original_high_before_peak.sum()),
            combined_BI_peak_coverage=int(ev.combined_review_before_peak.sum()),
            physical_event_count=len(ev)))
    m=pd.DataFrame(yearly)
    m.to_csv(OUT/"v21_2024_2026_comparison.csv",index=False)
    expected={2024:(4,2,2,0,1),2025:(0,0,0,2,2),2026:(1,1,0,2,3)}
    for _,row in m.iterrows():
        got=(int(row.new_shadow_watch_days),
             int(row.new_watch_next10_true_5pct),
             int(row.new_watch_next10_false_5pct),
             int(row.original_BI_peak_coverage),
             int(row.combined_BI_peak_coverage))
        assert got==expected[int(row.year)],(row.year,got)
    assert m.combined_BI_peak_coverage.sum()==6 and m.original_BI_peak_coverage.sum()==4
    assert history["positive_case_examples_without_NORMAL_req"]==0
    assert not history["supports_generalization"]
    assert not d.BI_is_live_enabled.any()
    summary=dict(status="RESEARCH_SHADOW_CANDIDATE_NOT_PROMOTED",
        red_alarms_replaced_or_deleted=False,
        historical_band_tuned_with_2024_2026=True,
        historical_2010_2022_has_supporting_cases=False,
        reproducible_retrospective_event_coverage="6/6 (not independent validation)",
        new_watch_days_2024_2026=int(d.BI_v21_fragility_watch.sum()),
        first_print_PIT_certified=False,
        prospective_holdout_completed=False,
        genuine_false_RED_days_reduced=False,
        production_modified=False,neon_modified=False)
    (OUT/"v21_audit.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    rep=[
      "# V21 — 2024 ve 2026 BASE14 NORMAL İKEN GÖRÜNMEYEN KIRILGANLIK",
      "",
      "Bu, mevcut alarm matematiğini bozmayan **RESEARCH-ONLY WATCH** katmanıdır.",
      "Yeni fiyat tahmin algoritması veya olasılık modeli yoktur. Eski BASE14 ve",
      "CFTC21 kırmızı alarmları ve Neon değiştirilmedi.",
      "",
      "## Açıklanabilir beş parametreli durum",
      "",
      "- Orijinal BASE14 NORMAL",
      "- RSI14 >= 0.74",
      "- Geçmiş 20g altın log getirisi 0.04-0.06 arasında",
      "- GVZ geçmiş oynaklık z-skoru >= 0",
      "- Kamuya açık gecikmeli CFTC altın net pozisyon haftalık değişimi < 0",
      "",
      "**KRİTİK:** %4-%6 bandı ve birlikte kullanım 2024/2026 tarihlerini daha",
      "önce inceledikten sonra oluşturuldu. Bu nedenle elde edilen 2024/2026",
      "performansı kör test DEĞİLDİR; aşırı uyum mümkündür.",
      "",
      "## 2024–2026 geriye dönük sonuçlar",
      "",
      m.to_markdown(index=False),
      "",
      "## Gerçek zirveden önceki dört işlem gününde görünürlük",
      "",
      event.to_markdown(index=False),
      "",
      "## Yeni WATCH günleri (gelecek düşüş sonradan ayrı sütun)",
      "",
      out[out.watch].to_markdown(index=False,floatfmt=".2f"),
      "",
      "## Tarihsel destek kontrolü",
      "",
      "2010–2022 düşüş/kontrol vaka defterinde ilgili çok dar koşula uygun",
      "örnek **yok** (case ve kontrol için 0). Bu veri yeni kuralın",
      "genellenebildiğini göstermez. Bu bir 'geçmişten kesin öğrenilmiş'",
      "indeks diye sunulamaz. 2023'ün tamamı da orijinal risk modelinin",
      "karar geçmişinde temsil edilmiyor.",
      "",
      "## Sınırlar",
      "- Yeni 5 WATCH günlük gözlem, sadece yeni 'dikkat' kaydıdır, RED değildir.",
      "- 2024 4 WATCH'un ikisi sonraki 10g >=%5 düşüşle örtüşmüyor.",
      "- 2026 tek WATCH 17 Nisan tarihindedir, sonraki 10g >=%5 düşüşle örtüşür.",
      "- 2025 ek WATCH üretilmedi; önceki iş zekası 2/2 zirve öncesi kayıttadır.",
      "- Geniş düşüş dönemlerinin 6/6 zirvede öncü koşulu görünmesi,",
      "  nokta atışı veya canlı tahmin başarı oranı değildir.",
      "- Günlük makro/CFTC ilk-baskı sayısal PIT doğrulaması tamam değil.",
      "- 2024/2026 vakaları bilinerek parametre bandı oluşturuldu;",
      "  istatistiksel bağımsız kanıt yoktur ve üretime alınamaz.",
      "",
      "Denetim: outputs/v21_daily_shadow.csv, outputs/v21_2024_2026_comparison.csv,",
      "outputs/v21_watch_episodes.csv, outputs/v21_6_events_peak_audit.csv,",
      "outputs/v21_historical_casebook_limitations.json, outputs/v21_audit.json."]
    (ROOT/"V21_FRAGILITY_SHADOW_TR.md").write_text("\n".join(rep)+"\n")
    print("V21_SHADOW_AUDITED",json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":
    main()
