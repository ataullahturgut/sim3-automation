import unittest
from gold_axis_2026.research.case_control_v13.risk_v45_v22_watch_duration_robustness import DURATIONS,RULES
class V45SettingsTests(unittest.TestCase):
 def test_all_fixed_watch_expirations(self):
  self.assertEqual(DURATIONS,(4,6,8,10,12,16))
 def test_original_and_structural_both_compared(self):
  self.assertIn("V22_IMMEDIATE",RULES)
  self.assertIn("V43_STRUCTURAL_1",RULES)
 def test_no_2026_threshold_tuning(self):
  self.assertEqual(len(RULES),4)
if __name__=="__main__":unittest.main()
