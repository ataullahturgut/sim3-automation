from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PIPELINE_VERSION = "GOLD_GPR_VINTAGE_PIT_BACKFILL_V2_2026-09-05"
SERIES_ID = "GPR_OFFICIAL"
SOURCE_NAME = "Caldara-Iacoviello official GitHub archive"
SOURCE_SYMBOL = "GPR"
EVIDENCE_CLASS = "HISTORICAL_REPLAY_RECONSTRUCTION"
QUALITY_STATUS = "APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH"


@dataclass(frozen=True)
class VintageRecord:
    origin_month: str
    required_observation_month: str
    archive_path: str
    archive_commit_sha: str
    archive_commit_at: str
    payload_sha256: str
    row_count: int
    required_value_present: bool


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def git_bytes(repo: Path, commit: str, relpath: str) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{relpath}"],
        cwd=repo,
        check=True,
        capture_output=True,
        timeout=90,
    )
    return proc.stdout


def git_text(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True, timeout=90
    )
    return proc.stdout.strip()


def earliest_add_commit(repo: Path, relpath: str) -> tuple[str, datetime] | None:
    out = git_text(repo, "log", "--all", "--diff-filter=A", "--format=%H|%cI", "--", relpath)
    rows: list[tuple[str, datetime]] = []
    for line in out.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        sha, stamp = line.split("|", 1)
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc)
        rows.append((sha, dt))
    if not rows:
        return None
    rows.sort(key=lambda x: x[1])
    return rows[0]


def previous_month(month: str) -> str:
    p = pd.Period(month, freq="M") - 1
    return str(p)


def parse_gpr_workbook(raw: bytes) -> pd.DataFrame:
    sheets = pd.read_excel(io.BytesIO(raw), sheet_name=None, engine="xlrd")
    best: pd.DataFrame | None = None
    for _, df in sheets.items():
        cols = {str(c).strip().upper(): c for c in df.columns}
        if "GPR" not in cols:
            continue
        date_col = cols.get("MONTH") or cols.get("DATE") or df.columns[0]
        q = df[[date_col, cols["GPR"]]].copy()
        q.columns = ["date", "GPR"]
        q["date"] = pd.to_datetime(q["date"], errors="coerce")
        q["GPR"] = pd.to_numeric(q["GPR"], errors="coerce")
        q = q.dropna(subset=["date", "GPR"]).sort_values("date")
        q = q[q["GPR"] > 0].drop_duplicates("date", keep="last")
        if best is None or len(q) > len(best):
            best = q
    if best is None or best.empty:
        raise RuntimeError("GPR_SCHEMA_NOT_FOUND_OR_EMPTY")
    return best


