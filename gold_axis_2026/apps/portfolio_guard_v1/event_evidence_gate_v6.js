"use strict";
/* V6 economic event-vintage gate. Original OLAY-02 file is immutable.
 * A confirmed official release time is evidence of chronology, NOT
 * evidence that the release caused a market move.
 */
const fs=require("node:fs"),path=require("node:path"),engine=require("./engine");
const REPO=path.resolve(__dirname,"../../..");
const PANEL={path:"gold_axis_2026/OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv",
 blob:"4b6c8fd84ea291ae22ddc9b0d5d545ce2d8fa527"};
const FED20230201={
 source:"https://www.federalreserve.gov/monetarypolicy/fomcpresconf20230201.htm",
 originalRelease:"2023-02-01T19:00:00.000Z",type:"FOMC_STATEMENT",
 evidence:"Official 2pm EST release time; February 1 2023 = 19:00 UTC"
};
function gate(checkpointUTC,publishedUTC){
 const point=Date.parse(checkpointUTC),first=Date.parse(publishedUTC);
 if(!Number.isFinite(point)||!Number.isFinite(first))throw Error("BAD_EVIDENCE_TIME");
 return {decisionUTC:new Date(point).toISOString(),releaseUTC:new Date(first).toISOString(),
  couldHaveKnownRelease:point>=first,
  verdict:point<first?"BLOCK_EVENT_FUTURE_RELEASE":"TIME_ORDER_POSSIBLE_NOT_CAUSAL_PROOF",
  minutesDifference:(first-point)/60000};
}
function runEvidenceAudit(){
 const source=engine.decodePinnedSource(PANEL,fs.readFileSync(path.join(REPO,PANEL.path)));
 const events=source.rows;
 if(events.length!==96)throw Error("OLAY02_ARCHIVE_COUNT_CHANGED");
 const firstprint=events.filter(e=>e.onset_firstprint_verified==="YES").length;
 const mechanism=events.filter(e=>e.mechanism_caused_proven==="YES").length;
 const allowed=events.filter(e=>e.asof_action_validated==="YES").length;
 const unknown=events.filter(e=>e.org_plot_candidate==="UNMAPPED_OR_NOT_DIRECT_DEEP_V1").length;
 const grade=Object.fromEntries([...new Set(events.map(e=>e.evidence_grade))]
  .map(x=>[x,events.filter(e=>e.evidence_grade===x).length]));
 const example=events.find(x=>x.case_id==="SWING_V1_002");
 if(!example)throw Error("MISSING_FED_CHECKPOINT");
 const t=gate(example.checkpoint_utc,FED20230201.originalRelease);
 if(t.couldHaveKnownRelease)throw Error("FED_VINTAGE_TIMELINE_BROKEN");
 return {version:"V6_EVENT_FIRSTPRINT_ARCHIVE_GATE_20261015",
  archiveGitBlob:PANEL.blob,totalEvents:events.length,
  independentCheckpointIDs:new Set(events.map(e=>e.unique_checkpoint_id)).size,
  firstprintVerified:firstprint,mechanismProven:mechanism,asofActionValidated:allowed,
  unmappedOrWeakOrgCount:unknown,evidenceGrades:grade,
  archiveReadyForCausalTrading:firstprint>0&&mechanism>0&&allowed>0,
  causalEventTradeAuthorization:false,
  officialReleaseExample:{caseId:example.case_id,org:example.org_plot_candidate,
   checkpointUTC:example.checkpoint_utc,official:FED20230201,comparison:t,
   caveat:"This rules out causation by the February 1 2023 FOMC statement for the 06:15 UTC checkpoint. Other earlier catalysts could exist and are NOT thereby ruled out."},
  asofRule:"The event must first exist publicly before it can inform a decision; causation also requires an independent evidence review.",
  originalArchiveMutated:false};
}
module.exports={PANEL,FED20230201,gate,runEvidenceAudit};
