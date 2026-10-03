# GOLD H3 NEON DATABASE INTEGRITY AUDIT — 2026-10-03

**Mode:** READ ONLY. No database rows were changed.

## Inventory

- user tables: **32**
- observation series: **63**
- series with duplicate observation timestamps: **14**
- duplicate timestamp groups inspected: **1910**
- duplicate groups with conflicting values: **374**

## Binding H3 hourly XAU source

- series: `XAU_USD_TWELVE_1H_RESEARCH_V1`
- deduped rows: **17644**
- range: **2022-01-02 23:00:00+00:00 -> 2024-12-31 21:00:00+00:00**
- timestamps with >1 stored revision: **0**
- abs 1h log-return >=2.5% candidates: **0**
- robust |z|>=8 return outliers: **68**
- gaps >4h: **158**
- max abs adjacent log return: **2.411%**

## Largest primary XAU jump candidates

| Timestamp | Prev timestamp | Prev | Value | Log return | Revision n |
|---|---|---:|---:|---:|---:|

## Primary XAU conflicting revisions

- none

## Governance

Jump and gap flags are screening candidates, not automatic data errors. Any flagged H3 source point must be independently cross-checked against the original provider before correction.
