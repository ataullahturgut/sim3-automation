"use strict";
/**
 * S1 DISCOVERY_FULL_ARCHIVE data-summary runner. DO NOT COMMIT PRIVATE INPUT.
 * 1) Generate read-only SQL from the research macro ledger:
 *    node independent_event_research_query_s1.js private_macro_ledger.csv > private_query.sql
 * 2) Run private_query.sql on read-only historical Neon and save JSON rows locally.
 * 3) node replay_independent_event_learning_s1.js private_derived_rows.json
 *
 * Output is ONLY aggregate evidence, no licensed raw market returns, prices,
 * event timestamps, per-event scores or checkpoint transferred into STRICT.
 */
const fs=require("node:fs"),crypto=require("node:crypto");
const engine=require("./independent_event_learning_s1");
function run(raw){
 if(!Array.isArray(raw))throw Error("DERIVED_ROWS_JSON_ARRAY_REQUIRED");
 const normalized=raw.map(r=>{
  const n={...r};
  for(const k of ["nfp","ahe","unemp","cpi","pre1h","next4h"])
   if(n[k]!==null&&n[k]!==undefined){
    n[k]=Number(n[k]);
    if(!Number.isFinite(n[k]))throw Error("NON_NUMERIC_DERIVED_INPUT_"+k);
   }
  return n;
 });
 const audit=engine.run(normalized);
 const inputHash=crypto.createHash("sha256").update(JSON.stringify(normalized)).digest("hex");
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",workstream:"MODEL",stage:"S1",
  runId:"DISCOVERY_FULL_ARCHIVE_"+inputHash.slice(0,16),
  inputSha256:inputHash,rawMarketPricesPersisted:false,
  inputRecords:normalized.length,...audit};
}
if(require.main===module){
 if(process.argv.length!==3)throw Error("Provide private derived-query-row JSON");
 const data=JSON.parse(fs.readFileSync(process.argv[2],"utf8"));
 console.log(JSON.stringify(run(data),null,2));
}
module.exports={run};