def load_coverage(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise RuntimeError("COVERAGE_ROWS_MISSING")
    return rows


def build_bundle(repo: Path, coverage_path: Path, retrieved_at: datetime) -> tuple[dict, list[VintageRecord]]:
    coverage = load_coverage(coverage_path)
    run_id = str(uuid.uuid4())
    observations: list[dict] = []
    vintages: list[dict] = []
    quality_events: list[dict] = []
    records: list[VintageRecord] = []

    for c in coverage:
        origin = str(c["origin_month"])
        if not bool(c.get("repo_git_pit_proven")):
            quality_events.append({
                "run_id": run_id,
                "series_id": SERIES_ID,
                "event_ts": retrieved_at.isoformat(),
                "severity": "ERROR",
                "code": "GPR_VINTAGE_PIT_NOT_PROVEN",
                "message": f"Official Git archive does not prove vintage availability by origin {origin}",
                "metadata": {"origin_month": origin, "coverage_status": c.get("pit_status")},
            })
            continue

        compact = origin.replace("-", "")
        relpath = f"gpr_archive_files/data_gpr_export_{compact}.xls"
        add = earliest_add_commit(repo, relpath)
        if add is None:
            raise RuntimeError(f"COVERAGE_INCONSISTENT_NO_ADD_COMMIT:{origin}")
        commit_sha, commit_at = add
        raw = git_bytes(repo, commit_sha, relpath)
        payload_hash = hashlib.sha256(raw).hexdigest()
        df = parse_gpr_workbook(raw)
        required_month = previous_month(origin)
        origin_cutoff = pd.Timestamp(c["origin_cutoff_utc"]).to_pydatetime().astimezone(timezone.utc)
        if commit_at > origin_cutoff:
            raise RuntimeError(f"COVERAGE_INCONSISTENT_COMMIT_AFTER_ORIGIN:{origin}")

        usable = df[df["date"].dt.to_period("M") <= pd.Period(required_month, freq="M")].copy()
        required = usable[usable["date"].dt.to_period("M") == pd.Period(required_month, freq="M")]
        if required.empty:
            quality_events.append({
                "run_id": run_id,
                "series_id": SERIES_ID,
                "event_ts": retrieved_at.isoformat(),
                "severity": "ERROR",
                "code": "GPR_REQUIRED_P_MINUS_1_MISSING",
                "message": f"Vintage {origin} lacks required GPR observation {required_month}",
                "metadata": {"origin_month": origin, "required_observation_month": required_month, "archive_path": relpath},
            })
            continue

        lineage = f"GPR_OFFICIAL_GIT_VINTAGE_{compact}_{payload_hash[:12]}"
        for _, row in usable.iterrows():
            obs_month = pd.Timestamp(row["date"]).to_period("M").to_timestamp()
            observations.append({
                "run_id": run_id,
                "series_id": SERIES_ID,
                "observation_ts": obs_month.tz_localize("UTC").isoformat(),
                "value": float(row["GPR"]),
                "source": SOURCE_NAME,
                "source_symbol": SOURCE_SYMBOL,
                "provider_as_of": commit_at.isoformat(),
                "available_as_of": commit_at.isoformat(),
                "first_seen_at": retrieved_at.isoformat(),
                "retrieved_at": retrieved_at.isoformat(),
                "frequency": "monthly_vintage",
                "unit": "index",
                "transform": "LEVEL_FROM_ORIGIN_VINTAGE",
                "quality_status": QUALITY_STATUS,
                "lineage_id": lineage,
                "payload_hash": payload_hash,
                "metadata": {
                    "origin_month": origin,
                    "required_observation_month": required_month,
                    "archive_path": relpath,
                    "archive_commit_sha": commit_sha,
                    "archive_commit_at": commit_at.isoformat(),
                    "availability_policy": "official_git_archive_commit_floor",
                    "historical_reconstruction_not_original_retrieval": True,
                    "retrieval_time_not_backdated": True,
                    "evidence_class": EVIDENCE_CLASS,
                    "vintage_specific_lineage": True,
                },
            })

        vintages.append({
            "source_id": f"GPR_OFFICIAL_GIT_VINTAGE_{compact}",
            "retrieved_at": retrieved_at.isoformat(),
            "provider_as_of": commit_at.isoformat(),
            "content_sha256": payload_hash,
            "content_type": "application/vnd.ms-excel",
            "byte_count": len(raw),
            "metadata": {
                "origin_month": origin,
                "required_observation_month": required_month,
                "archive_path": relpath,
                "archive_commit_sha": commit_sha,
                "archive_commit_at": commit_at.isoformat(),
                "availability_policy": "official_git_archive_commit_floor",
                "evidence_class": EVIDENCE_CLASS,
            },
        })
        records.append(VintageRecord(
            origin_month=origin,
            required_observation_month=required_month,
            archive_path=relpath,
            archive_commit_sha=commit_sha,
            archive_commit_at=commit_at.isoformat(),
            payload_sha256=payload_hash,
            row_count=len(usable),
            required_value_present=True,
        ))

    bundle = {
        "run_id": run_id,
        "started_at": retrieved_at.isoformat(),
        "finished_at": utcnow().isoformat(),
        "pipeline_version": PIPELINE_VERSION,
        "mode": "historical_reconstruction:gpr_official_git_vintage",
        "evidence_class": EVIDENCE_CLASS,
        "observations": observations,
        "vintages": vintages,
        "quality_events": quality_events,
        "metadata": {
            "production_write": False,
            "decision_write": False,
            "forecast_write": False,
            "source_series_id": SERIES_ID,
            "source_locator": "official iacoviel/iacoviel.github.io git history",
            "current_final_vintage_substitution_allowed": False,
        },
    }
    return bundle, records


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--upstream-repo", type=Path, required=True)
    p.add_argument("--coverage-json", type=Path, required=True)
    p.add_argument("--bundle-out", type=Path, default=Path("gpr_vintage_bundle_v2.json"))
    p.add_argument("--summary-out", type=Path, default=Path("gpr_vintage_bundle_v2_summary.json"))
    args = p.parse_args()
    if not (args.upstream_repo / ".git").exists():
        raise SystemExit("UPSTREAM_REPO_IS_NOT_A_GIT_CLONE")
    retrieved_at = utcnow()
    bundle, records = build_bundle(args.upstream_repo, args.coverage_json, retrieved_at)
    args.bundle_out.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "pipeline_version": PIPELINE_VERSION,
        "proven_vintages_built": len(records),
        "observation_rows_built": len(bundle["observations"]),
        "quality_errors": sum(1 for q in bundle["quality_events"] if q.get("severity") == "ERROR"),
        "origins": [asdict(r) for r in records],
        "production_write": False,
        "binding_note": "Bundle construction is research evidence only; persistence requires canonical governance acceptance.",
    }
    args.summary_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "origins"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
