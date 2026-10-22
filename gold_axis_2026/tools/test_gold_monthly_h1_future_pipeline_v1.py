"""Offline contract test: should require no new future GPR or market data."""
import copy,datetime,hashlib,json,tempfile
from pathlib import Path
from unittest import TestCase,main
import gold_monthly_h1_origin_public_bundle_v1 as source
import gold_monthly_h1_publish_neon_v1 as out
import gold_monthly_h1_forward_monthly_v1 as pred

class FutureGoldContract(TestCase):
    def test_next_target_origin(self):
        origin,last,cut=source.month_origin("2026-11")
        self.assertEqual(origin,"2026-10")
        self.assertEqual(last.isoformat(),"2026-10-31")
        self.assertEqual(cut.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M"),"2026-10-31T21:00")
        self.assertEqual(source.last_weekday_of_month(last).isoformat(),"2026-10-30")
        with self.assertRaisesRegex(RuntimeError,"NO_RETROACTIVE"):
            source.month_origin("2026-10")

    def inputs(self):
        cutoff="2026-10-31T21:00:00+00:00"
        comm={"committedAtUtc":"2026-10-31T20:00:00+00:00","sha":"a"*40}
        b={"schema":"GOLD_MONTHLY_H1_ORIGIN_PUBLIC_BUNDLE_V1",
           "target":"2026-11","origin":"2026-10","origin_cutoff_utc":cutoff,
           "daily_extension_rows":[{"date":"2025-01-02","Gold":1} for _ in range(260)],
           "gpr_meta":{"2026-10":{"source_xls_sha256":"1"*64}},
           "source_commits":{"stak":comm,"stak_api":comm,"gpr":comm}}
        b["payload_sha256"]=out.canonical_sha(b)
        f={"schema":"GOLD_MONTHLY_H1_FROZEN_FORWARD_V1","target":"2026-11","origin":"2026-10",
           "target_actual":None,"source_bundle_sha256":b["payload_sha256"],
           "model":"CHHHO","reference_authority":"STAKTRAKR_PROVISIONAL",
           "official_gpr_xls_sha256":"1"*64,
           "source_data_first_provenance":{"origin_daily_commit_by_cutoff":True,"target_month_actual_used":False},
           "forecast":4278.3,"origin_reference":4300.0,"train_rows":199,
           "input_feature_vector":{"values":[1.0]*8},"input_feature_sha256":out.canonical_sha({"values":[1.0]*8})}
        q={**f,"model":"DE_ABC","forecast":4255.7}
        return b,f,q

    def test_pair_and_source_hash_frozen(self):
        b,f,q=self.inputs()
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/p for p in ("bundle.json","a.json","b.json")]
            for p,x in zip(paths,(b,f,q)):p.write_text(json.dumps(x))
            a,models=out.certify(paths[0],paths[1:])
            self.assertEqual(len(models),2)
            f["target_actual"]=4310
            paths[1].write_text(json.dumps(f))
            with self.assertRaisesRegex(RuntimeError,"LOOKAHEAD"):
                out.certify(paths[0],paths[1:])

    def test_changing_sibling_input_is_blocked(self):
        b,f,q=self.inputs()
        q["input_feature_sha256"]="e"*64
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/p for p in ("bundle.json","a.json","b.json")]
            for p,x in zip(paths,(b,f,q)):p.write_text(json.dumps(x))
            with self.assertRaisesRegex(RuntimeError,"FEATURE_VECTOR_SHA_CHANGED"):
                out.certify(paths[0],paths[1:])
        self.assertNotEqual(out.canonical_sha(f),out.canonical_sha(q))

    def test_no_plaintext_neon_secret_in_code(self):
        root=Path(__file__).parent
        for f in ("gold_monthly_h1_origin_public_bundle_v1.py",
                  "gold_monthly_h1_forward_monthly_v1.py",
                  "gold_monthly_h1_publish_neon_v1.py"):
            content=(root/f).read_text()
            self.assertNotIn("postgresql://",content)
            self.assertNotIn("PRODUCTION_DB_PASSWORD",content)

if __name__=="__main__":main()
