from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCORE=ROOT/'data_pipeline'/'macro_event_successor_v3_existing_channels_r2.py'
BACKFILL=ROOT/'data_pipeline'/'macro_event_successor_v3_inflation_channel_backfill_r2.py'


def test_score_layer_has_no_http_provider_client():
    text=SCORE.read_text(encoding='utf-8')
    assert 'import requests' not in text
    assert 'investing.com' not in text.lower()
    assert 'stlouisfed.org' not in text.lower()


def test_score_layer_pins_frozen_employment_source():
    text=SCORE.read_text(encoding='utf-8')
    assert '6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a' in text
    assert 'EMPLOYMENT_FROZEN_SOURCE_ROW_COUNT_DRIFT' in text


def test_inflation_uses_existing_governed_series_ids():
    text=BACKFILL.read_text(encoding='utf-8')
    for sid in ['MACRO_CPI_ACTUAL_FIRST_PRINT','MACRO_CPI_CONSENSUS_PIT',
                'MACRO_CORE_CPI_ACTUAL_FIRST_PRINT','MACRO_CORE_CPI_CONSENSUS_PIT']:
        assert sid in text
    assert 'source_channel_reuse' in text


def test_market_shock_is_never_mutated():
    text=SCORE.read_text(encoding='utf-8')
    assert '"market_shock_threshold_changed":False' in text
    assert '"raw_market_shock_episode_changed":False' in text
