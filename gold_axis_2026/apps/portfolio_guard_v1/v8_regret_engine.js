"use strict";
/**
 * V8 research-only: as-of online conditional forecasts + delayed opportunity-regret
 * feedback. Not a live bank engine. Not a blindly validated trading system.
 */
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const {loadRows}=require("./adaptive_v7_app");
const COST=.008,HOURLY=3600000;
const SOURCE={
  history:{file:"RECOVERY_HIST_3H_2023_2025_V1.csv",sha:"a588b6745f893fcafc935fa486328a6349caa658"},
  cmeOld:{file:"CME_3H_ASOF_2023_2024_V6.csv",sha:"e8787df9823b412e31546c784f1e95a762126697"},
  cmeNew:{file:"CME_3H_ASOF_2025_2026_V6.csv",sha:"2a2b42d0140fac3aea197013c443cd268db92b6d"}
};
const clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
function parse(raw){
 const lines=raw.trim().split(/\r?\n/),keys=lines.shift().split(",");
 return lines.map(s=>{const values=s.replace(/\r$/,"").split(",");
  if(values.length!==keys.length)throw Error("BAD_CSV_ROW");
  return Object.fromEntries(keys.map((key,i)=>[key,key==="tt"?values[i]:values[i]===""?null:Number(values[i])]));});
}
function blobHash(raw){return crypto.createHash("sha1").update(Buffer.from("blob "+raw.length+"\0")).update(raw).digest("hex");}
function loadPinned(spec){
 const raw=fs.readFileSync(path.join(__dirname,"data",spec.file));
 const checked=blobHash(raw)===spec.sha?raw:Buffer.from(raw.toString("utf8").replace(/\r\n/g,"\n"));
 if(blobHash(checked)!==spec.sha)throw Error("V8_PINNED_DATA_MISMATCH:"+spec.file);
 return parse(checked.toString("utf8"));
}
function loadFullRows(){
 const hist=loadPinned(SOURCE.history),cme=[...loadPinned(SOURCE.cmeOld),...loadPinned(SOURCE.cmeNew)];
 const byCME=new Map(cme.map(x=>[x.tt,x]));
 // verified 2025-2026 has identical XAU proxy price with historic 2025
 const recent=loadRows();const histMap=new Map(hist.map(x=>[x.tt,x]));
 let checked=0;
 for(const r of recent){
  if(!r.tt.startsWith("2025-"))continue;
  const h=histMap.get(r.tt);
  if(h){checked++;if(h.p!==r.p||h.c!==r.c)throw Error("CROSS_SOURCE_PRICE_MISMATCH:"+r.tt);}
 }
 if(checked<1800)throw Error("INSUFFICIENT_SOURCE_OVERLAP");
 const early=hist.filter(x=>x.tt<"2025-01-01").map(r=>({
  tt:r.tt,p:r.p,c:r.c,r4:r.r4,r1:r.r92,r3:r.r276,rv:r.rv,
  ds:r.ds,eff:r.eff,loc:r.loc,dd:r.dd4,
  nq1:null,nq6:byCME.get(r.tt)?.nq6??null,zn1:null
 }));
 const union=[...early,...recent].map(x=>({...x,ts:Date.parse(x.tt)})).sort((a,b)=>a.ts-b.ts);
 for(let i=0;i<union.length;i++){
  if(!Number.isFinite(union[i].ts)||union[i].p<=0||!Number.isFinite(union[i].p)||
    !Number.isFinite(union[i].c))throw Error("INVALID_ROW");
  if(i&&union[i].ts<=union[i-1].ts)throw Error("OUT_OF_ORDER_DUPLICATE_TIMESTAMP");
 }
 return {rows:union,data:{historicBefore2025:early.length,after2025:recent.length,
   overlapVerified:checked,total:union.length,sha:SOURCE}};
}
function scoreFeature(row){
 const z=(v,scale,center=0)=>v==null||!Number.isFinite(v)?0:clamp((v-center)/scale,-2.5,2.5);
 const base=[1,z(row.r4,2),z(row.r1,6),z(row.r3,9),
   z(row.rv,1.5),z(row.ds,.5,.5),z(row.eff,.5,.5),z(row.loc,.5,.5),z(row.dd,3)];
 const cross=[...base,z(row.nq6,2.5),z(row.zn1,.3)];
 return {price:base,cross};
}
function marketRegime(r){
 if(r.r4!=null&&r.r4<=-2&&r.rv!=null&&r.rv>=1.1)return "SHOCK";
 if(r.r1!=null&&r.r3!=null&&r.r1>1.2&&r.r3>1.2)return "UP";
 if(r.r1!=null&&r.r3!=null&&r.r1< -1.2&&r.r3< -1.2)return "DOWN";
 return "RANGE";
}
function createExpert(size){
 return {w:Array(size).fill(0),n:0,loss:16,avg:0};
}
function learnOne(e,x,y,p){
 const err=clamp(y-p,-25,25),lr=1.5/(12+Math.sqrt(e.n+1)),den=1+x.reduce((s,v)=>s+v*v,0);
 e.w=e.w.map((w,i)=>clamp(w*.9998+lr*err*x[i]/den,-10,10));
 e.loss=e.n===0?err*err:.97*e.loss+.03*err*err;
 e.n++;e.avg=.97*e.avg+.03*y;
}
function newHorizon(){
 return {price:createExpert(9),cross:createExpert(11),
   conditional:Object.fromEntries(["UP","DOWN","SHOCK","RANGE"].map(r=>[r,{n:0,mean:0,mse:16,missedUp:0,badBuy:0,missedDown:0}])),
   n:0};
}
function forecast(model,feat,regime){
 const dot=(w,x)=>w.reduce((s,v,i)=>s+v*x[i],0);
 const a=clamp(dot(model.price.w,feat.price),-18,18);
 const b=clamp(dot(model.cross.w,feat.cross),-18,18);
 let w1=Math.exp(-clamp(model.price.loss/15,0,20)),w2=Math.exp(-clamp(model.cross.loss/15,0,20));
 const combine=(w1*a+w2*b)/(w1+w2);
 const m=model.conditional[regime];
 const trusted=m.n>=10;
 const mu=trusted?.6*combine+.4*m.mean:combine;
 const sigma=Math.sqrt(clamp((model.price.loss+model.cross.loss)/2,0.25,225));
 return {mu,prior:combine,experts:{price:a,cross:b},sigma,regime,
   mN:m.n,missedUp:m.missedUp,badBuy:m.badBuy,missedDown:m.missedDown};
}
function replay(rows,opts={}){
 const start=Date.parse(opts.start||"2026-02-02T06:00:00Z");
 const stop=Date.parse(opts.stop||"2026-09-30T12:00:00Z");
 const initial=opts.initial??119.753917;
 const mode=opts.mode||"regret";
 const freeze=opts.freeze_at?Date.parse(opts.freeze_at):Infinity;
 if(!["regret","no_regret","no_shock","frozen"].includes(mode))throw Error("BAD_V8_MODE");
 const Hs={short:96,long:336},models={short:newHorizon(),long:newHorizon()};
 let cash=initial,ounces=0,lastSale=-Infinity,prev=null;
 let pending=[],trades=[],decisions=[],errors=[],samples=[],learningLedger=[],matureCount={short:0,long:0},missedDue=0,lastCheckpoint=null;
 const stats={missed_up:0,false_buy:0,missed_down:0,early_sell:0,bad_reentry:0};
 const priced=rows.map(x=>({...x,ts:Number.isFinite(x.ts)?x.ts:Date.parse(x.tt)}));
 function matured(now,r){
  const future=[];
  for(const task of pending){
   if(task.due>now){future.push(task);continue;}
   // first observed 3-hour close AT OR AFTER the promised horizon; missing weekends cannot be future-filled.
   const delta=(now-task.due)/HOURLY;
   if(delta>78){missedDue++;continue;}
   const change=clamp(100*(r.c/task.price-1),-25,25);
   const model=models[task.h],bucket=model.conditional[task.regime];
   const pred=task.pred;
   const grossLongNet=100*((1-COST)**2*r.c/task.price-1);
   let errorType="NONE",costOpportunity=0;
   if(task.position==="CASH"&&grossLongNet>0){
    errorType="MISSED_UP";costOpportunity=grossLongNet;
    bucket.missedUp=.9*bucket.missedUp+.1*clamp(grossLongNet,0,12);
    stats.missed_up++;
   }else if(task.position==="GOLD"&&change<0){
    errorType="MISSED_DOWN";costOpportunity=-change;
    bucket.missedDown=.9*bucket.missedDown+.1*clamp(-change,0,12);
    stats.missed_down++;
   }else if(task.position==="GOLD"&&change>0&&task.entryAgeHours<72){
    errorType="HOLD_WIN"; // not a mistake
   }else if(task.position==="CASH"&&change<0){
    errorType="AVOIDED_DOWN";
   }
   if(task.position==="GOLD"&&grossLongNet<0){
      bucket.badBuy=.9*bucket.badBuy+.1*clamp(-grossLongNet,0,12);
      if(task.entryAgeHours<336){stats.false_buy++;if(task.entryAgeHours<72)stats.bad_reentry++;}
   }
   if(task.wasRecentSell&&grossLongNet>0){stats.early_sell++;}
   errors.push({origin:task.origin,asof_matured:r.tt,expectedHorizon:task.h,
     actualHours:(now-task.originTime)/HOURLY,regime:task.regime,positionAtOrigin:task.position,
     outcomePct:change,costedBuyReturnPct:grossLongNet,
     forecastAtOrigin:pred.mu,errorType,opportunityPct:costOpportunity,updated:now<freeze});
   samples.push({origin:task.origin,h:task.h,predicted:pred.mu,actual:change,regime:task.regime});
   if(now<freeze){
      learnOne(model.price,task.features.price,change,pred.experts.price);
      learnOne(model.cross,task.features.cross,change,pred.experts.cross);
      bucket.mean=bucket.n===0?change:.97*bucket.mean+.03*change;
      bucket.mse=bucket.n===0?Math.pow(change-pred.mu,2):
        .96*bucket.mse+.04*Math.pow(change-pred.mu,2);
      bucket.n++;model.n++;matureCount[task.h]++;
      learningLedger.push({at:r.tt,from:task.origin,h:task.h,
        actual:change,predicted:pred.mu,regime:task.regime,
        err:errorType,updated:true});
   }
  }
  pending=future;
 }
 for(const r of priced){
   const t=r.ts;
   if(t>stop)break;
   if(t<priced[0].ts)throw Error("BAD_TS");
   matured(t,r);
   const x=scoreFeature(r),regime=marketRegime(r);
   const ps=forecast(models.short,x,regime),pl=forecast(models.long,x,regime);
   const h=new Date(t).getUTCHours();
   if(h===6&&r.p>0){
      for(const horizon of ["short","long"])pending.push({
       h:horizon,origin:r.tt,originTime:t,due:t+Hs[horizon]*HOURLY,
       price:r.p,features:x,regime,pred:horizon==="short"?ps:pl,
       position:t>=start?(ounces?"GOLD":"CASH"):"WARMUP",
       wasRecentSell: t-lastSale<14*24*HOURLY,entryAgeHours:ounces?(t-(prev?.lastBuy??t))/HOURLY:Infinity
      });
   }
   if(t<start||![6,9,12].includes(h))continue;
   const bothReady=models.long.n>=90&&models.short.n>=90;
   const entryCost=100*(1/(1-COST)**2-1);
   // Conditional error feedback is OOS for each matured label; never current-month outcome.
   const mom=models.long.conditional[regime];
   const buyBias=mode==="no_regret"||mode==="frozen"?0:
      clamp(.25*(mom.missedUp-mom.badBuy),-1.5,1.5);
   const buyGate=entryCost+Math.min(1.5,.08*pl.sigma);
   const expectedLong=pl.mu+buyBias;
   const risk=models.short.conditional[regime];
   const sellBias=mode==="no_regret"||mode==="frozen"?0:
      clamp(.12*risk.missedDown,0,1.2);
   const sellGate=-entryCost-Math.min(1.5,.08*ps.sigma)+sellBias;
   const stress=(r.r4!=null&&r.r4<=-1&&r.nq6!=null&&r.nq6<=-1);
   const slowBreak=(r.r1!=null&&r.r3!=null&&r.r1< -4&&r.r3< -3);
   let act="HOLD",reason="NO_CONFIDENT_EDGE";
   if(bothReady&&!ounces&&t-lastSale>=72*HOURLY&&
       (expectedLong>buyGate||(mode!=="no_regret"&&
           regime==="UP"&&pl.mu>0&&r.r1>3&&r.r3>1&&mom.missedUp>1))){
      ounces=cash*(1-COST)/r.p;cash=0;act="BUY";reason="ONLINE_OPPORTUNITY_REGRET";
      prev={...prev,lastBuy:t};
   }else if(ounces&&
      (ps.mu<sellGate||(mode!=="no_shock"&&(stress||slowBreak)))){
      cash=ounces*r.p*(1-COST);ounces=0;lastSale=t;act="SELL";
      reason=stress?"XAU_NQ_STRESS":slowBreak?"SLOW_DOWNSIDE_BREAK":"ONLINE_RISK";
   }
   const nav=cash+ounces*r.c*(1-COST);
   const d={at:r.tt,regime,action:act,reason,nav,cash,position:ounces>0?"GOLD":"CASH",
     muLong:pl.mu,muShort:ps.mu,buyGate,sellGate,buyBias,sellBias,trainedLong:models.long.n,
     trainedShort:models.short.n};
   decisions.push(d);
   if(act!=="HOLD")trades.push({...d,mid:r.p});
   lastCheckpoint=r;prev={...prev,lastDecision:t};
 }
 const final=cash+ounces*(lastCheckpoint?.c||0)*(1-COST);
 let months={};for(const d of decisions){months[new Date(Date.parse(d.at)+3*HOURLY).toISOString().slice(0,7)]={final:d.nav,position:d.position,lastAsOf:d.at};}
 function metrics(prefix){
  const data=samples.filter(d=>d.origin.startsWith(prefix)&&Date.parse(d.origin)>=start);
  return Object.fromEntries(["short","long"].map(h=>{
    const a=data.filter(x=>x.h===h),n=a.length;
    return [h,{n,mae:n?a.reduce((s,x)=>s+Math.abs(x.actual-x.predicted),0)/n:null,
       directionCorrect:a.filter(x=>(x.predicted>=0)===(x.actual>=0)).length}];
  }));
 }
 return {config:{version:"V8_ONLINE_REGRET_EXPERIMENT_20261015",mode,feeEachSide:COST,first:start,last:stop,
    training:"matured96h_and336h_daily_09TR",base:"2023-2024 history plus 2025-2026 asof"},
  initial,final,gainPct:100*(final/initial-1),trades,months,learning:{
    matureCount,missedDue,types:stats,examples:errors.filter(e=>e.origin>="2026-02").slice(0,10),
    events:errors.length,updated:learningLedger.length,models:Object.fromEntries(
    Object.entries(models).map(([key,v])=>[key,{n:v.n,priceLoss:v.price.loss,crossLoss:v.cross.loss,
     bucket:Object.fromEntries(Object.entries(v.conditional).map(([k,s])=>[k,{n:s.n,mean:s.mean,missedUp:s.missedUp,badBuy:s.badBuy,missedDown:s.missedDown}]))}]))
  },metric:metrics(new Date(start).getUTCFullYear().toString()),
   decisions:opts.includeDecisions?decisions:undefined,errors:opts.includeErrors?errors:undefined,
   accepted:false,blind:false,realBankAskBidIncluded:false};
}
module.exports={SOURCE,COST,loadFullRows,scoreFeature,marketRegime,replay};
