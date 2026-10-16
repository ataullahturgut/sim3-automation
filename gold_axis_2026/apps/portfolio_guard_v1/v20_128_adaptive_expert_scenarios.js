"use strict";
/**
 * Fixed development challenge, 8 synthetic regime families * 8 seeds * 2 fees.
 * V19 model parameters frozen before any performance results were observed.
 * Extra adversarial scenarios are functional tests, NOT XAU validation.
 */
const V18=require("./v18_kavis_dayaniqlilik");
const V19=require("./v20_kavis_atlas");
const F=require("./v18_128_adversarial_scenarios");
const BASE=Date.parse("2020-01-01T00:00:00Z"),DAY=24*3600000,HR=3600000;
const at=(d,h=6)=>new Date(BASE+d*DAY+h*HR).toISOString();
const pctl=(a,percent)=>[...a].sort((x,y)=>x-y)[Math.floor((a.length-1)*percent)];
function riskReplay(prices,fee,opt={}){
 const s=V19.create({core:{feePerSide:fee},...opt});
 let pos="CASH",forced=0,blocked=0,misses=0,early=0;
 for(let d=0;d<prices.length;d++){
  const a=V19.signal(s,{asof:at(d),featureAvailableAt:at(d),
    position:pos,market:F.features(prices,d),
    bankFeeQuote:{feePerSide:fee,availableAt:at(d)}});
  const z=V19.quote(s,{at:at(d,9),price:prices[d],
    bankFeePerSide:fee,isBankCheckpoint:true});
  if(!z.fill)throw Error("V20_MISSING_EXECUTION");
  pos=z.portfolio.position;
  if(a.reason==="DRAW_DOWN_GUARD"||a.reason==="TAIL_BUDGET_GUARD")forced++;
  if(a.reason==="RISK_BUDGET_BLOCK")blocked++;
  if(z.gapDrawdownBreached)misses++;
  if(a.action!==a.baseAction)early++;
 }
 const p=s.portfolio;
 return {capital:+p.nav.toFixed(4),trades:p.trades,
  maxDrawdown:+p.maxDrawdownPct.toFixed(3),
  forced,blocked,breachedCheckpoints:misses,
  changedDecisions:early,tailSamples:s.risk.learnedReturns,
  realCash:+p.cash.toFixed(3),units:+p.units.toFixed(6)};
}
function run(){
 const modes=["slow_ramp","gap_crash","false_break","flat_trap","whipsaw",
  "random_walk","fat_tails","regime_flip"];
 const rows=[];
 for(const mode of modes)for(let k=1;k<=8;k++){
  const seed=8000+97*k+modes.indexOf(mode)*307;
  const prices=F.series(mode,seed);
  for(const fee of [.008,.025]){
   const previous=F.replay(V18,prices,fee);
   const current=riskReplay(prices,fee);
   const ablated=riskReplay(prices,fee,{useRiskPolicy:false});
   const passive=100*(1-fee)*(1-fee)*prices.at(-1)/prices[0];
   if(Math.abs(ablated.capital-previous.capital)>.005||
      ablated.trades!==previous.trades)throw Error("V20_ABLATION_NOT_IDENTICAL_V18");
   rows.push({mode,seed,fee,v18:previous,v19:current,ablated,
     passive:+passive.toFixed(4),
     delta:+(current.capital-previous.capital).toFixed(4)});
  }
 }
 const deltas=rows.map(r=>r.delta),
  cap=rows.map(r=>r.v19.capital),dd=rows.map(r=>r.v19.maxDrawdown);
 return {kind:"V20_DEVELOPMENT_SYNTHETIC_ONLY",
  sampleSize:rows.length,cannotEstablishExpectedRealWorldProfit:true,
  frozenPolicy:true,causalAdvisorLearning:true,
  summary:{wins:rows.filter(r=>r.delta>0).length,
   losses:rows.filter(r=>r.delta<0).length,
   ties:rows.filter(r=>r.delta===0).length,
   meanV18:rows.reduce((x,y)=>x+y.v18.capital,0)/rows.length,
   meanV19:cap.reduce((x,y)=>x+y,0)/rows.length,
   medianCapital:pctl(cap,.5),minCapital:Math.min(...cap),
   medianMDD:pctl(dd,.5),p95MDD:pctl(dd,.95),
   belowCash:rows.filter(r=>r.v19.capital<100).length,
   beatsPassive:rows.filter(r=>r.v19.capital>r.passive).length,
   forcedExits:rows.reduce((x,y)=>x+y.v19.forced,0),
   blockedEntries:rows.reduce((x,y)=>x+y.v19.blocked,0),
   ablationMismatch:0},
  regimes:modes.map(m=>{const z=rows.filter(r=>r.mode===m);
   return {mode:m,wins:z.filter(r=>r.delta>0).length,
     losses:z.filter(r=>r.delta<0).length,ties:z.filter(r=>r.delta===0).length,
     meanV18:z.reduce((a,b)=>a+b.v18.capital,0)/z.length,
     meanV19:z.reduce((a,b)=>a+b.v19.capital,0)/z.length,
     maxMDD19:Math.max(...z.map(r=>r.v19.maxDrawdown))};}),
  rows};
}
if(require.main===module)console.log(JSON.stringify(run(),null,2));
module.exports={riskReplay,run};
