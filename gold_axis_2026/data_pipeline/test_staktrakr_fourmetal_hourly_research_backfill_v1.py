"""V38 source provenance, integrity, and non-pretend-hourly tests."""
import json
import unittest
from datetime import date,datetime,timezone,timedelta
from gold_axis_2026.data_pipeline.staktrakr_fourmetal_hourly_research_backfill_v1 import (
    CODES,validate_day,fail_if_bad_date
)
DAY=date(2026,9,16)
URL="https://raw.githubusercontent.com/lbruton/StakTrakrApi/api/data/v2/spot/xag/2026/09/16.json"

def make_payload(n=4,items=24,generated="2026-09-16T23:53:05Z",mut=None):
    rows=[]
    for i in range(items):
        r={"t":f"2026-09-16T{i:02}:00:00Z","ts":1789516800+i*3600,
           "open":70.0,"high":71.0,"low":69.0,"close":70.5,"avg":70.1,"n":n}
        rows.append(r)
    if mut is not None:mut(rows)
    return json.dumps({"v":2,"generated_at":generated,
          "stale_after":3600,"data":rows}).encode()

class HourlyChecks(unittest.TestCase):
    def test_valid_four_metal_hourly_schema(self):
        for m in CODES:
            rows,meta=validate_day(m,DAY,make_payload(),URL.replace("xag",m))
            self.assertEqual(len(rows),24)
            self.assertEqual(meta["oneSampleSkipped"],0)
            self.assertTrue(all(x["source_samples"]==4 for x in rows))
            self.assertTrue(all(x["source_date"]=="2026-09-16" for x in rows))
    def test_daily_backfill_masquerading_as_hourly_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"TOO_FEW_REAL_HOURLY"):
            validate_day("xag",DAY,make_payload(n=1),URL)
    def test_mixed_1sample_entries_are_not_used(self):
        p=make_payload(mut=lambda rows: rows[0].update(n=1))
        rows,meta=validate_day("xag",DAY,p,URL)
        self.assertEqual(len(rows),23)
        self.assertEqual(meta["oneSampleSkipped"],1)
    def test_partial_source_day_rejected(self):
        with self.assertRaisesRegex(ValueError,"HOURLY_DATA_TOO_SPARSE"):
            validate_day("xag",DAY,make_payload(items=1),URL)
    def test_duplicate_hours_fail(self):
        def duplicate(rows):rows[1]["t"]=rows[0]["t"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_HOUR"):
            validate_day("xag",DAY,make_payload(mut=duplicate),URL)
    def test_price_inconsistent_fail(self):
        def invalid(rows):rows[5]["low"]=90
        with self.assertRaisesRegex(ValueError,"OHLC_PRICE_INCONSISTENT"):
            validate_day("xag",DAY,make_payload(mut=invalid),URL)
    def test_generated_at_day_wrong(self):
        with self.assertRaisesRegex(ValueError,"GENERATED_DATE_DOES_NOT_MATCH"):
            validate_day("xag",DAY,make_payload(generated="2026-09-17T00:01:00Z"),URL)
    def test_no_fake_2024_hourly_backdating(self):
        with self.assertRaisesRegex(ValueError,"DATE_BEFORE_REAL_HOURLY"):
            fail_if_bad_date(date(2024,1,1))
    def test_no_future_research_data(self):
        with self.assertRaisesRegex(ValueError,"DATE_BEFORE_REAL_HOURLY"):
            fail_if_bad_date(date(2027,1,1))
    def test_blob_revision_preserved(self):
        rows,_=validate_day("xag",DAY,make_payload(),URL)
        p=make_payload(mut=lambda a:a[0].update(close=70.6))
        updated,_=validate_day("xag",DAY,p,URL)
        self.assertNotEqual(rows[0]["source_blob_sha256"],updated[0]["source_blob_sha256"])
        self.assertNotEqual(rows[0]["source_row_sha256"],updated[0]["source_row_sha256"])
if __name__=="__main__":unittest.main()
