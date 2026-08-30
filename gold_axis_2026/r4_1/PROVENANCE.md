# Provenance

## Existing SIM3 Gold lineage retained in-place

Branch base: `tmp-gold-2026-model-test`.
Existing historical files remain under `gold_axis_2026/`, including:

- `run_august_2026.py`
- `run_models.py`
- `run_models_2023_2024.py`
- `run_models_2025.py`
- `run_vw_direct_h1_h5.py`
- `run_vw_direct_h1_h5_fast.py`
- `run_vw_full_rebuild.py`
- `run_vw_full_rebuild_v2.py`
- `monthly_predictions_2023_2026.csv`
- `results_2026.csv`
- `summary_2026.json`

## R4.1 addition

`gold_axis_2026/r4_1/` was frozen on 2026-08-30 from the latest audited conversation architecture:

- VW analytical primary + 3M monthly direction prior;
- Fast daily SMA20 / 2-market-day persistence;
- Slow completed-weekly SMA4 / 2-completed-week persistence;
- Emergency Level +/-4%;
- Reversal Emergency +/-4% from running extreme, ALERT_ONLY;
- GVZ caps 25.9795 / 30.5238;
- BOCPD-return context only;
- no 2026 threshold tuning.

The older SIM3 Gold files are not overwritten or relabeled as R4.1. This directory is an additive, versioned layer.
