# GOLD CONTROL — UP-2 INDEPENDENT INTEGRITY & ECONOMIC ARITHMETIC AUDIT V1

**Date:** 2026-09-23  
**Identity:** `UP2_INDEPENDENT_INTEGRITY_ECON_AUDIT_V1_RESEARCH`

Purpose: independently verify the frozen One-Sided UP-2 Logit V1 ledger, routing labels, call rule, target returns, and the investor arithmetic previously reported.

This audit does not change the model.

Checks:
1. Every ledger row is unique by origin/target and has origin < target.
2. `actual_up` equals the sign of the frozen parent `target_close_return`.
3. Frozen parent `target_close_return` equals an independently reconstructed log close-to-close return from the read-only governed 5-minute DB daily closes.
4. `up2_call == 1[p_up > tau]` exactly.
5. Annual and pooled confusion metrics recomputed from the ledger match the frozen result JSON.
6. Investor arithmetic is recomputed directly from governed daily close ratios, not from prior assistant calculations:
   - true-UP long gains;
   - false-UP long losses;
   - missed-UP opportunity while flat;
   - unresolved-DOWN short opportunity while flat;
   - fixed-notional net on UP2 calls;
   - compounded return across only UP2-call days.
7. No leverage, spread, fees or slippage.
8. Missed UP/DOWN are opportunity costs, not realized losses.
9. 2025 remains locked retrospective transport only; 2026 excluded.

Final audit statuses:
- `AUDIT_PASS`
- `AUDIT_FAIL`
