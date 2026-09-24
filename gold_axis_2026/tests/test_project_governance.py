"""Current project authority and non-promotion checks; no model execution."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_single_project_manifest_and_closed_automation():
    manifests = list(ROOT.glob("**/*PROJECT_MANIFEST*.md"))
    assert manifests == [ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"]
    current = manifests[0].read_text().split("## 3.", 1)[0]
    assert "sole project-level technical contract" in current
    assert re.search(r"AUTO_SELECTOR\s*=\s*OFF", current)
    assert re.search(r"AUTO_ENSEMBLE\s*=\s*OFF", current)
    assert "No random split" in current
    assert "2025 is locked retrospective transport/stress" in current
    assert "2026 cannot be used for model selection/tuning" in current
    assert "NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY" in current
    assert "ABSTAIN ≠ DOWN" in current
