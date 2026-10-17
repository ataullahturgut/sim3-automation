"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),
 m=require("./adaptive_conditional_position_s3");
const sid="SYN",ev={provenance:"RESEARCH_MACRO_UNVERIFIED",
 economicState:{family:"EMP",dominant:"nfp_surprise_z",sign:"POS",magnitude:1.5}};
const obs=(s,at,price=1900,e=ev,holding="CASH")=>m.observe(s,{at,price,sourceId:sid,
 fast:{phase:"START",direction:1},s1Evidence:e,holding});
const day=(s,d,price=1900)=>m.completedSession(s,{session:d,price,sourceId:sid,
 availableAt:d+"T22:00:00Z"});
test("no future label and separate market/economy cohorts",()=>{
 const s=m.create();let x=obs(s,"2023-01-06T17:00:00Z");
 assert.equal(x.actionCandidate,"KEEP");
 assert.equal(x.conditionKey,"MKT:START:UP|ECO:EMP:nfp_surprise_z:POS");
 day(s,"2023-01-06",1900);
 for(const d of ["2023-01-09","2023-01-10","2023-01-11","2023-01-12"])day(s,d,1910);
 assert.equal(m.summary(s).audit.labelsMatured,0);
 day(s,"2023-01-13",1970);
 assert.equal(m.summary(s).audit.labelsMatured,1);
 assert.equal(s.cohorts["MKT:START:UP|BUY#5"].n,1);
 assert.equal(s.cohorts["MKT:START:UP|ECO:EMP:nfp_surprise_z:POS|SELL#5"].n,1);
 assert.equal(m.score(s,{phase:"START",direction:1},ev,"CASH").actionCandidate,"KEEP");
});
test("economic not invented from invalid or market-only provenance",()=>{
 const s=m.create();obs(s,"2023-01-06T17:00:00Z",1900,
  {provenance:"MARKET_ONLY_UNVALIDATED",economicState:ev.economicState});
 assert.equal(s.audit.economicAnchors,0);
 assert.throws(()=>obs(s,"2023-01-06T17:15:00Z",1900,
  {provenance:ev.provenance,economicState:{family:"NFP",dominant:"nfp",sign:"LONG",magnitude:12}}),
  /CP_INVALID_ECONOMIC_STATE/);
});
test("learned economic advantage only with sufficient independent support",()=>{
 const s=m.create(),id="MKT:START:UP|ECO:EMP:nfp_surprise_z:POS|BUY#5";
 s.cohorts["MKT:START:UP|BUY#5"]={n:50,mean:-1,m2:50,independentN:10,
  independentMean:-1,independentM2:9,lastOriginIndex:0,lastMaturedAt:"2022-12-30"};
 s.cohorts[id]={n:50,mean:4,m2:15,independentN:10,independentMean:4,
  independentM2:9,lastOriginIndex:0,lastMaturedAt:"2022-12-30"};
 let x=m.score(s,{phase:"START",direction:1},ev,"CASH");
 assert.equal(x.actionCandidate,"BUY");
 assert.equal(x.best.source,"CONDITIONAL_ECONOMIC");
 s.cohorts[id].independentN=7;
 x=m.score(s,{phase:"START",direction:1},ev,"CASH");
 assert.equal(x.actionCandidate,"KEEP");
});
test("market fallback never credited to economic context",()=>{
 const s=m.create(),id="MKT:START:UP|SELL#5";
 s.cohorts[id]={n:25,mean:2.5,m2:3,independentN:8,independentMean:2.5,
  independentM2:4,lastOriginIndex:0,lastMaturedAt:"2022-12-30"};
 const x=m.score(s,{phase:"START",direction:1},ev,"GOLD");
 assert.equal(x.actionCandidate,"SELL");
 assert.equal(x.best.source,"MARKET_FALLBACK");
});
test("source transition censors rather than creates fake outcome",()=>{
 const s=m.create();obs(s,"2023-01-06T17:00:00Z");day(s,"2023-01-06");
 m.completedSession(s,{session:"2023-01-12",price:2000,sourceId:sid,
  availableAt:"2023-01-12T22:00:00Z"});
 assert.equal(s.audit.censored,3);assert.equal(s.audit.labelsMatured,0);
});
test("research non-execution, checkpoint restore and no event carry on market-only bar",()=>{
 const s=m.create();const x=obs(s,"2023-01-06T17:00:00Z");
 assert.equal(x.tradeAllowed,false);assert.equal(x.action,null);
 assert.equal(m.restore(m.checkpoint(s)).pending.length,3);
 const y=obs(s,"2023-01-06T17:15:00Z",1901,null);
 assert.equal(y.eventPresent,false);assert.equal(y.actionCandidate,"KEEP");
});

test("existing S3 CORE queues conditional research BUY and only fills next completed M15",()=>{
 const critic=require("./adaptive_position_value_s3");
 const reg={[sid]:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"}};
 const s=critic.create({sourceRegistry:reg,shadowEnabled:true,
  positionResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH"});
 const id="MKT:START:UP|ECO:EMP:nfp_surprise_z:POS|BUY#5";
 s.conditional.cohorts["MKT:START:UP|BUY#5"]={n:50,mean:-1,m2:50,
  independentN:10,independentMean:-1,independentM2:9,
  lastOriginIndex:0,lastMaturedAt:"2022-12-30"};
 s.conditional.cohorts[id]={n:50,mean:4,m2:15,independentN:10,
  independentMean:4,independentM2:9,lastOriginIndex:0,lastMaturedAt:"2022-12-30"};
 const mark=(time,price,phase,eco)=>critic.observe(s,{
  asof:time,priceAvailableAt:time,barMinutes:15,price,sourceId:sid,
  fast:{phase,direction:phase==="NEUTRAL"?0:1},slow:null,
  s1Evidence:{asof:time,provenance:eco?"RESEARCH_MACRO_UNVERIFIED":
   "MARKET_ONLY_UNVALIDATED",economicState:eco?ev.economicState:null,byHorizon:[]}});
 mark("2023-01-06T16:45:00Z",1860,"NEUTRAL",false);
 const signal=mark("2023-01-06T17:00:00Z",1863,"START",true);
 assert.equal(signal.proposedResearchAction,"BUY");
 assert.equal(signal.conditionalResearch.best.source,"CONDITIONAL_ECONOMIC");
 assert.equal(signal.tradeAllowed,false);
 assert.equal(s.paper.buyCount,0);
 mark("2023-01-06T17:15:00Z",1864,"CONTINUE",false);
 assert.equal(s.paper.buyCount,1);
 assert.equal(s.paper.holding,"GOLD");
 assert.equal(critic.summary(s).liveTradeAuthorized,false);
});
