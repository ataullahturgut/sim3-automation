#!/usr/bin/env python3
"""Reproduce price-direction AUC evidence from committed derived, vendor-price-redacted CSV.
The raw 15-minute input observations remain in the user's Neon database; no gold trading model.
Usage: python GOLD_EVENT_CHAIN_H03_EXTRAPERIOD_REPRODUCE_20261013.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = "GOLD_EVENT_CHAIN_H03_EXTRAPERIOD_2016_2026_"
DATA = HERE / (ROOT + "DAILY_OUTCOMES_20261013.csv")
SUMMARY = HERE / (ROOT + "RESULTS_20261013.json")


def rank_auc(records):
    down = [float(x["r20"]) for x in records if x["first"] == "DOWN"]
    up = [float(x["r20"]) for x in records if x["first"] == "UP"]
    if not down or not up:
        return None
    return sum(1 if d > u else 0.5 if d == u else 0
               for d in down for u in up) / (len(down) * len(up))


with DATA.open(encoding="utf-8", newline="") as fp:
    daily = list(csv.DictReader(fp))
with SUMMARY.open(encoding="utf-8") as fp:
    stored = json.load(fp)
results = {x["period"]: x for x in stored["results"]}
groups = defaultdict(list)
for row in daily:
    groups[row["scope"]].append(row)
for period, rows in groups.items():
    r = results[period]
    down = sum(x["first"] == "DOWN" for x in rows)
    up = sum(x["first"] == "UP" for x in rows)
    neither = sum(x["first"] == "NONE" for x in rows)
    a = rank_auc(rows)
    assert (len(rows), down, up, neither) == (r["days"], r["down"], r["up"], r["none"])
    assert abs(a - r["auc_r20_given_move"]) < 1e-11
    tension = sum(float(x["r20"]) >= 8 for x in rows)
    assert tension == r["tense8_n"]
    print(f"{period}: N={len(rows)}, down={down}, up={up}, none={neither}, "
          f"conditional AUC={a:.4f}, tense8_count={tension}")
    for year in r["years"]:
        yr = [x for x in rows if x["date"][:4] == year["year"]]
        assert abs(rank_auc(yr) - year["auc"]) < 1e-11, (period, year["year"])
print("PASS — all stored period and annual AUC figures reproduced.")
