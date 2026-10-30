import unittest
from gold_axis_2026.research.case_control_v13.risk_v40_causal_rolling_risk_rank import (
 past_only_ranks,WINDOW,CUTOFFS
)
class V40RankTests(unittest.TestCase):
 def test_no_rank_without_60_completed_prior_days(self):
  a=past_only_ranks([],[.1]*59)
  self.assertTrue(all(x is None for x in a))
 def test_prior_60_available_first_rank(self):
  a=past_only_ranks([.1]*60,[.2])
  self.assertAlmostEqual(a[0],1)
 def test_future_extension_does_not_rewrite_prior_ranks(self):
  p=[i/100 for i in range(100)]
  first=past_only_ranks([],[*p])
  longer=past_only_ranks([],[*p,0,0,0])
  self.assertEqual(first,longer[:len(first)])
 def test_rank_adapts_after_distribution_shift_without_future_data(self):
  p=[.01]*60
  rank=past_only_ranks(p,[.9]*65)
  self.assertEqual(rank[0],1)
  self.assertGreaterEqual(rank[-1],0.98)
 def test_rank_uses_only_last_60_days(self):
  a=past_only_ranks([.01]*60+[.6]*60,[.3])[0]
  self.assertLess(a,.05)
 def test_thresholds_not_fitted_to_2026(self):
  self.assertEqual(WINDOW,60)
  self.assertEqual(CUTOFFS[-1],1.01)
if __name__=="__main__":unittest.main()
