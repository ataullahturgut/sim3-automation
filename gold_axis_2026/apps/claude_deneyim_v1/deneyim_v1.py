"""DENEYİM v1 — ay ay deneyim maratonu (2023-01 → 2025-12). Bkz. DENEYIM_V1_MARATON_PROTOKOLU.md

Model (özgün): deneyim hafızası + ayırt edici metrik + benzer deneyim skoru + düzenlemeli doğrusal skor,
hatalardan öğrenen birleşim ağırlığı ve histerezisli giriş/çıkış eşikleri. Öğrenme yalnız ay sonuna kadarki veriyle.
"""
import math, json, os
from datetime import date
from collections import OrderedDict
import numpy as np
import deneyim_states as S

LOG1F = math.log(1 - S.FEE)
START = date(2023, 1, 3)
TH_IN = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
TH_OUT = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
DEFAULT_TH = (0.60, 0.40)
RIDGE = 10.0
PRIOR_W, PRIOR_P = 2.0, 0.5
H_OUT = 10                                   # v1.1 sonuç belleği ufku (karar günü)
C_RT = -200.0 * math.log(1 - S.FEE)          # tam tur log maliyet (%)
OUT_PRIOR_W = 5.0                            # sonuç tahmini öncül ağırlığı (sözde gözlem)


# ---------------------------------------------------------------- ideal al/sat (dinamik programlama)
def oracle(rows, i0, i1):
    """rows[i0..i1] üzerinde maliyetli en iyi NAKİT/ALTIN yolu. Dönüş: pozisyon listesi (1=ALTIN), işlemler."""
    n = i1 - i0 + 1
    Vc, Vg = 0.0, -1e18            # log servet (nakit) / log birim (altın)
    pc, pg = [None] * n, [None] * n  # geri izleme: önceki durum
    for j in range(n):
        r = rows[i0 + j]
        sell = Vg + math.log(r["bid"]) + LOG1F
        buy = Vc + LOG1F - math.log(r["ask"])
        nVc, pc[j] = (Vc, 0) if Vc >= sell else (sell, 1)
        nVg, pg[j] = (Vg, 1) if Vg >= buy else (buy, 0)
        Vc, Vg = nVc, nVg
    last = rows[i1]
    end_gold = Vg + math.log(last["bid"]) + LOG1F
    s = 1 if end_gold > Vc else 0
    pos = [0] * n
    for j in range(n - 1, -1, -1):
        pos[j] = s
        s = pg[j] if s == 1 else pc[j]
    return pos, max(Vc, end_gold)


def legs_from_positions(rows, i0, pos):
    legs, cur = [], None
    for j, p in enumerate(pos):
        prev = pos[j - 1] if j else 0
        if p == 1 and prev == 0:
            cur = dict(entry_i=i0 + j)
        if p == 0 and prev == 1 and cur:
            cur["exit_i"] = i0 + j; legs.append(cur); cur = None
    if cur:
        cur["exit_i"] = None; legs.append(cur)
    for L in legs:
        e = rows[L["entry_i"]]; L["entry_date"] = e["date"].isoformat(); L["entry_price"] = e["ask"]
        if L["exit_i"] is not None:
            x = rows[L["exit_i"]]; L["exit_date"] = x["date"].isoformat(); L["exit_price"] = x["bid"]
            L["net_pct"] = 100 * ((1 - S.FEE) ** 2 * x["bid"] / e["ask"] - 1)
        else:
            L["exit_date"] = None; L["exit_price"] = None; L["net_pct"] = None
    return legs


