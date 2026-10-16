"use strict";
const F=require("./v18_128_adversarial_scenarios"),
 E=require("./v20_r3_heldout_200_6families");
function parity(){
 const modes=["slow_ramp","gap_crash","false_break","flat_trap",
   "whipsaw","random_walk","fat_tails","regime_flip"];
 let n=0,maxAbs=0,wrong=0,checks=[];
 for(let j=0;j<modes.length;j++)for(let k=1;k<=8;k++){
  const seed=8000+97*k+j*307,p=F.series(modes[j],seed);
  for(const f of [.008,.025]){
   const z=E.replay(p,f,"off");
   const error=z.final-z.control;
   if(Math.abs(error)>1e-8)wrong++;
   maxAbs=Math.max(maxAbs,Math.abs(error));n++;
   checks.push({mode:modes[j],seed,fee:f,delta:error,overrides:z.overrides});
  }
 }
 return {contract:"EXPOSED_DIAGNOSTIC_ONLY",
  n,wrong,maxAbs,passed:n===128&&wrong===0,
  failures:checks.filter(x=>Math.abs(x.delta)>1e-8)};
}
if(require.main===module)console.log(JSON.stringify(parity(),null,2));
module.exports={parity};
