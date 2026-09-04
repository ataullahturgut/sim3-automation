from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import requests

BASE = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export_{stamp}.xls"
START = (2020, 1)
END = (2026, 9)


def month_stamps():
    y, m = START
    ey, em = END
    while (y, m) <= (ey, em):
        yield f"{y:04d}{m:02d}"
        m += 1
        if m == 13:
            y += 1
            m = 1


def contiguous_runs(ok_stamps: list[str]) -> list[list[str]]:
    ok = set(ok_stamps)
    runs: list[list[str]] = []
    cur: list[str] = []
    for stamp in month_stamps():
        if stamp in ok:
            cur.append(stamp)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/gpr_vintage_archive_audit_v1.json")
    args = ap.parse_args()

    s = requests.Session()
    s.headers.update({"User-Agent": "Gold-Control-GPR-Vintage-Audit/1.0"})
    rows = []
    for stamp in month_stamps():
        url = BASE.format(stamp=stamp)
        status = None
        nbytes = 0
        sha = None
        error = None
        for attempt in range(3):
            try:
                r = s.get(url, timeout=45)
                status = r.status_code
                nbytes = len(r.content)
                if r.status_code == 200 and nbytes > 1000:
                    sha = hashlib.sha256(r.content).hexdigest()
                break
            except requests.RequestException as exc:
                error = type(exc).__name__
                if attempt == 2:
                    break
                time.sleep(2 * (attempt + 1))
        accessible = bool(status == 200 and nbytes > 1000 and sha)
        rows.append({
            "stamp": stamp,
            "http_status": status,
            "bytes": nbytes,
            "accessible": accessible,
            "sha256": sha,
            "error": error,
        })
        print(f"GPR_VINTAGE stamp={stamp} http={status} accessible={str(accessible).upper()} bytes={nbytes} error={error or 'NONE'}")
        time.sleep(0.10)

    oks = [r["stamp"] for r in rows if r["accessible"]]
    runs = contiguous_runs(oks)
    longest = max(runs, key=len) if runs else []
    tail = []
    if rows:
        for r in reversed(rows):
            if r["accessible"]:
                tail.append(r["stamp"])
            elif tail:
                break
        tail.reverse()
    payload = {
        "audit": "GPR_MONTHLY_VINTAGE_ARCHIVE_V1",
        "range": [f"{START[0]:04d}{START[1]:02d}", f"{END[0]:04d}{END[1]:02d}"],
        "n_probed": len(rows),
        "n_accessible": len(oks),
        "first_accessible": oks[0] if oks else None,
        "last_accessible": oks[-1] if oks else None,
        "longest_contiguous": {
            "start": longest[0] if longest else None,
            "end": longest[-1] if longest else None,
            "n": len(longest),
        },
        "latest_contiguous_tail": {
            "start": tail[0] if tail else None,
            "end": tail[-1] if tail else None,
            "n": len(tail),
        },
        "rows": rows,
        "model_score_run": "NONE",
        "database_writes": "NONE",
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True))
    print("GPR_VINTAGE_FIRST_ACCESSIBLE=" + str(payload["first_accessible"] or "NONE"))
    print("GPR_VINTAGE_LONGEST_CONTIGUOUS=" + (f"{payload['longest_contiguous']['start']}..{payload['longest_contiguous']['end']} n={payload['longest_contiguous']['n']}" if longest else "NONE"))
    print("GPR_VINTAGE_LATEST_CONTIGUOUS_TAIL=" + (f"{payload['latest_contiguous_tail']['start']}..{payload['latest_contiguous_tail']['end']} n={payload['latest_contiguous_tail']['n']}" if tail else "NONE"))
    print("MODEL_SCORE_RUN=NONE")
    print("DATABASE_WRITES=NONE")


if __name__ == "__main__":
    main()
