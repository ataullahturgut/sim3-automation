"use strict";
/* V10 independent V7 signal model with deferred next-bank-checkpoint execution.
   Experimental, no bank connectivity, no model promotion. */
const fs=require("node:fs");
function parseCSV(raw) {
  const ls=raw.trim().split(/\r?\n/), columns=ls.shift().split(",");
  return ls.map(line=>{let cells=line.split(","),out={};columns.forEach((k,j)=>{out[k]=j===0||["event_id","org","firstprint_utc","available_at_utc","status","source_url"].includes(k)?cells[j]:(cells[j]===""?null:Number(cells[j]));});return out;});
}
function replayV6(rows,opts={}) {
 const F=opts.fee ?? .008, initial=opts.initial_usd ?? 119.753917;
 const begin=Date.parse(opts.start ?? "2026-02-02T06:00:00Z");
 const finish=Date.parse(opts.stop ?? "2026-09-30T12:00:00Z");
 const freezeAt=opts.freeze_learning_at?Date.parse(opts.freeze_learning_at):Infinity;
 const horizon={short:96,long:336},clamp=(n,l,h)=>Math.max(l,Math.min(h,n));
 const a=[...rows].map(x=>({...x,ts:Date.parse(x.tt)})).sort((x,y)=>x.ts-y.ts);
 if(a.some(x=>!Number.isFinite(x.ts)))throw Error("Invalid checkpoint timestamp");
 if(a.some((x,i)=>i>0&&x.ts===a[i-1].ts))throw Error("Duplicate checkpoint");
 const by=new Map(a.map(x=>[x.ts,x]));
 const events=(opts.events??[]).filter(e=>{
    let first=Date.parse(e.firstprint_utc),at=Date.parse(e.available_at_utc);
    return e.status==="VERIFIED"&&/^https:\/\//.test(e.source_url||"")&&Number.isFinite(first)&&Number.isFinite(at)&&first<=at&&/^ORG(0[1-9]|1[0-2])$/.test(e.org||"");
 }).map(e=>({...e,availableTs:Date.parse(e.available_at_utc)}));
 function eventFeatures(t){
   const qualified=events.filter(e=>e.availableTs<=t&&t-e.availableTs<=72*3600000);
   return {values:[qualified.some(e=>e.org==="ORG01")?1:0,qualified.some(e=>e.org==="ORG02")?1:0,qualified.some(e=>!["ORG01","ORG02"].includes(e.org))?1:0],ids:qualified.map(e=>e.event_id)};
 }
 function past(t,days){
   for(let h=0;h<=72;h+=3){let q=by.get(t-(days*24+h)*3600000);if(q&&Number.isFinite(q.c)&&q.c>0)return q.c}
   return null;
 }
 const z=(v,center,scale)=>v===null||!Number.isFinite(v)?0:clamp((v-center)/scale,-2,2);
 function features(r){
   const prior10=past(r.ts,10),prior20=past(r.ts,20),news=eventFeatures(r.ts);
   const p=[1,z(r.r4,0,1.5),z(r.r1,0,3),z(r.r3,0,3),z(r.rv,0,1),z(r.ds,.5,.5),z(r.eff,.5,.5),z(r.loc,.5,.5),z(r.dd,0,2),
   z(prior10?100*(r.c/prior10-1):null,0,5),z(prior20?100*(r.c/prior20-1):null,0,8)];
   const c=[...p,z(r.nq1,0,1.5),z(r.nq6,0,3),z(r.zn1,0,.3)];
   return {price:p,cross:c,event:[...c,...news.values],newsIds:news.ids};
 }
 const families=["price","cross","event","prior"],M={};
 for(let h of ["short","long"]){
   M[h]={price:{w:Array(11).fill(0),loss:10,n:0},cross:{w:Array(14).fill(0),loss:10,n:0},event:{w:Array(17).fill(0),loss:10,n:0,verifiedCount:0},prior:{mu:0,loss:10,n:0}};
 }
 function estimate(m,x){
   const predictions={prior:clamp(m.prior.mu,-20,20)};
   for(const k of ["price","cross","event"])predictions[k]=clamp(m[k].w.reduce((s,w,i)=>s+w*x[k][i],0),-20,20);
   const eligible=x.newsIds.length>0&&m.event.verifiedCount>=8;
   const experts=opts.price_only?["price","prior"]:(eligible?families:["price","cross","prior"]);
   const raw=experts.map(k=>Math.exp(-Math.min(25,m[k].loss/12)));
   const denom=raw.reduce((s,v)=>s+v,0);
   const weights=raw.map(v=>v/denom);
   return {mu:experts.reduce((s,k,i)=>s+weights[i]*predictions[k],0),
      uncertainty:Math.sqrt(experts.reduce((s,k,i)=>s+weights[i]*m[k].loss,0)),
      predictions,weights:Object.fromEntries(experts.map((k,i)=>[k,weights[i]])),
      economic_active:eligible,verified_case_ids:x.newsIds};
 }
 let pending=[],scored=[],skipped=0,updatesFrozen=0,activeVerified=0;
 let pendingOrder=null,signalLog=[],cash=initial,goldOz=0,firstEntryPrice=null,lastMark=null,lastSale=-Infinity,tradeLog=[],decisionLog=[],opportunity={missedUp:0,missedDown:0,missedUpCount:0,missedDownCount:0};
 function mature(now){
   let retain=[];
   for(const q of pending){
     if(q.due>now){retain.push(q);continue}
     let bar=by.get(q.due);if(!bar||!Number.isFinite(bar.c)||bar.c<=0){skipped++;continue}
     const y=clamp(100*(bar.c/q.p-1),-25,25),m=M[q.h];
     const absolute=Date.parse(q.origin);
     if(q.h==="long"&&absolute>=begin&&q.position==="CASH"&&y>100*(1/(1-F)**2-1)){opportunity.missedUpCount++;opportunity.missedUp+=y-100*(1/(1-F)**2-1)}
     if(q.h==="short"&&absolute>=begin&&q.position==="GOLD"&&y< -100*(1-(1-F)**2)){opportunity.missedDownCount++;opportunity.missedDown+=-y-100*(1-(1-F)**2)}
     scored.push({at:q.origin,h:q.h,return_pct:y,p:q.pred.predictions,ensemble:q.pred.mu});
     if(now>=freezeAt){updatesFrozen++;continue;}
     for(const k of ["price","cross","event"]){
       let v=m[k],err=y-q.pred.predictions[k],xx=q.x[k],ss=1+xx.reduce((s,j)=>s+j*j,0);
       v.loss=v.n?(.94*v.loss+.06*err*err):err*err;v.n++;
       const rate=.5/(12+Math.sqrt(v.n));
       v.w=v.w.map((w,i)=>clamp(.999*w+rate*clamp(err,-15,15)*xx[i]/ss,-8,8));
     }
     if(q.x.newsIds.length)m.event.verifiedCount++;
     let p=m.prior,err=y-q.pred.predictions.prior;
     p.loss=p.n?(.94*p.loss+.06*err*err):err*err;p.mu=.96*p.mu+.04*y;p.n++;
   }
   pending=retain;
 }
 const feeBreakEven=100*(1/(1-F)**2-1);
 for(const r of a){
   const t=r.ts;if(t>finish)break;mature(t);
   const x=features(r),s=estimate(M.short,x),l=estimate(M.long,x),hour=new Date(t).getUTCHours();
   if(hour===6&&Number.isFinite(r.p)&&r.p>0){
     for(const h of ["short","long"])pending.push({origin:r.tt,due:t+horizon[h]*3600000,h,p:r.p,x,pred:h==="short"?s:l,position:t>=begin?(goldOz>0?"GOLD":"CASH"):"PRESTART"});
   }
   if(t<begin||![6,9,12].includes(hour)||!Number.isFinite(r.p)||r.p<=0||!Number.isFinite(r.c))continue;
   if(firstEntryPrice===null)firstEntryPrice=r.p;
   const learned=M.long.prior.n>=40&&M.short.prior.n>=50;
   const stress=r.r4!==null&&r.r4<=-1&&r.nq6!==null&&r.nq6<=-1;
   const entryGate=feeBreakEven+Math.min(1.5,.1*l.uncertainty),exitGate=-feeBreakEven-Math.min(1.5,.1*s.uncertainty);
   let action="HOLD",reason="UNCERTAINTY_OR_COST",executedSignalAt=null;
   // Signals read the as-of bar at t, but cannot use that same bar's p
   // for a fill: execute a prior checkpoint's queued order only.
   if(pendingOrder&&pendingOrder.created<t){
     if(pendingOrder.side==="BUY"&&!goldOz){
       goldOz=cash*(1-F)/r.p;cash=0;action="BUY";
     }else if(pendingOrder.side==="SELL"&&goldOz){
       cash=goldOz*r.p*(1-F);goldOz=0;lastSale=t;action="SELL";
     }
     if(action!=="HOLD"){reason=pendingOrder.reason;executedSignalAt=pendingOrder.at;}
     pendingOrder=null;
   }
   let proposal=null;
   if(learned&&!goldOz&&t-lastSale>=72*3600000&&l.mu>entryGate){
     proposal={side:"BUY",reason:"ADAPTIVE_LONG_OPPORTUNITY"};
   }else if(goldOz&&(s.mu<exitGate||(!opts.disable_stress&&stress))){
     proposal={side:"SELL",reason:stress&&!opts.disable_stress?"XAU_NQ_STRESS":"ADAPTIVE_SHORT_RISK"};
   }
   if(proposal){
     pendingOrder={...proposal,at:r.tt,created:t};
     signalLog.push({at:r.tt,side:proposal.side,reason:proposal.reason,executionEarliestNextCheckpoint:true});
   }
   const liquidationNAV=cash+goldOz*r.c*(1-F);
   const record={time:r.tt,action,reason,position:goldOz?"GOLD":"CASH",nav:liquidationNAV,short: s.mu,long:l.mu,short_uncertainty:s.uncertainty,long_uncertainty:l.uncertainty,entryGate,exitGate,modelObservations:{short:M.short.prior.n,long:M.long.prior.n},economic_status:l.economic_active?"VERIFIED_MACRO_MODEL_ACTIVE":"MACRO_UNVERIFIED_OR_TOO_FEW",evidence_ids:l.verified_case_ids};
   decisionLog.push(record);if(action!=="HOLD")tradeLog.push({...record,fill_proxy:r.p,signal_at:executedSignalAt});
   if(l.economic_active)activeVerified++;lastMark=r;
 }
 const final=lastMark?cash+goldOz*lastMark.c*(1-F):initial;
 const holdGold=firstEntryPrice?initial*(1-F)*(lastMark.c/firstEntryPrice)*(1-F):initial;
 const perMonth={};for(const q of decisionLog)perMonth[q.time.slice(0,7)]={nav:q.nav,position:q.position,lastCheckpoint:q.time};
 const metrics={};for(const year of ["2025","2026"])for(const h of ["short","long"]){
   let arr=scored.filter(q=>q.h===h&&q.at.startsWith(year)&&(year!=="2026"||Date.parse(q.at)>=begin));
   const score={count:arr.length};
   for(const k of ["prior","price","cross","ensemble"]){let e=arr.map(q=>q.return_pct-(k==="ensemble"?q.ensemble:q.p[k]));score[k]={mae:e.length?e.reduce((s,d)=>s+Math.abs(d),0)/e.length:null,direction_correct:e.filter((v,i)=>(v<=arr[i].return_pct)===(arr[i].return_pct>=0)).length}}
   metrics[year+"_"+h]=score;
 }
 return {configuration:{start:new Date(begin).toISOString(),stop:new Date(finish).toISOString(),initial,fee_each_leg:F,entry_model:"14d forward",exit_model:"96h forward",training:"daily UTC 06, labels mature at origin+horizon",model:"ONLINE_EW_RIDGE_META_EXPLORATORY",macro:"Verified only, at least 8 mature macro cases"},final_usd:final,net_return_pct:100*(final/initial-1),hold_gold_usd:holdGold,cash_usd:initial,trades:tradeLog,per_month:perMonth,metrics,training_counts:{short:M.short.prior.n,long:M.long.prior.n,skippedMissingMatured:skipped,frozen_updates:updatesFrozen,verifiedEconomicCheckpoints:activeVerified},opportunity_regret_diagnostic:opportunity,queuedSignals:signalLog,unfilledPendingOrder:pendingOrder?{at:pendingOrder.at,side:pendingOrder.side}:null,executionContract:"NEXT_BANK_CHECKPOINT",decisionLog:opts.include_decisions?decisionLog:undefined};
}
if(require.main===module){
 const arg=(k,def)=>{let i=process.argv.indexOf(k);return i>=0?process.argv[i+1]:def};
 const input=arg("--data",null);if(!input)throw Error("Usage: node v6_adaptive_replay.js --data CHECKPOINTS.csv [--events VERIFIED_EVENTS.csv] [--out results.json]");
 const rows=parseCSV(fs.readFileSync(input,"utf8"));
 const eventsPath=arg("--events",null),events=eventsPath?parseCSV(fs.readFileSync(eventsPath,"utf8")):[];
 const result=replayV6(rows,{events,include_decisions:Boolean(arg("--decisions",null)),freeze_learning_at:arg("--freeze-at",null),disable_stress:Boolean(arg("--no-stress",null)),price_only:Boolean(arg("--price-only",null))});
 const dest=arg("--out",null);if(dest)fs.writeFileSync(dest,JSON.stringify(result,null,2)+"\n");
 console.log(JSON.stringify({...result,decisionLog:undefined},null,2));
}
module.exports={parseCSV,replayV6};
