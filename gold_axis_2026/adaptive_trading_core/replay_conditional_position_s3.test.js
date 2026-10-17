"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),
 replay=require("./replay_conditional_position_s3");
const t0=Date.parse("2023-01-05T12:00:00Z");
const bars=Array.from({length:45},(_,i)=>({
 source_id:"TEST",bar_start_utc:new Date(t0+i*900000).toISOString(),
 bid_close:1899+i*.15,ask_close:1900+i*.15}));
test("economic-on/off same CORE and same prices have exactly zero uplift when no event",()=>{
 const x=replay.run(bars,[],{economicSources:{},checkpoints:[]});
 assert.equal(x.admittedEconomicCheckpoints,0);
 assert.equal(x.incrementalEconomicWealthUsd,0);
 assert.equal(x.models.ECONOMIC_ON.economicAnchors,0);
 assert.equal(x.models.MARKET_ONLY.economicAnchors,0);
 assert.equal(x.scienceGate,"NOT_PROVEN");
});
test("future economic observation cannot influence a historical S1-S3 decision",()=>{
 const i=25,at=new Date(t0+(i+1)*900000).toISOString();
 const bundle={economicSources:{EVENT_TEST:{kind:"EVENT",evidenceStatus:"VERIFIED_PIT"}},
   checkpoints:[{asof:at,features:{cpi_surprise_z:{value:1,kind:"EVENT",
     source:"EVENT_TEST",observedAt:new Date(Date.parse(at)+900000).toISOString(),
     availableAt:new Date(Date.parse(at)+900000).toISOString(),
     firstPublishedAt:new Date(Date.parse(at)+900000).toISOString(),
     firstprintVerified:true}}}]};
 assert.throws(()=>replay.run(bars,[],bundle),/FUTURE_OR_REVERSED_FEATURE|FUTURE_EVENT_FIRSTPRINT/);
});
test("invalid source and duplicated events fail rather than manufacture evidence",()=>{
 const e={asof:"2023-01-05T12:15:00Z",features:{}};
 assert.throws(()=>replay.run(bars,[],{economicSources:{},checkpoints:[e,e]}),
  /DUPLICATE_EVENT_CHECKPOINT/);
 assert.throws(()=>replay.run([...bars.slice(0,4),bars[3]],[],{economicSources:{},checkpoints:[]}),
  /NONMONOTONIC/);
});
