"use strict";
/** PREREG-LOCKED R3 evaluation: NO threshold tuning after reading results.
 * 200 disjoint drift-zero seeds, 6*32 balanced families *2 fee arms.
 * All data synthetic, even if a family looks realistic.
 */
const Model=require("./v20_atlas_r3_gate");
const F=require("./v18_128_adversarial_scenarios");
const C=require("./v20_r3_500_null_calibration");
const LOCK=require("./v20_r3_gate_threshold_lock.json");
if(LOCK.T_OPEN!==1.9||LOCK.locked!==true||LOCK.prereg_commit!=="3c04badbf14c8aede2a5e4b3d1e1bc866af88134")
  throw Error("R3_THRESHOLD_NOT_PREREG_LOCKED");
const T=LOCK.T_OPEN,START=Date.parse("2020-01-01T00:00:00Z"),DAY=86400000;
const at=(d,h)=>new Date(START+d*DAY+h*3600000).toISOString();
function random(seed){let a=seed>>>0;return()=>{a=(Math.imul(a,1664525)+1013904223)>>>0;return (a+.5)/4294967296;};}
function normal(r){return Math.sqrt(-2*Math.log(r()))*Math.cos(2*Math.PI*r());}
const names=["zero_drift","mean_reversion","persistent_trend",
  "regime_transition","fat_tails","volatility_switch"];
function familyWorld(j,seed,index){
 const r=random(seed),p=[100];let prev=0;
 const dir=index<16?1:-1;
 for(let i=1;i<300;i++){
  const z=normal(r);let logReturn=0;
  if(j===0)logReturn=.018*z;
  if(j===1){logReturn=-.65*prev+.018*z;prev=logReturn;}
  if(j===2)logReturn=dir*.007+.012*z;
  if(j===3){const segment=Math.floor(i/50)%4;
    const drift=segment===0?.009:segment===1?0:segment===2?-.009:0;
    logReturn=drift+.014*z;}
  if(j===4){logReturn=.001+.013*z;
    if(r()<.028)logReturn+=(r()<.5?-1:1)*(.09+.06*r());}
  if(j===5){const sigma=Math.floor(i/50)%2===0?.006:.045;
    logReturn=.001+.0+sigma*z;}
  p.push(p.at(-1)*Math.exp(logReturn));
 }
 return p;
}
function replay(prices,fee,gate="gated"){
 const s=Model.create({shadowGate:gate,gateThreshold:T,riskMode:"alert",
   maxDrawdownPct:15,core:{feePerSide:fee}});
 let alignViolations=0;
 for(let i=0;i<prices.length;i++){
  const asof=at(i,6);
  const obs={asof,featureAvailableAt:asof,
   position:s.inner.portfolio.position,
   market:F.features(prices,i),
   bankFeeQuote:{feePerSide:fee,availableAt:asof}};
  const sig=Model.signal(s,obs);
  const fill=Model.quote(s,{at:at(i,9),price:prices[i],
     bankFeePerSide:fee,isBankCheckpoint:true});
  if(!fill.fill)throw Error("R3_MISSING_VERIFIED_BANK_FILL");
  if(sig.gateActive&&fill.portfolio.position!==fill.shadow.risk.position)
   alignViolations++;
  if(sig.ordersSent!==0||fill.ordersSent!==0)
   throw Error("R3_UNAUTHORIZED_BANK_ORDER");
 }
 const b=s.shadow.base,r=s.inner.portfolio;
 return {final:r.nav,control:b.nav,difference:r.nav-b.nav,
  maxDD:r.maxDrawdownPct,baseDD:b.maxDrawdownPct,
  trades:r.trades,baseTrades:b.trades,
  gateOpens:s.audit.gateOpens,gateCloses:s.audit.gateCloses,
  overrides:s.audit.specialistOverrides,
  alignmentViolations:alignViolations,fees:r.feeDollars,
  passive:100*(1-fee)**2*prices.at(-1)/prices[0]};
}
function mean(a){return a.reduce((x,y)=>x+y,0)/a.length;}
function wilson(k,n){const z=1.96,p=k/n,den=1+z*z/n;
 const mid=(p+z*z/(2*n))/den,
 half=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;
 return {low:mid-half,high:mid+half};}
