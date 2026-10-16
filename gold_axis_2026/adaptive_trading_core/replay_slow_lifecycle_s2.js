"use strict";
/** Research-only S2 daily-session replay; private SQL output never committed. */
const fs=require("node:fs"),crypto=require("node:crypto");
const slow=require("./adaptive_slow_lifecycle_s2");
const bridge=require("./adaptive_market_core_s1_s2");
function replay(rows,{attachSameCore=false}={}){
 if(!Array.isArray(rows)||!rows.length)throw Error("S2S_PRIVATE_ROWS_REQUIRED");
 const ids=[...new Set(rows.map(r=>r.source_id))];
 if(ids.length>4||ids.some(x=>typeof x!=="string"||!x))
  throw Error("S2S_SOURCE_ALLOWLIST_INVALID");
 const reg=Object.fromEntries(ids.map(id=>[id,
  {kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"}]));
 const mdl=attachSameCore?bridge.create({sourceId:ids[0],sourceIds:ids}):null;
 const s=mdl?mdl.slow:slow.create({sourceRegistry:reg});
 let previous="";
 for(const raw of rows){
  if(raw.session<=previous)throw Error("S2S_UNORDERED_OR_DUPLICATE_SESSION");
  previous=raw.session;
  const r={...raw,n:Number(raw.n),full_n:Number(raw.full_n),
   last_native_minute_bars:Number(raw.last_native_minute_bars),
   max_gap_minutes:Number(raw.max_gap_minutes),
   close_price:Number(raw.close_price)};
  if(mdl)bridge.observeSlowSession(mdl,r);
  else slow.observe(s,r);
 }
 slow.closeAtEnd(s);
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",stage:"S2_SLOW",
  withExistingS1Core:!!mdl,sourceIds:ids,privatePricesPersisted:false,
  inputSessions:rows.length,researchOnly:true,tradeActions:0,
  ...slow.summary(s),
  compositeAudit:mdl?{s1Version:mdl.s1.version,
   s2FastVersion:mdl.s2.version,slowVersion:s.version,
   attached:s.eligibleSessions,rejected:s.rejectedSessions}:null};
}
if(require.main===module){
 if(process.argv.length<3||process.argv.length>4||
  (process.argv[3]&&process.argv[3]!=="--same-core"))
   throw Error("Use PRIVATE_SESSION_JSON [--same-core]");
 const raw=fs.readFileSync(process.argv[2],"utf8");
 const sha=crypto.createHash("sha256").update(raw).digest("hex");
 console.log(JSON.stringify({runId:"S2_SLOW_"+sha.slice(0,16),inputSha256:sha,
  ...replay(JSON.parse(raw),{attachSameCore:process.argv[3]==="--same-core"})},null,2));
}
module.exports={replay};
