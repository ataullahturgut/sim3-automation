"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const V=require("./v21_monthly_2023_walk");
const FEE=.008;
test("strict source parsing and temporal guard",()=>{
 const p={tt:"2023-01-03T06:00:00.000Z",t:Date.parse("2023-01-03T06:00:00Z"),
  r4:"0.3",r92:"0.9",r276:"1.3",rv:"0.2",dd276:"-0.5",
  observed:{nq6:"1.2",age_nq:"1"}};
 A.throws(()=>V.inputFeatures(p,p.t,"crossmarket"),/LEAK/);
 A.throws(()=>V.inputFeatures(p,p.t+3600000,"crossmarket"),/MATURED/);
 A.equal(V.inputFeatures(p,p.t+10800000,"crossmarket").nq6,1.2);
 p.observed.age_nq="0";
 A.equal(V.inputFeatures(p,p.t+10800000,"crossmarket").nq6,undefined);
});
test("fee paid only on actual buy and sell, not HOLD",()=>{
 const s={cash:100,units:0,position:"CASH",fees:0,trades:0,
   peak:100,maxDD:0,lastNAV:100};
 V.settle(s,"WAIT",100);A.equal(s.fees,0);
 V.settle(s,"BUY",100);A.equal(s.trades,1);
 A.ok(Math.abs(s.units-.992)<1e-10);
 const n=V.settle(s,"WAIT",100);A.ok(Math.abs(n-98.4064)<1e-8);
 A.equal(s.fees,.8);
 V.settle(s,"SELL",100);A.ok(Math.abs(s.cash-98.4064)<1e-8);
 A.equal(s.trades,2);A.ok(s.fees>1.59&&s.fees<1.61);
});
test("missing crossmarket isn't imputed",()=>{
 const p={t:0,r4:".3",r92:".9",r276:"1.3",rv:".2",dd276:"-.5",observed:null};
 A.equal(V.inputFeatures(p,3*3600000,"crossmarket").nq6,undefined);
});
test("monthly portfolio learning doesn't silently create data on empty input",()=>{
 const s=V.replay([],[]);
 A.equal(s.monthCount,0);
 A.equal(s.agents.price_only.endingNAV,100);
});
