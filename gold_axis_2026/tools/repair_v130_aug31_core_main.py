from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data_pipeline" / "aug31_eod_state_historical_replay.py"
OLD = 'cur.execute("SELECT count(*) AS n FROM canonical_monthly_forecasts")\n            canonical_count = int(cur.fetchone()["n"])'
NEW = 'cur.execute("SELECT count(*) AS n FROM monthly_forecast_contracts")\n            canonical_count = int(cur.fetchone()["n"])'


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    count = text.count(OLD)
    if count != 1:
        raise RuntimeError(f"AUG31_REPLAY_CORE_REPAIR_MATCH_COUNT:{count}")
    PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    repaired = PATH.read_text(encoding="utf-8")
    if "canonical_monthly_forecasts" in repaired:
        raise RuntimeError("AUG31_REPLAY_CORE_STALE_TABLE_REFERENCE_REMAINS")
    print("AUG31_REPLAY_CORE_MAIN_REPAIR_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
