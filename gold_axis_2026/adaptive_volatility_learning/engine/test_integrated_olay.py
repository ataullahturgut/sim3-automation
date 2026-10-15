"""Regression and chronology tests for the integrated OLAY/OGREN module."""
import unittest
from pathlib import Path
from datetime import timedelta
from integrated_olay import load_cases, audit, predict, overlay_groups, instant, experts

HERE=Path(__file__).resolve().parent
SNAPSHOT=HERE/'HISTORICAL_MACRO_M15_SNAPSHOTS_2023_2025.csv'

class IntegratedEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=load_cases(SNAPSHOT)

    def test_47_valid_55_stored_event_snapshots(self):
        self.assertEqual(len(self.rows),47)
        self.assertEqual(sum(x['time'].year==2023 for x in self.rows),10)
        self.assertEqual(sum(x['time'].year==2024 for x in self.rows),19)
        self.assertEqual(sum(x['time'].year==2025 for x in self.rows),18)

    def test_frozen_holdout_is_not_price_overfit(self):
        result=audit(self.rows,year=2025,mode='frozen')
        m=result['test']
        self.assertEqual(m['macro']['correct'],11)
        self.assertEqual(m['joint']['correct'],10)
        self.assertEqual(m['base']['correct'],8)
        self.assertGreater(m['joint']['brier'],m['macro']['brier'])

    def test_prequential_matures_labels_before_reuse(self):
        result=audit(self.rows,year=2025,mode='prequential')
        self.assertEqual(result['test']['macro']['correct'],10)
        first=result['records'][0]
        second=result['records'][1]
        self.assertLess(instant(first['due']),instant(second['at_utc']))
        self.assertGreaterEqual(second['n_history'],first['n_history'])

    def test_unknown_events_never_force_group(self):
        t=instant('2026-01-09T16:30:00Z')
        good=dict(id='E',at=t,firstprint=t,groups=['ORG01','ORG02'],
                  kind='NFP',surprise=-5,status='VERIFIED')
        bad=dict(id='BAD',at=t-timedelta(hours=1),firstprint=t,
                 groups=['ORG12'],kind='OTHER',surprise=None,status='UNVERIFIED')
        self.assertEqual(overlay_groups([good],t-timedelta(seconds=1))['org_decision'],'UNKNOWN')
        result=overlay_groups([good,bad],t)
        self.assertEqual([x[0] for x in result['active_candidates']],['ORG01','ORG02'])
        self.assertNotIn('BAD',result['evidence_ids'])

    def test_same_event_not_in_own_training(self):
        x=next(x for x in self.rows if x['time'].year==2025)
        past=[p for p in self.rows if p['due']<=x['time']]
        self.assertNotIn(x['id'],{p['id'] for p in past})
        m=experts(past,x['candidate'],x['pre4h'])
        self.assertTrue(0<m['macro']<1)
        self.assertTrue(0<m['joint']<1)

    def test_decision_abstains_with_few_cases(self):
        x=self.rows[0]
        result=predict([],x['candidate'],x['pre4h'])
        self.assertEqual(result['evidence_gate'],'ABSTAIN_FEW_CASES')
        self.assertEqual(result['action'],'DISABLED')

if __name__=='__main__': unittest.main()
