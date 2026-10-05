# GOLD D1 — 28 Sep to 2 Oct 2026 CIG extension

**Status:** retrospective diagnostic; SAGE/RuleFlow fail-closed where frozen source snapshots are unavailable.

| Cutoff | Issue | Actual | SAGE+RF | V5 | RIFT | VEGA | CIG | Correct |
|---|---|---|---|---|---|---|---|---|
| 2026-09-25 | 2026-09-28 | DOWN | UP | UP | UP | UP | UP | 0 |
| 2026-09-28 | 2026-09-29 | DOWN | UP | UP | DOWN | DOWN | UNCERTAIN |  |
| 2026-09-29 | 2026-09-30 | UP | UP | UP | UP | UP | UP | 1 |
| 2026-09-30 | 2026-10-01 | UP | DOWN | DOWN | DOWN | DOWN | DOWN | 0 |
| 2026-10-01 | 2026-10-02 | DOWN | UP | UP | UP | UP | UP | 0 |

- days: **5**
- 4/4 consensus: **4**
- correct consensus: **1**
- consensus accuracy: **25.00%**
- coverage: **80.00%**
- V5 full-chain historical reproduction max abs diff: **5.551e-17**

## Governance

SAGE V2 requires both IFBC and LLRS under its frozen source contract. The archived snapshots end on 2026-09-24; the frozen missing-source policy therefore yields no exception and KEEP V5. RuleFlow V3-TG has no same-origin frozen source record for these post-snapshot origins, so this extension does not invent a retrospective RuleFlow flip. This preserves fail-closed semantics but is not equivalent to a fully reconstructed prospective source state.
