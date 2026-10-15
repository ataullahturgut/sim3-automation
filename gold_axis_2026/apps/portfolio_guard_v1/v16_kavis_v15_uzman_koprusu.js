"use strict";
/**
 * V16-V15 shadow/inference bridge. Research-only.
 * V15 is a separately evolving full-information learning expert; its
 * hypothetical GOLD/CASH position is NEVER passed off as the V16
 * decision portfolio position. V15 actual-position advice is obtained
 * from a detached clone for that SINGLE as-of instant.
 *
 * No historic replay, no real bank order, no eventual profitability claim.
 */
const V15=require("./v15_kavis_cekirdek");
const V16=require("./v16_kavis_siralama");
const VERSION="V16_V15_SHADOW_EXPERT_BRIDGE_20261016";
function create(o={}){
 return {version:VERSION,v15:V15.make(o.v15||{}),v16:V16.create(o.v16||{}),
   bridge:{signals:0,expertUsed:0,shadowMismatch:0,
     maturities:0,rollbackCount:0}};
}
function infer(h,ob){
 if(!h||h.version!==VERSION)throw Error("INVALID_V16_BRIDGE");
 const position=ob?.position;
 if(!["CASH","GOLD"].includes(position))throw Error("BAD_BRIDGE_POSITION");
 // Deep clone, never advance V15's market clock or hypothetical state
 // from a V16 advisory query.
 const temp=V15.restore(V15.checkpoint(h.v15));
 if(temp.pending.length)throw Error("V15_SHADOW_PENDING");
 temp.virtualPortfolio.position=position;
 const advice=V15.signal(temp,{...ob,position});
 if(advice.provenance.validatedPointInTime!==true)
  throw Error("UNVERIFIED_V15_PROVENANCE");
 const score=advice.decision.score;
 if(score==null||!Number.isFinite(score))return null;
 return {position,availableAt:ob.asof,actionEdge:score,
   horizon:advice.decision.selectedHorizon,version:"V15_ASOF_EXPERT_ONLY",
   notAnIndependentDataSource:true};
}
function signal(h,ob){
 if(!h||h.version!==VERSION)throw Error("INVALID_V16_BRIDGE");
 const pos=ob?.position;
 if(!["CASH","GOLD"].includes(pos))throw Error("BAD_BRIDGE_POSITION");
 const backupV15=V15.checkpoint(h.v15),backupV16=V16.save(h.v16);
 try{
  const expert=infer(h,ob);
  const shadowPosition=h.v15.virtualPortfolio.position??"CASH";
  // The shadow's executed position is explicitly NOT trusted as V16's.
  const shadow=V15.signal(h.v15,{...ob,position:shadowPosition});
  const decision=V16.signal(h.v16,{...ob,position:pos,
   ...(expert?{v15Expert:expert}:{})});
  h.bridge.signals++;
  if(expert)h.bridge.expertUsed++;
  if(shadowPosition!==pos)h.bridge.shadowMismatch++;
  return {version:VERSION,decision,shadow:{
    intent:shadow.decision.action,position:shadowPosition,
    onlyExpertTraining:true},
    expertUsed:!!expert,expertHorizon:expert?.horizon??null,
    noOrdersSent:true,validPortfolioDecision:"V16_ONLY"};
 }catch(e){
  h.v15=V15.restore(backupV15);
  h.v16=V16.restore(backupV16);
  h.bridge.rollbackCount++;
  throw e;
 }
}
function quote(h,ob){
 if(!h||h.version!==VERSION)throw Error("INVALID_V16_BRIDGE");
 const backupV15=V15.checkpoint(h.v15),backupV16=V16.save(h.v16);
 try{
  const shadow=V15.receiveQuote(h.v15,ob);
  const realDecision=V16.quote(h.v16,ob);
  h.bridge.maturities+=shadow.matured.length;
  return {version:VERSION,decisionFill:realDecision.fill,
   decisionFeedback:realDecision.update,
   shadowLearningMatured:shadow.matured.length,
   shadowOnly:true,ordersSent:0};
 }catch(e){
  h.v15=V15.restore(backupV15);
  h.v16=V16.restore(backupV16);
  h.bridge.rollbackCount++;
  throw e;
 }
}
function save(h){return JSON.parse(JSON.stringify(h));}
function restore(x){
 const h=typeof x==="string"?JSON.parse(x):x;
 if(!h||h.version!==VERSION||!h.bridge)
  throw Error("BAD_BRIDGE_CHECKPOINT");
 const copy=JSON.parse(JSON.stringify(h));
 copy.v15=V15.restore(copy.v15);
 copy.v16=V16.restore(copy.v16);
 if(!Number.isInteger(copy.bridge.signals)||copy.bridge.signals<0||
   !Number.isInteger(copy.bridge.expertUsed)||copy.bridge.expertUsed<0||
   !Number.isInteger(copy.bridge.shadowMismatch)||copy.bridge.shadowMismatch<0)
   throw Error("CORRUPT_BRIDGE_COUNTERS");
 return copy;
}
module.exports={VERSION,create,infer,signal,quote,save,restore};
