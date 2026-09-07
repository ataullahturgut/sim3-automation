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
    hits = []
    for path in files:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        low = rel.lower()
        if any(token in low for token in PATH_TOKENS):
            hits.append(rel)
    return hits


def legacy_content_hits(files: list[Path]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for token in CONTENT_TOKENS:
            if token not in text:
                continue
            lines = [i + 1 for i, line in enumerate(text.splitlines()) if token in line]
            hits.append({"path": rel, "token": token, "lines": lines[:20]})
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
    entry = "gold_control"
    reachable: set[str] = set()
    queue = [entry]
    while queue:
        name = queue.pop()
        if name in reachable or name not in modules:
            continue
        reachable.add(name)
        for dep in local_imports(modules[name]):
            if dep in modules and dep not in reachable:
                queue.append(dep)
    unused = sorted(set(modules) - reachable)
    return {
        "entrypoint": entry,
        "reachable_modules": sorted(reachable),
        "unused_modules": unused,
    }


def main() -> int:
    files = current_tree_files()
    report = {
        "contract": "GOLD_CONTROL_FULL_CURRENT_TREE_INVENTORY_V141",
        "scanned_file_count": len(files),
        "legacy_path_hits": legacy_path_hits(files),
        "legacy_content_hits": legacy_content_hits(files),
        "app_reachability": app_reachability(),
    }
    Path("full_current_tree_inventory_v141.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
