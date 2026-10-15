"use strict";
/* V6: frozen cross-market hourly AS-OF diagnostics, NEVER autonomous trading.
 * 2023-2026 already inspected: results are retrospective, not blind OOS.
 */
const fs=require("node:fs"),path=require("node:path");
const core=require("./engine"),v3=require("./recovery_v3"),feb=require("./monthly_runner"),more=require("./v4_forward_review");
const ROOT=path.resolve(__dirname,"../../..");
const VERSION="V6_CME_CROSS_ASSET_DOWNSIDE_DIAGNOSTIC_20261015";
const PINS=[
 ["2023","4ebf1c8dbbbac361bc345707fd46724d19214fb7"],
 ["2024","4080780e93cccabfc6c4271c4b10cdda93cbf76d"],
 ["2025","2c308b79a2ba26de611aa22e3ca2a50bdbf2cd8c"],
 ["2026","7da219b4f5d6b81a7a618d38e4dc1af3e662a7f8"]
];
const XAU=["r4","r92","r276","rv","ds"],OTHER=["nq1","nq6","zn1","zn6","cl1","cl6"],ALL=XAU.concat(OTHER);
const HOUR=3600000,DAY=24*HOUR,EMBARGO=96*HOUR;
const sigmoid=x=>1/(1+Math.exp(-Math.max(-30,Math.min(30,x))));
function macroRows(){
 const out=[];
 for(const [year,blob] of PINS){
  const spec={path:"gold_axis_2026/apps/portfolio_guard_v1/data/V6_CME_NQ_ZN_CL_1H_ASOF_"+year+".csv",blob};
  const source=core.decodePinnedSource(spec,fs.readFileSync(path.join(ROOT,spec.path)));
  const rows=source.rows.map(o=>{
   const r={tt:o.tt,time:Date.parse(o.tt)};
   for(const k of OTHER)r[k]=o[k]===""?null:Number(o[k]);
   if(!Number.isFinite(r.time)||r.tt.slice(0,4)!==year)throw Error("INVALID_CME_SOURCE_TIME");
   return r;
  });
  if(rows.some((r,i)=>i&&r.time<=rows[i-1].time))throw Error("CME_TIME_UNSORTED");
  out.push(...rows);
 }
 if(out.length!==2904)throw Error("CME_FROZEN_COUNT_CHANGED");
 return out;
}
function priceRows(){
 const a=v3.loadHistorical().filter(r=>r.tt>="2023-01-01");
 const jan=core.loadFrozen().rows.filter(r=>r.tt>="2026-01-01"&&new Date(r.time).getUTCMinutes()===0&&new Date(r.time).getUTCHours()%3===0);
 const febRows=more.loadFebruary3h();
 const later=more.loadHoldout().rows.filter(r=>r.time<Date.parse("2026-09-30T21:00:00.000Z"));
 const all=[...a,...jan,...febRows,...later];
 if(all.some((r,i)=>!Number.isFinite(r.time)||i&&r.time<=all[i-1].time))
  throw Error("UNSORTED_XAU_SOURCE");
 return all;
}
function labeledDays(price,macro){
 const map=new Map(macro.map(r=>[r.tt,r])),out=[];
 const missing={macro:0,no24hCoverage:0,price:0};let eligibleDays=0;
 for(let i=0;i<price.length;i++){
  const r=price[i];
  if(new Date(r.time).getUTCHours()!==6)continue; // Turkey 09:00 daily
  eligibleDays++;
  const m=map.get(r.tt);
  if(!m||OTHER.some(k=>!Number.isFinite(m[k]))){missing.macro++;continue;}
  if(XAU.some(k=>!Number.isFinite(r[k]))){missing.price++;continue;}
  const future=[];
  for(let j=i+1;j<price.length&&price[j].time<=r.time+DAY;j++)future.push(price[j]);
  if(future.length<5||future.at(-1).time<r.time+21*HOUR){missing.no24hCoverage++;continue;}
  const min=Math.min(...future.map(x=>x.c));
  out.push({tt:r.tt,time:r.time,year:Number(r.tt.slice(0,4)),
   y:min<=r.c*.98?1:0,retMinPct:100*(min/r.c-1),
   features:Object.fromEntries(ALL.map(k=>[k,k in r?r[k]:m[k]])),
   labelKnownAt:r.time+DAY,economicMechanism:"UNRESOLVED"});
 }
 return {rows:out,eligibleDays,missing};
}
function fit(training,names){
 if(training.length<50)throw Error("INSUFFICIENT_TRAINING");
 const stat=names.map(k=>{
  const col=training.map(x=>x.features[k]);
  const mean=col.reduce((a,b)=>a+b,0)/col.length;
  const std=Math.sqrt(col.reduce((a,b)=>a+(b-mean)**2,0)/col.length);
  return {key:k,mean,std:Math.max(1e-5,std)};
 });
 const pos=training.reduce((s,r)=>s+r.y,0),prior=(pos+1)/(training.length+2);
 let bias=Math.log(prior/(1-prior)),w=names.map(()=>0);
 for(let e=0;e<400;e++){
  let gb=0;const gw=w.map(()=>0);
  for(const r of training){
   const x=stat.map(f=>Math.max(-4,Math.min(4,(r.features[f.key]-f.mean)/f.std)));
   const error=sigmoid(bias+x.reduce((v,z,i)=>v+z*w[i],0))-r.y;
   gb+=error;for(let i=0;i<x.length;i++)gw[i]+=error*x[i];
  }
  bias-=.03*gb/training.length;
  w=w.map((v,i)=>v-.03*(gw[i]/training.length+.1*v));
 }
 return {prior,bias,w,stat,trainingCount:training.length,trainingPositives:pos};
}
function predict(model,r){
 let z=model.bias;
 for(let i=0;i<model.stat.length;i++){
  const f=model.stat[i],x=Math.max(-4,Math.min(4,(r.features[f.key]-f.mean)/f.std));
  z+=model.w[i]*x;
 }
 return sigmoid(z);
}
function score(rows,predictions){
 let b=0,loss=0,positives=0;
 for(let i=0;i<rows.length;i++){
  const y=rows[i].y,p=Math.max(1e-8,Math.min(1-1e-8,predictions[i]));
  b+=(p-y)**2;loss-=y*Math.log(p)+(1-y)*Math.log(1-p);positives+=y;
 }
 return {n:rows.length,positive:positives,negative:rows.length-positives,
  brier:b/rows.length,logLoss:loss/rows.length};
}
function annualTest(samples){
 return [2024,2025,2026].map(year=>{
  const start=Date.parse(year+"-01-01T00:00:00Z"),end=Date.parse((year+1)+"-01-01T00:00:00Z");
  const train=samples.filter(x=>x.labelKnownAt<start-EMBARGO);
  const test=samples.filter(x=>x.time>=start&&x.time<end);
  if(test.length<30||train.length<50)return {year,status:"INSUFFICIENT_DATA",trainN:train.length,testN:test.length};
  if(train.some(x=>x.labelKnownAt>=start-EMBARGO))throw Error("FUTURE_TRAIN_LABEL");
  const a=fit(train,XAU),b=fit(train,ALL);
  const baseline=score(test,test.map(()=>a.prior));
  const xau=score(test,test.map(x=>predict(a,x)));
  const macro=score(test,test.map(x=>predict(b,x)));
  return {year,status:"RETROSPECTIVE_CHRONOLOGICAL_TEST",
   training:{n:train.length,positive:a.trainingPositives,lastSeen:train.at(-1).tt,embargoHours:96},
   test:{n:test.length,positive:baseline.positive,negative:baseline.negative,
    first:test[0].tt,last:test.at(-1).tt,
    enoughIndependentDays:test.length>=100&&baseline.positive>=10&&baseline.negative>=10},
   baseline,xauOnly:xau,xauPlusCross:macro,
   crossBeatsPrice:{brier:macro.brier<xau.brier,logLoss:macro.logLoss<xau.logLoss},
   plusBeatsUnconditional:{brier:macro.brier<baseline.brier,logLoss:macro.logLoss<baseline.logLoss},
   fitted:{xauWeights:a.w,combinedWeights:b.w,features:ALL},
   firstprintVerified:false,bankSpreadIncluded:false};
 });
}
function runAudit(){
 const m=macroRows(),r=priceRows(),prepared=labeledDays(r,m);
 const annual=annualTest(prepared.rows);
 const tested=annual.filter(x=>x.year===2024||x.year===2025);
 const evidence=tested.every(x=>x.test?.enoughIndependentDays&&
  x.crossBeatsPrice.brier&&x.crossBeatsPrice.logLoss&&
  x.plusBeatsUnconditional.brier&&x.plusBeatsUnconditional.logLoss);
 return {version:VERSION,status:"READ_ONLY_NO_AUTOTRADING",
  source:{CME:PINS.map(([year,gitBlob])=>({year,gitBlob})),
   releaseTimestampPolicy:"ONLY_H1_BARS_COMPLETED_BY_DECISION_UTC",
   OLAY02_EconomicDNA:"UNVERIFIED_FIRST_PRINT",
   r71_r72_macroSurprise:"EXCLUDED_NO_VINTAGE_VERIFICATION",
   SI_futures:"EXCLUDED_SPARSE_3H_COVERAGE"},
  predictionTarget:"XAU_ANY_3H_CLOSE_DOWN_2PCT_WITHIN_NEXT_24H",
  coverage:{all09TRPriceDays:prepared.eligibleDays,completePairs:prepared.rows.length,
   exclusions:prepared.missing,perYear:prepared.rows.reduce((a,x)=>(a[x.year]=(a[x.year]||0)+1,a),{})},
  annual,acceptance:{incrementalEvidenceOn2024And2025:evidence,tradeAuthorized:false,
    verdict:evidence?"DIAGNOSTIC_ONLY_NEEDS_PROSPECTIVE_CONFIRMATION":
    "REJECT_UNPROVEN_CROSS_ASSET_IMPROVEMENT",
    economicMechanismVerified:false,prospectiveBlind:false,
    bidAskBankValidated:false},
  existingV1ToV5Frozen:true};
}
module.exports={VERSION,PINS,XAU,OTHER,ALL,macroRows,priceRows,labeledDays,fit,predict,score,annualTest,runAudit};
