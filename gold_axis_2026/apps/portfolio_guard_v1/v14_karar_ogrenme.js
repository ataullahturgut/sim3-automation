"use strict";
/**
 * V14 KOR: counterfactual GOLD/CASH log-wealth action learner.
 * Research only. Trains ONLY on strictly matured 7d / 28d
 * next-checkpoint outcomes. Not a trained LSTM or a proven novel theorem.
 */
const FEE=.008,HR=3600000,DAY=24*HR;
const K=10, MEM=5, HORIZONS=[7,28];
const clip=(x,a,b)=>Math.max(a,Math.min(b,Number.isFinite(x)?x:0));
const sig=x=>1/(1+Math.exp(-clip(x,-20,20)));
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
function makeHead(){return {n:0,w:Array(K).fill(0),acc:Array(K).fill(.001),
 riskW:Array(K).fill(0),riskAcc:Array(K).fill(.001),mse:64,downMse:25};}
function create(opts={}){
 return {heads:{7:makeHead(),28:makeHead()},gateW:[0,0,0],gateAcc:[.001,.001,.001],
   memory:0,drift:{n:0,mean:0,m2:0,last:0},observations:0,
   config:{riskAversion:opts.riskAversion??.20,disableGate:!!opts.disableGate,
     disableRisk:!!opts.disableRisk,disable7:!!opts.disable7,disable28:!!opts.disable28}};
}
function observe(s,f,oldForecast={}){
 const ret=clip(f[0]/3,-3,3),trend=clip((f[1]/6+f[2]/10)/2,-2,2);
 const vol=clip(f[3]/3,0,3),shock=clip(-ret,0,3);
 const old=s.memory,gateX=[1,vol,shock];
 const gate=s.config.disableGate?.75:sig(dot(s.gateW,gateX));
 const memory=clip(gate*old+(1-gate)*trend,-2,2);
 s.memory=memory;
 const gderiv=gateX.map(v=>s.config.disableGate?0:(old-trend)*gate*(1-gate)*v);
 const r=s.drift;
 const std=r.n>8?Math.sqrt(Math.max(.01,r.m2/(r.n-1))):1;
 const innovation=clip((ret-r.mean)/std,-3,3);
 r.n++;
 const diff=ret-r.mean;r.mean+=diff/r.n;r.m2+=diff*(ret-r.mean);
 r.last=innovation;s.observations++;
 const x=[1,ret,clip(f[1]/6,-3,3),clip(f[2]/10,-3,3),vol,memory,
   clip((oldForecast.net14??0)/10,-3,3),clip((oldForecast.net56??0)/15,-3,3),
   clip(oldForecast.regime?.stress??0,-2,2),innovation];
 return {x,gderiv,gate,regimeShock:innovation,atObservation:s.observations};
}
function forecast(s,snapshot){
 const estimates={};let norm=0,total=0,down=0,varMix=0;
 for(const h of HORIZONS){
   if((h===7&&s.config.disable7)||(h===28&&s.config.disable28))continue;
   const v=s.heads[h],mu=clip(dot(v.w,snapshot.x),-30,30);
   const downside=clip(dot(v.riskW,snapshot.x),0,25);
   const sigma=Math.sqrt(v.mse);
   // Loss-adjusted experts, learned from matured samples only.
   const weight=1/Math.max(1,Math.sqrt(v.mse));
   estimates[h]={mu,downside,sigma,weight,n:v.n};
   if(v.n>0){norm+=weight;total+=weight*mu;down+=weight*downside;varMix+=weight*sigma;}
 }
 const ready=Object.values(estimates).some(v=>v.n>=8) &&
   Object.values(estimates).every(v=>v.n>=3);
 return {estimates,ready,mu:norm?total/norm:0,
   downside:norm?down/norm:0,uncertainty:norm?varMix/norm:8,
   x:snapshot.x,gderiv:snapshot.gderiv};
}
function action(s,pred,position){
 if(position!=="CASH"&&position!=="GOLD")throw Error("INVALID_POSITION");
 const feeLog=-100*Math.log(1-FEE);
 const risk=s.config.disableRisk?0:s.config.riskAversion*pred.downside;
 const advantage=pred.mu-risk;
 // Economic fees (log units, pct): CASH->GOLD is an eventual round trip.
 // GOLD->CASH is compared against retaining already owned GOLD; 1 sale
 // is common to both paths. Reserve one fee for later re-entry.
 const entryBarrier=2*feeLog,exitBarrier=feeLog;
 const target=!pred.ready?position:
   position==="CASH"?(advantage>entryBarrier?"GOLD":"CASH"):
   (advantage< -exitBarrier?"CASH":"GOLD");
 return {target,position,advantage,entryBarrier,exitBarrier,
    reason:!pred.ready?"INSUFFICIENT_MATURED_EXPERIENCE":
      target===position?"NET_WEALTH_HOLD":"LEARNED_NET_WEALTH_SWITCH"};
}
function stepAda(w,acc,x,err,lr=.12){
 const e=clip(err,-25,25),scale=1+x.reduce((a,v)=>a+v*v,0);
 for(let i=0;i<w.length;i++){
   const g=e*x[i]/scale;
   acc[i]+=g*g;
   w[i]=clip(w[i]-lr*g/Math.sqrt(acc[i]),-30,30);
 }
}
function learn(s,queued,now){
 if(!(queued.exitTs<now))throw Error("V14_UNMATURED_OUTCOME");
 const h=queued.h;
 if(!HORIZONS.includes(h))throw Error("INVALID_HORIZON");
 const q=s.heads[h],x=queued.pred.x;
 const y=clip(queued.grossLogPct,-30,30);
 const downside=clip(queued.worstLossPct,0,30);
 const prior=dot(q.w,x),loss=clip(prior-y,-30,30);
 const riskPrior=dot(q.riskW,x),riskErr=clip(riskPrior-downside,-30,30);
 const memoryCoef=q.w[MEM];
 // Learn the local recurrent forget/update gate from delayed outcome error.
 if(h===7&&!s.config.disableGate){
   const grad=clip(loss*memoryCoef,-25,25);
   for(let i=0;i<s.gateW.length;i++){
     const g=grad*queued.pred.gderiv[i]/(1+x.reduce((a,v)=>a+v*v,0));
     s.gateAcc[i]+=g*g;
     s.gateW[i]=clip(s.gateW[i]-.04*g/Math.sqrt(s.gateAcc[i]),-6,6);
   }
 }
 stepAda(q.w,q.acc,x,loss);
 stepAda(q.riskW,q.riskAcc,x,riskErr);
 q.mse=q.n===0?loss*loss:.92*q.mse+.08*loss*loss;
 q.downMse=q.n===0?riskErr*riskErr:.92*q.downMse+.08*riskErr*riskErr;
 q.n++;
 return {h,origin:queued.origin,knownAt:now,actual:y,
   pred:prior,worstLossPct:downside,learned:q.n};
}
function label(bank,originTs,h){
 const after=(t,strict=false)=>{
   let l=0,r=bank.length;
   while(l<r){const m=(l+r)>>1;
     if(strict?bank[m].ts<=t:bank[m].ts<t)l=m+1;else r=m;}
   return bank[l]||null;
 };
 const entry=after(originTs,true);
 if(!entry||entry.ts-originTs>72*HR)return null;
 const exit=after(entry.ts+h*DAY);
 if(!exit||exit.ts-(entry.ts+h*DAY)>78*HR)return null;
 let worst=0;
 // Scan only for label construction; learning waits for exitTs<now.
 for(const b of bank){
   if(b.ts<entry.ts)continue;
   if(b.ts>exit.ts)break;
   worst=Math.min(worst,100*Math.log(b.p/entry.p));
 }
 return {exitTs:exit.ts,grossLogPct:100*Math.log(exit.p/entry.p),
   worstLossPct:-worst,entryAt:entry.ts,exitAt:exit.ts};
}
module.exports={FEE,HR,DAY,HORIZONS,create,observe,forecast,action,learn,label};