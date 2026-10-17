# E2/E3 — conditional direction and cost-hurdle magnitude: execution protocol (NOT RUN)

2026-10-12. Scientific research plan only; no refit, results, or model approval. Lower priority until E1 retrospective interpretation and E5 provenance/quoting prerequisites are resolved.

## E2 — direction probability from volatility (Christoffersen–Diebold mechanism)
- Separate DAY 09:00→16:45 TR and OVN 16:45→next09:00 TR, decision cutoffs ≤08:45 and ≤16:30 respectively.
- Pre-declared low-capacity rolling drift estimate `mu_t` from strictly prior returns; `sigma_t` from prior M15 realized volatility, point-in-time GVZ and calendar announcement-times known **before** each cutoff.
- Mechanistic probability `P(UP|F_t)=Phi(mu_t/sigma_t)`; compare with a constant-volatility alternative using the **identical drift** plus unconditional prior class-rate and always-UP/DOWN.
- Important falsification: if `mu_t=0`, probability is 0.5 for any sigma; if drift sign is constant, dynamic sigma changes **confidence**, not the optimal binary sign. Accordingly first test is **Brier/log-loss/calibration**, NOT arbitrary claim of directional switching.
- Use chronological 2023–24 development and label 2025/26 repeatedly inspected; month-block confidence intervals, explicit sample size/coverage, no lookahead or forward-filled macro surprises.
- Reject if calibration/Brier gains over class-prior and constant-variance reference do not hold robustly. No threshold search on opened 2025/26. Forecast source timestamps required.

## E3 — magnitude, event calendar and no-trade potential
- Outcomes separate from E2: next window absolute spot return and event `|return| > c` for fixed illustrative round-trip scenario costs 0.10%, 0.20%, 0.30%; these are **NOT real bank spreads**.
- Distinguish **movement exceeds cost** from **profitable direction call**: the former alone does not imply a trade should be taken.
- Predict risk and event probability with prior HAR realized volatility and pre-announced timestamp/event category; compare same-date rolling climatology and RV-only control, Brier/log-loss + calibration + uncertainty.
- Macro event *realized surprises* cannot be used before release; use ONLY as-of announced schedules. Historical first-announced schedule dates and reliable historical quote series must pass availability gates before modeling.
- A no-trade rule requires E5's real bid/ask samples and a separately validated post-decision directional edge. Do not optimize costs after inspecting profits.

## Common governance
- Inspect R15–R27, R23–R38, PRAMV/RFR, R73B and monthly R11 before building; avoid duplicating already-rejected mechanisms.
- Pre-register exact feature sources/windows/complete-case rules and a single statistical superiority family before opening target outcomes; 2025/26 already inspected.
- Fork a new research branch for each tested hypothesis; do not change existing model authorities, manifest or Neon originals. No model has been run in this PR.
