# incremental contribution v145

```json
{
  "cross_role_ranking": false,
  "rows": [
    {
      "classification": "UNIQUE_CONTRIBUTION_PROVEN",
      "engine_id": "CAUSAL_PATCH",
      "monthly_win_rate_vs_rw": 0.631578947368421,
      "n": 19,
      "residual_correlation_with_rw": 0.9926447654979398,
      "sum_ae_reduction_vs_rw": 154.3983426412774
    },
    {
      "classification": "UNIQUE_CONTRIBUTION_PROVEN",
      "engine_id": "VW_MIDAS_MSVR_SUCCESSOR_V1",
      "monthly_win_rate_vs_rw": 0.631578947368421,
      "n": 19,
      "residual_correlation_with_rw": 0.9340208748800192,
      "sum_ae_reduction_vs_rw": 692.1852435899368
    },
    {
      "classification": "UNIQUE_CONTRIBUTION_PROVEN",
      "engine_id": "MOMENTUM_3M",
      "monthly_win_rate_vs_rw": 0.6842105263157895,
      "n": 19,
      "residual_correlation_with_rw": 0.7634403255831164,
      "sum_ae_reduction_vs_rw": 336.92942760492633
    },
    {
      "classification": "MANDATORY_BENCHMARK",
      "engine_id": "RANDOM_WALK",
      "monthly_win_rate_vs_rw": 0.0,
      "n": 19,
      "residual_correlation_with_rw": 0.9999999999999999,
      "sum_ae_reduction_vs_rw": 0.0
    },
    {
      "classification": "COMPLEMENTARY",
      "cross_objective_ranking": "PROHIBITED",
      "engine_id": "MONTHLY_DIRECTION_3M",
      "role_metric": {
        "cells": 20,
        "hit_rate_non_neutral": 0.6,
        "hits": 12,
        "misses": 8,
        "neutral": 0
      }
    },
    {
      "classification": "COMPLEMENTARY",
      "cross_objective_ranking": "PROHIBITED",
      "engine_id": "FAST",
      "role_metric": {
        "direct_false_flip_proxy": 0,
        "distinct_state_share": 0.9025,
        "mean_persistence_observations": 6.349206349206349,
        "next_observation_direction_agreement": 0.4631578947368421,
        "observations": 400,
        "state_changes": 62
      }
    },
    {
      "classification": "COMPLEMENTARY",
      "cross_objective_ranking": "PROHIBITED",
      "engine_id": "SLOW",
      "role_metric": {
        "direct_false_flip_proxy": 0,
        "distinct_state_share": 0.75,
        "mean_persistence_observations": 8.333333333333334,
        "next_observation_direction_agreement": 0.4105263157894737,
        "observations": 400,
        "state_changes": 47
      }
    },
    {
      "classification": "COMPLEMENTARY",
      "cross_objective_ranking": "PROHIBITED",
      "engine_id": "MACRO_EVENT_SUCCESSOR_V2",
      "role_metric": {
        "complete_case_months": 126,
        "contractual_exclusion": "2025-10",
        "event_reaction": {
          "acceptance_gate_median_signed_r15_gt": 0.0,
          "acceptance_gate_sign_test_p_lte": 0.1,
          "decision_counts_after": {
            "decision_events": 0,
            "decision_runs": 0,
            "decision_signal_snapshots": 0,
            "monthly_forecast_contracts": 0
          },
          "decision_counts_before": {
            "decision_events": 0,
            "decision_runs": 0,
            "decision_signal_snapshots": 0,
            "monthly_forecast_contracts": 0
          },
          "direction_vote": false,
          "directional_hit_rate": 0.875,
          "directional_hits": 7,
          "engine_id": "MACRO_EVENT_SUCCESSOR_V2",
          "event_count": 8,
          "events": [
            {
              "directional_hit": false,
              "evidence_window": "VAL",
              "macro_state": "GOLD_ADVERSE_MACRO_SHOCK",
              "r15_pct": 0.085486,
              "r30_pct": -0.15447,
              "r5_pct": -0.363774,
              "reference_month": "2021-02",
              "release_date": "2021-03-05",
              "response_sha256": "aebb0fd848439162c8a41037afacbdf8bc0942dfc65f1ddc4c09b6d8f04f5e40",
              "signed_r15_pct": -0.085486
            },
            {
              "directional_hit": true,
              "evidence_window": "VAL",
              "macro_state": "GOLD_SUPPORTIVE_MACRO_SHOCK",
              "r15_pct": 1.068453,
              "r30_pct": 1.111898,
              "r5_pct": 0.88699,
              "reference_month": "2021-04",
              "release_date": "2021-05-07",
              "response_sha256": "011f34cfb598af93ef2b96b41d2ce200591830f68da9bd4abf67db0aa79d4338",
              "signed_r15_pct": 1.068453
            },
            {
              "directional_hit": true,
              "evidence_window": "VAL",
              "macro_state": "GOLD_ADVERSE_MACRO_SHOCK",
              "r15_pct": -1.090097,
              "r30_pct": -1.290669,
              "r5_pct": -0.521158,
              "reference_month": "2021-07",
              "release_date": "2021-08-06",
              "response_sha256": "f2da72888c63b7f150142877e24fbb3cc8b48110a3a0c0964228bb2db3eff2e3",
              "signed_r15_pct": 1.090097
            },
            {
              "directional_hit": true,
              "evidence_window": "VAL",
              "macro_state": "GOLD_ADVERSE_MACRO_SHOCK",
              "r15_pct": -0.846016,
              "r30_pct": -0.980582,
              "r5_pct": -0.660709,
              "reference_month": "2022-01",
              "release_date": "2022-02-04",
              "response_sha256": "99ea295cad7f5d29b1c8855416a9bc086abd4714ae75cbfee31949e4c61bff00",
              "signed_r15_pct": 0.846016
            },
            {
              "directional_hit": true,
              "evidence_window": "VAL",
              "macro_state": "GOLD_ADVERSE_MACRO_SHOCK",
              "r15_pct": -0.84971,
              "r30_pct": -1.106299,
              "r5_pct": -0.628899,
              "reference_month": "2022-07",
              "release_date": "2022-08-05",
              "response_sha256": "9dcb1e02d83795bd45a4eedac6c554e328e27027aa05660e6bea1dd92939a5d1",
              "signed_r15_pct": 0.84971
            },
            {
              "directional_hit": true,
              "evidence_window": "VAL",
              "macro_state": "GOLD_ADVERSE_MACRO_SHOCK",
              "r15_pct": -1.352256,
              "r30_pct": -1.40973,
              "r5_pct": -0.897146,
              "reference_month": "2023-01",
              "release_date": "2023-02-03",
              "response_sha256": "ffba50112c540bf60bd87522b063649c52d5c9a29785333d5276bfd91ebdb48a",
              "signed_r15_pct": 1.352256
            },
            {
              "directional_hit": true,
              "evidence_window": "VAL",
              "macro_state": "GOLD_ADVERSE_MACRO_SHOCK",
              "r15_pct": -1.251172,
              "r30_pct": -1.16563,
              "r5_pct": -0.356425,
              "reference_month": "2023-04",
              "release_date": "2023-05-05",
              "response_sha256": "0d916fb3afb9fb0e6849a2dad229ab23932ae98fa42ef8c7db3b7e081a32f530",
              "signed_r15_pct": 1.251172
            },
            {
              "directional_hit": true,
              "evidence_window": "LOCK",
              "macro_state": "GOLD_ADVERSE_MACRO_SHOCK",
              "r15_pct": -0.675211,
              "r30_pct": -1.016714,
              "r5_pct": -0.547086,
              "reference_month": "2024-01",
              "release_date": "2024-02-02",
              "response_sha256": "5cab93ce8390aa0fe099df99970b210d5505d8c9def41d17aabf9dce91532d36",
              "signed_r15_pct": 0.675211
            }
          ],
          "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
          "forecast_or_decision_write": false,
          "gold_source": "Twelve Data XAU/USD Commodity Aggregate",
          "interval": "1min",
          "median_signed_r15_pct": 0.9590818647119803,
          "model_result_persisted_to_neon": false,
          "one_sided_exact_sign_test_p": 0.03515625,
          "primary_window": "08:29_bar_close_to_08:44_bar_close",
          "production_db_write": false,
          "promotion_status": "ELIGIBLE_FOR_PROMOTION_CHANGE_CONTROL",
          "reaction_gate_pass": true,
          "source_run_id": "6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a",
          "status": "PASS_EVENT_REACTION_EVIDENCE",
          "timezone": "America/New_York",
          "validation_id": "MACRO_EVENT_SUCCESSOR_V2_EVENT_REACTION_VALIDATION_V1"
        },
        "shock_events": [
          {
            "adverse_breadth": 1,
            "evidence_window": "DEV",
            "reference_month": "2020-03",
            "score": 3.869057,
            "state": "GOLD_SUPPORTIVE_MACRO_SHOCK",
            "supportive_breadth": 2
          },
          {
            "adverse_breadth": 3,
            "evidence_window": "DEV",
            "reference_month": "2020-04",
            "score": -20.084836,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 0
          },
          {
            "adverse_breadth": 2,
            "evidence_window": "DEV",
            "reference_month": "2020-05",
            "score": -61.820908,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 1
          },
          {
            "adverse_breadth": 2,
            "evidence_window": "DEV",
            "reference_month": "2020-06",
            "score": -10.184332,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 1
          },
          {
            "adverse_breadth": 3,
            "evidence_window": "DEV",
            "reference_month": "2020-07",
            "score": -3.011789,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 0
          },
          {
            "adverse_breadth": 2,
            "evidence_window": "DEV",
            "reference_month": "2020-10",
            "score": -1.742991,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 1
          },
          {
            "adverse_breadth": 2,
            "evidence_window": "VAL",
            "reference_month": "2021-02",
            "score": -1.138058,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 0
          },
          {
            "adverse_breadth": 1,
            "evidence_window": "VAL",
            "reference_month": "2021-04",
            "score": 2.403954,
            "state": "GOLD_SUPPORTIVE_MACRO_SHOCK",
            "supportive_breadth": 2
          },
          {
            "adverse_breadth": 3,
            "evidence_window": "VAL",
            "reference_month": "2021-07",
            "score": -1.203258,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 0
          },
          {
            "adverse_breadth": 2,
            "evidence_window": "VAL",
            "reference_month": "2022-01",
            "score": -1.544667,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 1
          },
          {
            "adverse_breadth": 3,
            "evidence_window": "VAL",
            "reference_month": "2022-07",
            "score": -1.73386,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 0
          },
          {
            "adverse_breadth": 2,
            "evidence_window": "VAL",
            "reference_month": "2023-01",
            "score": -1.73662,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 0
          },
          {
            "adverse_breadth": 3,
            "evidence_window": "VAL",
            "reference_month": "2023-04",
            "score": -1.179878,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 0
          },
          {
            "adverse_breadth": 3,
            "evidence_window": "LOCK",
            "reference_month": "2024-01",
            "score": -1.565782,
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "supportive_breadth": 0
          }
        ],
        "state_counts": [
          {
            "count": 5,
            "evidence_window": "DEV",
            "state": "GOLD_ADVERSE_MACRO_SHOCK"
          },
          {
            "count": 1,
            "evidence_window": "DEV",
            "state": "GOLD_SUPPORTIVE_MACRO_SHOCK"
          },
          {
            "count": 24,
            "evidence_window": "DEV",
            "state": "INSUFFICIENT_HISTORY"
          },
          {
            "count": 29,
            "evidence_window": "DEV",
            "state": "MACRO_MIXED_OR_SMALL"
          },
          {
            "count": 1,
            "evidence_window": "LOCK",
            "state": "GOLD_ADVERSE_MACRO_SHOCK"
          },
          {
            "count": 30,
            "evidence_window": "LOCK",
            "state": "MACRO_MIXED_OR_SMALL"
          },
          {
            "count": 6,
            "evidence_window": "VAL",
            "state": "GOLD_ADVERSE_MACRO_SHOCK"
          },
          {
            "count": 1,
            "evidence_window": "VAL",
            "state": "GOLD_SUPPORTIVE_MACRO_SHOCK"
          },
          {
            "count": 29,
            "evidence_window": "VAL",
            "state": "MACRO_MIXED_OR_SMALL"
          }
        ],
        "status": "PASS_V2_ROBUST_PREREG_REPLAY_REPRODUCIBLE"
      }
    },
    {
      "classification": "INSUFFICIENT_EVIDENCE",
      "cross_objective_ranking": "PROHIBITED",
      "engine_id": "BOCPD_RETURN_SUCCESSOR_V1",
      "role_metric": {
        "blocker_code": "CORE5_GOLD_MONTHLY_2026_08_NOT_FOUND",
        "partial_risk_validation": "VALIDATION_RISK_DIAGNOSTIC_COMPLETE",
        "status": "BLOCKED_DATA"
      }
    },
    {
      "classification": "INSUFFICIENT_EVIDENCE",
      "cross_objective_ranking": "PROHIBITED",
      "engine_id": "EMERGENCY_LEVEL",
      "role_metric": {
        "alert_months": 16,
        "alert_observations": 200,
        "first_alert_by_month": {
          "2025-01": "2025-01-21",
          "2025-02": "2025-02-14",
          "2025-03": "2025-03-27",
          "2025-04": "2025-04-11",
          "2025-09": "2025-09-02",
          "2025-10": "2025-10-01",
          "2025-11": "2025-11-04",
          "2025-12": "2025-12-12",
          "2026-01": "2026-01-09",
          "2026-02": "2026-02-03",
          "2026-03": "2026-03-01",
          "2026-04": "2026-04-02",
          "2026-05": "2026-05-04",
          "2026-06": "2026-06-05",
          "2026-07": "2026-07-18",
          "2026-08": "2026-08-08"
        },
        "independent_false_miss_label": "NOT_PROVEN",
        "observations": 400
      }
    },
    {
      "classification": "INSUFFICIENT_EVIDENCE",
      "cross_objective_ranking": "PROHIBITED",
      "engine_id": "EMERGENCY_REVERSAL",
      "role_metric": {
        "alert_months": 9,
        "alert_observations": 43,
        "first_alert_by_month": {
          "2025-10": "2025-10-21",
          "2025-11": "2025-11-10",
          "2025-12": "2025-12-29",
          "2026-01": "2026-01-30",
          "2026-02": "2026-02-17",
          "2026-03": "2026-03-03",
          "2026-04": "2026-04-14",
          "2026-05": "2026-05-08",
          "2026-06": "2026-06-15"
        },
        "independent_false_miss_label": "NOT_PROVEN",
        "observations": 400
      }
    },
    {
      "classification": "COMPLEMENTARY",
      "cross_objective_ranking": "PROHIBITED",
      "engine_id": "GVZ_RISK",
      "role_metric": {
        "cap_below_one": 124,
        "cap_runs_mean": 9.674418604651162,
        "mean_next_gold_return_stressed": -0.0005429308685503387,
        "mean_next_gold_return_unstressed": 0.0016634818937528069,
        "observations": 416,
        "panic": 53
      }
    }
  ],
  "thresholds_changed": false,
  "weights_optimized": false
}
```
