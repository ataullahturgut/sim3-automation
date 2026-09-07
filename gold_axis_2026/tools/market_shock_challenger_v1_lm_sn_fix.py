from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from gold_axis_2026.tools import market_shock_challenger_v1 as v1


def lm_critical(alpha: float, n: int = v1.N_INTRADAY) -> float:
    """Lee-Mykland (2008) Eq. (13), correcting V1 S_n only.

    This intentionally preserves every other V1 detector, threshold, data,
    consensus, walk-forward, EVT, and synthetic-injection rule unchanged.
    """
    if not (0 < alpha < 1):
        raise ValueError(alpha)
    c = math.sqrt(2.0 / math.pi)
    root = math.sqrt(2.0 * math.log(n))
    cn = root / c - (math.log(math.pi) + math.log(math.log(n))) / (2.0 * c * root)
    sn = 1.0 / (c * root)
    beta = -math.log(-math.log(1.0 - alpha))
    return cn + sn * beta


def _output_path() -> Path:
    if "--output" in sys.argv:
        i = sys.argv.index("--output")
        if i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return Path("market_shock_challenger_v1_report.json")


def main() -> int:
    # Isolated patch: V1 main resolves lm_critical from its module globals.
    v1.lm_critical = lm_critical
    rc = v1.main()

    path = _output_path()
    if path.exists():
        report = json.loads(path.read_text(encoding="utf-8"))
        report["contract"] = "GOLD_CONTROL_MARKET_SHOCK_CHALLENGER_V1_LM_SN_FIX"
        report["methodology_patch"] = {
            "scope": "ISOLATED_ONE_FORMULA_PATCH",
            "changed": "LM_S_N_ONLY",
            "v1_formula": "1/(2*c*sqrt(2*log(n)))",
            "corrected_formula": "1/(c*sqrt(2*log(n)))",
            "local_variance_changed": False,
            "periodicity_changed": False,
            "evt_changed": False,
            "consensus_rule_changed": False,
            "synthetic_protocol_changed": False,
            "purpose": "APPLES_TO_APPLES_V1_REPLAY_AFTER_PRIMARY_SOURCE_AUDIT",
        }
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
