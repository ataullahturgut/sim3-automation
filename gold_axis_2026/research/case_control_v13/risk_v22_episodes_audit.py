#!/usr/bin/env python3
"""V22 separate true/false review DAYS from contiguous alert EPISODES.

Important: an episode is not an independent economic shock. Daily targets
are evaluated over future 10 scored sessions *only after the episode occurs*.
An episode is counted as verified TRUE if at least one in-episode alert day
has a mature >=5% upcoming fall in its next 10 scored sessions.
Censor unverifiable future outcomes instead of calling them false.
Original production BASE14 alerts remain unchanged.

Calendar gaps >4 days start a new alarm episode; sensitivity to >=6d
tested separately because this choice is arbitrary (weekend/holidays).
"""
from pathlib import Path
import json,pandas as pd,numpy as np
O=Path(__file__).parent/"outputs"
P={"BASE14_ORIGINAL_RED":lambda x:x.BASE14_original_alert_level.eq("RED"),
   "V22_ACTIVE_RED_ONLY":lambda x:x.active_RED_phase.astype(bool),
   "V22_ACTIVE_AND_YELLOW":lambda x:(x.active_RED_phase|x.yellow_carry),
   "V22_PRIORITIZED_PLUS_WATCH":lambda x:x.effective_review.astype(bool),
   "V22_WATCH_ONLY":lambda x:x.watch.astype(bool)}
def compute(gap):
    d=pd.read_csv(O/"v22_daily_outcome_audit_ONLY.csv").sort_values("origin")
    ep=[];metrics=[]
    for (yr),full in d.groupby("year"):
        for policy,fn in P.items():
            selected=full.loc[fn(full)].sort_values("origin").reset_index(drop=True)
            groups=[];group=[]
            for _,x in selected.iterrows():
                if group and (pd.Timestamp(x.origin)-pd.Timestamp(group[-1].origin)).days>gap:
                    groups.append(group);group=[]
                group.append(x)
            if group:groups.append(group)
            for group in groups:
                s=pd.DataFrame(group)
                mature=s[s.ten_day_mature]
                ever=bool((mature.next10_min_pct_AUDIT_ONLY<=-5).any())
                can_assess=len(mature)>0
                ep.append(dict(year=int(yr),policy=policy,gap_days=gap,
                   first=group[0].origin,last=group[-1].origin,days=len(group),
                   has_full_ten_day_label=can_assess,
                   ten_day_true_event=ever if can_assess else False,
                   ten_day_false_event=(not ever) if can_assess else False,
                   five_day_target_any=bool(s.y5_AUDIT_ONLY.any()),
                   never_inferred_intraday=True))
            subset=[x for x in ep if x["year"]==int(yr) and x["policy"]==policy and x["gap_days"]==gap]
            metrics.append(dict(year=int(yr),policy=policy,gap_days=gap,
                episodes_total=len(subset),episodes_mature=sum(x["has_full_ten_day_label"] for x in subset),
                episodes_true10=sum(x["ten_day_true_event"] for x in subset),
                episodes_false10=sum(x["ten_day_false_event"] for x in subset),
                episodes_unknown10=sum(not x["has_full_ten_day_label"] for x in subset),
                episodes_any5=sum(x["five_day_target_any"] for x in subset)))
    return pd.DataFrame(ep),pd.DataFrame(metrics)

