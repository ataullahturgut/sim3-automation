from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "SESSION_BOCPD_V1_STAGE2_OUT"
OUT.mkdir(exist_ok=True)

PREREG = AX / "GOLD_SESSION_BOCPD_V1_STAGE2_PREREG_2026-10-07.md"
RIFT_PATH = AX / "tools" / "gold_session_rift_v1_20261007.py"
INC_PATH = AX / "tools" / "gold_session_incremental_disagreement_v1_20261007.py"
BASE_AUTH = AX / "GOLD_SESSION_INCREMENTAL_DISAGREEMENT_V1_BASES_2026-10-07.csv"

ROLL_FILES = {
    "c": AX / "GOLD_DATABENTO_GLBX_OHLCV1H_C_RAW_2022_2024.csv.gz",
    "n": AX / "GOLD_DATABENTO_GLBX_OHLCV1H_N_RAW_2022_2024.csv.gz",
    "v": AX / "GOLD_DATABENTO_GLBX_OHLCV1H_V_RAW_2022_2024.csv.gz",
}

VARIANTS = {
    "BASE": {"GC":"v","SI":"v","NQ":"v","ZN":"n","CL":"c"},
    "SI_n": {"GC":"v","SI":"n","NQ":"v","ZN":"n","CL":"c"},
    "NQ_n": {"GC":"v","SI":"v","NQ":"n","ZN":"n","CL":"c"},
    "ZN_v": {"GC":"v","SI":"v","NQ":"v","ZN":"v","CL":"c"},
    "CL_v": {"GC":"v","SI":"v","NQ":"v","ZN":"n","CL":"v"},
    "GC_n": {"GC":"n","SI":"v","NQ":"v","ZN":"n","CL":"c"},
    "NQ_c": {"GC":"v","SI":"v","NQ":"c","ZN":"n","CL":"c"},
}

EXPECTED_RUN = 4
A0 = B0 = 0.5
PRED_THRESHOLD = 0.60
P_GT_HALF_THRESHOLD = 0.80

CAL_N = 120
MIN_CAL = 60
RANK_WINDOW = 120
RANK_MIN = 20
WINDOW_DAYS = 60
MIN_TRAIN = 500
RIDGE_ALPHA = 10.0
EPS = 1e-8
NY = ZoneInfo("America/New_York")

EXT_FEATURES = [
    "ZN_r1","ZN_r3","ZN_r6",
    "NQ_r1","NQ_r3","NQ_r6",
    "SI_r1","SI_r3","SI_r6",
    "CL_r1","CL_r3","CL_r6",
]
GC_FEATURES = ["GC_r1","GC_r3","GC_r6"]


