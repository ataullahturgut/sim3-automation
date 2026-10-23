# CRITICAL DATA QUALITY ALERT — 2026-02-27 pinned four-metal source anomaly

Date: 2026-10-23
Status: SOURCE_CONFLICT_DETECTED / STOP_2026_EVALUATION_PROMOTION / NO_DATA_REPLACEMENT
Project: gold-weekly-h1-ann-v1-20261023
Evidence: GitHub Actions run https://github.com/ataullahturgut/sim3-automation/actions/runs/40001347644
Source artifact: gold-weekly-h1-4metal-original-git-source-v1, SHA256 a36cebdd1dc2b46766e42407bdf275115b1656e500b3cc3dadfba8a1d5597b2e
Source daily: lbruton/StakTrakr September-2026 research snapshot commit 02964d0324dde362099976c867f5077a369acaa5, NOT first-print PIT.

## Four-metal daily end-of-week values from the stored snapshot

2026-02-23 week first shared observation: Au 5214.24 USD/oz.
2026-02-27 last shared observation: Au **3516.02 USD/oz**, Ag **62.15**, Pt **1585.39**, Pd **1201.26**.
2026-02-23 week mean Au 4851.424; 2026-03-02 next week's Au open 5354.59, mean 5197.702.
Across all four metals Feb-23-to-Feb-27 week moves according to the snapshot are abnormal, approximately gold -27% simple (-39.4% log), silver -28.7% simple (-33.8% log), platinum -26.3% simple (-30.5% log), palladium -31.8% simple (-38.3% log).
Gold 2026-02-27 quote 3516.02 is inconsistent with externally contemporaneous public reporting of >5200.

External contemporaneous dated checks:
- Reuters 2026-02-27: spot gold approx USD 5230.56: https://www.reuters.com/world/india/gold-steady-investors-weigh-progress-us-iran-talks-2026-02-27/
- World Gold Council official 2026-03-05 February commentary referencing Feb 27: LBMA PM monthly-end Gold USD 5222, February return +4.8%: https://www.gold.org/goldhub/research/gold-market-commentary-february-2026

These are not identical price benchmarks/time snapshots; the discrepancy is far too large to pass as routine fixing variation. Preserve original evidence and flag it, do not silently substitute Reuters spot for LBMA source price.

## Consequences

- The weekly 2026-02-23 target's true last-day outcome may be corrupted; 2026-03-02 weekly inputs depend on corrupted Feb-27 close, high-low/range and vol; further training data include this anomalous week. Weekly Feb mean is also skewed.
- The existing monthly four-metal "single source" normalization checks *only internal parity* against monthly view. If the same daily bad row feeds both views, parity can PASS despite source error.
- Hence **ALL 2026 retrospective weekly/monthly rankings have data-quality caveats until this source anomaly is resolved**. Do not publish them as price-input-verified; specifically February monthly target and later month training rows could be affected, including GPR VW training and ANN.
- Distinguish actual sharp 2026-01-30 + 2026-02-02 two-session gold selloff, confirmed by Reuters, from suspect fake 2026-02-27 collapse. 
- Necessary action: date-level raw git comparison and 4-metal anomaly scan 2010-2026 with independent authority; quarantine invalid daily data and regenerate canonical source, then rerun all affected models with frozen algorithm settings and comparative versioned results. No rewriting historical files and no silent edits to NeoN.
