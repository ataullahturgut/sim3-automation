# R23 prereg | preissue GVZ-only vs asymmetric downside tail risk model soft-gated by ex ante volatility regime
Research: R18 GOV stationary prior-last GVZ alone better than RV+GVZ some years. R22 SEMI_ACCEL improves 2025/26 high/low tail event ranking but 2023 is inverted. Test whether **PREISSUE independently measured GVZ stress regime** explains why, using no reference monthly HMM states or future chart. Explicit distinction: high-GVZ proxy NOT reconstructed original 13D HMM. 2025/26 already inspected multiple times and never virgin.
Same R22 source cohort exact 3 weekdays09TR BID/ASK sign parity, 08:45 issue complete16 M15 04:45–08:30 XAU BID, last GVZ date before issue with<=7d gap, last5 quote-close returns completed prior date with source gaps<=7, and last20 past GVZ observations (all gap<=7). Event 3day BID logret<=−0.015; retain identical scored year dates and training origin labels matured before annual Jan1.
FROZEN once per training cutoff (end2022 for2023, end2023 for2024,end2024 SAME for2025/2026) standardized logistic lambda30:
GVZ_ONLY logit y~log(previous GVZ close);
SEMI_ACCEL logit y~log(4h XAU realized RV)+log(previous GVZ)+last5 closed XAU09-to09 sum+most negative last5 return+negative semivar fraction last5 +GVZ5 slope;
NO refitting 2025/26.
Scenario A `HALF_ENSEMBLE` =.5×GVZ_ONLY +.5×SEMI_ACCEL;
Scenario B `STATIC_UPPER_QUARTILE_GATE`: if GVZprevious >= percentile75 of original TRAIN PRIOR-NY GVZ level asof on full training months, use SEMI_ACCEL, else GVZ_ONLY (hard fixed conditional switch); NO thresholds optimized later.
Scenario C `SOFT_UPPER_QUARTILE_GATE`: if stress high predict .75×SEMI_ACCEL + .25×GVZ_ONLY; else .25×SEMI_ACCEL+.75×GVZ_ONLY. Fixed blend.
Brier per2023/24/25/26 vs same-source frozen Beta and first two experts and 20% high-v-low event risk sorted, observed events count; if 2023 loss reverses but Brier better via fallback can qualify research risk under regime. Also stratify GPR? Original gold monthly GPR source not live daily so NO. No signed UP/DOWN improvement claimed, no bank PnL, 3weekday events overlap, prospective2027 required.
