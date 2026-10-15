"use strict";
const t=require("node:test"),assert=require("node:assert/strict");
const e=require("./event_evidence_gate_v6"),m=require("./macro_v6");
t("original 96-event archive remains intact and all unverified causal firstprint flags block trading",()=>{
 const r=e.runEvidenceAudit();
 assert.equal(r.totalEvents,96);
 assert.equal(r.independentCheckpointIDs,84);
 assert.equal(r.firstprintVerified,0);
 assert.equal(r.mechanismProven,0);
 assert.equal(r.asofActionValidated,0);
 assert.equal(r.unmappedOrWeakOrgCount,78);
 assert.equal(r.causalEventTradeAuthorization,false);
 assert.equal(r.archiveReadyForCausalTrading,false);
 assert.equal(r.originalArchiveMutated,false);
 assert.equal(Object.values(r.evidenceGrades).reduce((a,b)=>a+b,0),96);
});
t("the FOMC official 2pm EST first release was AFTER the 06:15 UTC Feb1 2023 checkpoint",()=>{
 const r=e.runEvidenceAudit().officialReleaseExample;
 assert.equal(r.caseId,"SWING_V1_002");
 assert.equal(r.checkpointUTC,"2023-02-01T06:15Z");
 assert.equal(r.official.originalRelease,"2023-02-01T19:00:00.000Z");
 assert.equal(r.comparison.minutesDifference,765);
 assert.equal(r.comparison.couldHaveKnownRelease,false);
 assert.equal(r.comparison.verdict,"BLOCK_EVENT_FUTURE_RELEASE");
 assert.equal(e.gate("2023-02-01T20:00:00Z","2023-02-01T19:00:00Z").couldHaveKnownRelease,true);
});
t("V6 risk classifier cannot mutate or override negative event-vintage evidence",()=>{
 const r=m.runAudit();
 assert.equal(r.archiveEvidence.firstprintVerified,0);
 assert.equal(r.archiveEvidence.mechanismProven,0);
 assert.equal(r.acceptance.tradeAuthorized,false);
 assert.equal(r.acceptance.economicMechanismVerified,false);
});
