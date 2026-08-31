-- GOLD_DATA_R2.6_2026-08-31
-- Point-in-time safety patch.
--
-- canonical_latest is intentionally a CURRENT-state convenience view. It must
-- never be used to reconstruct a historical forecast origin because later
-- provider revisions may be visible there. Historical model code must call
-- observations_as_of(origin_ts) or consume an immutable forecast_input_snapshot.

CREATE OR REPLACE FUNCTION observations_as_of(p_as_of timestamptz)
RETURNS TABLE (
    id bigint,
    series_id text,
    observation_ts timestamptz,
    value double precision,
    source text,
    source_symbol text,
    provider_as_of timestamptz,
    available_as_of timestamptz,
    first_seen_at timestamptz,
    retrieved_at timestamptz,
    frequency text,
    unit text,
    transform text,
    quality_status text,
    lineage_id text,
    payload_hash text,
    metadata jsonb
)
LANGUAGE sql
STABLE
AS $$
    SELECT DISTINCT ON (o.series_id, o.observation_ts, o.lineage_id)
        o.id,
        o.series_id,
        o.observation_ts,
        o.value,
        o.source,
        o.source_symbol,
        o.provider_as_of,
        o.available_as_of,
        o.first_seen_at,
        o.retrieved_at,
        o.frequency,
        o.unit,
        o.transform,
        o.quality_status,
        o.lineage_id,
        o.payload_hash,
        o.metadata
    FROM observations o
    WHERE o.retrieved_at <= p_as_of
      AND o.available_as_of <= p_as_of
      AND o.quality_status NOT IN ('ERROR', 'REJECTED', 'INVALID', 'INVALID_AVAILABILITY_LEGACY')
      -- Early R2 Cboe rows incorrectly used the observation date as their
      -- availability timestamp even though historical publication timestamps
      -- were not reconstructed. Keep those raw rows for audit, but make them
      -- ineligible for every point-in-time query.
      AND NOT (
          o.series_id IN ('GVZ_CBOE', 'VIX_CBOE')
          AND COALESCE(o.metadata->>'availability_policy', '')
              NOT IN ('first_retrieval_floor', 'retrieval_time_floor')
      )
    ORDER BY
        o.series_id,
        o.observation_ts,
        o.lineage_id,
        o.retrieved_at DESC,
        o.id DESC;
$$;

CREATE OR REPLACE FUNCTION latest_series_as_of(p_as_of timestamptz)
RETURNS TABLE (
    id bigint,
    series_id text,
    observation_ts timestamptz,
    value double precision,
    source text,
    source_symbol text,
    provider_as_of timestamptz,
    available_as_of timestamptz,
    first_seen_at timestamptz,
    retrieved_at timestamptz,
    frequency text,
    unit text,
    transform text,
    quality_status text,
    lineage_id text,
    payload_hash text,
    metadata jsonb
)
LANGUAGE sql
STABLE
AS $$
    SELECT DISTINCT ON (q.series_id, q.lineage_id)
        q.id,
        q.series_id,
        q.observation_ts,
        q.value,
        q.source,
        q.source_symbol,
        q.provider_as_of,
        q.available_as_of,
        q.first_seen_at,
        q.retrieved_at,
        q.frequency,
        q.unit,
        q.transform,
        q.quality_status,
        q.lineage_id,
        q.payload_hash,
        q.metadata
    FROM observations_as_of(p_as_of) q
    ORDER BY
        q.series_id,
        q.lineage_id,
        q.observation_ts DESC,
        q.retrieved_at DESC,
        q.id DESC;
$$;

CREATE OR REPLACE VIEW usable_observations AS
SELECT
    series_id,
    observation_ts,
    value,
    source,
    source_symbol,
    provider_as_of,
    available_as_of,
    first_seen_at,
    retrieved_at,
    frequency,
    unit,
    transform,
    quality_status,
    lineage_id,
    metadata
FROM canonical_latest
WHERE quality_status NOT IN ('ERROR', 'REJECTED', 'INVALID', 'INVALID_AVAILABILITY_LEGACY')
  AND NOT (
      series_id IN ('GVZ_CBOE', 'VIX_CBOE')
      AND COALESCE(metadata->>'availability_policy', '')
          NOT IN ('first_retrieval_floor', 'retrieval_time_floor')
  );

COMMENT ON VIEW canonical_latest IS
'CURRENT latest provider-lineage state only. NOT point-in-time safe for historical backtests; use observations_as_of(origin_ts).';

COMMENT ON VIEW usable_observations IS
'CURRENT quality-filtered state only. NOT point-in-time safe for historical backtests; use observations_as_of(origin_ts).';

COMMENT ON FUNCTION observations_as_of(timestamptz) IS
'Point-in-time observation surface: returns only data retrieved and available by p_as_of, selecting the latest then-known revision per provider lineage.';

COMMENT ON FUNCTION latest_series_as_of(timestamptz) IS
'Point-in-time latest observation per provider lineage at p_as_of.';

INSERT INTO system_metadata (key, value)
VALUES
    ('schema_version', 'GOLD_DATA_R2.6_2026-08-31'),
    ('historical_query_contract', 'USE observations_as_of(origin_ts); canonical_latest is current-state only')
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value, updated_at = now();
