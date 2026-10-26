#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m zipfile -e frozen_inputs.zip inputs
mkdir -p outputs
python gold_risk_cftc_v8_fixed.py --source-zip inputs/source.zip --cftc-csv inputs/CFTC_GC_SI_2023_2026_QUALITY_GATED.csv --outdir outputs/replay > outputs/replay.log
python research.py > outputs/run.log
python audit_outputs.py > outputs/additional_audit.log
python -m unittest test_research -v > outputs/tests.log 2>&1