def loadmod(name: str, path: Path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    assert s.loader is not None
    s.loader.exec_module(m)
    return m


rift = loadmod("session_rift_for_bocpd", RIFT_PATH)
inc = loadmod("session_incremental_for_bocpd", INC_PATH)


def rank_val(hist, val, min_n):
    a = pd.to_numeric(pd.Series(hist), errors="coerce").to_numpy(float)
    a = a[np.isfinite(a)]
    if len(a) < min_n or not np.isfinite(val):
        return np.nan
    return float((1 + np.sum(a <= val)) / (len(a) + 1))


def rolling_rank(values, sign=1.0, window=RANK_WINDOW, min_n=RANK_MIN):
    x = pd.to_numeric(pd.Series(values), errors="coerce").to_numpy(float) * sign
    out = np.full(len(x), np.nan)
    for i in range(len(x)):
        h = x[max(0, i-window):i]
        h = h[np.isfinite(h)]
        if len(h) < min_n or not np.isfinite(x[i]):
            continue
        out[i] = float((1 + np.sum(h <= x[i])) / (len(h) + 1))
    return out


def med(df, cols):
    return np.nanmedian(df[cols].to_numpy(float), axis=1)


def efficiency(ret):
    den = float(np.abs(ret).sum())
    return 0.0 if den <= 1e-12 else float(abs(ret.sum()) / den)


def vol_flow(ret, vol, sign):
    den = float(vol.sum())
    return 0.0 if den <= 0 else float(sign * np.sum(ret * vol) / den)


def opp_share(ret, vol, sign):
    den = float(vol.sum())
    if den <= 0:
        return 0.0
    return float(vol[(sign * ret) < 0].sum() / den)


def load_archives():
    out = {}
    for roll, path in ROLL_FILES.items():
        q = pd.read_csv(path, compression="gzip")
        q["ts_event"] = pd.to_datetime(q.ts_event, utc=True, errors="raise")
        q["symbol"] = q.symbol.astype(str)
        for c in ["close","volume"]:
            q[c] = pd.to_numeric(q[c], errors="raise")
        q["available_at_utc"] = q.ts_event + pd.Timedelta(hours=1)
        out[roll] = q[["ts_event","available_at_utc","symbol","close","volume"]].copy()
    return out


def symbol_frame(archives, root, roll):
    sym = f"{root}.{roll}.0"
    q = archives[roll][archives[roll].symbol.eq(sym)][
        ["ts_event","available_at_utc","close","volume"]
    ].copy()
    if q.empty:
        raise RuntimeError(f"MISSING_SYMBOL:{sym}")
    q = q.sort_values("ts_event").drop_duplicates("ts_event", keep="last")
    return q


def xau_hourly_from_raw15():
    q = rift.load_raw15().copy()
    q["hour"] = q.ts.dt.floor("1h")
    q["minute"] = q.ts.dt.minute
    rows = []
    for h, g in q.groupby("hour", sort=True):
        mins = tuple(sorted(set(map(int, g.minute))))
        if len(g) == 4 and mins == (0,15,30,45):
            rows.append({
                "ts": pd.Timestamp(h),
                "available_at_utc": pd.Timestamp(h) + pd.Timedelta(hours=1),
                "value": float(g.sort_values("ts").iloc[-1].value),
            })
    return pd.DataFrame(rows).sort_values("available_at_utc").reset_index(drop=True)


def attach_session_against_trend(panel):
    h = xau_hourly_from_raw15()
    h["logp"] = np.log(h.value.astype(float))
    h["ny_date"] = h.available_at_utc.dt.tz_convert("America/New_York").dt.date

    vals = []
    for r in panel.itertuples(index=False):
        T = pd.Timestamp(r.start_utc)
        q = h[h.available_at_utc < T]
        if q.empty:
            vals.append(np.nan)
            continue
        target_date = T.tz_convert("America/New_York").date()
        d = q[q.ny_date == target_date]
        if d.empty:
            vals.append(np.nan)
            continue
        session_ret = float(d.iloc[-1].logp - d.iloc[0].logp)
        sign = 1.0 if float(r.g_ret_12h) >= 0 else -1.0
        vals.append(float(-sign * session_ret / (float(r.g_rv_12) + EPS)))

    z = panel.copy()
    z["session_against_trend"] = vals
    return z


def build_path_panel():
    p = rift.build_panel().copy()
    p = attach_session_against_trend(p)
    need = [
        "trend_strength","session_against_trend","trend_close_location",
        "adverse_excursion","momentum_up","start_utc","end_utc","y_up",
    ]
    p = p.dropna(subset=need).copy()
    p["start_utc"] = pd.to_datetime(p.start_utc, utc=True)
    p["end_utc"] = pd.to_datetime(p.end_utc, utc=True)
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True)


