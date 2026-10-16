"use strict";
/**
 * Research-only replay of the SAME S1+S2+S3 core. Private reconstructed
 * M15 BID/ASK (MID research proxy) + completed qualified S2 slow sessions.
 * Example: node replay_position_value_s3.js PRIVATE_JOINED_ROWS.json
 * JSON: {"bars":[{bar_start_utc,source_id,bid_close,ask_close}],
 *        "slowSessions":[... S2_SLOW_EV_DUKA_SESSION_AUDIT rows ...]}
 * Output ONLY aggregated audit; original prices and trained checkpoint stay private.
 */
const fs=require("node:fs"),crypto=require("node:crypto");
const core=require("./adaptive_market_core_s1_s2");
function replay({bars,slowSessions=[]}={}){
 if(!Array.isArray(bars)||!bars.length||!Array.isArray(slowSessions))
  throw Error("S3_PRIVATE_MARKET_ROWS_REQUIRED");
 const sources=[...new Set(bars.map(r=>r.source_id))];
 if(sources.length>4||sources.some(x=>typeof x!=="string"||!x))
  throw Error("S3_SOURCE_ALLOWLIST_INVALID");
 const model=core.create({sourceId:sources[0],sourceIds:sources,
  learningMode:"DISCOVERY_FULL_ARCHIVE",shadowResearch:true});
 let last=-Infinity,slowAt=0,slowSeen=0,processed=0;
 const when=x=>{const d=Date.parse(x);
  if(!Number.isFinite(d)||!/(?:Z|[+-]\d\d:\d\d)$/i.test(x))
   throw Error("S3_PRIVATE_DATE_INVALID");return d;};
 const ordered=slowSessions.map(r=>({...r,sessionAt:when(r.session+"T22:00:00Z")}));
 for(let i=1;i<ordered.length;i++)
  if(ordered[i].sessionAt<=ordered[i-1].sessionAt)
   throw Error("S3_SLOW_SESSIONS_UNORDERED");
 function addSlow(r){
  core.observeSlowSession(model,{...r,n:Number(r.n),full_n:r.full_n===undefined?null:Number(r.full_n),
   valid_quotes:r.valid_quotes===undefined?null:Number(r.valid_quotes),
   last_native_minute_bars:r.last_native_minute_bars===undefined?null:Number(r.last_native_minute_bars),
   max_gap_minutes:Number(r.max_gap_minutes),close_price:Number(r.close_price)});
  slowSeen++;
 }
 for(const r of bars){
  const started=when(r.bar_start_utc);
  if(started<=last)throw Error("S3_PRIVATE_BARS_UNORDERED");
  last=started;
  const end=started+900000;
  while(slowAt<ordered.length&&ordered[slowAt].sessionAt<end)
   addSlow(ordered[slowAt++]);
  let price=Number(r.close_price);
  if(r.bid_close!==undefined&&r.ask_close!==undefined){
   const bid=Number(r.bid_close),ask=Number(r.ask_close);
   if(!Number.isFinite(bid)||bid<=0||!Number.isFinite(ask)||ask<bid)
    throw Error("S3_INVALID_BIDASK_PRICE");
   price=(bid+ask)/2;
  }
  if(!Number.isFinite(price)||price<=0)throw Error("S3_INVALID_PRICE");
  core.observe(model,{asof:new Date(end).toISOString(),
   barStartedAt:new Date(started).toISOString(),
   priceAvailableAt:new Date(end).toISOString(),
   price,priceSource:r.source_id,barMinutes:15});
  processed++;
  // The session ending exactly with this M15 close was not known earlier.
  while(slowAt<ordered.length&&ordered[slowAt].sessionAt===end)
   addSlow(ordered[slowAt++]);
 }
 const report=core.summary(model);
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",
  researchOnly:true,stage:"S3_ENGINEERING_SMOKE_NOT_S4_STRICT",
  quoteSemantics:"RECONSTRUCTED_M15_MID_PROXY_NOT_BANK_BIDASK",
  firstprintPIT:false,sourceIds:sources,barCount:processed,slowSeen,
  positionResearch:report.positionResearch,
  s1:report.ruleDiscovery,
  s2:{fastObservations:report.lifecycle.observations,
   fastEpisodes:report.lifecycle.completeEpisodes,
   slowSessions:report.slowLifecycle.completedSessions,
   slowEpisodes:report.slowLifecycle.completeEpisodes}};
}
if(require.main===module){
 if(process.argv.length!==3)throw Error("Use PRIVATE_JOINED_ROWS.json");
 const raw=fs.readFileSync(process.argv[2],"utf8");
 const inputSha256=crypto.createHash("sha256").update(raw).digest("hex");
 console.log(JSON.stringify({runId:"S3_RESEARCH_"+inputSha256.slice(0,16),
  inputSha256,...replay(JSON.parse(raw))},null,2));
}
module.exports={replay};
