"""Fail-closed source publication clocks for gold risk research replay.

Original numeric vintage is NOT certified by a publication schedule.
H10 is released NY 16:15 each Monday, next business day on a Fed Monday closure;
dates have been checked against official Fed H10 release list 2023-2026.
Date-only issue = existing after-close NY 17:30 risk origin. Morning decisions
MUST supply a timezone-aware datetime.
"""
from __future__ import annotations
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
NY=ZoneInfo('America/New_York')
TR=ZoneInfo('Europe/Istanbul')
FED_H10_CLOSED_MONDAYS=frozenset(date.fromisoformat(x) for x in (
 '2023-01-02','2023-01-16','2023-02-20','2023-05-29','2023-06-19','2023-09-04','2023-10-09','2023-12-25',
 '2024-01-01','2024-01-15','2024-02-19','2024-05-27','2024-09-02','2024-10-14','2024-11-11',
 '2025-01-20','2025-02-17','2025-05-26','2025-09-01','2025-10-13',
 '2026-01-19','2026-02-16','2026-05-25','2026-09-07','2026-10-12'
))
def asof_instant(issue: str | date | datetime) -> datetime:
 if isinstance(issue,datetime):
  if issue.tzinfo is None or issue.utcoffset() is None:
   raise ValueError('Naive decision datetime is not permitted')
  return issue.astimezone(NY)
 if isinstance(issue,str):issue=date.fromisoformat(issue)
 if not isinstance(issue,date):raise TypeError('date, YYYY-MM-DD or aware datetime required')
 return datetime.combine(issue,time(17,30),NY)

def next_h10_publication(observation: str | date) -> datetime:
 d=date.fromisoformat(observation) if isinstance(observation,str) else observation
 if not isinstance(d,date) or isinstance(d,datetime):raise TypeError('observation date required')
 monday=d+timedelta(days=(7-d.weekday())%7 or 7)
 if not (2023<=monday.year<=2026):raise ValueError('H10_RELEASE_CALENDAR_OUT_OF_COVERAGE')
 day=monday+timedelta(days=1) if monday in FED_H10_CLOSED_MONDAYS else monday
 return datetime.combine(day,time(16,15),NY)

def h10_is_available(observation, issue):
 return next_h10_publication(observation)<=asof_instant(issue)

def h15_previous_day_is_available(observation,issue):
 """Preserve incumbent previous-day restriction (more conservative than H15 NY16:15)."""
 d=date.fromisoformat(observation) if isinstance(observation,str) else observation
 issue=asof_instant(issue)
 return d<issue.date() and datetime.combine(d,time(16,15),NY)<=issue

def cftc_conservative_is_available(eligible_day,issue):
 """For preprocessed conservative GC/SI eligible date ONLY; NOT actual public release date."""
 d=date.fromisoformat(eligible_day) if isinstance(eligible_day,str) else eligible_day
 return datetime.combine(d,time(0,0),NY)<=asof_instant(issue)

def cftc_published_is_available(official_release_day,issue):
 """Verified official CFTC publication date at NY 15:30; NOT report Tuesday."""
 d=date.fromisoformat(official_release_day) if isinstance(official_release_day,str) else official_release_day
 return datetime.combine(d,time(15,30),NY)<=asof_instant(issue)