# ---------------------------------------------------------------- özgün deneyim modeli
class DeneyimModel:
    def __init__(self):
        self.w = None; self.beta = None; self.alpha = 0.5; self.th = DEFAULT_TH
        self.memX = None; self.memY = None; self.h = 1.0
        self.outX = None; self.outR = None; self.outD = None

    def set_outcomes(self, X, r, d):
        self.outX, self.outR, self.outD = X.copy(), r.copy(), d.copy()

    def outcome_est(self, x):
        """Benzer geçmiş durumlardan E[r_H] ve P(düşüş) (öncüllü çekirdek ortalaması)."""
        if self.outX is None or self.w is None or len(self.outR) == 0:
            return None
        d2 = ((self.outX - x) ** 2 * self.w).sum(1)
        k = np.exp(-d2 / (2 * self.h ** 2))
        base = float(self.outD.mean())
        Er = float((k @ self.outR + OUT_PRIOR_W * 0.0) / (k.sum() + OUT_PRIOR_W))
        Pd = float((k @ self.outD + OUT_PRIOR_W * base) / (k.sum() + OUT_PRIOR_W))
        return Er, Pd

    def fit(self, X, Y):
        """X: durum vektörleri, Y: ideal pozisyon (0/1). Tarih kullanılmaz."""
        self.memX, self.memY = X.copy(), Y.astype(float).copy()
        n1, n0 = Y.sum(), len(Y) - Y.sum()
        if n1 >= 10 and n0 >= 10:
            m1, m0 = X[Y == 1].mean(0), X[Y == 0].mean(0)
            sd = np.sqrt(0.5 * (X[Y == 1].var(0) + X[Y == 0].var(0))) + 1e-6
            d = np.abs(m1 - m0) / sd
            shrink = (n1 * n0 / (n1 + n0)) / ((n1 * n0 / (n1 + n0)) + 25.0)
            w = np.maximum(0.0, d * shrink - 0.02)
            self.w = w / w.sum() if w.sum() > 0 else np.full(X.shape[1], 1.0 / X.shape[1])
        else:
            self.w = np.full(X.shape[1], 1.0 / X.shape[1])
        # bant genişliği: hafızadaki rastgele ikililerin ağırlıklı uzaklık medyanı (sabit tohum)
        rng = np.random.default_rng(11)
        a = rng.integers(0, len(X), 400); b = rng.integers(0, len(X), 400)
        dd = np.sqrt(((X[a] - X[b]) ** 2 * self.w).sum(1))
        self.h = float(np.median(dd)) * 0.5 + 1e-6
        # düzenlemeli lojistik (Newton)
        A = np.hstack([np.ones((len(X), 1)), X]); beta = np.zeros(A.shape[1])
        R = np.eye(A.shape[1]) * RIDGE; R[0, 0] = 1e-6
        for _ in range(25):
            p = 1 / (1 + np.exp(-(A @ beta)))
            g = A.T @ (p - Y) + R @ beta
            Hm = (A * (p * (1 - p))[:, None]).T @ A + R
            step = np.linalg.solve(Hm, g); beta -= step
            if np.abs(step).max() < 1e-8: break
        self.beta = beta

    def p_parts(self, x):
        if self.memX is None:
            return None, None
        d2 = ((self.memX - x) ** 2 * self.w).sum(1)
        k = np.exp(-d2 / (2 * self.h ** 2))
        pa = float((k @ self.memY + PRIOR_W * PRIOR_P) / (k.sum() + PRIOR_W))
        pl = float(1 / (1 + math.exp(-(self.beta[0] + self.beta[1:] @ x))))
        return pa, pl

    def p(self, x):
        pa, pl = self.p_parts(x)
        if pa is None:
            return None, None, None
        return self.alpha * pa + (1 - self.alpha) * pl, pa, pl


def replay(rows, idx, probs, th_in, th_out):
    """Gerçek zamanlı skor dizisiyle gerçek yürütme (maliyetli) — eşik öğrenimi ve raporlar için."""
    cash, units, pos, trades = 100.0, 0.0, 0, 0
    for i, p in zip(idx, probs):
        r = rows[i]
        if p is None:
            continue
        if pos == 0 and p >= th_in:
            units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1; trades += 1
        elif pos == 1 and p <= th_out:
            cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0; trades += 1
    last = rows[idx[-1]]
    return cash + units * last["bid"] * (1 - S.FEE), trades


def logloss(p, y):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


