"""Research-side, fail-closed availability clock for existing gold risk replay.

H.10's official weekly schedule is Monday 16:15 America/New_York,
Tuesday at 16:15 if Monday is a Federal Reserve holiday.
Explicit 2023-2026 Monday closures are derived from Fed release dates:
https://www.federalreserve.gov/releases/h10/ and official Fed holiday schedules.
The dates certify a scheduling rule, NOT the first published numerical vintage.
Decision date strings are interpreted as 17:30 New York, matching BASE14.
For earlier-in-day decisions ALWAYS pass an aware datetime.
"""
from __future__ import annotations
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo('America/New_York')
TR = ZoneInfo('Europe/Istanbul')
# Explicit MONDAY Fed closures, 2023-26, not generic US Federal/OPM dates.
# Verified against https://www.federalreserve.gov/releases/h10/default.htm
FED_H10_CLOSED_MONDAYS = frozenset(date.fromisoformat(x) for x in (
    '2023-01-02','2023-01-16','2023-02-20','2023-05-29',
    '2023-06-19','2023-09-04','2023-10-09','2023-12-25',
    '2024-01-01','2024-01-15','2024-02-19','2024-05-27',
    '2024-09-02','2024-10-14','2024-11-11',
    '2025-01-20','2025-02-17','2025-05-26',
    '2025-09-01','2025-10-13',
    '2026-01-19','2026-02-16','2026-05-25',
    '2026-09-07','2026-10-12'
))

def asof_instant(issue: str | date | datetime) -> datetime:
    """Naive issue dates mean NY17:30 *only* for existing after-close model."""
    if isinstance(issue,datetime):
        if issue.tzinfo is None or issue.utcoffset() is None:
            raise ValueError('naive datetime cannot establish public availability')
        return issue.astimezone(NY)
    if isinstance(issue,str): issue=date.fromisoformat(issue)
    if not isinstance(issue,date):raise TypeError('issue must be date, YYYY-MM-DD or aware datetime')
    return datetime.combine(issue,time(17,30),NY)

def next_h10_publication(observation: str | date) -> datetime:
    """Earliest conservative weekly *scheduled* release, at NY16:15.

    Source numeric vintages are explicitly unverified. An unsupported release
    year is a fatal error, not a speculative fallback to Monday.
    """
    d=date.fromisoformat(observation) if isinstance(observation,str) else observation
    if not isinstance(d,date) or isinstance(d,datetime):raise TypeError('observation date required')
    next_monday=d+timedelta(days=(7-d.weekday()) % 7 or 7)
    if not (2023<=next_monday.year<=2026):
        raise ValueError('H10_RELEASE_CALENDAR_OUT_OF_COVERAGE')
    # Fed H10 is released Tuesday when Monday is a Fed holiday.
    published=next_monday+timedelta(days=1) if next_monday in FED_H10_CLOSED_MONDAYS else next_monday
    return datetime.combine(published,time(16,15),NY)

def h10_is_available(observation: str | date, issue: str | date | datetime) -> bool:
    return next_h10_publication(observation) <= asof_instant(issue)

def h15_previous_day_is_available(observation: str | date, issue: str | date | datetime) -> bool:
    """Preserve incumbent BASE14 previous-calendar-day restriction.

    H15 official at NY16:15 of observation date; previous-day cutoff is a
    deliberately more conservative incumbent feature contract.
    """
    d=date.fromisoformat(observation) if isinstance(observation,str) else observation
    when=asof_instant(issue)
    return d < when.date() and datetime.combine(d,time(16,15),NY)<=when

def cftc_conservative_is_available(eligible_day: str | date, issue: str | date | datetime) -> bool:
    """Conservative +7d or publication+1d gate; never treat report Tuesday as release."""
    d=date.fromisoformat(eligible_day) if isinstance(eligible_day,str) else eligible_day
    return datetime.combine(d,time(0,0),NY)<=asof_instant(issue)

def cftc_published_is_available(official_release_day: str | date, issue: str | date | datetime) -> bool:
    """Use only for official CONFIRMED public releases, NY15:30 on that day."""
    d=date.fromisoformat(official_release_day) if isinstance(official_release_day,str) else official_release_day
    return datetime.combine(d,time(15,30),NY)<=asof_instant(issue)
