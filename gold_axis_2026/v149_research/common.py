from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_frame_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(
        frame.to_csv(index=False, float_format="%.12g", lineterminator="\n").encode()
    ).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def assert_finite(values, label: str) -> None:
    if not np.isfinite(np.asarray(values, float)).all():
        raise ValueError(f"NONFINITE_{label}")