# ---------------------------------------------------------------- maraton
def marathon(outdir, mode="C0", report_dir="reports"):
    assert mode in ("C0", "C1", "C2")
    rows = S.load_rows(dev_only=True)
    raw, macro = S.build_states(rows)
    Z, std = S.standardize(raw)
    eventreg = load_event_register()
    i_start = next(i for i, r in enumerate(rows) if r["date"] >= START)
    months = OrderedDict()
    for i in range(i_start, len(rows)):
        months.setdefault(rows[i]["date"].strftime("%Y-%m"), []).append(i)
    model = DeneyimModel()
    est = {}                      # gerçek zamanlı sonuç tahminleri: i -> (E[r_H], P(düşüş))
    rt = {}                       # gerçek zamanlı skorlar: i -> (p, pa, pl)
    cash, units, pos = 100.0, 0.0, 0
    nav_hist, trades_all = [], []
    prev_w = None
    reports = []
    os.makedirs(os.path.join(outdir, report_dir), exist_ok=True)
    for m, idxs in months.items():
        # (A) ay içi gerçek zamanlı kararlar: model parametreleri önceki ay sonundan
        month_trades = []; nav0 = cash + units * rows[idxs[0] - 1]["bid"] * (1 - S.FEE) if idxs[0] > i_start else 100.0
        for i in idxs:
            r = rows[i]
            p, pa, pl = model.p(Z[i])
            rt[i] = (p, pa, pl)
            est[i] = model.outcome_est(Z[i]) if mode != "C0" else None
            buy = sell = False
            if mode == "C0" and p is not None:
                buy = pos == 0 and p >= model.th[0]; sell = pos == 1 and p <= model.th[1]
            elif mode in ("C1", "C2") and est[i] is not None:
                Er, Pd = est[i]
                if mode == "C1":
                    buy = pos == 0 and Er > C_RT / 2; sell = pos == 1 and Er < -C_RT / 2
                else:
                    buy = pos == 0 and Er > 0 and Pd < 0.30; sell = pos == 1 and Pd > 0.50
            if buy:
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1
                month_trades.append(dict(date=r["date"].isoformat(), action="AL", price=r["ask"], p=None if p is None else round(p, 3),
                                         Er=None if est[i] is None else round(est[i][0], 3), Pdown=None if est[i] is None else round(est[i][1], 3)))
            elif sell:
                cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
                month_trades.append(dict(date=r["date"].isoformat(), action="SAT", price=r["bid"], p=None if p is None else round(p, 3),
                                         Er=None if est[i] is None else round(est[i][0], 3), Pdown=None if est[i] is None else round(est[i][1], 3)))
            nav_hist.append((i, cash + units * r["bid"] * (1 - S.FEE), pos))
        trades_all += month_trades
        i_end = idxs[-1]
        # (B) ideal yol: başlangıçtan bu ay sonuna (yalnız mevcut veriyle)
        opos, olog = oracle(rows, i_start, i_end)
        Y = np.array(opos)
        legs = legs_from_positions(rows, i_start, opos)
        # (C) bu ayın analizi ve hatalar
        rep = month_report(m, idxs, rows, raw, Z, Y, i_start, legs, nav_hist, month_trades, nav0, rt, model,
                           macro, eventreg, prev_w)
        # (D) deneyimi güncelle ve yeniden öğren (yalnız bu ay sonuna kadarki veri)
        X = Z[i_start:i_end + 1]
        model.fit(X, Y)
        # sonuç belleği: yalnız bu ay sonuna kadar olgunlaşmış ileri sonuçlar (i + H <= i_end)
        oi = list(range(i_start, i_end - H_OUT + 1))
        if oi:
            mid = lambda q: (rows[q]["bid"] + rows[q]["ask"]) / 2
            rH = np.array([100 * math.log(mid(q + H_OUT) / mid(q)) for q in oi])
            dH = np.array([1.0 if 100 * math.log(min(mid(q + j) for j in range(1, H_OUT + 1)) / mid(q)) < -C_RT else 0.0 for q in oi])
            model.set_outcomes(Z[oi], rH, dH)
        if mode != "C0":
            ests = [est[q] for q in idxs if est.get(q) is not None]
            rep["model"]["mean_Er"] = round(float(np.mean([e[0] for e in ests])), 3) if ests else None
            rep["model"]["mean_Pdown"] = round(float(np.mean([e[1] for e in ests])), 3) if ests else None
        hist_i = [i for i in range(i_start, i_end + 1) if rt.get(i, (None,))[0] is not None]
        recent = hist_i[-126:]
        if len(recent) >= 60:
            lla = np.mean([logloss(rt[i][1], Y[i - i_start]) for i in recent])
            lll = np.mean([logloss(rt[i][2], Y[i - i_start]) for i in recent])
            model.alpha = float((1 / lla) / ((1 / lla) + (1 / lll)))
            probs = [rt[i][0] for i in hist_i]
            best = None
            for a in TH_IN:
                for b in TH_OUT:
                    if b >= a: continue
                    nav, ntr = replay(rows, hist_i, probs, a, b)
                    key = (round(nav, 6), a - b)
                    if best is None or key > best[0]: best = (key, (a, b), ntr)
            model.th = best[1]
        rep["learning_after_month"] = dict(
            memory_days=int(len(X)), ideal_gold_share=round(float(Y.mean()), 3), alpha_analog=round(model.alpha, 3),
            th_in=model.th[0], th_out=model.th[1],
            top_weights=[(S.FEATURES[j], round(float(model.w[j]), 4)) for j in np.argsort(-model.w)[:8]],
            group_weights={g: round(float(sum(model.w[S.FEATURES.index(f)] for f in fs)), 3) for g, fs in S.GROUPS.items()})
        prev_w = model.w.copy()
        write_report(outdir, rep, report_dir)
        reports.append(rep)
    return dict(rows=rows, raw=raw, Z=Z, std=std, model=model, rt=rt, est=est, mode=mode, nav_hist=nav_hist, trades=trades_all,
                reports=reports, i_start=i_start, macro=macro, oracle_final=(opos, olog), legs_final=legs)


