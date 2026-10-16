"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const {replayArchive}=require("./replay_slow_position_memory_s3");
const source="SYNTHETIC_ONLY_ONE_SOURCE";
function rec(day,i){
 const prev=new Date(Date.parse(day+"T22:00:00Z")-86400000).toISOString();
 const end=new Date(Date.parse(day+"T22:00:00Z")-900000).toISOString();
 return {session:day,source_id:source,sessionEvidence:"BIDASK_M15_RECONSTRUCTED_NOT_M1",
  close_price:1800*Math.pow(1.002,i),first_bar:prev,
  last_bar:end,n:92,valid_quotes:92,terminal_bar_valid:true,
  max_gap_minutes:15};
}
test("One CORE's completed sessions mature S3 long net labels, research only",()=>{
 const days=["2023-01-02","2023-01-03","2023-01-04",
  "2023-01-05","2023-01-06","2023-01-09",
  "2023-01-10","2023-01-11","2023-01-12","2023-01-13",
  "2023-01-16","2023-01-17"];
 const out=replayArchive(days.map(rec));
 assert.equal(out.qualifiedSessions,12);
 assert.ok(out.memory.audit.maturedLabels>0);
 assert.ok(out.memory.audit.acceptedSessions===12);
 assert.equal(out.liveTradeAuthorized,false);
 assert.equal(out.bankFeesPerLeg,.008);
 assert.equal(out.certifiedPIT,false);
 assert.ok(out.memory.learnedCohorts);
});
test("Archive does not splice quote sources; time order must be monotonic",()=>{
 assert.throws(()=>replayArchive([]),/ROWS_REQUIRED/);
 assert.throws(()=>replayArchive([rec("2023-01-02",0),
  {...rec("2023-01-03",1),source_id:"DIFFERENT"}]),/ONE_UNSPLICED_SOURCE/);
 assert.throws(()=>replayArchive([rec("2023-01-03",1),
  rec("2023-01-02",0)]),/NONMONOTONIC_SESSION/);
});
