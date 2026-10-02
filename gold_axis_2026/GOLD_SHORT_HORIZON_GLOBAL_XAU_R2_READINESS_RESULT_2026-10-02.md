# GOLD SHORT-HORIZON GLOBAL XAU — R2 Data Readiness

**Status:** **PASS**

Identity: **GLOBAL_XAU_PUBLIC_STAKTRAKR_R2**
Pinned StakTrakr commit: 54fdf1c8d39b7b6c7b874d0f30f784296e886044
Public common weekday coverage: 2010-01-04 .. 2026-09-29 (n=4233)

R2 is a full-history reconstruction at one pinned public StakTrakr commit. It is not a silent append to the prior Neon snapshot.

## CORE3 coverage

| H | Train | DEV | 2025 | Opened 2026 | Last issue |
|---|---:|---:|---:|---:|---|
| H1 | 3010 | 755 | 253 | 193 | 2026-09-29 |
| H3 | 3010 | 755 | 253 | 191 | 2026-09-25 |
| H5 | 3010 | 755 | 253 | 189 | 2026-09-23 |

## Gate
{
  "dev_ge_700": true,
  "train_ge_2000": true,
  "transport_2025_ge_200": true,
  "aug_sep_2026_present": true
}
