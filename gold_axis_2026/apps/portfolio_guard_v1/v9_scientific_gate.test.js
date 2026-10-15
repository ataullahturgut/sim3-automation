"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const vm=require("node:vm"),fs=require("node:fs"),path=require("node:path");
const {loadFullRows}=require("./v8_regret_engine");
const {replay:episode}=require("./v9_episode_guard");
const {replay:naive}=require("./v9_state_transition");
const {simulate:meta}=require("./v9_shadow_selector");
const {report,VERSION}=require("./v9_research_audit");
const data=loadFullRows(),rows=data.rows;
const nearly=(a,b,tolerance=.000025)=>assert.ok(Math.abs(a-b)<tolerance,String(a)+" vs "+String(b));

test("2023-26 pinned source, independent 2025 overlap checks",()=>{
 assert.equal(rows.length,6724);
 assert.equal(data.data.overlapVerified,1892);
 assert.equal(rows[0].tt,"2023-01-03T06:00:00.000Z");
 assert.equal(rows.at(-1).tt,"2026-09-30T21:00:00.000Z");
});

test("V9 online naive mixture loses to cash after commission, never promotes",()=>{
 const a=report();
 assert.equal(a.version,VERSION);
 assert.equal(a.status,"REJECT_V9_PROMOTION_SAVE_LEARNING_EXPERIMENTS");
 assert.equal(a.gate.promote,false);
 assert.equal(a.gate.canTradeLive,false);
 assert.equal(a.method.futureMonthOracleUsedAsSignal,false);
 assert.equal(a.method.economicFirstprintsVerified,0);
 assert.equal(a.method.prospectiveBlindPeriod,false);
 assert.equal(a.coverage.sourceRows,6724);
 assert.equal(a.pre2026PassBothPassive.count,0);
 assert.ok(a.comparisons.V7_2026>a.comparisons.V8_2026);
});

test("2024 hysteresis success does not generalize to 2025/26",()=>{
 const a=report();
 const get=(name,year)=>a.episodeCandidates.find(x=>x.variant===name&&x.year===year).final;
 nearly(get("BASE","2024"),125.12907032005278);
 nearly(get("SLOW_EXIT","2025"),148.03111496963868);
 nearly(get("POSTERIOR","2026"),119.753917);
 assert.ok(get("BASE","2024")>123.84971030121015);
 assert.ok(get("SLOW_EXIT","2025")<160.4152649234894);
 assert.ok(get("BASE","2026")<119.753917);
});

test("overtrading costs sharply reduce naive ensemble value",()=>{
 const a=report(),get=(year,mode)=>a.naiveMixture.find(x=>x.year===year&&x.policy===mode);
 assert.ok(get("2024","ensemble").finalUSD<100);
 assert.ok(get("2025","ensemble").finalUSD<100);
 assert.ok(get("2026_FebSep","ensemble").finalUSD<119.753917);
 assert.ok(get("2025","ensemble").trades>10);
 assert.ok(get("2024","ensemble").trades>10);
});

test("meta expert ranking uses realized net paper returns and future checkpoint fills",()=>{
 const a=report(),get=(name,year)=>a.shadowCandidates.find(x=>x.variant===name&&x.year===year);
 assert.ok(get("VOTE_42D","2026").final<119.753917);
 assert.ok(get("VOTE_42D","2025").final>100);
 assert.ok(get("VOTE_42D","2024").final>100);
 assert.equal(a.execution.nextCheckpointFill,true);
 assert.equal(a.execution.sameCheckpointSignalFill,false);
 assert.equal(a.execution.bankBidAsk,false);
});

test("no hindsight fills: each shadow trade follows, not precedes, signal",()=>{
 const x=meta(rows,{start:"2026-02-02T06:00:00Z",
  end:"2026-03-31T12:00:00Z",initial:119.753917,window:126,mode:"vote",band:.6});
 for(const t of x.trades){
  assert.ok(Date.parse(t.utc)>Date.parse(t.asOf));
  assert.ok([6,9,12].includes(new Date(t.utc).getUTCHours()));
 }
 assert.equal(x.asOfLag,true);
 assert.equal(x.realBankBidAsk,false);
});

test("non-overlapping 336-hour opportunity labels mature before any learning",()=>{
 const a=episode(rows,{start:"2024-01-02T06:00:00Z",end:"2025-12-31T12:00:00Z",
   initial:100,includeLabels:true});
 for(let i=0;i<a.learnedLabels.length;i++){
  const label=a.learnedLabels[i];
  assert.ok(Date.parse(label.labelKnown)>=Date.parse(label.origin)+336*3600000);
  if(i)assert.ok(Date.parse(label.origin)-Date.parse(a.learnedLabels[i-1].origin)>=336*3600000);
 }
 assert.ok(a.learnedLabels.length>20);
 assert.equal(a.automaticPromotion,false);
});

test("96-hour/336-hour online posterior discounts overlapping daily anchors",()=>{
 const x=naive(rows,{start:"2025-01-07T06:00:00Z",end:"2025-12-31T12:00:00Z",initial:100});
 for(const key of Object.keys(x.labelsByRegime)){
  const h=x.labelsByRegime[key];
  nearly(h.h336.nEffective,h.h336.nRaw/14,.0000001);
  nearly(h.h96.nEffective,h.h96.nRaw/4,.0000001);
  assert.ok(h.h336.winProbability>=0&&h.h336.winProbability<=1);
 }
 assert.equal(x.execution.signalOneCheckpointBeforeFill,true);
});

test("altering future source rows cannot change earlier executed trades",()=>{
 const args={start:"2026-02-02T06:00:00Z",end:"2026-05-29T12:00:00Z",initial:119.753917};
 const original=meta(rows,args);
 const changed=rows.map(r=>r.tt>"2026-05-29T12:00:00.000Z"?
  {...r,p:r.p*1.8,c:r.c*1.8,r1:300,r3:300}:r);
 const result=meta(changed,args);
 assert.deepEqual(original.trades,result.trades);
 nearly(original.final,result.final);
});

test("V9 read-only HTTP contract, legacy health and UI JavaScript parse",()=>{
 const {requestHandler}=require("./server");
 const respond=(method,url)=>{
  let status,body;
  requestHandler({method,url},{writeHead(x){status=x},end(x){body=x}});
  return {status,body:body?JSON.parse(body):null};
 };
 const x=respond("GET","/api/algorithm/v9/scientific");
 assert.equal(x.status,200);
 assert.equal(x.body.version,VERSION);
 assert.equal(x.body.gate.promote,false);
 assert.equal(x.body.gate.canTradeLive,false);
 assert.equal(respond("POST","/api/algorithm/v9/scientific").status,405);
 assert.equal(respond("GET","/api/health").status,200);
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 assert.match(html,/id="runV9Scientific"/);
 const js=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 assert.doesNotThrow(()=>new vm.Script(js));
});
