from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import audit_model_data_readiness_v143 as base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        base._self_test()
        if not os.environ.get("NEON_DATABASE_URL"):
            return 0

    report = base.run_audit()
    # psycopg may return UUID objects in nested audit details. Keep the underlying
    # audit read-only and preserve exact semantic values while serializing UUIDs
    # and any other standard scalar-like DB objects deterministically as strings.
    text = json.dumps(report, indent=2, sort_keys=True, default=str)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")

    if report["operational_model_data_ready"]:
        print("GOLD_CONTROL_MODEL_DATA_READINESS_V143_PASS")
        return 0
    print("GOLD_CONTROL_MODEL_DATA_READINESS_V143_BLOCKED")
    return 0 if args.report_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
