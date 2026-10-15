"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const v3=require("./recovery_v3");
test("frozen 2020-2025 3h history and origin embargo are valid",()=>{
 const rows=v3.loadHistorical();
 assert.equal(rows.length,10850);
 assert.equal(rows[0].tt,"2020-01-07T00:00:00.000Z");
 assert.ok(rows.every((r,i)=>i===0||r.time>rows[i-1].time));
 const prior=v3.pastOnlyEpisodeBank(rows,Date.parse("2026-01-01T00:00:00Z"));
 assert.ok(prior.every(e=>e.knownAt<=Date.parse("2026-01-01T00:00:00Z")));
 assert.ok(prior.every(e=>e.causalMechanism==="UNRESOLVED"));
 assert.ok(prior.every(e=>e.possibleDNA.includes("G05-C")&&e.possibleDNA.includes("G06-B")));
});
test("phase recognition never infers economic causality",()=>{
 const row={p:1,c:1,r4:2,r92:4,r276:-12,rv:2,ds:.35,loc:.8,dd276:-13,
  v92:2,eff:.5,dd4:-1};
 assert.equal(v3.condition(row,null,"UNKNOWN"),"RECOVERY_CANDIDATE");
 row.r4=-4;row.rv=3;
 assert.equal(v3.condition(row,null,"UNKNOWN"),"CAPITULATION_CANDIDATE");
 row.r4=-1.5;row.rv=1;row.r92=-3;
 assert.equal(v3.condition(row,null,"UNKNOWN"),"FALLING_FAST");
});
test("no bank orders beyond 09:00-17:00 Istanbul",()=>{
 assert.equal(v3.isDecisionTime(Date.parse("2026-02-03T03:00:00Z")),false);
 assert.equal(v3.isDecisionTime(Date.parse("2026-02-03T06:00:00Z")),true);
 assert.equal(v3.isDecisionTime(Date.parse("2026-02-03T12:00:00Z")),true);
 assert.equal(v3.isDecisionTime(Date.parse("2026-02-03T15:00:00Z")),false);
});
test("walk-forward training excludes target year and model is deterministic",()=>{
 const a=v3.annualWalk(),b=v3.annualWalk();
 assert.deepEqual(a,b);
 assert.deepEqual(a.map(x=>x.year),[2023,2024,2025]);
 assert.ok(a.every(x=>x.trainThrough<x.year));
 assert.ok(a.every(x=>x.bankEpisodes>0));
 assert.ok(a.every(x=>x.finalUSD>0&&x.buyHoldUSD>0));
 assert.ok(a.every(x=>x.fullTemporalCoverage===false));
});
test("Feb research starts with EXACT frozen Jan V1 cash, independent of Jan V3",()=>{
 const a=v3.runJanuaryFebruary(),b=v3.runJanuaryFebruary();
 assert.deepEqual(a,b);
 assert.equal(a.status,"EXPLORATORY_RETROSPECTIVE_NOT_OOS");
 assert.equal(a.february.startUSD,119.75391720039644);
 assert.equal(a.february.days.length,28);
 assert.equal(a.january.days.length,31);
 assert.equal(a.sourcePriceHistory2023Incomplete,true);
 assert.equal(a.february.economicCausalityProven,false);
 for(const action of a.february.actions){
  const hour=+action.tr.slice(11,13);
  assert.ok([9,12,15].includes(hour));
  assert.equal(action.causality,"UNRESOLVED");
 }
});
test("no phase transition can access price history after its as-of timestamp",()=>{
 const rows=v3.loadHistorical();
 const origin=Date.parse("2023-01-01T00:00:00Z");
 const b=v3.pastOnlyEpisodeBank(rows.filter(x=>x.time<origin),origin);
 assert.ok(b.every(x=>x.knownAt<=origin));
 assert.ok(b.every(x=>x.time<origin));
 const future=v3.pastOnlyEpisodeBank(rows.filter(x=>x.time<origin),Date.parse("2022-06-01T00:00:00Z"));
 assert.ok(future.every(x=>x.knownAt<=Date.parse("2022-06-01T00:00:00Z")));
});


test("V3 research API is read-only and original January/February results remain unchanged",()=>{
 const {requestHandler}=require("./server");
 function req(url,method="GET"){
  let status,body;requestHandler({method,url},{writeHead(s){status=s;},end(b){body=b;}});
  return {status,json:JSON.parse(body)};
 }
 const r=req("/api/algorithm/v3");
 assert.equal(r.status,200);
 assert.equal(r.json.version,v3.VERSION);
 assert.equal(r.json.history.totalRows,10850);
 assert.equal(r.json.february.startUSD,119.75391720039644);
 assert.equal(r.json.february.period,"Şubat 2026");
 assert.equal(r.json.annual.length,3);
 assert.equal(r.json.bankSpreadIncluded,false);
 assert.equal(req("/api/algorithm/v3","POST").status,405);
 const frozen=req("/api/summary");
 assert.ok(Math.abs(frozen.json.comparison[2].finalUSD-119.75391720039644)<1e-8);
});
test("V3 screen has its own non-authoritative button and valid javascript",()=>{
 const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 const javascript=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 assert.match(html,/id="runV3"/);
 assert.match(html,/id="v3FebFinal"/);
 assert.match(javascript,/api\/algorithm\/v3/);
 assert.doesNotThrow(()=>new vm.Script(javascript));
});


test("market closure cannot certify consecutive phase confirmation, or backfill February 1 prices",()=>{
 const x=v3.runJanuaryFebruary();
 assert.equal(x.february.days[0].date,"2026-02-01");
 assert.equal(x.february.days[0].completeBars,0);
 assert.equal(x.february.days[0].netValue,119.7539);
 assert.equal(x.february.days[0].actions.length,0);
});