def main():
    out=[];events=[]
    for gap in [4,6,10]:
        e,m=compute(gap)
        events.append(e);out.append(m)
    ev=pd.concat(events,ignore_index=True)
    m=pd.concat(out,ignore_index=True)
    ev.to_csv(O/"v22_alarm_episodes.csv",index=False)
    m.to_csv(O/"v22_episode_sensitivity.csv",index=False)
    q=m[m.gap_days==4].set_index(["year","policy"])
    exp={
     (2024,"BASE14_ORIGINAL_RED"):(4,0,4,0),
     (2024,"V22_ACTIVE_RED_ONLY"):(4,0,4,0),
     (2024,"V22_PRIORITIZED_PLUS_WATCH"):(8,1,7,0),
     (2025,"BASE14_ORIGINAL_RED"):(7,3,4,0),
     (2025,"V22_ACTIVE_RED_ONLY"):(4,3,1,0),
     (2025,"V22_PRIORITIZED_PLUS_WATCH"):(5,3,2,0),
     (2026,"BASE14_ORIGINAL_RED"):(8,4,3,1),
     (2026,"V22_ACTIVE_RED_ONLY"):(8,6,2,0),
     (2026,"V22_PRIORITIZED_PLUS_WATCH"):(9,7,2,0)}
    for k,w in exp.items():
        v=q.loc[k]
        got=(int(v.episodes_total),int(v.episodes_true10),
             int(v.episodes_false10),int(v.episodes_unknown10))
        assert got==w,(k,got,w)
    assert (m.episodes_total==m.episodes_true10+m.episodes_false10+m.episodes_unknown10).all()
    warning={"episode_gap_not_independent_economic_events":True,
         "retrospective_not_blind":True,
         "original_red_unchanged":True,
         "2024_composite_review_episodes_increased_due_to_nonred_watches":True,
         "2026_last_original_red_early_sep_no_ten_day_maturity":True,
         "price_fall_target_only_post_hoc":True}
    (O/"v22_episode_caveat.json").write_text(json.dumps(warning,ensure_ascii=False,indent=2)+"\n")
    report=[
      "# V22 BAĞIMSIZ OLMAYAN ALARM EPİZOTLARI DENETİMİ",
      "","Kırmızı alarm GÜNLERİ ile ardışık ALARM EPİZOTLARI",
      "aynı başarı ölçütü değildir. Eski 2026 RED 50 gün; işlem günleri",
      "dört takvim günü boşluk aşmadıkça aynı alarm epizodu sayılıyor.",
      "Çakışan 10-gün etiketleri bağımsız piyasa krizi gibi sayılmaz.",
      "",q.reset_index()[["year","policy","episodes_total","episodes_true10","episodes_false10","episodes_unknown10"]].to_markdown(index=False),
      "",
      "## Düşüş etiketi ve sansür",
      "Gelecek 10 işlem günü boyunca altının aynı uyarı kapanışına göre",
      "en az %5 aşağı işlem günü kapanışı varsa geriye dönük TRUE.",
      "Dönem sonundan ötürü gelecek 10 işlem günü görünmüyorsa UNKNOWN.",
      "Epizot TRUE ise en az bir uyarı günü olgun TRUE; bu baştan",
      "tahminin gerçekleştiğini kanıtlamaz.",
      "",
      "## Neden yalnız yanlış uyarı günlerini azaltmak yetmez?",
      "- 2024: Eski 4 RED epizodu da sonradan düşüşle eşleşmez;",
      "  V22 ACTIVE_RED 4 benzer false epizod; başarı ilerlemesi YOK.",
      "- 2024: V22 FRAGILITY_WATCH da alarm sayılırsa kompozit 8 epizot",
      "  üretir, sadece biri (30 Ekim) düşüşle örtüşür. Bunu saklama.",
      "- 2025: Eski 7 epizot, 4 false; ACTIVE_RED 4 epizot, 1 false.",
      "- 2026: Eski 8 epizot, 3 false, 1 gelecek 10g yetersiz;",
      "  ACTIVE_RED 8 epizot, 2 false, 0 yetersiz.",
      "- Dört takvim günü epizot ayrımı sabit ve keyfi, 6 ve 10 gün",
      "  sonuçları outputs/v22_episode_sensitivity.csv içinde.",
      "- 2024 WATCH ve 2026 WATCH canli al/sat tetikleyici degildir.",
      "- İlk-baskı makro veri PIT tam doğrulanmadı; olaylar biliniyordu.",
      "",
      "Dosyalar: outputs/v22_alarm_episodes.csv, outputs/v22_episode_sensitivity.csv,",
      "outputs/v22_episode_caveat.json."]
    (Path(__file__).parent/"V22_ALARM_EPISODE_AUDIT_TR.md").write_text("\n".join(report)+"\n")
    print("V22_EPISODES_OK",json.dumps(warning))
if __name__=="__main__":main()
