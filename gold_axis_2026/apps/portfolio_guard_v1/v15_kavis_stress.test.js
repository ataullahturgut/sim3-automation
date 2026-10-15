"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const C=require("./v15_kavis_cekirdek");
const DAY=C.DAY,HOUR=C.HOUR,base=Date.parse("2020-01-01T00:00:00Z");
const T=(d,h=6)=>new Date(base+d*DAY+h*HOUR).toISOString();
const obs=(d,pos="CASH",r=0)=>({asof:T(d),featureAvailableAt:T(d),
 position:pos,market:{r4:r,r1:r*2,r3:r*3,rv:Math.abs(r),dd:Math.min(0,r)}});
test("AUDIT STRESS: extremely large/small positive prices never produce infinite log returns",()=>{
 const s=C.make(),sig=C.signal(s,obs(0));
 C.receiveQuote(s,{at:T(0,9),price:1e-200,isBankCheckpoint:true});
 const z=C.receiveQuote(s,{at:T(1,12),price:1e200,isBankCheckpoint:true});
 const v=z.matured.find(e=>e.h===1);
 A.ok(v&&Number.isFinite(v.gross),JSON.stringify(v));
 A.ok(Number.isFinite(v.entry)&&Number.isFinite(v.exit));
 A.ok(Number.isFinite(s.heads.ENTRY[1].linear.w[0]));
 A.doesNotThrow(()=>C.restore(C.checkpoint(s)));
});
test("AUDIT STRESS: flat market eventually rejects two-way bank fees",()=>{
 const s=C.make({minMaturedLabels:3,confidenceZ:.35});
 let position="CASH",actions=[];
 for(let d=0;d<180;d++){
   const b=C.signal(s,obs(d,position));
   const fill=C.receiveQuote(s,{at:T(d,9),price:100,isBankCheckpoint:true}).fills[0];
   position=fill.intendedPosition;
   if(d>=150&&b.decision.action!=="WAIT")actions.push({d,act:b.decision.action,score:b.decision.score});
 }
 A.deepEqual(actions,[]);
 A.ok(s.heads.ENTRY[56].n>2&&s.heads.EXIT[7].n>10);
});
test("AUDIT STRESS: deterministic volatile alternating sequence stays finite without outside time data",()=>{
 const s=C.make({minMaturedLabels:4,maxHypotheticalDownsidePct:5});
 let position="CASH",seed=123456789,price=100;
 for(let d=0;d<460;d++){
   seed=(1664525*seed+1013904223)>>>0;
   const shock=(seed/2**32-.5)*9;
   const sign=C.signal(s,obs(d,position,shock));
   price*=Math.exp(.01*shock);
   const x=C.receiveQuote(s,{at:T(d,9),price,isBankCheckpoint:true});
   A.equal(x.fills.length,1);
   position=x.fills[0].intendedPosition;
   A.ok(["BUY","SELL","WAIT"].includes(sign.decision.action));
   A.ok(sign.decision.score===null||Number.isFinite(sign.decision.score));
   A.ok(Number.isFinite(s.risk.lambda));
   if(d%50===0)A.doesNotThrow(()=>C.restore(C.checkpoint(s)));
 }
 A.ok(s.learning.matured>350);
});
