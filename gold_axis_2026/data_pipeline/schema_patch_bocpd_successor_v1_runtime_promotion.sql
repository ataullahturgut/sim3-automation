-- GOLD_CONTROL_BOCPD_SUCCESSOR_V1_RUNTIME_PROMOTION
-- Change-control: GOLD_CONTROL_BOCPD_SUCCESSOR_V1_PROMOTION_CHANGE_CONTROL_2026-09-05.md
-- Purpose: permit the separately named BOCPD successor identity in the append-only engine runtime ledger.
-- This migration does not delete or rewrite archived BOCPD rows.

ALTER TABLE public.engine_execution_runs
    DROP CONSTRAINT IF EXISTS engine_execution_runs_engine_id_check;

ALTER TABLE public.engine_execution_runs
    ADD CONSTRAINT engine_execution_runs_engine_id_check
    CHECK (
        engine_id IN (
            'CAUSAL_PATCH',
            'VW_MIDAS_MSVR',
            'MOMENTUM_3M',
            'RANDOM_WALK',
            'MONTHLY_DIRECTION_3M',
            'FAST',
            'SLOW',
            'MACRO_EVENT',
            'EMERGENCY_LEVEL',
            'EMERGENCY_REVERSAL',
            'BOCPD',
            'BOCPD_RETURN_SUCCESSOR_V1',
            'GVZ_RISK'
        )
    );

-- Historical BOCPD remains a valid archived ledger identity.
-- Current governed application registry replaces its runtime slot with
-- BOCPD_RETURN_SUCCESSOR_V1. Runtime state transition rows are append-only.