def build_ifbc_raw(panel, archives, mapping):
    gc = symbol_frame(archives, "GC", mapping["GC"]).rename(
        columns={"close":"GC_close","volume":"GC_volume","available_at_utc":"GC_avail"}
    )
    si = symbol_frame(archives, "SI", mapping["SI"]).rename(
        columns={"close":"SI_close","volume":"SI_volume","available_at_utc":"SI_avail"}
    )
    x = gc[["ts_event","GC_avail","GC_close","GC_volume"]].merge(
        si[["ts_event","SI_avail","SI_close","SI_volume"]],
        on="ts_event", how="inner", validate="one_to_one"
    ).sort_values("ts_event").reset_index(drop=True)
    x["available_at_utc"] = x[["GC_avail","SI_avail"]].max(axis=1)
    x["GC_ret1"] = np.log(x.GC_close).diff()
    x["SI_ret1"] = np.log(x.SI_close).diff()

    rows = []
    keep_path = [
        "partition","window","label_date","start_utc","end_utc","year","y_up",
        "momentum_up","trend_strength","session_against_trend",
        "trend_close_location","adverse_excursion"
    ]
    for r in panel[keep_path].itertuples(index=False):
        T = pd.Timestamp(r.start_utc)
        w = x[
            (x.available_at_utc < T) &
            (x.available_at_utc >= T - pd.Timedelta(hours=18))
        ].tail(12).copy()
        if len(w) < 12:
            continue
        stale = (T - w.available_at_utc.iloc[-1]).total_seconds() / 3600.0
        span = (w.available_at_utc.iloc[-1] - w.available_at_utc.iloc[0]).total_seconds() / 3600.0
        if not (0 < stale <= 3.0) or span > 18.0:
            continue
        if w[["GC_ret1","SI_ret1"]].isna().any(axis=None):
            continue

        s = 1.0 if int(r.momentum_up) == 1 else -1.0
        d = r._asdict()
        for hh in [3,6,12]:
            z = w.tail(hh)
            d[f"gc_flow_{hh}"] = vol_flow(z.GC_ret1.to_numpy(float), z.GC_volume.to_numpy(float), s)
            d[f"gc_opp_vol_share_{hh}"] = opp_share(z.GC_ret1.to_numpy(float), z.GC_volume.to_numpy(float), s)
        for hh in [6,12]:
            z = w.tail(hh)
            d[f"gc_efficiency_{hh}"] = efficiency(z.GC_ret1.to_numpy(float))
            d[f"si_flow_{hh}"] = vol_flow(z.SI_ret1.to_numpy(float), z.SI_volume.to_numpy(float), s)
            d[f"si_opp_vol_share_{hh}"] = opp_share(z.SI_ret1.to_numpy(float), z.SI_volume.to_numpy(float), s)
        d["gc_si_flow_gap12"] = float(d["gc_flow_12"] - d["si_flow_12"])
        d["joint_opposition_share12"] = float((d["gc_opp_vol_share_12"] + d["si_opp_vol_share_12"]) / 2)
        d["cross_last_available_utc"] = w.available_at_utc.iloc[-1]
        rows.append(d)
    return pd.DataFrame(rows)


def apply_ifbc_calibration(raw):
    outs = []
    for (part, win), g0 in raw.groupby(["partition","window"], sort=True):
        g = g0.sort_values("start_utc").reset_index(drop=True).copy()
        g["x1"] = g.gc_opp_vol_share_12
        g["x2"] = -g.gc_flow_12
        g["x3"] = -g.si_flow_12
        g["x4"] = g.joint_opposition_share12
        g["x5"] = g.gc_si_flow_gap12
        g["x6"] = 1 - g.gc_efficiency_12
        rows = []
        for i, r in g.iterrows():
            hist = g.iloc[max(0, i-CAL_N):i]
            ranks = [rank_val(hist[f"x{k}"], r[f"x{k}"], MIN_CAL) for k in range(1,7)]
            if any(not np.isfinite(v) for v in ranks):
                continue
            d = r.to_dict()
            d["ifbc_score"] = float(np.median(ranks))
            rows.append(d)
        if rows:
            outs.append(pd.DataFrame(rows))
    return pd.concat(outs, ignore_index=True) if outs else pd.DataFrame()


def sync_hourly(archives, mapping):
    out = None
    for root in ["GC","SI","NQ","ZN","CL"]:
        q = symbol_frame(archives, root, mapping[root])[["ts_event","close"]].rename(columns={"close":root})
        out = q if out is None else out.merge(q, on="ts_event", how="inner", validate="one_to_one")
    x = out.sort_values("ts_event").reset_index(drop=True)
    x["available_at_utc"] = x.ts_event + pd.Timedelta(hours=1)
    for root in ["GC","SI","NQ","ZN","CL"]:
        lv = np.log(pd.to_numeric(x[root], errors="coerce"))
        for hh in [1,3,6]:
            x[f"{root}_r{hh}"] = lv - lv.shift(hh)
    x["target_ts_6h"] = x.ts_event.shift(-6)
    x["target_available_6h"] = x.target_ts_6h + pd.Timedelta(hours=1)
    x["GC_fwd6"] = np.log(x.GC.shift(-6)) - np.log(x.GC)
    wall = (x.target_ts_6h - x.ts_event).dt.total_seconds() / 3600.0
    x.loc[(wall < 5) | (wall > 8.5), "GC_fwd6"] = np.nan
    return x


def ridge():
    return Pipeline([
        ("scale", StandardScaler()),
        ("ridge", Ridge(alpha=RIDGE_ALPHA)),
    ])


