"use strict";
/**
 * NEW fictional families and seeds chosen after algorithm code lock.
 * No real financial observations, and no claim of blindness to synthetic
 * scenario family because general development patterns were already known.
 */
const F=require("./v18_128_adversarial_scenarios"),
 D=require("./v20_r2_128_dev_worlds");
const families=["volatility_collapse","spike_and_grind","nested_v",
 "persistent_down","low_vol_rally","alternating_quarter"];
function rng(seed){let x=seed>>>0;return()=>{
  x=(Math.imul(x,1664525)+1013904223)>>>0;return x/4294967296;};}
function series(kind,seed){
 const r=rng(seed),n=285,log=[Math.log(100)];
 for(let i=1;i<n;i++){
  let drift=0,sigma=.007;
  if(kind==="volatility_collapse"){drift=i<90?.0004:i<180?.008:-.005;
    sigma=i<90?.06:i<180?.005:.018;}
  if(kind==="spike_and_grind"){drift=i<85?.004:i<95?-.034:i<235?.006:-.003;sigma=.011;}
  if(kind==="nested_v"){drift=i<65?.012:i<95?-.020:i<150?.015:i<179?-.016:.01;sigma=.008;}
  if(kind==="persistent_down"){drift=i<90?-.005:i<185?-.008:-.002;sigma=.012;}
  if(kind==="low_vol_rally"){drift=.0025;sigma=.001;}
  if(kind==="alternating_quarter"){drift=Math.floor(i/65)%2===0?.01:-.009;sigma=.025;}
  const ret=drift+(r()-.5)*sigma;
  log.push(log.at(-1)+ret);
 }
 return log.map(Math.exp);
}
function mean(a){return a.reduce((x,y)=>x+y,0)/a.length;}
function evaluate(){
 const worlds=[];
 for(let j=0;j<families.length;j++)for(let k=0;k<4;k++){
  const kind=families[j],seed=905123+j*971+k*41,prices=series(kind,seed);
  for(const fee of [.008,.025]){
   const reference=F.replay(require("./v18_kavis_dayaniqlilik"),prices,fee),
    alert=D.run(prices,fee,"alert"),risk=D.run(prices,fee,"soft_penalty");
   if(Math.abs(alert.capital-reference.capital)>1e-4)
    throw Error("R2_OOD_ALERT_V18_INVARIANCE_FAIL");
   worlds.push({kind,seed,fee,reference,alert,risk,
     advantage:risk.capital-alert.capital});
  }
 }
 return {contract:"POST_FREEZE_NEW_FICTIONAL_WORLDS_NOT_REAL_HOLDOUT",
   worlds:worlds.length,
   summary:{better:worlds.filter(w=>w.advantage>1e-5).length,
    worse:worlds.filter(w=>w.advantage< -1e-5).length,
    ties:worlds.filter(w=>Math.abs(w.advantage)<=1e-5).length,
    meanAlert:mean(worlds.map(w=>w.alert.capital)),
    meanRisk:mean(worlds.map(w=>w.risk.capital)),
    p95RiskDD:[...worlds].map(w=>w.risk.mdd).sort((a,b)=>a-b)[44],
    riskSpecialistOverrides:worlds.reduce((s,w)=>s+w.risk.overrideCount,0),
    softVetoes:worlds.reduce((s,w)=>s+w.risk.softEntryVetoes,0),
    worstRiskCapital:Math.min(...worlds.map(w=>w.risk.capital))},
   byKind:families.map(k=>{
    const r=worlds.filter(w=>w.kind===k);
    return {kind:k,meanBaseline:mean(r.map(w=>w.alert.capital)),
      meanR2:mean(r.map(w=>w.risk.capital)),
      wins:r.filter(w=>w.advantage>1e-5).length,
      losses:r.filter(w=>w.advantage< -1e-5).length};
   }),full:worlds};
}
if(require.main===module)console.log(JSON.stringify(evaluate(),null,2));
module.exports={series,evaluate};
