"use strict";
const t=require("node:test"),assert=require("node:assert/strict");
const m=require("./macro_v6");
t("CME data is byte-pinned, non-future aligned, and complete within year",()=>{
 const x=m.macroRows();
 assert.equal(x.length,2904);
 assert.equal(x[0].tt,"2023-01-03T06:00:00.000Z");
 assert.equal(x.at(-1).tt,"2026-09-30T12:00:00.000Z");
 assert.ok(x.every((a,i)=>i===0||a.time>x[i-1].time));
 assert.ok(x.some(r=>r.zn6==null));
});
t("XAU price and CME match only exact 09:00 TRT times, with mature forward label separated",()=>{
 const r=m.labeledDays(m.priceRows(),m.macroRows());
 assert.ok(r.rows.length>100);
 assert.ok(r.rows.every(x=>x.tt.slice(11,13)==="06"));
 assert.ok(r.rows.every(x=>x.labelKnownAt===x.time+86400000));
 assert.ok(r.rows.every(x=>x.economicMechanism==="UNRESOLVED"));
 assert.ok(r.rows.every(x=>m.ALL.every(k=>Number.isFinite(x.features[k]))));
 assert.ok(r.missing.macro>0);
});
t("2024,2025,2026 chronological tests forbid contemporaneous labels for fitting",()=>{
 const a=m.runAudit();
 assert.equal(a.existingV1ToV5Frozen,true);
 assert.equal(a.annual.length,3);
 assert.deepEqual(a.annual.map(x=>x.year),[2024,2025,2026]);
 assert.ok(a.annual.every(x=>x.training.lastSeen.slice(0,4)<String(x.year)));
 assert.ok(a.annual.every(x=>x.test.positive+x.test.negative===x.test.n));
 assert.equal(a.acceptance.tradeAuthorized,false);
 assert.equal(a.acceptance.prospectiveBlind,false);
 assert.equal(a.acceptance.economicMechanismVerified,false);
 assert.equal(a.source.r71_r72_macroSurprise,"EXCLUDED_NO_VINTAGE_VERIFICATION");
});
t("logistic is deterministic, training-only and predictions are bounded",()=>{
 const data=m.labeledDays(m.priceRows(),m.macroRows()).rows;
 const before=data.filter(r=>r.year===2023),a=m.fit(before,m.XAU),b=m.fit(before,m.XAU);
 assert.deepEqual(a,b);
 assert.equal(a.w.length,5);
 const preds=data.slice(0,10).map(r=>m.predict(a,r));
 assert.ok(preds.every(p=>Number.isFinite(p)&&p>0&&p<1));
 const metric=m.score(data.slice(0,10),preds);
 assert.ok(Number.isFinite(metric.brier)&&Number.isFinite(metric.logLoss));
});


t("V6 must reject macro-edge claim when 2025 and 2026 underperform price-only",()=>{
 const a=m.runAudit();
 assert.equal(a.acceptance.incrementalEvidenceOn2024And2025,false);
 assert.equal(a.acceptance.verdict,"REJECT_UNPROVEN_CROSS_ASSET_IMPROVEMENT");
 assert.equal(a.acceptance.tradeAuthorized,false);
 assert.ok(a.annual.find(x=>x.year===2025).xauPlusCross.brier>a.annual.find(x=>x.year===2025).xauOnly.brier);
 assert.ok(a.annual.find(x=>x.year===2026).xauPlusCross.brier>a.annual.find(x=>x.year===2026).xauOnly.brier);
 assert.ok(a.annual.find(x=>x.year===2024).test.positive<10);
 assert.ok(a.coverage.completePairs>=400);
});
t("V6 API and screen are live, read-only, and do not change V1 decisions",()=>{
 const {requestHandler}=require("./server");
 function get(url,method="GET"){
  let status,body;requestHandler({url,method},{writeHead(v){status=v;},end(x){body=x;}});
  return {status,json:JSON.parse(body)};
 }
 const a=get("/api/algorithm/v6");
 assert.equal(a.status,200);
 assert.equal(a.json.version,m.VERSION);
 assert.equal(a.json.acceptance.tradeAuthorized,false);
 assert.equal(get("/api/algorithm/v6","POST").status,405);
 assert.ok(Math.abs(get("/api/summary").json.comparison[2].finalUSD-119.75391720039644)<1e-8);
 const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 const js=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 assert.match(html,/id="runV6"/);assert.match(js,/api\/algorithm\/v6/);
 assert.doesNotThrow(()=>new vm.Script(js));
});
