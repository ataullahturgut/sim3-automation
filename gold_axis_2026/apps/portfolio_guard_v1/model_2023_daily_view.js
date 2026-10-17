"use strict";
/**
 * Application read-only adapter for the EXISTING mathematical CORE's frozen
 * Jan and Feb 2023 daily audit reports. This does not train or choose actions.
 * Never reinterpret a research ORG hypothesis as an actual learned economic rule.
 */
const fs=require("node:fs");
const path=require("node:path");
const MODEL=path.resolve(__dirname,"..","..","adaptive_trading_core");
const VERSION="GOLD_MODEL_2023_DAILY_READONLY_VIEW_V1_20261017";
const MONTHS=Object.freeze({
 "2023-01":{label:"Ocak 2023",filename:"JAN_2023_INTEGRATED_S1_S2_S3_REAL_DAILY_RESULTS_20261017.md",
  expectedDays:31,sourceRun:"https://github.com/ataullahturgut/sim3-automation/actions/runs/39044090856",
  trainingM15Bars:5865,monthM15Bars:1920,pretrainedMarketRules:3,priorMaturedLabels:344,
  endMarketRules:5,endMaturedLabels:443,knownEventDays:["2023-01-06","2023-01-12"]},
 "2023-02":{label:"Şubat 2023",filename:"FEB_2023_INTEGRATED_S1_S2_S3_REAL_DAILY_RESULTS_20261017.md",
  expectedDays:28,sourceRun:"https://github.com/ataullahturgut/sim3-automation/actions/runs/39044531815",
  trainingM15Bars:7785,monthM15Bars:1830,pretrainedMarketRules:5,priorMaturedLabels:443,
  endMarketRules:6,endMaturedLabels:553,knownEventDays:["2023-02-03","2023-02-14"]}
});
const trim=x=>String(x).trim();
function num(x){
 if(x===undefined||x===null||x==="—")return null;
 if(!/^-?\d+(?:\.\d+)?%?$/.test(trim(x)))throw Error("DAILY_METRIC_BAD_NUMBER:"+x);
 return Number(trim(x).replace("%",""));
}
function phaseDirection(x){
 const [phase,direction]=x.split("/").map(trim);
 if(!["START","CONTINUE","PULLBACK","END","REENTRY","NEUTRAL","WARMUP","UNREADY","—"].includes(phase)||
  !["UP","DOWN","—"].includes(direction??""))
   throw Error("DAILY_S2_PHASE_INVALID:"+x);
 return {phase:phase==="—"?null:phase,direction:direction==="—"?null:direction};
}
function parseEventNotes(text,month){
 const out=new Map();
 const section=text.split("## Olayın ilk araştırma gözlemi")[1]||
  text.split("## Ekonomik açıklama anındaki asıl algoritma gözlemi")[1];
 if(!section)throw Error("DAILY_EVENT_SECTION_MISSING");
 for(const l of section.split("\n")){
  if(!l.startsWith("- **2023-"))continue;
  const date=l.match(/^- \*\*(2023-\d\d-\d\d)(?: \/ [^*]+)?:\*\*/)?.[1];
  if(!date)throw Error("DAILY_EVENT_DATE_UNPARSEABLE");
  const at=l.match(/\b2023-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z/)?.[0];
  const z=l.match(/trend z \*\*(-?\d+(?:\.\d+)?)\*\*/)?.[1];
  const match=l.match(/S2 \*\*([A-Z]+)(?:\/(UP|DOWN|—))?\*\*/);
  const s3=l.match(/S3 \*\*(KEEP|BUY|SELL|ABSTAIN)\*\*/)?.[1];
  if(!at||!match||!s3)throw Error("DAILY_EVENT_RECORD_INCOMPLETE:"+date);
  const notReady=l.includes("**NOT READY**")||l.includes("**hazır değil**");
  if(!notReady)throw Error("DAILY_EVENT_READINESS_NOT_GROUNDED:"+date);
  out.set(date,{at, s1EconomicFourHourReady:false,s2Phase:match[1],
   s2Direction:match[2]??null, s2TrendZ:num(z),s3ResearchAction:s3,
   availabilityBasis:"RETROSPECTIVE_RELEASE_PLUS_60MIN_UNVERIFIED_FIRST_PRINT"});
 }
 if(out.size!==month.knownEventDays.length ||
   month.knownEventDays.some(d=>!out.has(d)))throw Error("DAILY_EVENT_SET_MISMATCH");
 return out;
}
function readMonth(monthId){
 if(!Object.prototype.hasOwnProperty.call(MONTHS,monthId))throw Error("MONTH_NOT_AVAILABLE");
 const month=MONTHS[monthId];
 const sourcePath=path.join(MODEL,month.filename);
 const text=fs.readFileSync(sourcePath,"utf8");
 const lines=text.split(/\r?\n/).filter(line=>/^\| 2023-\d\d-\d\d \|/.test(line));
 if(lines.length!==month.expectedDays)throw Error("DAILY_ROW_COUNT_MISMATCH:"+monthId+":"+lines.length);
 const eventNotes=parseEventNotes(text,month);
 const rows=lines.map((line,index)=>{
  const cols=line.split("|").slice(1,-1).map(trim);
  const jan=monthId==="2023-01";
  if(cols.length!==(jan?8:10))throw Error("DAILY_COLUMN_COUNT_MISMATCH:"+cols[0]);
  const [date,rule,prob,expected]=cols;
  const dateExpected=monthId+"-"+String(index+1).padStart(2,"0");
  if(date!==dateExpected)throw Error("DAILY_CHRONOLOGY_MISMATCH:"+date);
  const fast=phaseDirection(cols[jan?4:5]);
  const sessionReturnPct=num(cols[jan?7:9]);
  const noSession=sessionReturnPct===null;
  const s1PUpPct=num(prob),s1ExpectedLogPct=num(expected);
  const slow=jan?null:cols[7]==="—"?null:cols[7];
  if(!jan&&slow!==null&&!["START","CONTINUE","PULLBACK","END","REENTRY","NEUTRAL","WARMUP","UNREADY"].includes(slow))
   throw Error("DAILY_SLOW_PHASE_INVALID:"+date);
  const s3=cols[jan?6:8]==="—"?null:cols[jan?6:8];
  if(![null,"KEEP","ABSTAIN","BUY","SELL"].includes(s3))throw Error("DAILY_ACTION_INVALID:"+date);
  if(noSession&&[s1PUpPct,s1ExpectedLogPct,fast.phase,s3].some(v=>v!==null))
   throw Error("DAILY_NO_SESSION_WITH_METRICS:"+date);
  if(!noSession&&(s1PUpPct===null||fast.phase===null||s3===null))
   throw Error("DAILY_SESSION_MISSING_METRICS:"+date);
  const event=eventNotes.get(date)||null;
  return {date,hasSession:!noSession,
   ruleCandidate:rule==="YOK"||rule==="—"?null:rule,
   ruleClassification:"RESEARCHER_RETROSPECTIVE_HYPOTHESIS_NOT_TRAINED_CAUSAL_RULE",
   s1:{horizonMinutes:240,pUpPct:s1PUpPct,expectedLogPct:s1ExpectedLogPct,
      effectiveN:jan?null:num(cols[4]), economicRuleCertified:false,
      type:"PRICE_CONDITIONED_RESEARCH_FORECAST"},
   s2:{fastPhase:fast.phase,fastDirection:fast.direction,
      trendZ:num(cols[jan?5:6]),slowPhase:slow,
      fourHourEndProbability:null,slowEndProbability:null},
   s3:{researchSuggestion:s3,realAction:null,tradeAllowed:false,
      explanation:s3==="KEEP"?"Ekonomik koşula bağlı, işlem maliyeti sonrası kanıtlanmış avantaj yok.":null,
      simulatedPosition:s3==="KEEP"?"CASH":null},
   observedSessionReturnPct:sessionReturnPct,
   observedReturnWindow:"SAME_DAY_SESSION_OPEN_TO_CLOSE_NOT_S1_FORECAST_TARGET",
   economicRelease: event
  };
 });
 return {version:VERSION,month:monthId,label:month.label,
  source:"EXISTING_CORE_20261017_DAILY_REPORTS",sourceRun:month.sourceRun,
  metricsAsOf:"LAST_COMPLETED_15M_BAR_OF_RESEARCH_SESSION",
  evaluationMode:"RETROSPECTIVE_NOT_BLIND_OUT_OF_SAMPLE",bankTradeAuthorized:false,
  actualMacroPITVerified:false,actualEconomicRuleLearningVerified:false,
  costPerLeg:0.008,marketPriceType:"RECONSTRUCTED_VENDOR_MID_NOT_BANK_BID_ASK",
  performanceClaimAllowed:false,trainingM15Bars:month.trainingM15Bars,
  monthM15Bars:month.monthM15Bars,startingLearnedMarketRules:month.pretrainedMarketRules,
  startingMaturedFourHourLabels:month.priorMaturedLabels,
  endingLearnedMarketRules:month.endMarketRules,
  endingMaturedFourHourLabels:month.endMaturedLabels,
  economicEventDaysVerifiedPIT:0,
  days:rows,sessionDays:rows.filter(r=>r.hasSession).length,
  ruleCandidateDays:rows.filter(r=>r.hasSession&&r.ruleCandidate!==null).length,
  confirmedTradeSignals:0,
  economicSnapshots:rows.filter(r=>r.economicRelease).length};
}
module.exports={MONTHS,VERSION,readMonth,parseEventNotes};
