# GLOBAL XAU DAILY H3 — Raw-Source CART Pattern Screen

Model: shallow CART, depth=3, min leaf=60. 2025/2026 were not used.

| Source block | N | Accuracy | Balanced acc | Brier | Log loss | Pred SD |
|---|---:|---:|---:|---:|---:|---:|
| GOLD_ONLY | 755 | 51.92% | 50.35% | 0.252650 | 0.698884 | 0.0611 |
| METALS4 | 755 | 50.60% | 50.02% | 0.252962 | 0.701126 | 0.0890 |
| GOLD_EQUITY3 | 755 | 49.40% | 49.21% | 0.258808 | 0.712499 | 0.0937 |
| ALL7 | 755 | 48.48% | 48.36% | 0.263193 | 0.721218 | 0.0962 |

Best block by Brier: **GOLD_ONLY**.

Split/rule logs and final pre-2025 tree rules were saved for later inspection.
