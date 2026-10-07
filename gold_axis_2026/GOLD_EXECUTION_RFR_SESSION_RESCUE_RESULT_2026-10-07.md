# GOLD EXECUTION RFR + SESSION EXPERT RESCUE RESULT — 2026-10-07

**Status:** COMPLETE / DEVELOPMENT-ONLY RESCUE-GATE AUDIT

Base is PAIR on RFR-NOMACRO eligible days. A gate can override PAIR with RFR only when PAIR and RFR disagree. Session signals are state evidence, not relabeled overnight targets.

| Gate | DEV overrides | DEV rescue | DEV break | DEV net | DEV BA | Base BA | 2025 overrides | 2025 rescue | 2025 break | 2025 net | 2025 BA | Base BA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RFR_ALWAYS | 32 | 19 | 13 | +6 | 57.07% | 53.43% | 5 | 2 | 3 | -1 | 58.14% | 58.68% |
| WGC_BOTH_RFR | 2 | 2 | 0 | +2 | 54.37% | 53.43% | 0 | 0 | 0 | +0 | 58.68% | 58.68% |
| SOBTI_BOTH_RFR | 4 | 2 | 2 | +0 | 53.56% | 53.43% | 0 | 0 | 0 | +0 | 58.68% | 58.68% |
| ANY_SESSION_BOTH_RFR | 4 | 2 | 2 | +0 | 53.56% | 53.43% | 0 | 0 | 0 | +0 | 58.68% | 58.68% |
| THREE_OF_FOUR_RFR | 2 | 2 | 0 | +2 | 54.37% | 53.43% | 0 | 0 | 0 | +0 | 58.68% | 58.68% |

Development-only selected gate: **RFR_ALWAYS**.
Selection requires nonnegative net rescue in both 2023 and 2024 and at least five development overrides. 2025 is transport evidence only.
If no gate passes, session expert-state gating is rejected at this stage.
