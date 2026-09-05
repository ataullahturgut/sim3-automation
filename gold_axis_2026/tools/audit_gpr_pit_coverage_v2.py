from __future__ import annotations

import argparse
import calendar
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

OFFICIAL_WEB = "https://www.matteoiacoviello.com/gpr_files"
ARCHIVE_DIR = "gpr_archive_files"
NY = ZoneInfo("America/New_York")
UTC = timezone.utc


@dataclass(frozen=True)
class CoverageRow:
    origin_month: str
    expected_filename: str
    expected_web_url: str
    origin_cutoff_utc: str
    direct_http_status: int | None
    direct_http_present: bool
    repo_current_xls: bool
    repo_ever_xls: bool
    repo_earliest_add_utc: str | None
    repo_git_pit_proven: bool
    repo_current_dta: bool
    repo_ever_dta: bool
    repo_dta_earliest_add_utc: str | None
    v1_source_ready: bool
    pit_status: str


def month_range(start: str, end: str) -> list[str]:
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    out: list[str] = []
    y, m = sy, sm
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y += 1
            m = 1
    return out


def origin_cutoff(month: str) -> datetime:
    y, m = map(int, month.split("-"))
    last_day = calendar.monthrange(y, m)[1]
    local = datetime(y, m, last_day, 17, 0, 0, tzinfo=NY)
    return local.astimezone(UTC)


