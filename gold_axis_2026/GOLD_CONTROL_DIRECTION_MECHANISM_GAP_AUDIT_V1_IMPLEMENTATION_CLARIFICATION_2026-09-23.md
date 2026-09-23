# GOLD CONTROL — DIRECTION MECHANISM-GAP AUDIT V1 IMPLEMENTATION CLARIFICATION

**Date:** 2026-09-23  
**Identity:** `DIRECTION_MECHANISM_GAP_AUDIT_V1_RESEARCH`  
**Timing:** before scoring.

Implementation edge cases are frozen as follows:

- Path always includes session start at cumulative return 0.
- Final quarter uses `ceil(0.25*N)` final returns.
- Final hour uses the final 12 retained 5-minute returns.
- A "new low" requires the current cumulative path endpoint to be strictly below all earlier path points by more than `1e-15`.
- If the global trough is the closing path point:
  - `post_trough_efficiency=0`;
  - `post_trough_positive_move_share=0`;
  - `post_trough_sign_change_rate=0`;
  - `recovery_speed_norm=0`;
  - `near_trough_revisit_rate=1`, reflecting a close at the trough.
- Zero returns are removed only when calculating sign-change rate.
- `last_hour_slope_norm` fits OLS to the cumulative path of the final-hour returns including a local start point at zero; the per-bar slope is multiplied by `N/sqrt(RV)`.
- `last_hour_trend_r2=0` when the final-hour cumulative path has zero variance.
- If full-day downside realized variance is zero, both shock-concentration ratios and the late-downside shares that divide by it are set to zero.
- No feature, contrast, stability threshold, or interpretation rule is otherwise changed.
