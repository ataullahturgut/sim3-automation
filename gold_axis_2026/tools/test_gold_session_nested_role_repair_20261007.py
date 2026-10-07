"""Regression: future selector evidence cannot change an earlier outer block."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
import numpy as np
import pandas as pd

spec=importlib.util.spec_from_file_location('repair',Path(__file__).with_name('gold_session_nested_role_repair_20261007.py'))
repair=importlib.util.module_from_spec(spec);spec.loader.exec_module(repair)

class ChronologyTest(unittest.TestCase):
    def run_policy(self,future_marker):
        origins=pd.to_datetime(['2022-12-28','2022-12-29','2023-01-03','2023-01-04','2024-01-03','2025-01-03'],utc=True)
        panel=pd.DataFrame(dict(partition='TEST',window='ASIA',start_utc=origins,end_utc=origins+pd.Timedelta(hours=2),year=origins.year,y_up=[0,1,0,1,0,1],p_A1_arcr=.5,marker=[0,0,0,future_marker,future_marker,future_marker]))
        def choose(tr):
            # A future-influenced selector would switch representations.
            path='future_path' if tr.marker.max()>0 else 'past_path'
            return [path,'sage'],1,{},None
        def fit(tr,te,features):return np.full(len(te),.9 if 'future_path' in features else .1)
        module=SimpleNamespace(BLOCK=1,MIN_TRAIN=2,PATH=['past_path','future_path'],SAGE=['sage'],build_panel=lambda:panel.copy(),choose_features=choose,choose_sage=choose,fit_l2=fit,fit_selected=fit)
        oldload,oldax=repair.load,repair.AX
        try:
            with tempfile.TemporaryDirectory() as td:
                repair.AX=Path(td);repair.load=lambda *args:module
                with contextlib.redirect_stdout(io.StringIO()):repair.main()
                out=pd.read_csv(Path(td)/'GOLD_SESSION_NESTED_ROLE_REPAIR_PREDICTIONS_2026-10-07.csv')
                timing=pd.read_csv(Path(td)/'GOLD_SESSION_NESTED_ROLE_REPAIR_TIMING_2026-10-07.csv')
                return out,timing
        finally:repair.load,repair.AX=oldload,oldax
    def test_future_changes_leave_earlier_selected_predictions_unchanged(self):
        before,_=self.run_policy(0);after,_=self.run_policy(99)
        first=before.start_utc.min()
        pd.testing.assert_frame_equal(before[before.start_utc==first].reset_index(drop=True),after[after.start_utc==first].reset_index(drop=True))
        # The counterfactual really affects later selections, avoiding a vacuous test.
        self.assertFalse(before.p_up.equals(after.p_up))
    def test_future_transport_rows_are_excluded_and_labels_are_mature(self):
        out,timing=self.run_policy(99)
        self.assertEqual(set(out.year),{2023,2024})
        self.assertTrue((pd.to_datetime(timing.max_train_end,utc=True)<=pd.to_datetime(timing.cutoff,utc=True)).all())
        self.assertTrue((pd.to_datetime(timing.max_train_start,utc=True)<pd.to_datetime(timing.cutoff,utc=True)).all())

if __name__=='__main__':unittest.main()
