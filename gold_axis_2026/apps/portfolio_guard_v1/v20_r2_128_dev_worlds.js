"use strict";
const R2=require("./v20_atlas_r2_shadow");
const Core=require("./v18_kavis_dayaniqlilik");
const F=require("./v18_128_adversarial_scenarios");
const t0=Date.parse("2020-01-01T00:00:00Z"),D=86400000,H=3600000;
const iso=(i,h)=>new Date(t0+i*D+h*H).toISOString();
function run(p,fee,mode){
 const s=R2.create({core:{feePerSide:fee},maxDrawdownPct:15,
   riskMode:mode});
 let maxRiskProof=-1e3,acceptedQuotes=0;
 for(let i=0;i<p.length;i++){
  const ob={asof:iso(i,6),featureAvailableAt:iso(i,6),
    position:s.inner.portfolio.position,market:F.features(p,i),
    bankFeeQuote:{feePerSide:fee,availableAt:iso(i,6)}};
  const advice=R2.signal(s,ob);
  const result=R2.quote(s,{at:iso(i,9),price:p[i],
    bankFeePerSide:fee,isBankCheckpoint:true});
  if(!result.fill)throw Error("R2_UNEXPECTED_MISSING_QUOTE");
  if(result.ordersSent!==0||advice.ordersSent!==0)throw Error("R2_LIVE_ORDER");
  acceptedQuotes++;
  if(result.shadow.evidence.ready)
    maxRiskProof=Math.max(maxRiskProof,result.shadow.evidence.lower);
 }
 const port=s.inner.portfolio;
 return {capital:port.nav,mdd:port.maxDrawdownPct,
   trades:port.trades,
   baseShadowNAV:s.shadow.base.nav,
   riskShadowNAV:s.shadow.risk.nav,
   baseShadowTrades:s.shadow.base.trades,
   riskShadowTrades:s.shadow.risk.trades,
   evidenceCount:s.shadow.relativeReturns.length,
   maxRiskProof,overrideCount:s.audit.specialistOverrides,
   softEntryVetoes:s.audit.softEntryVetoes,
   softExits:s.audit.softExitDecisions,
   warningCount:s.audit.warnings,
   acceptedQuotes};
}
function pct(x,p){
 const q=[...x].sort((a,b)=>a-b);
 return q[Math.floor((q.length-1)*p)];
}
function summarize(a,key){
 const b=a.map(z=>z[key]);
 return {meanCapital:b.reduce((u,v)=>u+v.capital,0)/b.length,
   minCapital:Math.min(...b.map(x=>x.capital)),
   medianMDD:pct(b.map(x=>x.mdd),.5),
   p95MDD:pct(b.map(x=>x.mdd),.95),
   adviserOverrides:b.reduce((u,v)=>u+v.overrideCount,0),
   softVetoes:b.reduce((u,v)=>u+v.softEntryVetoes,0),
   warningCount:b.reduce((u,v)=>u+v.warningCount,0),
   riskShadowBetter:b.filter(x=>x.riskShadowNAV>x.baseShadowNAV).length};
}
function main(){
 const regimes=["slow_ramp","gap_crash","false_break","flat_trap",
   "whipsaw","random_walk","fat_tails","regime_flip"];
 const rows=[];
 for(let j=0;j<regimes.length;j++)for(let k=1;k<=8;k++){
  const mode=regimes[j],seed=8000+97*k+j*307,p=F.series(mode,seed);
  for(const fee of [.008,.025]){
   const v18=F.replay(Core,p,fee);
   const alert=run(p,fee,"alert"),soft=run(p,fee,"soft_penalty");
   if(Math.abs(alert.capital-v18.capital)>.0001)
     throw Error("R2_ALERT_MUST_EQUAL_V18");
   rows.push({mode,seed,fee,reference:v18.capital,alert,soft,
    delta:soft.capital-alert.capital});
  }
 }
 const limit=rows.filter(x=>x.fee===.008&&
   ["gap_crash","whipsaw","fat_tails"].includes(x.mode));
 return {contract:"EXPOSED_128_ONLY_NOT_BLIND",rows:rows.length,
  summary:{alert:summarize(rows,"alert"),soft:summarize(rows,"soft"),
   wins:rows.filter(z=>z.delta>0).length,
   losses:rows.filter(z=>z.delta<0).length,
   ties:rows.filter(z=>z.delta===0).length},
  user15Subset:{rows:limit.length,
   alert:summarize(limit,"alert"),soft:summarize(limit,"soft")},
  lowQuality:rows.filter(x=>x.delta<-.01).sort((a,b)=>a.delta-b.delta)
    .slice(0,16).map(x=>({mode:x.mode,seed:x.seed,fee:x.fee,
      alert:x.alert.capital,soft:x.soft.capital,
      penaltyVetoes:x.soft.softEntryVetoes})),
  allRows:rows};
}
if(require.main===module)console.log(JSON.stringify(main(),null,2));
module.exports={run,main};
