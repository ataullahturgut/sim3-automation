# GOLD H3 — Existing API Futures Recovery Probe V2

**Conclusion:** **EXACT_2023_FIVE_CHANNEL_RECOVERY_NOT_ESTABLISHED_FROM_EXISTING_TWELVE_API**  
Frozen Yahoo LLRS panel loaded for bridge check: **True**.  
**Governance:** no model rules changed; no database writes; raw vendor market values are not logged.

## Exact futures recovery

| Channel | 2023 exact 1h established? | Best direct 2025 result | 2023 result | Bridge evidence |
|---|---|---|---|---|
| GC | **False** | No successful direct 1h identity | — | — |
| SI | **False** | No successful direct 1h identity | — | — |
| NQ | **False** | No successful direct 1h identity | — | — |
| ZN | **False** | No successful direct 1h identity | — | — |
| CL | **False** | No successful direct 1h identity | — | — |

## Commodity alternatives (not exact futures)

| Channel | Catalog candidates found | 2023 1h proxy test | Status |
|---|---:|---|---|
| GC | 16 | GAU/EUR n=0 meta={} | PROXY ONLY |
| SI | 10 | XAG/AUD n=0 meta={} | PROXY ONLY |
| NQ | 0 | — | PROXY ONLY |
| ZN | 0 | — | PROXY ONLY |
| CL | 2 | URALS/USD n=0 meta={} | PROXY ONLY |

## Interpretation

- A Twelve Data series is called **exact futures** only if returned metadata itself identifies the intended futures instrument; a similarly named equity/ETF/commodity is rejected.
- Commodity/index proxies may have deep 1h history, but they are not allowed to silently replace GC/SI/NQ/ZN/CL in the frozen DPTC lineage.
- If all five exact channels are not established, the next step is to audit other already-connected/public source routes rather than retune DPTC on proxy data.
