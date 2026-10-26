#!/usr/bin/env python3
"""V22 research-only: slope, original anomaly cause and CFTC/GVZ phase.
ORIGINAL BASE14/CFTC21 RED unchanged. No new prediction model.
2024-2026 all inspected before rule chosen: NOT blind validation.
Future prices/targets used exclusively in audit, never decisions.
"""
from pathlib import Path
import numpy as np,pandas as pd,json
ROOT=Path(__file__).parent
OUT=ROOT/"outputs"

def read_original():
    a=pd.read_csv(OUT/"v19_2024_BI_signals.csv")
    a=a[a.model=="BASE14"][["origin","alert_level","risk_score","BI_high_attention","BI_reasons"]].rename(columns={"BI_high_attention":"strong","BI_reasons":"why"})
    b=pd.read_csv(OUT/"v18_daily_business_intelligence.csv")[["origin","alert_level","risk_score","BI_strong_attention","BI_reason_three_paths"]].rename(columns={"BI_strong_attention":"strong","BI_reason_three_paths":"why"})
    d=pd.concat([a,b],ignore_index=True)
    assert d.origin.is_unique
    return d

def calculate():
    source=pd.read_csv(OUT/"v19_asof_21_variable_panel.csv")
    original=read_original()
    watch=pd.read_csv(OUT/"v21_daily_shadow.csv")[["origin","BI_v21_fragility_watch"]]
    d=source.merge(original,on="origin",validate="one_to_one").merge(watch,on="origin",validate="one_to_one")
    d=d.sort_values("origin").reset_index(drop=True)
    assert len(d)==647 and d.origin.is_unique
    decisions=[]
    for yr,g in d.groupby(d.origin.str[:4],sort=True):
        g=g.reset_index(drop=True)
        for i,r in g.iterrows():
            prev=g.iloc[i-1] if i else None
            prior5=g.iloc[i-5] if i>=5 else None
            adjacent=prev is not None and 0<(pd.Timestamp(r.origin)-pd.Timestamp(prev.origin)).days<=4
            accel=(100*(r.AU_ret5-prior5.AU_ret5)) if prior5 is not None else np.nan
            day=(100*(r.price/prev.price-1)) if adjacent else np.nan
            red=r.alert_level=="RED";yellow=r.alert_level=="YELLOW";strong=bool(r.strong)
            reason=str(r.why)
            # Original V18/V19 RED stays available as low priority when
            # not selected: do NOT delete an operational model warning.
            P1=bool(red and strong and np.isfinite(accel) and accel>1)
            P2=bool(red and strong and ("CFTC_CONFIRMED_RISK_ACCELERATION" in reason or "CFTC_RISK_ACCEL" in reason))
            P3=bool(red and strong and np.isfinite(day) and day<=-1.5 and "GVZ" in reason)
            P4=bool(red and strong and r.gvz_level>=35 and r.rsi14>=.55)
            RED_CORE=P1 or P2 or P3 or P4
            # Only prior ORIGINAL RED + positive momentum qualifying P1-P4.
            # Cannot chain a previous RED_MEMORY into another RED_MEMORY.
            if i and adjacent:
                p=decisions[-1]
                prior_core=p["original_RED_core"]
                prior_positive=p["five_day_gold_pct"]>0
            else:prior_core=prior_positive=False
            P5=bool(red and strong and r.AU_ret5>0 and prior_core and prior_positive)
            P6=bool(yellow and strong)
            P7=bool(r.BI_v21_fragility_watch)
            if P7: assert r.alert_level=="NORMAL"
            selected=RED_CORE or P5 or P6 or P7
            if RED_CORE or P5:status="ACTIVE_REVIEW"
            elif P6:status="CONTINUATION_REVIEW"
            elif P7:status="FRAGILITY_WATCH"
            elif red:status="ORIGINAL_RED_REVIEW_ONLY"
            else:status="NO_ACTIONABLE_REVIEW"
            names=[v for k,v in [(P1,"MOMENTUM_ACCELERATES"),(P2,"CFTC_CONFIRM"),
                (P3,"GVZ_SHOCK"),(P4,"EXTREME_GVZ"),(P5,"ONE_DAY_RED_MEMORY"),
                (P6,"V18_ONE_DAY_YELLOW"),(P7,"V21_NORMAL_FRAGILITY")] if k]
            if r.AU_ret5<0:slope="DOWN_5DAY"
            elif not np.isfinite(accel):slope="UNKNOWN"
            elif accel>1:slope="UP_ACCELERATING"
            elif accel< -1:slope="UP_DECELERATING"
            else:slope="UP_STABLE"
            decisions.append(dict(origin=r.origin,year=int(yr),
                price=float(r.price),BASE14_original_alert_level=r.alert_level,
                BASE14_original_score=float(r.risk_score),
                previous_BI_strong=strong,
                five_day_gold_pct=float(100*r.AU_ret5),
                twenty_day_gold_pct=float(100*r.AU_ret20),
                five_day_acceleration_pp=accel,
                one_day_gold_pct=day,slope=slope,gvz=float(r.gvz_level),
                rsi14=float(r.rsi14),original_reason=reason,
                original_RED_core=RED_CORE,effective_review=selected,
                effective_level=status,effective_reasons="|".join(names),
                active_RED_phase=RED_CORE or P5,
                yellow_carry=P6,watch=P7,
                original_alert_changed=False,live_enabled=False,
                nonblind_stress=True,
                y5_AUDIT_ONLY=bool(r.y5_AUDIT_ONLY),
                y1_AUDIT_ONLY=bool(r.y1_AUDIT_ONLY)))
    o=pd.DataFrame(decisions)
    assert all(len(o[o.year==y])==n for y,n in [(2024,254),(2025,232),(2026,161)])
    assert not o.original_alert_changed.any() and not o.live_enabled.any()
    o.to_csv(OUT/"v22_daily_decisions.csv",index=False)
    return o

