"""DENEYİM v1 — tarihsiz, karar anında bilinen durum değişkenleri.

Her karar günü t (06:00Z) için yalnız o ana kadar yayımlanmış verilerle durum vektörü üretir.
Erişim kuralları DENEYIM_V1_MARATON_PROTOKOLU.md'dedir. Geliştirme modunda 2025-12-31 sonrası yüklenmez.
"""
import csv, math, os
from datetime import date, datetime, timedelta, timezone
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))           # gold_axis_2026
PANEL = os.path.join(HERE, "..", "claude_pusula_v1", "data", "PUSULA_V1_DAILY_ASOF_PANEL.csv")
DOLLAR = os.path.join(HERE, "..", "claude_pusula_v1", "data", "FRED_DOLLAR_2020_2026.csv")
EVENTS = os.path.join(HERE, "..", "claude_pusula_v1", "data", "events")
DEV_END = date(2025, 12, 31)
FEE = 0.008
MIN_HIST, ZCLIP = 60, 4.0

FEATURES = [
    "g_r1", "g_r5", "g_r20", "g_r60", "g_vol20", "g_dd60", "g_dist200",
    "rr_d5", "rr_d20", "y2_d5", "y2_d20",
    "usd_d20",
    "gvz_lvl", "gvz_d5",
    "cot_mm", "cot_mm_d4",
    "cpi_surp", "cpi_days", "nfp_surp", "nfp_days", "fomc_since", "fomc_to", "last_react",
    "nq_r5", "nq_r20", "zn_r5", "cl_r5", "cl_r20", "si_r5", "si_r20", "gs_ratio_d20",
    "sig_equity_shock", "sig_flight", "sig_oil_shock", "sig_vol_jump",
]
BINARY = {"sig_equity_shock", "sig_flight", "sig_oil_shock", "sig_vol_jump"}

GROUPS = {
    "altın fiyat yapısı": ["g_r1", "g_r5", "g_r20", "g_r60", "g_vol20", "g_dd60", "g_dist200"],
    "faiz (reel ve nominal)": ["rr_d5", "rr_d20", "y2_d5", "y2_d20"],
    "dolar": ["usd_d20"],
    "altın oynaklığı": ["gvz_lvl", "gvz_d5"],
    "spekülatif pozisyon (COT)": ["cot_mm", "cot_mm_d4"],
    "makro veri sürprizi/takvim": ["cpi_surp", "cpi_days", "nfp_surp", "nfp_days", "fomc_since", "fomc_to", "last_react"],
    "hisse/tahvil/petrol/gümüş": ["nq_r5", "nq_r20", "zn_r5", "cl_r5", "cl_r20", "si_r5", "si_r20", "gs_ratio_d20"],
    "olay izi (şok)": ["sig_equity_shock", "sig_flight", "sig_oil_shock", "sig_vol_jump"],
}
LABEL_TR = {
    "g_r1": "altın 1g getiri", "g_r5": "altın 5g getiri", "g_r20": "altın 20g getiri", "g_r60": "altın 60g getiri",
    "g_vol20": "altın 20g oynaklık", "g_dd60": "60g zirveye uzaklık", "g_dist200": "200g ortalamaya uzaklık",
    "rr_d5": "10Y reel faiz 5g değişim", "rr_d20": "10Y reel faiz 20g değişim", "y2_d5": "2Y faiz 5g değişim",
    "y2_d20": "2Y faiz 20g değişim", "usd_d20": "dolar endeksi 20g değişim", "gvz_lvl": "GVZ düzeyi",
    "gvz_d5": "GVZ 5g değişim", "cot_mm": "COT managed money net", "cot_mm_d4": "COT MM 4 hafta değişim",
    "cpi_surp": "son CPI sürprizi", "cpi_days": "son CPI'dan beri gün", "nfp_surp": "son NFP sürprizi",
    "nfp_days": "son NFP'den beri gün", "fomc_since": "son FOMC'den beri gün", "fomc_to": "sonraki FOMC'ye gün",
    "last_react": "son makro yayına altın tepkisi", "nq_r5": "Nasdaq 5g", "nq_r20": "Nasdaq 20g",
    "zn_r5": "10Y tahvil vadeli 5g", "cl_r5": "petrol 5g", "cl_r20": "petrol 20g", "si_r5": "gümüş 5g",
    "si_r20": "gümüş 20g", "gs_ratio_d20": "altın/gümüş oranı 20g değişim", "sig_equity_shock": "hisse şoku",
    "sig_flight": "güvenli limana kaçış", "sig_oil_shock": "petrol şoku", "sig_vol_jump": "oynaklık sıçraması",
}


