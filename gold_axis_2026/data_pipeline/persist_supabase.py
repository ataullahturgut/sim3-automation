from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_pipeline" / "_out"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required secret: {name}")
    return value.rstrip("/")


def headers(service_key: str, *, prefer: str | None = None) -> dict[str, str]:
    h = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def post_rows(base: str, key: str, table: str, rows: list[dict], *, ignore_duplicates: bool = False) -> None:
    if not rows:
        return
    prefer = "return=minimal"
    if ignore_duplicates:
        prefer = "resolution=ignore-duplicates,return=minimal"
    url = f"{base}/rest/v1/{table}"
    for i in range(0, len(rows), 500):
        batch = rows[i:i+500]
        r = requests.post(url, headers=headers(key, prefer=prefer), json=batch, timeout=60)
        if r.status_code not in (200, 201, 204):
            raise RuntimeError(f"Supabase {table} insert failed {r.status_code}: {r.text[:1000]}")


def main() -> int:
    base = env("SUPABASE_URL")
    key = env("SUPABASE_SERVICE_ROLE_KEY")

    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    observations = pd.read_csv(OUT / "observations.csv").where(pd.notna, None).to_dict("records")
    vintages = json.loads((OUT / "vintages.json").read_text(encoding="utf-8"))
    quality = json.loads((OUT / "quality_events.json").read_text(encoding="utf-8"))

    run_id = manifest["run_id"]
    started_at = manifest["retrieved_at"]
    git_sha = os.getenv("GITHUB_SHA")

    run_row = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "git_sha": git_sha,
        "pipeline_version": manifest["pipeline_version"],
        "status": "PASS" if not quality else "PASS_WITH_QUALITY_EVENTS",
        "notes": f"series={len(manifest.get('series', []))}; observations={manifest.get('n_observations', 0)}",
    }
    post_rows(base, key, "retrieval_runs", [run_row], ignore_duplicates=True)

    # Normalize JSON fields that were serialized as strings through CSV.
    for row in observations:
        meta = row.get("metadata")
        if isinstance(meta, str):
            try:
                row["metadata"] = json.loads(meta.replace("'", '"'))
            except Exception:
                row["metadata"] = {"raw_metadata": meta}
        if row.get("payload_hash") in ("", "nan"):
            row["payload_hash"] = None
        if row.get("provider_as_of") in ("", "nan"):
            row["provider_as_of"] = None

    post_rows(base, key, "observations", observations, ignore_duplicates=True)

    for v in vintages:
        v.setdefault("provider_as_of", None)
    post_rows(base, key, "source_vintages", vintages, ignore_duplicates=True)

    qrows = []
    for q in quality:
        qrows.append({
            "run_id": run_id,
            "series_id": q.get("series_id"),
            "event_ts": pd.Timestamp.now(tz="UTC").isoformat(),
            "severity": q.get("severity", "WARN"),
            "code": q.get("code", "UNSPECIFIED"),
            "message": q.get("message", ""),
            "metadata": q.get("metadata", {}),
        })
    post_rows(base, key, "quality_events", qrows)
    print(json.dumps({"persisted": True, "run_id": run_id, "observations": len(observations), "quality_events": len(qrows)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
