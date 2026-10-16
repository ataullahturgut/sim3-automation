"use strict";
/** Research archive segment for SAME S2+S3 opportunity learner; no private bars stored. */
const s2=require("./adaptive_phase_lifecycle_s2");
const opportunity=require("./adaptive_opportunity_learning_s3");
const SOURCE="EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1";
const dayMillis=d=>Date.parse(d+"T22:00:00Z");
function trainSegment(bars,days,{priorKnowledge=null}={}){
 if(!Array.isArray(bars)||!Array.isArray(days)||!bars.length)throw Error("OP_ARCHIVE_INPUT_REQUIRED");
 const states=s2.create({sourceRegistry:{[SOURCE]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"}}});
 const s=priorKnowledge?opportunity.fromKnowledge(priorKnowledge):opportunity.create();
 // Years are independent training blocks for price-phase sensing: ensure that
 // new effective-N anchors are not compared to indices in the previous year.
 if(priorKnowledge)for(const v of Object.values(s.cohorts))v.lastIndependentIndex=null;
 let j=0,accepted=0,skipped=0,upCandidates=0,downCandidates=0;
 const examples=[];
 let lastTime=-Infinity;
 for(const [seconds,price] of bars){
  const t=Number(seconds)*1000,end=t+900000;
  if(!(t>lastTime)||!(Number(price)>0))throw Error("OP_ARCHIVE_BAR_INVALID");
  lastTime=t;
  while(j<days.length&&dayMillis(days[j].sd)<end){
   const x=days[j++];
   const valid=Number(x.n)>=80&&Number(x.valid_quotes)===Number(x.n)&&
     Number(x.gap)<=90&&dayMillis(x.sd)-(Date.parse(x.l)+900000)<=5400000&&
     Date.parse(x.l)+900000<=dayMillis(x.sd);
   if(valid){
    opportunity.closeSession(s,{session:x.sd,sourceId:SOURCE,
      price:Number(x.p),availableAt:new Date(dayMillis(x.sd)).toISOString()});
    accepted++;
   }else skipped++;
  }
  const at=new Date(end).toISOString();
  const phase=s2.observe(states,{asof:at,barStartedAt:new Date(t).toISOString(),
    priceAvailableAt:at,price:Number(price),priceSource:SOURCE,barMinutes:15});
  const q=opportunity.observeCandidate(s,{at,price:Number(price),
    sourceId:SOURCE,fast:phase});
  if(q.candidate){
   if(phase.direction===1)upCandidates++;else downCandidates++;
   if(at.startsWith("2023-01-06")||at.startsWith("2023-01-09"))
     examples.push({at,price:Number(price),phase:phase.phase,
       direction:phase.direction,prequential:q.forecast.learnedResearchPreference});
  }
 }
 const know=opportunity.knowledge(s);
 return {knowledge:know,summary:{
   bars:bars.length,acceptedSessions:accepted,rejectedSessions:skipped,
   upCandidates,downCandidates,
   learning:opportunity.summary(s).audit,
   cohortCount:Object.keys(know.cohorts).length,examples,
   completePhaseEpisodes:s2.summary(states).completeEpisodes,
   source:SOURCE,rawPricesIncluded:false}};
}
module.exports={SOURCE,trainSegment};
