"use strict";
/** Independently specified fictional scenario generator for audit sensitivity.
 * No actual XAU/BID/ASK. NOT a statistically blind holdout.
 */
const Benchmark=require("./v18_kavis_dayaniqlilik");
const F=require("./v18_128_adversarial_scenarios");
const Audit=require("./v20_audit_128_economic");
const modes=["late_crash_recovery","successive_selloffs","trend_exhaustion",
 "compress_break","sawtooth_reversal","vol_cluster","delayed_rally","double_dip"];
function rnd(seed){let x=(seed*2654435761)>>>0;
 return ()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x/4294967296;};
}
function world(mode,seed){
 const gen=rnd(seed),N=320,log=[Math.log(100)];
 for(let i=1;i<N;i++){
  let drift=0;
  if(mode==="late_crash_recovery")drift=i<90?.006:i<96?-.070:i<175?.011:.0008;
  if(mode==="successive_selloffs")drift=.003+(i%61===3?-.13:0)+(i%61===5?.09:0);
  if(mode==="trend_exhaustion")drift=i<185?.008:i<210?-.024:-.0007;
  if(mode==="compress_break")drift=i<160?.0001:i<240?.014:-.009;
  if(mode==="sawtooth_reversal")drift=Math.floor(i/19)%2===0?.011:-.013;
  if(mode==="vol_cluster")drift=.002+(i%95<13?(gen()-.5)*.10:(gen()-.5)*.015);
  if(mode==="delayed_rally")drift=i<130?-.009:i<230?.014:.002;
  if(mode==="double_dip")drift=i<100?.009:i<120?-.045:i<180?.014:i<195?-.035:.012;
  drift+=(gen()-.5)*.008;
  log.push(log.at(-1)+drift);
 }
 return log.map(x=>Math.exp(x));
}
function simulate(){
 const x=[];
 for(let m=0;m<modes.length;m++)for(let i=1;i<=4;i++){
  const mode=modes[m],seed=101000+m*239+53*i,p=world(mode,seed);
  for(const fee of [.008,.025]){
   const control=F.replay(Benchmark,p,fee);
   const corrected=Audit.replay(require("./v20_kavis_atlas_repaired"),p,fee);
   const old=Audit.replay(require("./v20_kavis_atlas"),p,fee);
   x.push({mode,seed,fee,control,corrected,old,
    delta:+(corrected.capital-control.capital).toFixed(3)});
  }
 }
 const a=x.map(q=>q.delta);
 return {contract:"64_NEWLY_DESIGNED_FICTIONAL_WORLDS_NOT_BLIND",
  createdWithoutHistoricalGold:true,
  worlds:x.length,
  summary:{wins:a.filter(q=>q>0).length,losses:a.filter(q=>q<0).length,
    ties:a.filter(q=>q===0).length,
    avgV18:x.reduce((s,z)=>s+z.control.capital,0)/x.length,
    avgRepair:x.reduce((s,z)=>s+z.corrected.capital,0)/x.length,
    avgOriginal:x.reduce((s,z)=>s+z.old.capital,0)/x.length,
    minRepaired:Math.min(...x.map(z=>z.corrected.capital)),
    anyAdvisorActivated:x.reduce((s,z)=>s+z.corrected.adviser,0),
    matured1:x.reduce((s,z)=>s+z.corrected.trained1,0),
    matured2:x.reduce((s,z)=>s+z.corrected.trained2,0)},
  summaryByWorld:modes.map(k=>{
   const a=x.filter(q=>q.mode===k);
   return {mode:k,V18:+(a.reduce((s,z)=>s+z.control.capital,0)/a.length).toFixed(3),
     audit:+(a.reduce((s,z)=>s+z.corrected.capital,0)/a.length).toFixed(3),
     losses:a.filter(z=>z.delta<0).length};
  }),rows:x};
}
if(require.main===module)console.log(JSON.stringify(simulate(),null,2));
module.exports={world,simulate};