def build_llrs(panel, hourly):
    ready = hourly.dropna(subset=EXT_FEATURES + GC_FEATURES + ["GC_fwd6","target_available_6h"]).copy()
    rows = []
    cols = ["partition","window","label_date","start_utc","end_utc","year","y_up","momentum_up"]
    for r in panel[cols].itertuples(index=False):
        T = pd.Timestamp(r.start_utc)
        hist = ready[
            (ready.available_at_utc >= T - pd.Timedelta(days=WINDOW_DAYS)) &
            (ready.target_available_6h < T)
        ].copy()
        if len(hist) < MIN_TRAIN:
            continue
        cur = hourly[hourly.available_at_utc < T].tail(1).copy()
        if cur.empty or cur[EXT_FEATURES + GC_FEATURES].isna().any(axis=None):
            continue
        stale = (T - cur.available_at_utc.iloc[0]).total_seconds() / 3600.0
        if not (0 < stale <= 3.0):
            continue

        y = hist.GC_fwd6.to_numpy(float)
        me, mg = ridge(), ridge()
        me.fit(hist[EXT_FEATURES].to_numpy(float), y)
        mg.fit(hist[GC_FEATURES].to_numpy(float), y)
        pe = float(me.predict(cur[EXT_FEATURES].to_numpy(float))[0])
        pg = float(mg.predict(cur[GC_FEATURES].to_numpy(float))[0])
        sigma = float(np.std(y - me.predict(hist[EXT_FEATURES].to_numpy(float)), ddof=1))
        if not np.isfinite(sigma) or sigma <= 1e-9:
            continue

        s = 1.0 if int(r.momentum_up) == 1 else -1.0
        rows.append({
            **r._asdict(),
            "llrs_pressure": float(-s * pe / sigma),
            "llrs_incremental": float(-s * (pe - pg) / sigma),
            "llrs_external_opposes": bool(s * pe < 0),
            "hourly_source_available_utc": cur.available_at_utc.iloc[0],
            "hourly_train_n": int(len(hist)),
        })
    return pd.DataFrame(rows)


def build_handoff_state(ifbc, llrs):
    outs = []
    keys = ["partition","window","start_utc"]
    z = ifbc.merge(
        llrs[keys + ["llrs_pressure","llrs_incremental","llrs_external_opposes","hourly_source_available_utc","hourly_train_n"]],
        on=keys, how="inner", validate="one_to_one"
    )

    for (part, win), g0 in z.groupby(["partition","window"], sort=True):
        g = g0.sort_values("start_utc").reset_index(drop=True).copy()
        mom = np.where(g.momentum_up.astype(int).to_numpy() == 1, 1.0, -1.0)
        g["gc_flow_against_mom"] = -mom * g.gc_flow_12.to_numpy(float)
        g["si_flow_against_mom"] = -mom * g.si_flow_12.to_numpy(float)

        specs = {
            "r_frag_trend": ("trend_strength", -1.0),
            "r_frag_session": ("session_against_trend", 1.0),
            "r_frag_close": ("trend_close_location", -1.0),
            "r_frag_adverse": ("adverse_excursion", 1.0),
            "r_flow_gc_oppvol": ("gc_opp_vol_share_12", 1.0),
            "r_flow_si_oppvol": ("si_opp_vol_share_12", 1.0),
            "r_flow_joint": ("joint_opposition_share12", 1.0),
            "r_flow_gc_against": ("gc_flow_against_mom", 1.0),
            "r_flow_si_against": ("si_flow_against_mom", 1.0),
            "r_flow_ineff": ("gc_efficiency_12", -1.0),
        }
        for out, (col, sgn) in specs.items():
            g[out] = rolling_rank(g[col], sgn)

        g["fragility_score"] = med(g, ["r_frag_trend","r_frag_session","r_frag_close","r_frag_adverse"])
        g["flow_score"] = med(g, ["r_flow_gc_oppvol","r_flow_si_oppvol","r_flow_joint","r_flow_gc_against","r_flow_si_against","r_flow_ineff"])

        g["r_llrs_pressure"] = rolling_rank(g.llrs_pressure, 1.0)
        g["r_llrs_incremental"] = rolling_rank(g.llrs_incremental, 1.0)
        g["llrs_strict"] = (
            g.llrs_external_opposes.astype(bool) &
            (pd.to_numeric(g.llrs_pressure, errors="coerce") > 0) &
            (pd.to_numeric(g.llrs_incremental, errors="coerce") > 0)
        )
        g["leadlag_score"] = med(g, ["r_llrs_pressure","r_llrs_incremental"])
        g.loc[~g.llrs_strict, "leadlag_score"] = 0.0

        for c in ["fragility_score","flow_score","leadlag_score"]:
            g[f"{c}_lag1"] = g[c].shift(1)
            g[f"{c}_lag2"] = g[c].shift(2)
        g["leadlag_score_premax"] = g[["leadlag_score_lag1","leadlag_score_lag2"]].max(axis=1)
        g["internal_now"] = g[["fragility_score","flow_score"]].max(axis=1)
        g["internal_lag1"] = g[["fragility_score_lag1","flow_score_lag1"]].max(axis=1)
        g["internal_d1"] = g.internal_now - g.internal_lag1
        outs.append(g)

    return pd.concat(outs, ignore_index=True) if outs else pd.DataFrame()