def load_event_register():
    import csv
    out = []
    with open(os.path.join(S.EVENTS, "GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv")) as fh:
        for r in csv.DictReader(fh):
            try:
                a = date.fromisoformat(r["start_or_first_flag"][:10]); b = date.fromisoformat(r["end_or_last_flag"][:10])
            except ValueError:
                continue
            out.append(dict(start=a, end=b, dir=r["gold_direction"], move=r["movement_pct_value"],
                            cls=r["old_Claude_95_economic_class_HYPOTHESIS"], mech=r["economic_mechanism_HYPOTHESIS"],
                            evidence=r["scientific_evidence_current_level"], key=r["corrected_key"]))
    return out


# ---------------------------------------------------------------- aylık rapor
def month_report(m, idxs, rows, raw, Z, Y, i_start, legs, nav_hist, mtrades, nav0, rt, model, macro, eventreg, prev_w):
    r0, r1 = rows[idxs[0]], rows[idxs[-1]]
    prev_close = rows[idxs[0] - 1]["p06"] if idxs[0] > 0 else r0["p06"]
    navs = {i: v for (i, v, _) in nav_hist}
    nav_end = navs[idxs[-1]]
    # ideal yolun bu aydaki getirisi (log) ve modelin
    def mid(i): return (rows[i]["bid"] + rows[i]["ask"]) / 2
    ideal_ret = sum(100 * math.log(mid(i) / mid(i - 1)) for i in idxs if i > i_start and Y[i - 1 - i_start] == 1)
    month_legs = [L for L in legs if (L["exit_i"] is None or L["exit_i"] >= idxs[0]) and L["entry_i"] <= idxs[-1]]
    # hatalar
    mp = {i: p for (i, _, p) in nav_hist}
    miss_up = sum(1 for i in idxs if Y[i - i_start] == 1 and mp[i] == 0)
    false_hold = sum(1 for i in idxs if Y[i - i_start] == 0 and mp[i] == 1)
    # neden: her ideal bacakta değişkenlerin standart değişimi (bacak içi, ay içine kırpılmış)
    drivers = []
    for L in month_legs:
        a = max(L["entry_i"], idxs[0]); b = L["exit_i"] if (L["exit_i"] is not None and L["exit_i"] <= idxs[-1]) else idxs[-1]
        dz = Z[b] - Z[a]
        top_move = [(S.LABEL_TR[S.FEATURES[j]], round(float(dz[j]), 2)) for j in np.argsort(-np.abs(dz))[:5]]
        top_state = [(S.LABEL_TR[S.FEATURES[j]], round(float(Z[a][j]), 2)) for j in np.argsort(-np.abs(Z[a]))[:5]]
        drivers.append(dict(entry=L["entry_date"], exit=L["exit_date"], net_pct=None if L["net_pct"] is None else round(L["net_pct"], 2),
                            state_at_entry=top_state, biggest_changes=top_move))
    # ideal NAKİT dönemleri (düşüşler) için de neden
    cash_spells = []
    j = 0
    while j < len(idxs):
        if Y[idxs[j] - i_start] == 0:
            k = j
            while k + 1 < len(idxs) and Y[idxs[k + 1] - i_start] == 0: k += 1
            if k - j + 1 >= 2:
                a, b = idxs[j], idxs[k]
                drop = 100 * math.log(mid(b) / mid(a - 1)) if a > 0 else 0.0
                dz = Z[b] - Z[a]
                cash_spells.append(dict(start=rows[a]["date"].isoformat(), end=rows[b]["date"].isoformat(), gold_move_pct=round(drop, 2),
                                        state_at_start=[(S.LABEL_TR[S.FEATURES[q]], round(float(Z[a][q]), 2)) for q in np.argsort(-np.abs(Z[a]))[:5]],
                                        biggest_changes=[(S.LABEL_TR[S.FEATURES[q]], round(float(dz[q]), 2)) for q in np.argsort(-np.abs(dz))[:5]]))
            j = k + 1
        else:
            j += 1
    rel = [dict(kind=x["kind"], utc=x["ts"].isoformat()[:16], surprise=x["surprise"], gold_post60=x["post60"], gold_post240=x["post240"])
           for x in macro if x["ts"].date() >= r0["date"] and x["ts"].date() <= r1["date"]]
    ev = [dict(key=e["key"], dir=e["dir"], move_pct=e["move"], cls=e["cls"], mech=e["mech"], start=e["start"].isoformat(), end=e["end"].isoformat())
          for e in eventreg if e["start"] <= r1["date"] and e["end"] >= r0["date"]]
    cot_a, cot_b = raw[idxs[0]].get("cot_mm"), raw[idxs[-1]].get("cot_mm")
    rr_a, rr_b = raw[idxs[0]].get("rr_d20"), raw[idxs[-1]].get("rr_d20")
    rep = OrderedDict(
        month=m, days=len(idxs),
        gold=dict(start_prev_close=round(prev_close, 2), end=round(r1["p06"], 2), change_pct=round(100 * (r1["p06"] / prev_close - 1), 2),
                  high=round(max(rows[i]["p06"] for i in idxs), 2), low=round(min(rows[i]["p06"] for i in idxs), 2)),
        ideal=dict(month_log_return_pct=round(ideal_ret, 2), gold_days_share=round(float(np.mean([Y[i - i_start] for i in idxs])), 3),
                   legs=[dict(entry=L["entry_date"], entry_price=round(L["entry_price"], 2), exit=L["exit_date"],
                              exit_price=None if L["exit_price"] is None else round(L["exit_price"], 2),
                              net_pct=None if L["net_pct"] is None else round(L["net_pct"], 2)) for L in month_legs]),
        model=dict(nav_start=round(nav0, 4), nav_end=round(nav_end, 4), month_ret_pct=round(100 * (nav_end / nav0 - 1), 2),
                   trades=mtrades, position_end="ALTIN" if mp[idxs[-1]] else "NAKİT",
                   mean_p=None if rt[idxs[0]][0] is None else round(float(np.mean([rt[i][0] for i in idxs])), 3),
                   capture_of_ideal=None if abs(ideal_ret) < 1e-9 else round(100 * math.log(nav_end / nav0) / ideal_ret, 1)),
        errors=dict(missed_gold_days=miss_up, false_gold_days=false_hold, wrong_day_share=round((miss_up + false_hold) / len(idxs), 3)),
        why=dict(ideal_legs_drivers=drivers, ideal_cash_spells=cash_spells, macro_releases=rel,
                 cot_mm_change=None if (cot_a is None or cot_b is None) else round(cot_b - cot_a, 4),
                 real_rate_20d_change_start_end=[rr_a, rr_b], event_register_hypotheses_hindsight=ev),
    )
    return rep


