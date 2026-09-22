from __future__ import annotations

import bisect
import math
from datetime import date

import numpy as np

from regime_v1_data import (
    Daily, bonato_mod, logit_mod, ttsm_mod,
    to_bonato_days, to_logit_days, to_ttsm_days,
)


def bonato_h1_median(days_b) -> dict[str, dict]:
    out = {}
    for i in range(1, len(days_b) - 1):
        if not math.isfinite(days_b[i].lag1_return):
            continue
        train_idx = list(range(1, i))
        if len(train_idx) < 250:
            continue
        y = np.array(
            [math.log(days_b[j+1].close / days_b[j].close) for j in train_idx],
            dtype=float,
        )
        X = np.array(
            [[days_b[j].lag1_return, days_b[j].rv, days_b[j].rsk] for j in train_idx],
            dtype=float,
        )
        xn = np.array(
            [days_b[i].lag1_return, days_b[i].rv, days_b[i].rsk],
            dtype=float,
        )
        fc, mstar = bonato_mod.fit_qboost(X, y, xn, 0.50)
        ret = math.log(days_b[i+1].close / days_b[i].close)
        if ret == 0:
            continue
        out[days_b[i+1].d.isoformat()] = {
            "origin_date": days_b[i].d.isoformat(),
            "actual_up": int(ret > 0),
            "median": float(fc),
            "up": int(fc > 0),
            "mstar": int(mstar),
        }
    return out


def logit_two(days_l) -> dict[str, dict]:
    out = {}
    for i in range(1, len(days_l) - 1):
        origin = days_l[i]
        if not math.isfinite(origin.lag1_return):
            continue
        train_idx = list(range(1, i))
        if len(train_idx) < 250:
            continue
        y = np.array(
            [
                1.0 if math.log(days_l[j+1].close / days_l[j].close) > 0 else 0.0
                for j in train_idx
            ],
            dtype=float,
        )
        ret = math.log(days_l[i+1].close / origin.close)
        if ret == 0:
            continue
        result = {
            "origin_date": origin.d.isoformat(),
            "actual_up": int(ret > 0),
        }
        for name, feats in {
            "RM_LOGIT": ("log_rv", "rsk"),
            "AR1_RM_LOGIT": ("lag1_return", "log_rv", "rsk"),
        }.items():
            X = np.array(
                [[float(getattr(days_l[j], f)) for f in feats] for j in train_idx],
                dtype=float,
            )
            xn = np.array([float(getattr(origin, f)) for f in feats], dtype=float)
            p, _ = logit_mod.fit_logit_predict(X, y, xn)
            result[name + "_p"] = float(p)
            result[name + "_up"] = int(p >= 0.5)
        out[days_l[i+1].d.isoformat()] = result
    return out


def legacy_context(days: list[Daily]) -> dict[str, dict]:
    n = len(days)
    closes = np.array([x.close for x in days], dtype=float)

    # FAST: SMA20 and two completed daily observations persistence.
    sma20 = np.full(n, np.nan)
    for i in range(19, n):
        sma20[i] = float(np.mean(closes[i-19:i+1]))
    fast = {}
    for i in range(n):
        up = False
        if i >= 20:
            up = bool(closes[i] > sma20[i] and closes[i-1] > sma20[i-1])
        fast[days[i].d] = int(up)

    # SLOW: completed weekly closes, SMA4 weekly, two completed-week persistence.
    weekly_last: list[tuple[date, float]] = []
    week_pos = {}
    for x in days:
        iso = x.d.isocalendar()
        key = (iso.year, iso.week)
        if key in week_pos:
            weekly_last[week_pos[key]] = (x.d, x.close)
        else:
            week_pos[key] = len(weekly_last)
            weekly_last.append((x.d, x.close))

    wdates = [x[0] for x in weekly_last]
    wcl = np.array([x[1] for x in weekly_last], dtype=float)
    wsma4 = np.full(len(wcl), np.nan)
    for k in range(3, len(wcl)):
        wsma4[k] = float(np.mean(wcl[k-3:k+1]))
    wrobust = np.zeros(len(wcl), dtype=int)
    for k in range(4, len(wcl)):
        wrobust[k] = int(wcl[k] > wsma4[k] and wcl[k-1] > wsma4[k-1])

    slow = {}
    for x in days:
        k = bisect.bisect_right(wdates, x.d) - 1
        slow[x.d] = int(wrobust[k]) if k >= 0 else 0

    # MONTHLY_DIRECTION_3M: only completed months strictly before origin month.
    monthly_last: list[tuple[date, float]] = []
    month_pos = {}
    for x in days:
        key = (x.d.year, x.d.month)
        if key in month_pos:
            monthly_last[month_pos[key]] = (x.d, x.close)
        else:
            month_pos[key] = len(monthly_last)
            monthly_last.append((x.d, x.close))

    mdates = [x[0] for x in monthly_last]
    mclose = [x[1] for x in monthly_last]
    monthly = {}
    for x in days:
        current_key = (x.d.year, x.d.month)
        completed = [k for k,dv in enumerate(mdates) if (dv.year,dv.month) < current_key]
        up = 0
        if len(completed) >= 4:
            k = completed[-1]
            rets = [math.log(mclose[j] / mclose[j-1]) for j in range(k-2, k+1)]
            up = int(float(np.mean(rets)) > 0)
        monthly[x.d] = up

    out = {}
    for x in days:
        fu, su, mu = fast[x.d], slow[x.d], monthly[x.d]
        out[x.d.isoformat()] = {
            "FAST_UP": fu,
            "SLOW_UP": su,
            "MONTHLY_UP": mu,
            "legacy_up_count": fu + su + mu,
            "legacy_bucket": "CONSENSUS_UP" if fu + su + mu >= 2 else "NON_CONSENSUS_UP",
        }
    return out


def build_common(days: list[Daily]) -> list[dict]:
    tmap = {
        r["target_date"]: r
        for r in ttsm_mod.build_signal_rows(to_ttsm_days(days))
    }
    bmap = bonato_h1_median(to_bonato_days(days))
    lmap = logit_two(to_logit_days(days))
    ctx = legacy_context(days)

    common = []
    for td in sorted(set(tmap) & set(bmap) & set(lmap)):
        t, b, l = tmap[td], bmap[td], lmap[td]
        od = t["origin_date"]
        if od != b["origin_date"] or od != l["origin_date"]:
            raise RuntimeError(f"ORIGIN_MISMATCH:{td}")
        if int(t["actual_up"]) != int(b["actual_up"]) or int(t["actual_up"]) != int(l["actual_up"]):
            raise RuntimeError(f"ACTUAL_MISMATCH:{td}")
        c = ctx[od]
        common.append({
            "origin_date": od,
            "target_date": td,
            "actual_up": int(t["actual_up"]),
            "TTSM_S2": int(t["ttsm_s2_signal"] == 1),
            "TTSM_S1": int(t["ttsm_s1_signal"] == 1),
            "BONATO_AR1_RM_QBOOST_H1": int(b["up"]),
            "AR1_RM_LOGIT": int(l["AR1_RM_LOGIT_up"]),
            "RM_LOGIT": int(l["RM_LOGIT_up"]),
            **c,
        })
    return common
