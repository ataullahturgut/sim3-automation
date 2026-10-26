import unittest,json
import pandas as pd,numpy as np
import research as r
class ResearchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.f=pd.read_csv(r.O/'research_feature_panel.csv',parse_dates=['origin']).set_index('origin');cls.cols=json.loads((r.O/'feature_contract.json').read_text())['features'];cls.source,cls.cot,_=r.old.load(r.I/'source.zip',r.O/'CFTC_ION_corrected.csv');cls.ref=r.old.make_rows(cls.source,cls.cot);cls.w=pd.read_csv(r.O/'cftc_parsed_all.csv')
 def test_original_reference(self):
  x=json.loads((r.O/'replay/gold_risk_v2_manifest.json').read_text())['score_summary']
  self.assertEqual([x['2026'][k]['count_red'] for k in ['BASE_14','BASE_14_PLUS_CFTC_7']],[46,31])
  self.assertEqual([x['2026'][k]['y_next5_drawdown5_red']['false_alert_origin_days'] for k in ['BASE_14','BASE_14_PLUS_CFTC_7']],[37,25])
 def test_future_price_cannot_change_historical_features(self):
  import copy
  s=copy.deepcopy(self.source)
  for row in s['prices']:
   if row['date']>='2023-01-01':row['metals']=[v*11 for v in row['metals']]
  a,_=r.build_panel(s,self.ref,self.w)
  np.testing.assert_allclose(a.loc[:'2022-12-31',self.cols],self.f.loc[:'2022-12-31',self.cols],rtol=1e-9,atol=1e-10,equal_nan=True)
 def test_training_dates(self):
  t=pd.read_csv(r.O/'training_rows.csv');self.assertTrue((t.origin<'2023-01-01').all());self.assertEqual(t.y.unique().tolist(),[1,0])
 def test_controls_nonoverlap(self):
  e=pd.read_csv(r.O/'historical_events.csv');c=pd.read_csv(r.O/'matched_controls.csv')
  self.assertTrue(c.groupby('event_id').size().between(2,4).all());self.assertTrue(c.control_date.is_unique)
  for _,q in c.iterrows():
   self.assertEqual(q.case_date[:4],q.control_date[:4]);self.assertTrue((abs(e.peak_i-q.control_i)>40).all());self.assertGreater(self.f.iloc[q.control_i].future_min10,-.05)
  for a,b in zip(sorted(c.control_i),sorted(c.control_i)[1:]):self.assertGreater(b-a,40)
 def test_no_backdated_cftc(self):
  c=pd.read_csv(r.O/'CFTC_ION_date_changes.csv');self.assertTrue((c.research_available>c.official_publication).all());self.assertTrue((c.research_available>c.old_proxy).all())
  for q in self.ref:self.assertLessEqual(q['cftc_available_date'],q['origin'])
 def test_unknown_firstprints_block(self):
  with self.assertRaisesRegex(ValueError,'STRICT_PIT_BLOCK'):r.strict_gate()
 def test_bad_price_window(self):
  ds=[q['date'] for q in self.source['prices']]
  for q in self.ref:
   j=ds.index(q['origin']);self.assertNotIn('2026-02-27',ds[j-20:j+6])
 def test_same_test_origins(self):
  d=pd.read_csv(r.O/'daily_all_models.csv');sets=[set(g.origin) for _,g in d.groupby('model')];self.assertTrue(all(s==sets[0] for s in sets));self.assertEqual(len(sets[0]),393)
 def test_selection_only_validation(self):
  frozen=json.loads((r.O/'FROZEN_SELECTION_2025.json').read_text());self.assertFalse(frozen['selection_uses_2026']);v=pd.read_csv(r.O/'validation_2025_selection.csv');eligible=v[(v.hit1==v.total1)&(v.groups_hit==v.groups)&(~v.model.isin(['BASE14','CFTC21']))]
  expected=eligible.sort_values(['false5','false_episodes','model']).iloc[0].model if len(eligible) else 'PASSTHROUGH';self.assertEqual(frozen['selected'],expected)
 def test_release_ledger(self):
  d=pd.read_csv(r.O/'historical_asof_PROXY_NOT_PIT.csv')
  for c in d:
   if c.endswith('_proxy_available'):self.assertTrue((d[c].dropna()<=d.loc[d[c].notna(),'origin']).all())
 def test_neon_parity(self):self.assertEqual(json.loads((r.O/'neon_parity.json').read_text())['value_differences'],0)
 def test_quarantined_event_not_false_miss(self):
  t=pd.read_csv(r.O/'event_alarm_timeline.csv');self.assertTrue((t.loc[t.eligible_origins_in_event==0,'timing']=='NOT_EVALUABLE_QUARANTINE').all())
if __name__=='__main__':unittest.main(verbosity=2)
