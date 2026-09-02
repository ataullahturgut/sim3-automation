from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import math
import random
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "patch_repro_v1"
PIN = "ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
METALS = ["Gold", "Silver", "Platinum", "Palladium"]
SEED = 20260902
GRID = [(126, 7, 24), (126, 14, 32), (252, 7, 24), (252, 14, 32), (252, 21, 32)]
LOCKED_START = pd.Timestamp("2023-01-01")
LOCKED_END = pd.Timestamp("2026-07-01")
DEV_TRAIN_END = pd.Timestamp("2020-12-01")
DEV_VALID_START = pd.Timestamp("2021-01-01")
DEV_VALID_END = pd.Timestamp("2022-12-01")


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass


def load_core() -> pd.DataFrame:
    p = ROOT / "core5_monthly.csv.gz.b64"
    raw = gzip.decompress(base64.b64decode(p.read_text().strip())).decode()
    return pd.read_csv(io.StringIO(raw), parse_dates=["date"]).set_index("date").sort_index()


def fetch_pinned_metals() -> pd.DataFrame:
    rows = []
    session = requests.Session()
    for y in range(2010, 2027):
        url = f"https://raw.githubusercontent.com/lbruton/StakTrakr/{PIN}/data/spot-history-{y}.json"
        r = session.get(url, timeout=90, headers={"User-Agent": "Gold-Control-Patch-Repro/1.0"})
        r.raise_for_status()
        for z in r.json():
            if z.get("metal") in METALS:
                d = pd.to_datetime(z["timestamp"]).normalize()
                if d <= pd.Timestamp("2026-07-31"):
                    rows.append((d, z["metal"], float(z["spot"])))
    d = pd.DataFrame(rows, columns=["date", "metal", "spot"]).sort_values(["date", "metal"])
    d = d.drop_duplicates(["date", "metal"], keep="last")
    wide = d.pivot(index="date", columns="metal", values="spot").sort_index()[METALS].dropna()
    if wide.empty:
        raise RuntimeError("PINNED_METALS_EMPTY")
    return wide


def gpr_z_asof(core: pd.DataFrame, asof_month: pd.Timestamp) -> float:
    h = core.loc[:asof_month, "gpr"].dropna().astype(float)
    if h.empty:
        return 0.5
    lo, hi = float(h.min()), float(h.max())
    return 0.5 if hi <= lo else float((h.iloc[-1] - lo) / (hi - lo))


def causal_decomp(a: np.ndarray, win: int = 21) -> np.ndarray:
    tr = np.zeros_like(a)
    for i in range(len(a)):
        tr[i] = a[max(0, i - win + 1): i + 1].mean(0)
    return np.concatenate([tr, a - tr], axis=1)


