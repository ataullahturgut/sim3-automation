"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const m=require("./independent_event_learning_s1");
const q=require("./independent_event_research_query_s1");
const day=86400000,iso=t=>new Date(t).toISOString();
const base=Date.parse("2023-01-04T13:30:00Z");
function toy(n=38){
 const rows=[];
 for(let i=0;i<n;i++){
  const t=base+i*14*day,release=iso(t),anchor=iso(t+60*60000);
  const family=i%2===0?"EMP":"CPI";
  const up=i%4<2;
  rows.push({kind:"EVENT",release_utc:release,release_family:family,
    nfp:family==="EMP"?(up?180:-180):null,ahe:family==="EMP"?(up?.2:-.2):null,
    unemp:family==="EMP"?(up?-.2:.2):null,cpi:family==="CPI"?(up?-.4:.4):null,
    anchor_utc:anchor,pre1h:0.1,next4h:up?.8:-.8});
  for(let j=0;j<4;j++)rows.push({kind:"CONTROL",release_utc:release,
    anchor_utc:iso(t+60*60000+(j+2)*day),pre1h:0.1,
    next4h:j%2===0?.2:-.2});
 }
 return rows;
}
test("Independent release must be one label; 4 controls cannot become 4 macro cases",()=>{
 const r=m.run(toy());
 assert.equal(r.candidateReleaseWaves,38);
 assert.equal(r.completeWaves,38);
 assert.equal(r.descriptors.employment.events,19);
 assert.equal(r.descriptors.inflation.events,19);
 assert.ok(r.predictive.all.count>10);
 assert.equal(r.predictive.byYear["2025"].count,0);
 assert.equal(r.technicalSupport.controlsUsedForPrediction,false);
 assert.equal(r.technicalSupport.modelGate,"FAIL");
});
test("Synthetic alternating news-state outcomes learn conditional surprises without manually coded signs",()=>{
 const s=m.run(toy());
 assert.ok(s.predictive.all.brierEconomic<s.predictive.all.brierMarket,
   JSON.stringify(s.predictive.all));
 assert.equal(s.outputAuthority,"DESCRIPTIVE_LEARNED_HYPOTHESIS_ONLY_NO_TRADE");
});
test("Contrary negative controls must stay in same UTC clock and outside ALL economic blackouts",()=>{
 const rows=toy();
 const c=rows.find(x=>x.kind==="CONTROL");
 c.anchor_utc=rows.find(x=>x.kind==="EVENT").anchor_utc;
 assert.throws(()=>m.run(rows),/EVENT_CONTAMINATED_NEGATIVE_CONTROL/);
 const rows2=toy();
 rows2.find(x=>x.kind==="CONTROL").anchor_utc="2023-01-06T12:00:00Z";
 assert.throws(()=>m.run(rows2),/CLOCK_UNMATCHED_CONTROL/);
});
test("Archive economic learning cannot be elevated to LIVE or STRICT by changing a flag",()=>{
 assert.throws(()=>m.run(toy(),{mode:"STRICT_WALK_FORWARD"}),/CANNOT_PASS_STRICT_GATE/);
 assert.throws(()=>m.run(toy(),{proof:"VERIFIED_PIT"}),/CANNOT_PASS_STRICT_GATE/);
});
test("Missing continuous market outcome is excluded; economic label is never invented",()=>{
 const rows=toy();
 const e=rows.find(x=>x.kind==="EVENT");
 e.anchor_utc=null;e.pre1h=null;e.next4h=null;
 const r=m.run(rows);
 assert.equal(r.rejectedIncompleteWaves,1);
 assert.equal(r.completeWaves,37);
});
test("Future release actual is not a model input before the publication anchor",()=>{
 const rows=toy();
 rows.find(x=>x.kind==="EVENT").anchor_utc="2023-01-04T14:00:00Z";
 assert.throws(()=>m.run(rows),/ANCHOR_PRE_AVAILABILITY/);
});
test("Duplicate event components never count as independent sample",()=>{
 const rows=toy();
 rows.push({...rows[0]});
 assert.throws(()=>m.run(rows),/DUPLICATED_RELEASE_CLUSTER/);
});
test("SQL builder only uses retrospective pair-complete releases and matches controls on prior market move",()=>{
 const hdr="event_type,event_ts_utc,actual,consensus,surprise,actual_available_as_of_utc,consensus_available_as_of_utc,surprise_ready_at_utc,pair_complete,actual_lineage_id,consensus_lineage_id,pit_use";
 const lines=[];
 for(let i=0;i<22;i++){
  const t=iso(base+i*14*day);
  lines.push("CPI,"+t+",0.3,0.2,0.1,"+t+","+t+","+t+",True,actual"+i+",forecast"+i+",POST_RELEASE_ONLY");
 }
 const s=q.buildSql([hdr,...lines].join("\n"));
 assert.match(s,/ORDER BY abs\(x.pre1h-e.pre1h\)/);
 assert.match(s,/lead\(close_price,16\)/);
 assert.match(s,/NOT EXISTS/);
 assert.ok(!s.includes("ORDER BY abs(x.next4h"));
});
