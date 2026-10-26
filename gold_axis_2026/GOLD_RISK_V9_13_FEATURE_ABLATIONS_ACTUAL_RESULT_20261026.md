# GOLD RISK V9 — 13 source-group ablations (2026-10-26)

**STATUS: EXECUTED, research-only; NOT promoted.** Actual code was run locally using original V8 data artifact, 398-row CFTC CSV, original BlackRock SLV workbook, FRB H.15 CSV and 2023–2026 US Treasury real-yield CSVs. All six source file SHA256 digests matched the prior official acquisition audit. No production model or Neon changes.

## Model and fixed contract

- All 13 candidates use the existing `RobustScaler -> IsolationForest(200 trees; random_state=1701) -> fit-only 90th/95th percentile alarms`. No price forecast; no new supervised training.
- The candidate groups add 2 features for H15 2-year nominal / 10Y−2Y curve slope, 2 for 10-year par real yield / recent movement, and 2 for one/five observed valid market-session SLV shares-outstanding percent change. CFTC retains 7 previous variables. GLD/CME are NOT in V9: no release-vintage-qualified source.
- Target periods: 2023–2024 fit/2025 validation; refit 2023–2025/2026 historical stress through Sep21. Issue at **17:30 America/New_York** only; *not* a Turkey 09:00 replay.
- Verified V8 reference first: 873 original aligned observations, 2025 BASE14 31 red, 2/3 next-day >=3%; CFTC21 30 red, 3/3; 2026 BASE14 46 red, 4/4; CFTC21 31 red, 4/4.
- To compare **on identical available-input origins**, V9 excludes **5 2024 original training rows** near missing SLV issuer entries, leaving 868 common dates (2025 232, 2026 161), training 470 / 702. **Important:** re-fitting BASE14 on this matched sample changes 2025 BASE14 from 31 to 33 red and 2/3 to 3/3; this is SAMPLE EFFECT, not a new-feature improvement. Compare only V9 matched rows with each other.

## 2026 matched-source results

| Family | Red days | Next-day >=3% origin hits | Next 5d >=5% origin hits | 5d overlapping label groups hit | Next5 non-event red days |
|---|---:|---:|---:|---:|---:|
| BASE14 | 45 | 4/4 | 9/13 | **4/4** | 36 |
| BASE14+CFTC7 | 29 | 4/4 | 6/13 | 2/4 | 23 |
| BASE14+2Y nominal | 47 | 4/4 | 9/13 | **4/4** | 38 |
| BASE14+real yield | 48 | 4/4 | 9/13 | **4/4** | 39 |
| BASE14+SLV | 48 | 4/4 | 9/13 | **4/4** | 39 |
| BASE14+2Y+real | 30 | 4/4 | 6/13 | 2/4 | 24 |
| BASE14+2Y+SLV | 34 | 4/4 | 7/13 | 3/4 | 27 |
| BASE14+real+SLV | 24 | 4/4 | 6/13 | 2/4 | 18 |
| BASE14+2Y+real+SLV | 39 | 4/4 | 7/13 | 3/4 | 32 |
| BASE14+CFTC+2Y | 27 | 4/4 | 7/13 | 3/4 | 20 |
| BASE14+CFTC+real | 27 | 4/4 | 7/13 | 2/4 | 20 |
| BASE14+CFTC+SLV | 33 | 4/4 | 8/13 | 3/4 | 25 |
| BASE14+CFTC+all-new | 21 | 4/4 | 6/13 | 2/4 | 15 |

**No version improves BASE14 both in 5-day risk-cluster capture and false-red days.** BASE14+2Y retains 4/4 and reduces false *alert episodes* from 6 to 4 in 2026 but actually worsens false RED *days* (36→38), and 2025 RED days worsen from 33 to 51. Not robust improvement.

**2025-only validation selection:** BASE14+CFTC7 (26 red, 3/3 daily >=3% and 3/3 5d origin clusters) rather than 2025 BASE14 (33 red); this selected model subsequently catches only **2/4 2026** 5d risk clusters. It fails the 2026 retrospective transport stress.

## Safety and limitations

- The 4/4 “hit” means a RED alert fell somewhere *inside a group of overlapping next-five-day risk-origin labels*; NOT 4 independently verified physical crash onsets forecast beforehand. Prior-5-origin warnings were counted separately, still not physically verified intraday onset.
- H15 historical availability was filtered by scheduled 16:15 NY publication. TIPS and SLV have only a **research T+1 weekday 09:00 NY proxy**, and their first-published vintage values/timestamps are NOT verified. Retrospective issuer snapshots may have changed. CFTC normal +7d is a conservative proxy; shutdown exceptions use the recorded issuer release schedule. These are not trade-ready PIT signals.
- The known bad 2026-02-27 price and affected target/feature windows remain quarantined in the unchanged V8 source. 2026 cases were already observed during research, so 2026 does not establish genuinely blind model-design performance. False 2026 March and August alarms are not a basis to retune thresholds.
- SLV Good Friday 2024-03-29 and Sunday 2024-03-31 were NOT counted as market sessions and their missing share observations were NOT zero-filled. Date gaps invalidate crossing share-change windows.
- **10/10 unit and leakage/test gates passed.** The full V9 package was unpacked into a new directory and re-executed; byte-for-byte identical `audit.json`, `paired_results.csv`, and daily score CSV SHA256s.
- **NO Neon writes; NO live app changes; NO deployment; NO winner.** Preserve BASE14 reference.

## Reproduction

The packaged local experiment contains `gold_risk_v9_ablation.py`, `gold_risk_cftc_v8.py`, `gold_risk_release_clock_v8.py`, `gold_risk_asof_audit_20261026.py`, `test_v9.py`, six original source files, source overlay zip, CFTC CSV, 994-date source-feature panel, and result files.

Commands after unpacking:
```bash
python -m pip install numpy scikit-learn
python gold_risk_v9_ablation.py
python -m unittest discover -p test_v9.py -v
```

This experiment's runnable full input+output archive was also generated in the current ChatGPT turn as `gold_risk_v9_13_model_karsilastirma_20261026.zip`.

**Decision:** New features do not demonstrate a reliable improvement; do not replace BASE14. Continue independent first-print historical release verification and use future untouched dates to evaluate any model-selection criterion.