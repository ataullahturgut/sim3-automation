"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),
 path=require("node:path"),vm=require("node:vm");
const A=require("./v11_ann_mlp"),V=require("./v11_ann_research");
const {loadFullRows}=require("./v8_regret_engine");
const {requestHandler}=require("./server");
const eq=(a,b,e=.000035)=>assert.ok(Math.abs(a-b)<e,String(a)+" != "+String(b));
let D;const data=()=>D??(D=V.dataset(loadFullRows().rows));

test("real two-hidden-layer ANN gradients match finite differences",()=>{
 assert.deepEqual([A.INPUTS,A.WIDTH1,A.WIDTH2,A.OUTPUTS],[14,12,8,2]);
 const w=A.init(32),x=Array.from({length:14},(_,i)=>Math.sin(i+2)/2),y=[.17,-.29];
 const grad=A.gradient(w,A.forward(w,x),y).g;
 const loss=()=>{let z=A.forward(w,x).o;
  return (A.huber(z[0]-y[0])[0]+A.huber(z[1]-y[1])[0])/2;};
 for(const [k,i,j] of [["W1",1,2],["W2",2,4],["W3",1,1]]){
  const old=w[k][i][j],delta=1e-5;
  w[k][i][j]=old+delta;const hi=loss();
  w[k][i][j]=old-delta;const lo=loss();w[k][i][j]=old;
  eq((hi-lo)/(2*delta),grad[k][i][j],1e-7);
 }
});
test("true next-bank-fill costed 4d and 14d labels",()=>{
 const d=data();assert.equal(d.records,6724);
 assert.equal(d.sampleCount,947);assert.equal(d.bank.length,2771);
 const q=d.samples[0];assert.equal(q.entryUTC,"2023-01-03T09:00:00.000Z");
 const exit=d.bank.find(x=>x.tt===q.exit14UTC);
 eq(q.y[1],100*((1-.008)**2*exit.p/q.priceAtEntry-1),1e-9);
 assert.ok(q.exit14Ts-q.entryTs>=336*3600000);
});
test("train only matured labels, no label crosses fold start",()=>{
 const d=data();
 for(const [when,n] of [
  ["2024-01-02T06:00:00Z",246],
  ["2025-01-07T06:00:00Z",504],
  ["2026-02-02T06:00:00Z",775]
 ]){
  const arr=V.chronologicalTraining(d,when);
  assert.equal(arr.length,n);
  assert.ok(arr.every(x=>x.exit14Ts<Date.parse(when)));
 }
});
test("2024 and 2025 uncertainty-calibrated ANN abstains rather than manufacturing gains",()=>{
 const d=data();
 for(const [start,end] of [["2024-01-02T06:00:00Z","2024-12-31T12:00:00Z"],
  ["2025-01-07T06:00:00Z","2025-12-31T12:00:00Z"]]){
  const r=V.simulate(d,{policy:"calibratedAbstain",start,end,initial:100});
  eq(r.final,100);assert.equal(r.trades.length,0);
 }
});
test("2026 baseline, uncertainty gate, online monthly training distinct",()=>{
 const d=data(),base={start:"2026-02-02T06:00:00Z",
  end:"2026-09-30T12:00:00Z",initial:119.753917};
 const a=V.simulate(d,{...base,policy:"netPositive"});
 const b=V.simulate(d,{...base,policy:"calibratedAbstain"});
 const c=V.simulate(d,{...base,policy:"adaptiveMonthly"});
 eq(a.final,105.37865131840464);
 eq(b.final,123.57096211015902);
 eq(c.final,93.94154399163456);
 assert.equal(c.training.length,8);
 assert.equal(b.fees.realBankBidAsk,false);
 assert.equal(b.liveTradingAuthorized,false);
 for(const t of c.trades){
  assert.ok(Date.parse(t.at)>Date.parse(t.asOf));
  assert.ok([6,9,12].includes(new Date(t.at).getUTCHours()));
 }
});
test("perturbation of future bars cannot change prior ANN signals",()=>{
 const cut="2026-05-29T12:00:00Z",args={start:"2026-02-02T06:00:00Z",
  end:cut,initial:119.753917,policy:"netPositive",includePredictions:true};
 const before=V.simulate(data(),args);
 const shifted=loadFullRows().rows.map(r=>r.tt>cut?
  {...r,p:r.p*1.5,c:r.c*1.5,r1:99,r3:99}:r);
 const after=V.simulate(V.dataset(shifted),args);
 eq(before.final,after.final);assert.deepEqual(before.trades,after.trades);
 assert.deepEqual(before.predictions.map(x=>[x.at,x.net4,x.net14,x.desired]),
  after.predictions.map(x=>[x.at,x.net4,x.net14,x.desired]));
});
test("scientific guard rejects ANN live promotion and legacy remains",()=>{
 const r=V.research();
 assert.equal(r.version,"V11_ANN_CORRECTLY_SUPERVISED_20261016");
 assert.equal(r.gate.promote,false);
 assert.equal(r.model.learnAlgorithm,"FULL_BACKPROP_ADAM_HUBER");
 assert.equal(r.gate.independentBlindTest,false);
 let status=0,body="";
 requestHandler({method:"GET",url:"/api/algorithm/v11/ann"},
  {writeHead(s){status=s},end(x){body=x}});
 assert.equal(status,200);assert.equal(JSON.parse(body).gate.promote,false);
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 assert.match(html,/id="runV11Ann"/);
 const script=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 assert.doesNotThrow(()=>new vm.Script(script));
});