# Resmi FOMC açıklama zamanları (Fed'in önceden ilan ettiği takvim; 14:00 ET).
def _fomc():
    ds = ["2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
          "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
          "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
          "2026-01-28",
          # 2026 takvimi: federalreserve.gov/monetarypolicy/fomccalendars.htm (2026-10-17'de doğrulandı)
          "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09"]
    out = []
    for s in ds:
        d = date.fromisoformat(s)
        summer = date(d.year, 3, 8) <= d <= date(d.year, 11, 1)   # ABD yaz saati (yaklaşık; ±1 saat etkisizdir)
        out.append(datetime(d.year, d.month, d.day, 18 if summer else 19, tzinfo=timezone.utc))
    return out
FOMC_SCHEDULE = _fomc()


def _series(path, col="value", datecol="date"):
    out = []
    with open(path) as fh:
        for r in csv.DictReader(fh):
            v = r.get(col, "")
            try:
                x = float(v)
            except (TypeError, ValueError):
                continue
            if math.isfinite(x):
                out.append((date.fromisoformat(r[datecol][:10]), x))
    out.sort()
    return out


def _asof(series, cutoff):
    """cutoff tarihine eşit ya da önceki son değer (ikili arama)."""
    lo, hi = 0, len(series) - 1
    if hi < 0 or series[0][0] > cutoff:
        return None
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if series[mid][0] <= cutoff:
            lo = mid
        else:
            hi = mid - 1
    return series[lo][1]


def load_rows(dev_only=True):
    rows = []
    with open(PANEL) as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["date"])
            if dev_only and d > DEV_END:
                continue
            if r["open"] != "1":
                continue
            rec = dict(date=d, src=r["src"], p06=float(r["p06"]), bid=float(r["bid09"]), ask=float(r["ask09"]))
            for s in ("nq", "zn", "cl", "si"):
                rec[s] = float(r[s]) if r[s] else None
                rec[s + "_k"] = int(r[s + "_k"]) if r[s + "_k"] else None
            rows.append(rec)
    if dev_only:
        assert max(r["date"] for r in rows) <= DEV_END, "2026 verisi geliştirme modunda yüklenemez"
    return rows


def load_macro():
    rows = []
    with open(os.path.join(EVENTS, "GOLD_2023_2025_CPI_NFP_FOMC_M15_RELEASE_WEEKMATCH_EVENTSTUDY_20261014.csv")) as fh:
        for r in csv.DictReader(fh):
            if r["arm_week_lag"] != "0":
                continue
            ts = datetime.fromisoformat(r["scheduled_utc_or_placebo_utc"].replace("Z", "+00:00"))
            f = lambda k: float(r[k]) if r[k] not in ("", None) else None
            rows.append(dict(kind=r["kind"], ts=ts, surprise=f("macro_surprise"), post60=f("xau_logret_post60_pct"),
                             post240=f("xau_logret_post240_pct"), actual=f("macro_actual"), consensus=f("macro_consensus")))
    rows.sort(key=lambda x: x["ts"])
    return rows


def load_cot():
    out = []
    with open(os.path.join(ROOT, "GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv")) as fh:
        for r in csv.DictReader(fh):
            try:
                v = float(r["fut_mm_net"]); av = datetime.fromisoformat(r["cot_available_at_utc"])
            except (TypeError, ValueError):
                continue
            out.append((av, v))
    out.sort()
    return out


