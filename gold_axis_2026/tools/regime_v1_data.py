from __future__ import annotations

import csv
import importlib.util
import math
import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import psycopg

TZ = "America/New_York"
TABLE = "public.xau_intraday_research_cache_5m"
ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "regime_dampener_v1"


def import_vendor(filename: str, name: str):
    p = VENDOR / filename
    spec = importlib.util.spec_from_file_location(name, p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_SPEC_FAILED:{p}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ttsm_mod = import_vendor("frozen_direction_ttsm_realized_semivariance_xau_v1.py", "frozen_ttsm_v1")
bonato_mod = import_vendor("frozen_direction_bonato_qboost_realized_moments_spot_xau_v1.py", "frozen_bonato_v1")
logit_mod = import_vendor("frozen_direction_downside_realized_moments_logit_v2.py", "frozen_logit_v2")


@dataclass(frozen=True)
class Daily:
    d: date
    close: float
    n_bars: int
    m_returns: int
    rv: float
    r3: float
    dr: float
    rs_plus: float
    rs_minus: float


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v


def load_external() -> list[Daily]:
    p = VENDOR / "dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv"
    out: list[Daily] = []
    with p.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            n = int(r["n_bars"])
            out.append(Daily(
                d=date.fromisoformat(r["date"]),
                close=float(r["close_mid"]),
                n_bars=n,
                m_returns=max(0, n - 1),
                rv=float(r["rv_5m"]),
                r3=float(r["r3_5m"]),
                dr=float(r["dr_5m"]),
                rs_plus=float(r["rs_plus_5m"]),
                rs_minus=float(r["rs_minus_5m"]),
            ))
    if len(out) != 1038:
        raise RuntimeError(f"EXTERNAL_ROW_COUNT:{len(out)}")
    if any(out[i].d >= out[i+1].d for i in range(len(out)-1)):
        raise RuntimeError("EXTERNAL_NOT_STRICTLY_SORTED")
    return out


def load_governed() -> list[Daily]:
    sql = f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date as d,
        observation_ts,
        close::double precision as close,
        lag(close::double precision) over (
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) as prev_close
      from {TABLE}
      where observation_ts >= '2020-01-01'::timestamptz
        and observation_ts < '2025-01-15'::timestamptz
        and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    intr as (
      select d, observation_ts, close,
             case when prev_close is not null and prev_close > 0
                  then ln(close/prev_close) end as r
      from b
    )
    select d,
      count(*)::int as n_bars,
      count(r)::int as m_returns,
      (array_agg(close order by observation_ts desc))[1]::double precision as close,
      coalesce(sum(r*r),0)::double precision as rv,
      coalesce(sum(r*r*r),0)::double precision as r3,
      coalesce(sum(case when r <= 0 then r*r else 0 end),0)::double precision as dr,
      coalesce(sum(case when r > 0 then r*r else 0 end),0)::double precision as rs_plus,
      coalesce(sum(case when r < 0 then r*r else 0 end),0)::double precision as rs_minus
    from intr
    group by d
    having count(*) >= 240
    order by d
    """
    with psycopg.connect(db_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql)
            raw = cur.fetchall()

    out: list[Daily] = []
    for d,n,m,c,rv,r3,dr,rp,rm in raw:
        vals = [float(c),float(rv),float(r3),float(dr),float(rp),float(rm)]
        if not all(math.isfinite(x) for x in vals) or vals[0] <= 0:
            raise RuntimeError(f"BAD_GOVERNED_ROW:{d}")
        out.append(Daily(
            d=d, close=vals[0], n_bars=int(n), m_returns=int(m),
            rv=vals[1], r3=vals[2], dr=vals[3],
            rs_plus=vals[4], rs_minus=vals[5],
        ))
    if len(out) < 900:
        raise RuntimeError(f"GOVERNED_TOO_SHORT:{len(out)}")
    return out


def rsk_value(r: Daily) -> float:
    if r.rv > 0 and r.m_returns > 0:
        z = math.sqrt(r.m_returns) * r.r3 / (r.rv ** 1.5)
        return z if math.isfinite(z) else 0.0
    return 0.0


def to_ttsm_days(days: list[Daily]):
    return [ttsm_mod.Day(x.d, x.close, x.n_bars, x.rs_plus, x.rs_minus) for x in days]


def to_bonato_days(days: list[Daily]):
    out = []
    prev = None
    for x in days:
        lag = float("nan") if prev is None else math.log(x.close / prev)
        out.append(bonato_mod.DayRow(x.d, x.close, x.n_bars, x.rv, rsk_value(x), lag))
        prev = x.close
    return out


def to_logit_days(days: list[Daily]):
    out = []
    prev = None
    for x in days:
        lag = float("nan") if prev is None else math.log(x.close / prev)
        out.append(logit_mod.DayRow(
            x.d, x.close, x.n_bars, x.rv, math.log(max(x.rv, 1e-12)), rsk_value(x), lag
        ))
        prev = x.close
    return out
