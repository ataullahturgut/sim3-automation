import unittest
import pandas as pd
from risk_v24_source_publication_audit import main,O

class ExternalReferenceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main()
        cls.price=pd.read_csv(O/"v24_external_price_source_comparison.csv").set_index("date")
        cls.cftc=pd.read_csv(O/"v24_cftc_official_schedule_spotchecks.csv")
    def test_corrupt_feb_27_source_kept_quarantined(self):
        r=self.price.loc["2026-02-27"]
        self.assertAlmostEqual(r.stored_price,3516.02)
        self.assertAlmostEqual(r.secondary_LBMA_AM,5174.10)
        self.assertAlmostEqual(r.secondary_LBMA_PM,5222.30)
        self.assertTrue(r.quarantined)
        self.assertFalse(r.safe_to_overwrite_original_source)
    def test_source_is_not_uniformly_exact_fixing(self):
        self.assertTrue(self.price.loc["2026-01-29","aligns_exact_AM"])
        self.assertFalse(self.price.loc["2026-02-26","aligns_exact_AM"])
        self.assertFalse(self.price.loc["2026-10-16","aligns_exact_PM"])
    def test_cftc_shutdown_date_official(self):
        x=self.cftc.set_index("CFTC_report_as_of").loc["2025-09-30"]
        self.assertEqual(x.official_released,"2025-11-19")
        self.assertEqual(x.conservative_usable,"2025-11-20")
    def test_june_holiday_delay(self):
        x=self.cftc.set_index("CFTC_report_as_of").loc["2026-06-16"]
        self.assertEqual(x.official_released,"2026-06-22")
if __name__=="__main__":unittest.main(verbosity=2)
