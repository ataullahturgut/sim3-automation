"use strict";
const t=require("node:test"),assert=require("node:assert/strict");
const v3=require("./recovery_v3"),v4=require("./recovery_v4"),core=require("./engine");
t("V4 learns volatility thresholds only before each origin",()=>{
 const hist=v3.loadHistorical(),a=v4.trainBefore(hist,Date.parse("2023-01-01T00:00:00Z"));
 assert.ok(a.trainBars>3000);
 assert.equal(a.trainingEndUTC.startsWith("2022"),true);
 assert.ok(a.rvP95>a.rvP75);
 assert.ok(a.bank.every(e=>e.knownAt<=Date.parse("2023-01-01T00:00:00Z")));
 assert.equal(a.riskProbabilityCalibrated,false);
});
t("V4 no trades outside three daytime decision slots",()=>{
 const x=v4.runResearch();
 for(const result of [x.january,x.february]){
  for(const order of result.actions){
   assert.ok([9,12,15].includes(Number(order.tr.slice(11,13))));
   assert.equal(order.economicCause,"UNRESOLVED");
   assert.equal(order.fullBankSpreadIncluded,false);
   assert.ok(order.trainingEndUTC.startsWith("2025"));
  }
 }
 assert.equal(x.economicCauseVerified,false);
});
t("V4 rolls from frozen Jan V1 cash, leaves V1 unchanged",()=>{
 const a=v4.runResearch(),b=v4.runResearch();
 assert.deepEqual(a,b);
 assert.equal(a.february.startUSD,119.75391720039644);
 assert.equal(a.january.startUSD,100);
 assert.equal(a.annual.length,3);
 assert.deepEqual(a.annual.map(y=>y.year),[2023,2024,2025]);
 assert.ok(a.annual.every(y=>y.trainingUntil.slice(0,4)<String(y.year)));
 assert.equal(a.baseline.v1JanUSD,core.runAll().scenarios.event15m.finalUSD);
 assert.equal(a.warning.includes("retrospective"),true);
});
t("V4 input contract forbids invalid or unsorted prices",()=>{
 const train=v4.trainBefore(v3.loadHistorical(),Date.parse("2023-01-01T00:00:00Z"));
 assert.throws(()=>v4.simulate([],train,{initialUSD:100}),/EMPTY_TRADING_ROWS/);
 const x=v3.loadHistorical()[0];
 assert.throws(()=>v4.simulate([x,x],train),/NONMONOTONIC_SOURCE/);
 assert.throws(()=>v4.simulate([x],train,{initialUSD:0}),/INVALID_CASH/);
});
t("V4 can abstain, or signal emergency, without inventing a G05/G06 cause",()=>{
 const h=v3.loadHistorical(),tr=v4.trainBefore(h,Date.parse("2023-01-01T00:00:00Z"));
 const r={...h[0],r4:-4,r92:-10,rv:Math.max(tr.rvP95*1.3,3)};
 const s=v4.classify(r,null,"UNKNOWN",tr);
 assert.equal(s.emergency,true);
 assert.equal(s.marketCause,"UNRESOLVED");
 const x=v4.quantile([10,20,30,40,50],.75);
 assert.equal(x,40);
});


t("V4 endpoint actually replays and old V1 endpoint remains frozen",()=>{
 const {requestHandler}=require("./server");
 function read(url,method="GET"){
  let status,body;
  requestHandler({url,method},{writeHead(code){status=code;},end(content){body=content;}});
  return {status,value:JSON.parse(body)};
 }
 const m=read("/api/algorithm/v4");
 assert.equal(m.status,200);
 assert.equal(m.value.version,v4.VERSION);
 assert.equal(m.value.february.startUSD,119.75391720039644);
 assert.equal(m.value.annual.length,3);
 assert.equal(m.value.economicCauseVerified,false);
 assert.equal(m.value.bankBidAskSpreadIncluded,false);
 assert.equal(read("/api/algorithm/v4","POST").status,405);
 const old=read("/api/summary");
 assert.equal(old.status,200);
 assert.ok(Math.abs(old.value.comparison[2].finalUSD-119.75391720039644)<1e-8);
});
t("V4 button and read-only JS visualizer are present and parse cleanly",()=>{
 const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 const js=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 assert.match(html,/id="runV4"/);
 assert.match(html,/id="v4Trades"/);
 assert.match(js,/api\/algorithm\/v4/);
 assert.doesNotThrow(()=>new vm.Script(js,{filename:"public/app.js"}));
});
