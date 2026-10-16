"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const e=require("./economic_evidence_s1");
const csv=[
"event_type,event_ts_utc,actual,consensus,surprise,actual_available_as_of_utc,consensus_available_as_of_utc,surprise_ready_at_utc,pair_complete,actual_lineage_id,consensus_lineage_id,pit_use",
"NFP,2023-01-06T13:30:00Z,223,200,23,2023-01-06T13:30:00Z,2023-01-06T13:30:00Z,2023-01-06T13:30:00Z,True,publication_after_fact_v1,old_consensus_v1,POST_RELEASE_ONLY",
"AHE,2023-01-06T13:30:00Z,0.3,0.4,-0.1,2023-01-06T13:30:00Z,2023-01-06T13:30:00Z,2023-01-06T13:30:00Z,True,publication_after_fact_v1,old_consensus_v1,POST_RELEASE_ONLY"
].join("\n");
const rcs=e.readReleaseClusters(csv,"2023-01-01T00:00:00Z","2023-02-01T00:00:00Z");
const mk=(iso,p=100,v=.1)=>({end_utc:iso,close_price:p,gold_1h_pct:v,nq_1h_pct:.02,zn_1h_pct:.01,cl_1h_pct:-.02});
test("CSV parser accepts quotes but not misaligned evidence rows",()=>{
 assert.equal(e.csv('a,b\n"one,two","said ""ok"""\n')[0].a,"one,two");
 assert.equal(e.csv('a,b\n"one,two","said ""ok"""\n')[0].b,'said "ok"');
 assert.throws(()=>e.csv("a,b\none\n"),/COLUMN_COUNT/);
});
test("One release time has multiple contrary economic surprise records but zero PIT certification",()=>{
 assert.equal(rcs.length,1);
 assert.equal(rcs[0].records.length,2);
 assert.equal(rcs[0].featureAdmissible,false);
 assert.equal(rcs[0].firstprintVerified,false);
 assert.equal(rcs[0].records[0].scoreSignInterpretation,"NOT_ASSIGNED_NO_MANUAL_DIRECTION_RULE");
});
test("No surprise may be available before the announcement",()=>{
 const corrupted=csv.replaceAll("2023-01-06T13:30:00Z,True","2023-01-06T13:25:00Z,True");
 assert.throws(()=>e.readReleaseClusters(corrupted,"2023-01-01T00:00:00Z","2023-02-01T00:00:00Z"),/PRE_RELEASE/);
});
test("Same-clock pre-outcome comparator has opposite evidence and no feature leakage",()=>{
 const rows=[
 mk("2023-01-04T16:00:00Z",100),mk("2023-01-04T20:00:00Z",101),
 mk("2023-01-06T16:00:00Z",104),mk("2023-01-06T20:00:00Z",103),
 mk("2023-01-10T16:00:00Z",98),mk("2023-01-10T20:00:00Z",100),
 mk("2023-01-16T16:00:00Z",97),mk("2023-01-16T20:00:00Z",96)
 ];
 const v=e.pairControls(rows,rcs);
 assert.equal(v.events.length,1);
 assert.equal(v.events[0].releaseTimes.length,1);
 assert.ok(v.events[0].observedNext4hLogPct<0);
 assert.ok(v.events[0].matchedControls.some(q=>q.next4hLogPct>0));
 assert.ok(v.events[0].matchedControls.some(q=>q.next4hLogPct<0));
 assert.equal(v.eventFeaturesFedIntoCore,0);
 assert.ok(v.sameClockControl4h.up+v.sameClockControl4h.nonUp>=2);
 assert.equal(v.outcomesUsedToFormMatch,false);
 assert.equal(v.events[0].causalStatus,"UNVERIFIED_MATCHED_OBSERVATIONAL_EVIDENCE");
});
test("A case archive is research context only and never feeds hindsight labels as alpha",()=>{
 const q="# ÖĞREN-03\n"+["G01","G02","G03","G04","G05","G06","G07"].map(s=>"### "+s+" —\n").join("")+
 [...Array(12)].map((_,i)=>"### ORG"+String(i+1).padStart(2,"0")+" — \n").join("");
 const d="case_id,primary_plot_candidate_id,secondary_plot_candidate_id,source_support_grade,firstprint_utc\nSWING_V1_001,ORG01,ORG09,HYPOTHESIS,UNKNOWN\n";
 const a=e.readArchive("# OLAY-02\n",q,d);
 assert.equal(a.caseCount,1);
 assert.equal(a.pitCertifiedCases,0);
 assert.equal(a.cases[0].permissibleAsTradingInput,false);
 assert.equal(a.cases[0].candidateOrg,"ORG01");
});
