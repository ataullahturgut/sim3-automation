"""DENEYİM v1.2: 2020-2022 ısıtmalı maraton (karar kuralı C1, değişmedi). Raporları yazar ve modeli dondurur.
Kullanım: python3 run_v1_2.py
"""
import os, json, math, tempfile
from collections import OrderedDict
from datetime import date
import numpy as np
import deneyim_states as S
import deneyim_v1 as D

HERE = os.path.dirname(os.path.abspath(__file__))


def mdd(v):
    pk, m = -1e18, 0.0
    for x in v: pk = max(pk, x); m = max(m, 100 * (1 - x / pk))
    return m


def summarize(R):
    rows, nh = R["rows"], R["nav_hist"]
    nav = lambda d: [v for (i, v, _) in nh if rows[i]["date"] <= d][-1]
    return OrderedDict(nav_2023=round(nav(date(2023, 12, 31)), 2), nav_2024=round(nav(date(2024, 12, 31)), 2),
                       nav_final=round(nh[-1][1], 2), maxdd=round(mdd([v for (_, v, _) in nh]), 2),
                       trades=len(R["trades"]), trade_list=R["trades"])


def main():
    cold = D.marathon(tempfile.mkdtemp(), mode="C1", warmup=False)
    R = D.marathon(HERE, mode="C1", report_dir="reports_v1_2", warmup=True)
    rows, Z, model, i0, m0 = R["rows"], R["Z"], R["model"], R["i_start"], R["m0"]
    first = rows[i0]
    passive = [100 * (1 - S.FEE) ** 2 * rows[i]["bid"] / first["ask"] for (i, _, _) in R["nav_hist"]]
    P = [r["p06"] for r in rows]; c, u, ps, tn = 100.0, 0.0, 0, []
    for (i, _, _) in R["nav_hist"]:
        r = rows[i]; sma = sum(P[i - 99:i + 1]) / 100
        if ps == 0 and P[i] > 1.01 * sma: u = c * (1 - S.FEE) / r["ask"]; c = 0; ps = 1
        elif ps == 1 and P[i] < 0.99 * sma: c = u * r["bid"] * (1 - S.FEE); u = 0; ps = 0
        tn.append(c + u * r["bid"] * (1 - S.FEE))
    opos, olog = R["oracle_final"]
    jan = [i for (i, _, _) in R["nav_hist"] if str(rows[i]["date"])[:7] == "2023-01"]
    jan_est = [R["est"][i] for i in jan if R["est"].get(i)]
    frozen = OrderedDict(
        model="DENEYIM_V1_2", decision_layer="C1", warmup="2020-01-02..2022-12-30", frozen_at_month="2025-12",
        features=S.FEATURES, standardizer=R["std"].state(),
        memory_X=Z[m0:len(rows)].round(6).tolist(), memory_Y=list(map(int, opos)),
        outcome_X=model.outX.round(6).tolist(), outcome_r=model.outR.round(6).tolist(), outcome_d=model.outD.tolist(),
        metric_weights=model.w.round(6).tolist(), bandwidth=model.h, logistic_beta=model.beta.round(6).tolist(),
        alpha_analog=model.alpha, th_in=model.th[0], th_out=model.th[1], H_out=D.H_OUT, c_rt=D.C_RT, fee=S.FEE,
        out_prior_w=D.OUT_PRIOR_W, prior=dict(weight=D.PRIOR_W, p=D.PRIOR_P), ridge=D.RIDGE,
        buy_threshold_pct=D.C_RT / 2, sell_threshold_pct=-D.C_RT / 2,
        note="2026 testi bu dosyayla, kod değiştirilmeden yapılır. 2026 verisi yüklenmedi.")
    json.dump(frozen, open(os.path.join(HERE, "DENEYIM_V1_2_DONDURULMUS_MODEL.json"), "w"), ensure_ascii=False)
    out = OrderedDict(
        v1_1_cold=summarize(cold), v1_2_warm=summarize(R),
        warmup_days=i0, memory_days_total=len(rows) - m0,
        january_2023=dict(est_min=round(min(e[0] for e in jan_est), 3), est_max=round(max(e[0] for e in jan_est), 3),
                          buy_threshold=round(D.C_RT / 2, 3), traded=any(str(t["date"])[:7] == "2023-01" for t in R["trades"])),
        benchmarks=dict(passive_final=round(passive[-1], 2), passive_maxdd=round(mdd(passive), 2),
                        trend_final=round(tn[-1], 2), ideal_final=round(100 * math.exp(olog), 2)),
        honesty=["Isıtma yalnız 2020-01-02..2022-12-30 verisini kullanır; 2023+ bilgisi sızmaz.",
                 "Karar kuralı C1 değişmedi; ısıtma bir kurulum düzeltmesidir, performansa göre seçim değildir.",
                 "Geliştirme dönemi sonucudur; 2026 testi ayrıdır."])
    json.dump(out, open(os.path.join(HERE, "DENEYIM_V1_2_SONUC.json"), "w"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps({k: (v if k not in ("v1_1_cold", "v1_2_warm") else {a: b for a, b in v.items() if a != "trade_list"})
                      for k, v in out.items()}, indent=1, ensure_ascii=False, default=str))
    print("v1.2 işlemler:", [(t["date"], t["action"], round(t["price"], 2), t["Er"]) for t in R["trades"]])


if __name__ == "__main__":
    main()
