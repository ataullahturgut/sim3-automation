"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const {csvParse,runAll,simulate,loadFrozen,VERSION}=require("./engine");

test("CSV parser preserves quoted source fields and quoted line breaks",()=>{
 const source='a,b,c\n1,"k,l","q""w"\n2,"multiline\ninside",x\n';
 const rows=csvParse(source);
 assert.equal(rows.length,2);
 assert.deepEqual(rows[0],{a:"1",b:"k,l",c:'q"w'});
 assert.equal(rows[1].b,"multiline\ninside");
});

test("same pinned data and code always produce identical results",()=>{
 const a=runAll(),b=runAll();
 assert.equal(a.version,VERSION);
 assert.deepEqual(a,b);
 assert.equal(Object.keys(a.inputs).length,3);
});

test("Ocak 2026 frozen 15m event model regression",()=>{
 const r=runAll().scenarios.event15m;
 assert.ok(Math.abs(r.finalUSD-119.75391720039644)<0.000001);
 assert.equal(r.actions.length,2);
 assert.equal(r.actions[0].utc,"2026-01-05T06:30:00.000Z");
 assert.equal(r.actions[0].price,4424.055);
 assert.equal(r.actions[0].action,"BUY_GOLD");
 assert.equal(r.actions[1].utc,"2026-01-29T15:15:00.000Z");
 assert.equal(r.actions[1].price,5383.775);
 assert.equal(r.actions[1].action,"SELL_TO_CASH");
 assert.equal(r.terminalAsset,"CASH");
 assert.equal(r.fullCalendarSlots,2976);
 assert.equal(r.completePriceBars,1804);
 assert.equal(r.archiveCases,92);
 assert.equal(r.days.length,31);
 assert.ok(Math.abs(r.maxDrawdownPct-3.6125326847556094)<0.01);
});

test("event DNA does not claim a P&L contribution absent in the data",()=>{
 const {event15m,price15m,legacy3h}=runAll().scenarios;
 assert.ok(Math.abs(event15m.finalUSD-price15m.finalUSD)<1e-9);
 assert.deepEqual(event15m.actions.map(x=>x.utc),price15m.actions.map(x=>x.utc));
 assert.ok(Math.abs(legacy3h.finalUSD-118.337853)<0.00002);
 assert.notEqual(legacy3h.finalUSD,event15m.finalUSD);
});

test("no 2026 Jan decisions are created at absent M15 time slots",()=>{
 const r=runAll().scenarios.event15m;
 assert.ok(r.ledger.some(x=>!x.hasNewBar));
 assert.equal(r.ledger[0].turkey,"2026-01-01 00:00");
 assert.equal(r.ledger.at(-1).turkey,"2026-01-31 23:45");
 for(const x of r.ledger){
  if(!x.hasNewBar)assert.ok(x.action==="HOLD_CASH"||x.action==="HOLD_GOLD");
 }
});

test("invalid mode rejected and source is not mutated by replay",()=>{
 const dataset=loadFrozen();
 assert.throws(()=>simulate(dataset,"arbitrary"),/UNSUPPORTED_MODEL_VERSION/);
 const before=JSON.stringify(dataset.rows[0]);
 simulate(dataset,"event15m");
 assert.equal(JSON.stringify(dataset.rows[0]),before);
});


test("read-only local API exposes pinned health, three models and full ledger",()=>{
 const {requestHandler,summary}=require("./server");
 assert.equal(summary().comparison.length,3);
 function request(url,method="GET"){
  let code,headers,payload;
  const req={url,method};
  const res={writeHead(c,h){code=c;headers=h;},end(x){payload=x;}};
  requestHandler(req,res);
  return {code,headers,body:JSON.parse(payload)};
 }
 const h=request("/api/health");
 assert.equal(h.code,200);
 assert.equal(h.body.readOnly,true);
 const s=request("/api/summary");
 assert.equal(s.code,200);
 assert.equal(s.body.comparison.length,3);
 assert.equal(s.body.incrementalDNABenefitUSD,0);
 const d=request("/api/replay?mode=event15m");
 assert.equal(d.code,200);
 assert.equal(d.body.ledger.length,2976);
 assert.equal(d.body.actions.length,2);
 assert.equal(request("/api/replay?mode=other").code,400);
 assert.equal(request("/api/unknown").code,404);
 assert.equal(request("/api/summary","POST").code,405);
});


test("dashboard JavaScript parses and the local landing page is served",()=>{
 const vm=require("node:vm"),fs=require("node:fs"),path=require("node:path");
 const script=fs.readFileSync(path.join(__dirname,"public","app.js"),"utf8");
 assert.doesNotThrow(()=>new vm.Script(script,{filename:"public/app.js"}));
 const {requestHandler}=require("./server");
 let status,content,header;
 requestHandler({method:"GET",url:"/"},{
  writeHead(s,h){status=s;header=h;},
  end(v){content=v;}
 });
 assert.equal(status,200);
 assert.match(header["Content-Type"],/text\/html/);
 assert.match(content,/Altın portföy koruma/);
 assert.match(content,/data-mode="event15m"/);
});


test("Windows CRLF checkout of a pinned CSV still passes strict Git blob check",()=>{
 const {gitBlobHash,decodePinnedSource}=require("./engine");
 const input=Buffer.from("time,value\n2026-01-01,100\n2026-01-02,101\n","utf8");
 const spec={path:"test-source.csv",blob:gitBlobHash(input)};
 const win=Buffer.from(input.toString("utf8").replace(/\n/g,"\r\n"),"utf8");
 assert.notEqual(gitBlobHash(win),spec.blob);
 const decoded=decodePinnedSource(spec,win);
 assert.equal(decoded.gitBlob,spec.blob);
 assert.equal(decoded.windowsLineEndingsNormalized,true);
 assert.equal(decoded.rows.length,2);
 assert.deepEqual(decoded.rows,decodePinnedSource(spec,input).rows);
});
test("Windows CRLF repair must never silently accept modified prices",()=>{
 const {gitBlobHash,decodePinnedSource}=require("./engine");
 const clean=Buffer.from("price\n100\n101\n","utf8");
 const spec={path:"fake.csv",blob:gitBlobHash(clean)};
 const bad=Buffer.from("price\r\n100\r\n999\r\n","utf8");
 assert.throws(()=>decodePinnedSource(spec,bad),/DATA_VERSION_MISMATCH/);
});
