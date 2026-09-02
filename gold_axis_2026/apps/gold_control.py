from __future__ import annotations

"""Canonical Gold Control Streamlit entrypoint.

Presentation authority is the final mobile V2 contract frozen in manifest v1.20.
The implementation lives in ``gold_control_mobile_v1.py`` for continuity with
its audited candidate history; this wrapper prevents the legacy desktop UI from
remaining the production/deployment entrypoint.
"""

import runpy
from pathlib import Path


APP = Path(__file__).with_name("gold_control_mobile_v1.py")
if not APP.exists():
    raise RuntimeError("GOLD_CONTROL_MOBILE_V2_ENTRYPOINT_NOT_FOUND")

runpy.run_path(str(APP), run_name="__main__")
