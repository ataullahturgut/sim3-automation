"use strict";
/**
 * OLAY-02 → ETKI-05 (K labels) → OGREN-03 (ORG candidate) research router.
 * NOT A NEWS SCRAPER, NEWS CLASSIFIER AI, PRICE FORECASTER OR TRADING POLICY.
 * Caller supplies article/release records and a reviewed publisher allowlist.
 * A publisher domain or event occurrence alone NEVER proves causal XAU direction.
 * Release actual/consensus, firstprint and time-gated data are authoritative
 * only if independently certified (otherwise research candidates).
 */
const VERSION="GOLD_GLOBAL_NEWS_EVENT_CONDITION_ROUTER_V1_20261018";
const MIN=60000, HOUR=60*MIN;
const TIME=/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/i;
const isnum=x=>typeof x==="number"&&Number.isFinite(x);
function ms(x,name){
 if(typeof x!=="string"||!TIME.test(x)||!Number.isFinite(Date.parse(x)))
  throw Error("NEWS_OFFSET_TIMESTAMP_REQUIRED_"+name);
 return Date.parse(x);
}
function hostname(url){
 if(typeof url!=="string")return null;
 const m=/^https:\/\/([^\/?#]+)(?:[\/?#]|$)/i.exec(url);
 return m?m[1].toLowerCase():null;
}
function publisher(registry,news){
 const source=registry.sources.find(s=>s.id===news.publisher);
 if(!source)throw Error("UNREGISTERED_NEWS_PUBLISHER");
 if(source.jurisdiction!=="GLOBAL" && source.jurisdiction!==news.jurisdiction)
  throw Error("PUBLISHER_JURISDICTION_MISMATCH");
 if(!source.eventKinds.includes(news.eventKind))throw Error("PUBLISHER_EVENT_KIND_NOT_AUTHORIZED");
 const host=hostname(news.sourceUrl);
 if(!host||!source.domains.some(d=>host===d||host.endsWith("."+d)))
  throw Error("PUBLISHER_DOMAIN_NOT_TRUSTED");
 return source;
}
const byTag={
 K01:[["ORG02","TRANSMISSION"]],K02:[["ORG01","TRANSMISSION"]],
 K03:[["ORG02","TRANSMISSION"]],K04:[["ORG01","TRANSMISSION"]],
 K06:[["ORG02","TRANSMISSION"]],K07:[["ORG01","TRANSMISSION"]],
 K08:[["ORG02","TRANSMISSION"]],K09:[["ORG01","TRANSMISSION"]],
 K10:[["ORG02","TRANSMISSION"]],K11:[["ORG01","TRANSMISSION"]],
 K12:[["ORG03","TRIGGER"],["ORG12","AMPLIFIER"]],
 K13:[["ORG10","AMPLIFIER"],["ORG12","AMPLIFIER"]],
 K16:[["ORG02","TRANSMISSION"]],K17:[["ORG01","TRANSMISSION"]],
 K18:[["ORG01","TRANSMISSION"]],K19:[["ORG02","TRANSMISSION"]],
 K20:[["ORG02","TRANSMISSION"]],K21:[["ORG01","TRANSMISSION"]],
 K23:[["ORG02","TRANSMISSION"]],K24:[["ORG01","TRANSMISSION"]],
 K25:[["ORG09","TRIGGER"]],K26:[["ORG11","TRIGGER"]],
 K27:[["ORG06","TRIGGER"],["ORG08","COMPETING"]],
 K28:[["ORG07","TRIGGER"]],K29:[["ORG04","TRIGGER"],["ORG08","COMPETING"]],
 K30:[["ORG05","TRIGGER"]],
 K31:[["ORG03","TRIGGER"],["ORG12","COMPETING"]],
 K32:[["ORG03","TRANSMISSION"]],
 K33:[["ORG09","TRIGGER"]],K34:[["ORG09","TRIGGER"]],
 K35:[["ORG09","AMPLIFIER"]],K36:[["ORG10","AMPLIFIER"]],
 K37:[["ORG04","COMPETING"],["ORG02","TRANSMISSION"]],
 K38:[["ORG05","COMPETING"]],
 K39:[["ORG01","COMPETING"],["ORG02","COMPETING"]],
 K40:[["ORG01","COMPETING"],["ORG02","COMPETING"]],
 K41:[["ORG02","TRANSMISSION"]],K42:[["ORG01","TRANSMISSION"]],
 K43:[["ORG02","TRANSMISSION"]],K44:[["ORG01","TRANSMISSION"]],
 K45:[["ORG02","TRANSMISSION"]],K46:[["ORG01","TRANSMISSION"]],
 K47:[["ORG02","COMPETING"],["ORG01","COMPETING"]],
 K48:[["ORG01","COMPETING"],["ORG02","COMPETING"]]
};
function route(news,{asof,registry}){
 if(!news||typeof news!=="object"||!registry||!Array.isArray(registry.sources))
  throw Error("NEWS_ROUTE_CONTRACT_INVALID");
 if(!news.id||!news.jurisdiction||!news.eventKind)throw Error("NEWS_EVENT_ID_REGION_KIND_REQUIRED");
 const moment=ms(asof,"asof"),origin=ms(news.eventTime,"eventTime"),
  pub=ms(news.publishedAt,"publishedAt"),avail=ms(news.availableAt,"availableAt"),
  detect=ms(news.detectedAt,"detectedAt");
 if(pub<origin||avail<pub||detect<avail)throw Error("NEWS_TEMPORAL_ORDER_INVALID");
 const src=publisher(registry,news);
 const empty={id:news.id,source:src.id,jurisdiction:news.jurisdiction,
  eventKind:news.eventKind,eventTime:news.eventTime,publishedAt:news.publishedAt,
  availableAt:news.availableAt,detectedAt:news.detectedAt,
  asof,status:"PENDING_FIRST_ACCESS",conditions:[],unknown:[],candidateOrgs:[],
  economicDirection:"UNKNOWN",xauPrediction:"NOT_ESTIMATED",action:null,tradeAllowed:false};
 if(detect>moment)return empty;
 const primary=src.role==="PRIMARY_RELEASE";
 const firstprint=primary&&news.firstprintVerified===true&&
  typeof news.firstprintEvidenceId==="string"&&news.firstprintEvidenceId.length>8;
 const conditions=[], unknown=[];
 const add=id=>{if(!conditions.includes(id))conditions.push(id);};
 function dataGap(field){unknown.push("MISSING_OR_UNVERIFIED_"+field);}
 function compare(name,positive,negative,equal){
  const d=news.data?.[name];
  if(!d||!isnum(d.actual)||!isnum(d.consensus)||d.consensusVerified!==true||
   !d.actualAvailableAt||!d.consensusAvailableAt){dataGap(name);return;}
  const tActual=ms(d.actualAvailableAt,name+"_actual"),tConsensus=ms(d.consensusAvailableAt,name+"_consensus");
  if(tActual>moment||tActual<pub||tConsensus>=origin){dataGap(name+"_time");return;}
  // Precision/rounding comes from the publisher's raw reported precision.
  const tol=(isnum(d.epsilon)&&d.epsilon>=0&&d.epsilon<=0.1)?d.epsilon:1e-9;
  const diff=d.actual-d.consensus;
  if(diff>tol) add(positive);
  else if(diff< -tol)add(negative);
  else if(equal)add(equal);
 }
 switch(news.eventKind){
  case "CPI":
   if(news.jurisdiction==="US"){
    compare("headline","K01","K02","K05");
    compare("core","K16","K17",null);
   }else compare("headline","K41","K42",null);
   break;
  case "NFP":
   if(news.jurisdiction!=="US")throw Error("NON_US_NFP_UNSUPPORTED_USE_EMPLOYMENT");
   compare("employment","K03","K04",null);
   compare("wages","K06","K18",null);
   compare("unemployment","K07","K19",null);
   break;
  case "EMPLOYMENT":
   if(news.jurisdiction==="US")throw Error("US_EMPLOYMENT_EXPECT_NFP");
   compare("employment","K43","K44",null);break;
  case "PCE":
   if(news.jurisdiction!=="US")throw Error("PCE_JURISDICTION_REQUIRES_US");
   compare("headline","K45","K46",null);break;
  case "GDP":
   compare("growth","K47","K48",null);break;
  case "CB_DECISION":{
   const d=news.data?.rate;
   if(d&&isnum(d.actual)&&isnum(d.consensus)&&d.consensusVerified===true&&
      d.actualAvailableAt&&d.consensusAvailableAt&&
      ms(d.actualAvailableAt,"rate_actual")<=moment&&
      ms(d.consensusAvailableAt,"rate_prior")<origin&&
      ms(d.actualAvailableAt,"rate_actual")>=pub){
    compare("rate","K20","K21","K22");
   }else{add("K39");dataGap("rate_surprise");}
   break;
  }
  case "CB_PRESSER":
   add("K40");
   // Speech opening ≠ unknown later speech surprise. Never infer from keywords.
   dataGap("guidance_first_sentence_evidence");
   break;
  case "CB_GUIDANCE":{
   const g=news.guidance;
   if(g&&["HAWKISH","DOVISH"].includes(g.vsExpectation)&&
      g.priorExpectationVerified===true&&g.sourceTextVerified===true&&
      g.firstSentenceAvailableAt&&g.priorExpectationAvailableAt&&
      ms(g.firstSentenceAvailableAt,"guidance_line")<=moment&&
      ms(g.firstSentenceAvailableAt,"guidance_line")>=avail&&
      ms(g.priorExpectationAvailableAt,"prior_guidance")<origin&&
      typeof g.sourceTextEvidenceId==="string"&&g.sourceTextEvidenceId.length>=9){
    add(g.vsExpectation==="HAWKISH"?"K23":"K24");
   }else dataGap("guidance_relative_to_pre_known_expectations");
   break;
  }
  case "CB_RESERVE":
  case "TRADE_POLICY":
  case "GEOPOLITICS":
  case "FUNDING":
  case "PHYSICAL_GOLD":
  case "ETF_FLOW":
  case "ENERGY":{
   const map={
    CB_RESERVE:{BUY:"K25",SELL:"K26"},
    TRADE_POLICY:{TIGHTEN:"K27",EASE:"K28"},
    GEOPOLITICS:{ESCALATE:"K29",DEESCALATE:"K30"},
    FUNDING:{WORSEN:"K31",EASE:"K32"},
    PHYSICAL_GOLD:{RISE:"K33",FALL:"K34"},
    ETF_FLOW:{INFLOW:"K35",OUTFLOW:"K36"},
    ENERGY:{DISRUPT:"K37",RESTORE:"K38"}
   };
   const a=news.change;
   if(a&&map[news.eventKind][a.direction]&&a.evidenceAvailableAt&&
     a.factualEvidenceVerified===true&&a.sourceEvidenceId?.length>=9&&
     ms(a.evidenceAvailableAt,"event_change")>=pub&&
     ms(a.evidenceAvailableAt,"event_change")<=moment){
     add(map[news.eventKind][a.direction]);
   }else dataGap("independent_change_evidence");
   break;
  }
  default: dataGap("unsupported_event_kind");
 }
 // A valid domain is not a verified causal mechanism.
 const isSecondary=["SECONDARY_NEWS","MARKET_OBSERVATION","LAGGED_POSITION_REPORT","LAGGED_AGGREGATE_REPORT"].includes(src.role);
 const conditionStatus=conditions.length===0?"CONDITIONS_UNKNOWN":
   firstprint?"FIRSTPRINT_ATTESTED_NOT_CAUSAL":
   isSecondary?"SECONDARY_OR_LAGGED_CONTEXT_ONLY":"RETROSPECTIVE_OR_UNVERIFIED";
 const seen=new Map();
 for(const id of conditions)for(const [org,role] of (byTag[id]??[])){
  const key=org+"|"+role;
  if(!seen.has(key))seen.set(key,{org,role,triggerTags:[]});
  seen.get(key).triggerTags.push(id);
 }
 const orgs=[...seen.values()].map(x=>({...x,confidence:"UNVALIDATED_HYPOTHESIS"}));
 const conflicting=orgs.some(x=>x.org==="ORG01")&&orgs.some(x=>x.org==="ORG02");
 return {...empty,status:conditionStatus,conditions,unknown,candidateOrgs:orgs,
  hasCompetingRateChannels:conflicting,firstprintAttested:firstprint,
  firstprintScope:"source provenance only; not proof gold transmission",
  countAsIndependentPriceCause:false};
}
function routeMany(news,{asof,registry,overlapMinutes=240}){
 if(!Array.isArray(news)||!Number.isInteger(overlapMinutes)||overlapMinutes<0)
  throw Error("NEWS_BATCH_INVALID");
 const ids=new Set();for(const x of news){if(ids.has(x.id))throw Error("DUPLICATE_NEWS_EVENT_ID");ids.add(x.id);}
 const outputs=news.map(x=>route(x,{asof,registry}));
 const visible=outputs.filter(x=>x.status!=="PENDING_FIRST_ACCESS")
  .sort((a,b)=>ms(a.eventTime,"eventTime")-ms(b.eventTime,"eventTime")||
    ms(a.detectedAt,"detectedAt")-ms(b.detectedAt,"detectedAt"));
 const episodes=[];
 for(const e of visible){
  const t=ms(e.eventTime,"eventTime");
  // Reporting-overlap grouping, not independent causal attribution.
  const last=episodes.at(-1);
  if(last&&t-last.lastEventMs<=overlapMinutes*MIN){
   last.ids.push(e.id);last.lastEventMs=Math.max(t,last.lastEventMs);
   last.regions=[...new Set([...last.regions,e.jurisdiction])];
   last.conditions=[...new Set([...last.conditions,...e.conditions])];
  }else episodes.push({ids:[e.id],firstEventMs:t,lastEventMs:t,
    regions:[e.jurisdiction],conditions:e.conditions.slice()});
 }
 return {version:VERSION,asof,events:outputs,
  overlappingEpisodes:episodes.map(({firstEventMs,lastEventMs,...e})=>({
   ...e,firstEventTime:new Date(firstEventMs).toISOString(),lastEventTime:new Date(lastEventMs).toISOString(),
   causalAttribution:"UNVERIFIED_OVERLAPPING_INFORMATION"})),
  audit:{total:outputs.length,visible:visible.length,pending:outputs.length-visible.length,
   withConditions:visible.filter(x=>x.conditions.length).length,
   firstprintAttested:visible.filter(x=>x.firstprintAttested).length,
   tradeSignals:0},tradeAllowed:false};
}
module.exports={VERSION,route,routeMany};