def audit(d):
    # V23 corrective audit: DO NOT count CFTC-eligible sparse decisions
    # as consecutive full trading sessions. Full price calendar is required.
    from risk_v23_calendar_safe_audit import build_daily
    daily, price_calendar = build_daily()
    assert daily.origin.tolist() == d.origin.tolist()
    assert len(price_calendar) == 713 and price_calendar.quarantined.sum() == 1
    daily.to_csv(OUT/"v22_daily_outcome_audit_ONLY.csv",index=False)
    rows=[]
    for yr,g in daily.groupby("year"):
        g=g.reset_index(drop=True);pos=g.y5_AUDIT_ONLY.to_numpy(bool);nextday=g.y1_AUDIT_ONLY.to_numpy(bool)
        segments=[];current=[]
        for i,x in enumerate(pos):
            if x:
                if current and i!=current[-1]+1:segments.append(current);current=[]
                current.append(i)
        if current:segments.append(current)
        for policy,mask in [("BASE14_ORIGINAL_RED",g.BASE14_original_alert_level.eq("RED").to_numpy(bool)),
                            ("V22_PRIORITIZED_REVIEW_PLUS_WATCH",g.effective_review.to_numpy(bool)),
                            ("V22_ACTIVE_RED_PHASE_ONLY",g.active_RED_phase.to_numpy(bool))]:
            mature=g.ten_day_mature.to_numpy(bool)
            true10=g.next10_min_pct_AUDIT_ONLY.to_numpy(float)<=-5
            rows.append(dict(year=int(yr),policy=policy,eligible_origins=len(g),
                flagged_days=int(mask.sum()),false5_days=int((mask&~pos).sum()),
                true5_days=int((mask&pos).sum()),
                nextday3_hit=int((mask&nextday).sum()),
                nextday3_total=int(nextday.sum()),
                five_day_clusters_hit=int(sum(mask[a].any() for a in segments)),
                five_day_clusters_total=len(segments),
                mature10_flagged=int((mask&mature).sum()),
                true10_days=int((mask&mature&true10).sum()),
                false10_days=int((mask&mature&~true10).sum()),
                unknown10_days=int((mask&~mature).sum())))
    m=pd.DataFrame(rows)
    m.to_csv(OUT/"v22_three_year_metrics.csv",index=False)
    physical=pd.read_csv(OUT/"v20_physical_peak_definitions.csv")
    events=[]
    for _,row in physical.iterrows():
        x=d[d.year==int(row.year)].sort_values("origin").reset_index(drop=True)
        i=x.index[x.origin==row.price_peak]
        assert len(i)==1
        window=x.iloc[max(0,int(i[0])-4):int(i[0])+1]
        active=window[window.effective_review]
        events.append(dict(event=row.event,year=int(row.year),peak=row.price_peak,
          original_RED_last5=int(window.BASE14_original_alert_level.eq("RED").sum()),
          V22_active_before_or_on_peak=bool(len(active)),
          first_V22_attention_last5=active.origin.iloc[0] if len(active) else "",
          hypothesis_was_not_blind=True))
    ev=pd.DataFrame(events)
    ev.to_csv(OUT/"v22_physical_early_warning.csv",index=False)
    return m,ev

