"""DENEYİM v1.1: üç adayı koşar, ön kayıtlı kuralla seçer, seçileni dondurur.
Kullanım: python3 run_v1_1.py
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


def stats(R):
    rows = R["rows"]; nh = R["nav_hist"]
    nav_at = lambda d: [v for (i, v, _) in nh if rows[i]["date"] <= d][-1]
    n24 = nav_at(date(2024, 12, 31)); nend = nh[-1][1]
    return OrderedDict(nav_2023_2024=round(n24, 4), ret_2025_pct=round(100 * (nend / n24 - 1), 2), nav_final=round(nend, 4),
                       maxdd_2023_2024=round(mdd([v for (i, v, _) in nh if rows[i]["date"] <= date(2024, 12, 31)]), 2),
                       maxdd_all=round(mdd([v for (_, v, _) in nh]), 2), trades=len(R["trades"]), trade_list=R["trades"])


def main():
    res = OrderedDict(); runs = {}
    for mode in ("C0", "C1", "C2"):
        R = D.marathon(tempfile.mkdtemp(), mode=mode); runs[mode] = R; res[mode] = stats(R)
    # ön kayıtlı seçim: 2023–2024 NAV en yüksek (eşitlikte düşük maks. düşüş)
    pick = max(res, key=lambda k: (res[k]["nav_2023_2024"], -res[k]["maxdd_2023_2024"]))
    reverted = False
    if pick != "C0" and res[pick]["ret_2025_pct"] < res["C0"]["ret_2025_pct"] - 5.0:
        reverted = True; first_pick = pick; pick = "C0"
    # seçilenin aylık raporlarını yaz
    R = D.marathon(HERE, mode=pick, report_dir="reports_v1_1")
    rows, Z, model, i0 = R["rows"], R["Z"], R["model"], R["i_start"]
    first = rows[[i for (i, _, _) in R["nav_hist"]][0]]
    passive = [100 * (1 - S.FEE) ** 2 * rows[i]["bid"] / first["ask"] for (i, _, _) in R["nav_hist"]]
    opos, olog = R["oracle_final"]
    frozen = OrderedDict(
        model="DENEYIM_V1_1", decision_layer=pick, frozen_at_month="2025-12", features=S.FEATURES,
        standardizer=R["std"].state(), memory_X=Z[i0:len(rows)].round(6).tolist(), memory_Y=list(map(int, opos)),
        outcome_X=model.outX.round(6).tolist(), outcome_r=model.outR.round(6).tolist(), outcome_d=model.outD.tolist(),
        metric_weights=model.w.round(6).tolist(), bandwidth=model.h, logistic_beta=model.beta.round(6).tolist(),
        alpha_analog=model.alpha, th_in=model.th[0], th_out=model.th[1], H_out=D.H_OUT, c_rt=D.C_RT, fee=S.FEE,
        out_prior_w=D.OUT_PRIOR_W, prior=dict(weight=D.PRIOR_W, p=D.PRIOR_P), ridge=D.RIDGE,
        note="2026 testi bu dosyayla, kod değiştirilmeden yapılır. 2026 verisi yüklenmedi.")
    json.dump(frozen, open(os.path.join(HERE, "DENEYIM_V1_1_DONDURULMUS_MODEL.json"), "w"), ensure_ascii=False)
    out = OrderedDict(candidates=res, selected=pick, reverted_by_2025_check=reverted,
                      first_pick=first_pick if reverted else pick,
                      passive=dict(nav_2023_2024=round([p for (i, _, _), p in zip(R["nav_hist"], passive) if rows[i]["date"] <= date(2024, 12, 31)][-1], 4),
                                   nav_final=round(passive[-1], 4), maxdd_all=round(mdd(passive), 2)),
                      ideal_final_nav=round(100 * math.exp(olog), 4))
    json.dump(out, open(os.path.join(HERE, "DENEYIM_V1_1_SECIM_SONUCU.json"), "w"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps({k: (v if k != "candidates" else {m: {x: y for x, y in s.items() if x != "trade_list"} for m, s in v.items()}) for k, v in out.items()}, indent=1, ensure_ascii=False, default=str))
    for m in res:
        print(m, [(t["date"], t["action"]) for t in res[m]["trade_list"]])


if __name__ == "__main__":
    main()