class BetaBernoulliBOCPD:
    def __init__(self):
        self.h = 1.0 / EXPECTED_RUN
        self.r = np.array([1.0], float)
        self.a = np.array([A0], float)
        self.b = np.array([B0], float)
        self.n_updates = 0

    def predictive(self):
        means = self.a / (self.a + self.b)
        p = float(np.dot(self.r, means))
        pgt = np.array([1.0 - beta_dist.cdf(0.5, aa, bb) for aa, bb in zip(self.a, self.b)], float)
        return {
            "p_rescue": p,
            "p_theta_gt_half": float(np.dot(self.r, pgt)),
            "map_run": int(np.argmax(self.r)),
            "n_updates": int(self.n_updates),
        }

    def update(self, y):
        y = int(y)
        means = self.a / (self.a + self.b)
        like = means if y == 1 else (1.0 - means)
        prior_like = 0.5
        new = np.zeros(len(self.r) + 1, float)
        new[0] = self.h * prior_like * float(self.r.sum())
        new[1:] = (1.0 - self.h) * self.r * like
        ev = float(new.sum())
        if not np.isfinite(ev) or ev <= 0:
            raise RuntimeError("BOCPD_INVALID_EVIDENCE")
        new /= ev

        na = np.empty(len(self.a) + 1, float)
        nb = np.empty(len(self.b) + 1, float)
        na[0] = A0 + y
        nb[0] = B0 + (1-y)
        na[1:] = self.a + y
        nb[1:] = self.b + (1-y)
        self.r, self.a, self.b = new, na, nb
        self.n_updates += 1


def metric(y, p):
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    d = (p >= 0.5).astype(int)
    tp = int(((y==1)&(d==1)).sum())
    tn = int(((y==0)&(d==0)).sum())
    fp = int(((y==0)&(d==1)).sum())
    fn = int(((y==1)&(d==0)).sum())
    up = tp / max(tp+fn, 1)
    dn = tn / max(tn+fp, 1)
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(d==y)) if len(y) else np.nan,
        "balanced_accuracy": float((up+dn)/2),
        "up_recall": float(up),
        "down_recall": float(dn),
        "brier": float(np.mean((p-y)**2)) if len(y) else np.nan,
    }


def load_frozen_bases():
    long, _ = inc.load_models()
    nm = inc.native_metrics(long)
    bases = inc.select_bases(nm)

    auth = pd.read_csv(BASE_AUTH)
    k = ["partition","window"]
    chk = bases[k+["base_model"]].merge(
        auth[k+["base_model"]],
        on=k, suffixes=("_new","_auth"), validate="one_to_one"
    )
    if len(chk) != len(auth) or not chk.base_model_new.eq(chk.base_model_auth).all():
        raise RuntimeError("FROZEN_BASE_SELECTION_MISMATCH")

    rows = []
    for b in auth.itertuples(index=False):
        q = long[
            long.partition.eq(b.partition) &
            long.window.eq(b.window) &
            long.model.eq(b.base_model)
        ].copy()
        q["base_model"] = b.base_model
        rows.append(q)
    out = pd.concat(rows, ignore_index=True)
    out["start_utc"] = pd.to_datetime(out.start_utc, utc=True)
    out["end_utc"] = pd.to_datetime(out.end_utc, utc=True)
    return out.sort_values(["partition","window","start_utc"]).reset_index(drop=True), auth