def main():
    o=calculate()
    m,ev=audit(o)
    expected={
     (2024,"BASE14_ORIGINAL_RED"):(18,18,0,0),
     (2024,"V22_PRIORITIZED_REVIEW_PLUS_WATCH"):(12,12,0,0),
     (2025,"BASE14_ORIGINAL_RED"):(32,27,5,2),
     (2025,"V22_PRIORITIZED_REVIEW_PLUS_WATCH"):(20,15,5,3),
     (2026,"BASE14_ORIGINAL_RED"):(50,40,10,4),
     (2026,"V22_PRIORITIZED_REVIEW_PLUS_WATCH"):(32,22,10,4)}
    print("V22_ALL_HISTORICAL_METRICS\n",m.to_string(index=False))
    for key,exp in expected.items():
        r=m[(m.year==key[0])&(m.policy==key[1])].iloc[0]
        got=(int(r.flagged_days),int(r.false5_days),int(r.true5_days),int(r.nextday3_hit))
        assert got==exp,(key,got,exp)
    assert len(ev)==6 and ev.V22_active_before_or_on_peak.all()
    assert ev[ev.event=="2024_11"].first_V22_attention_last5.iloc[0]=="2024-10-30"
    assert ev[ev.event=="2026_MAY_JUNE"].first_V22_attention_last5.iloc[0]=="2026-04-17"
    limitation={"candidate":"V22_SLOPE_ORIGINAL_RISK_TRIAGE",
       "original_red_changed":False,"production_promoted":False,
       "2026_blind_validation":False,"2024_and_2026_events_known_during_design":True,
       "2025_hypotheses_explored":True,"full_numeric_PIT_certified":False,
       "10_day_outcomes_not_in_decision":True,
       "the_22_2026_false5_are_PRIORITIZED_days_not_live_original_RED":True,
       "ten_day_uses_full_price_calendar":True,
       "bad_2026_02_27_future_windows_censored":True,
       "late_2026_october_prices_included_for_september_horizon":True,
       "false5_is_days_not_independent_false_economic_events":True,
       "V21_historical_old_casebook_did_not_support_this_narrow_band":True}
    (OUT/"v22_audit_limits.json").write_text(json.dumps(limitation,indent=2)+"\n")
    table=m[["year","policy","flagged_days","false5_days","true5_days","nextday3_hit","nextday3_total","five_day_clusters_hit","five_day_clusters_total","mature10_flagged","true10_days","false10_days","unknown10_days"]].to_markdown(index=False)
    report=["# V22: ORİJİNAL BASE14/CFTC21 + EĞİM TEMELLİ KARAR ÖNCELİĞİ",
      "", "**SONUÇ: Araştırma amaçlı öncelik filtresi. Canlı kırmızı alarm",
      "silinmedi, Neon/üretim uygulaması değişmedi.**",
      "",table,"","## Gerçek zirve öncesi beş skorlanabilir işlem günü","",
      ev.to_markdown(index=False),
      "","## Yöntem: Gözlenmiş veri ve ekonomik aşamalar",
      "- Orijinal V18/V19 güçlü RED, 5g momentumun beş seans önceye göre >1 yüzde puanı hızlanması",
      "- Orijinal risk skorunda CFTC21 doğrulanmış ivmelenen anormallik",
      "- Orijinal GVZ kaynaklı RED, son günün kapanışında >=%1,5 değer kaybı",
      "- Orijinal güçlü RED, GVZ>=35 ve RSI>=0,55",
      "- Önceki asıl RED çekirdeğinden bir günlük pozitif momentum RED devamı",
      "- V18 güçlü YELLOW'un tek oturumluk devamı",
      "- V21 BASE14 NORMAL kırılganlık WATCH ayrı, kırmızı yerine geçmez",
      "","## Yöntem sınırları ve geliştirme kararı",
      "- Eşikler 2024–2026 vakaları görüldükten sonra araştırıldı: sonuç kör OOS değil.",
      "- 2024/2025/2026 günlük sonuçları az sayıda bağımsız düşüş içerir.",
      "- 2010–22 dar V21 kuralını destekleyen yeterli bağımsız örnek yok.",
      "- 27 Şubat 2026 bozuk fiyatı karantinada; etkilenen gelecek 10g sonuçlar UNKNOWN.",
      "- Sözde yanlış alarm sayısı 40->22 yalnız önceliklendirilen gün sayısıdır;",
      "  BASE14 asli 50 kırmızı ve 40 false5 günü değişmedi.",
      "- Olay bazlı öncü zirve inceleme ayrı, 5-gün ve 10-gün sonuçlar ayrı.",
      "- Bu başlıktaki RED bir yatırım AL/SAT emri değildir.",
      "- İlk yayın makro/CFTC sayısal vintage sertifikası eksik.",
      "- Canlıya geçmek için yeni bağımsız dönem, olay sayısı ve dönem genişliği gerekir.",
      "","Dosyalar: outputs/v22_daily_decisions.csv,",
      "outputs/v22_daily_outcome_audit_ONLY.csv,",
      "outputs/v22_three_year_metrics.csv,",
      "outputs/v22_physical_early_warning.csv, outputs/v22_audit_limits.json."]
    (ROOT/"V22_SLOPE_DECISION_RESULTS_TR.md").write_text("\n".join(report)+"\n")
    print("V22_EVALUATED",json.dumps(limitation))
if __name__=="__main__":main()
