"""Leakage guards and data-quality tests for the OLAY adaptive prototype."""
import csv
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from adaptive_olay import candidate, feature, instant, load_events, walk

class OlayEngineTests(unittest.TestCase):
    def test_provisional_macro_hypothesis(self):
        self.assertEqual(candidate('NFP',-15),'ORG01')
        self.assertEqual(candidate('CPI',.1),'ORG02')
        self.assertIsNone(candidate('FOMC',-25))
        self.assertIsNone(candidate('CPI',0))

    def test_no_timezone_guessing(self):
        with self.assertRaises(ValueError):
            instant('2026-01-09T16:30:00')

    def test_missing_M15_prevents_false_feature(self):
        start=instant('2026-01-02T04:00:00Z')
        bars=[dict(end=start+timedelta(minutes=i*15),close=2000+i) for i in range(17)]
        self.assertNotEqual(feature(bars)['state'],'MISSING')
        del bars[5]
        self.assertEqual(feature(bars)['state'],'MISSING')

    def test_future_news_never_appears_early(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'events.csv'
            names=['event_id','firstprint_utc','available_at_utc','firstprint_status','org_candidates','kind','macro_surprise']
            with path.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=names)
                writer.writeheader()
                writer.writerow(dict(event_id='future',firstprint_utc='2026-01-02T10:00:00Z',
                    available_at_utc='2026-01-02T10:05:00Z',firstprint_status='VERIFIED',
                    org_candidates='ORG02',kind='NFP',macro_surprise='100'))
                writer.writerow(dict(event_id='unverified',firstprint_utc='2026-01-02T08:00:00Z',
                    available_at_utc='2026-01-02T08:01:00Z',firstprint_status='UNVERIFIED',
                    org_candidates='ORG01',kind='CPI',macro_surprise='-0.1'))
            start=instant('2026-01-02T04:00:00Z')
            bars=[dict(start=start+timedelta(minutes=i*15),
                end=start+timedelta(minutes=(i+1)*15),close=2000+i)
                for i in range(32)]
            out=list(walk(bars,load_events(str(path))))
            early=next(x for x in out if x['at_utc']=='2026-01-02T09:00:00+00:00')
            self.assertNotIn('future',early['event_ids'])
            self.assertEqual(early['verified_groups'],[])
            later=next(x for x in out if x['at_utc']=='2026-01-02T10:15:00+00:00')
            self.assertEqual(later['verified_groups'],['ORG02'])
            self.assertEqual(later['preliminary_predictions'][0]['status'],'ABSTAIN_INSUFFICIENT_HISTORY')

    def test_forward_label_matures_only_after_four_hours(self):
        start=instant('2026-01-02T00:00:00Z')
        bars=[dict(start=start+timedelta(minutes=i*15),
            end=start+timedelta(minutes=(i+1)*15),close=2000+i)
            for i in range(70)]
        out=list(walk(bars,[]))
        self.assertEqual(out[0]['price_state_distribution']['n_total'],0)
        self.assertGreater(out[-1]['price_state_distribution']['n_total'],0)
        self.assertLess(out[-1]['price_state_distribution']['n_total'],5)
        self.assertTrue(all(x['trade'].startswith('DISABLED') for x in out))

if __name__=='__main__': unittest.main()
