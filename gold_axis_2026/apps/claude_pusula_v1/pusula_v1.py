"""PUSULA v1 — Claude özgün öğrenen altın modeli (PUSULA_V1_PREREG.md'ye birebir uygulanır).

Bayesçi indirimli doğrusal modeller topluluğu (9 aday), log-skorla öğrenen ağırlıklar,
ay sonu kalibrasyonu ve maliyete duyarlı uzun/nakit karar kuralı.
Gelecek bilgisi: t gününün kararı yalnız P_0..P_t (06:00Z) ve t−H−1 gününe kadar
olgunlaşmış etiketleri kullanır. Canlı emir yoktur.
"""
import csv, math, json
from datetime import date
import numpy as np

H = 10                     # ufuk (karar günü)
FEE = 0.008                # banka maliyeti / yön (varsayım)
C_RT = -200.0 * math.log(1 - FEE)   # tam tur log maliyet (%)
B = C_RT / 6.0             # ufuk başına eşik (%)
DELTAS = (0.990, 0.997, 0.999)
SETS = ("S0", "S1", "S2")
W_DECAY = 0.995
S_INIT, S_DECAY, S_FLOOR = 9.0, 0.99, 0.25
CAL_WINDOW, CAL_LO, CAL_HI = 120, 0.5, 2.0
MIN_HIST, ZCLIP = 60, 4.0
TRADE_START = date(2023, 1, 3)
GOLD_F = ("f1", "f2", "f3", "f4", "f5", "f6")
CROSS_F = ("x_nq", "x_zn", "x_cl", "x_si")


def load_panel(path):
    rows = []
    with open(path) as fh:
        for r in csv.DictReader(fh):
            if r["open"] != "1":
                continue
            d = date.fromisoformat(r["date"])
            rec = dict(date=d, src=r["src"], p06=float(r["p06"]),
                       bid=float(r["bid09"]), ask=float(r["ask09"]))
            for s in ("nq", "zn", "cl", "si"):
                rec[s] = float(r[s]) if r[s] else None
                rec[s + "_k"] = int(r[s + "_k"]) if r[s + "_k"] else None
            rows.append(rec)
    return rows


def raw_features(rows):
    """Her karar günü için ham özellikler; yalnız o güne kadarki fiyatlar."""
    P = [r["p06"] for r in rows]
    out = []
    f1hist = []
    for t, r in enumerate(rows):
        f = {}
        lp = math.log(P[t])
        f["f1"] = 100 * (lp - math.log(P[t - 1])) if t >= 1 else None
        f["f2"] = 100 * (lp - math.log(P[t - 5])) if t >= 5 else None
        f["f3"] = 100 * (lp - math.log(P[t - 20])) if t >= 20 else None
        f["f4"] = 100 * (lp - math.log(P[t - 60])) if t >= 60 else None
        if f["f1"] is not None:
            f1hist.append(f["f1"])
        f["f5"] = math.log(max(1e-6, float(np.std(f1hist[-20:])))) if len(f1hist) >= 20 else None
        f["f6"] = 100 * (lp - math.log(max(P[max(0, t - 59):t + 1]))) if t >= 59 else None
        for s in ("nq", "zn", "cl", "si"):
            v = None
            if t >= 5:
                a, b = r[s], rows[t - 5][s]
                if a is not None and b is not None and r[s + "_k"] == rows[t - 5][s + "_k"]:
                    v = 100 * math.log(a / b)
            f["x_" + s] = v
        out.append(f)
    return out


class Standardizer:
    """Genişleyen pencere; istatistik yalnız ÖNCEKİ günlerden."""
    def __init__(self, names):
        self.n = {k: 0 for k in names}; self.m = {k: 0.0 for k in names}; self.q = {k: 0.0 for k in names}

    def z(self, k, v):
        if v is None or self.n[k] < MIN_HIST:
            return 0.0
        sd = math.sqrt(self.q[k] / (self.n[k] - 1))
        if sd <= 0:
            return 0.0
        return max(-ZCLIP, min(ZCLIP, (v - self.m[k]) / sd))

    def add(self, k, v):
        if v is None:
            return
        self.n[k] += 1; d = v - self.m[k]; self.m[k] += d / self.n[k]; self.q[k] += d * (v - self.m[k])


class DLM:
    def __init__(self, dim, delta):
        self.delta = delta
        self.m = np.zeros(dim)
        self.C = np.diag([1.0] + [0.25] * (dim - 1))
        self.S = S_INIT

    def predict(self, x):
        R = self.C / self.delta
        s2 = float(x @ R @ x)
        return float(x @ self.m), s2, s2 + self.S

    def update(self, x, y):
        e = y - float(x @ self.m)
        R = self.C / self.delta
        q = float(x @ R @ x) + H * self.S
        A = (R @ x) / q
        self.m = self.m + A * e
        self.C = R - np.outer(A, A) * q
        self.C = 0.5 * (self.C + self.C.T)
        self.S = max(S_FLOOR, S_DECAY * self.S + (1 - S_DECAY) * e * e)


def lognorm(y, mu, v):
    return -0.5 * math.log(2 * math.pi * v) - (y - mu) ** 2 / (2 * v)


def vec(zs, which):
    names = {"S0": (), "S1": GOLD_F, "S2": GOLD_F + CROSS_F}[which]
    return np.array([1.0] + [zs[k] for k in names])


