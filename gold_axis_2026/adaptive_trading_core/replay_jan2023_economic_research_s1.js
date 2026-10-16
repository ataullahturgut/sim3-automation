"use strict";
/**
 * Reproduce S1 January 2023 reconstructed economic on/off ablation.
 * Input private marketRows exported read-only from JAN2023_RECONSTRUCTED_ASOF_S1_INPUT.sql.
 * NO raw prices/checkpoints go to GitHub or stdout; derived results only.
 *
 * Usage: node replay_jan2023_economic_research_s1.js /path/private_jan2023_rows.json
 */
const fs=require("node:fs");
const path=require("node:path");
const replay=require("./replay_reconstructed_jan2023_s1");
const eco=require("./economic_pit_learning_s1");
const conf=require("./JAN2023_RESEARCH_PUBLICATION_ASSUMPTIONS_20261016.json");
const SCHEMA=[...replay.SCHEMA,...conf.releases.map(x=>x.type.toLowerCase()+"_surprise_z")];
function run(rows){
  if(!Array.isArray(rows)||rows.length!==102)throw Error("JAN2023_SOURCE_ANCHORS_NOT_102");
  const q={clipped:0};
  const obs=rows.map(r=>{
    const t=Date.parse(r.end_utc);
    if(!Number.isFinite(t)||t<Date.parse("2023-01-01T00:00:00Z")||
       t>=Date.parse("2023-02-01T00:00:00Z"))
       throw Error("JAN2023_INPUT_ONLY");
    if(r.source_id!==replay.XAU)throw Error("NOT_WHITELISTED_MARKET");
    const f={
      gold_1h:replay.feature(t,r.end_utc,r.gold_1h_pct,replay.XAU,q),
      nq_1h:replay.feature(t,r.nq_end,r.nq_1h_pct,replay.CME,q),
      zn_1h:replay.feature(t,r.zn_end,r.zn_1h_pct,replay.CME,q),
      cl_1h:replay.feature(t,r.cl_end,r.cl_1h_pct,replay.CME,q)
    };
    return {asof:r.end_utc,barStartedAt:r.bar_start_utc,barMinutes:15,
      price:Number(r.close_price),priceAvailableAt:r.end_utc,priceSource:replay.XAU,
      features:Object.fromEntries(Object.entries(f).filter(([,v])=>v!==null))};
  });
  const sourceRegistry={
    [replay.XAU]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"},
    [replay.CME]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"},
    RECONSTRUCTED_BLS_RESEARCH:{kind:"EVENT",evidenceStatus:"RECONSTRUCTED_RELEASE_RESEARCH"}
  };
  const base={marketRows:obs,releases:conf.releases,scales:conf.scales,
    featureNames:[...new Set(SCHEMA)],eventSource:"RECONSTRUCTED_BLS_RESEARCH",
    sourceRegistry,learningMode:"DISCOVERY_FULL_ARCHIVE",noveltyDistance:.3,maxRules:16};
  const results=conf.latencyMinutesSensitivity.map(delay=>{
    const a=eco.pairedReplay({...base,assumedAccessDelayMinutes:delay});
    return {latencyMinutes:delay,compared:a.compared,eventCompared:a.eventCompared,
      admittedComponentObservations:a.admitted,quarantinedComponentObservations:a.quarantined,
      eventDecisionAnchors:a.admissibleDecisionAnchors,
      unreadyEventForecasts:a.eventForecastNotReady,
      fallbackToMarketOnly:a.marketFallbackCount,
      correctEconomicOn:a.correctWith,correctMarketOnly:a.correctWithout,
      brierEconomicOn:a.withBrier,brierMarketOnly:a.withoutBrier,
      eventBrierEconomicOn:a.eventWithBrier,eventBrierMarketOnly:a.eventWithoutBrier,
      ruleCountEconomicOn:a.learnedWith.length,ruleCountMarketOnly:a.learnedWithout.length,
      eventRules:a.learnedWith.filter(x=>Object.keys(x.center).some(k=>k.endsWith("_surprise_z")))
        .map(x=>({nAnchors:x.anchorObservations,mature4h:x.outcomes[240]?.n||0,
          learnedDimensions:Object.keys(x.center).filter(k=>k.endsWith("_surprise_z"))}))};
  });
  const baseline=replay.run(rows).audit.prequential4h;
  return {workstream:"MODEL",stage:"S1",month:"2023-01",
    mode:"DISCOVERY_FULL_ARCHIVE",truePIT:false,certifiedFirstAccess:false,
    source:"READ_ONLY_NEON_RECONSTRUCTED_MARKET_AND_PUBLIC_HISTORICAL_RELEASES",
    rows:rows.length,quality:{reconstructedBarInputs:true,continuousFuturesPIT:false,clipped:q.clipped},
    oldMarketBaseline:{scored:baseline.scored,correct:baseline.modelCorrect,
      brier:baseline.modelBrier,historicalUpCorrect:baseline.historicalBaseCorrect,
      historicalUpBrier:baseline.historicalBaseBrier},
    results,scientificGate:"FAIL_EVENT_RULES_UNDER_MIN_SUPPORT",
    modelGate:"FAIL",tradePolicy:"NOT_IMPLEMENTED",
    reminder:"Never treat research mode as strict out-of-sample or a trade recommendation"};
}
if(require.main===module){
 if(process.argv.length!==3)throw Error("Usage: node replay_jan2023_economic_research_s1.js private_rows.json");
 const rows=JSON.parse(fs.readFileSync(path.resolve(process.argv[2]),"utf8"));
 console.log(JSON.stringify(run(rows),null,2));
}
module.exports={run};
