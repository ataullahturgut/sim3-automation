# GOLD H3 — Historical Futures Archive Recovery Audit V2

**Conclusion:** **NO_RAW_2023_2024_FIVE_CHANNEL_PANEL_FOUND**

V2 corrects V1 false positives by excluding source code/docs and requiring a data-like file with all five channel names plus at least 20 dated 2023/2024 records.

## Git history
- all branches fetched: **True**
- unique CSV/TSV/JSON/TXT blobs scanned: **1369**
- raw old five-channel candidates: **0**
- LFS pointer candidates: **0**

## Retained Actions artifacts
- repository artifacts enumerated: **1639**
- tightly relevant non-expired artifacts selected: **43**
- inspected: **43**
- raw old five-channel members found: **0**

## Scientific interpretation
- Python scripts that merely mention GC=F/SI=F/NQ=F/ZN=F/CL=F are not counted as data.
- A candidate is counted only when the actual stored data body has all five channels and repeated 2023/2024 date records.
- No model thresholds or DPTC rules are changed by this audit.