def build_states(rows):
    """Ham durum değişkenleri (standardize edilmemiş); her biri karar anında bilinir."""
    rr = _series(os.path.join(ROOT, "GOLD_EXECUTION_DFII10_FREE_CANDIDATE_2020_20261007.csv"))
    # 2026 uzatması: aynı seriler, GOLD_EXECUTION_*_FREE_CANDIDATE_2020_20261007.csv dosyalarından
    # YALNIZ 2025-12-31 sonrası günler eklenir; ortak günlerde iki kaynak birebir aynı
    # (DGS2 757/757, GVZ 1257/1257 gün, 2026-10-17'de doğrulandı). 2025 ve öncesi değişmez.
    y2 = _series(os.path.join(ROOT, "GOLD_DGS2_RAW_2022_2025.csv")) + [
        x for x in _series(os.path.join(ROOT, "GOLD_EXECUTION_DGS2_FREE_CANDIDATE_2020_20261007.csv"))
        if x[0] > date(2025, 12, 31)]
    gvz = _series(os.path.join(ROOT, "GOLD_GVZCLS_RAW_2021_2025.csv")) + [
        x for x in _series(os.path.join(ROOT, "GOLD_EXECUTION_GVZ_FREE_CANDIDATE_2020_20261007.csv"))
        if x[0] > date(2025, 12, 31)]
    usd = _series(DOLLAR, col="DTWEXBGS")
    cot = load_cot()
    macro = load_macro()
    P = [r["p06"] for r in rows]
    T = len(rows)
    # günlük zincirleme log getiri: ardışık iki karar gününde aynı sözleşme ve iki fiyat da varsa
    cdr = {}
    for s in ("nq", "zn", "cl", "si"):
        cdr[s] = [None] + [math.log(rows[i][s] / rows[i - 1][s])
                           if (rows[i][s] and rows[i - 1][s] and rows[i][s + "_k"] == rows[i - 1][s + "_k"]) else None
                           for i in range(1, T)]
    raw = []
    rr_v, y2_v, gvz_v, usd_v, cot_v = [], [], [], [], []
    for t, r in enumerate(rows):
        d = r["date"]; dt = datetime(d.year, d.month, d.day, 6, tzinfo=timezone.utc)
        f = {}
        lp = math.log(P[t])
        f["g_r1"] = 100 * (lp - math.log(P[t - 1])) if t >= 1 else None
        f["g_r5"] = 100 * (lp - math.log(P[t - 5])) if t >= 5 else None
        f["g_r20"] = 100 * (lp - math.log(P[t - 20])) if t >= 20 else None
        f["g_r60"] = 100 * (lp - math.log(P[t - 60])) if t >= 60 else None
        if t >= 21:
            rets = [100 * math.log(P[i] / P[i - 1]) for i in range(t - 19, t + 1)]
            f["g_vol20"] = float(np.std(rets))
        else:
            f["g_vol20"] = None
        f["g_dd60"] = 100 * (lp - math.log(max(P[t - 59:t + 1]))) if t >= 59 else None
        f["g_dist200"] = 100 * (lp - math.log(sum(P[t - 199:t + 1]) / 200)) if t >= 199 else None
        # faizler: değer tarihi <= 2 karar günü önce
        cut2 = rows[t - 2]["date"] if t >= 2 else None
        rr_v.append(_asof(rr, cut2) if cut2 else None); y2_v.append(_asof(y2, cut2) if cut2 else None)
        for name, vals in (("rr", rr_v), ("y2", y2_v)):
            for lag in (5, 20):
                a = vals[t]; b = vals[t - lag] if t >= lag else None
                f[f"{name}_d{lag}"] = (a - b) if (a is not None and b is not None) else None
        # dolar: değer tarihi <= karar tarihi − 10 takvim günü
        usd_v.append(_asof(usd, d - timedelta(days=10)))
        a, b = usd_v[t], (usd_v[t - 20] if t >= 20 else None)
        f["usd_d20"] = 100 * math.log(a / b) if (a and b) else None
        # GVZ: önceki karar günü kapanışı
        gvz_v.append(_asof(gvz, rows[t - 1]["date"]) if t >= 1 else None)
        f["gvz_lvl"] = gvz_v[t]
        f["gvz_d5"] = (gvz_v[t] - gvz_v[t - 5]) if (t >= 5 and gvz_v[t] is not None and gvz_v[t - 5] is not None) else None
        # COT: yayın anı < karar anı
        avail = [v for (av, v) in cot if av < dt]
        f["cot_mm"] = avail[-1] if avail else None
        f["cot_mm_d4"] = (avail[-1] - avail[-5]) if len(avail) >= 5 else None
        # makro: yayın + 240 dk <= karar anı
        known = [m for m in macro if m["ts"] + timedelta(minutes=240) <= dt]
        for kind, key in (("CPI", "cpi"), ("NFP", "nfp")):
            ks = [m for m in known if m["kind"] == kind and m["surprise"] is not None]
            if len(ks) >= 6:
                sd = float(np.std([m["surprise"] for m in ks[:-1]])) or 1.0
                f[f"{key}_surp"] = ks[-1]["surprise"] / sd
            else:
                f[f"{key}_surp"] = None
            f[f"{key}_days"] = min(45.0, (dt - ks[-1]["ts"]).total_seconds() / 86400) if ks else None
        # FOMC: resmi, önceden ilan edilmiş toplantı takvimi (karar anında bilinir)
        past = [x for x in FOMC_SCHEDULE if x + timedelta(minutes=240) <= dt]
        fut = [x for x in FOMC_SCHEDULE if x > dt]
        f["fomc_since"] = min(60.0, (dt - past[-1]).total_seconds() / 86400) if past else None
        f["fomc_to"] = min(60.0, (fut[0] - dt).total_seconds() / 86400) if fut else None
        f["last_react"] = known[-1]["post240"] if known and known[-1]["post240"] is not None else None
        # piyasalar arası: vade geçişlerini atlayan zincirleme getiri (gün içi aynı sözleşme)
        def cret(s, lag):
            if t < lag: return None
            v = [cdr[s][i] for i in range(t - lag + 1, t + 1)]
            ok = [x for x in v if x is not None]
            return 100 * sum(ok) if len(ok) >= 0.6 * lag else None
        f["nq_r5"], f["nq_r20"], f["zn_r5"] = cret("nq", 5), cret("nq", 20), cret("zn", 5)
        f["cl_r5"], f["cl_r20"], f["si_r5"], f["si_r20"] = cret("cl", 5), cret("cl", 20), cret("si", 5), cret("si", 20)
        si20 = cret("si", 20)
        f["gs_ratio_d20"] = (f["g_r20"] - si20) if (si20 is not None and f["g_r20"] is not None) else None
        raw.append(f)
    return raw, macro


