#!/usr/bin/env node
"use strict";
/*
 Only JAN 2023: chronological source adapter for timeless KAVIS Core V0.
 Historical HistData M15 XAU MID; not user's executable bank BID/ASK.
 Pre-published macro event records feed parameter learning as quantitative
 family/surprise; event prices after first publication do NOT travel backward.
 No stock/ETF/missing metal data fabricated; all missingness explicit.
 Not a proof of causality, bank profit, or blind out-of-sample ability.
*/
const fs=require("node:fs"),path=require("node:path");
const Core=require("./kavis_core_timeless_v0");
const JAN="2023-01";
const TZONE=3*3600000,MS15=900000;
function csv(t){
 const lines=t.trim().split(/\r?\n/),headers=lines.shift().split(",");
 return lines.filter(Boolean).map(x=>{
  const vals=x.split(",");
  return Object.fromEntries(headers.map((v,i)=>[v,vals[i]??""]));
 });
}
function readPrices(s){
 const a=csv(s).map(x=>({t:Date.parse(x.tt),asof:x.tt,
  close:Number(x.close),open:Number(x.p)}));
 for(let i=0;i<a.length;i++){
  if(!Number.isFinite(a[i].t)||!(a[i].close>0)||!(a[i].open>0)||
   !a[i].asof.startsWith(JAN)||
   i>0&&a[i].t<=a[i-1].t)throw Error("JAN_2023_ONLY_PRICE_SOURCE");
 }
 return a;
}
function readReleases(s){
 return csv(s).filter(x=>x.event_ts_utc.startsWith("2023-01")&&
  x.pair_complete==="True"&&x.pit_use==="POST_RELEASE_ONLY"&&
  x.actual_lineage_id&&x.consensus_lineage_id&&
  Number.isFinite(Date.parse(x.surprise_ready_at_utc))&&
  Number.isFinite(+x.surprise)).map(x=>({
   published:Date.parse(x.surprise_ready_at_utc),type:x.event_type,
   surprise:Number(x.surprise),actual:+x.actual,consensus:+x.consensus,
   proof:{actual:x.actual_lineage_id,consensus:x.consensus_lineage_id},
   // This is provisional unit-wise economic scaling, NOT an effect-direction rule.
   z:Math.max(-4,Math.min(4,
     x.event_type==="NFP"?Number(x.surprise)/150:
     Number(x.surprise)/.2)),
   mechanismFamily:"G01_RATES_USD"}))
  .sort((a,b)=>a.published-b.published);
}
function local(t){return new Date(t+TZONE).toISOString().slice(0,16).replace("T"," ");}
function bank(t){
 const d=new Date(t+TZONE),day=d.getUTCDay(),hour=d.getUTCHours();
 return day!==0&&day!==6&&hour>=9&&hour<17;
}
function lagPct(a,i,n){
 if(i-n<0)return null;
 // Prior-observed data: sparse overnight interval permitted but no look-ahead.
 return 100*Math.log(a[i].close/a[i-n].close);
}
function market(a,i){
 const m={};
 const add=(name,value)=>{
  if(value!==null&&Number.isFinite(value))m[name]={
   value,availableAt:a[i].asof};
 };
 add("goldR1hPct",lagPct(a,i,4));
 add("goldR4hPct",lagPct(a,i,16));
 add("goldR1dPct",lagPct(a,i,96));
 if(i>=16){
  const recent=[];for(let j=i-15;j<=i;j++)
   if(a[j].t-a[j-1].t===MS15)recent.push(100*Math.log(a[j].close/a[j-1].close));
  if(recent.length>=12){
   const avg=recent.reduce((x,y)=>x+y,0)/recent.length;
   add("goldVol1dPct",Math.sqrt(recent.reduce((x,y)=>x+(y-avg)**2,0)/recent.length));
  }
 }
 const high=Math.max(...a.slice(Math.max(0,i-64),i+1).map(x=>x.close));
 add("goldDrawdownPct",100*Math.log(a[i].close/high));
 return m;
}
function impactfulMovements(a){
 // Ex post monthly diagnostics ONLY; never used as trading inputs or labels.
 const candidates=[];
 for(let i=16;i<a.length;i++)if(a[i].t-a[i-16].t===16*MS15){
  const ret=100*Math.log(a[i].close/a[i-16].close);
  candidates.push({start:a[i-16].asof,end:a[i].asof,
   returnPct:ret,abs:Math.abs(ret),startI:i-16,endI:i});
 }
 candidates.sort((x,y)=>y.abs-x.abs);
 const kept=[];
 for(const c of candidates){
  if(kept.some(z=>!(c.endI<z.startI||c.startI>z.endI)))continue;
  kept.push(c);
  if(kept.length===6)break;
 }
 return kept.map(({startI,endI,abs,...other})=>({
  ...other,changeMagnitudePct:abs,selection:"EXPOST_DESCRIPTION_NOT_CORE_SIGNAL"}));
}
function run(priceRows,releaseRows){
 if(priceRows.length<800)throw Error("NOT_ENOUGH_JAN_2023_DATA");
 if(releaseRows.some(x=>!Number.isFinite(x.published)))throw Error("BAD_RELEASE");
 const s=Core.create(),actions=[],checks=[],daily=new Map(),startPrice=priceRows[0].open;
 let firstEligiblePrice=null,accepted=0,usedNews=0;
 for(let i=0;i<priceRows.length;i++){
  const r=priceRows[i];
  const events=releaseRows.filter(x=>x.published<=r.t&&r.t-x.published<=48*3600000)
   .map(e=>({mechanismFamily:e.mechanismFamily,
    signedSurprise:e.z,sourceConfidence:.7,
    firstAvailableAt:new Date(e.published).toISOString()}));
  const prediction=Core.observe(s,{
   asof:r.asof,price:r.close,priceAvailableAt:r.asof,
   market:market(priceRows,i),events});
  if(events.length)usedNews++;
  const day=local(r.t).slice(0,10);
  if(!daily.has(day))daily.set(day,{date:day,bars:0,checkpoints:0,
    buys:0,sells:0,labelsBefore:0,labelsAtEnd:0,nav:100,position:"CASH"});
  const d=daily.get(day);d.bars++;d.labelsAtEnd=s.totalMatured;
  const next=priceRows[i+1],canTrade=bank(r.t)&&next&&
    next.t-r.t===MS15&&bank(next.t);
  if(canTrade){
   if(firstEligiblePrice===null)firstEligiblePrice=next.open;
   accepted++;d.checkpoints++;
   const rec={asof:r.asof,timeTR:local(r.t),
    action:prediction.action,positionBefore:prediction.positionBefore,
    expectedNetSwitchAdvantagePct:prediction.lowerSwitchAdvantagePct,
    costBothLegsPct:prediction.costTwoLegPct,
    maturedTargets:s.totalMatured,
    sourceCount:prediction.quality.available,
    missingCount:prediction.quality.missing,
    newsEvidenceActive:events.length,
    forecast:prediction.forecast};
   checks.push(rec);
   if(prediction.action!=="WAIT"){
    const fill=Core.fill(s,prediction,{
      price:next.open,at:new Date(next.t).toISOString(),
      quoteFirstAvailableAt:new Date(next.t).toISOString()});
    const tx={at:new Date(next.t).toISOString(),timeTR:local(next.t),
      action:prediction.action,priceProxy:next.open,
      nav:fill.capitalNetLiquidation,
      feePerLeg:Core.FEE,modelScore:prediction.lowerSwitchAdvantagePct,
      labeledEventsUsed:events.length};
    actions.push(tx);
    if(tx.action==="BUY")d.buys++;else d.sells++;
   }
  }
  d.nav=s.portfolio.lastNav;d.position=s.portfolio.position;
 }
 const passiveFirst=firstEligiblePrice===null?null:
  100*(1-Core.FEE)*priceRows.at(-1).close/firstEligiblePrice*(1-Core.FEE);
 return {
  scope:"2023-01_ONLY",
  source:"HISTORICAL_HISTDATA_XAU_M15_MID_PROXY_NOT_BANK_BIDASK",
  historicalVintage:"HISTORICAL_SOURCE_RETRIEVED_POST_EVENT_NOT_TRUE_PIT",
  tradingWindow:"TR_WEEKDAYS_09_17_15MIN",eventFamiliesUsed:["G01_RATES_USD"],
  macroProof:"POST_RELEASE_ONLY_SOURCE_LINEAGE_WITH_RECONSTRUCTED_2026_AVAILABILITY",
  firstBar:priceRows[0].asof,lastBar:priceRows.at(-1).asof,
  bars:priceRows.length,releaseRecords:releaseRows.length,
  barsWithPublishedNewsActive:usedNews,
  acceptedBankChecks:accepted,
  costPctPerLeg:100*Core.FEE,
  predictedEventWeightsAreTrainable:true,
  maturedEconomicOutcomeLabels:s.totalMatured,
  changedMathematicalUpdates:s.totalNonzeroUpdates,
  finalNetUSD:s.portfolio.lastNav,
  maxDDPct:s.portfolio.maxDDPct,trades:actions,
  initialUSD:100,passiveBuyHoldNetUSD:passiveFirst,
  cashBaselineUSD:100,
  headStats:s.heads.map(h=>({horizonMinutes:h.h,n:h.n,
   rmsePct:Math.sqrt(h.mse),maePct:h.mae,
   weightEventG01:h.wReturn[1+Core.SIGNALS.length+4],
   learnedWeightsNorm:Math.sqrt(h.wReturn.reduce((z,x)=>z+x*x,0)),
   labelsSkipped:h.labelsSkipped})),
  daily:Array.from(daily.values()),
  significantExpostMovements:impactfulMovements(priceRows),
  eventLedger:releaseRows.map(e=>({published:new Date(e.published).toISOString(),
   originalType:e.type,modelMechanism:e.mechanismFamily,
   normalizedSurprise:e.z,lineageVerified:!!e.proof.actual&&!!e.proof.consensus,
   remark:"candidate mechanism, not proof of causing gold response"})),
  decisionLedger:checks,coreCheckpoint:Core.checkpoint(s)};
}
function writeResult(root,r){
 if(r.scope!=="2023-01_ONLY")throw Error("MONTH_SCOPE_MISMATCH");
 fs.mkdirSync(root,{recursive:true});
 const cp=r.coreCheckpoint,decision=r.decisionLedger;
 const totals={...r};delete totals.coreCheckpoint;delete totals.decisionLedger;
 fs.writeFileSync(path.join(root,"MATH_AUDIT.json"),JSON.stringify(totals,null,2));
 fs.writeFileSync(path.join(root,"CORE_CHECKPOINT.json"),JSON.stringify(cp));
 fs.writeFileSync(path.join(root,"DECISIONS.json"),JSON.stringify(decision));
 fs.writeFileSync(path.join(root,"EVENT_ECONOMICS.jsonl"),
  r.eventLedger.map(e=>JSON.stringify(e)).join("\n")+"\n");
 const md=[
 "# KAVİS CORE — OCAK 2023 (yalnız bu ay)",
 "Bu rapor gerçek banka emir kaydı değil; tarihsel kaynak üzerinden geriye dönük araştırmadır.",
 "## Matematiksel öğrenme",
 "- Olgunlaşan tahmin/olay etkisi etiketleri: "+r.maturedEconomicOutcomeLabels,
 "- Sıfırdan farklı ağırlık güncellemesi: "+r.changedMathematicalUpdates,
 "- Açılmış aylık kontrol noktası: "+r.acceptedBankChecks,
 "- Kullanılan makro açıklama kayıtları: "+r.releaseRecords,
 "- Gerçekleşmiş sanal işlem: "+r.trades.length,
 "- Aylık kapanış teorik net sermaye: "+r.finalNetUSD.toFixed(4)+" USD",
 "- Pasif ilk uygun seansta AL / ay sonu net: "+r.passiveBuyHoldNetUSD?.toFixed(4)+" USD",
 "- Nakit kal: 100 USD; Maksimum düşüş: %"+r.maxDDPct.toFixed(3),
 "## Aylık önemli hareketler — yalnız sonradan açıklayıcı analiz",
 "Aşağıdaki büyüklükler algoritmanın o anda kullanabildiği geleceği temsil ETMEZ.",
 ...r.significantExpostMovements.map(x=>"- "+x.start+" → "+x.end+" : "+x.returnPct.toFixed(3)+"% (4 saatlik gerçekleşmiş hareket)"),
 "## Çekirdeğin hangi ilişkileri öğrendiği",
 ...r.headStats.map(h=>"- Ufuk "+h.horizonMinutes+" dakika: olgunlaşmış "+h.n+" örnek; MAE %"+h.maePct.toFixed(4)+"; G01 olay katsayısı "+h.weightEventG01.toFixed(6)),
 "## Sonraki ay",
 "Bu araştırmada başka ay ÇALIŞTIRILMADI. Tarihten bağımsız ağırlıklar CORE_CHECKPOINT.json'dadır; Şubat için ayrıca veri ve bilimsel denetim gereklidir."
 ].join("\n")+"\n";
 fs.writeFileSync(path.join(root,"MONTH_REPORT.md"),md);
}
if(require.main===module){
 const [p,e,o]=process.argv.slice(2);
 if(!p||!e||!o)throw Error("usage: node v23_jan2023_core_walk.js jan_2023_m15.csv macro_releases.csv output_directory");
 const result=run(readPrices(fs.readFileSync(p,"utf8")),
   readReleases(fs.readFileSync(e,"utf8")));
 writeResult(o,result);
 console.log(JSON.stringify({
  scope:result.scope,bars:result.bars,releases:result.releaseRecords,
  bankChecks:result.acceptedBankChecks,learned:result.maturedEconomicOutcomeLabels,
  updated:result.changedMathematicalUpdates,trades:result.trades,
  finalNetUSD:result.finalNetUSD,passive:result.passiveBuyHoldNetUSD,
  maxDDPct:result.maxDDPct,headStats:result.headStats,
  noteworthyExpost:result.significantExpostMovements},null,2));
}
module.exports={csv,readPrices,readReleases,run,writeResult,market,impactfulMovements,bank};
