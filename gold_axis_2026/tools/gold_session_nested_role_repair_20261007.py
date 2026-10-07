"""Repair 07B/08B/09B development selection chronology; no transport refit.

Archived predictions are evaluation evidence only. Panels/experts are rebuilt
from governed raw sources by the original producers. No consensus is produced.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import numpy as np
import pandas as pd

AX = Path(__file__).resolve().parents[1]
PREFIX = "GOLD_SESSION_NESTED_ROLE_REPAIR"

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, AX / "tools" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    m7 = load("repair_m7", "gold_session_model07b_sage_path_session_feature_selection_20261007.py")
    m8 = load("repair_m8", "gold_session_model08b_sage_a1_session_feature_selection_20261007.py")
    m9 = load("repair_m9", "gold_session_model09b_sage_a1_path_session_feature_selection_20261007.py")
    # Fetch each exact pinned raw payload once; repeated producers retain the
    # same bytes and transforms. Never cache derived historical predictions.
    cache = {}
    def cache_bytes(original):
        def get(url, timeout=120):
            if url not in cache:
                cache[url] = original(url, timeout)
            return cache[url]
        return get
    modules = [m7, m8, m9]
    # Original modules create independent import trees. Locate all raw loaders.
    seen = set()
    def patch_tree(obj):
        if id(obj) in seen:
            return
        seen.add(id(obj))
        if hasattr(obj, "get_bytes") and hasattr(obj, "STAK_REF"):
            obj.get_bytes = cache_bytes(obj.get_bytes)
        for value in vars(obj).values():
            if hasattr(value, "__file__") and str(getattr(value, "__file__", "")).startswith(str(AX / "tools")):
                patch_tree(value)
    for module in modules:
        patch_tree(module)
    rows, timing = [], []
    for family, module in [("07B", m7), ("08B", m8), ("09B", m9)]:
        print(f"BUILD_RAW_PANEL {family}", flush=True)
        panel = module.build_panel()
        # 2025 target labels are used solely by the inherited V5 equality check;
        # remove them before any role selection or downstream replay.
        panel = panel[panel.year.le(2024)].copy()
        assert panel.year.max() == 2024
        for (part, win), g0 in panel.groupby(["partition", "window"], sort=True):
            g = g0.sort_values("start_utc").reset_index(drop=True)
            test = g[g.year.isin([2023, 2024])].reset_index(drop=True)
            for bs in range(0, len(test), module.BLOCK):
                te = test.iloc[bs:bs + module.BLOCK]
                cutoff = te.start_utc.min()
                tr = g[(g.end_utc <= cutoff) & (g.start_utc < cutoff)].copy()
                if len(tr) < module.MIN_TRAIN or tr.y_up.nunique() < 2:
                    continue
                assert tr.end_utc.max() <= cutoff
                assert tr.start_utc.max() < cutoff
                if family == "08B":
                    selected, C, detail, _ = module.choose_sage(tr)
                    cand = module.fit_selected(tr, te, selected)
                    comp = te.p_A1_arcr.to_numpy(float)
                    features = ["a1_logit"] + selected
                    comparator = "DIRECT_A1"
                else:
                    selected, C, detail, _ = module.choose_features(tr)
                    path = [f for f in selected if f in module.PATH]
                    sage = [f for f in selected if f in module.SAGE]
                    assert path and sage
                    if family == "07B":
                        features = selected
                        comparator = "NESTED_PATH_MATCHED"
                        comp = module.fit_l2(tr, te, path)
                    else:
                        features = ["a1_logit"] + selected
                        comparator = "NESTED_A1_PATH_MATCHED"
                        comp = module.fit_l2(tr, te, ["a1_logit"] + path)
                    cand = module.fit_l2(tr, te, features)
                model = {"07B": "NESTED_PATH_SESSION", "08B": "NESTED_A1_SESSION", "09B": "NESTED_A1_PATH_SESSION"}[family]
                timing.append(dict(family=family, partition=part, window=win,
                    block=bs // module.BLOCK, cutoff=str(cutoff),
                    max_train_start=str(tr.start_utc.max()), max_train_end=str(tr.end_utc.max()),
                    train_n=len(tr), selector_C=C, features="|".join(features),
                    detail=json.dumps(detail, default=str)))
                for r, pc, pb in zip(te.itertuples(index=False), cand, comp):
                    common = dict(partition=part, window=win, start_utc=r.start_utc,
                        end_utc=r.end_utc, year=int(r.year), y_up=int(r.y_up),
                        train_n=len(tr), selection_cutoff=cutoff)
                    rows.append(dict(**common, model=model, p_up=float(pc)))
                    rows.append(dict(**common, model=comparator, p_up=float(pb)))
            print(f"DONE {family} {part}/{win}", flush=True)
    pd.DataFrame(rows).to_csv(AX / f"{PREFIX}_PREDICTIONS_2026-10-07.csv", index=False)
    pd.DataFrame(timing).to_csv(AX / f"{PREFIX}_TIMING_2026-10-07.csv", index=False)
    summary = dict(status="NESTED_DEVELOPMENT_REPAIR_COMPLETE", model_families=["07B", "08B", "09B"],
        no_2025_scoring=True, no_2026=True, no_consensus=True, scored_years=[2023, 2024],
        selection_policy="Every outer block selects from matured training history only; no full-development frozen list is replayed backwards.",
        rows=len(rows), blocks=len(timing))
    (AX / f"{PREFIX}_SUMMARY_2026-10-07.json").write_text(json.dumps(summary, indent=2) + "\n")

if __name__ == "__main__":
    main()