def replay_one_source(base_rows, state, source_variant):
    z = base_rows.merge(
        state[[
            "partition","window","start_utc","momentum_up",
            "leadlag_score_premax","internal_now","internal_d1",
            "fragility_score","flow_score","leadlag_score",
            "cross_last_available_utc","hourly_source_available_utc"
        ]],
        on=["partition","window","start_utc"],
        how="inner", validate="one_to_one"
    )
    z = z[z.start_utc.dt.year.isin([2023,2024])].copy()
    z["baseline_pred"] = (z.p_up >= 0.5).astype(int)
    z["baseline_correct"] = z.baseline_pred.eq(z.y_up.astype(int))
    z["handoff_alarm"] = (
        (pd.to_numeric(z.leadlag_score_premax, errors="coerce") >= 0.60) &
        (pd.to_numeric(z.internal_now, errors="coerce") >= 0.60) &
        (pd.to_numeric(z.internal_d1, errors="coerce") >= 0.0) &
        z.baseline_pred.eq(z.momentum_up.astype(int))
    )
    z["competence_y"] = (~z.baseline_correct).astype(int)
    z["act"] = False
    z["p_rescue_pre"] = np.nan
    z["p_theta_gt_half_pre"] = np.nan
    z["bocpd_updates_pre"] = np.nan

    action_rows = []

    for (part, win), idx in z.groupby(["partition","window"], sort=True).groups.items():
        ids = list(idx)
        ids.sort(key=lambda j: z.loc[j, "start_utc"])
        model = BetaBernoulliBOCPD()
        pending = []

        for j in ids:
            row = z.loc[j]
            T = pd.Timestamp(row.start_utc)
            matured = [p for p in pending if p["maturity"] <= T]
            pending = [p for p in pending if p["maturity"] > T]
            matured.sort(key=lambda x: (x["maturity"], x["origin"]))
            for p in matured:
                model.update(p["y"])

            if not bool(row.handoff_alarm):
                continue

            pre = model.predictive()
            act = bool(
                pre["p_rescue"] >= PRED_THRESHOLD and
                pre["p_theta_gt_half"] >= P_GT_HALF_THRESHOLD
            )
            z.at[j, "act"] = act
            z.at[j, "p_rescue_pre"] = pre["p_rescue"]
            z.at[j, "p_theta_gt_half_pre"] = pre["p_theta_gt_half"]
            z.at[j, "bocpd_updates_pre"] = pre["n_updates"]

            pending.append({
                "maturity": pd.Timestamp(row.end_utc),
                "origin": T,
                "y": int(row.competence_y),
            })

            if act:
                action_rows.append({
                    "source_variant": source_variant,
                    "partition": part,
                    "window": win,
                    "base_model": row.base_model,
                    "start_utc": T,
                    "end_utc": pd.Timestamp(row.end_utc),
                    "year": int(T.year),
                    "y_up": int(row.y_up),
                    "baseline_pred": int(row.baseline_pred),
                    "momentum_up": int(row.momentum_up),
                    "outcome": "RESCUE" if int(row.competence_y)==1 else "BROKEN",
                    **pre,
                })

    z["p_assisted"] = z.p_up.astype(float)
    z.loc[z.act, "p_assisted"] = 1.0 - z.loc[z.act, "p_up"].astype(float)

    metrics_rows = []
    for (part, win), g in z.groupby(["partition","window"], sort=True):
        for period, q in [
            ("2023", g[g.start_utc.dt.year.eq(2023)]),
            ("2024", g[g.start_utc.dt.year.eq(2024)]),
            ("2023-2024", g),
        ]:
            if q.empty:
                continue
            mb = metric(q.y_up, q.p_up)
            ma = metric(q.y_up, q.p_assisted)
            acted = q[q.act].copy()
            rescue = int((~acted.baseline_correct).sum())
            broken = int(acted.baseline_correct.sum())
            first_act = acted.start_utc.min().isoformat() if not acted.empty else None
            metrics_rows.append({
                "source_variant": source_variant,
                "partition": part,
                "window": win,
                "base_model": q.base_model.iloc[0],
                "period": period,
                "eligible_n": int(len(q)),
                "handoff_alarms": int(q.handoff_alarm.sum()),
                "acts": int(q.act.sum()),
                "rescue": rescue,
                "broken": broken,
                "net_rescue": rescue-broken,
                "action_precision": float(rescue/max(len(acted),1)),
                "first_act": first_act,
                **{f"base_{k}":v for k,v in mb.items()},
                **{f"assisted_{k}":v for k,v in ma.items()},
            })

    return z, pd.DataFrame(metrics_rows), pd.DataFrame(action_rows)


