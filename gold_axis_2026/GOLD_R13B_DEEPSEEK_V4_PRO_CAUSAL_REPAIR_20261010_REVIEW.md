# R13B genuine DeepSeek V4 Pro causal repair

**One highest-value exact falsifiable experiment (R13-REV-A)**

**Target:** \(Y_t = \text{sign}(\text{H3}_{t}^{09})\), i.e. sign of GVZ 09:00→09:00 three-business-day return for origin day \(t\).  
**Forecast issue:** \(t\) at 09:00 New York.  
**Legal inputs at issue:** prior NY close GVZ, prior DAY\(_{t-1}\) (09→17, completed), matured H3 origins \(\mathcal{M}_t=\{i: \text{close}_i+3\text{business days} \leq t-1\}\), scheduled event dates with vintage-as-of-origin, RV regimes from prior close: \(\text{RV}_{t-1}^{20d} \in \{L,M,H\}\) (terciles on historical 2020–24, frozen).  
**Event label ex ante:** \(E_t=1\) if any CPI, NFP, or FOMC release is scheduled on calendar date \(t\) per calendar published before 2020; else 0.  
**Feature:**  
\[
x_t = \text{sgn}(A_{t-1}) \, \mathbf{1}(\text{coverage}_{t-1} \geq 0.8),
\]
where
\[
A_{t-1} = \text{median}_{i \in \mathcal{M}_t}\left[ \text{sgn}(\text{DAY}_{i}^{09\to17}) \cdot \text{sgn}(\text{H3}_{i}^{09\to09+3bd}) \right],
\]
and coverage is \(|\mathcal{M}_t|/|\text{eligible origins in past 63 business days}|\). If coverage < 0.8, abstain.

**Prediction rule:**
\[
\hat{Y}_t =
\begin{cases}
+\text{sgn}(A_{t-1}), & x_t \neq 0,\ \text{RV}_{t-1}^{20d}=L/M,\ E_t=0 \\
-\text{sgn}(A_{t-1}), & x_t \neq 0,\ \text{RV}_{t-1}^{20d}=H,\ E_t=0 \\
\text{abstain}, & E_t=1 \text{ or coverage}<0.8
\end{cases}
\]
Directional accuracy:
\[
\text{DA} = \frac{1}{|\mathcal{T}_s|}\sum_{t\in\mathcal{T}_s} \mathbf{1}(\hat{Y}_t = Y_t),
\]
over non-abstained origins. Error metric:
\[
\text{MAE}_{\text{sgn}} = \frac{1}{|\mathcal{T}_s|}\sum |\hat{Y}_t - Y_t| \in \{0,1,2\},
\]
and abstention rate.

**Folds:**  
Fold A (train/calibrate): origins 2023-01-03 to 2024-12-31.  
Fold B (test, unopened prior to 2025): origins 2025-01-02 to 2026-12-31. Freeze terciles and coverage threshold from Fold A only.  
**Benchmark:** sign(previous month direction) computed from matured H3 at \(t\), identical abstain gate.

**Negative controls:**  
(i) *Event-day permutation:* replace \(E_t\) with \(E_t^{\text{perm}}\) = random permutation of event indicators within same year, 10,000 draws; test DA difference vs real event schedule.  
(ii) *Calendar-vintage:* use 2019-published calendar to assign \(E_t\) for 2023–25; if event-day DA deviates > 2 standard errors from no-event days across vintages, reject causal claim.

**Preorigin maturation check:** for each \(t\), compute
\[
\text{MaturationGap}_t = \min_{i\in\mathcal{M}_t}(\text{issue}_t - \text{close}_i - 3\text{bd}),
\]
must be ≥ 0; any negative entry invalidates run. Report distribution of gap.

**Ex-ante regime counts and direction:** Report DA within \(\text{RV}=L/M\), H; within no-event; two-sided binomial exact p-value vs 0.5. Target minimum DA 0.55 with 50 non-abstained origins to claim signal.

---

**Fallback experiment (R13-REV-B)**

**Target:** \(Y_t = \text{sign}(\text{DAY}_t^{09\to17})\).  
**Input:** only \(Y_{t-1}\), \(\text{RV}_{t-1}^{20d}\), and \(E_t\) as above.  
**Rule:**
\[
\hat{Y}_t = \text{sgn}(Y_{t-1}) \quad \text{if } E_t=0 \text{ and } \text{RV}_{t-1}^{20d} \in \{L,M\},
\]
abstain if \(E_t=1\) or H regime.  
**Metric:** DA, MAE, abstention.  
**Negative control:** permuted event days; fixed calendar vintage.  
**Fold:** same 2023–24 vs 2025–26. If DA ≤ 0.50 on no-event L/M days, momentum absent; if >0.55, test regime interaction with H separately.
