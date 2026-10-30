-- 30 Oct 2026: append-only public-source reference; never overwrites canonical NY17.
CREATE TABLE IF NOT EXISTS gold_weekly_live.staktrakr_daily_utc_reference_v1 (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  metal text NOT NULL CHECK (metal IN ('AU','AG','PT','PD')),
  price_date date NOT NULL,
  spot_usd_oz numeric(20,8) NOT NULL CHECK (spot_usd_oz > 0),
  source_row_timestamp text NOT NULL,
  source_event text,
  upstream_provider text,
  source_row_sha256 text NOT NULL CHECK (source_row_sha256 ~ '^[a-f0-9]{64}$'),
  raw_snapshot_sha256 text NOT NULL CHECK (raw_snapshot_sha256 ~ '^[a-f0-9]{64}$'),
  source_url text NOT NULL,
  first_observed_utc timestamptz NOT NULL DEFAULT now(),
  evidence_class text NOT NULL DEFAULT 'PUBLIC_API_FETCH_NOT_ORIGIN_PIT'
    CHECK (evidence_class='PUBLIC_API_FETCH_NOT_ORIGIN_PIT'),
  price_reference text NOT NULL DEFAULT 'STAKTRAKR_UTC_DAILY_REFERENCE_NOT_NY17'
    CHECK (price_reference='STAKTRAKR_UTC_DAILY_REFERENCE_NOT_NY17'),
  CONSTRAINT staktrakr_raw_daily_revision UNIQUE (metal,price_date,source_row_sha256)
);
