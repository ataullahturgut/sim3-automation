"use strict";
/** R3 frozen PREREG null calibration, no outcome-based tune.
 * 500 paired seeds, 300 bank checkpoints, two fees, max path-level
 * 2-consecutive-block t statistic; grid 0..12 step 0.1.
 */
const R3=require("./v20_atlas_r3_gate"),Core=require("./v18_kavis_dayaniqlilik"),
 F=require("./v18_128_adversarial_scenarios");
const BASE=Date.parse("2020-01-01T00:00:00Z"),D=86400000;
const at=(i,h)=>new Date(BASE+i*D+h*3600000).toISOString();
function rand(seed){let v=seed>>>0;return()=>{
 v=(Math.imul(1664525,v)+1013904223)>>>0;return (v+.5)/4294967296;};}
function normal(r){return Math.sqrt(-2*Math.log(r()))*
 Math.cos(2*Math.PI*r());}
function nullWorld(seed){
 const r=rand(seed),p=[100];
 for(let i=1;i<300;i++)p.push(p.at(-1)*Math.exp(.018*normal(r)));
 return p;
}
function regime(m){
 if(m.r4< -1.5||m.rv>3||m.dd< -5)return "STRESS";
 if(m.r4>0&&m.r1>0)return "RALLY";
 return "QUIET";
}
function shadowOnly(prices,fee){
 const base=Core.create({feePerSide:fee}),
  led=R3.create({core:{feePerSide:fee}});
 const a=led.shadow.base,b=led.shadow.risk,returns=[];
 for(let i=0;i<prices.length;i++){
  const market=F.features(prices,i),asof=at(i,6);
  const obs={asof,featureAvailableAt:asof,
   position:a.position,market,
   bankFeeQuote:{feePerSide:fee,availableAt:asof}};
  Core.signal(base,obs);
  const q=Core.quote(base,{at:at(i,9),price:prices[i],
    bankFeePerSide:fee,isBankCheckpoint:true});
  if(!q.fill)throw Error("R3_SHADOW_CALIBRATION_BAD_FILL");
  const r=R3.rule(b.position,regime(market));
  const x=R3.apply(a,q.fill.suggestedAction,prices[i],fee);
  const y=R3.apply(b,r,prices[i],fee);
  returns.push(y-x);
 }
 return {returns,
  maxPairT:R3.reconstruct(returns,0).maxPairT,
  lastBaseNAV:a.nav,lastRiskNAV:b.nav};
}
function calibrate(){
 const pairs=[];
 for(let i=0;i<500;i++){
  const seed=100000+37*i,p=nullWorld(seed);
  const m1=shadowOnly(p,.008).maxPairT,
        m2=shadowOnly(p,.025).maxPairT;
  pairs.push({seed,maxPair:Math.max(m1,m2),fee008:m1,fee025:m2});
 }
 let threshold=null;
 for(let i=0;i<=120;i++){
  const t=i/10;
  if(pairs.filter(p=>p.maxPair>=t).length/500<=.05){
    threshold=t;break;
  }
 }
 return {kind:"R3_CALIBRATION_ONLY_NO_OUTCOME_TUNING",
  worldCount:500,feeArms:[.008,.025],
  seeds:"100000+37*i, i=0..499",threshold,
  nullPairOpens:threshold===null?null:
    pairs.filter(p=>p.maxPair>=threshold).length,
  maxOfMax:Math.max(...pairs.map(p=>p.maxPair)),
  minOfMax:Math.min(...pairs.map(p=>p.maxPair)),
  calibrationPassed:threshold!==null,pairs};
}
if(require.main===module)console.log(JSON.stringify(calibrate(),null,2));
module.exports={calibrate,nullWorld,shadowOnly,regime};
