from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from gold_r4 import EmergencyState, classify_state, completed_weekly_closes, fast_state, gvz_risk, slow_state, three_month_direction


def _parse_optional_bool(value):
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return True
    if text in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"Cannot parse macro_event_down={value!r}")


def run_replay(daily: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    required_daily = {"date", "close"}
    required_monthly = {"target_month", "vw_forecast", "return_t1", "return_t2", "return_t3"}
    if not required_daily.issubset(daily.columns):
        raise KeyError(f"daily.csv missing: {sorted(required_daily - set(daily.columns))}")
    if not required_monthly.issubset(monthly.columns):
        raise KeyError(f"monthly_contract.csv missing: {sorted(required_monthly - set(monthly.columns))}")

    d = daily.copy()
    d["date"] = pd.to_datetime(d["date"], errors="raise")
    d["close"] = pd.to_numeric(d["close"], errors="raise")
    d = d.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)

    m = monthly.copy()
    m["target_month"] = m["target_month"].astype(str)
    for col in ["vw_forecast", "return_t1", "return_t2", "return_t3"]:
        m[col] = pd.to_numeric(m[col], errors="raise")
    contract = m.set_index("target_month").to_dict(orient="index")

    emergency = EmergencyState()
    rows = []
    for i, row in d.iterrows():
        date = pd.Timestamp(row["date"])
        month_key = date.strftime("%Y-%m")
        if month_key not in contract:
            raise KeyError(f"No monthly contract for {month_key}")
        mc = contract[month_key]
        vw = float(mc["vw_forecast"])
        monthly_direction = three_month_direction([float(mc["return_t3"]), float(mc["return_t2"]), float(mc["return_t1"])])
        history = d.iloc[: i + 1]
        fast = fast_state(history["close"].tolist())
        slow = slow_state(completed_weekly_closes(history[["date", "close"]], date))
        level, reversal = emergency.update(date, float(row["close"]), vw)
        risk = gvz_risk(float(row["gvz"])) if "gvz" in d.columns and not pd.isna(row.get("gvz")) else None
        macro = _parse_optional_bool(row.get("macro_event_down")) if "macro_event_down" in d.columns else None
        bocpd = str(row["bocpd_context"]) if "bocpd_context" in d.columns and not pd.isna(row.get("bocpd_context")) else None
        classification = classify_state(monthly_direction, level, reversal, fast, slow, macro)
        next_session = pd.Timestamp(d.iloc[i + 1]["date"]).date().isoformat() if i + 1 < len(d) else None
        rows.append({
            "date": date.date().isoformat(), "close": float(row["close"]), "target_month": month_key,
            "vw_forecast_frozen": vw, "monthly_direction_3m": monthly_direction.value,
            "level_emergency": level.value, "reversal_emergency": reversal.value,
            "fast_state": fast.value, "slow_state": slow.value,
            "gvz": None if risk is None else risk.value, "gvz_cap": None if risk is None else risk.cap,
            "gvz_panic": None if risk is None else risk.panic, "macro_event_down": macro,
            "bocpd_context": bocpd, "classification": classification,
            "default_execution_session": next_session,
        })
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Frozen Gold R4.1 daily sequential replay")
    p.add_argument("--daily", required=True, type=Path)
    p.add_argument("--monthly", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    result = run_replay(pd.read_csv(a.daily), pd.read_csv(a.monthly))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(a.out, index=False)
    print(f"Wrote {len(result)} sequential EOD states -> {a.out}")


if __name__ == "__main__":
    main()
