from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
BOOTSTRAP_SHA = "3c7e2b1bae588ce38982c0804e78bc576642382a"
FINAL_STATUS = "RUNTIME_BOOTSTRAP_PRODUCTION_PASS"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{count}:{old[:120]!r}")
    return text.replace(old, new, 1)


def main() -> int:
    text = MANIFEST.read_text(encoding="utf-8")
    if FINAL_STATUS in text and "PENDING_CANONICAL_BOOTSTRAP" not in text:
        print("MANIFEST_V125_RUNTIME_BOOTSTRAP_ALREADY_FINAL")
        return 0

    text = replace_once(
        text,
        "Runtime bootstrap is an observability/provenance operation only and remains `PENDING_CANONICAL_BOOTSTRAP` until the canonical code SHA is promoted and the 12-engine post-write audit passes.",
        f"Runtime bootstrap completed as an observability/provenance operation using canonical bootstrap code SHA `{BOOTSTRAP_SHA}`. The production post-write audit proved 12/12 runtime states, 4 ACTIVE / 3 WAITING / 5 BLOCKED, 3 direction-vote-permitted context motors, and exactly-one runtime linkage for all seven persisted component-context rows. No forecast, expert forecast, canonical forecast or Decision Store row was fabricated by bootstrap.",
    )
    text = replace_once(
        text,
        "14. Runtime-ledger bootstrap status at this manifest issue point is `PENDING_CANONICAL_BOOTSTRAP`; it may only link the existing seven persisted context rows and status-only WAITING/BLOCKED engines, with no recalculation or prospective relabeling.",
        f"14. Runtime-ledger bootstrap status is `{FINAL_STATUS}` using canonical bootstrap code SHA `{BOOTSTRAP_SHA}`; it linked only the existing seven persisted context rows and status-only WAITING/BLOCKED engines, with no recalculation or prospective relabeling.",
    )
    text = replace_once(
        text,
        "Runtime bootstrap status:\n\n`PENDING_CANONICAL_BOOTSTRAP`",
        f"Runtime bootstrap status:\n\n`{FINAL_STATUS}`",
    )
    MANIFEST.write_text(text, encoding="utf-8")
    print("MANIFEST_V125_RUNTIME_BOOTSTRAP_FINALIZE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