def run(rows):
    """Tüm koşu. Dönüş: gün günlük kayıt, aylık raporlar, son durum."""
    feats = raw_features(rows)
    std = Standardizer(GOLD_F + CROSS_F)
    models = [(s, d, DLM(len(vec({k: 0 for k in GOLD_F + CROSS_F}, s)), d)) for s in SETS for d in DELTAS]
    K = len(models)
    L = np.zeros(K)
    c2 = 1.0
    store = []          # karar anı tahminleri (etiket olgunlaşınca kullanılır)
    matured = []        # (t, y, mu, v) topluluk; kalibrasyon için
    next_label = 0
    pos, cash, units = "CASH", 100.0, 0.0
    trend = dict(pos="CASH", cash=100.0, units=0.0)
    passive = None
    log = []
    T = len(rows)
    for t in range(T):
        r = rows[t]
        # (1) olgunlaşan etiketler: i + H <= t − 1  (i+H gününün 09:00Z fiyatı, t gününün 06:00Z'sinden önce bilinir)
        while next_label + H <= t - 1:
            i = next_label
            y = 100 * math.log(((rows[i + H]["bid"] + rows[i + H]["ask"]) / 2) / ((rows[i]["bid"] + rows[i]["ask"]) / 2))
            rec = store[i]
            for k, (_, _, mdl) in enumerate(models):
                mu_k, s2_k, v_k = rec["k"][k]
                L[k] = W_DECAY * L[k] + (1.0 / H) * lognorm(y, mu_k, rec["c2"] * v_k)
                mdl.update(rec["x"][k], y)
            matured.append((i, y, rec["mu"], rec["v"]))
            log[i]["y"] = y
            next_label += 1
        # (2) özellikler (yalnız önceki günlerin istatistiğiyle standardize), sonra istatistiğe bugünü ekle
        zs = {k: std.z(k, feats[t][k]) for k in GOLD_F + CROSS_F}
        for k in GOLD_F + CROSS_F:
            std.add(k, feats[t][k])
        # (3) aday tahminleri ve topluluk
        w = np.exp(L - L.max()); w /= w.sum()
        preds, xs = [], []
        for (s, d, mdl) in models:
            x = vec(zs, s); xs.append(x); preds.append(mdl.predict(x))
        mu = float(sum(w[k] * preds[k][0] for k in range(K)))
        s2 = float(sum(w[k] * (preds[k][1] + (preds[k][0] - mu) ** 2) for k in range(K)))
        v = float(sum(w[k] * (preds[k][2] + (preds[k][0] - mu) ** 2) for k in range(K)))
        sd = math.sqrt(s2)
        store.append(dict(x=xs, k=preds, mu=mu, v=v, c2=c2, w=w.copy()))
        # (4) karar ve dolum (09:00Z aynı gün)
        action = "WAIT"
        if r["date"] >= TRADE_START:
            if passive is None:
                passive = dict(units=100.0 * (1 - FEE) / r["ask"], start=r["date"].isoformat())
            if pos == "CASH" and mu - sd > B:
                units = cash * (1 - FEE) / r["ask"]; cash = 0.0; pos = "GOLD"; action = "BUY"
            elif pos == "GOLD" and mu < -B:
                cash = units * r["bid"] * (1 - FEE); units = 0.0; pos = "CASH"; action = "SELL"
            # trend kuralı (SMA100, ±%1 bant), aynı yürütme
            if t >= 99:
                sma = sum(x["p06"] for x in rows[t - 99:t + 1]) / 100.0
                if trend["pos"] == "CASH" and r["p06"] > 1.01 * sma:
                    trend["units"] = trend["cash"] * (1 - FEE) / r["ask"]; trend["cash"] = 0.0; trend["pos"] = "GOLD"
                elif trend["pos"] == "GOLD" and r["p06"] < 0.99 * sma:
                    trend["cash"] = trend["units"] * r["bid"] * (1 - FEE); trend["units"] = 0.0; trend["pos"] = "CASH"
        liq = lambda c, u: c + u * r["bid"] * (1 - FEE)
        log.append(dict(t=t, date=r["date"].isoformat(), src=r["src"], mu=mu, sd=sd, v=v, c2=c2,
                        action=action, pos=pos,
                        nav=liq(cash, units) if r["date"] >= TRADE_START else None,
                        nav_passive=liq(0.0, passive["units"]) if passive else None,
                        nav_trend=liq(trend["cash"], trend["units"]) if r["date"] >= TRADE_START else None,
                        trend_pos=trend["pos"], mu_s0=preds[1][0], v_s0=preds[1][2],
                        w=[round(float(a), 4) for a in w], wf=[float(a) for a in w],
                        kp=[(p[0], p[2]) for p in preds], y=None,
                        trend_up=(r["p06"] > sum(x["p06"] for x in rows[t - 99:t + 1]) / 100.0) if t >= 99 else None))
        # (5) ay sonu öğrenme adımı: son 120 olgun etiketle kalibrasyon; sonraki ay geçerli
        last_of_month = (t == T - 1) or (rows[t + 1]["date"].month != r["date"].month)
        if last_of_month:
            recent = matured[-CAL_WINDOW:]
            if len(recent) >= CAL_WINDOW:
                zz = [(y - m_) ** 2 / vv for (_, y, m_, vv) in recent]
                c2 = min(CAL_HI, max(CAL_LO, sum(zz) / len(zz)))
            else:
                c2 = 1.0
            log[-1]["c2_next"] = c2
    return log, models, dict(pos=pos, cash=cash, units=units)


def max_dd(series):
    peak, mdd = -1e18, 0.0
    for v in series:
        peak = max(peak, v); mdd = max(mdd, 100 * (1 - v / peak))
    return mdd
