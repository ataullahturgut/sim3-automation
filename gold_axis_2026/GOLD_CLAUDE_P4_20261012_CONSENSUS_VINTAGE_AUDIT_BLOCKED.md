# CLAUDE P4 — CPI/NFP expectation revisions and analyst dispersion: DATA AUDIT — **BLOCKED**

Date: 2026-10-12. Protocol PR #93, stage P4: "First run coverage/vintage/provenance audit without data
purchase; if only current consensus/after-event surprise, mark BLOCKED not synthetic." No model was
fitted and no return was looked at for P4.

## What the hypothesis needs
Information that is known **before** the 08:30 ET release and is not in past prices:
1. the pre-release consensus with a provable timestamp earlier than the decision;
2. **revisions** of that consensus in the days before the release (consensus vintages);
3. **dispersion** across analysts (individual forecasts or high/low/standard deviation).

## What Neon holds (read-only queries inside `SET TRANSACTION READ ONLY`, 2026-10-12)
| Series | Rows / events | Distinct `available_as_of` | `available_as_of` < release | `first_seen_at` | Provider timestamp proven |
|---|---|---|---|---|---|
| `MACRO_NFP_CONSENSUS_PIT` | 126 / 126 | 126 (= release time) | 0 | 1 value (2026-09-05) | false |
| `MACRO_CPI_CONSENSUS_PIT` | 126 / 126 | 126 | 1 | 2 values (2026-09-08) | false |
| `MACRO_CORE_CPI_CONSENSUS_PIT` | 126 / 126 | 126 | 1 | 2 values | false |
| `MACRO_AHE_CONSENSUS_PIT`, `MACRO_UNEMP_CONSENSUS_PIT` | 126 / 126 each | 126 | 0 | 1 value | false |

Metadata of every row (example 2024-06-07 NFP, value 182): `provider_field = "Forecast"` (Investing.com
event attribute), `availability_policy = "NO_EARLIER_THAN_OFFICIAL_BLS_RELEASE_TIMESTAMP"`,
`historical_reconstruction_not_original_retrieval = true`,
`provider_exact_pre_release_update_timestamp_proven = false`, `no_redistribution = true`.

## Findings
- **Exactly one consensus value per release.** There are no vintages, so revisions cannot be
  computed.
- **No analyst-level data**, no high/low/standard deviation, so dispersion cannot be computed.
- The single value was scraped retrospectively in September 2026, and the repository's own policy
  makes it available only at the official release time. It cannot be used as decision-time (08:45 or
  16:30 TR) information without assuming, unprovably, that the final consensus was the one visible
  before the decision.
- The actual-minus-consensus *surprise* is known only after 08:30 ET. It was already studied
  contemporaneously in R7/R8: first 15 minutes 43/55, T+1→T+15 25/50.

## Verdict
**P4 BLOCKED** for revisions and dispersion. No synthetic proxies were built: no backfilled
"pseudo-vintages" and no dispersion imputed from later revisions.

## What would unblock it (no purchase made, no credits spent)
- Analyst-level or high/low survey data with time stamps: Bloomberg ECO survey, LSEG/Refinitiv
  polls. These are paid terminal/vendor products, and a cost quote and license are needed (user
  approval required under CLAUDE.md).
- Free, but **not verified here**: public inflation nowcasts with daily publication histories (for
  example the Cleveland Fed CPI nowcast) could provide a pre-release, time-stamped expectation for
  CPI only. Their archive's vintage integrity must be audited before any test.
- Prospective capture: the repository notes "PROSPECTIVE_CAPTURE_ENABLED" for CPI consensus. Logging the
  consensus with a timestamp before each release from now on would allow a clean test in 1–2 years
  (about 12 NFP + 12 CPI events per year; a small sample).
