# GOLD H3 — Databento Bridge Cost Probe — 2026-10-05

**Status:** **BLOCKED_DATABENTO_API_KEY_MISSING**

- This probe performs no historical market-data download.
- It does not change LLRS, IFBC, Handoff, DPTC, Q95 or Q99.
- Purpose: verify continuous symbology and estimate cost before spending credits.

## Blocker

GitHub Actions secret DATABENTO_API_KEY is not present or visible to the workflow.

Add that repository secret, then rerun this workflow.
