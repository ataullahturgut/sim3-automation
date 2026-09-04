from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"

HEADER_OLD = "**Manifest version:** 1.30\n**Freeze / issue date:** 2026-09-03"
HEADER_NEW = "**Manifest version:** 1.31\n**Freeze / issue date:** 2026-09-04"

ANCHOR = """The historical 2024–2026 evaluation is a **locked historical replay**, not genuinely unseen prospective evidence.\n\nThis distinction must remain visible in reporting and UI.\n"""

INSERT = """

## 10.1 BOCPD successor recovery path — v1.31 research evidence

The exact archived `BOCPD` executable identity remains:

`BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED`

That archived identity has **not** been reconstructed by guesswork and has not been reactivated.

Under the successor path authorized by `GOLD_CONTROL_V130_UNRESOLVED_ENGINE_RECOVERY_AUDIT_2026-09-04.md`, a clearly separate research identity has been created:

`BOCPD_RETURN_SUCCESSOR_V1`

Governance/evidence files:

- `gold_axis_2026/GOLD_CONTROL_UNRESOLVED_ENGINE_SUCCESSOR_ROADMAP_2026-09-04.md`
- `gold_axis_2026/GOLD_CONTROL_BOCPD_RETURN_SUCCESSOR_V1_CHANGE_CONTROL_2026-09-04.md`
- `gold_axis_2026/GOLD_CONTROL_BOCPD_RETURN_SUCCESSOR_V1_RISK_VALIDATION_CONTRACT_2026-09-04.md`
- `gold_axis_2026/GOLD_CONTROL_BOCPD_RETURN_SUCCESSOR_V1_ENGINEERING_EVIDENCE_2026-09-04.md`
- `gold_axis_2026/GOLD_CONTROL_PROJECT_STAGE_BOCPD_SUCCESSOR_V1_STATUS_2026-09-04.md`
- `gold_axis_2026/bocpd_successor_v1/frozen_contract_v1.json`
- `gold_axis_2026/tools/bocpd_return_successor_v1.py`
- `gold_axis_2026/tools/bocpd_return_successor_v1_risk_validation.py`

Methodological authority for the new recursion is Adams & MacKay (2007), *Bayesian Online Changepoint Detection*, arXiv:0710.3742. This authority supports the BOCPD framework; it does **not** prove the missing archived Gold Control prior/reset-score implementation.

Frozen successor role:

`REGIME_BREAK_CONTEXT`

Frozen successor constraints:

- direction vote = `false`;
- no H=1 price forecast;
- no automatic exit/action;
- no selector/ensemble role;
- no position mapping;
- completed monthly CORE5 GOLD log-return research axis;
- `L=36`, constant hazard `1/36`;
- DEV `2010-01..2020-12` only for prior fitting;
- VAL `2021-01..2023-12` untouched by fitting;
- LOCK `2024-01..2026-07` diagnostic only;
- 2026 tuning = `NONE`;
- archived threshold `0.034027906134261016` is **not reused** because archived score equivalence is not proven;
- historical evidence classes remain non-prospective.

Engineering evidence:

- run `33872811566` = `SUCCESS`, 9 tests PASS;
- run `33873106128` = `SUCCESS`, 14 combined engineering/risk tests PASS;
- run-2 tested SHA `993ad49abae525a58362dd7d51f551d965cf2156`;
- frozen replay rows `199` = DEV `132` + VAL `36` + LOCK `31`;
- deterministic result hash `59195f0375b43a30f77829b10d33101cc737624a9626b5281f9c637ab046358a`;
- posterior normalization, development-only prior, prefix invariance/PIT, no-threshold-reuse, no-validation-tuning, no-locked-tuning and no-write gates all PASS;
- database writes = `NONE`;
- prospective claim = `false`;
- promotion authorized = `false`.

Risk-diagnostic evidence reused the previously frozen Gold Control BOCPD severity semantics rather than introducing a post-result success threshold: 2–3 month primary horizon, cumulative forward GOLD return `<= -3%` as the tail definition, 1M secondary only, no automatic exposure action and locked replay excluded from approval. Validation candidate N=`5` showed descriptive downside-risk separation (candidate 2M/3M tail rates `60%/60%` versus non-candidate `12.90%/19.35%`; candidate mean 3M forward return `-3.55%` versus non-candidate `+2.12%`). This remains `DESCRIPTIVE_ONLY`; locked candidate N=`2` remains `DIAGNOSTIC_ONLY`.

Maximum current successor status:

`RESEARCH_SHADOW_CANDIDATE_RISK_DIAGNOSTIC_COMPLETE_PROSPECTIVE_VALIDATION_REQUIRED`

This status does **not** change the current production runtime inventory, does not replace the blocked archived `BOCPD` row, and does not create Decision Store authority. A later prospective-shadow observation requires a separately frozen completed-month issuer contract and may not backdate historical months as prospective.
"""


def main() -> None:
    text = MANIFEST.read_text(encoding="utf-8")

    if HEADER_NEW in text and "## 10.1 BOCPD successor recovery path — v1.31 research evidence" in text:
        print("MANIFEST_V1_31_BOCPD_SUCCESSOR_ALREADY_APPLIED")
        return

    if HEADER_OLD not in text:
        raise RuntimeError("manifest v1.30 header anchor not found; refusing silent patch")
    if text.count(ANCHOR) != 1:
        raise RuntimeError(f"BOCPD section anchor count must be 1, got {text.count(ANCHOR)}")
    if "## 10.1 BOCPD successor recovery path — v1.31 research evidence" in text:
        raise RuntimeError("successor section already exists under unexpected header")

    text = text.replace(HEADER_OLD, HEADER_NEW, 1)
    text = text.replace(ANCHOR, ANCHOR + INSERT, 1)
    MANIFEST.write_text(text, encoding="utf-8")

    check = MANIFEST.read_text(encoding="utf-8")
    required = [
        "**Manifest version:** 1.31",
        "BOCPD_RETURN_SUCCESSOR_V1",
        "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED",
        "RESEARCH_SHADOW_CANDIDATE_RISK_DIAGNOSTIC_COMPLETE_PROSPECTIVE_VALIDATION_REQUIRED",
        "AUTO_SELECTOR",
        "AUTO_ENSEMBLE",
        "NOT_PROVEN_POSITION_MAPPING",
    ]
    missing = [x for x in required if x not in check]
    if missing:
        raise RuntimeError(f"manifest post-patch required markers missing: {missing}")

    print("MANIFEST_V1_31_BOCPD_SUCCESSOR_APPLY=PASS")
    print("ARCHIVED_BOCPD_REMAINS_BLOCKED=YES")
    print("SUCCESSOR_PROSPECTIVE_CLAIM=NO")
    print("SUCCESSOR_PRODUCTION_PROMOTION=NO")


if __name__ == "__main__":
    main()
