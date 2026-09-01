-- GOLD_CONTROL_FORECAST_STATE_APPEND_ONLY_V1_2026-09-01
-- Enforce the manifest's immutable forecast-state contract at the database layer.
-- INSERT is allowed; UPDATE and DELETE are rejected for issued forecast inputs,
-- derived features, and monthly forecast contracts.

CREATE OR REPLACE FUNCTION reject_gold_control_forecast_state_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'IMMUTABLE_FORECAST_STATE_MUTATION_REJECTED table=% operation=%', TG_TABLE_NAME, TG_OP
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_forecast_input_snapshots_immutable
    ON forecast_input_snapshots;
CREATE TRIGGER trg_forecast_input_snapshots_immutable
BEFORE UPDATE OR DELETE ON forecast_input_snapshots
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_forecast_state_mutation();

DROP TRIGGER IF EXISTS trg_derived_feature_snapshots_immutable
    ON derived_feature_snapshots;
CREATE TRIGGER trg_derived_feature_snapshots_immutable
BEFORE UPDATE OR DELETE ON derived_feature_snapshots
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_forecast_state_mutation();

DROP TRIGGER IF EXISTS trg_monthly_forecast_contracts_immutable
    ON monthly_forecast_contracts;
CREATE TRIGGER trg_monthly_forecast_contracts_immutable
BEFORE UPDATE OR DELETE ON monthly_forecast_contracts
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_forecast_state_mutation();

COMMENT ON FUNCTION reject_gold_control_forecast_state_mutation() IS
'Gold Control forecast-state append-only guard. Issued rows may be inserted but not updated or deleted.';
