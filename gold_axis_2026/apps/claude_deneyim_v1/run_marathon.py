"""DENEYİM v1 maratonunu koşar, aylık raporları yazar, 36 ayı birleştirip nihai algoritmayı dondurur.
Kullanım: python3 run_marathon.py
"""
import os, json, math, csv
from collections import OrderedDict
import numpy as np
import deneyim_states as S
import deneyim_v1 as D

HERE = os.path.dirname(os.path.abspath(__file__))


def max_dd(v):
    pk, m = -1e18, 0.0
    for x in v:
        pk = max(pk, x); m = max(m, 100 * (1 - x / pk))
    return m


def main():
    R = D.marathon(HERE)
    rows, Z, model, i0 = R["rows"], R["Z"], R["model"], R["i_start"]
    idx = [i for (i, _, _) in R["nav_hist"]]
    nav = [v for (_, v, _) in R["nav_hist"]]
    first, last = rows[idx[0]], rows[idx[-1]]
    passive = [100 * (1 - S.FEE) ** 2 * rows[i]["bid"] / first["ask"] for i in idx]
    # trend kıyası: SMA100 ±%1, aynı yürütme
    P = [r["p06"] for r in rows]; c, u, pos, tn = 100.0, 0.0, 0, []
    for i in idx:
        r = rows[i]; sma = sum(P[i - 99:i + 1]) / 100
        if pos == 0 and P[i] > 1.01 * sma: u = c * (1 - S.FEE) / r["ask"]; c = 0; pos = 1
        elif pos == 1 and P[i] < 0.99 * sma: c = u * r["bid"] * (1 - S.FEE); u = 0; pos = 0
        tn.append(c + u * r["bid"] * (1 - S.FEE))
    opos, olog = R["oracle_final"]
    legs = R["legs_final"]
    reps = R["reports"]
    # öğrenme gelişimi: yıllara göre yanlış gün payı ve yakalama
    by_year = OrderedDict()
    for rp in reps:
        y = rp["month"][:4]; by_year.setdefault(y, []).append(rp)
    evol = OrderedDict((y, dict(wrong_day_share=round(float(np.mean([x["errors"]["wrong_day_share"] for x in v])), 3),
                                model_ret_pct=round(100 * (np.prod([1 + x["model"]["month_ret_pct"] / 100 for x in v]) - 1), 2),
                                gold_change_pct=round(100 * (np.prod([1 + x["gold"]["change_pct"] / 100 for x in v]) - 1), 2),
                                trades=sum(len(x["model"]["trades"]) for x in v))) for y, v in by_year.items())
    # mekanizma sentezi: ideal girişlerden/çıkışlardan önceki tipik durum (36 ay birleşik)
    Y = np.array(opos); X = Z[i0:idx[-1] + 1]
    entries = [L["entry_i"] - i0 for L in legs]; exits = [L["exit_i"] - i0 for L in legs if L["exit_i"] is not None]
    def profile(ix):
        if not ix: return []
        m = X[ix].mean(0)
        return [(S.LABEL_TR[S.FEATURES[j]], round(float(m[j]), 2)) for j in np.argsort(-np.abs(m))[:8]]
    gold_vs_cash = (X[Y == 1].mean(0) - X[Y == 0].mean(0))
    beta = model.beta[1:]
    frozen = OrderedDict(
        model="DENEYIM_V1", frozen_at_month="2025-12", features=S.FEATURES,
        standardizer=R["std"].state(), memory_X=X.round(6).tolist(), memory_Y=Y.tolist(),
        metric_weights=model.w.round(6).tolist(), bandwidth=model.h, logistic_beta=model.beta.round(6).tolist(),
        alpha_analog=model.alpha, th_in=model.th[0], th_out=model.th[1], fee=S.FEE,
        prior=dict(weight=D.PRIOR_W, p=D.PRIOR_P), ridge=D.RIDGE,
        note="2026 testi bu dosyadaki parametrelerle, kod değiştirilmeden yapılır. 2026 verisi bu dosya üretilirken yüklenmedi.")
    json.dump(frozen, open(os.path.join(HERE, "DENEYIM_V1_DONDURULMUS_MODEL.json"), "w"), ensure_ascii=False)
    summary = OrderedDict(
        period=[first["date"].isoformat(), last["date"].isoformat()], trading_days=len(idx),
        model=dict(final_nav=round(nav[-1], 4), maxdd=round(max_dd(nav), 2), trades=len(R["trades"]), trade_list=R["trades"]),
        passive=dict(final_nav=round(passive[-1], 4), maxdd=round(max_dd(passive), 2)),
        trend_sma100=dict(final_nav=round(tn[-1], 4), maxdd=round(max_dd(tn), 2)),
        ideal_oracle=dict(final_nav=round(100 * math.exp(olog) * first["ask"] / first["ask"], 4), legs=len(legs),
                          gold_days_share=round(float(Y.mean()), 3)),
        learning_by_year=evol,
        mechanism=dict(state_before_ideal_entries=profile(entries), state_before_ideal_exits=profile(exits),
                       ideal_gold_minus_cash=[(S.LABEL_TR[S.FEATURES[j]], round(float(gold_vs_cash[j]), 2)) for j in np.argsort(-np.abs(gold_vs_cash))[:10]],
                       final_group_weights=reps[-1]["learning_after_month"]["group_weights"],
                       logistic_positive=[(S.LABEL_TR[S.FEATURES[j]], round(float(beta[j]), 3)) for j in np.argsort(-beta)[:6]],
                       logistic_negative=[(S.LABEL_TR[S.FEATURES[j]], round(float(beta[j]), 3)) for j in np.argsort(beta)[:6]]),
        final_params=dict(alpha_analog=round(model.alpha, 3), th_in=model.th[0], th_out=model.th[1]),
        honesty=["Geliştirme (deneyim) dönemi sonucudur; test değildir.",
                 "Model kararları her ay yalnız önceki ay sonu bilgisiyle gerçek zamanlı verildi; ideal etiketler geriye dönüktür.",
                 "Dukascopy BID/ASK + varsayımsal %0,8/yön; Türk bankası kotasyonu değildir.",
                 "Haber metni yok; olaylar piyasa izi ve planlı makro yayınlarla temsil edildi."])
    json.dump(summary, open(os.path.join(HERE, "DENEYIM_V1_MARATON_OZET.json"), "w"), indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(HERE, "DENEYIM_V1_AYLIK_TABLO.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ay", "altin_degisim_pct", "ideal_altin_gun_payi", "ideal_ay_log_getiri_pct", "model_ay_getiri_pct", "model_nav_son",
                    "model_islem", "yanlis_gun_payi", "pozisyon_son", "alpha", "th_giris", "th_cikis"])
        for rp in reps:
            le = rp["learning_after_month"]
            w.writerow([rp["month"], rp["gold"]["change_pct"], rp["ideal"]["gold_days_share"], rp["ideal"]["month_log_return_pct"],
                        rp["model"]["month_ret_pct"], rp["model"]["nav_end"], len(rp["model"]["trades"]), rp["errors"]["wrong_day_share"],
                        rp["model"]["position_end"], le["alpha_analog"], le["th_in"], le["th_out"]])
    print(json.dumps({k: summary[k] for k in ("model", "passive", "trend_sma100", "ideal_oracle", "learning_by_year", "final_params")}, indent=1, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