def http_status(url: str, timeout: int = 20) -> int | None:
    # GET is intentional: the official host has not always treated HEAD consistently.
    req = Request(url, headers={"User-Agent": "Gold-Control-GPR-PIT-Audit/2.0", "Range": "bytes=0-0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return int(getattr(resp, "status", 200))
    except HTTPError as exc:
        return int(exc.code)
    except (URLError, TimeoutError, OSError):
        return None


def git(*args: str, cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, timeout=90
    )
    return proc.stdout.strip()


def path_current(repo: Path, rel: str) -> bool:
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{rel}"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return proc.returncode == 0


def earliest_add(repo: Path, rel: str) -> str | None:
    # --all matters because an archived file can have been deleted from current master.
    out = git("log", "--all", "--diff-filter=A", "--format=%cI", "--", rel, cwd=repo)
    dates = [x.strip() for x in out.splitlines() if x.strip()]
    if not dates:
        return None
    parsed = sorted(datetime.fromisoformat(x.replace("Z", "+00:00")).astimezone(UTC) for x in dates)
    return parsed[0].isoformat().replace("+00:00", "Z")


def ever_exists(repo: Path, rel: str) -> bool:
    return earliest_add(repo, rel) is not None


def parse_utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def audit(repo: Path, start: str, end: str, skip_http: bool) -> list[CoverageRow]:
    rows: list[CoverageRow] = []
    for month in month_range(start, end):
        compact = month.replace("-", "")
        xls = f"data_gpr_export_{compact}.xls"
        dta = f"data_gpr_export_{compact}.dta"
        xls_rel = f"{ARCHIVE_DIR}/{xls}"
        dta_rel = f"{ARCHIVE_DIR}/{dta}"
        cutoff = origin_cutoff(month)
        status = None if skip_http else http_status(f"{OFFICIAL_WEB}/{xls}")
        xls_add = earliest_add(repo, xls_rel)
        dta_add = earliest_add(repo, dta_rel)
        xls_add_dt = parse_utc(xls_add)
        git_pit = bool(xls_add_dt is not None and xls_add_dt <= cutoff)
        direct_present = bool(status is not None and 200 <= status < 300)
        v1_ready = direct_present and git_pit
        if v1_ready:
            pit_status = "PROVEN_OFFICIAL_GIT_BY_ORIGIN_AND_CURRENT_DIRECT_RETRIEVABLE"
        elif git_pit and not direct_present:
            pit_status = "PIT_GIT_PROVEN_BUT_FROZEN_DIRECT_SOURCE_NOT_RETRIEVABLE_NOW"
        elif xls_add is not None:
            pit_status = "NOT_PROVEN_GIT_ARCHIVE_ADD_AFTER_ORIGIN"
        else:
            pit_status = "NOT_PROVEN_NO_OFFICIAL_GIT_ARCHIVE_XLS_HISTORY"
        rows.append(CoverageRow(
            origin_month=month,
            expected_filename=xls,
            expected_web_url=f"{OFFICIAL_WEB}/{xls}",
            origin_cutoff_utc=cutoff.isoformat().replace("+00:00", "Z"),
            direct_http_status=status,
            direct_http_present=direct_present,
            repo_current_xls=path_current(repo, xls_rel),
            repo_ever_xls=xls_add is not None,
            repo_earliest_add_utc=xls_add,
            repo_git_pit_proven=git_pit,
            repo_current_dta=path_current(repo, dta_rel),
            repo_ever_dta=dta_add is not None,
            repo_dta_earliest_add_utc=dta_add,
            v1_source_ready=v1_ready,
            pit_status=pit_status,
        ))
    return rows


def summarize(rows: list[CoverageRow]) -> dict:
    n = len(rows)
    ready = sum(r.v1_source_ready for r in rows)
    direct = sum(r.direct_http_present for r in rows)
    git_ever = sum(r.repo_ever_xls for r in rows)
    git_pit = sum(r.repo_git_pit_proven for r in rows)
    dta_ever = sum(r.repo_ever_dta for r in rows)
    return {
        "required": n,
        "direct_http_present": direct,
        "repo_ever_xls": git_ever,
        "repo_git_pit_proven_xls": git_pit,
        "repo_ever_dta": dta_ever,
        "v1_source_ready": ready,
        "v1_binding_result": "PASS_72_OF_72" if ready == n == 72 else "SOURCE_BLOCKED_NO_MODEL_SCORE",
        "missing_or_not_pit_proven": [r.origin_month for r in rows if not r.v1_source_ready],
    }


def write_markdown(path: Path, rows: list[CoverageRow], summary: dict) -> None:
    lines = [
        "# GPR PIT Coverage Audit V2",
        "",
        f"- Required origins: **{summary['required']}**",
        f"- Direct official `.xls` retrievable now: **{summary['direct_http_present']}**",
        f"- Official Git history ever contains `.xls`: **{summary['repo_ever_xls']}**",
        f"- Official Git `.xls` added by the corresponding 17:00 ET month-end origin: **{summary['repo_git_pit_proven_xls']}**",
        f"- Frozen V1 source-ready origins: **{summary['v1_source_ready']}**",
        f"- Binding V1 result: **{summary['v1_binding_result']}**",
        "",
        "Current archive presence and origin-time availability are deliberately reported separately. A later archive upload is not treated as PIT proof.",
        "",
        "| Origin | HTTP | Git ever xls | Earliest add UTC | PIT by origin | V1 ready | Status |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.origin_month} | {r.direct_http_status if r.direct_http_status is not None else 'ERR'} | "
            f"{'Y' if r.repo_ever_xls else 'N'} | {r.repo_earliest_add_utc or '-'} | "
            f"{'Y' if r.repo_git_pit_proven else 'N'} | {'Y' if r.v1_source_ready else 'N'} | {r.pit_status} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--upstream-repo", type=Path, required=True)
    p.add_argument("--start", default="2020-09")
    p.add_argument("--end", default="2026-08")
    p.add_argument("--json-out", type=Path, default=Path("gpr_pit_coverage_v2.json"))
    p.add_argument("--md-out", type=Path, default=Path("gpr_pit_coverage_v2.md"))
    p.add_argument("--skip-http", action="store_true")
    p.add_argument("--strict", action="store_true", help="exit nonzero unless all 72 frozen V1 origins pass")
    args = p.parse_args()
    if not (args.upstream_repo / ".git").exists():
        raise SystemExit("UPSTREAM_REPO_IS_NOT_A_GIT_CLONE")
    rows = audit(args.upstream_repo, args.start, args.end, args.skip_http)
    summary = summarize(rows)
    payload = {"summary": summary, "rows": [asdict(r) for r in rows]}
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(args.md_out, rows, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.strict and summary["v1_binding_result"] != "PASS_72_OF_72":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
