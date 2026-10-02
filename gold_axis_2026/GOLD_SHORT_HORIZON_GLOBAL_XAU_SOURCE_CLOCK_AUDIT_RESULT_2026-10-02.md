# GLOBAL XAU DAILY — Source / Clock Audit

This audit inventories the established project registry. It does not authorize a new provider or add a feature to the frozen H3 CORE3 engine.

| Family | Registered series | Latest observation | Aug-Sep rows | Binding daily rule |
|---|---:|---|---:|---|
| EQUITY | 5 | 2026-10-01 | 127 | strictly previous available date at daily forecast origin |
| FX_USD | 3 | 2026-09-25 | 78 | release-aware H.10/as-of; no same-origin future publication |
| GPR | 7 | 2026-09-01 | 9 | release-aware / vintage-safe only |
| PRECIOUS | 11 | 2026-07-31 | 0 | as-of feature cutoff / previous available observation |
| RATES | 3 | 2026-09-29 | 42 | release-aware; conservative H.15 lag |
| VOL | 4 | 2026-10-01 | 125 | strictly previous available date at daily forecast origin |
| XAU | 13 | 2026-10-02 | 9976 | explicit target identity; do not stitch clocks |

Key governance:
- Source identity and availability clock are separate contracts.
- DEXCHUS must not be relabeled as broad USD; use the corrected Broad-USD authority where registered.
- WTI/Brent remain challengers until their short-horizon PIT clock is explicitly frozen.
- Current R2 baseline uses CORE3 only; external families are not silently added.
