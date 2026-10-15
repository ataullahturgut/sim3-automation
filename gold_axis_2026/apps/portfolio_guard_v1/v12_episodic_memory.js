"use strict";
/**
 * Original V12: REHBER — Rejim Evresi Hafızası, Benzetim ve Eylem Revizyonu.
 * Memory-based conditional forecaster, NOT ANN and not a post-2026 optimized rule set.
 *
 * Three independent "lenses" match genuinely similar prior state vectors.
 * Every neighbor is a fully matured past 14-day cash→gold→cash episode.
 * A 14-calendar-day-block dedup prevents overlapping daily outcomes from
 * masquerading as independent historical episodes.
 * Reliability weights update from matured, past forecasts (online expert regret).
 */
const HR=3600000,DAY=24*HR,FEE=.008;
const SCALES=[3,7,10,2,.6,.7,.7,5,4,.4,1,1,5,12];
const CENTERS=[0,0,0,0,.5,.5,.5,0,0,0,0,0,0,0];
const LENSES=Object.freeze({
 TREND:[0,1,2,12,13],
 STRESS:[0,3,4,7,8,9,10,11],
 STRUCTURE:[0,1,4,5,6,7,12]
});
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function phi(features){
 if(!Array.isArray(features)||features.length!==14)throw Error("REHBER_FEATURE_CONTRACT");
 return features.map((v,i)=>{
  if(!Number.isFinite(v))throw Error("REHBER_NONFINITE_ASOF_FEATURE");
  return clamp((v-CENTERS[i])/SCALES[i],-3,3);
 });
}
function blockOf(t){return Math.floor(t/(14*DAY));}
function distanceSq(a,b,dimensions){
 let sum=0;
 for(const j of dimensions){
  const d=a[j]-b[j];sum+=d*d;
 }
 return sum/dimensions.length;
}
function weightedQuantile(samples,q){
 if(!samples.length)return null;
 const sorted=[...samples].sort((a,b)=>a.y-b.y);
 const total=sorted.reduce((s,x)=>s+x.w,0);
 let sum=0;
 for(const x of sorted){sum+=x.w;if(sum>=total*q)return x.y;}
 return sorted.at(-1).y;
}
function expertForecast(name,features,memory,now,limit=32){
 const dims=LENSES[name],chosen=new Map();
 for(const ep of memory){
  if(ep.exit14Ts>=now)throw Error("FUTURE_EPISODE_IN_MEMORY");
  const t=ep.ts;
  const dist=distanceSq(features,ep.vector,dims);
  const block=blockOf(t),prior=chosen.get(block);
  if(!prior||dist<prior.dist)chosen.set(block,{dist,ep});
 }
 const nearest=[...chosen.values()].sort((a,b)=>a.dist-b.dist).slice(0,limit);
 if(nearest.length<6)return {name,ready:false,episodes:nearest.length};
 let total=0,weights=[],nEffNum=0;
 for(const {dist,ep} of nearest){
  // Independent episodes within 14d blocks, kernel similarity and slow
  // chronology discount. No later-than-now label contributes.
  const decay=Math.exp(-Math.max(0,now-ep.exit14Ts)/(3*365*DAY));
  const w=Math.exp(-1.8*dist)*decay;
  weights.push({w,dist,ep});total+=w;nEffNum+=w*w;
 }
 if(total<1e-6)return{name,ready:false,episodes:0};
 const nEffective=total*total/nEffNum;
 const norm=weights.map(x=>({w:x.w/total,ep:x.ep,dist:x.dist}));
 const avg=k=>norm.reduce((s,x)=>s+x.w*x.ep.y[k],0);
 const obs=norm.map(x=>({w:x.w,y:x.ep.y[1]}));
 const p=obs.reduce((s,x)=>s+x.w*(x.y>0?1:0),0);
 const quantile20=weightedQuantile(obs,.2);
 const dispersion=Math.sqrt(norm.reduce((s,x)=>s+x.w*(x.ep.y[1]-avg(1))**2,0));
 return {name,ready:true,episodes:nearest.length,nEffective,
  net4:avg(0),net14:avg(1),pNet14Positive:p,q20:quantile20,
  dispersion,analogs:nearest.slice(0,3).map(n=>({
   date:n.ep.at,distance:Number(n.dist.toFixed(4)),
   realizedNet14:Number(n.ep.y[1].toFixed(3))
  }))};
}
function create(){
 return {memory:[],loss:Object.fromEntries(Object.keys(LENSES).map(k=>[k,{n:0,emaSquared:16}])),
   realizedFeedback:[],maturedEpisodeCount:0};
}
function forecast(model,features,time){
 const now=typeof time==="number"?time:Date.parse(time),vec=phi(features);
 const estimates=Object.fromEntries(Object.keys(LENSES).map(k=>
   [k,expertForecast(k,vec,model.memory,now)]));
 const valid=Object.values(estimates).filter(x=>x.ready);
 if(!valid.length)return {ready:false,reasons:["INSUFFICIENT_MATURED_ANALOG_EPISODES"],
   experts:estimates,nEffective:0};
 // Exponentially discount specialists that predicted earlier completed episodes
 // poorly; predicted labels only enter after their full 14d exit.
 const scores=valid.map(e=>Math.exp(-Math.min(30,model.loss[e.name].emaSquared/24)));
 const sum=scores.reduce((a,b)=>a+b,0);
 const weight=Object.fromEntries(valid.map((e,i)=>[e.name,scores[i]/sum]));
 const wavg=k=>valid.reduce((s,e)=>s+weight[e.name]*e[k],0);
 const nEff=Math.min(...valid.map(e=>e.nEffective));
 const expectedNet14=wavg("net14"),expectedNet4=wavg("net4"),p=wavg("pNet14Positive");
 const variance=valid.reduce((s,e)=>s+weight[e.name]*(
   e.dispersion**2+(e.net14-expectedNet14)**2
 ),0);
 const sigma=Math.sqrt(variance);
 return {ready:true,net14:expectedNet14,net4:expectedNet4,
   pProfit:p,tail20:wavg("q20"),sigma,nEffective:nEff,
   uncertaintyPct:sigma/Math.sqrt(Math.max(1,nEff)),
   experts:estimates,weights:weight,modelFeedback:model.realizedFeedback.length};
}
function appendMatured(model,ep,now){
 if(!(ep.exit14Ts<now))throw Error("REHBER_FUTURE_LABEL_REJECTED");
 if(ep.vector==null)ep={...ep,vector:phi(ep.features)};
 model.memory.push(ep);model.maturedEpisodeCount++;
}
function feedback(model,origin,pred,realized,when){
 if(origin.exit14Ts>=when)throw Error("REHBER_FEEDBACK_NOT_MATURE");
 const completed={origin:origin.at,knownAt:new Date(when).toISOString(),
   realized14:realized[1],predicted14:pred.net14};
 if(pred.ready)for(const lens of Object.keys(LENSES)){
  const ep=pred.experts[lens];
  if(!ep?.ready)continue;
  const error=ep.net14-realized[1],entry=model.loss[lens];
  entry.emaSquared=entry.n===0?error*error:
    .90*entry.emaSquared+.10*error*error;
  entry.n++;
  completed[lens+"Error"]=error;
 }
 model.realizedFeedback.push(completed);
}
module.exports={SCALES,CENTERS,LENSES,HR,DAY,FEE,phi,blockOf,
 distanceSq,weightedQuantile,expertForecast,create,forecast,appendMatured,feedback};
