# Gold Control — Project Stage Status: BOCPD Successor V1

**Date:** 2026-09-04  
**Stage status:** `BOCPD_SUCCESSOR_V1_RESEARCH_GATE_PASS_PROSPECTIVE_REQUIRED`  
**Canonical production authority changed:** `NO`  
**Production Neon changed:** `NO`  
**Selector / ensemble / position locks changed:** `NO`

## 1. Why this stage exists

The exact archived `BOCPD` executable could not be fully recovered. The project recovery audit permits a second path: build a clearly new successor under new identity, pre-register its contract, validate it without hindsight and require future prospective evidence before production promotion.

That path has now been executed for:

`BOCPD_RETURN_SUCCESSOR_V1`

The archived identity remains blocked and is not overwritten.

## 2. Completed work

Completed in governance order:

1. project/manifest/recovery constraints re-read;
2. original BOCPD methodological authority reviewed;
3. successor roadmap pre-registered;
4. successor model/change-control frozen before historical validation outputs;
5. frozen JSON contract created;
6. deterministic BOCPD executable implemented;
7. unit/determinism/PIT-prefix tests implemented;
8. engineering historical replay executed in CI;
9. prior Gold Control risk/severity methodology recovered;
10. risk-validation contract frozen before forward-risk metrics were calculated;
11. historical risk diagnostic executed in CI;
12. evidence artifacts audited and frozen.

## 3. Research-gate result

Engineering:

- CI run `33872811566` = SUCCESS;
- CI run `33873106128` = SUCCESS;
- latest research SHA under test: `993ad49abae525a58362dd7d51f551d965cf2156`;
- 14 tests PASS on the combined engineering/risk run;
- 199 frozen monthly replay rows;
- all defined engineering hard gates PASS;
- deterministic hash `59195f0375b43a30f77829b10d33101cc737624a9626b5281f9c637ab046358a`;
- database writes NONE.

Risk diagnostic:

- primary horizon inherited from prior project audit: 2–3M;
- tail definition inherited from prior audit: cumulative forward GOLD return <= -3%;
- validation candidate N=5;
- validation candidate 2M/3M tail rate = 60% / 60%;
- validation non-candidate 2M/3M tail rate = 12.90% / 19.35%;
- candidate mean 3M forward return = -3.55%;
- non-candidate mean 3M forward return = +2.12%;
- interpretation remains `DESCRIPTIVE_ONLY` because sample is small and no production threshold/action was pre-authorized;
- locked replay candidate N=2 and remains `DIAGNOSTIC_ONLY`.

## 4. What is proven versus not proven

### Proven at this stage

- new successor identity is explicit and separate from archived BOCPD;
- implementation is deterministic;
- frozen DEV/VAL/LOCK windows are respected;
- prior uses DEV only;
- future-prefix invariance passes;
- no archived reset-score threshold is reused;
- no same-month hindsight is used;
- no direction vote is introduced;
- no automatic action is introduced;
- no DB write is performed;
- historical risk diagnostic shows descriptive 2–3M downside-risk separation in validation.

### Not proven

- genuine prospective efficacy;
- runtime production suitability;
- automatic action value;
- direction-vote value;
- position mapping;
- `LIVE_PRODUCTION` graduation.

## 5. Runtime and UI consequence now

None.

The current production engine inventory is not silently altered by this research result. In particular:

- archived `BOCPD` remains blocked;
- no production runtime row is overwritten;
- no new direction vote appears;
- no Decision Store authority is created;
- no UI card may relabel this research replay as a live/prospective motor output.

If this successor is surfaced before prospective evidence, it must be explicitly labelled as research/shadow candidate only.

## 6. Next legitimate BOCPD step

Freeze a separate prospective-shadow issuer contract for a future **completed month-close** observation. The issuer must bind:

- governed completed-month monthly GOLD input;
- origin/as-of timestamp;
- immutable input identity/snapshot;
- exact successor code SHA and contract version;
- state output;
- evidence class `PROSPECTIVE_SHADOW`;
- no direction vote;
- no automatic action;
- no selector/ensemble;
- no position mapping.

No historical month may be backdated and called prospective.

The September 2026 month is still open; therefore the first new successor observation capable of becoming genuinely prospective under a completed-month rule is the completed September state after September closes, provided its data/availability gates are satisfied.

## 7. Remaining unresolved-engine roadmap

After this BOCPD research gate, unresolved successor engineering priority remains:

1. `VW_MIDAS_MSVR_SUCCESSOR_V1` — authority/PIT-safe source contract and new executable identity;
2. `MACRO_EVENT_SUCCESSOR_V1` — release-vintage/timestamp/consensus-safe event contract;
3. BOCPD prospective shadow at first legitimate completed-month origin.

This status document does not authorize any of those later steps to bypass their own change-control.