class Standardizer:
    def __init__(self):
        self.n = {k: 0 for k in FEATURES}; self.m = {k: 0.0 for k in FEATURES}; self.q = {k: 0.0 for k in FEATURES}

    def z(self, k, v):
        if k in BINARY:
            return float(v or 0.0)
        if v is None or self.n[k] < MIN_HIST:
            return 0.0
        sd = math.sqrt(self.q[k] / (self.n[k] - 1))
        return 0.0 if sd <= 0 else max(-ZCLIP, min(ZCLIP, (v - self.m[k]) / sd))

    def add(self, k, v):
        if k in BINARY or v is None:
            return
        self.n[k] += 1; d = v - self.m[k]; self.m[k] += d / self.n[k]; self.q[k] += d * (v - self.m[k])

    def state(self):
        return dict(n=dict(self.n), m=dict(self.m), q=dict(self.q))


def standardize(raw):
    """Genişleyen pencere; t gününün z'si yalnız t'den önceki günlerin istatistiğiyle."""
    st = Standardizer(); Z = []
    for f in raw:
        z = {}
        for k in FEATURES:
            if k in BINARY:
                continue
            z[k] = st.z(k, f.get(k))
        # olay izleri: standart değerlerden türetilir
        z["sig_equity_shock"] = 1.0 if z["nq_r5"] < -2 else 0.0
        z["sig_flight"] = 1.0 if (z["zn_r5"] > 1 and z["nq_r5"] < -1) else 0.0
        z["sig_oil_shock"] = 1.0 if z["cl_r5"] > 2 else 0.0
        z["sig_vol_jump"] = 1.0 if z["gvz_d5"] > 2 else 0.0
        Z.append(np.array([z[k] for k in FEATURES]))
        for k in FEATURES:
            st.add(k, f.get(k))
    return np.array(Z), st
