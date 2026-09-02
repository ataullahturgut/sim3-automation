from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable

from multi_expert_forecast import (
    AUTO_ENSEMBLE,
    AUTO_SELECTOR,
    EARLY_INDICATIVE_TRACK if False else TRACK_EARLY_INDICATIVE,
    EXPERT_ORDER,
    PATCH_EXPERT,
    RW_EXPERT,
    SELECTOR_STATUS,
    VW_EXPERT,
    MOMENTUM_EXPERT,
)


OVERALL_BLOCK = "BLOCKED_NO_EXECUTABLE_PIT_SAFE_EXPERT_TRACK"
PATCH_BLOCK = "BLOCKED_EARLY_INDICATIVE_PATCH_PIT_CONTRACT_NOT_FROZEN"
VW_BLOCK = "BLOCKED_NOT_PROVEN_EXECUTABLE"
LEVEL_SOURCE_BLOCK = "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"


@dataclass(frozen=True)
class EarlyIndicativeReadiness:
    as_of: str
    forecast_track: str
    expert_id: str
    status: str
    executable: bool
    write_allowed: bool
    reason: str


STATUS_BY_EXPERT = {
    PATCH_EXPERT: (
        PATCH_BLOCK,
        "Patch V7 month-end input semantics are frozen for the end-September origin; an intramonth PIT contract is not frozen.",
    ),
    VW_EXPERT: (
        VW_BLOCK,
        "Exact archived VW-MIDAS-MSVR executable runner is not proven.",
    ),
    MOMENTUM_EXPERT: (
        LEVEL_SOURCE_BLOCK,
        "3M Momentum formula is reproducible but no manifest-authorized forward monthly-level source is bound.",
    ),
    RW_EXPERT: (
        LEVEL_SOURCE_BLOCK,
        "RW formula is reproducible but no manifest-authorized forward monthly-level source is bound.",
    ),
}


def readiness(as_of: datetime | None = None) -> list[EarlyIndicativeReadiness]:
    ts = as_of or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        raise ValueError("EARLY_INDICATIVE_AS_OF_MUST_BE_TIMEZONE_AWARE")
    return [
        EarlyIndicativeReadiness(
            as_of=ts.isoformat(),
            forecast_track=TRACK_EARLY_INDICATIVE,
            expert_id=expert_id,
            status=STATUS_BY_EXPERT[expert_id][0],
            executable=False,
            write_allowed=False,
            reason=STATUS_BY_EXPERT[expert_id][1],
        )
        for expert_id in EXPERT_ORDER
    ]


def overall_status(rows: Iterable[EarlyIndicativeReadiness]) -> str:
    items = list(rows)
    if not items:
        return OVERALL_BLOCK
    if any(x.write_allowed or x.executable for x in items):
        raise RuntimeError("EARLY_INDICATIVE_READINESS_INCONSISTENT_WITH_FROZEN_V1_CONTRACT")
    return OVERALL_BLOCK


def report(as_of: datetime | None = None) -> dict:
    rows = readiness(as_of)
    return {
        "contract": "FROZEN_FAIL_CLOSED_EARLY_INDICATIVE_CONTRACT_V1",
        "forecast_track": TRACK_EARLY_INDICATIVE,
        "overall_status": overall_status(rows),
        "selector_status": SELECTOR_STATUS,
        "auto_selector": AUTO_SELECTOR,
        "auto_ensemble": AUTO_ENSEMBLE,
        "database_writes": "NONE",
        "canonical_forecast_contract_write": "NONE",
        "experts": [asdict(x) for x in rows],
    }


def main() -> int:
    payload = report()
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    print(f"EARLY_INDICATIVE_OVERALL_STATUS={payload['overall_status']}")
    print(f"FORECAST_TRACK={payload['forecast_track']}")
    print(f"SELECTOR_STATUS={payload['selector_status']}")
    print(f"AUTO_SELECTOR={payload['auto_selector']}")
    print(f"AUTO_ENSEMBLE={payload['auto_ensemble']}")
    print("DATABASE_WRITES=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
