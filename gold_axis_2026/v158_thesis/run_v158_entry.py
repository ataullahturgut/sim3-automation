from __future__ import annotations

import pandas as pd

from gold_axis_2026.v158_thesis import run_v158_trend_reversal_router as core

_original = core.sequential_reversal_probabilities


def _within_frozen_period_maturity(frame: pd.DataFrame, contract: dict) -> pd.DataFrame:
    if frame.empty:
        return frame
    w = contract["windows"]
    origin = pd.to_datetime(frame["origin_date"])
    target = pd.to_datetime(frame["target_date"])
    keep = (
        ((origin >= pd.Timestamp(w["formation_score_start"])) & (origin <= pd.Timestamp(w["formation_score_end"])) & (target <= pd.Timestamp(w["formation_score_end"])))
        | ((origin >= pd.Timestamp(w["validation_start"])) & (origin <= pd.Timestamp(w["validation_end"])) & (target <= pd.Timestamp(w["validation_end"])))
        | ((origin >= pd.Timestamp(w["test_start"])) & (origin <= pd.Timestamp(w["test_end"])) & (target <= pd.Timestamp(w["test_end"])))
    )
    return frame.loc[keep].copy()


def _sequential(*args, **kwargs):
    frame = _original(*args, **kwargs)
    contract = args[2] if len(args) >= 3 else kwargs["contract"]
    return _within_frozen_period_maturity(frame, contract)


core.sequential_reversal_probabilities = _sequential


def main() -> int:
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