def build_gate(metrics):
    base = metrics[metrics.source_variant.eq("BASE")].copy()
    combined = base[base.period.eq("2023-2024")].copy()
    out = []

    for r in combined.itertuples(index=False):
        g = base[(base.partition.eq(r.partition)) & (base.window.eq(r.window))]
        years = {x.period:x for x in g.itertuples(index=False) if x.period in ["2023","2024"]}

        base_gate = bool(
            int(r.acts) >= 1 and
            int(r.net_rescue) > 0 and
            float(r.assisted_balanced_accuracy) + 1e-12 >= float(r.base_balanced_accuracy)
        )
        year_ok = True
        for yr in ["2023","2024"]:
            if yr in years:
                yy = years[yr]
                if float(yy.assisted_accuracy) + 0.01 + 1e-12 < float(yy.base_accuracy):
                    year_ok = False

        nets = {}
        missing = []
        for v in VARIANTS:
            q = metrics[
                metrics.source_variant.eq(v) &
                metrics.partition.eq(r.partition) &
                metrics.window.eq(r.window) &
                metrics.period.eq("2023-2024")
            ]
            if q.empty:
                missing.append(v)
            else:
                nets[v] = int(q.iloc[0].net_rescue)

        any_negative = any(v < 0 for k,v in nets.items() if k != "BASE")
        any_zero = any(v == 0 for k,v in nets.items() if k != "BASE")
        source_ok = (not missing) and (not any_negative)

        eligible = bool(base_gate and year_ok and source_ok)
        if missing:
            status = "SOURCE_MISSING_FAIL"
        elif any_negative:
            status = "SOURCE_SENSITIVE_FAIL"
        elif not base_gate or not year_ok:
            status = "DEVELOPMENT_GATE_FAIL"
        elif any_zero:
            status = "PASS_SOURCE_WEAK"
        else:
            status = "PASS_SOURCE_ROBUST"

        out.append({
            "partition": r.partition,
            "window": r.window,
            "base_model": r.base_model,
            "base_eligible_n": int(r.eligible_n),
            "base_handoff_alarms": int(r.handoff_alarms),
            "base_acts": int(r.acts),
            "base_rescue": int(r.rescue),
            "base_broken": int(r.broken),
            "base_net": int(r.net_rescue),
            "base_ba": float(r.base_balanced_accuracy),
            "assisted_ba": float(r.assisted_balanced_accuracy),
            "year_accuracy_gate": bool(year_ok),
            "source_nets_json": json.dumps(nets, sort_keys=True),
            "transport_eligible": eligible,
            "status": status,
        })
    return pd.DataFrame(out)


