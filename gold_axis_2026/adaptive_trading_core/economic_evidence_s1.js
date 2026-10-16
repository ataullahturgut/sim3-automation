"use strict";
/**
 * S1 research evidence bridge, NOT market causal inference or a trading policy.
 * Input strings are read-only copies of OLAY-02, ÖĞREN-03 and macro ledger.
 * Absolutely NO ex-post case ID/price-outcome becomes a model feature.
 *
 * 2023 macro ledger was reconstructed post-event. Its 'surprise_ready' field is
 * NOT proof of the first contemporary print. It is quarantined until verifiable.
 */
const FAMILIES=new Set(["G01","G02","G03","G04","G05","G06","G07"]);
const time=s=>{
  const t=Date.parse(s);
  if(typeof s!=="string"||!Number.isFinite(t)||
    !(/Z$|[+-]\d{2}:\d{2}$/.test(s)))throw Error("EVENT_TIME_MISSING_OFFSET");
  return t;
};
const iso=t=>new Date(t).toISOString();
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
function csv(src){
  if(typeof src!=="string"||!src.trim())throw Error("CSV_MISSING");
  let rows=[],fields=[],field="",inQuote=false;
  for(let i=0;i<src.length;i++){
    const c=src[i];
    if(c==='"'){
      if(inQuote&&src[i+1]==='"'){field+='"';i++}else inQuote=!inQuote;
    }else if(c===","&&!inQuote){fields.push(field);field=""}
    else if((c==="\n"||c==="\r")&&!inQuote){
      if(c==="\r"&&src[i+1]==="\n")i++;
      fields.push(field);field="";
      if(fields.some(x=>x.trim().length))rows.push(fields);
      fields=[];
    }else field+=c;
  }
  if(inQuote)throw Error("UNTERMINATED_CSV_QUOTE");
  fields.push(field);if(fields.some(x=>x.trim().length))rows.push(fields);
  if(rows.length<2)throw Error("CSV_HAS_NO_ROWS");
  const header=rows.shift().map(x=>x.trim());
  if(new Set(header).size!==header.length)throw Error("DUPLICATE_CSV_HEADER");
  return rows.map((a,i)=>{
    if(a.length!==header.length)throw Error("CSV_COLUMN_COUNT_AT_"+i);
    return Object.fromEntries(header.map((k,j)=>[k,a[j]]));
  });
}
function readArchive(olayText,ogrenText,deepCsv){
  if(typeof olayText!=="string"||!olayText.startsWith("# OLAY-02")||
     typeof ogrenText!=="string"||!ogrenText.startsWith("# ÖĞREN-03"))
    throw Error("ARCHIVE_PROVENANCE_REQUIRED");
  const families=[...FAMILIES].filter(x=>ogrenText.includes("### "+x+" "));
  const orgr=Array.from(ogrenText.matchAll(/^### (ORG\d{2}) — /gm),m=>m[1]);
  if(families.length!==7||orgr.length<12)throw Error("DNA_ONTOLOGY_MISMATCH");
  const cases=csv(deepCsv).map(row=>{
    if(!row.case_id||!/^(SWING_V1_|MOVE_V2_)/.test(row.case_id))throw Error("CASE_ID_INVALID");
    if(!/^ORG\d{2}$/.test(row.primary_plot_candidate_id)||
       !orgr.includes(row.primary_plot_candidate_id))
       throw Error("UNREGISTERED_ORG_CANDIDATE");
    return {caseRef:row.case_id,candidateOrg:row.primary_plot_candidate_id,
      competingOrg:row.secondary_plot_candidate_id,
      primaryEvidence:row.source_support_grade,
      firstprint:row.firstprint_utc,
      permissibleAsTradingInput:false,
      role:"POST_EVENT_RESEARCH_CASE_NOT_TRADE_FEATURE"};
  });
  return {familyVocabulary:families,orgVocabulary:orgr,
    caseCount:cases.length,
    firstprintClaimedCases:cases.filter(c=>c.firstprint!=="UNKNOWN"&&c.firstprint!=="").length,
    pitCertifiedCases:0, // Even a dated retrospectively entered source isn't proof of live first-print
    cases,ontologyStatus:"RESEARCH_HYPOTHESES_NOT_CAUSAL_RULES"};
}
function readReleaseClusters(macroCsv,start,end){
  const events=csv(macroCsv).filter(r=>r.event_ts_utc&&r.event_ts_utc!=="");
  const tStart=time(start),tEnd=time(end);
  const clusters=new Map();
  for(const row of events){
    const ts=time(row.event_ts_utc);
    if(ts<tStart||ts>=tEnd)continue;
    if(row.pair_complete!=="True"||row.pit_use!=="POST_RELEASE_ONLY")continue;
    if(!row.actual_lineage_id||!row.consensus_lineage_id||
       !Number.isFinite(Number(row.surprise)))continue;
    const available=time(row.surprise_ready_at_utc);
    if(available<ts)throw Error("PRE_RELEASE_SURPRISE_BLOCKED");
    const k=iso(ts);
    if(!clusters.has(k))clusters.set(k,{
      scheduledReleaseUtc:k,earliestResearchAvailabilityUtc:iso(available),
      candidateFamily:"G01",firstprintVerified:false,
      evidenceStatus:"RECONSTRUCTED_POST_RELEASE_ONLY_NOT_PIT",
      featureAdmissible:false,records:[]});
    clusters.get(k).records.push({
      type:row.event_type,surprise:Number(row.surprise),
      sourcePairIds:[row.actual_lineage_id,row.consensus_lineage_id],
      scoreSignInterpretation:"NOT_ASSIGNED_NO_MANUAL_DIRECTION_RULE"});
  }
  return [...clusters.values()].sort((a,b)=>a.scheduledReleaseUtc.localeCompare(b.scheduledReleaseUtc));
}
function pairControls(marketRows,macroClusters,{exposureMinutes=240,blackoutMinutes=1440}={}){
  if(!Array.isArray(marketRows)||marketRows.length<3)throw Error("MARKET_ROWS_REQUIRED");
  if(exposureMinutes>240||exposureMinutes<=0||blackoutMinutes<exposureMinutes)
    throw Error("EVENT_STUDY_WINDOW_INVALID");
  const cache=marketRows.map(row=>({
    t:time(row.end_utc),
    tstr:row.end_utc,price:Number(row.close_price),
    // Market fields are used for matching PRE-OUTCOME only.
    context:["gold_1h_pct","nq_1h_pct","zn_1h_pct","cl_1h_pct"].map(k=>{
      const n=row[k];return n===null||n===undefined?null:Number(n);
    })
  }));
  for(let i=0;i<cache.length;i++){
    if(i&&cache[i].t<=cache[i-1].t)throw Error("MARKET_NONCHRONOLOGICAL");
    if(!(cache[i].price>0)||cache[i].context.some(z=>z!==null&&!Number.isFinite(z)))
      throw Error("MARKET_ROW_BAD");
  }
  const times=macroClusters.map(e=>time(e.scheduledReleaseUtc));
  const candidate=[],control=[];
  for(let i=0;i<cache.length-1;i++){
    const a=cache[i],b=cache[i+1];
    if(b.t-a.t!==240*60000)continue; // exact 4h after-event outcome
    const nearby=times.map((t,j)=>({t,j,ageMin:(a.t-t)/60000})).filter(x=>x.ageMin>=0&&x.ageMin<exposureMinutes);
    const excluded=times.some(t=>Math.abs(a.t-t)<=blackoutMinutes*60000);
    const row={at:a.tstr,hourUtc:new Date(a.t).getUTCHours(),
      // Future price is attached ONLY TO EX-POST EVIDENCE; never used as feature.
      outcome4hLogPct:100*Math.log(b.price/a.price),
      marketContext:a.context,infoAvailableAtDecision:a.tstr};
    if(nearby.length){
      const ids=nearby.map(x=>x.j);
      candidate.push({...row,releaseIndex:ids});
    }else if(!excluded)control.push(row);
  }
  const usedControls=new Set(),events=candidate.map(v=>{
    // Comparators are same UTC hour, NOT outcome-selected, with temporally
    // distant event windows. If no same-hour control, do not fabricate one.
    const same=control.filter(q=>q.hourUtc===v.hourUtc).map(q=>({
      ...q,dist:Math.sqrt(v.marketContext.reduce((a,z,i)=>{
        const y=q.marketContext[i];
        return a+((z===null||y===null)?1:((z-y)/1.5)**2);
      },0))
    })).sort((a,b)=>a.dist-b.dist);
    const matched=same.slice(0,4);
    for(const c of matched)usedControls.add(c.at);
    return {at:v.at,releaseTimes:v.releaseIndex.map(i=>macroClusters[i].scheduledReleaseUtc),
      observedNext4hLogPct:v.outcome4hLogPct,
      candidateFamily:"G01",
      matchedControls:matched.map(c=>({at:c.at,next4hLogPct:c.outcome4hLogPct,
        distanceFromPreOutcomeContext:c.dist})),
      controlMeanLogPct:mean(matched.map(c=>c.outcome4hLogPct)),
      aboveControlMean:matched.length?v.outcome4hLogPct>mean(matched.map(c=>c.outcome4hLogPct)):null,
      sameSignAsControlCount:matched.filter(c=>(c.outcome4hLogPct>0)===(v.outcome4hLogPct>0)).length,
      oppositeSignControlCount:matched.filter(c=>(c.outcome4hLogPct>0)!==(v.outcome4hLogPct>0)).length,
      causalStatus:"UNVERIFIED_MATCHED_OBSERVATIONAL_EVIDENCE",
      admission:"QUARANTINED_FROM_ASOF_TRADING_FEATURES"};
  });
  const signCount=a=>({up:a.filter(c=>c.outcome4hLogPct>0).length,
    nonUp:a.filter(c=>c.outcome4hLogPct<=0).length});
  return {events,controlsTotal:control.length,
    allNoEventControls4h:signCount(control),
    sameClockControl4h:signCount(control.filter(q=>candidate.some(v=>v.hourUtc===q.hourUtc))),
    uniqueMatchedControls:usedControls.size,
    outcomesUsedToFormMatch:false,eventFeaturesFedIntoCore:0,
    comparisonMethod:"SAME_UTC_HOUR_NEAREST_PRE_OUTCOME_MARKET_CONTEXT",
    claim:"RETROSPECTIVE_NEGATIVE_CONTROLS_NOT_CAUSAL_IDENTIFICATION"};
}
function evaluate(input){
  const a=readArchive(input.olay02,input.ogren03,input.deepCaseCsv);
  const ts=readReleaseClusters(input.macroCsv,"2023-01-01T00:00:00Z","2023-02-01T00:00:00Z");
  const study=pairControls(input.marketRows,ts);
  return {archive:{...a,cases:undefined},releases:ts,controls:study,
    scientificGate:"FAIL_NO_INDEPENDENT_FIRSTPRINT_NO_CAUSAL_PROOF",
    modelPolicy:"UNCHANGED_NO_TRADE_ACTION"};
}
module.exports={csv,readArchive,readReleaseClusters,pairControls,evaluate};
