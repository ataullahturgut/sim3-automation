"use strict";
const $=function(id){return document.getElementById(id);};
const format=new Intl.NumberFormat("tr-TR",{minimumFractionDigits:2,maximumFractionDigits:2});
let response=null,mode="event15m",activeMonth="2026-01";
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
 const suffix=activeMonth==="2026-02"?"Şub":"Oca";
 const yr=function(v){return padT+(max-v)*(H-padT-padB)/(max-min);};
 const coords=values.map(function(v,i){return xr(i).toFixed(1)+","+yr(v).toFixed(1);});
 const baseY=yr(min);
 let svg='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" aria-labelledby="chart-title" role="img">'+
 '<title id="chart-title">'+(activeMonth==="2026-02"?"Şubat":"Ocak")+' 2026 günlük net portföy değeri</title>';
 for(let i=0;i<=4;i++){
  const v=min+i*(max-min)/4,y=yr(v);
  svg+='<line x1="'+padL+'" y1="'+y+'" x2="'+(W-padR)+'" y2="'+y+'" stroke="#29394b" stroke-width="1"/>'+
       '<text x="'+(padL-9)+'" y="'+(y+4)+'" text-anchor="end">'+format.format(v)+' $</text>';
 }
 svg+='<polygon points="'+xr(0)+','+baseY+' '+coords.join(" ")+' '+xr(days.length-1)+','+baseY+
   '" fill="#cfa96f" fill-opacity=".09"/>';
 svg+='<polyline points="'+coords.join(" ")+'" fill="none" stroke="#d8b37b" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>';
 for(let i=0;i<days.length;i++){
  if([0,4,9,14,19,24,days.length-1].includes(i)){
   svg+='<text x="'+xr(i)+'" y="'+(H-12)+'" text-anchor="middle">'+(i+1)+' '+suffix+'</text>';
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
 $("profitUSD").textContent="Başlangıç "+money(s.startUSD)+" · Net fark "+money(s.finalUSD-s.startUSD);
 $("returnPct").textContent=pct(s.returnPct);
 $("benchmark").textContent=money(s.benchmarkBuyHoldUSD);
 $("benchmarkNote").textContent=s.benchmarkNote||"Aynı kontrol sıklığı ve fiyat kaynağı";
 $("maxDD").textContent=format.format(s.maxDrawdownPct)+"%";
 $("position").textContent=s.terminalAsset==="CASH"?"NAKİT":"ALTIN";
 $("tradesCount").textContent=s.actions.filter(function(x){return x.action==="BUY_GOLD";}).length+
   " AL / "+s.actions.filter(function(x){return x.action==="SELL_TO_CASH";}).length+" SAT";
 $("checksCount").textContent=new Intl.NumberFormat("tr-TR").format(s.checks);
 $("calendarCount").textContent=new Intl.NumberFormat("tr-TR").format(s.fullCalendarSlots);
 $("archivesCount").textContent=s.archiveCases+" olgunlaşmış olay";
 $("notice").textContent=(activeMonth==="2026-02"?"Şubat 2026 V1 — Ocak sonu nakitten devredildi":"Ocak 2026 V1 referans")+ " · Gerçek banka makası dahil değil · Bağımsız ileri test değil."+
   " Ekonomik nedenler henüz doğrulanmadı. Bu uygulama emir üretmez.";
 $("learningNote").textContent=(activeMonth==="2026-02"?"Şubat":"Ocak")+" ayında olay katmanının fiyat modeline ek kazancı: "+
   money(event.finalUSD-baseline.finalUSD)+
   (Math.abs(event.finalUSD-baseline.finalUSD)<1e-8?". Bu ay olay katmanı ek getiri sağlamadı.":". İşlem farkı ve net sonuç karar geçmişinden denetlenmelidir.");
 $("modelVersion").textContent=response.version;
 $("footerVersion").textContent=response.version;
 $("monthHeading").textContent="ARAŞTIRMA / "+(activeMonth==="2026-02"?"ŞUBAT":"OCAK")+" 2026";
 $("dailyTitle").textContent=(activeMonth==="2026-02"?"Şubat":"Ocak")+" 2026 · Gün gün";
 $("startingCash").textContent=money(s.startUSD)+" başlangıç";
 $("hashes").innerHTML=Object.entries(response.dataHashes).map(function(pair){
   return '<div class="hashline"><b>'+escapeText(pair[0])+'</b><small> '+escapeText(pair[1].path)+
     '</small><code>'+escapeText(pair[1].gitBlob)+'</code></div>';
 }).join("");
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
async function executeSelectedMonth(){
 const wanted=$("monthSelect").value;
 const control=$("runMonth"),status=$("monthStatus");
 control.disabled=true;
 status.textContent=(wanted==="2026-02"?"Şubat 2026":"Ocak 2026")+" çalıştırılıyor; kaynak imzaları ve kararlar denetleniyor…";
 try{
   const url=wanted==="2026-02"?"/api/months/2026-02/run":"/api/summary";
   const reply=await fetch(url,{cache:"no-store"});
   if(!reply.ok)throw new Error("Sunucu "+reply.status);
   const data=await reply.json();
   if(data.status!=="RESEARCH_ONLY_NOT_LIVE"||data.comparison.length!==3)
     throw new Error("FROZEN_MONTHLY_DATA_CONTRACT_FAILED");
   response=data;activeMonth=wanted;
   render();
   const end=response.comparison.find(x=>x.model==="event15m");
   status.textContent=(wanted==="2026-02"?"Şubat 2026":"Ocak 2026")+" tamamlandı · Başlangıç "+
     money(end.startUSD)+" → Son değer "+money(end.finalUSD)+" · "+
     (end.terminalAsset==="CASH"?"NAKİT":"ALTIN")+
     (end.hypotheticalExitFeeDeducted?" (satılmadan, yalnız teorik satış komisyonuyla değerlenmiş)":"")+
     ". Kurallar geçmişe dönük güncellenmedi.";
 }catch(error){
   status.textContent="Ay çalıştırılamadı: "+error.message+". Önceki sonuç korunuyor.";
 }finally{
   control.disabled=false;
 }
}
$("runMonth").addEventListener("click",executeSelectedMonth);

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


async function runV3Research(){
 const btn=$("runV3"),status=$("v3status");btn.disabled=true;
 status.textContent="V3 geçmiş evreleri, olay epizotları ve Ocak-Şubat sonuçları hesaplanıyor…";
 try{
  const http=await fetch("/api/algorithm/v3",{cache:"no-store"});
  if(!http.ok)throw new Error("API HTTP "+http.status);
  const v=await http.json();
  if(v.status!=="EXPLORATORY_RETROSPECTIVE_NOT_OOS"||v.annual.length!==3||
     v.february.startUSD<119||v.bankSpreadIncluded!==false)throw Error("V3_RESEARCH_SCHEMA_INVALID");
  $("v3FebFinal").textContent=money(v.february.finalUSD);
  $("v3JanFinal").textContent=money(v.january.finalUSD);
  $("v3History").textContent=new Intl.NumberFormat("tr-TR").format(v.history.totalRows);
  $("v3Episodes").textContent=String(v.history.trainEpisodesMatureBeforeJan);
  const orders=v.february.actions.map(function(a){
   return "<tr>"+cell(escapeText(a.tr))+
    cell(a.action==="BUY_GOLD"?"AL":"SAT")+
    cell(money(a.price))+
    cell(escapeText(a.phase))+
    cell(escapeText(a.reason)+" · Ekonomik neden: doğrulanmadı")+"</tr>";
  });
  $("v3FebActions").innerHTML=table(["Türkiye saati","Karar","Ons","Fiyat evresi","Gerekçe"],orders);
  const annual=v.annual.map(function(y){
    return "<tr>"+cell(y.year)+cell(y.bankEpisodes)+cell(y.rows)+
     cell(money(y.finalUSD))+cell(money(y.buyHoldUSD))+
     cell(y.buyCount+" AL / "+y.sellCount+" SAT")+"</tr>";
  });
  $("v3Annual").innerHTML=table(["Yıl","Geçmiş epizot","Kontrol noktası","V3 net","Al ve tut","İşlem"],annual);
  const comparison=(v.february.finalUSD-v.frozenOriginalJanuaryCashUSD);
  status.textContent="V3 hesaplandı · Şubat: "+money(v.february.finalUSD)+
   " · Nakitte kalmaya göre fark: "+(comparison>=0?"+":"")+money(comparison)+
   " · Şubat'ta "+v.february.actions.length+" işlem. Ekonomik neden henüz doğrulanmadı.";
  $("v3Caveat").textContent="Uyarı: 2023 veri kapsaması 2024–2025'ten daha zayıf. 2025 'al ve tut' "+money(v.annual[2].buyHoldUSD)+
   ", V3 "+money(v.annual[2].finalUSD)+
   ". Model birden fazla yılda pasif altından geride kaldı. Şubat sonucu kör bağımsız test değil. Gerçek banka BID/ASK makası dahil değil.";
 }catch(error){
  status.textContent="V3 araştırması yüklenemedi: "+error.message+"; V1 sonuçları değişmedi.";
 }finally{btn.disabled=false;}
}
$("runV3").addEventListener("click",runV3Research);


async function runV4Research(){
 const button=$("runV4"),state=$("v4status");
 button.disabled=true;
 state.textContent="V4 geçmiş öğrenme ve yıllık stres sonuçları hesaplanıyor…";
 try{
  const response=await fetch("/api/algorithm/v4",{cache:"no-store"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const s=await response.json();
  if(s.version!=="V4_ADAPTIVE_CARRY_GUARD_SHADOW_20261015"||
     s.status!=="EXPLORATORY_NOT_BLIND_OOS"||s.annual.length!==3||
     s.bankBidAskSpreadIncluded!==false||s.economicCauseVerified!==false)
   throw Error("V4_CONTRACT_MISMATCH");
  $("v4Feb").textContent=money(s.february.finalUSD);
  $("v4Jan").textContent=money(s.january.finalUSD);
  $("v4Actions").textContent=s.february.actionCount+" işlem";
  $("v4Cases").textContent=s.training.episodeCount+" olay";
  $("v4Annual").innerHTML=table(
   ["Yıl","V4","Başta AL / TUT","NAKİT","V4 AL / SAT"],
   s.annual.map(function(y){
    return "<tr>"+cell(y.year)+cell(money(y.V4))+
     cell(money(y.buyHoldUSD))+cell(money(y.cashUSD))+
     cell(y.buys+" AL / "+y.sells+" SAT")+"</tr>";
   })
  );
  $("v4Trades").innerHTML=s.february.actions.length?table(
   ["Türkiye zamanı","Karar","Fiyat","Gerekçe","Karardan önceki XAU verileri"],
   s.february.actions.map(function(a){
    return "<tr>"+cell(escapeText(a.tr))+
     cell(a.action==="BUY_GOLD"?"AL":"SAT")+
     cell(money(a.price))+cell(escapeText(a.reason))+
     cell("4 saat: "+pct(a.decisionData.r4)+" · Orta vade: "+pct(a.decisionData.r92)+
      " · Ekonomik neden: BELİRSİZ")+"</tr>";
   })
  ):"<p>V4 bu ay AL veya SAT yapmadı.</p>";
  const delta=s.february.finalUSD-s.baseline.v3FebUSD;
  state.textContent="V4 hesaplandı · Şubat "+money(s.february.finalUSD)+
   " · V3'e göre "+(delta<0?"":"+")+money(delta)+
   " · 2025'te pasif altının gerisinde kaldı. Kör doğrulama yapılmadı.";
 }catch(error){
  state.textContent="V4 araştırması hesaplanamadı: "+error.message+
   ". Eski V1/V3 işlemleri korunuyor.";
 }finally{button.disabled=false;}
}
$("runV4").addEventListener("click",runV4Research);


async function runLongScientificReview(){
 const button=$("runLongReview"),status=$("longStatus");button.disabled=true;
 status.textContent="V4 ve V5 2026 Şubat–Eylül verileri ve önceki yıllar sırayla hesaplanıyor…";
 try{
  const replies=await Promise.all([
   fetch("/api/algorithm/v4/forward",{cache:"no-store"}),
   fetch("/api/algorithm/v5",{cache:"no-store"})
  ]);
  if(replies.some(r=>!r.ok))throw Error("SUNUCU_ISTEGI_BASARISIZ");
  const [v4,v5]=await Promise.all(replies.map(r=>r.json()));
  if(v4.actual.finalUSD<=0||v5.fromFebThroughSeptember.finalUSD<=0||
     v4.monthly.length!==8||v5.monthResults.length!==8||
     v5.promotionAuthorized!==false||v5.scientificGate.status!=="REJECT_PROMOTION"||v4.monthEndCarryVerified!==true||
     v4.hasProspectiveBlindValidation!==false||
     v5.status!=="EXPLORATORY_DESIGNED_AFTER_SEEING_2026")
   throw Error("ARASTIRMA_VERI_SOZLESMESI_HATASI");
  $("longV4").textContent=money(v4.actual.finalUSD);
  $("longV5").textContent=money(v5.fromFebThroughSeptember.finalUSD);
  $("longCash").textContent=money(v4.benchmarks.cashOnlyUSD);
  $("longHold").textContent=money(v4.benchmarks.firstBankWindowBuyHoldUSD);
  $("longMonths").innerHTML=table(
    ["Ay","V4 net","V5 net","NAKİT","İlk AL/TUT","V5 işlem"],
    v4.monthly.map(function(x,i){
     const y=v5.monthResults[i],c=v4.monthlyBenchmarks[i];
     if(x.month!==y.month||x.month!==c.month)throw Error("AY_ESLESMESI_BOZULDU");
     return "<tr>"+cell(escapeText(x.month))+cell(money(x.terminalNetUSD))+
      cell(money(y.finalUSD))+cell(money(c.cashOnlyUSD))+
      cell(money(c.firstBankWindowBuyHoldUSD))+
      cell(y.buys+" AL / "+y.sells+" SAT")+"</tr>";
    })
  );
  $("longAnnual").innerHTML=table(
    ["Yıl","V5","Altını al ve tut","Nakitte bekle","V5 işlemler"],
    v5.years.map(function(y){
     return "<tr>"+cell(y.year+(y.coverageWarning?" *":""))+
      cell(money(y.finalUSD))+cell(money(y.buyHoldUSD))+cell(money(y.cashOnlyUSD))+
      cell(y.buys+" AL / "+y.sells+" SAT")+"</tr>";
    })
  );
  status.textContent="Bilimsel kıyas tamamlandı: V4 "+money(v4.actual.finalUSD)+
    " → V5 "+money(v5.fromFebThroughSeptember.finalUSD)+
    ". Ancak V5 hem nakitte beklemeden kötü, hem eski yıllardaki kazançları düşürüyor.";
  $("longVerdict").textContent="MODEL SEÇİM KARARI: V5 ONAYLANMADI. 2023 veri kapsamı eksik; "+
   "2024–2025 testlerinde gereksiz AL/SAT arttı; başarısız bilimsel kabul ölçütü sayısı: "+v5.scientificGate.unmetRequirements.length+". 2026 sonuçları V5 geliştirilmeden önce "+
   "görüldüğünden bağımsız ileri test değildir. Yalnız araştırma; "+
   "G05-C/G06-B nedensellik doğrulanmadı, gerçek banka ASK/BID makası ve emir kayması yok.";
 }catch(error){
  status.textContent="Uzun dönem araştırması yüklenemedi: "+error.message+
    ". Eski V1–V4 sonuçları değişmedi.";
 }finally{button.disabled=false;}
}
$("runLongReview").addEventListener("click",runLongScientificReview);


async function runV6EconomicEvidence(){
 const b=$("runV6"),st=$("v6Status");b.disabled=true;
 st.textContent="Altın, Nasdaq, tahvil ve petrol kapanış saatleri eşleştiriliyor…";
 try{
  const res=await fetch("/api/algorithm/v6",{cache:"no-store"});
  if(!res.ok)throw Error("SUNUCU_HTTP_"+res.status);
  const x=await res.json();
  if(x.status!=="READ_ONLY_NO_AUTOTRADING"||x.annual.length!==3||
     x.acceptance.tradeAuthorized!==false||
     x.predictionTarget!=="XAU_ANY_3H_CLOSE_DOWN_2PCT_WITHIN_NEXT_24H")
   throw Error("V6_BILIMSEL_SOZLESME");
  const y25=x.annual.find(r=>r.year===2025);
  $("v6Archive").textContent="OLAY-02: "+x.archiveEvidence.totalEvents+" olaydan "+
   x.archiveEvidence.firstprintVerified+" ilk haber zamanı, "+
   x.archiveEvidence.mechanismProven+" doğrulanmış ekonomik neden, "+
   x.archiveEvidence.asofActionValidated+" geçerli işlem kararı. "+
   "Örnek: 1 Şubat 2023 06.15 UTC olayından sonra Fed açıklaması 19.00 UTC. "+
   "Olayı bu sonraki Fed kararının sonucuymuş gibi sınıflandırmak engellendi.";
  $("v6Pairs").textContent=new Intl.NumberFormat("tr-TR").format(x.coverage.completePairs);
  $("v6Cases").textContent=String(y25.test.positive);
  $("v6Gold").textContent=y25.xauOnly.brier.toFixed(5);
  $("v6Macro").textContent=y25.xauPlusCross.brier.toFixed(5);
  $("v6Table").innerHTML=table(
   ["Yıl","İncelenen gün","Büyük düşüş günü","Altın Brier","Altın + diğerleri Brier","Ek veri katkısı"],
   x.annual.map(function(v){
    return "<tr>"+cell(v.year)+cell(v.test.n)+cell(v.test.positive)+
      cell(v.xauOnly.brier.toFixed(5))+cell(v.xauPlusCross.brier.toFixed(5))+
      cell(v.crossBeatsPrice.brier&&v.crossBeatsPrice.logLoss?"İyileşme (örnek yetersiz olabilir)":"Kanıtlanmadı")+"</tr>";
   })
  );
  st.textContent=x.acceptance.incrementalEvidenceOn2024And2025?
    "Ek piyasalarda yalnız sınıflandırma sinyali görüldü; canlı/otomatik karar onaylanmadı.":
    "V6 sonucunda ek piyasa bilgileri iki yılda da güvenilir tahmin üstünlüğü sağlamadı. İşleme açılmadı.";
  $("v6Verdict").textContent="SONUÇ: "+x.acceptance.verdict+
   ". Fed/TÜFE/NFP ilk yayın sürümleri doğrulanmadı. 2024–2025'te düşüş sayısı az; "+
   "2026 verileri geriye dönük stres değerlendirmesi. Gerçek banka BID/ASK makası bulunmuyor. "+
   "G05-C/G06-B ekonomik olay nedenleri doğrulanmadı ve bu kontrol AL/SAT üretmez.";
 }catch(err){
  st.textContent="V6 hesaplaması tamamlanamadı: "+err.message+". Eski sonuçlar değişmedi.";
 }finally{b.disabled=false;}
}
$("runV6").addEventListener("click",runV6EconomicEvidence);


async function runV6Portfolio(){
 const button=$("runV6Portfolio"),status=$("v6PortfolioStatus");
 button.disabled=true;
 status.textContent="Ekonomik veri eşleştirmesi, kararlar ve yıllık testler hesaplanıyor…";
 try{
  const res=await fetch("/api/algorithm/v6/portfolio",{cache:"no-store"});
  if(!res.ok)throw Error("HTTP "+res.status);
  const d=await res.json();
  if(d.status!=="CROSS_ASSET_RETROSPECTIVE_NOT_BLIND"||
     d.scientificGate.authorized!==false||d.promotionAuthorized!==false||
     d.economicEventEvidence.allowedAsCausalTradingInputs!==false||
     d.monthResults.length!==8||d.years.length!==3||d.bankSpreadIncluded!==false)
   throw Error("V6_RESEARCH_CONTRACT_INVALID");
  $("v6PortfolioFinal").textContent=money(d.finalUSD);
  $("v6PortfolioV5").textContent=money(d.comparison.V5);
  $("v6Firstprints").textContent=d.economicEventEvidence.verifiedFirstprints+" / "+d.economicEventEvidence.cases;
  $("v6Promotion").textContent="REDDEDİLDİ";
  const pairs=d.scientificGate.testedFullYears;
  $("v6PortfolioAnnual").innerHTML=table(
   ["Yıl","V6 ekonomi","V5 fiyat","Altın al / tut","V6 AL / SAT"],
   d.years.map(function(y){
    const pair=pairs.find(z=>z.year===y.year);
    return "<tr>"+cell(y.year+(y.coverageWarning?" *":""))+
     cell(money(y.finalUSD))+cell(pair?money(pair.V5):"—")+
     cell(money(y.buyHoldUSD))+cell(y.buys+" AL / "+y.sells+" SAT")+"</tr>";
   })
  );
  $("v6PortfolioMonths").innerHTML=table(
   ["Ay","V6 net değer","Durum","AL / SAT"],
   d.monthResults.map(function(y){
    return "<tr>"+cell(escapeText(y.month))+cell(money(y.finalUSD))+
     cell(y.position==="CASH"?"NAKİT":"ALTIN")+
     cell(y.buys+" AL / "+y.sells+" SAT")+"</tr>";
   })
  );
  status.textContent="Deney tamamlandı: V6 "+money(d.finalUSD)+
   ", V5 "+money(d.comparison.V5)+
   ". Ekonomik göstergelerin kalıcı üstünlüğü kanıtlanmadı; canlı karar olarak onaylanmadı.";
  $("v6PortfolioCaveat").textContent="2024–2025 V6 eski fiyat modelini iyileştirmedi. 2026 veri dönemleri daha önce görüldüğü için kör ileri test değil. "+
   "96 OLAY-02 vakasında ilk haber ve ekonomik nedensellik kanıtı yok. Gerçek banka makası dahil değil. "+
   "Yalnız geçmiş fiyat/ekonomik durum deneyi; uygulama canlı banka işlemi yapmaz.";
 }catch(e){status.textContent="V6 ekonomik deney çalıştırılamadı: "+e.message+". Eski modeller değişmedi.";}
 finally{button.disabled=false;}
}
$("runV6Portfolio").addEventListener("click",runV6Portfolio);
