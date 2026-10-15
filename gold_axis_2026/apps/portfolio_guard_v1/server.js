"use strict";
/** Offline-first local historical research dashboard; localhost only. */
const http=require("node:http");
const fs=require("node:fs");
const path=require("node:path");
const engine=require("./engine");
const HOST="127.0.0.1";
const portValue=process.env.PORT||"8787";
const PORT=Number(portValue);
if(!Number.isSafeInteger(PORT)||PORT<1024||PORT>65535)throw new Error("PORT must be 1024..65535");
const snapshots=engine.runAll(); // load + verify Git blob SHA + regression tests; fail closed
const scientificV2=require("./event_audit_v2").runAudit(); // read-only, independent shadow diagnostics
function small(v) {
 const x=snapshots.scenarios[v];
 return {
  model:x.model,version:x.version,period:x.period,startUSD:x.startUSD,
  finalUSD:x.finalUSD,returnPct:x.returnPct,maxDrawdownPct:x.maxDrawdownPct,
  benchmarkBuyHoldUSD:x.benchmarkBuyHoldUSD,terminalAsset:x.terminalAsset,
  goldOunces:x.goldOunces,checks:x.checks,fullCalendarSlots:x.fullCalendarSlots,
  completePriceBars:x.completePriceBars,archiveCases:x.archiveCases,
  actions:x.actions,days:x.days
 };
}
function respond(res,code,data,type) {
 res.writeHead(code,{"Content-Type":type||"application/json; charset=utf-8",
  "Cache-Control":"no-store","X-Content-Type-Options":"nosniff",
  "X-Frame-Options":"DENY",
  "Content-Security-Policy":"default-src 'self'; connect-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'",
  "Access-Control-Allow-Origin":"null"});
 res.end(data);
}
function summary(){
 const {scenarios}=snapshots;
 return {
  version:snapshots.version,
  status:"RESEARCH_ONLY_NOT_LIVE",
  guarantee:"same frozen input blob + code + parameters = same replay output",
  dataHashes:snapshots.inputs,
  bankSpreadIncluded:false,commissionPerSide:0.008,
  independentOutOfSample:false,economicCausalityProven:false,
  comparison:["legacy3h","price15m","event15m"].map(function(m){return small(m);}),
  incrementalDNABenefitUSD:scenarios.event15m.finalUSD-scenarios.price15m.finalUSD
 };
}
function requestHandler(req,res) {
 if(req.method!=="GET"&&req.method!=="HEAD")return respond(res,405,JSON.stringify({error:"READ_ONLY_GET_ONLY"}));
 const url=new URL(req.url,"http://localhost");
 const route=url.pathname;
 if(route==="/api/summary")return respond(res,200,JSON.stringify(summary()));
 if(route==="/api/replay"){
  const mode=url.searchParams.get("mode");
  if(!["event15m","price15m","legacy3h"].includes(mode))
   return respond(res,400,JSON.stringify({error:"UNKNOWN_FROZEN_MODEL",allowed:["event15m","price15m","legacy3h"]}));
  return respond(res,200,JSON.stringify(snapshots.scenarios[mode]));
 }
 if(route==="/api/algorithm/v2")return respond(res,200,JSON.stringify(scientificV2));
 if(route==="/api/health"){
  return respond(res,200,JSON.stringify({ok:true,version:snapshots.version,verifiedAtStartup:true,readOnly:true}));
 }
 const files={"/":"index.html","/index.html":"index.html","/app.js":"app.js","/style.css":"style.css"};
 const name=files[route];
 if(!name)return respond(res,404,JSON.stringify({error:"NOT_FOUND"}));
 const mime=name.endsWith(".js")?"text/javascript; charset=utf-8":name.endsWith(".css")?"text/css; charset=utf-8":"text/html; charset=utf-8";
 return respond(res,200,fs.readFileSync(path.join(__dirname,"public",name),"utf8"),mime);
}
if(require.main===module){
 if(process.argv.includes("--verify")){
  const s=summary();
  console.log(JSON.stringify({status:"PASS",version:s.version,
    price15m:s.comparison[1].finalUSD,
    event15m:s.comparison[2].finalUSD,
    legacy3h:s.comparison[0].finalUSD,
    hashChecks:"PASS",bankExecution:false},null,2));
 }else{
  http.createServer(requestHandler).listen(PORT,HOST,function(){
   console.log("Gold Portfolio Guard V1 — http://"+HOST+":"+PORT);
   console.log("Historical replay only; no bank login and no order execution.");
  });
 }
}
module.exports={requestHandler,summary,small};
