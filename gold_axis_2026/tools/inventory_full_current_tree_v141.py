from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GC = ROOT / "gold_axis_2026"

PATH_TOKENS = (
    "v123", "v124", "v125", "v126", "v127", "v128", "v129", "v130", "v131", "v132",
    "v133", "v134", "v135", "v136", "v137", "v138", "v139", "v140",
    "stage4", "stage_4", "aug31", "september_replay", "macro_event_successor_v1",
    "direction_summary_acceptance_trigger", "mobile_viewport_qa",
)
CONTENT_TOKENS = (
    "GOLD_CONTROL_STAGE4",
    "GOLD_CONTROL_STAGE_4",
    "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V1",
    "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2",
    "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V3",
    "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE",
    "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED",
    "NOT_ISSUED_MISSED_2026_08_31_ORIGIN",
    "SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED",
    "MACRO_EVENT_SUCCESSOR_V1",
)
SCAN_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml"}
SELF_EXCLUDE = {
    "gold_axis_2026/tools/audit_current_surface_v141.py",
    "gold_axis_2026/tools/inventory_full_current_tree_v141.py",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def current_tree_files() -> list[Path]:
    roots = [GC, ROOT / ".github" / "workflows"]
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SCAN_EXTENSIONS and "__pycache__" not in path.parts:
                files.append(path)
    return sorted(set(files))


def legacy_path_hits(files: list[Path]) -> list[str]:
    return [rel(path) for path in files if any(token in rel(path).lower() for token in PATH_TOKENS)]


def legacy_content_hits(files: list[Path]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in files:
        relative = rel(path)
        if relative in SELF_EXCLUDE:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for token in CONTENT_TOKENS:
            if token in text:
                lines = [i + 1 for i, line in enumerate(text.splitlines()) if token in line]
                hits.append({"path": relative, "token": token, "lines": lines[:20]})
    return hits


def local_imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def app_reachability() -> dict[str, object]:
    app_dir = GC / "apps"
    modules = {path.stem: path for path in app_dir.glob("*.py") if not path.name.startswith("test_")}
    # gold_control.py dynamically loads gold_control_mobile.py, so both are explicit roots.
    queue = ["gold_control", "gold_control_mobile"]
    reachable: set[str] = set()
    while queue:
        name = queue.pop()
        if name in reachable or name not in modules:
            continue
        reachable.add(name)
        for dep in local_imports(modules[name]):
            if dep in modules and dep not in reachable:
                queue.append(dep)
    return {
        "entrypoints": ["gold_control", "gold_control_mobile"],
        "reachable_modules": sorted(reachable),
        "unused_modules": sorted(set(modules) - reachable),
    }


def main() -> int:
    files = current_tree_files()
    root_docs = sorted(rel(p) for p in GC.glob("GOLD_CONTROL_*.md"))
    workflows = sorted(rel(p) for p in (ROOT / ".github" / "workflows").glob("gold-control-*.yml"))
    report = {
        "contract": "GOLD_CONTROL_FULL_CURRENT_TREE_INVENTORY_V141",
        "scanned_file_count": len(files),
        "legacy_path_hits": legacy_path_hits(files),
        "legacy_content_hits": legacy_content_hits(files),
        "root_gold_control_docs": root_docs,
        "root_gold_control_doc_count": len(root_docs),
        "gold_control_workflows": workflows,
        "gold_control_workflow_count": len(workflows),
        "app_reachability": app_reachability(),
    }
    Path("full_current_tree_inventory_v141.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
