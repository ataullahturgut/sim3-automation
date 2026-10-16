"""TERAZİ v3.7 — 2026 sınavı. Ön kayıt: TERAZI_V3_7_2026_SINAV_ON_KAYIT.md. Tek koşu."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "claude_deneyim_v1"))   # import yolu (model değişikliği değil)
import deneyim_states as S
_orig = S.load_rows
S.load_rows = lambda dev_only=True: _orig(dev_only=False)
import run_terazi_v3_4 as R4, karar_v37 as K, run_terazi_v3 as RV


def main():
    res, A = R4.run("v310")
    rows = A["rows"]; daily = A["daily"]
    json.dump(daily, open(os.path.join(HERE, "TERAZI_2026_SINAV_GUNLUK.json"), "w"), indent=0)
    navs, tr, trace = K.simulate(daily, rows)
    dates = [x["date"] for x in trace]
    d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    i25 = max(i for i, d in enumerate(dates) if d <= "2025-12-31")
    n0 = navs[i25]; seg = [(d, v / n0 * 100) for d, v in zip(dates[i25:], navs[i25:])]
    p0 = rows[d2i[dates[i25]]]["bid"]
    bh = [(d, 100 * rows[d2i[d]]["bid"] / p0) for d in dates[i25:]]
    pos_end25 = trace[i25]["pos"]
    tr26 = [t for t in tr if t[0] >= "2026-01-01"]
    pairs = [dict(sat=a[0], sat_f=a[2], al=b[0], al_f=b[2], kazanc=round(100 * (a[2] * (1 - S.FEE) ** 2 / b[2] - 1), 2))
             for a, b in zip(tr, tr[1:]) if a[1] == "SAT" and b[1] == "AL" and a[0] >= "2026-01-01"]
    dd_m, dd_b = RV.mdd([v for _, v in seg]), RV.mdd([v for _, v in bh])
    monthly = {}
    for (d, v), (_, b) in zip(seg, bh):
        monthly[d[:7]] = (round(v, 2), round(b, 2))
    src = sorted({r["src"] for r in rows if str(r["date"]) >= "2026-01-01"})
    out = dict(model_2026=round(seg[-1][1] - 100, 2), al_tut_2026=round(bh[-1][1] - 100, 2),
               T1=seg[-1][1] >= bh[-1][1], max_dd_model=round(dd_m, 2), max_dd_al_tut=round(dd_b, 2), T2=dd_m < dd_b,
               pos_2025_sonu=pos_end25, islemler_2026=tr26, satis_geri_alim=pairs, ay_sonu=monthly,
               son_gun=dates[-1], kaynak_2026=src, dev_kontrol_nav_2025_sonu=round(n0, 2),
               nav_2026=[(d, round(v, 2)) for d, v in seg], al_tut_nav_2026=[(d, round(v, 2)) for d, v in bh])
    print(json.dumps({k: v for k, v in out.items() if k not in ("nav_2026", "al_tut_nav_2026")}, indent=1, ensure_ascii=False))
    json.dump(out, open(os.path.join(HERE, "TERAZI_V3_7_2026_SINAV_SONUC.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