def write_report(outdir, rep, report_dir="reports"):
    m = rep["month"]
    json.dump(rep, open(os.path.join(outdir, report_dir, f"AYLIK_{m.replace('-', '_')}.json"), "w"), indent=1, ensure_ascii=False, default=str)
    g, ide, mo, er, why, le = rep["gold"], rep["ideal"], rep["model"], rep["errors"], rep["why"], rep["learning_after_month"]
    L = [f"# DENEYİM v1 — Aylık matematiksel model raporu: {m}", "",
         f"**Altın (06:00Z mid):** {g['start_prev_close']} → {g['end']} (%{g['change_pct']}), ay içi en yüksek {g['high']}, en düşük {g['low']}.", "",
         "## En uygun strateji (maliyetli dinamik programlama, geriye dönük)",
         f"Bu ayda ideal yol günlerin %{round(100 * ide['gold_days_share'])}'inde ALTIN; ideal yolun ay içi log getirisi %{ide['month_log_return_pct']}."]
    for x in ide["legs"]:
        L.append(f"- AL {x['entry']} @ {x['entry_price']} → SAT {x['exit'] or '(açık)'} @ {x['exit_price'] or '-'} | net %{x['net_pct'] if x['net_pct'] is not None else '-'}")
    if not ide["legs"]:
        L.append("- Bu ay ideal yolda altın pozisyonu yok.")
    L += ["", "## Modelin bu ayki kendi kararları (gerçek zamanlı, önceki ay sonu bilgisiyle)",
          f"NAV {mo['nav_start']} → {mo['nav_end']} (%{mo['month_ret_pct']}); ay sonu pozisyon {mo['position_end']}; ort. skor {mo['mean_p']}; ideal getirinin yakalanan payı %{mo['capture_of_ideal']}."]
    if "mean_Er" in mo:
        L.append(f"Benzer geçmiş durumlardan tahmin (ay ortalaması): 10 günlük beklenen getiri %{mo['mean_Er']}, düşüş (> %1,6) olasılığı {mo['mean_Pdown']}.")
    for t in mo["trades"]:
        extra = f", E[r]={t['Er']}, P(düşüş)={t['Pdown']}" if t.get("Er") is not None else ""
        L.append(f"- {t['date']} {t['action']} @ {round(t['price'], 2)} (skor {t['p']}{extra})")
    if not mo["trades"]:
        L.append("- İşlem yok.")
    L += ["", f"**Hatalar:** ideal ALTIN iken NAKİT kalınan gün {er['missed_gold_days']}, ideal NAKİT iken ALTIN tutulan gün {er['false_gold_days']} (yanlış gün payı %{round(100 * er['wrong_day_share'])}).", "",
          "## Neden yükseldi / neden düştü (ölçülen durum değişimleri)"]
    for d in why["ideal_legs_drivers"]:
        L.append(f"- **Yükseliş bacağı {d['entry']} → {d['exit'] or 'açık'}** (net %{d['net_pct'] if d['net_pct'] is not None else '-'}). Girişteki belirgin durum: " +
                 ", ".join(f"{a} {b:+}" for a, b in d["state_at_entry"]) + ". En çok değişenler: " + ", ".join(f"{a} {b:+}" for a, b in d["biggest_changes"]) + ".")
    for c in why["ideal_cash_spells"]:
        L.append(f"- **İdeal NAKİT dönemi {c['start']} → {c['end']}** (altın %{c['gold_move_pct']}). Başlangıç durumu: " +
                 ", ".join(f"{a} {b:+}" for a, b in c["state_at_start"]) + ". En çok değişenler: " + ", ".join(f"{a} {b:+}" for a, b in c["biggest_changes"]) + ".")
    if why["macro_releases"]:
        L.append("- Makro yayınlar: " + "; ".join(f"{x['kind']} {x['utc']} sürpriz {x['surprise']} → altın 60dk %{x['gold_post60']}, 240dk %{x['gold_post240']}" for x in why["macro_releases"]))
    L.append(f"- COT managed money net değişimi: {why['cot_mm_change']}.")
    if why["event_register_hypotheses_hindsight"]:
        L.append("- Olay kaydı hipotezleri (geriye dönük bağlam, model girdisi değil): " +
                 "; ".join(f"{e['dir']} {e['start']}→{e['end']} %{e['move_pct']} [{e['cls']}: {e['mech']}]" for e in why["event_register_hypotheses_hindsight"][:6]))
    L += ["", "## Ay sonu öğrenme (bu aya kadarki deneyimle)",
          f"Hafıza {le['memory_days']} gün, ideal ALTIN payı %{round(100 * le['ideal_gold_share'])}; benzer-deneyim ağırlığı α={le['alpha_analog']}; eşikler giriş {le['th_in']} / çıkış {le['th_out']}.",
          "Değişken grubu önemleri: " + ", ".join(f"{g} {w}" for g, w in sorted(le["group_weights"].items(), key=lambda kv: -kv[1])) + ".",
          "En ayırt edici değişkenler: " + ", ".join(f"{S.LABEL_TR[a]} {b}" for a, b in le["top_weights"]) + ".", ""]
    with open(os.path.join(outdir, report_dir, f"AYLIK_{m.replace('-', '_')}.md"), "w") as fh:
        fh.write("\n".join(L))
