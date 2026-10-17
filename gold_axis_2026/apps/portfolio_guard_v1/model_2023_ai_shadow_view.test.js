"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path");
const {read}=require("./model_2023_ai_shadow_view");
const result=read(),audit=result.portfolioAudit;
test("Jan-Feb 2023 actual gated one-source 2022Q4-pretrained model",()=>{
 assert.equal(result.pretrain.bars,5865);
 assert.equal(result.pretrain.ruleCount,3);
 assert.equal(result.janFebBars,3750);
 assert.equal(result.gateCalls,3750);
 assert.equal(result.coreCalls,3750);
 assert.equal(result.dates.length,59);
 assert.equal(result.dates[0].date,"2023-01-01");
 assert.equal(result.dates.at(-1).date,"2023-02-28");
 assert.equal(result.dates.find(z=>z.date==="2023-01-03").bars,92);
 assert.equal(result.dates.find(z=>z.date==="2023-01-06").bars,92);
 assert.equal(result.dates.find(z=>z.date==="2023-01-07").bars,0);
 assert.equal(result.dates.find(z=>z.date==="2023-02-02").core.s2.direction,-1);
});
test("research candidate triggers and counterfactual baselines, no invented GPT investments",()=>{
 assert.equal(audit.attentionCount,156);
 assert.equal(audit.quarantinedEconomicEvents,4);
 assert.equal(audit.aiUsed,0);
 assert.equal(result.aiProviderConnected,false);
 assert.equal(audit.gptRuntimeConnected,false);
 assert.equal(audit.originalPITEventVerified,false);
 assert.equal(audit.bankTradeAuthorized,false);
 assert.equal(audit.arms.CORE.finalLiquidatableUSD,100);
 assert.equal(audit.reference.cashUSD,100);
 assert.ok(audit.reference.buyHoldLiquidatableUSD<100);
 for(const name of ["AI","HYBRID"]){
  assert.equal(audit.arms[name].transactions.length,0);
  assert.equal(audit.arms[name].finalLiquidatableUSD,100);
 }
 const events=result.dates.filter(x=>x.observedArchiveMacroWaves);
 assert.deepEqual(events.map(e=>e.date),[
  "2023-01-06","2023-01-12","2023-02-03","2023-02-14"]);
});
test("client view and API are actually connected, but AI not faked as a result",()=>{
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 const js=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 const server=fs.readFileSync(path.join(__dirname,"server.js"),"utf8");
 for(const id of ["ai2023","ai23Bars","ai23Attention","ai23Macro","ai23GPT",
  "ai23Portfolio","ai23Start","ai23Next","ai23End","ai23Slider",
  "ai23Current","ai23Table","ai23Status","ai23Source"]){
  assert.match(html,new RegExp('id="'+id+'"'));
 }
 assert.match(html,/href="#ai2023"/);
 assert.match(js,/function ai23Render/);
 assert.match(js,/ai23Load\(\)/);
 assert.match(js,/\/api\/model\/2023\/jan-feb-ai-shadow/);
 assert.match(server,/janFebAI\.read\(\)/);
});
