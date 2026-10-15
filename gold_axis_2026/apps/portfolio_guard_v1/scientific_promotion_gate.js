"use strict";
/**
 * Fail-closed model selection. Retrospective demonstrations cannot silently
 * promote an experimental model to investment authority.
 * This module does not fit any parameters or read future labels.
 */
function evaluate(V4annual,V5annual,V4forward,V5forward){
 const years=[2023,2024,2025];
 const paired=years.map(y=>{
  const a=V4annual.find(z=>z.year===y),b=V5annual.find(z=>z.year===y);
  if(!a||!b)throw Error("MISSING_COMPARISON_YEAR");
  const oldEnd=a.V4,newEnd=b.finalUSD,hold=b.buyHoldUSD;
  return {year:y,olderV4USD:oldEnd,newV5USD:newEnd,
   buyHoldUSD:hold,v5MinusV4:newEnd-oldEnd,
   v5MinusHold:newEnd-hold,
   v5MaxDDPct:b.maxDrawdownPct,v4MaxDDPct:a.maxDrawdownPct,
   v5Trades:b.buys+b.sells,v4Trades:a.trades,
   validFullYearCoverage:y!==2023};
 });
 const checked=paired.filter(p=>p.validFullYearCoverage);
 const winsV4=checked.filter(p=>p.newV5USD>p.olderV4USD).length;
 const winsHold=checked.filter(p=>p.newV5USD>p.buyHoldUSD).length;
 const ddWins=checked.filter(p=>p.v5MaxDDPct<p.v4MaxDDPct).length;
 const fewerTrades=checked.filter(p=>p.v5Trades<=p.v4Trades).length;
 const extraProtected2026=V5forward.fromFebThroughSeptember.finalUSD-V4forward.actual.finalUSD;
 const costAwareGate=checked.every(p=>p.v5Trades<=p.v4Trades);
 const requirements={
  winsOlderStrategyAcrossBothCompleteYears:winsV4===2,
  beatsHoldAcrossBothCompleteYears:winsHold===2,
  improvesDrawdownAcrossBothCompleteYears:ddWins===2,
  doesNotIncreaseTransactionCountInEitherYear:costAwareGate,
  verifiedRealBankBidAsk:false,
  prospectivelyBlindValidation:false,
  confirmedEconomicEventFirstprint:false,
  original2023SourceComplete:false
 };
 return {
  status:"REJECT_PROMOTION",
  candidate:"V5_SLOW_TREND_PROTECTION_SHADOW_20261015",
  evaluationBasis:"PREREGISTERED_FIXED_V4_V5_AFTER_KNOWN_2026_STRESS",
  currentResearchComparisons:{years:paired,
   completeYearV4Wins:winsV4,completeYearHoldWins:winsHold,
   completeYearMaxDDWins:ddWins,completeYearFewerOrEqualTrades:fewerTrades,
   V5AdditionalUSDFromFebThroughSep:extraProtected2026},
  requirements,authorized:false,
  unmetRequirements:Object.entries(requirements).filter(([_,ok])=>!ok).map(([name])=>name),
  limitations:["Feb-Sep 2026 outcomes observed before V5 design",
   "real bank bid-ask and slip absent","2023 source coverage incomplete",
   "G05-C/G06-B economic causality not verified"],
  rule:"Pass every gate and demonstrate future validated value before changing V1 or connecting a broker."
 };
}
module.exports={evaluate};
