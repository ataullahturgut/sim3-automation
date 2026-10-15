"use strict";
const $=function(id){return document.getElementById(id);};
const format=new Intl.NumberFormat("tr-TR",{minimumFractionDigits:2,maximumFractionDigits:2});
let response=null,mode="event15m";
function money(v){return format.format(v)+" $";}
function pct(v){return (v>=0?"+":"")+format.format(v)+"%";}
function escapeText(v){
 return String(v===null||v===undefined?"—":v).replace(/&/g,"&amp;")
   .replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
const labels={event15m:"Olay destekli · 15 dk",price15m:"Yalnız fiyat · 15 dk",legacy3h:"Eski model · 3 saat"};
function cell(v){return "<td>"+v+"</td>";}
function table(headers,body){
 return "<table><thead><tr>"+headers.map(function(x){return "<th>"+escapeText(x)+"</th>";}).join("")+
 "</tr></thead><tbody>"+body.join("")+"</tbody></table>";
}
function chart(days){
 const W=800,H=280,padL=63,padR=16,padT=23,padB=38;
 const values=days.map(function(d){return d.netValue;});
 const min=Math.floor((Math.min(...values)-1)/5)*5,max=Math.ceil((Math.max(...values)+1)/5)*5;
 const xr=function(i){return padL+i*(W-padL-padR)/(days.length-1);};
 const yr=function(v){return padT+(max-v)*(H-padT-padB)/(max-min);};
 const coords=values.map(function(v,i){return xr(i).toFixed(1)+","+yr(v).toFixed(1);});
 const baseY=yr(min);
 let svg='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" aria-labelledby="chart-title" role="img">'+
 '<title id="chart-title">Ocak 2026 günlük net portföy değeri</title>';
 for(let i=0;i<=4;i++){
  const v=min+i*(max-min)/4,y=yr(v);
  svg+='<line x1="'+padL+'" y1="'+y+'" x2="'+(W-padR)+'" y2="'+y+'" stroke="#29394b" stroke-width="1"/>'+
       '<text x="'+(padL-9)+'" y="'+(y+4)+'" text-anchor="end">'+format.format(v)+' $</text>';
 }
 svg+='<polygon points="'+xr(0)+','+baseY+' '+coords.join(" ")+' '+xr(30)+','+baseY+
   '" fill="#cfa96f" fill-opacity=".09"/>';
 svg+='<polyline points="'+coords.join(" ")+'" fill="none" stroke="#d8b37b" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>';
 for(let i=0;i<days.length;i++){
  if([0,4,9,14,19,24,30].includes(i)){
   svg+='<text x="'+xr(i)+'" y="'+(H-12)+'" text-anchor="middle">'+(i+1)+' Oca</text>';
  }
  if(days[i].actions.length){
   svg+='<circle cx="'+xr(i)+'" cy="'+yr(values[i])+'" r="6" fill="#d8b37b" stroke="#0c1420" stroke-width="2">'+
       '<title>'+escapeText(days[i].date+' · '+days[i].actions[0].action+' · '+money(values[i]))+'</title></circle>';
  }
 }
 svg+='</svg>';
 return svg;
}
function compare(items,selected){
 return table(["Model","Son portföy","Getiri","Koruma satışı","Durum"],items.map(function(m){
  const sells=m.actions.filter(function(x){return x.action==="SELL_TO_CASH";}).length;
  const cls=m.returnPct>=0?"positive":"negative";
  const summary=selected===m.model?"<small>Seçili model</small>":"";
  return '<tr class="'+(selected===m.model?"emphasis":"")+'">'+
    cell(escapeText(labels[m.model])+summary)+
    cell(money(m.finalUSD))+
    cell('<b class="'+cls+'">'+pct(m.returnPct)+'</b>')+
    cell(sells)+cell(m.terminalAsset==="CASH"?"NAKİT":"ALTIN")+"</tr>";
 }));
}
function transactions(entries) {
 if(!entries.length)return "<p>Bu senaryoda alım / satım yapılmadı.</p>";
 return table(["Türkiye saati","Karar","Ons fiyatı","Gerekçe ve olay kanıtı"],entries.map(function(e){
  const kind=e.action==="BUY_GOLD"?"AL":"SAT";
  let explanation='<b>'+escapeText(e.reason)+'</b>';
  if(e.riskScore!==null&&e.riskScore!==undefined)explanation+='<small>Benzer olay skoru: '+
    format.format(e.riskScore)+" · Örnek uzaklığı: "+format.format(e.nearestDistance)+"</small>";
  if(e.nearestCases&&e.nearestCases.length)explanation+='<small>Yakın vakalar: '+
    e.nearestCases.map(function(z){return escapeText(z.id);}).join(", ")+"</small>";
  return "<tr>"+cell(escapeText(e.tr))+cell('<b class="'+(kind==="AL"?"positive":"negative")+'">'+kind+"</b>")+
   cell(money(e.price))+cell(explanation)+"</tr>";
 }));
}
function daily(items){
 return table(["Tarih","Pozisyon","Net değer","M15 veri sayısı","Karar","Olay penceresi"],items.map(function(d){
  const actions=d.actions.length?d.actions.map(function(x){return escapeText(x.action==="BUY_GOLD"?"AL":"SAT")+" "+x.when;}).join(", "):"TUT / BEKLE";
  const cls=d.actions.length?"emphasis":"";
  return '<tr class="'+cls+'">'+cell(escapeText(d.date))+cell(d.position==="GOLD"?"ALTIN":"NAKİT")+
   cell(money(d.netValue))+cell(d.completeBars)+cell(actions)+cell(escapeText(d.macroWindows.join(", ")||"—"))+"</tr>";
 }));
}
function render(){
 if(!response)return;
 const s=response.comparison.find(function(z){return z.model===mode;});
 if(!s)return;
 const baseline=response.comparison.find(function(z){return z.model==="price15m";});
 const event=response.comparison.find(function(z){return z.model==="event15m";});
 $("finalUSD").textContent=money(s.finalUSD);
 $("profitUSD").textContent="Başlangıç 100,00 $ · Net fark "+money(s.finalUSD-100);
 $("returnPct").textContent=pct(s.returnPct);
 $("benchmark").textContent=money(s.benchmarkBuyHoldUSD);
 $("benchmarkNote").textContent="Aynı kontrol sıklığı ve fiyat kaynağı";
 $("maxDD").textContent=format.format(s.maxDrawdownPct)+"%";
 $("position").textContent=s.terminalAsset==="CASH"?"NAKİT":"ALTIN";
 $("tradesCount").textContent=s.actions.filter(function(x){return x.action==="BUY_GOLD";}).length+
   " AL / "+s.actions.filter(function(x){return x.action==="SELL_TO_CASH";}).length+" SAT";
 $("checksCount").textContent=new Intl.NumberFormat("tr-TR").format(s.checks);
 $("calendarCount").textContent=new Intl.NumberFormat("tr-TR").format(s.fullCalendarSlots);
 $("archivesCount").textContent=s.archiveCases+" olgunlaşmış olay";
 $("notice").textContent="Sabit Ocak 2026 veri görüntüsü · Gerçek banka makası dahil değil · Bağımsız ileri test değil."+
   " Ekonomik nedenler henüz doğrulanmadı. Bu uygulama emir üretmez.";
 $("learningNote").textContent="Ocak'ta olay katmanının fiyat modeline ek kazancı: "+
   money(event.finalUSD-baseline.finalUSD)+
   ". Tanınmayan şok alarmı gerekçe sunar; bu ay ek işlem sağlamamıştır.";
 $("chart").innerHTML=chart(s.days);
 $("comparisonTable").innerHTML=compare(response.comparison,mode);
 $("transactions").innerHTML=transactions(s.actions);
 $("daily").innerHTML=daily(s.days);
 for(const btn of document.querySelectorAll("[data-mode]")){
  btn.classList.toggle("selected",btn.dataset.mode===mode);
  btn.setAttribute("aria-pressed",String(btn.dataset.mode===mode));
 }
}
async function load(){
 try{
  const fetchResult=await fetch("/api/summary",{cache:"no-store"});
  if(!fetchResult.ok)throw new Error("API HTTP "+fetchResult.status);
  response=await fetchResult.json();
  if(response.status!=="RESEARCH_ONLY_NOT_LIVE"||response.comparison.length!==3)throw new Error("FROZEN_RESEARCH_CONTRACT_FAILED");
  $("modelVersion").textContent=response.version;
  $("footerVersion").textContent=response.version;
  $("hashes").innerHTML=Object.entries(response.dataHashes).map(function(pair){
   return '<div class="hashline"><b>'+escapeText(pair[0])+'</b><small> '+escapeText(pair[1].path)+
     '</small><code>'+escapeText(pair[1].gitBlob)+'</code></div>';
  }).join("");
  render();
 }catch(err){
  $("notice").textContent="Uygulama veriyi doğrulayamadı; sonuç gösterilmiyor: "+err.message;
  $("finalUSD").textContent="VERİ HATASI";
 }
}
for(const btn of document.querySelectorAll("[data-mode]")){
 btn.addEventListener("click",function(){mode=btn.dataset.mode;render();});
}
load();

function renderScientificV2(data){
 if(data.stage!=="DIAGNOSTIC_SHADOW_ONLY"||data.archive.archiveRows!==96||!Array.isArray(data.critical)){
  throw new Error("Unexpected scientific audit schema");
 }
 $("v2Raw").textContent=String(data.archive.archiveRows);
 $("v2Unique").textContent=String(data.archive.uniqueCheckpoints);
 $("v2Controls").textContent=String(data.timeSampledControls.count);
 $("v2ControlDrops").textContent=String(data.timeSampledControls.down3);
 $("v2Proven").textContent=String(data.archive.clearlyCausalEvents);
 $("v2Cost").textContent=format.format(data.critical[0].trading.roundTripCommissionBreakEvenPct)+"%";
 $("v2status").textContent="V2 analizi: "+
   data.archive.duplicateAliases+" mükerrer olay kaydı ayrıştırıldı. "+
   "Ekonomik ilk yayın ve neden kanıtlanmadığından vaka skoru tek başına AL/SAT üretmiyor. "+
   "Ocak 2026 V1 portföy sonucu değiştirilmedi.";
 const content=[];
 for(const d of data.critical){
  content.push('<article class="v2decision"><h3>'+escapeText(d.action==="BUY_GOLD"?"ALTIN AL":"NAKDE GEÇ")+
   ' · '+escapeText(new Date(d.utc).toLocaleString("tr-TR",{timeZone:"Europe/Istanbul",dateStyle:"short",timeStyle:"short"}))+
   '</h3><p>V1 işlem fiyatı: <b>'+money(d.decisionPrice)+
   '</b> · Fiyat profilindeki eski benzer-vaka payı: '+pct(d.analog.legacySelectedEventFraction*100)+
   ' · Mükerrer kayıtlar ayrıştırılınca: '+pct(d.analog.correctedSelectedEventFraction*100)+
   ' <em>(bunlar tahmin olasılığı değil)</em></p>'+
   '<p>Benzer bağımsız olay evresi: '+d.sampleQuality.episodesInNine+
   ' · En yakın uzaklık: '+format.format(d.sampleQuality.distance)+
   ' · Ekonomik neden: doğrulanmadı. Takvim kontrol grubu komşularının riskli örnek payı: '+pct(d.control.observedControlFraction*100)+
   ' (olasılık değil)</p>');
  content.push('<div class="v2questionGrid">'+d.questions.map(function(q){
   const status=q.verified?'KONTROL EDİLDİ':'KANIT EKSİK';
   return '<div class="v2question"><b>'+escapeText(q.id)+' · '+escapeText(q.question)+
     '</b><p>'+escapeText(q.answer)+'</p><small>'+status+'</small></div>';
  }).join("")+'</div></article>');
 }
 $("v2decisions").innerHTML=content.join("");
 const items=[
  "Haberlerin ilk yayımı ve aynı andaki piyasa beklentisi arşivde doğrulanmalı",
  "Olay olmayan kontrol günleri eklenmeden risk oranı kalibre edilmiş olasılık sayılmamalı",
  "Benzer olayların farklı kimlikli kopyaları ve üst üste gelen 96 saatlik dönemleri ayrı örnek sayılmamalı",
  "Gerçek banka alış/satış kotasyonları olmadan bir risk alarmının kazanç sağlayacağı varsayılmamalı",
  "Model değişikliği yalnız sonraki ayda sınanmalı; Ocak sonucu görülüp Ocak yeniden başarı testi sayılamaz"
 ];
 $("v2gaps").innerHTML=items.map(function(item){
  return '<p><span class="v2bullet">○</span>'+escapeText(item)+'</p>';
 }).join("");
}
async function loadScientificV2(){
 try{
  const req=await fetch("/api/algorithm/v2",{cache:"no-store"});
  if(!req.ok)throw new Error("HTTP "+req.status);
  renderScientificV2(await req.json());
 }catch(error){
  $("v2status").textContent="V2 bilimsel denetim henüz yüklenemiyor: "+error.message+
    ". Eski model ve ana ekran bu durumdan etkilenmez.";
 }
}
loadScientificV2();
