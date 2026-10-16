"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const {replay}=require("./replay_position_value_s3");
test("Real replay contract uses no future prices or writes and returns only aggregate shadow values",()=>{
 const bars=Array.from({length:60},(_,i)=>{
  const bar_start_utc=new Date(Date.parse("2023-01-03T10:00:00Z")+900000*i).toISOString();
  return {bar_start_utc,source_id:"SYNTHETIC_1",bid_close:1799+i,ask_close:1801+i};
 });
 const q=replay({bars});
 assert.equal(q.barCount,60);
 assert.equal(q.researchOnly,true);
 assert.equal(q.positionResearch.liveTradeAuthorized,false);
 assert.equal(q.positionResearch.portfolio.passiveCashNetUsd,100);
 assert.equal(JSON.stringify(q).includes("1801"),false);
 assert.equal(q.s2.fastObservations,60);
});
test("Prices cannot be silently fabricated from inverted or negative quote",()=>{
 const bad={bars:[{bar_start_utc:"2023-01-03T10:00:00Z",
  source_id:"SYNTHETIC_1",bid_close:1900,ask_close:1800}]};
 assert.throws(()=>replay(bad),/INVALID_BIDASK_PRICE/);
});
