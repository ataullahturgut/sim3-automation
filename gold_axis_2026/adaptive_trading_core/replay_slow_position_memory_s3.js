"use strict";
/**
 * Private 2020–2025 retrospective DAILY research of the SAME S2 and S3 memory,
 * not a new trading system or a date-time reverse profitable simulation.
 * CLI: node replay_slow_position_memory_s3.js PRIVATE_S2_SESSION_ROWS.json
 * Daily source rows are produced by S2_SLOW_EV_DUKA_SESSION_AUDIT_2020_2025.sql.
 * No raw prices/learned proprietary checkpoint are emitted or committed.
 */
const fs=require("node:fs"),crypto=require("node:crypto");
const slow=require("./adaptive_slow_lifecycle_s2");
const memory=require("./adaptive_position_memory_s3");
function replayArchive(rows){
 if(!Array.isArray(rows)||!rows.length)throw Error("S3_ARCHIVE_ROWS_REQUIRED");
 const ids=[...new Set(rows.map(x=>x.source_id))];
 if(ids.length!==1||typeof ids[0]!=="string"||!ids[0])
  throw Error("S3_ARCHIVE_ONE_UNSPLICED_SOURCE_REQUIRED");
 const source=ids[0],registry={[source]:{
   kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"}};
 const s2=slow.create({sourceRegistry:registry}),m=memory.create();
 let rejected=0;
 for(const row of rows){
  const q={...row,close_price:Number(row.close_price),
    valid_quotes:Number(row.valid_quotes),n:Number(row.n),
    max_gap_minutes:Number(row.max_gap_minutes)};
  const r=slow.observe(s2,q);
  if(r.phase==="REJECTED_SESSION"){rejected++;continue;}
  memory.completed(m,{session:q.session,sourceId:q.source_id,
    price:q.close_price,phase:r.phase,direction:r.direction,
    availableAt:q.session+"T22:00:00Z"});
 }
 const a=memory.summary(m),b=slow.summary(s2);
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",
    report:"S2_S3_MULTIDAY_RETROSPECTIVE_MEMORY_NOT_S4_TRADING_TEST",
    learningMode:"DISCOVERY_FULL_ARCHIVE",liveTradeAuthorized:false,
    sourceId:source,rows:rows.length,rejected,
    qualifiedSessions:b.completedSessions,s2CompletedEpisodes:b.completeEpisodes,
    s2CensoredEpisodes:b.censoredEpisodes,
    memory:a,bankFeesPerLeg:0.008,
    inferenceWarning:"OVERLAPPING_SESSION_RETURNS_NO_INDEPENDENT_ALPHA_PROOF",
    certifiedPIT:false,bankExecutionPrices:false};
}
if(require.main===module){
 if(process.argv.length!==3)throw Error("Use PRIVATE_S2_SESSION_ROWS.json");
 const raw=fs.readFileSync(process.argv[2],"utf8");
 const hash=crypto.createHash("sha256").update(raw).digest("hex");
 console.log(JSON.stringify({runId:"S3_SLOW_ARCHIVE_"+hash.slice(0,16),
  inputSha256:hash,...replayArchive(JSON.parse(raw))},null,2));
}
module.exports={replayArchive};
