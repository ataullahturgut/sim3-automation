# R11C — Monthly price target mechanism test (registered after signed DAY/OVN R11/R11B failure, before R11C target outcomes)
Do NOT modify or overwrite frozen primary monthly ChHHO-ANFIS `GOLD_MONTHLY_PROJECT_MANIFEST.md` or claim new H1 champion based on single selection-sensitive 33DEV months. Goal: see whether the same previously completed month Au/Ag/Pt/Pd MR/GPR-VW low-frequency representations carry value on MONTHLY AVERAGE PRICE while failing bank session UP/DOWN.

As-of info: for target month t, origin p=t-1 fully completed Stak daily research Au/Ag/Pt/Pd data and historic GPR vintage p + lag gpr pp=p-1 (same feature gates as R11). Label t monthly XAU/USD from frozen `CORE5_GOLD_USD_OZ_RESEARCH_R1` (WorldBank research monthly core5); no target-month features. Price origin `O_p` = mean of Stak-trakr daily Gold observations in completed origin p, NOT WorldBank p because WB p may not have been published at forecast issue. `Stak` historical observations were re-imported in 2026-09, hence source-latency first-print NOT proved for 2022–25; this is retrospective mechanism, NOT production forecast.
NO optimizer tuned to 2025/2026 or RETROSPECTIVE selection: locked candidates:
(1) `RW_STAK`: forecast `O_p`.
(2) `MOM_GOLD_25`: `O_p * exp(0.25* AuMR_p)`.
(3) `MOM_GOLD_50`: `O_p * exp(0.50*AuMR_p)`.
(4) `MOM_METALS_25`: `O_p * exp(0.25*mean(AuMR,AgMR,PtMR,PdMR)_p)`.
(5) `GPR_GOLD_VW_25`: `O_p * exp(0.25*(n_p-1)*AuVW_GPR_p)`, using previous month's daily GPR-MIDAS VW scaled to monthly total daily return equivalent, origin no-target.
Compare at identical dates 2022-04..2024-12 canonical DEV n33 if source-complete and 2025 Jan–Dec exposed vs 2026 Jan–Jul exposed, by mean and sum absolute USD price error, MAPE, sign from Stak origin vs target WB, worst month, annual, paired wins vs RW_STAK. Historical frozen ChHHO dev reference ΣAE1413.03, MAE42.82 direction23/33 uses different level/proxy as-of contexts and cannot be equated without parity. Any simple contender that beats RW_STAK but does not match ChHHO on fully governed parity does not replace monthly authority.
No blending/switching or regime HMM membership from model errors, original monthly HMM frozen13 states separate market-only.
