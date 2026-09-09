# Gold Control V1.45 — NY17 Exact Reconstruction Checkpoint

**Status:** `PASS`  
**Previous canonical HEAD:** `0a938d0628cee6c9e0ca948eb2e6d048a89ff574`  
**Production database writes:** `NONE`

The frozen NY17 source contract was preserved without substitution, interpolation, forward-fill or synthetic bars. The immutable workflow artifact contains all 684 required-date adjudications:

- `VALID_EXACT_BAR = 442`
- `PROVIDER_NO_BAR = 242`
- `UNRESOLVED = 0`

The only attempt-2 transport failure, `2025-05-13`, was retried under the unchanged Twelve Data `XAU/USD`, `1min`, `America/New_York`, exact `16:59:00` contract. It resolved as `VALID_EXACT_BAR`; retrieval time and payload hash are preserved.

Artifact identity:

- workflow run: `34348854514`
- artifact ID: `10102818986`
- artifact digest: `sha256:b5de36b77cd24626e2c264510dac57adcb9483b36ff444c9861100b913ceb7d6`
- JSON SHA-256: `b4b66535617ec074d84ca9a7c157f22f509d9d7c35dc6e1f42b9937b4681ddf4`
- CSV SHA-256: `94db339eb5d34b7df35a4342082710fc4900f9ac141168138c82ec3db66434b9`

The frozen artifact-lane contract explicitly authorizes zero production writes for this pilot. Production `XAU_EOD_TWELVE_NY17` therefore remains the live/current lane and was not backfilled. Postcheck row count is 52 and all four authority stores remain zero.

Machine-readable evidence: `data_pipeline/audits/historical_ny17_exact_date_probe_v145_final_evidence.json`.
