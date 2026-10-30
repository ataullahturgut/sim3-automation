"""Source-shape, 15 minute timestamp and no-invented-metals checks."""
import json
import unittest
from datetime import date,timedelta
from gold_axis_2026.data_pipeline.staktrakr_fourmetal_15min_research_ingest_v1 import (
    validate_snapshot,check_day
)
D=date(2026,9,16)
URL="https://raw.githubusercontent.com/lbruton/StakTrakrApi/api/data/15min/2026/09/16/1900.json"
def payload(bad=None):
    rows=[{"metal":m,"spot":v,"source":"seed","provider":"StakTrakr",
           "timestamp":"2026-09-16 19:00:02"}
          for m,v in (("Gold",4300),("Silver",63.1),("Platinum",1790),("Palladium",1300))]
    rows.append({"metal":"Copper","spot":0.4,"source":"seed","provider":"StakTrakr",
                 "timestamp":"2026-09-16 19:00:02"})
    if bad:bad(rows)
    return json.dumps(rows).encode()
class Tests(unittest.TestCase):
    def test_valid_four_metals_same_timestamp_window(self):
        rows=validate_snapshot(D,19*60,payload(),URL)
        self.assertEqual(len(rows),4)
        self.assertEqual({x["metal"] for x in rows},{"AU","AG","PT","PD"})
        self.assertTrue(all(x["window_start_utc"].endswith("19:00:00+00:00") for x in rows))
    def test_source_is_preserved_not_firstprint(self):
        rows=validate_snapshot(D,19*60,payload(),URL)
        self.assertTrue(all(x["source_label"]=="seed" for x in rows))
        self.assertTrue(all(x["provider_label"]=="StakTrakr" for x in rows))
        self.assertTrue(all(len(x["snapshot_sha256"])==64 for x in rows))
    def test_duplicate_metal_blocked(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            validate_snapshot(D,19*60,payload(lambda r:r.append(r[0].copy())),URL)
    def test_missing_metal_blocked(self):
        with self.assertRaisesRegex(ValueError,"NOT_FOUR_METAL"):
            validate_snapshot(D,19*60,payload(lambda r:r.pop(1)),URL)
    def test_future_bar_misuse_blocked(self):
        with self.assertRaisesRegex(ValueError,"QUOTE_OUTSIDE"):
            validate_snapshot(D,19*60,payload(lambda r:r[0].update(timestamp="2026-09-16 19:20:00")),URL)
    def test_invalid_numeric_blocked(self):
        with self.assertRaises(ValueError):
            validate_snapshot(D,19*60,payload(lambda r:r[0].update(spot=-1)),URL)
    def test_wrong_floor_does_not_accept(self):
        with self.assertRaisesRegex(ValueError,"BAD_QUARTER_HOUR"):
            validate_snapshot(D,19*60+1,payload(),URL)
    def test_older_than_available_archive_rejected(self):
        with self.assertRaisesRegex(ValueError,"DAY_NOT_IN_SOURCE_ARCHIVE"):
            check_day(date(2025,8,1))
    def test_future_dates_rejected(self):
        with self.assertRaisesRegex(ValueError,"DAY_NOT_IN_SOURCE_ARCHIVE"):
            check_day(date(2027,1,1))
    def test_revised_sample_is_new_version_not_silent_rewrite(self):
        before=validate_snapshot(D,19*60,payload(),URL)
        after=validate_snapshot(D,19*60,payload(lambda r:r[0].update(spot=4301)),URL)
        self.assertNotEqual(before[0]["row_sha256"],after[0]["row_sha256"])
if __name__=="__main__":unittest.main()
