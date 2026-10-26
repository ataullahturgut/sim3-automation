#!/usr/bin/env python3
"""No forecast. Rule on existing BASE14/CFTC21 IsolationForest RED.
Never remove/redesign the RED signal. Historical closest analogue <=2022.
All future outcomes are retrospective AUDIT_ONLY, not rule features.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
R=Path(__file__).parent
O=R/"outputs"
O.mkdir(exist_ok=True)

def decisions():
    orig=pd.read_csv(O/"v15_daily_intelligence.csv")
    prior=pd.read_csv(O/"v15_historical_parameter_analogues.csv")
    assert (prior.nearest_historic_crash_date.str[:4].astype(int)<=2022).all()
    assert (prior.nearest_historic_no_crash_date.str[:4].astype(int)<=2022).all()
    t=orig.merge(prior[["origin","model","nearest_historic_crash_date",
       "nearest_historic_no_crash_date","nearest_crash_parameter_distance",
       "nearest_control_parameter_distance"]],on=["origin","model"],
       how="left",validate="one_to_one")
    red=t.alert_level.eq("RED")
    gvz=t.strongest_whatif_group.eq("GVZ")
    analogue=(t.nearest_crash_parameter_distance<
                t.nearest_control_parameter_distance).fillna(False)
    confirm=red&(gvz|analogue)
    t["original_red_unchanged"]=red
    t["BI_gvz_dominant"]=gvz
    t["BI_crash_analogue_closer"]=analogue
    t["BI_priority"]=np.select([confirm,red],
       ["BI_CONFIRMED","BI_REVIEW"],default="NOT_RED")
    t["BI_reason"]=np.select(
        [confirm&gvz&analogue,confirm&gvz,confirm&analogue,red],
        ["GVZ_AND_CASEBOOK","GVZ_DOMINATES","HISTORICAL_CASEBOOK",
         "REVIEW_OTHER_DRIVER"],default="NOT_RED")
    t["BI_changes_original_alarm"]=False
    t["BI_probability_of_decline"]=np.nan
    t["strict_first_print_PIT_verified"]=False
    t.to_csv(O/"v16_bi_daily.csv",index=False)
    return t

def compute(d):
    stats=[]
    for (model,year),g in d.groupby(["model",d.origin.str[:4]]):
        g=g.sort_values("origin").reset_index(drop=True)
        pos=g.future_drop5_AUDIT_ONLY.to_numpy(bool)
        y1=g.future_nextday_pct_AUDIT_ONLY.to_numpy(float)<=-3
        groups=[];group=[]
        for i,p in enumerate(pos):
            if not p:continue
            if group and i!=group[-1]+1:groups.append(group);group=[]
            group.append(i)
        if group:groups.append(group)
        for label,mask in [
            ("ORIGINAL_RED",g.original_red_unchanged.to_numpy(bool)),
            ("BI_CONFIRMED",g.BI_priority.eq("BI_CONFIRMED").to_numpy(bool))]:
            stats.append(dict(year=int(year),model=model,layer=label,
              scored_days=len(g),flag_days=int(mask.sum()),
              hit_nextday3=int((mask&y1).sum()),total_nextday3=int(y1.sum()),
              hit_5d_origin=int((mask&pos).sum()),
              total_5d_origins=int(pos.sum()),
              group_hit=sum(bool(mask[z].any()) for z in groups),
              groups=len(groups),
              false_5d_days=int((mask&~pos).sum())))
    q=pd.DataFrame(stats)
    q.to_csv(O/"v16_bi_metrics.csv",index=False)
    return q

def timeline(d):
    old=pd.read_csv(O/"event_alarm_timeline.csv")
    old=old[(old.period==2026)&old.model.isin(["BASE14","CFTC21"])]
    result=[]
    for _,e in old.iterrows():
        g=d[(d.model==e.model)&(d.origin.str[:4]=="2026")].sort_values("origin")
        before=g[g.origin<e.onset_proxy].tail(10)
        date=before.loc[before.BI_priority.eq("BI_CONFIRMED"),"origin"]
        first=date.iloc[0] if len(date) else None
        status=("NOT_EVALUABLE_QUARANTINE" if e.timing=="NOT_EVALUABLE_QUARANTINE"
                 else "BEFORE_ONSET_DAILY_PROXY" if first
                 else "ONSET_CLOSE_NOT_EARLY" if
                     bool((g.origin.eq(e.onset_proxy)&g.BI_priority.eq("BI_CONFIRMED")).any())
                 else "NO_EARLY_CONFIRMATION")
        result.append(dict(event_id=e.event_id,model=e.model,
          onset_proxy=e.onset_proxy,previous_first_original_red=e.first_alarm,
          first_BI_confirmed_before_onset=first or "",
          status=status,daily_onset_is_intraday_verified=False))
    t=pd.DataFrame(result)
    t.to_csv(O/"v16_bi_event_timeline.csv",index=False)
    return t

def main():
    d=decisions()
    s=compute(d)
    t=timeline(d)
    assert len(d)==786
    get=lambda year,model,layer:s[(s.year==year)&(s.model==model)&(s.layer==layer)].iloc[0]
    a=get(2025,"BASE14","ORIGINAL_RED")
    b=get(2025,"BASE14","BI_CONFIRMED")
    c=get(2026,"BASE14","ORIGINAL_RED")
    e=get(2026,"BASE14","BI_CONFIRMED")
    assert (a.flag_days,a.false_5d_days,a.group_hit,a.hit_nextday3)==(32,27,3,2)
    assert (b.flag_days,b.false_5d_days,b.group_hit,b.hit_nextday3)==(28,23,3,2)
    assert (c.flag_days,c.false_5d_days,c.group_hit,c.hit_nextday3)==(50,40,4,4)
    assert (e.flag_days,e.false_5d_days,e.group_hit,e.hit_nextday3)==(28,19,4,3)
    assert not d.BI_changes_original_alarm.any()
    overview={"stage":"RETROSPECTIVE_RESEARCH_REVIEW_ONLY",
      "predictor_trained":False,"red_levels_changed":False,
      "uses_future_outcome_as_input":False,
      "2026_is_blind_test":False,"first_print_verified":False,
      "rule":"Existing RED and (GVZ dominant or closer to historic drop than no-drop control)",
      "total_scored_records":len(d),
      "original_red_records":int(d.original_red_unchanged.sum()),
      "confirmed_red_records":int(d.BI_priority.eq("BI_CONFIRMED").sum())}
    (O/"v16_bi_audit.json").write_text(json.dumps(overview,indent=2)+"\n")
    lines=[
     "# V16 — 2026 gerçek iş zekâsı karşılaştırması",
     "",
     "Bu bir altın fiyatı/düşüş tahmin modeli değil. Orijinal RED korunur.",
     "GVZ göstergesi IsolationForest skorunda en baskın gruptaysa veya",
     "mevcut 14/21 parametrelerin 2010–2022 bilinen büyük düşüş örneğine",
     "uzaklığı, aynı parametrelerle düşüşsüz kontrole uzaklığından küçükse",
     "mevcut kırmızı ek olarak BI güçlü teyit olarak işaretlenir.",
     "Aksi halde kırmızı alarm silinmez; sadece gözden geçirilmeli etiketi alır.",
     "",
     "| Yıl | BASE14 alarm sınıfı | Gün | 5g %5 risk kümesi | Ertesi gün %3 hit | 5g hedefe göre yanlış gün |",
     "|---|---|---:|---:|---:|---:|",
    ]
    for year in (2025,2026):
        for layer in ("ORIGINAL_RED","BI_CONFIRMED"):
            row=get(year,"BASE14",layer)
            lines.append(f"| {year} | {layer} | {row.flag_days} | {row.group_hit}/{row.groups} | {row.hit_nextday3}/{row.total_nextday3} | {row.false_5d_days} |")
    lines += [
     "",
     "**2026 BASE14:** BI güçlü teyitte 28 gün/19 yanlış gün ve 4/4 risk kümesi;",
     "ancak ertesi gün %3 düşüşlerin yalnız 3/4 günü güçlü teyit.",
     "Özgün BASE14 50 alarm / 40 yanlış / 4/4; hiçbir RED kaldırılmadı.",
     "Erken alarm 5g penceresinin dışında kaldığında günlük yanlış alarm",
     "sayılabilir; bu sayı bağımsız kriz-öncesi erkenlik başarısı değildir.",
     "",
     "## Kanıt ve sınırlar",
     "- v16_bi_daily.csv: karar günü, orijinal skor/alarm, parametre sebebi,",
     "  geçmiş vaka/control yakınlığı ve BI ek etiketi.",
     "- v16_bi_metrics.csv: 2025 ve 2026 karşılaştırma.",
     "- v16_bi_event_timeline.csv: olayın başlamasından önce ek teyit.",
     "- v16_bi_audit.json: değişmeyen alarm ve no-forecast kontrolleri.",
     "",
     "2026 sonuçları daha önce araştırmacı tarafından görülmüştür;",
     "**BU KÖR BİR BAŞARI TESTİ DEĞİLDİR.** Başarılı görünmesi",
     "üretim modeline alınmasını kanıtlamaz. 2025 sadece üç 5g risk kümesi",
     "içeriyor ve kaynak ilk yayın numerik vintage tam sertifikalı değil.",
     "Neon ve gerçek alarm uygulaması değiştirilmedi.",
    ]
    (R/"V16_BI_2026_REPORT_TR.md").write_text("\n".join(lines)+"\n")
    print("V16_BI_ANALYSIS_EXECUTED",json.dumps(overview))

if __name__=="__main__":
    main()
