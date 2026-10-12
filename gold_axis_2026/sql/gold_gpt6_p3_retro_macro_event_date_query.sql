SELECT series_id,to_char(observation_ts,'YYYY-MM-DD') event_date, to_char(available_as_of,'YYYY-MM-DD"T"HH24:MI:SS"Z"') first_print_utc
FROM observations WHERE series_id IN ('MACRO_CPI_ACTUAL_FIRST_PRINT','MACRO_NFP_ACTUAL_FIRST_PRINT')
AND observation_ts>='2020-01-01' AND observation_ts<'2026-01-01' ORDER BY observation_ts,series_id;