class PatchTransformer(nn.Module):
    def __init__(self, ch: int, patch: int, d: int):
        super().__init__()
        self.patch = patch
        self.stride = max(1, patch // 2)
        self.emb = nn.Linear(patch * ch, d)
        layer = nn.TransformerEncoderLayer(
            d_model=d, nhead=4, dim_feedforward=4 * d, dropout=0.10,
            batch_first=True, activation="gelu", norm_first=True,
        )
        self.enc = nn.TransformerEncoder(layer, 2)
        self.conv = nn.Conv1d(d, d, 3, padding=1)
        self.head = nn.Sequential(nn.Linear(d + 5, 64), nn.GELU(), nn.Dropout(0.10), nn.Linear(64, 1))

    def forward(self, x: torch.Tensor, m: torch.Tensor) -> torch.Tensor:
        p = x.unfold(1, self.patch, self.stride).permute(0, 1, 3, 2).contiguous().flatten(2)
        z = self.enc(self.emb(p))
        z = self.conv(z.transpose(1, 2)).transpose(1, 2).mean(1)
        return self.head(torch.cat([z, m], 1)).squeeze(1)


def build_samples(wide: pd.DataFrame, core: pd.DataFrame, L: int):
    r = np.log(wide[METALS]).diff().dropna()
    out = []
    for t in sorted(core.index):
        if t < pd.Timestamp("2011-03-01") or t > LOCKED_END:
            continue
        p = t - pd.offsets.MonthBegin(1)
        pp = p - pd.offsets.MonthBegin(1)
        if p not in core.index or pp not in core.index:
            continue
        origin_end = t - pd.Timedelta(days=1)
        hist = r.loc[:origin_end]
        if len(hist) < L:
            continue
        x = causal_decomp(hist.iloc[-L:].values.astype(np.float32), 21).astype(np.float32)
        nas = float(np.log(float(core.loc[p, "nasdaq"]) / float(core.loc[pp, "nasdaq"])))
        fx = float(np.log(float(core.loc[p, "usdcny"]) / float(core.loc[pp, "usdcny"])))
        # Conservative GPR publication safety: use t-2 period only.
        gpr = float(core.loc[pp, "gpr"])
        macro = np.array([
            float(core.loc[p, "fedfunds"]), nas, fx, np.log1p(gpr), gpr_z_asof(core, pp)
        ], dtype=np.float32)
        y = float(np.log(float(core.loc[t, "gold_monthly"]) / float(core.loc[p, "gold_monthly"])))
        out.append((t, x, macro, y))
    return out


def normalize_sets(tr, va):
    X = np.stack([s[1] for s in tr])
    M = np.stack([s[2] for s in tr])
    y = np.array([s[3] for s in tr], np.float32)
    xm = X.reshape(-1, X.shape[-1]).mean(0)
    xs = X.reshape(-1, X.shape[-1]).std(0) + 1e-6
    mm = M.mean(0)
    ms = M.std(0) + 1e-6
    ym = float(y.mean())
    ys = float(y.std() + 1e-6)

    def f(s):
        return ((s[1] - xm) / xs, (s[2] - mm) / ms, np.float32((s[3] - ym) / ys))

    return [f(s) for s in tr], [f(s) for s in va], (xm, xs, mm, ms, ym, ys)


def fit_patch(tr, va, patch: int, dim: int, seed: int, epochs: int = 140):
    seed_all(seed)
    A, B, sc = normalize_sets(tr, va)
    X = torch.tensor(np.stack([z[0] for z in A]), dtype=torch.float32)
    M = torch.tensor(np.stack([z[1] for z in A]), dtype=torch.float32)
    Y = torch.tensor(np.array([z[2] for z in A]), dtype=torch.float32)
    model = PatchTransformer(X.shape[-1], patch, dim)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.HuberLoss()
    best, best_v, bad = None, 1e99, 0
    for _ in range(epochs):
        model.train()
        q = torch.randperm(len(X))
        for k in range(0, len(X), 32):
            ix = q[k:k + 32]
            opt.zero_grad()
            loss = loss_fn(model(X[ix], M[ix]), Y[ix])
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        if B:
            model.eval()
            VX = torch.tensor(np.stack([z[0] for z in B]), dtype=torch.float32)
            VM = torch.tensor(np.stack([z[1] for z in B]), dtype=torch.float32)
            VY = torch.tensor(np.array([z[2] for z in B]), dtype=torch.float32)
            with torch.no_grad():
                v = float(torch.mean(torch.abs(model(VX, VM) - VY)))
            if v < best_v - 1e-5:
                best_v = v
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
                bad = 0
            else:
                bad += 1
                if bad >= 24:
                    break
    if best:
        model.load_state_dict(best)
    return model, sc, best_v


def predict(model, sc, s) -> float:
    xm, xs, mm, ms, ym, ys = sc
    x = ((s[1] - xm) / xs).astype(np.float32)
    m = ((s[2] - mm) / ms).astype(np.float32)
    model.eval()
    with torch.no_grad():
        z = float(model(torch.tensor(x[None]), torch.tensor(m[None])).item())
    return z * ys + ym


def select_geometry(core, wide):
    ranked = []
    for L, P, D in GRID:
        S = build_samples(wide, core, L)
        tr = [s for s in S if s[0] <= DEV_TRAIN_END]
        va = [s for s in S if DEV_VALID_START <= s[0] <= DEV_VALID_END]
        if len(tr) < 60 or len(va) < 12:
            raise RuntimeError(f"INSUFFICIENT_DEV_SAMPLE:{L}:{len(tr)}:{len(va)}")
        model, sc, _ = fit_patch(tr, va, P, D, SEED + L + P + D, 160)
        pr = np.array([predict(model, sc, s) for s in va])
        yy = np.array([s[3] for s in va])
        ranked.append({"L": L, "P": P, "D": D, "dev_return_mae": float(np.mean(np.abs(pr - yy)))})
    ranked.sort(key=lambda x: (x["dev_return_mae"], x["L"], x["P"], x["D"]))
    return ranked


def locked_predictions(core, wide, geom):
    L, P, D = int(geom["L"]), int(geom["P"]), int(geom["D"])
    S = build_samples(wide, core, L)
    out = []
    for t in pd.date_range(LOCKED_START, LOCKED_END, freq="MS"):
        trall = [s for s in S if s[0] < t]
        te = [s for s in S if s[0] == t]
        if len(te) != 1:
            raise RuntimeError(f"TARGET_SAMPLE_MISSING:{t.date()}")
        cut = max(48, int(len(trall) * 0.85))
        cut = min(cut, len(trall) - 12)
        tr, va = trall[:cut], trall[cut:]
        if len(tr) < 48 or len(va) < 12:
            raise RuntimeError(f"TRAIN_VALID_SPLIT_INVALID:{t.date()}:{len(tr)}:{len(va)}")
        rr = []
        for off in [0, 101, 202]:
            model, sc, _ = fit_patch(tr, va, P, D, SEED + off + int(t.strftime("%Y%m")), 140)
            rr.append(predict(model, sc, te[0]))
        ret = float(np.median(rr))
        p = t - pd.offsets.MonthBegin(1)
        forecast = float(core.loc[p, "gold_monthly"]) * math.exp(ret)
        out.append((t.strftime("%Y-%m"), forecast, ret))
    return pd.DataFrame(out, columns=["month", "patch_repro", "predicted_log_return"])


def metrics(actual, pred):
    a = np.asarray(actual, float)
    p = np.asarray(pred, float)
    e = p - a
    return {
        "MAE": float(np.mean(np.abs(e))),
        "MAPE_pct": float(np.mean(np.abs(e) / a) * 100),
        "median_APE_pct": float(np.median(np.abs(e) / a) * 100),
        "worst_APE_pct": float(np.max(np.abs(e) / a) * 100),
        "RMSE": float(np.sqrt(np.mean(e * e))),
    }


def mode_select():
    OUT.mkdir(exist_ok=True)
    core = load_core()
    wide = fetch_pinned_metals()
    ranked = select_geometry(core, wide)
    core_sha = hashlib.sha256((ROOT / "core5_monthly.csv.gz.b64").read_bytes()).hexdigest()
    contract_sha = hashlib.sha256((ROOT / "GOLD_CONTROL_CAUSAL_PATCH_R1_REPRO_CONTRACT_V1.md").read_bytes()).hexdigest()
    payload = {
        "candidate_id": "CAUSAL_PATCH_R1_REPRO_V1",
        "selected_pre_2023_geometry": ranked[0],
        "development_window": {"train_end": str(DEV_TRAIN_END.date()), "validation_start": str(DEV_VALID_START.date()), "validation_end": str(DEV_VALID_END.date())},
        "full_development_ranking": ranked,
        "daily_metals_source_commit": PIN,
        "core5_sha256": core_sha,
        "contract_sha256": contract_sha,
        "locked_score_window_used_for_selection": False,
    }
    (OUT / "frozen_geometry.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("PATCH_GEOMETRY_SELECTION_SOURCE_PIN_PASS=true")
    print("PATCH_GEOMETRY_SELECTION_LOCKED_WINDOW_USED=false")
    print("PATCH_GEOMETRY_SELECTED=" + json.dumps(ranked[0], sort_keys=True))
    print("PATCH_GEOMETRY_SELECTION_COMPLETE")


def mode_replay():
    gp = OUT / "frozen_geometry.json"
    if not gp.exists():
        raise RuntimeError("FROZEN_GEOMETRY_NOT_FOUND")
    geom_doc = json.loads(gp.read_text())
    geom = geom_doc["selected_pre_2023_geometry"]
    core = load_core()
    wide = fetch_pinned_metals()
    a = locked_predictions(core, wide, geom)
    b = locked_predictions(core, wide, geom)
    maxdiff = float(np.max(np.abs(a["patch_repro"].to_numpy() - b["patch_repro"].to_numpy())))

    ref = pd.read_csv(ROOT / "production_closure" / "production_history_43.csv")
    if len(ref) != 43:
        raise RuntimeError(f"REFERENCE_N_NOT_43:{len(ref)}")
    z = ref.merge(a, on="month", how="inner")
    if len(z) != 43:
        raise RuntimeError(f"COMMON_N_NOT_43:{len(z)}")

    # Reconcile CORE5 target and RW exactly against the closure file.
    target_ok = 0
    rw_ok = 0
    for _, row in z.iterrows():
        t = pd.Timestamp(row["month"] + "-01")
        p = t - pd.offsets.MonthBegin(1)
        target_ok += int(abs(float(core.loc[t, "gold_monthly"]) - float(row["actual"])) <= 1e-9)
        rw_ok += int(abs(float(core.loc[p, "gold_monthly"]) - float(row["rw"])) <= 1e-9)

    m_patch = metrics(z.actual, z.patch_repro)
    m_rw = metrics(z.actual, z.rw)
    m_arch = metrics(z.actual, z.patch_r1)
    m_vw = metrics(z.actual, z.vw)
    hard_pass = (target_ok == 43 and rw_ok == 43 and maxdiff <= 1e-8)
    perf_pass = (m_patch["MAPE_pct"] < m_rw["MAPE_pct"] and m_patch["MAE"] < m_rw["MAE"])
    status = (
        "PATCH_R1_REPRO_V1_HISTORICAL_REPLAY_ELIGIBLE" if hard_pass and perf_pass else
        "REPRODUCIBLE_PATCH_IMPLEMENTATION_PASS; PRODUCTION_PRIMARY_NOT_APPROVED" if hard_pass else
        "PATCH_R1_REPRO_V1_HARD_GATE_FAIL"
    )

    z["patch_repro_ape"] = np.abs(z.patch_repro - z.actual) / z.actual * 100
    z.to_csv(OUT / "locked_replay_43.csv", index=False)
    evidence = {
        "candidate_id": "CAUSAL_PATCH_R1_REPRO_V1",
        "evidence_class": "HISTORICAL_REPLAY",
        "prospective_claim": False,
        "source_pin": PIN,
        "selected_geometry": geom,
        "N": 43,
        "target_reconciliation": f"{target_ok}/43",
        "rw_reconciliation": f"{rw_ok}/43",
        "future_information_used": False,
        "deterministic_max_abs_diff": maxdiff,
        "patch_repro_metrics": m_patch,
        "rw_metrics": m_rw,
        "archived_patch_reference_metrics": m_arch,
        "vw_audited_reference_metrics": m_vw,
        "hard_gate_pass": hard_pass,
        "performance_gate_pass": perf_pass,
        "decision": status,
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
    }
    (OUT / "locked_replay_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"PATCH_REPRO_TARGET_RECONCILIATION={target_ok}/43")
    print(f"PATCH_REPRO_RW_RECONCILIATION={rw_ok}/43")
    print(f"PATCH_REPRO_DETERMINISTIC_MAX_ABS_DIFF={maxdiff:.12g}")
    print(f"PATCH_REPRO_MAPE_PCT={m_patch['MAPE_pct']:.9f}")
    print(f"RW_MAPE_PCT={m_rw['MAPE_pct']:.9f}")
    print(f"PATCH_REPRO_MAE={m_patch['MAE']:.9f}")
    print(f"RW_MAE={m_rw['MAE']:.9f}")
    print(f"ARCHIVED_PATCH_MAPE_PCT={m_arch['MAPE_pct']:.9f}")
    print(f"VW_REFERENCE_MAPE_PCT={m_vw['MAPE_pct']:.9f}")
    print(f"PATCH_REPRO_HARD_GATE_PASS={str(hard_pass).lower()}")
    print(f"PATCH_REPRO_PERFORMANCE_GATE_PASS={str(perf_pass).lower()}")
    print(f"PATCH_REPRO_DECISION={status}")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")
    print("PATCH_R1_REPRO_LOCKED_REPLAY_COMPLETE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["select", "replay"], required=True)
    args = ap.parse_args()
    seed_all(SEED)
    mode_select() if args.mode == "select" else mode_replay()


if __name__ == "__main__":
    main()