function report(){
 const nullRows=[];
 for(let i=0;i<200;i++){
  const seed=200000+53*i,p=C.nullWorld(seed),
    fees=[.008,.025].map(f=>replay(p,f));
  nullRows.push({seed,falseOpen:fees.some(x=>x.gateOpens>0),fees});
 }
 const falseCount=nullRows.filter(x=>x.falseOpen).length;
 const zeroMean=mean(nullRows.flatMap(w=>w.fees.map(f=>f.difference)));
 const family=[];
 for(let j=0;j<6;j++){
  const cases=[];
  for(let i=0;i<32;i++){
   const seed=410000+j*10000+i*137,p=familyWorld(j,seed,i);
   for(const fee of [.008,.025])
    cases.push({seed,fee,...replay(p,fee)});
  }
  family.push({family:names[j],cases,
    meanDifference:mean(cases.map(x=>x.difference)),
    worse:cases.filter(x=>x.difference< -1e-6).length,
    better:cases.filter(x=>x.difference>1e-6).length,
    equal:cases.filter(x=>Math.abs(x.difference)<=1e-6).length,
    meanNAV:mean(cases.map(x=>x.final)),
    meanBase:mean(cases.map(x=>x.control)),
    maxDD95:[...cases.map(x=>x.maxDD)].sort((a,b)=>a-b)[60]});
 }
 const all=family.flatMap(f=>f.cases);
 const gains=all.map(x=>Math.max(0,x.difference)).sort((a,b)=>b-a);
 const sum=gains.reduce((a,b)=>a+b,0);
 const top3share=sum>0?gains.slice(0,3).reduce((a,b)=>a+b,0)/sum:null;
 const familyChecks=family.every(f=>f.meanDifference>=-1);
 const k=nullRows.filter(x=>x.falseOpen).length;
 const gates={falseOpenRate:k/200<=.05,
   nullMeanDelta:zeroMean>=-.10,
   meanRevDelta:family[1].meanDifference>=-.10,
   familyFloor:familyChecks,
   top3Concentration:top3share!==null&&top3share<=.4,
   aligned:all.every(x=>x.alignmentViolations===0)&&
    nullRows.every(x=>x.fees.every(f=>f.alignmentViolations===0))};
 const result={kind:"R3_PREREG_SIX_FAMILY_FICTIONAL_ONLY",
  calibrationT:T,zeroSeeds:200,familySeeds:192,feeArms:[.008,.025],
  zero:{falseOpens:k,falseRate:k/200,wilson95:wilson(k,200),meanDelta:zeroMean},
  family:family.map(({cases,...rest})=>rest),
  concentration:{top3share:top3share,totalPositiveSum:sum},
  gates,allPass:Object.values(gates).every(Boolean),
  economics:{meanCandidate:mean(all.map(x=>x.final)),
   meanBaseline:mean(all.map(x=>x.control)),
   meanMaxDD:mean(all.map(x=>x.maxDD)),
   minCandidate:Math.min(...all.map(x=>x.final)),
   totalOverrides:all.reduce((x,y)=>x+y.overrides,0),
   beatsCash:all.filter(x=>x.final>100).length,
   beatsPassive:all.filter(x=>x.final>x.passive).length},
  allRows:all,nullRows};
 return result;
}
if(require.main===module){
 const r=report();console.log(JSON.stringify(r,null,2));
 // Allow CI to COMPLETE and upload failures, let verification stage
 // decide "pass or reject" instead of suppressing weak performance.
}
module.exports={report,replay,wilson,familyWorld};
