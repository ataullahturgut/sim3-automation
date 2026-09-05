from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "data_pipeline" / "macro_event_successor_v1_sources.py"
spec = importlib.util.spec_from_file_location("macro_event_successor_v1_sources", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def wrap(body: str) -> str:
    return f"<html><body>{body}</body></html>"


def test_parse_recent_release_explicit_ahe_percent():
    html = wrap(
        "Transmission of material in this release is embargoed until 8:30 a.m. (EDT) Friday, September 4, 2026 "
        "THE EMPLOYMENT SITUATION -- AUGUST 2026 "
        "Total nonfarm payroll employment increased by 162,000 in August, and the unemployment rate was unchanged at 4.1 percent. "
        "In August, average hourly earnings for all employees on private nonfarm payrolls rose by 10 cents, or 0.3 percent, to $37.75."
    )
    p = mod.parse_release("https://www.bls.gov/news.release/archives/empsit_09042026.htm", html)
    assert p.reference_month == "2026-08"
    assert p.nfp_thousands == 162.0
    assert p.unemployment_pct == 4.1
    assert p.ahe_mom_pct == 0.3
    assert p.ahe_transform == "PUBLISHED_MOM_PERCENT"
    assert p.release_ts.hour == 8 and p.release_ts.minute == 30


def test_parse_2016_release_derived_ahe_percent():
    html = wrap(
        "8:30 a.m. (EDT) Friday, July 8, 2016 THE EMPLOYMENT SITUATION -- JUNE 2016 "
        "Total nonfarm payroll employment increased by 287,000 in June, and the unemployment rate rose to 4.9 percent. "
        "In June, average hourly earnings for all employees on private nonfarm payrolls edged up (+2 cents) to $25.61."
    )
    p = mod.parse_release("https://www.bls.gov/news.release/archives/empsit_07082016.htm", html)
    assert p.reference_month == "2016-06"
    assert p.nfp_thousands == 287.0
    assert p.unemployment_pct == 4.9
    expected = (25.61 / 25.59 - 1.0) * 100.0
    assert abs(p.ahe_mom_pct - expected) < 1e-12
    assert p.ahe_transform == "DERIVED_FROM_FIRST_RELEASE_CENTS_AND_LEVEL"


def test_parse_changed_little_positive_nfp():
    html = wrap(
        "THE EMPLOYMENT SITUATION -- MAY 2016 "
        "The unemployment rate declined by 0.3 percentage point to 4.7 percent in May, and nonfarm payroll employment changed little (+38,000). "
        "Average hourly earnings for all employees on private nonfarm payrolls increased by 5 cents to $25.59."
    )
    p = mod.parse_release("https://www.bls.gov/news.release/archives/empsit_06032016.htm", html)
    assert p.reference_month == "2016-05"
    assert p.nfp_thousands == 38.0
    assert p.unemployment_pct == 4.7
    expected = (25.59 / 25.54 - 1.0) * 100.0
    assert abs(p.ahe_mom_pct - expected) < 1e-12


def test_parse_negative_nfp_and_ahe():
    text = (
        "THE EMPLOYMENT SITUATION -- JANUARY 2020 "
        "Total nonfarm payroll employment declined by 20,000 in January, and the unemployment rate was 3.6 percent. "
        "Average hourly earnings for all employees on private nonfarm payrolls declined by 0.2 percent to $28.00."
    )
    p = mod.parse_release("https://www.bls.gov/news.release/archives/empsit_02072020.htm", wrap(text))
    assert p.nfp_thousands == -20.0
    assert p.unemployment_pct == 3.6
    assert p.ahe_mom_pct == -0.2


def test_observation_chronology_truth():
    release_ts = mod.release_ts_from_url("https://www.bls.gov/news.release/archives/empsit_09042026.htm")
    retrieved = mod.datetime(2026, 9, 5, 15, 0, tzinfo=mod.timezone.utc)
    o = mod.make_observation(
        "00000000-0000-0000-0000-000000000000",
        "MACRO_NFP_ACTUAL_FIRST_PRINT",
        release_ts,
        162.0,
        "thousand_persons_change",
        retrieved,
        "a" * 64,
        "2026-08",
        "https://www.bls.gov/news.release/archives/empsit_09042026.htm",
        "first_print_release_value",
    )
    assert o["provider_as_of"] == o["available_as_of"]
    assert o["retrieved_at"] == o["first_seen_at"]
    assert o["provider_as_of"] < o["retrieved_at"]
    assert o["metadata"]["historical_reconstruction_not_original_retrieval"] is True
    assert o["metadata"]["current_vintage_substitution"] is False
