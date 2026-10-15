"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const {loadRows,runResearch,VERSION,DATA_BLOB_SHA}=require("./adaptive_v7_app");
const {replayV6}=require("./adaptive_v7_engine");

function almost(a,b){assert.ok(Math.abs(a-b)<0.00002, String(a)+" != "+String(b));}

test("Pinned V7 3h 2025-2026 as-of source is unchanged",()=>{
 const data=loadRows();
 assert.equal(data.length,3511);
 assert.equal(data[0].tt,"2025-01-07T00:00:00.000Z");
 assert.equal(data.at(-1).tt,"2026-09-30T21:00:00.000Z");
 assert.equal(DATA_BLOB_SHA,"db9a2777b5daf0bc4dab64157a176f71a30a9df5");
});
test("Actual V7 + ablation + older 2025 negative control are reproducible",()=>{
 const r=runResearch();
 assert.equal(r.version,VERSION);
 assert.equal(r.status,"EX_POST_RESEARCH_NOT_BLIND");
 almost(r.primary.finalUSD,123.52954535978293);
 almost(r.ablations.learningFrozenUSD,105.18177145259395);
 almost(r.ablations.stressRuleDisabledUSD,108.44434219692778);
 almost(r.ablations.priceOnlyWithStressUSD,123.52954535978293);
 almost(r.negativeControls.year2025.finalUSD,104.27573426448016);
 assert.ok(r.negativeControls.year2025.finalUSD<r.negativeControls.year2025.passiveGoldUSD);
 assert.equal(r.scientificGate.promote,false);
 assert.equal(r.scientificGate.bankTradeAuthorized,false);
 assert.equal(r.primary.trades.length,4);
 assert.equal(r.primary.months.length,8);
 assert.equal(r.primary.trainingCounts.verifiedEconomicCheckpoints,0);
});
test("3h app V7 remains no-lookahead for all decisions before the changed future",()=>{
 const rows=loadRows(),stop="2026-06-30T12:00:00Z";
 const a=replayV6(rows,{stop,include_decisions:true});
 const synthetic=rows.map(r=>r.tt>stop?{...r,c:(r.c||1)*2,p:(r.p||1)*2}:r);
 const b=replayV6(synthetic,{stop,include_decisions:true});
 assert.deepEqual(a.decisionLog,b.decisionLog);
});
test("V7 local API read-only and legacy dashboard unaffected",()=>{
 const {requestHandler}=require("./server");
 const query=(url,method="GET")=>{
   let status,body;
   requestHandler({method,url},{writeHead(n){status=n;},end(x){body=x;}});
   return {status,body:JSON.parse(body)};
 };
 const actual=query("/api/algorithm/v7/adaptive");
 assert.equal(actual.status,200);
 assert.equal(actual.body.version,VERSION);
 assert.equal(actual.body.scientificGate.promote,false);
 assert.equal(query("/api/algorithm/v7/adaptive","POST").status,405);
 assert.equal(query("/api/health").status,200);
});
test("V7 dashboard section and JavaScript syntax are present",()=>{
 const html=fs.readFileSync(path.join(__dirname,"public","index.html"),"utf8");
 assert.match(html,/id="adaptiveV7"/);
 assert.match(html,/id="runAdaptiveV7"/);
 const source=fs.readFileSync(path.join(__dirname,"public","app.js"),"utf8");
 assert.doesNotThrow(()=>new vm.Script(source));
 assert.match(source,/\/api\/algorithm\/v7\/adaptive/);
});
