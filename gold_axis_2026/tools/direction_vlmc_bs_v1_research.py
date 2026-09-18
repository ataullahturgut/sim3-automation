#!/usr/bin/env python3
"""DIRECTION_VLMC_BS_V1_RESEARCH

Frozen 52-week bootstrapped Variable-Length Markov Chain (VLMC-BS)
implementation for Gold Control. No parameter tuning is performed outside the
preregistered bootstrap cutoff selection.

Input CSV columns:
  observation_ts,value
Optional:
  retrieved_at,quality_status

Method authority:
  GOLD_CONTROL_DIRECTION_VLMC_BS_V1_PREREG_2026-09-18.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np

NY = ZoneInfo("America/New_York")
WINDOW = 52
K0 = 0.30
K_GRID = np.round(np.arange(0.40, 2.5000001, 0.02), 2)
BOOTSTRAPS = 1000
BURN_IN = 10000
SEED = 1521
ALPHABET = (0, 1)


@dataclass(frozen=True)
class WeeklyClose:
    week_start: date
    close_date: date
    close: float


@dataclass
class Node:
    # Context symbols are stored newest-first.
    ctx: tuple[int, ...]
    parent: "Node | None" = None
    children: dict[int, "Node"] = field(default_factory=dict)
    active: set[int] = field(default_factory=set)
    n_occ: int = 0
    trans_down: int = 0
    trans_up: int = 0
    delta: float = 0.0


class VLMC:
    """Classical Bühlmann-Wyner / Mächler-Bühlmann context algorithm."""

    def __init__(self, seq):
        self.seq = tuple(int(x) for x in seq)
        self.n = len(self.seq)
        self.root = Node(())
        self.nodes: dict[tuple[int, ...], Node] = {(): self.root}
        self._build_maximal_tree()
        self.reset_active()
        self._compute_pruning_statistics()

    def _occurrence_and_transition_counts(self, ctx_newest):
        if not ctx_newest:
            up = sum(self.seq)
            return self.n, self.n - up, up

        chron = ctx_newest[::-1]
        length = len(chron)
        n_occ = down = up = 0
        for start in range(0, self.n - length + 1):
            if self.seq[start : start + length] == chron:
                n_occ += 1
                next_index = start + length
                if next_index < self.n:
                    if self.seq[next_index] == 1:
                        up += 1
                    else:
                        down += 1
        return n_occ, down, up

    def _build_maximal_tree(self):
        self.root.n_occ, self.root.trans_down, self.root.trans_up = (
            self._occurrence_and_transition_counts(())
        )
        stack = [self.root]
        while stack:
            node = stack.pop()
            # Extending a newest-first context appends an older symbol.
            for older in ALPHABET:
                ctx = node.ctx + (older,)
                n_occ, down, up = self._occurrence_and_transition_counts(ctx)
                # Source context algorithm: every maximal terminal context
                # must be observed at least twice.
                if n_occ >= 2:
                    child = Node(
                        ctx=ctx,
                        parent=node,
                        n_occ=n_occ,
                        trans_down=down,
                        trans_up=up,
                    )
                    node.children[older] = child
                    self.nodes[ctx] = child
                    stack.append(child)

    def reset_active(self):
        for node in self.nodes.values():
            node.active = set(node.children.keys())

    @staticmethod
    def _probabilities(node):
        den = node.trans_down + node.trans_up
        if den <= 0:
            return 0.5, 0.5
        return node.trans_down / den, node.trans_up / den

    def _compute_pruning_statistics(self):
        for ctx, node in self.nodes.items():
            if not ctx:
                node.delta = math.inf
                continue
            p_down, p_up = self._probabilities(node)
            q_down, q_up = self._probabilities(node.parent)
            div = 0.0
            for p, q in ((p_down, q_down), (p_up, q_up)):
                if p <= 0:
                    continue
                if q <= 0:
                    div = math.inf
                    break
                div += p * math.log(p / q)
            node.delta = node.n_occ * div if math.isfinite(div) else math.inf

    def prune_to(self, cutoff):
        """Prune monotonically to cutoff K. May be called with increasing K."""
        while True:
            terminals = []
            stack = [self.root]
            while stack:
                node = stack.pop()
                active_children = [node.children[a] for a in node.active]
                if node is not self.root and not active_children:
                    terminals.append(node)
                else:
                    stack.extend(active_children)

            to_prune = [node for node in terminals if node.delta < cutoff]
            if not to_prune:
                return self

            for node in to_prune:
                node.parent.active.discard(node.ctx[-1])

    def active_context(self, history):
        node = self.root
        for symbol in reversed(history):
            if symbol in node.active:
                node = node.children[symbol]
            else:
                break
        return node

    def probability_up(self, history):
        node = self.active_context(history)
        return self._probabilities(node)[1], node

    def predict(self, history):
        p_up, node = self.probability_up(history)
        return (1 if p_up >= 0.5 else 0), p_up, node

    def max_order(self):
        max_depth = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            max_depth = max(max_depth, len(node.ctx))
            stack.extend(node.children[a] for a in node.active)
        return max_depth

    def context_count(self):
        # Leaves are contexts. An incomplete internal node also serves as a
        # fallback context for missing child branches.
        count = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            if len(node.active) < len(ALPHABET):
                count += 1
            stack.extend(node.children[a] for a in node.active)
        return count


def fit_vlmc(seq, cutoff):
    model = VLMC(seq)
    return model.prune_to(cutoff)


def simulate_bootstrap(model, replications=BOOTSTRAPS, n=WINDOW + 1):
    """Simulate B sequences after a 10,000-step burn-in.

    The source tutorial uses n.start=10000. A fixed seed is reset per real
    forecast origin so each origin is exactly reproducible and independent of
    execution ordering/parallelism.
    """
    rng = np.random.default_rng(SEED)
    order = model.max_order()

    if order == 0:
        p_up = model._probabilities(model.root)[1]
        return (rng.random((replications, n)) < p_up).astype(np.int8)

    nstates = 1 << order
    mask = nstates - 1
    p_table = np.empty(nstates, dtype=float)

    for state in range(nstates):
        history = [(state >> (order - 1 - i)) & 1 for i in range(order)]
        p_table[state] = model.probability_up(history)[0]

    states = np.zeros(replications, dtype=np.int64)
    for _ in range(BURN_IN):
        bits = (rng.random(replications) < p_table[states]).astype(np.int64)
        states = ((states << 1) | bits) & mask

    out = np.empty((replications, n), dtype=np.int8)
    for j in range(n):
        bits = (rng.random(replications) < p_table[states]).astype(np.int8)
        out[:, j] = bits
        states = ((states << 1) | bits.astype(np.int64)) & mask
    return out


def tune_cutoff(seq52):
    initial_model = fit_vlmc(seq52, K0)
    bootstrap = simulate_bootstrap(initial_model)
    matches = np.zeros(len(K_GRID), dtype=int)

    for b in range(BOOTSTRAPS):
        train = tuple(int(x) for x in bootstrap[b, :WINDOW])
        actual = int(bootstrap[b, WINDOW])

        # One maximal tree is enough: as K rises, pruning is nested.
        model = VLMC(train)
        for i, cutoff in enumerate(K_GRID):
            model.prune_to(float(cutoff))
            pred, _, _ = model.predict(train)
            matches[i] += int(pred == actual)

    losses = 1.0 - matches / BOOTSTRAPS
    minimum = float(losses.min())
    winners = np.flatnonzero(losses == minimum)
    # Preregistered tie rule: first/smallest K on ascending grid.
    idx = int(winners[0])
    return {
        "k_star": float(K_GRID[idx]),
        "bootstrap_loss": minimum,
        "k_tie_count": int(len(winners)),
        "bootstrap_matches": int(matches[idx]),
        "initial_order": initial_model.max_order(),
        "initial_context_count": initial_model.context_count(),
    }


def parse_ts(text):
    text = text.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"observation_ts must be timezone-aware: {text}")
    return dt


def monday_of(d):
    return d - timedelta(days=d.weekday())


def load_weekly(path):
    latest = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not {"observation_ts", "value"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires observation_ts,value")
        for row in reader:
            key = row["observation_ts"].strip()
            prior = latest.get(key)
            if prior is None or row.get("retrieved_at", "") > prior.get("retrieved_at", ""):
                latest[key] = row

    by_week = {}
    for row in latest.values():
        if row.get("quality_status") and "APPROV" not in row["quality_status"].upper():
            continue
        dt_ny = parse_ts(row["observation_ts"]).astimezone(NY)
        d = dt_ny.date()
        if d.weekday() >= 5:
            continue
        value = float(row["value"])
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Invalid XAU value on {d}: {value}")
        week = monday_of(d)
        old = by_week.get(week)
        if old is None or d > old[0]:
            by_week[week] = (d, value)

    return [
        WeeklyClose(week_start=w, close_date=d, close=v)
        for w, (d, v) in sorted(by_week.items())
    ]


def weekly_signs(weeks):
    signs = [None]
    for i in range(1, len(weeks)):
        signs.append(1 if math.log(weeks[i].close / weeks[i - 1].close) > 0 else 0)
    return signs


def forecast_one(seq52):
    tuning = tune_cutoff(seq52)
    model = fit_vlmc(seq52, tuning["k_star"])
    pred, p_up, node = model.predict(seq52)
    support = node.trans_down + node.trans_up
    context_chron = "".join(str(x) for x in node.ctx[::-1]) if node.ctx else "ROOT"
    return {
        **tuning,
        "final_order": model.max_order(),
        "final_context_count": model.context_count(),
        "active_context": context_chron,
        "active_context_depth": len(node.ctx),
        "active_context_support": support,
        "active_trans_down": node.trans_down,
        "active_trans_up": node.trans_up,
        "p_up": p_up,
        "forecast_up": pred,
    }


def build_forecasts(weeks):
    signs = weekly_signs(weeks)
    rows = []
    # 52 weekly signs are required. sign[0] is undefined.
    for origin in range(WINDOW, len(weeks) - 1):
        hist = signs[origin - WINDOW + 1 : origin + 1]
        if len(hist) != WINDOW or any(x is None for x in hist):
            continue
        result = forecast_one(tuple(int(x) for x in hist))
        actual = signs[origin + 1]
        rows.append({
            "origin_week_start": weeks[origin].week_start,
            "origin_close_date": weeks[origin].close_date,
            "target_week_start": weeks[origin + 1].week_start,
            **result,
            "actual_up": int(actual),
            "previous_sign": int(signs[origin]),
        })
    return rows


def metrics(rows):
    if not rows:
        return {"n": 0}

    n = len(rows)
    actual_up = sum(r["actual_up"] for r in rows)
    actual_down = n - actual_up
    tp = sum(r["forecast_up"] == 1 and r["actual_up"] == 1 for r in rows)
    tn = sum(r["forecast_up"] == 0 and r["actual_up"] == 0 for r in rows)
    fp = sum(r["forecast_up"] == 1 and r["actual_up"] == 0 for r in rows)
    fn = sum(r["forecast_up"] == 0 and r["actual_up"] == 1 for r in rows)

    eps = 1e-12
    brier = sum((r["p_up"] - r["actual_up"]) ** 2 for r in rows) / n
    logloss = -sum(
        r["actual_up"] * math.log(min(max(r["p_up"], eps), 1 - eps))
        + (1 - r["actual_up"]) * math.log(min(max(1 - r["p_up"], eps), 1 - eps))
        for r in rows
    ) / n

    return {
        "n": n,
        "accuracy": (tp + tn) / n,
        "balanced_accuracy": ((tp / actual_up) + (tn / actual_down)) / 2
        if actual_up and actual_down else None,
        "brier": brier,
        "log_loss": logloss,
        "actual_up": actual_up,
        "actual_down": actual_down,
        "forecast_up": tp + fp,
        "forecast_down": tn + fn,
        "up_sensitivity": tp / actual_up if actual_up else None,
        "down_sensitivity": tn / actual_down if actual_down else None,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "always_up_accuracy": actual_up / n,
        "previous_sign_accuracy": sum(r["previous_sign"] == r["actual_up"] for r in rows) / n,
        "mean_p_up": sum(r["p_up"] for r in rows) / n,
        "min_p_up": min(r["p_up"] for r in rows),
        "max_p_up": max(r["p_up"] for r in rows),
        "mean_k_star": sum(r["k_star"] for r in rows) / n,
        "min_k_star": min(r["k_star"] for r in rows),
        "max_k_star": max(r["k_star"] for r in rows),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("--forecast-csv", type=Path, required=True)
    ap.add_argument("--summary-json", type=Path, required=True)
    args = ap.parse_args()

    weeks = load_weekly(args.input_csv)
    rows = build_forecasts(weeks)

    fields = [
        "origin_week_start","origin_close_date","target_week_start",
        "k_star","bootstrap_loss","k_tie_count","bootstrap_matches",
        "initial_order","initial_context_count","final_order","final_context_count",
        "active_context","active_context_depth","active_context_support",
        "active_trans_down","active_trans_up","p_up","forecast_up",
        "actual_up","previous_sign",
    ]
    with args.forecast_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    years = sorted({r["target_week_start"].year for r in rows})
    summary = {
        "identity": "DIRECTION_VLMC_BS_V1_RESEARCH",
        "window_weeks": WINDOW,
        "K0": K0,
        "K_grid": [float(K_GRID[0]), float(K_GRID[-1]), 0.02],
        "bootstraps": BOOTSTRAPS,
        "burn_in": BURN_IN,
        "seed": SEED,
        "decision_rule": "UP iff p_up >= 0.5",
        "by_target_year": {
            str(y): metrics([r for r in rows if r["target_week_start"].year == y])
            for y in years
        },
        "all": metrics(rows),
    }
    args.summary_json.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
