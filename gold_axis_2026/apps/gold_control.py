from __future__ import annotations

# Canonical Gold Control Streamlit entrypoint.
# Presentation authority: manifest v1.20 / final mobile V2 contract.
# The implementation remains in gold_control_mobile_v1.py to preserve its
# audited candidate history while this file stays the deployment entrypoint.

import runpy
from pathlib import Path


APP = Path(__file__).with_name("gold_control_mobile_v1.py")
if not APP.exists():
    raise RuntimeError("GOLD_CONTROL_MOBILE_V2_ENTRYPOINT_NOT_FOUND")

runpy.run_path(str(APP), run_name="__main__")
