# GOLD CONTROL — DIRECTION ERROR ANATOMY AUDIT V1 RESULT

**Status:** AUDIT_COMPLETE

## Group counts

Pre-2025: {"CAPTURED_UP": 8, "FALSE_UP_ACTUAL_DOWN": 3, "MISSED_UP": 5, "REJECTED_DOWN": 10}  
Locked 2025: {"CAPTURED_UP": 13, "FALSE_UP_ACTUAL_DOWN": 12, "MISSED_UP": 22, "REJECTED_DOWN": 27}

## Cross-period effect-size stability

### CAPTURED_UP_vs_MISSED_UP
- last_quarter_return_norm: STRONG_STABLE; pre delta=-0.650; 2025 delta=-0.552; pre median diff=-0.390748; 2025 median diff=-0.230087; pre BH q=0.30303030303030304
- downside_share: STRONG_STABLE; pre delta=0.600; 2025 delta=1.000; pre median diff=0.0556399; 2025 median diff=0.134954; pre BH q=0.7373737373737375
- post_trough_return_norm: MODERATE_STABLE; pre delta=-0.450; 2025 delta=-0.678; pre median diff=-0.293593; 2025 median diff=-0.560965; pre BH q=0.7373737373737375
- direct_up_fraction: MODERATE_STABLE; pre delta=-0.425; 2025 delta=-0.587; pre median diff=0; 2025 median diff=-0.2; pre BH q=1.0
- close_location: MODERATE_STABLE; pre delta=-0.350; 2025 delta=-0.657; pre median diff=-0.257417; 2025 median diff=-0.51527; pre BH q=0.7373737373737375
- trough_position: MODERATE_STABLE; pre delta=0.350; 2025 delta=0.713; pre median diff=0.307273; 2025 median diff=0.67829; pre BH q=0.7373737373737375

### REJECTED_DOWN_vs_FALSE_UP_ACTUAL_DOWN
- close_location: STRONG_STABLE; pre delta=0.533; 2025 delta=0.759; pre median diff=0.279915; 2025 median diff=0.434905; pre BH q=0.4444444444444444
- last_quarter_return_norm: MODERATE_STABLE; pre delta=0.400; 2025 delta=0.278; pre median diff=0.069989; 2025 median diff=0.106367; pre BH q=0.9297520661157024
- trough_position: MODERATE_STABLE; pre delta=-0.400; 2025 delta=-0.574; pre median diff=-0.261818; 2025 median diff=-0.226756; pre BH q=0.4444444444444444
- downside_share: MODERATE_STABLE; pre delta=-0.333; 2025 delta=-0.716; pre median diff=-0.0785873; 2025 median diff=-0.0914216; pre BH q=0.4090909090909091
- recovery_to_close_ratio: MODERATE_STABLE; pre delta=0.333; 2025 delta=0.753; pre median diff=0.676107; 2025 median diff=0.671121; pre BH q=0.4444444444444444
- sqrt_score: PRE2025_ONLY; pre delta=-0.800; 2025 delta=-0.012; pre median diff=-0.317207; 2025 median diff=0.0319137; pre BH q=0.4090909090909091
- legacy_up_fraction: PRE2025_ONLY; pre delta=-0.400; 2025 delta=-0.040; pre median diff=0; 2025 median diff=0; pre BH q=1.0

### MISSED_UP_vs_REJECTED_DOWN
- lag1_close_return: PRE2025_ONLY; pre delta=-0.520; 2025 delta=0.027; pre median diff=-0.00927157; 2025 median diff=-0.00146754; pre BH q=0.6267436267436267
- recovery_to_close_ratio: PRE2025_ONLY; pre delta=-0.520; 2025 delta=0.098; pre median diff=-0.578791; 2025 median diff=0.0131288; pre BH q=0.6267436267436267
- intraday_end_norm: PRE2025_ONLY; pre delta=-0.480; 2025 delta=0.027; pre median diff=-0.711551; 2025 median diff=-0.223299; pre BH q=0.6267436267436267
- post_trough_return_norm: PRE2025_ONLY; pre delta=-0.480; 2025 delta=0.030; pre median diff=-0.404806; 2025 median diff=-0.116292; pre BH q=0.6267436267436267
- close_location: PRE2025_ONLY; pre delta=-0.440; 2025 delta=0.061; pre median diff=-0.182598; 2025 median diff=0.00162184; pre BH q=0.6267436267436267
- trough_position: PRE2025_ONLY; pre delta=0.440; 2025 delta=-0.089; pre median diff=0.0618182; 2025 median diff=-0.096408; pre BH q=0.6267436267436267
- downside_share: PRE2025_ONLY; pre delta=0.360; 2025 delta=-0.152; pre median diff=0.0570217; 2025 median diff=-0.0144238; pre BH q=0.6267436267436267

### CAPTURED_UP_vs_REJECTED_DOWN
- post_trough_return_norm: STRONG_STABLE; pre delta=-0.800; 2025 delta=-0.675; pre median diff=-0.698399; 2025 median diff=-0.677256; pre BH q=0.020796197266785502
- intraday_end_norm: STRONG_STABLE; pre delta=-0.725; 2025 delta=-0.692; pre median diff=-1.53538; 2025 median diff=-1.27789; pre BH q=0.03446226975638741
- close_location: STRONG_STABLE; pre delta=-0.725; 2025 delta=-0.641; pre median diff=-0.440015; 2025 median diff=-0.513648; pre BH q=0.03446226975638741
- downside_share: STRONG_STABLE; pre delta=0.700; 2025 delta=0.858; pre median diff=0.112662; 2025 median diff=0.120531; pre BH q=0.05629827688651218
- recovery_to_close_ratio: STRONG_STABLE; pre delta=-0.700; 2025 delta=-0.664; pre median diff=-0.836207; 2025 median diff=-0.759475; pre BH q=0.05629827688651218
- trough_position: STRONG_STABLE; pre delta=0.600; 2025 delta=0.635; pre median diff=0.369091; 2025 median diff=0.581882; pre BH q=0.03446226975638741
- last_quarter_return_norm: STRONG_STABLE; pre delta=-0.575; 2025 delta=-0.493; pre median diff=-0.285125; 2025 median diff=-0.193231; pre BH q=0.05814446990917578
- lag1_close_return: STRONG_STABLE; pre delta=-0.550; 2025 delta=-0.521; pre median diff=-0.018134; 2025 median diff=-0.0109128; pre BH q=0.08065953654188948
- max_drawdown_norm: STRONG_STABLE; pre delta=0.500; 2025 delta=0.538; pre median diff=0.536255; 2025 median diff=0.680174; pre BH q=0.13032283620518914
- post_trough_positive_fraction: MODERATE_STABLE; pre delta=0.575; 2025 delta=0.231; pre median diff=0.0129058; 2025 median diff=0.0106061; pre BH q=0.17112299465240643
- direct_up_fraction: MODERATE_STABLE; pre delta=-0.463; 2025 delta=-0.558; pre median diff=-0.2; 2025 median diff=-0.2; pre BH q=0.17112299465240643

Interpretation is descriptive. REJECTED_DOWN is not a validated predicted-DOWN class.
No model was trained or retuned.
