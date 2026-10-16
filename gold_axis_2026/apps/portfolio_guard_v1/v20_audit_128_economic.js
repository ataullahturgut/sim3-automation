"use strict";
const F=require("./v18_128_adversarial_scenarios"),
  Core=require("./v18_kavis_dayaniqlilik"),
  Old=require("./v20_kavis_atlas"),
  Fixed=require("./v20_kavis_atlas_repaired");
const BASE=Date.parse("2020-01-01T00:00:00Z"),DAY=86400000,HR=3600000;
const stamp=(d,h)=>new Date(BASE+d*DAY+h*HR).toISOString();
const median=x=>[...x].sort((a,b)=>a-b)[Math.floor((x.length-1)/2)];
function replay(Model,prices,fee,options={}){
 const s=Model.create({core:{feePerSide:fee},...options});
 let pos="CASH",changes=0;
 for(let i=0;i<prices.length;i++){
  const x=Model.signal(s,{asof:stamp(i,6),featureAvailableAt:stamp(i,6),
   position:pos,market:F.features(prices,i),
   bankFeeQuote:{feePerSide:fee,availableAt:stamp(i,6)}});
  const q=Model.quote(s,{at:stamp(i,9),price:prices[i],
   isBankCheckpoint:true,bankFeePerSide:fee});
  if(!q.fill)throw Error("UNEXPECTED_NON_EXECUTED_QUOTE");
  pos=q.portfolio.position;
  if(x.baseAction!==x.action)changes++;
 }
 return {capital:+s.portfolio.nav.toFixed(3),
  maxDD:+s.portfolio.maxDrawdownPct.toFixed(3),
  trades:s.portfolio.trades,
  changed:changes,
  falseGapWarnings:s.audit.postCrashGapWarnings,
  blocked:s.audit.blockedEntries,
  adviser:s.audit.advisorActivated,
  trained1:s.audit.advisorMatured,
  trained2:s.audit.advisorMatured2??0,
  lastFee:s.core.feeKnowledge.lastKnown};
}
function summarize(rows,key){
 const a=rows.map(z=>z[key]);
 return {meanCapital:+(a.reduce((u,z)=>u+z.capital,0)/a.length).toFixed(3),
  medianCapital:+median(a.map(z=>z.capital)).toFixed(3),
  minCapital:Math.min(...a.map(z=>z.capital)),
  meanMDD:+(a.reduce((u,z)=>u+z.maxDD,0)/a.length).toFixed(3),
  maxMDD:Math.max(...a.map(z=>z.maxDD)),
  totalAdvisorActivations:a.reduce((u,z)=>u+z.adviser,0),
  totalTrainedOneStep:a.reduce((u,z)=>u+z.trained1,0),
  totalTrainedTwoStep:a.reduce((u,z)=>u+z.trained2,0),
  falseGapWarnings:a.reduce((u,z)=>u+z.falseGapWarnings,0)};
}
function study(){
 const modes=["slow_ramp","gap_crash","false_break","flat_trap",
  "whipsaw","random_walk","fat_tails","regime_flip"];
 const rows=[];
 for(let j=0;j<modes.length;j++)for(let k=1;k<=8;k++){
  const mode=modes[j],seed=8000+97*k+j*307,
    price=F.series(mode,seed);
  for(const fee of [.008,.025]){
   const original=replay(Old,price,fee);
   const repaired=replay(Fixed,price,fee);
   const control=F.replay(Core,price,fee);
   rows.push({mode,seed,fee,original,repaired,control,
     delta:+(repaired.capital-original.capital).toFixed(3)});
  }
 }
 const subset=rows.filter(z=>z.fee===.008&&
  ["gap_crash","whipsaw","fat_tails"].includes(z.mode));
 const limit=[];
 for(const row of subset){
  const prices=F.series(row.mode,row.seed),fee=row.fee;
  limit.push({mode:row.mode,seed:row.seed,
   old15:replay(Old,prices,fee,{maxDrawdownPct:15}),
   repaired15:replay(Fixed,prices,fee,{maxDrawdownPct:15}),
   repairedStrict:replay(Fixed,prices,fee,
      {maxDrawdownPct:15,enforceEntryRiskBudget:true})});
 }
 return {label:"SYNTHETIC_REVISITED_DEVELOPMENT_NOT_BLIND",
  rows:rows.length,
  summary:{v18:{meanCapital:+(rows.reduce((u,z)=>u+z.control.capital,0)/rows.length).toFixed(3)},
   original:summarize(rows,"original"),repaired:summarize(rows,"repaired"),
   wins:rows.filter(z=>z.delta>0).length,
   losses:rows.filter(z=>z.delta<0).length,
   ties:rows.filter(z=>z.delta===0).length},
  explicit15pct:{cases:limit.length,old:summarize(limit,"old15"),
   repaired:summarize(limit,"repaired15"),
   prospectiveOptional:summarize(limit,"repairedStrict")},
  byMode:modes.map(mode=>{const a=rows.filter(z=>z.mode===mode);
   return {mode,oldMean:+(a.reduce((x,y)=>x+y.original.capital,0)/a.length).toFixed(3),
     repairedMean:+(a.reduce((x,y)=>x+y.repaired.capital,0)/a.length).toFixed(3),
     better:a.filter(z=>z.delta>0).length,worse:a.filter(z=>z.delta<0).length};}),
  worstCases:rows.sort((a,b)=>a.delta-b.delta).slice(0,10).map(z=>({
   mode:z.mode,fee:z.fee,seed:z.seed,delta:z.delta,
   original:z.original.capital,repaired:z.repaired.capital})),
  researchOnly:true};
}
if(require.main===module)console.log(JSON.stringify(study(),null,2));
module.exports={replay,study};
