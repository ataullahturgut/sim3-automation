from __future__ import annotations

from pathlib import Path
import pandas as pd

from gold_axis_2026.v170_research import run_v170_public_positioning_context as base


def prepare_cot_r1(path: Path) -> pd.DataFrame:
    # Read as text so the official six-character CFTC contract market code 088691
    # retains its leading zero. This is an implementation/schema fix only.
    d = pd.read_csv(path, dtype=str)
    code_col = base.resolve_col(d, ["cftc_contract_market_code", "CFTC_Contract_Market_Code"])
    code = d[code_col].astype(str).str.strip().str.replace(".0", "", regex=False).str.zfill(6)
    d = d[code.eq("088691")].copy()
    if d.empty:
        raise RuntimeError("V170_NO_GOLD_COT_ROWS_R1")
    report_col = base.resolve_col(d, ["report_date_as_yyyy_mm_dd", "Report_Date_as_YYYY_MM_DD"])
    oi_col = base.resolve_col(d, ["open_interest_all", "Open_Interest_All"])
    pm_l = base.resolve_col(d, ["prod_merc_positions_long", "prod_merc_positions_long_all", "Prod_Merc_Positions_Long_All"])
    pm_s = base.resolve_col(d, ["prod_merc_positions_short", "prod_merc_positions_short_all", "Prod_Merc_Positions_Short_All"])
    sw_l = base.resolve_col(d, ["swap_positions_long_all", "Swap_Positions_Long_All"])
    sw_s = base.resolve_col(d, ["swap__positions_short_all", "swap_positions_short_all", "Swap__Positions_Short_All"])
    mm_l = base.resolve_col(d, ["m_money_positions_long_all", "M_Money_Positions_Long_All"])
    mm_s = base.resolve_col(d, ["m_money_positions_short_all", "M_Money_Positions_Short_All"])
    z = pd.DataFrame({
        "report_date": pd.to_datetime(d[report_col], errors="coerce"),
        "oi": pd.to_numeric(d[oi_col], errors="coerce"),
        "pm_long": pd.to_numeric(d[pm_l], errors="coerce"), "pm_short": pd.to_numeric(d[pm_s], errors="coerce"),
        "sw_long": pd.to_numeric(d[sw_l], errors="coerce"), "sw_short": pd.to_numeric(d[sw_s], errors="coerce"),
        "mm_long": pd.to_numeric(d[mm_l], errors="coerce"), "mm_short": pd.to_numeric(d[mm_s], errors="coerce"),
    }).dropna(subset=["report_date", "oi"])
    z = z[z["oi"] > 0].sort_values("report_date").drop_duplicates("report_date", keep="last").reset_index(drop=True)
    z["pub_cot_mm_net_oi"] = (z["mm_long"] - z["mm_short"]) / z["oi"]
    z["pub_cot_prod_net_oi"] = (z["pm_long"] - z["pm_short"]) / z["oi"]
    z["pub_cot_swap_net_oi"] = (z["sw_long"] - z["sw_short"]) / z["oi"]
    z["pub_cot_mm_net_change_1w_oi"] = z["pub_cot_mm_net_oi"].diff(1)
    z["pub_cot_oi_change_1w"] = z["oi"].pct_change(1)
    z["available_date"] = z["report_date"] + pd.to_timedelta(7, unit="D")
    for rd, ad in base.SHUTDOWN_RELEASES.items():
        z.loc[z["report_date"] == pd.Timestamp(rd), "available_date"] = pd.Timestamp(ad)
    return z[["report_date", "available_date", "pub_cot_mm_net_oi", "pub_cot_prod_net_oi", "pub_cot_swap_net_oi", "pub_cot_mm_net_change_1w_oi", "pub_cot_oi_change_1w"]]


if __name__ == "__main__":
    base.prepare_cot = prepare_cot_r1
    base.main()