def main():
    if "PREREGISTERED BEFORE 2023–2024 SESSION RESULTS" not in PREREG.read_text():
        raise RuntimeError("BOCPD_STAGE2_PREREG_MISSING")

    path_panel = build_path_panel()
    base_rows, base_auth = load_frozen_bases()
    archives = load_archives()

    ifbc_cache = {}
    state_by_variant = {}
    all_metrics = []
    all_actions = []

    for vname, mapping in VARIANTS.items():
        ikey = (mapping["GC"], mapping["SI"])
        if ikey not in ifbc_cache:
            raw_ifbc = build_ifbc_raw(path_panel, archives, mapping)
            ifbc_cache[ikey] = apply_ifbc_calibration(raw_ifbc)

        hourly = sync_hourly(archives, mapping)
        llrs = build_llrs(path_panel, hourly)
        state = build_handoff_state(ifbc_cache[ikey], llrs)
        state_by_variant[vname] = state

        _, mdf, adf = replay_one_source(base_rows, state, vname)
        if not mdf.empty:
            all_metrics.append(mdf)
        if not adf.empty:
            all_actions.append(adf)

    metrics = pd.concat(all_metrics, ignore_index=True) if all_metrics else pd.DataFrame()
    actions = pd.concat(all_actions, ignore_index=True) if all_actions else pd.DataFrame()

    if metrics.empty:
        raise RuntimeError("NO_BOCPD_STAGE2_METRICS")

    gate = build_gate(metrics)

    sens_rows = []
    for r in gate.itertuples(index=False):
        nets = json.loads(r.source_nets_json)
        vals = [nets.get(v) for v in VARIANTS if v in nets]
        sens_rows.append({
            "partition": r.partition,
            "window": r.window,
            "base_model": r.base_model,
            **{f"net_{v}": nets.get(v) for v in VARIANTS},
            "min_net": min(vals) if vals else None,
            "max_net": max(vals) if vals else None,
            "median_net": float(np.median(vals)) if vals else None,
            "negative_variants": int(sum(v < 0 for v in vals)),
            "zero_variants": int(sum(v == 0 for v in vals)),
            "status": r.status,
            "transport_eligible": bool(r.transport_eligible),
        })
    sensitivity = pd.DataFrame(sens_rows)

    metrics.to_csv(OUT / "metrics.csv", index=False)
    actions.to_csv(OUT / "actions.csv", index=False)
    gate.to_csv(OUT / "gate.csv", index=False)
    sensitivity.to_csv(OUT / "source_sensitivity.csv", index=False)

    summary = {
        "status": "SESSION_BOCPD_V1_STAGE2_COMPLETE",
        "scope": "2022 source/rank warmup only; 2023-2024 development scored; 2025/2026 not read",
        "identity": {
            "expected_run": EXPECTED_RUN,
            "prior": [A0,B0],
            "p_rescue_min": PRED_THRESHOLD,
            "p_theta_gt_half_min": P_GT_HALF_THRESHOLD,
            "hysteresis_v4_used": False,
        },
        "source_variants": VARIANTS,
        "base_selection": base_auth.to_dict("records"),
        "transport_eligible": gate[gate.transport_eligible].to_dict("records"),
        "gate": gate.to_dict("records"),
        "guardrails": [
            "Frozen preregistration existed before Stage-2 result.",
            "No 2025 or 2026 target outcome is loaded.",
            "BOCPD posterior state is independent by partition/window.",
            "Only matured prior Handoff outcomes update the posterior.",
            "Cross-market raw bars are available only after their hourly bar completes and exact-boundary equality is rejected.",
            "No source mapping is selected from BOCPD performance.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    base_comb = metrics[
        metrics.source_variant.eq("BASE") & metrics.period.eq("2023-2024")
    ].sort_values(["partition","window"])

    lines = [
        "# GOLD SESSION — BOCPD V1 STAGE-2 RESULT",
        "",
        "**Status:** SESSION_BOCPD_V1_STAGE2_COMPLETE",
        "",
        "- 2022: source/rank warm-up only.",
        "- 2023–2024: development scoring.",
        "- 2025/2026: not read.",
        "- BOCPD V1 only; V4 hysteresis not used.",
        "",
        "## Canonical BASE mapping — combined 2023–2024",
        "",
        "| Partition | Window | Base | N | Handoff | ACT | R/B/Net | Precision | Base BA | Assisted BA | Base Acc | Assisted Acc | Gate |",
        "|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|",
    ]

    gate_map = {(r.partition,r.window):r for r in gate.itertuples(index=False)}
    for r in base_comb.itertuples(index=False):
        gg = gate_map[(r.partition,r.window)]
        lines.append(
            f"| {r.partition} | {r.window} | {r.base_model} | {r.eligible_n} | "
            f"{r.handoff_alarms} | {r.acts} | {r.rescue}/{r.broken}/{r.net_rescue:+d} | "
            f"{100*r.action_precision:.1f}% | {100*r.base_balanced_accuracy:.2f}% | "
            f"{100*r.assisted_balanced_accuracy:.2f}% | {100*r.base_accuracy:.2f}% | "
            f"{100*r.assisted_accuracy:.2f}% | {gg.status} |"
        )

    lines += [
        "",
        "## Source sensitivity — combined net rescue",
        "",
        "| Partition | Window | BASE | SI_n | NQ_n | ZN_v | CL_v | GC_n | NQ_c | Min | Median | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in sensitivity.sort_values(["partition","window"]).itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {r.net_BASE} | {r.net_SI_n} | {r.net_NQ_n} | "
            f"{r.net_ZN_v} | {r.net_CL_v} | {r.net_GC_n} | {r.net_NQ_c} | "
            f"{r.min_net} | {r.median_net:+.1f} | {r.status} |"
        )

    lines += [
        "",
        "## Frozen 2025 transport decision",
        "",
    ]
    eligible = gate[gate.transport_eligible]
    if eligible.empty:
        lines.append("- **No BOCPD session head is eligible to open 2025.**")
    else:
        for r in eligible.itertuples(index=False):
            lines.append(f"- **{r.partition} / {r.window} / {r.base_model}** — {r.status}")

    lines += [
        "",
        "## Governance",
        "",
        "The 2025 holdout remains closed in this run. Stage-2 cannot alter BOCPD parameters, Handoff thresholds, roll mapping, or the frozen session bases.",
    ]
    (OUT / "result.md").write_text("\n".join(lines) + "\n")

    print(json.dumps({
        "status": summary["status"],
        "eligible": summary["transport_eligible"],
        "gate": summary["gate"],
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
