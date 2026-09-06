from __future__ import annotations

# Canonical Streamlit entrypoint for the current Gold Control surface.
# Current presentation code lives in gold_control_mobile.py. Historical/version-
# specific replay modules are intentionally not part of the current app path.

import importlib.util
import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

app_path = APP_DIR / "gold_control_mobile.py"
spec = importlib.util.spec_from_file_location("gold_control_mobile", app_path)
if spec is None or spec.loader is None:
    raise ImportError(f"CURRENT_GOLD_CONTROL_APP_LOAD_FAILED:{app_path}")
module = importlib.util.module_from_spec(spec)
sys.modules["gold_control_mobile"] = module
spec.loader.exec_module(module)
