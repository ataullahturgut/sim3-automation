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

async function runAdaptiveV7(){
 const button=$("runAdaptiveV7"),state=$("adaptiveV7Status");
 button.disabled=true;
 state.textContent="V7: 2025 öğrenme, 2026 güncellemeleri, işlem maliyeti ve karşı deneyler hesaplanıyor…";
 try{
  const response=await fetch("/api/algorithm/v7/adaptive",{cache:"no-store"});
  if(!response.ok)throw Error("SUNUCU_HTTP_"+response.status);
  const d=await response.json();
  if(d.version!=="V7_ADAPTIVE_DUAL_HORIZON_RESEARCH_20261015"||
     d.status!=="EX_POST_RESEARCH_NOT_BLIND"||
     d.scientificGate.promote!==false||d.scientificGate.bankTradeAuthorized!==false||
     d.scientificGate.economicCausalityProven!==false||
     d.primary.months.length!==8||d.primary.initialUSD<119||d.primary.trades.length!==4)
   throw Error("V7_BILIMSEL_VERI_SOZLESMESI");
  $("adaptiveV7Net").textContent=money(d.primary.finalUSD);
  $("adaptiveV7Frozen").textContent=money(d.ablations.learningFrozenUSD);
  $("adaptiveV7NoStress").textContent=money(d.ablations.stressRuleDisabledUSD);
  $("adaptiveV7News").textContent=d.primary.trainingCounts.verifiedEconomicCheckpoints+" / 96";
  $("adaptiveV7Months").innerHTML=table(
   ["Ay","Dönem sonu net","Pozisyon","Son kontrol saati"],
   d.primary.months.map(function(m){
    const time=new Intl.DateTimeFormat("tr-TR",{
      timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false
    }).format(new Date(m.lastCheckpoint));
    return "<tr>"+cell(escapeText(m.month))+cell(money(m.nav))+
      cell(m.position==="GOLD"?"ALTIN":"NAKİT")+cell(escapeText(time))+"</tr>";
   })
  );
  $("adaptiveV7Trades").innerHTML=table(
   ["Türkiye saati","Karar","XAU MID vekili","Gerekçe","Net tasfiye"],
   d.primary.trades.map(function(t){
    const time=new Intl.DateTimeFormat("tr-TR",{
      timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false
    }).format(new Date(t.time));
    const why=t.reason==="XAU_NQ_STRESS"?"Altın + Nasdaq stres satış kuralı":
      t.reason==="ADAPTIVE_LONG_OPPORTUNITY"?"14 gün ileri adaptif alım fırsatı":t.reason;
    return "<tr>"+cell(escapeText(time))+cell(t.action==="BUY"?"AL":"SAT")+
      cell(format.format(t.fill_proxy))+cell(escapeText(why))+
      cell(money(t.nav))+"</tr>";
   })
  );
  $("adaptiveV7Failures").innerHTML=table(
    ["Karşı test","V7 net","Pasif altın","Yorum"],
    [
      {title:"2025 başlangıç 100 $",v:d.negativeControls.year2025,warning:"Uzun UP trendi büyük ölçüde kaçırıldı"},
      {title:"Ocak 2026 başlangıç 100 $",v:d.negativeControls.january2026,warning:"Eski Ocak 119,75 $ referansı yerine geçmez"}
    ].map(function(x){return "<tr>"+cell(escapeText(x.title))+cell(money(x.v.finalUSD))+
      cell(money(x.v.passiveGoldUSD))+cell(escapeText(x.warning))+"</tr>";})
  );
  state.textContent="V7 geriye dönük test: "+money(d.primary.finalUSD)+
    " (başlangıç "+money(d.primary.initialUSD)+"). Öğrenme dondurulunca "+
    money(d.ablations.learningFrozenUSD)+
    ". Ekonomi uzmanı doğrulanmış olay bulamadığından devreye girmedi.";
  $("adaptiveV7Warning").textContent="BİLİMSEL KARAR: ONAYLANMADI. 2025 karşı testinde V7 "+
    money(d.negativeControls.year2025.finalUSD)+", pasif altın "+
    money(d.negativeControls.year2025.passiveGoldUSD)+
    ". 2026 birçok kez görüldüğünden kör doğrulama değil. Fiyat + çapraz piyasa uzmanlarının ilave işlem avantajı kanıtlanmadı. "+
    "Kullanılan 3 saatlik MID paneli V4/V5 ile aynı banka icra sözleşmesi değildir; gerçek ASK/BID ve kayma eksik. Bankaya emir gönderilmez.";
 }catch(e){
  state.textContent="V7 ayrı araştırması çalıştırılamadı: "+e.message+
    ". V1–V6 referansları etkilenmedi.";
 }finally{button.disabled=false;}
}
$("runAdaptiveV7").addEventListener("click",runAdaptiveV7);

async function runMonthlyRegimeBenchmarkV7(){
 const button=$("runMonthlyBenchmarkV7"),status=$("monthlyBenchmarkV7Status");
 button.disabled=true;
 status.textContent="Ay bazında NAKİT/ALTIN, geçmiş aydan seçim ve V7 farkları hesaplanıyor…";
 try{
  const res=await fetch("/api/algorithm/v7/monthly-regimes",{cache:"no-store"});
  if(!res.ok)throw Error("HTTP "+res.status);
  const d=await res.json();
  if(d.status!=="RETROSPECTIVE_BENCHMARK_HINDSIGHT_NOT_ASOF"||
     d.hindsightChoiceIsNotModelPrediction!==true||
     d.acceptedForLiveTrading!==false||d.bankBidAskIncluded!==false||
     d.months.length!==8||d.months[0].month!=="2026-02"||
     d.months.at(-1).month!=="2026-09")throw Error("MONTHLY_BENCHMARK_CONTRACT_INVALID");
  $("monthlyOracleUSD").textContent=money(d.endUSD.hindsightMonthlyOracle);
  $("monthlyLaggedUSD").textContent=money(d.endUSD.previousMonthWinner);
  $("monthlyV7USD").textContent=money(d.endUSD.v7);
  $("monthlyRegretUSD").textContent=money(d.v7VsMonthlyOracleGapUSD);
  $("monthlyBenchmarkV7Table").innerHTML=table(
   ["Ay","Altın: net aylık","Ay bitince kazanan","Geçen ayı takip","Ay sonu ideal nakit","Ay sonu V7"],
   d.months.map(function(m){
     return "<tr>"+cell(escapeText(m.month))+
       cell(pct(m.goldNetPct))+
       cell(m.hindsightWinner==="GOLD"?"ALTIN":"NAKİT")+
       cell((m.laggedSelected==="GOLD"?"ALTIN":"NAKİT")+(m.lagChoiceCorrect?" ✓":" ✕"))+
       cell(money(m.oracleTerminalUSD))+
       cell(money(m.v7TerminalUSD))+
       "</tr>";
   })
  );
  status.textContent="Aylık karşılaştırma tamamlandı. Geçen ayın kazananı "+
   d.lagCorrectMonths+"/"+d.lagTotalMonths+" ayda doğru, ancak sonuç "+
   money(d.endUSD.previousMonthWinner)+". V7 sonucu "+money(d.endUSD.v7)+".";
  $("monthlyBenchmarkV7Warning").textContent=
   "ÖNEMLİ: "+money(d.endUSD.hindsightMonthlyOracle)+
   " rakamı, aylar bittikten sonra bilinen aylık NAKİT/ALTIN seçimlerinin teorik karşılığıdır; as-of gerçek bir tahmin veya tüm intraday stratejilerin üst kâr sınırı değildir. "+
   "Gerçek zamanlı basit geçen-ay politikasının "+money(d.endUSD.previousMonthWinner)+
   " sonucu, nakitte kalmanın altındadır. Fiyatlar araştırma MID vekili, gerçek banka ASK/BID hariçtir. "+
   "V4/V5 ile doğrudan aynı emir sözleşmesi kurulmuş değildir. Ekonomik haber öğrenmesi ayrıca doğrulanacaktır.";
 }catch(e){
  status.textContent="Aylık strateji karşılaştırması çalıştırılamadı: "+e.message;
 }finally{button.disabled=false;}
}
$("runMonthlyBenchmarkV7").addEventListener("click",runMonthlyRegimeBenchmarkV7);

async function runIntramonthOracleV7(){
 const button=$("runIntramonthOracleV7"),status=$("intramonthOracleV7Status");
 button.disabled=true;
 status.textContent="Tüm ayların üç saatlik AL/SAT zamanlaması geriye dönük eniyileniyor…";
 try{
  const reply=await fetch("/api/algorithm/v7/intramonth-oracle",{cache:"no-store"});
  if(!reply.ok)throw Error("HTTP "+reply.status);
  const x=await reply.json();
  if(x.status!=="EX_POST_UNTRADEABLE_ORACLE"||
      x.liveTradingAuthorized!==false||x.independentBlindTest!==false||
      x.costs.realBankBidAsk!==false||
      x.months.length!==9)throw Error("THEORETICAL_ORACLE_SCHEMA_MISMATCH");
  $("intramonthBasicUSD").textContent=money(x.continuationUSD.cashMonthly);
  $("intramonthOneUSD").textContent=money(x.continuationUSD.one);
  $("intramonthTwoUSD").textContent=money(x.continuationUSD.two);
  $("intramonthAllUSD").textContent=money(x.continuationUSD.upto15);
  const trShort=function(utc){return new Intl.DateTimeFormat("tr-TR",{
    timeZone:"Europe/Istanbul",day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false
  }).format(new Date(utc));};
  $("intramonthOracleV7Table").innerHTML=table(
    ["Ay","Ay boyu altın","Ayın en iyi tek AL/SAT turu","En iyi 2 tura kadar",
     "Tek turun geriye dönük AL → SAT zamanları"],
    x.months.map(function(m){
     const acts=m.bestOneRound.actions;
     const when=acts.length===2?trShort(acts[0].utc)+" → "+trShort(acts[1].utc):
       "İşlem avantajı yok";
     return "<tr>"+cell(escapeText(m.month))+
      cell(pct(m.holdGoldNetUSD-100))+
      cell(pct(m.bestOneRound.netPct))+
      cell(pct(m.bestTwoRounds.netPct))+
      cell(escapeText(when))+"</tr>";
    })
  );
  status.textContent="Geriye dönük araştırma hesaplandı. Bir aylık ideal işlem tek turuyla "+
   money(x.continuationUSD.one)+" ve iki tura kadar "+money(x.continuationUSD.two)+
   " teorik portföy görülüyor. Bu sonuçların hiçbiri ileriye dönük olarak bilinemiyordu.";
  $("intramonthOracleV7Warning").textContent=
   "UYARI: Bunlar ayın bütün fiyatlarını gördükten sonra seçilmiş işlem zamanlarıdır. "+
   "Yalnız üç saatlik 09/12/15 kontrol noktaları ve %0,8 / %0,8 maliyet vardır. "+
   "Gerçek banka alış-satış kotasyonları, emir gecikmesi ve başka saatlerdeki fiyatlar yoktur. "+
   "Dolayısıyla bankada uygulanabilir azami kâr veya başarılı tahmin sayılmaz. "+
   "Aylık NAKİT/ALTIN etiketi yerine al-sat modelinin hata açıklamasında araştırma karşı örneğidir.";
 }catch(e){
  status.textContent="Ay içi ideal işlem denetimi çalıştırılamadı: "+e.message;
 }finally{button.disabled=false;}
}
$("runIntramonthOracleV7").addEventListener("click",runIntramonthOracleV7);

async function runV8Regret(){
 const button=$("runV8Regret"),state=$("v8RegretStatus");
 button.disabled=true;
 state.textContent="2023–2025 geçmişi ve 2026 öğrenme hataları kronolojik yeniden oynatılıyor…";
 try{
  const result=await fetch("/api/algorithm/v8/regret",{cache:"no-store"});
  if(!result.ok)throw Error("HTTP_"+result.status);
  const d=await result.json();
  if(d.version!=="V8_REGRET_SHADOW_REJECT_PROMOTION_20261015"||
      d.status!=="REJECT_PROMOTION_SHADOW_ONLY"||
      d.scientificGate.authorized!==false||
      d.contract.liveTradeAuthorized!==false||
      d.contract.automaticPromotionAuthorized!==false||
      d.contract.bankBidAskIncluded!==false||
      d.yearScores.length!==3)throw Error("V8_SCIENTIFIC_CONTRACT_INVALID");
  $("v8EndUSD").textContent=money(d.controls.v8OnlineUSD);
  $("v8V7USD").textContent=money(d.controls.referenceV7USD);
  $("v8FrozenUSD").textContent=money(d.controls.v8AllLearningFrozenUSD);
  $("v8NoRegretUSD").textContent=money(d.controls.v8RegretLearningOffUSD);
  $("v8YearTable").innerHTML=table(["Dönem","Başlangıç","V8 net","Pasif ALTIN / V7","Sonuç"],d.yearScores.map(function(x){
   const baseline=x.v7FinalUSD??x.passiveGoldUSD;
   return "<tr>"+cell(escapeText(x.year))+cell(money(x.initialUSD))+
     cell(money(x.v8FinalUSD))+cell(money(baseline))+
     cell(x.v8FinalUSD>baseline?"İyileşti, bağımsız test değil":"Karşı stratejinin altında")+"</tr>";
  }));
  const when=function(utc){return new Intl.DateTimeFormat("tr-TR",{
    timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false
   }).format(new Date(utc));};
  $("v8TradesTable").innerHTML=table(["Türkiye saati","AL / SAT","Fiyat","Gerekçe","Net tasfiye"],d.trades.map(function(t){
    return "<tr>"+cell(escapeText(when(t.at)))+cell(t.action==="BUY"?"AL":"SAT")+
      cell(format.format(t.mid))+cell(escapeText(t.reason))+cell(money(t.nav))+"</tr>";
  }));
  $("v8ErrorsTable").innerHTML=table(
    ["Hatanın başlangıç ayı","Tamamlanan etiket","Kaçırılan yükseliş","Eldeyken düşüş","Nakitte kaçınılan düşüş"],
    d.errorsByMonth.map(function(m){
      return "<tr>"+cell(escapeText(m.month))+cell(m.completedLabels)+
      cell(m.missedUP)+cell(m.missedDOWN)+cell(m.avoidedDOWN)+"</tr>";
    })
  );
  state.textContent="V8 araştırması tamamlandı. 2026 V8 "+
    money(d.controls.v8OnlineUSD)+", V7 "+money(d.controls.referenceV7USD)+
    ". Hata düzeltmesini kapatmak V8 sonucunu değiştirmedi. Model terfisi: REDDEDİLDİ.";
  $("v8GateWarning").textContent="Bilimsel karar: REDDEDİLDİ. "+
   "Geçmiş hata etiketleri yalnız 96 saat veya 14 gün olgunlaştıktan sonra güncellenir; "+
   "örtüşen vakalar bağımsız kâr sayılmaz. 2026 geçmişi daha önce görüldüğünden kör test değildir. "+
   "Ekonomik olayların doğrulanmış ilk erişim saati 0/96, bankanın gerçek BID/ASK makası yok. "+
   "V1–V7 orijinal modelleri değiştirilmedi, canlı yatırım emri yok.";
 }catch(err){
   state.textContent="V8 gölge deney yüklenemedi: "+err.message+". V1–V7 korunuyor.";
 }finally{button.disabled=false;}
}
$("runV8Regret").addEventListener("click",runV8Regret);

async function runV9Scientific(){
 const b=$("runV9Scientific"),status=$("v9ScientificStatus");
 b.disabled=true;
 status.textContent="2023–2026 sıralı veriyle V9 maliyetli stratejileri ve geçmişte olgunlaşmış öğrenme etiketlerini değerlendiriyor…";
 try{
  const res=await fetch("/api/algorithm/v9/scientific",{cache:"no-store"});
  if(!res.ok)throw Error("HTTP_"+res.status);
  const a=await res.json();
  if(a.version!=="V9_STATE_REGRET_SCIENTIFIC_AUDIT_20261015"||
     a.status!=="REJECT_V9_PROMOTION_SAVE_LEARNING_EXPERIMENTS"||
     a.gate.promote!==false||a.gate.canTradeLive!==false||
     a.execution.sameCheckpointSignalFill!==false||
     a.execution.bankBidAsk!==false||
     a.method.prospectiveBlindPeriod!==false)throw Error("V9_SCIENTIFIC_AUDIT_GATE_INVALID");
  const choose=(name,year)=>a.shadowCandidates.find(x=>x.variant===name&&x.year===year);
  const episode=(name,year)=>a.episodeCandidates.find(x=>x.variant===name&&x.year===year);
  $("v9Meta2026").textContent=money(choose("VOTE_42D","2026").final);
  $("v9Episode2026").textContent=money(episode("POSTERIOR","2026").final);
  $("v9LegacyV7").textContent=money(a.comparisons.V7_2026);
  $("v9Promotion").textContent="ONAY YOK";
  const rows=[
   {label:"2024 · Histerezis / rejim",price:episode("BASE","2024").final,ref:123.84971030121015,why:"Pasif altın"},
   {label:"2025 · Histerezis / rejim",price:episode("BASE","2025").final,ref:160.4152649234894,why:"Pasif altın"},
   {label:"2026 · Naif uzman karışımı",price:a.naiveMixture.find(x=>x.year==="2026_FebSep"&&x.policy==="ensemble").finalUSD,ref:119.753917,why:"Nakit"},
   {label:"2026 · Çevrimiçi uzman seçici",price:choose("VOTE_42D","2026").final,ref:a.comparisons.V7_2026,why:"V7"},
   {label:"2026 · Gecikmeli etiket koruması",price:episode("POSTERIOR","2026").final,ref:a.comparisons.V7_2026,why:"V7"}
  ];
  $("v9ResultsTable").innerHTML=table(["Araştırma / Dönem","Net sonuç","Karşılaştırma","Karar"],rows.map(x=>
   "<tr>"+cell(escapeText(x.label))+cell(money(x.price))+
   cell(money(x.ref)+" · "+escapeText(x.why))+
   cell(x.price>x.ref?"ÜSTÜN (yalnız tarihsel)":"ALTINDA / EŞİT")+"</tr>"
  ));
  $("v9Findings").textContent="Önemli bulgular: ani politika geçişleri yüzünden komisyon kaybı; "+
   "2024'te iyi görünen stratejinin 2025 ve 2026'ya taşınamaması; "+
   "14 günlük gecikmeli etiketlerin bağımsız sayılabilmesi için seyrek eğitim ihtiyacı; "+
   "42–84 günlük geçmişte en çok kazandıran uzmanı seçmenin 2026 rejimini öngörememesi. "+
   "2024–2025'te pasif altını HER İKİ yılda geçen yeni aday: "+
   a.pre2026PassBothPassive.count+".";
  $("v9ScientificWarning").textContent="BİLİMSEL KARAR: V9 TERFİ REDDEDİLDİ. "+
   "Tüm emir vekilleri sinyalden sonraki 09/12/15 banka saatinde uygulanır; "+
   "%0,8 alış + %0,8 satış düşülür. "+
   "2026 zaten incelenmiş olduğundan kör test değildir. "+
   "Gerçek banka alış/satış fiyatları ve 96 OLAY-02 firstprint kanıtları eksik. "+
   "2026 sonuçlarına bakarak seçilen 'en iyi V9' model değildir, yatırıma uygulanamaz.";
  status.textContent="V9 analiz tamamlandı: adayların hiçbirinde sağlam çok-yıllı üstünlük yok. "+
   "V7 korunuyor. V9 otomatik işlem veya model değiştirme yapmıyor.";
 }catch(err){
  status.textContent="V9 bilimsel deneyi yüklenemedi: "+err.message+
   ". V7 kaynakları ve mevcut program değişmedi.";
 }finally{b.disabled=false;}
}
$("runV9Scientific").addEventListener("click",runV9Scientific);

async function runV10Evidence(){
 const b=$("runV10Evidence"),status=$("v10EvidenceStatus");
 b.disabled=true;
 status.textContent="Gecikmeli banka icrası, yeniden alım hataları ve 2024–2026 karşı testleri hesaplanıyor…";
 try{
  const res=await fetch("/api/algorithm/v10/evidence",{cache:"no-store"});
  if(!res.ok)throw Error("HTTP "+res.status);
  const x=await res.json();
  if(x.version!=="V10_BANK_LAG_RECOVERY_GUARD_20261015"||
     x.status!=="SCIENTIFIC_SHADOW_CANDIDATE_NOT_VALIDATED"||
     x.scientificGate.validationPassed!==false||
     x.scientificGate.liveTradingAuthorized!==false||
     x.scientificGate.automaticPromotion!==false||
     x.contracts.barSignalNotSameBarFill!==true||
     x.contracts.realBankBidAskPresent!==false||
     x.contracts.independentBlindValidation!==false)throw Error("V10_RESEARCH_CONTRACT_INVALID");
  $("v10OldUSD").textContent=money(x.base2026.v7OriginalSameBarUSD);
  $("v10LagUSD").textContent=money(x.base2026.v7DelayedBankUSD);
  $("v10ProtectedUSD").textContent=money(x.base2026.v10BankRecoveryUSD);
  $("v10Gate").textContent="ONAY YOK";
  const dateTR=function(utc){return new Intl.DateTimeFormat("tr-TR",{
    timeZone:"Europe/Istanbul",day:"2-digit",month:"2-digit",
    hour:"2-digit",minute:"2-digit",hour12:false
  }).format(new Date(utc));};
  $("v10TradeTable").innerHTML=table(
   ["Sinyal (TR)","Sonraki işlem (TR)","Emir","İşlem fiyat vekili","Karar","Net bakiye"],
   x.transactions.guarded.map(t=>"<tr>"+cell(escapeText(dateTR(t.signalAt)))+
    cell(escapeText(dateTR(t.at)))+cell(escapeText(t.side==="BUY"?"AL":"SAT"))+
    cell(format.format(t.mid))+cell(escapeText(t.reason))+
    cell(money(t.netUSD))+"</tr>")
  );
  $("v10Sensitivity").innerHTML=table(
    ["Her yönde maliyet","Beklenen banka kesiti","2026 teorik son bakiye","İşlem sayısı"],
    x.costLatencySensitivity.map(v=>"<tr>"+cell(pct(v.feePerSide*100))+
      cell(v.executionBankCheckpoints)+cell(money(v.finalUSD))+
      cell(v.tradeCount)+"</tr>")
  );
  const controls=[
   {period:"2025 · Önceki V7, gecikmeli",v:x.negativeControl2025.delayedV7USD,
      ref:x.negativeControl2025.passiveGoldUSD,flag:"Koruma 0 kez tetiklendi"},
   {period:"2025 · V10 koruma, gecikmeli",v:x.negativeControl2025.guardedV10USD,
      ref:x.negativeControl2025.passiveGoldUSD,flag:"Önceki V7 ile aynı"},
   ...x.historicalControl.map(q=>({period:q.period,v:q.finalUSD,
      ref:q.passiveGoldUSD,flag:"Bağımsız doğrulama değil"}))
  ];
  $("v10Historical").innerHTML=table(
     ["Tarihsel kontrol","Strateji sonucu","Pasif altın","Denetim"],
     controls.map(v=>"<tr>"+cell(escapeText(v.period))+cell(money(v.v))+
         cell(money(v.ref))+cell(escapeText(v.flag))+"</tr>")
  );
  status.textContent="V10 araştırması tamamlandı. 2026 gecikmeli temel "+
    money(x.base2026.v7DelayedBankUSD)+", korumalı "+money(x.base2026.v10BankRecoveryUSD)+
    ". Korunan işlem girişimi "+x.deniedBuys.total+
    " kez engellendi; 2025'te ise 0 kez. Model bilimsel terfi almadı.";
  $("v10Warning").textContent=
     "ÖNEMLİ: 2026 örneklemini bu kuralın tasarımından önce görmüştük. "+
     "Bu nedenle "+money(x.base2026.v10BankRecoveryUSD)+
     " bağımsız geleceğe dönük doğrulama değildir. 2025'te koruma karar değiştirmedi. "+
     "2024–25 stratejisi pasif altında kaldı. Fiyatlar banka MID vekili, gerçek banka ASK/BID yok. "+
     "Olay-öğren kütüphanesinde kaynaklı 96 vakadan 0 doğrulanmış ilk yayın zamanı var. "+
     "V7 asıl modeli ve eski dosyalar değiştirilmedi; canlı banka emri üretilmiyor.";
 }catch(err){
  status.textContent="V10 denetimi çalıştırılamadı: "+err.message+". V1–V9 araştırma sürümleri korunuyor.";
 }finally{b.disabled=false;}
}
$("runV10Evidence").addEventListener("click",runV10Evidence);

async function runV11Ann(){
 const button=$("runV11Ann"),status=$("v11AnnStatus");
 button.disabled=true;
 status.textContent="Gerçek ANN eğitiliyor: yalnız olgunlaşmış etiketlerle 2024, 2025 ve 2026 sırayla deneniyor…";
 try{
  const response=await fetch("/api/algorithm/v11/ann",{cache:"no-store"});
  if(!response.ok)throw Error("HTTP_"+response.status);
  const obj=await response.json();
  if(obj.version!=="V11_ANN_CORRECTLY_SUPERVISED_20261016"||
    obj.status!=="RESEARCH_NOT_PROMOTED"||
    obj.model.learnAlgorithm!=="FULL_BACKPROP_ADAM_HUBER"||
    obj.gate.promote!==false||
    obj.gate.realBankAskBid!==false||
    obj.gate.independentBlindTest!==false||
    obj.source.trainLabels<900)throw Error("V11_INVALID_RESEARCH_OUTPUT");
  const find=(year,policy)=>obj.experiments.find(x=>x.year===year&&x.policy===policy);
  const base=find("2026_FEB_SEP","netPositive");
  const upd=find("2026_FEB_SEP","adaptiveMonthly");
  const abs=find("2026_FEB_SEP","calibratedAbstain");
  $("v11BaseUSD").textContent=money(base.final);
  $("v11MonthlyUSD").textContent=money(upd.final);
  $("v11AbstainUSD").textContent=money(abs.final);
  $("v11Promotion").textContent="ONAY YOK";
  $("v11AnnResults").innerHTML=table(
   ["Dönem","ANN strateji","İlk olgun eğitim örneği","Komisyon sonrası net bakiye","İşlem"],
   obj.experiments.map(x=>"<tr>"+cell(escapeText(x.year))+
    cell(escapeText(x.policy))+
    cell(x.training[0].maturedN)+
    cell(money(x.final))+
    cell(x.nTrades)+"</tr>")
  );
  const tr=function(t){return new Intl.DateTimeFormat("tr-TR",{
   timeZone:"Europe/Istanbul",day:"2-digit",month:"2-digit",
   hour:"2-digit",minute:"2-digit",hour12:false
  }).format(new Date(t));};
  $("v11AnnTrades").innerHTML=table(
    ["Sinyal zamanı","İcra zamanı","AL/SAT","Fiyat vekili","Karar gerekçesi"],
    abs.trades.map(x=>"<tr>"+cell(escapeText(tr(x.asOf)))+
     cell(escapeText(tr(x.at)))+cell(escapeText(x.side==="BUY"?"AL":"SAT"))+
     cell(format.format(x.mid))+
     cell(escapeText(x.why))+"</tr>")
  );
  status.textContent="ANN araştırması tamamlandı: 2026 temel "+money(base.final)+
    ", her ay yeniden öğrenme "+money(upd.final)+
    ", belirsizlikten kaçınma "+money(abs.final)+
    ". Model başarıyla doğrulanmadığı için otomatik kabul edilmedi.";
  $("v11AnnWarning").textContent=
   "BİLİMSEL KARAR: TERFİ YOK. ANN 14-12-8-2 topolojisi gerçek backpropagation/Adam ile eğitildi. "+
   "4/14 günlük hedef yalnız sinyalden sonraki banka kesitinin alışından sonra başlayan, "+
   "her yönde %0,8 maliyetli gerçekleşen getiridir. İlk eğitim etiketi hedef tamamlanmadan öğrenilmiyor; "+
   "son %20 kronolojik doğrulama ve 21 günlük embargo var. Ancak etiketler zaman içinde "+
   "örtüşüyor, 2026 zaten görülmüş, banka ASK/BID ve ilk yayınlı haber kayıtları mevcut değil. "+
   "2025'te belirsizlikten kaçınan model hiç altın almadığı için pasif altının güçlü yükselişini kaçırdı. "+
   "Bu ekran geçmiş deneydir, gerçek yatırım emri üretmez.";
 }catch(err){status.textContent="ANN denetimi yürütülemedi: "+err.message+". V1–V10 sürümleri korunuyor.";}
 finally{button.disabled=false;}
}
$("runV11Ann").addEventListener("click",runV11Ann);

async function runV12Rehber(){
 const b=$("runV12Rehber"),state=$("v12Status");
 b.disabled=true;
 state.textContent="REHBER yeni hafızayla ve öğrenmesi dondurularak 2024–2026 boyunca tekrar oynatılıyor…";
 try{
  const res=await fetch("/api/algorithm/v12/rehber",{cache:"no-store"});
  if(!res.ok)throw Error("HTTP_"+res.status);
  const x=await res.json();
  if(x.version!=="V12_REHBER_ORIGINAL_CAUSAL_MEMORY_RESEARCH"||
    x.status!=="NO_AUTOMATIC_PROMOTION"||
    x.design.ANNArchitecture!==false||
    x.scientificGate.promote!==false||
    x.scientificGate.independentBlindPeriod!==false||
    x.scientificGate.liveTradingAuthorized!==false||
    x.scientificGate.bankAskBidMeasured!==false)throw Error("REHBER_SCIENTIFIC_GATE_INVALID");
  const find=(year,variant)=>x.results.find(v=>v.year===year&&v.variant===variant);
  const core=find("2026_FEB_SEP","REHBER_CORE"),
    frozen=find("2026_FEB_SEP","REHBER_FROZEN_MEMORY"),
    noReliability=find("2026_FEB_SEP","REHBER_NO_RELIABILITY"),
    fixedMargin=find("2026_FEB_SEP","REHBER_FIXED_MARGIN"),
    prev=find("2025","REHBER_CORE");
  $("v12Online").textContent=money(core.final);
  $("v12Frozen").textContent=money(frozen.final);
  $("v12Year2025").textContent=money(prev.final);
  $("v12Gate").textContent="ONAY YOK";
  $("v12Results").innerHTML=table(
   ["Dönem","Algoritma varyantı","Komisyon sonrası net","İşlem","Tamamlanmış hafıza bloğu","Güncellenmiş karar hatası"],
   x.results.map(z=>"<tr>"+cell(escapeText(z.year))+
    cell(escapeText(z.variant))+
    cell(money(z.final))+cell(z.tradeCount)+cell(z.analogBlocks)+
    cell(z.learning.updates)+"</tr>")
  );
  const when=t=>new Intl.DateTimeFormat("tr-TR",{
    timeZone:"Europe/Istanbul",day:"2-digit",month:"2-digit",hour:"2-digit",
    minute:"2-digit",hour12:false}).format(new Date(t));
  $("v12Trades").innerHTML=table(
   ["Sinyal (TR)","İcra (TR)","AL/SAT","Piyasa fiyat vekili","Gerekçe"],
   core.trades.map(z=>"<tr>"+cell(escapeText(when(z.signalAt)))+
     cell(escapeText(when(z.at)))+cell(z.side==="BUY"?"AL":"SAT")+
     cell(format.format(z.price))+cell(escapeText(z.reason))+"</tr>")
  );
  state.textContent="REHBER sonuçlandı: 2026 online "+
    money(core.final)+", yıl başı dondurulmuş hafıza "+money(frozen.final)+
    ", 2025 "+money(prev.final)+". Model bilimsel terfi almadı.";
  $("v12Warning").textContent=
    "DİKKAT: Hafıza güncellemeleri 2026'da "+money(core.final-frozen.final)+
    " fark yarattı; ancak karar marjı ve uzman güven güncellemelerini kapatmak "+
    "bu dönem işlemlerini değiştirmedi (marj: "+money(fixedMargin.final)+
    ", uzman: "+money(noReliability.final)+"). "+
    "2024 ve 2025'te model hiç altın almayıp yükselişleri kaçırdı. "+
    "2026 önceden incelendi; kör test ve gerçek banka BID/ASK yok. "+
    "Yalnızca olgunlaşmış etiketler kullanılıyor, üç ayırt edici piyasa merceği "+
    "her 14 günlük bloktan en çok bir geçmiş vaka seçiyor. "+
    "OTOMATİK AL/SAT VE V7 DEĞİŞİKLİĞİ YOK.";
 }catch(err){
  state.textContent="REHBER denetimi yüklenemedi: "+err.message+". Eski sürümler korundu.";
 }finally{b.disabled=false;}
}
$("runV12Rehber").addEventListener("click",runV12Rehber);

async function runV12Earliest(){
 const button=$("runV12Earliest"),status=$("v12EarliestStatus");
 button.disabled=true;
 status.textContent="3 Ocak 2023'ten başlayarak sıfırlanmayan 100 dolarlık portföy yeniden oynatılıyor…";
 try{
  const response=await fetch("/api/algorithm/v12/earliest",{cache:"no-store"});
  if(!response.ok)throw Error("HTTP_"+response.status);
  const a=await response.json();
  if(a.version!=="V12_EARLIEST_UNBROKEN_CHRONOLOGICAL_AUDIT_20261016"||
    a.scientificGate.promote!==false||
    a.auditLimitations.prospectiveBlindPeriod!==false||
    a.auditLimitations.trueBankBidAsk!==false)throw Error("EARLIEST_RESEARCH_CONTRACT_INVALID");
  const entries=[
   ...a.continuous.yearly.map(y=>({
     period:String(y.year)+" sonu",final:y.yearEndUSD,
     details:y.filledTrades+" işlem · "+y.memoryReadyDays+" model-hazır gün"
   })),
   {period:"2023–2026 pasif ALTIN",final:a.passiveGold.finalUSD,details:"İlk banka saati al, Eylül 2026 sonunda sat"},
   {period:"Yalnız Şubat–Eylül 2026",final:a.resetFeb2026.finalUSD,details:"119,75 $ farklı başlangıç; kesintisiz koşu değil"}
  ];
  $("v12EarliestTable").innerHTML=table(
    ["Karşı deney","Komisyon sonrası son bakiye","Gözlem"],
    entries.map(x=>"<tr>"+cell(escapeText(x.period))+
      cell(money(x.final))+cell(escapeText(x.details))+"</tr>")
  );
  const y24=a.continuous.yearly.find(x=>x.year===2024),
    y25=a.continuous.yearly.find(x=>x.year===2025);
  status.textContent="Kesintisiz 2023–2026: 100 $ → "+money(a.continuous.finalUSD)+
    ". İlk kullanılabilir hafıza: "+a.continuous.earliestMemoryReady.slice(0,10)+
    ". İlk gerçek AL: "+a.continuous.firstFilledTrade.at.slice(0,10)+
    ". 2024 net kazanç eşiğini geçen gün: "+y24.buyNetGainGateDays+
    "; 2025 %58 kâr olasılığını geçen gün: "+y25.buyProbabilityGateDays+
    ". Model bilimsel olarak başarılı ilan edilmedi.";
 }catch(err){
  status.textContent="Kesintisiz yürüyüş yüklenemedi: "+err.message;
 }finally{button.disabled=false;}
}
$("runV12Earliest").addEventListener("click",runV12Earliest);

async function runV13Sentez(){
 const b=$("runV13Sentez"),status=$("v13SentezStatus");
 b.disabled=true;
 status.textContent="SENTEZ: 2023 başlangıcı, 14/56 gün olgunlaşmış tahminler ve ANN/bulanık/hafıza karşı testleri çalışıyor…";
 try{
  const response=await fetch("/api/algorithm/v13/sentez",{cache:"no-store"});
  if(!response.ok)throw Error("HTTP_"+response.status);
  const r=await response.json();
  if(r.version!=="V13_SENTEZ_RESEARCH_AUDIT_20261016"||
   r.status!=="SHADOW_EXPERIMENT_NO_AUTOMATIC_PROMOTION"||
   r.scientificGate.promote!==false||
   r.scientificGate.liveTrading!==false||
   r.scientificGate.blind2026!==false||
   r.scientificGate.bankBidAskVerified!==false||
   r.experiments.length!==20)throw Error("SENTEZ_CONTRACT_REJECTED");
  const get=(period,variant="SENTEZ_HYBRID")=>
     r.experiments.find(x=>x.period===period&&x.variant===variant);
  const full=get("2023_TO_2026"),a2025=get("2025"),a2026=get("2026_FEB_SEP");
  $("v13Full").textContent=money(full.finalUSD);
  $("v13Hold").textContent=money(full.buyHoldUSD);
  $("v13Year2025").textContent=money(a2025.finalUSD);
  $("v13Year2026").textContent=money(a2026.finalUSD);
  $("v13Ablations").innerHTML=table(
   ["Dönem","Model bileşenleri","Komisyonlu final","Pasif ALTIN","İşlem"],
   r.experiments.map(x=>"<tr>"+cell(escapeText(x.period))+
    cell(escapeText(x.variant))+cell(money(x.finalUSD))+
    cell(money(x.buyHoldUSD))+cell(x.trades)+"</tr>")
  );
  const tr=function(s){return new Intl.DateTimeFormat("tr-TR",{
   timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",
   hour:"2-digit",minute:"2-digit",hour12:false
  }).format(new Date(s));};
  $("v13Trades").innerHTML=table(
   ["Sinyal (TR)","İşlem (TR)","AL/SAT","Fiyat vekili","Gerekçe"],
   full.ledger.map(x=>"<tr>"+cell(escapeText(tr(x.asOf)))+
    cell(escapeText(tr(x.at)))+cell(x.side==="BUY"?"AL":"SAT")+
    cell(format.format(x.price))+cell(escapeText(x.why))+"</tr>")
  );
  status.textContent="SENTEZ deneyleri tamamlandı: 2023–2026 "+
   money(full.finalUSD)+"; pasif altın "+money(full.buyHoldUSD)+
   "; 2026 Şubat–Eylül "+money(a2026.finalUSD)+
   ". Otomatik model terfisi yok.";
  $("v13SentezWarning").textContent=
   "ARAŞTIRMA, YATIRIM SİNYALİ DEĞİL. ANN ağı yıllık yalnız geçmişte tamamlanan etiketlerle "+
   "geri yayılımla öğreniyor. Bulanık Sugeno sonuç kuralları 14 ve 56 günlük net getiriler "+
   "oluştukça güncelleniyor; kapılı geçmiş hafızası LSTM'den esinli ama kapıları eğitilmiş "+
   "gerçek LSTM değil. 2023–2026 daha önce görülmüş dönem, ileri kör test yok. "+
   "2026'da SENTEZ bankadaki nakitten daha kötü; gerçek banka ASK/BID ve "+
   "zaman damgalı ekonomik firstprint kanıtları doğrulanmadı. "+
   "Eski sürümler korunuyor, canlı emir yok.";
 }catch(err){
  status.textContent="SENTEZ araştırması yüklenemedi: "+err.message+
    ". Eski modellere dokunulmadı.";
 }finally{b.disabled=false;}
}
$("runV13Sentez").addEventListener("click",runV13Sentez);



/* Existing MODEL research outputs — January / February 2023 daily explorer.
 * Deliberately separate from frozen 2026 V1 and 2023 legacy V13 workflows.
 */
let model23=null,model23SelectedDate=null;
const model23Numeric=new Intl.NumberFormat("tr-TR",{minimumFractionDigits:2,maximumFractionDigits:2});
const model23Four=new Intl.NumberFormat("tr-TR",{minimumFractionDigits:3,maximumFractionDigits:4});
function model23Value(v,suffix=""){
 return typeof v==="number"&&Number.isFinite(v)?model23Numeric.format(v)+suffix:"Veri yok";
}
function model23Direction(v){return v==="UP"?"Yukarı":v==="DOWN"?"Aşağı":"Yön belirsiz";}
function model23Phase(v){
 return ({START:"Başlangıç",CONTINUE:"Devam",PULLBACK:"Düzeltme",
  END:"Bitiş",REENTRY:"Yeniden giriş",NEUTRAL:"Nötr",
  WARMUP:"Öğrenme aşaması",UNREADY:"Hazır değil"})[v]||"Veri yok";
}
function model23DayLabel(date){return date.slice(8,10)+"."+date.slice(5,7)+"."+date.slice(0,4);}
function model23Percent(v){
 if(typeof v!=="number")return "—";
 return (v>0?"+":"")+model23Numeric.format(v)+"%";
}
function model23Rows(){
 if(!model23)return;
 const filter=$("model23Filter").value;
 const days=model23.days.filter(function(d){
  return filter==="all"||filter==="candidate"&&d.hasSession&&d.ruleCandidate||
   filter==="observed"&&d.hasSession;
 });
 $("model23RowsLabel").textContent=days.length+" gün / "+model23.days.length+" takvim günü";
 const lines=days.map(function(d){
  const phase=d.hasSession?model23Phase(d.s2.fastPhase):"İşlem seansı yok";
  const side=d.s2.fastDirection?model23Direction(d.s2.fastDirection):"";
  const cls=d.date===model23SelectedDate?"model23-selected":d.ruleCandidate?"model23-highlight":"";
  const econ=d.ruleCandidate?
   '<span class="model23-hypo">'+escapeText(d.ruleCandidate)+'</span><small>Doğrulanmamış araştırma adayı</small>':
   '<span class="muted">—</span>';
  const actual=d.hasSession?
   '<b class="'+(d.observedSessionReturnPct>=0?"positive":"negative")+'">'+
    model23Percent(d.observedSessionReturnPct)+'</b>':"—";
  return '<tr class="'+cls+'">'+
   cell('<button type="button" class="model23-day" data-model23-date="'+escapeText(d.date)+'">'+
    escapeText(model23DayLabel(d.date))+'</button>')+
   cell(econ)+
   cell(d.hasSession?model23Value(d.s1.pUpPct,"%"):"—")+
   cell(d.hasSession?model23Four.format(d.s1.expectedLogPct)+"%":"—")+
   cell(escapeText(phase)+(side?"<small>"+escapeText(side)+"</small>":""))+
   cell(d.hasSession?model23Value(d.s2.trendZ):"—")+
   cell(d.hasSession?"<span class='model23-decision'>NAKİT KORU</span>":"—")+
   cell(actual)+"</tr>";
 });
 $("model23Rows").innerHTML=table([
  "Tarih","Ekonomik kural adayı","S1 UP · +4 saat",
  "S1 beklenen log%","S2 evre / yön","S2 trend z","S3 araştırma","Altın · aynı seans"
 ],lines);
}
function model23Detail(){
 const d=model23?.days.find(x=>x.date===model23SelectedDate);
 if(!d){$("model23Detail").textContent="Gün seçin.";return;}
 $("model23DetailDate").textContent=model23DayLabel(d.date);
 if(!d.hasSession){
  $("model23Detail").innerHTML='<p class="notice">Bu tarihle etiketlenen araştırma seansında fiyat kaydı yok. S1, S2 veya S3 sinyali üretilmiş gibi gösterilmez.</p>';
  return;
 }
 const detailed=[
  {title:"Ekonomik kural adayı",value:d.ruleCandidate||"Eşleşme yok",
   info:"OLAY-02 / ÖĞREN-03 araştırma teşhisi; öğrenilmiş kesin ekonomik kural değil."},
  {title:"S1 · UP olasılığı (+4 saat)",value:model23Value(d.s1.pUpPct,"%"),
   info:"Gün sonu itibarıyla sonraki 4 saat. Piyasa-temelli; ekonomik alpha kanıtı değil."},
  {title:"S1 · beklenen log getiri (+4 saat)",
   value:model23Four.format(d.s1.expectedLogPct)+"%",
   info:"Tüm işlem maliyetleri sonrası AL getirisi veya günlük getiri değildir."},
  {title:"S2 · hızlı hareket evresi",value:model23Phase(d.s2.fastPhase)+
   (d.s2.fastDirection?" / "+model23Direction(d.s2.fastDirection):""),
   info:"Tamamlanmış 15 dakikalık fiyatlar üzerinden; trend z="+model23Value(d.s2.trendZ)+"."},
  {title:"S2 · uzun evre",value:model23Phase(d.s2.slowPhase),
   info:"Uzun hareket bitiş olasılığı bu raporda kalibre edilmiş olarak hazır değil."},
  {title:"S3 · araştırma sonucu",value:"NAKİT KORU",
   info:"Model KEEP verdi. Onaylı AL/SAT emri, gölge portföy işlemi veya ekonomik neden ispatı yok."},
  {title:"Altının o seanstaki gerçekleşen hareketi",value:model23Percent(d.observedSessionReturnPct),
   info:"Aynı günün ilk–son fiyatı; S1'in ileri 4 saat tahminiyle karşılaştırmayın."}
 ];
 let html='<div class="model23-detail-grid">'+detailed.map(function(k){
  return '<article class="model23-detail-card"><span>'+escapeText(k.title)+'</span>'+
   '<strong>'+escapeText(k.value)+'</strong><small>'+escapeText(k.info)+'</small></article>';
 }).join("")+'</div>';
 if(d.economicRelease){
  const e=d.economicRelease;
  const date=new Intl.DateTimeFormat("tr-TR",{timeZone:"Europe/Istanbul",
   year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}).format(new Date(e.at));
  html+='<div class="model23-release"><h3>Ekonomik açıklama sonrası ilk araştırma gözlemi</h3>'+
   '<p>Türkiye saati: <strong>'+escapeText(date)+'</strong> (ilk yayın doğrulanmadı, varsayılan +60 dk gecikme).</p>'+
   '<p><strong>Ekonomiye özgü S1:</strong> Hazır değil. '+
   '<strong>S2:</strong> '+escapeText(model23Phase(e.s2Phase))+
   (e.s2Direction?" / "+escapeText(model23Direction(e.s2Direction)):"")+
   ', trend z: '+model23Value(e.s2TrendZ)+
   '. <strong>S3:</strong> NAKİT KORU.</p>'+
   '<small>Bu gözlem gün sonu ölçümünden farklı saattedir. Sonradan oluşan fiyatı bu anın bilgisi saymıyoruz.</small></div>';
 }
 $("model23Detail").innerHTML=html;
}
function renderModel23(){
 if(!model23)return;
 $("model23Rules").textContent=model23.startingLearnedMarketRules;
 $("model23Labels").textContent=model23.startingMaturedFourHourLabels;
 $("model23Events").textContent=model23.ruleCandidateDays;
 $("model23Trades").textContent="0";
 $("model23Status").textContent=model23.label+" · "+model23.sessionDays+
  " fiyat seansı · "+model23.monthM15Bars+" adet 15 dakikalık fiyat kaydı · S3 işlem önerisi: NAKİT KORU.";
 $("model23Source").innerHTML="Kaynak: <a href='"+escapeText(model23.sourceRun)+
  "' target='_blank' rel='noopener noreferrer'>"+escapeText(model23.label)+
  " CORE GitHub test kaydı</a>. "+model23.trainingM15Bars+
  " geçmiş fiyat barıyla öğrenilmiş; Şubat'ta Ocak hafızası korunmuştur. Bu veriler banka BID/ASK değil; araştırma amaçlı yeniden oluşturulmuş MID kotasyonlarıdır.";
 model23Rows();
 model23Detail();
}
async function loadModel23(){
 const month=$("model23Month").value;
 model23=null;model23SelectedDate=null;
 $("model23Rows").textContent="Günlük veriler kontrol ediliyor…";
 $("model23Detail").textContent="Seçilen gün yükleniyor…";
 $("model23Status").textContent=month+" kayıtları yükleniyor…";
 try{
  const res=await fetch("/api/model/2023/daily?month="+encodeURIComponent(month),{cache:"no-store"});
  if(!res.ok)throw Error("Kaynak doğrulama veya API hatası: "+res.status);
  const result=await res.json();
  if(result.version!=="GOLD_MODEL_2023_DAILY_READONLY_VIEW_V1_20261017"||
     result.month!==month||result.bankTradeAuthorized!==false||
     result.actualEconomicRuleLearningVerified!==false||!Array.isArray(result.days)||
     result.days.length!==(month==="2023-01"?31:28))
   throw Error("2023 model rapor sözleşmesi uyuşmuyor");
  model23=result;
  model23SelectedDate=result.days.find(d=>d.hasSession&&d.ruleCandidate)?.date||
    result.days.find(d=>d.hasSession)?.date;
  renderModel23();
 }catch(err){
  $("model23Status").textContent="2023 raporu gösterilemiyor: "+err.message+
   ". Bu ekran eksik değeri tahmin ederek doldurmaz.";
  $("model23Rows").textContent="Kaynak hatası nedeniyle günlük metrikler görüntülenemedi.";
  $("model23Detail").textContent="—";
 }
}
$("model23Month").addEventListener("change",loadModel23);
$("model23Filter").addEventListener("change",function(){
 if(model23){model23Rows();}
});
$("model23Rows").addEventListener("click",function(e){
 const button=e.target.closest("button[data-model23-date]");
 if(!button||!model23)return;
 const date=button.getAttribute("data-model23-date");
 if(!model23.days.some(d=>d.date===date))return;
 model23SelectedDate=date;model23Rows();model23Detail();
});
loadModel23();


/* Jan 2023: actual CORE replay through M1 operational cadence validation.
 * This is a scrubbed, immutable research aggregate, NOT a live market feed.
 */
let selective23=null,selective23Index=0;
function selective23N(v,digits=2){
 return typeof v==="number"&&Number.isFinite(v)?
  new Intl.NumberFormat("tr-TR",{minimumFractionDigits:digits,maximumFractionDigits:digits}).format(v):"—";
}
function selective23Phase(v){
 return ({START:"Başlangıç",CONTINUE:"Devam",PULLBACK:"Düzeltme",
  REENTRY:"Yeniden giriş",END:"Bitiş",NEUTRAL:"Nötr",
  WARMUP:"Hazırlık",UNREADY:"Hazır değil"})[v]||"—";
}
function selective23Date(d){return d.date.slice(8,10)+" Ocak 2023";}
function selective23Draw(){
 if(!selective23)return;
 const days=selective23.days.slice(0,selective23Index+1);
 const d=days.at(-1),s=d.snapshot;
 const n=(a,key)=>a.reduce((x,y)=>x+(y[key]||0),0);
 $("selective23Bars").textContent=n(days,"m1Accepted");
 $("selective23Events").textContent=n(days,"eventCandidateCount");
 $("selective23Watches").textContent=n(days,"priceChangeWatchCount");
 $("selective23Trades").textContent="0";
 $("selective23DaySlider").value=String(selective23Index+1);
 $("selective23ProgressLabel").textContent=selective23Date(d)+" · "+(selective23Index+1)+"/31";
 $("selective23Count").textContent=days.length+" takvim günü, "+days.filter(x=>x.hasSession).length+" fiyat seansı";
 $("selective23Next").disabled=selective23Index>=30;
 const s1=s?.s1,s2=s?.s2,s3=s?.s3;
 let headline=d.eventCandidateCount?"Arşivde ekonomik açıklama adayı":
  d.priceChangeWatchCount?"Fiyat hareketi izleme işareti":"Yeni doğrulanmış ekonomik açıklama yok";
 let details=s?
  '<div class="selective23-current-grid">'+
  '<article><span>S1 · +4 saat UP</span><strong>'+ (s1.ready?selective23N(s1.pUpPct)+"%":"Hazır değil")+
    '</strong><small>Tamamlanan seansın son gözlemi · fiyat temelli</small></article>'+
  '<article><span>S2 · hızlı evre</span><strong>'+escapeText(selective23Phase(s2.phase))+
    (s2.direction===1?" ↑":s2.direction===-1?" ↓":"")+
    '</strong><small>Trend z: '+selective23N(s2.trendZ)+'</small></article>'+
  '<article><span>S2 · uzun</span><strong>'+escapeText(selective23Phase(s2.slowPhase))+
    '</strong><small>Kalan hareket süresi kalibre değil</small></article>'+
  '<article><span>S3 · araştırma</span><strong>NAKİT KORU</strong>'+
    '<small>Gerekçe: '+escapeText(s3.reason)+'. Banka emri yok.</small></article>'+
  '</div>': '<p>Bu tarih için tamamlanmış fiyat seansı yok; fiyat veya AL/SAT sinyali uydurulmadı.</p>';
 if(d.eventNotes.length){
  details+='<div class="selective23-research-note"><strong>Ekonomik yayın denetimi:</strong> '+
   d.eventNotes.map(x=>escapeText(x.scheduledReleaseUTC.slice(11,16))+
    ' UTC · varsayılan erişim '+escapeText(x.assumedResearchAvailableUTC.slice(11,16))+
    ' UTC · ilk yayın ve beklenti vintage kanıtı olmadığından koşullu S1 özelliği engellendi.')
   .join(" ")+'</div>';
 }
 if(d.priceChangeWatchCount)details+='<p class="selective23-watch">O gün '+d.priceChangeWatchCount+
   ' adet ardışık 15dk fiyat hareketi ≥%0,5 işareti görüldü. Bu bir ekonomik neden veya AL/SAT sinyali değildir.</p>';
 if(d.ruleCandidate)details+='<p><strong>Geriye dönük ekonomik kural adayı:</strong> '+
   escapeText(d.ruleCandidate)+' <small>(sonradan eklenmiş araştırma notu; o anda doğrulanmış otomatik tetik değil)</small></p>';
 $("selective23Current").innerHTML='<h3>'+escapeText(selective23Date(d))+
  ' · '+escapeText(headline)+'</h3>'+details+
  (d.hasSession?'<p class="selective23-sessionret">O günün gerçekleşmiş fiyat hareketi: <strong>'+
   (d.observedSessionReturnPct>0?"+":"")+selective23N(d.observedSessionReturnPct,3)+'%</strong> (aynı seans; S1 tahmininin hedefi değildir)</p>':"");
 const rows=days.map(row=>{
  const z=row.snapshot,m=row.ruleCandidate||"—";
  const ret=row.hasSession?(row.observedSessionReturnPct>=0?"+":"")+
   selective23N(row.observedSessionReturnPct,3)+"%":"—";
  const sl=z?.s2,cellV=val=>cell(escapeText(val));
  return '<tr class="'+(row.date===d.date?"model23-selected":row.eventCandidateCount?"model23-highlight":"")+'">'+
   cellV(row.date)+cellV(row.barCount)+cellV(row.eventCandidateCount)+
   cellV(row.priceChangeWatchCount)+cellV(m)+
   cellV(z?.s1?.ready?selective23N(z.s1.pUpPct)+"%":"—")+
   cellV(sl?selective23Phase(sl.phase)+(sl.direction===1?" / ↑":sl.direction===-1?" / ↓":""):"—")+
   cellV(z?"NAKİT KORU":"—")+cellV(ret)+"</tr>";
 });
 $("selective23Table").innerHTML=table(
  ["Gün","M15","Olay kanıt kontrolü","Fiyat izleme","Ekonomik araştırma adayı","S1 UP","S2 evre","S3 araştırma","Gün içi altın"],
  rows);
 $("selective23Status").textContent=(selective23Index===30?
  "Ocak 2023 arşiv yürüyüşü tamamlandı. ":"Gün gün ilerliyorsunuz. ")+
  "CORE yalnız tamamlanmış M15 kayıtlarını kullandı. Arşiv haberleri PIT-sertifikalı değil; ekonomi sinyali olarak kullanılmadı.";
}
async function selective23Load(){
 try{
  const r=await fetch("/api/model/2023/january/selective-walk",{cache:"no-store"});
  if(!r.ok)throw Error("HTTP "+r.status);
  const x=await r.json();
  if(x.version!=="GOLD_JAN2023_SELECTIVE_M1_S1_S2_S3_WALK_V1_20261017"||
    x.days?.length!==31||x.tradeAllowed!==false||x.firstPrintMacroVerified!==false||
    x.observed?.gateCalls!==1920||x.observed?.modelCalls!==1920||
    x.observed?.macroPITFeaturesAccepted!==0)
   throw Error("CORE kaynak/kanıt sözleşmesi tutarsız");
  selective23=x;selective23Index=0;
  $("selective23Source").innerHTML="Kaynak: <a target='_blank' rel='noopener noreferrer' href='"+
   escapeText(x.sourceWorkflowRun)+"'>Ocak 2023 gerçek CORE yürüyüşünün başarılı GitHub çalışması</a>. "+
   escapeText(x.prior.bars)+" M15 önceki öğrenme, 1.920 Ocak fiyat kontrolü, yalnız 2 geriye dönük makro adayı. "+
   "Ne gerçek 2023 canlı fiyat erişim kayıtları ne de sertifikalı haber ilk baskıları mevcuttur.";
  selective23Draw();
 }catch(e){
  $("selective23Status").textContent="Ocak 2023 yürüyüşü gösterilemedi: "+
   e.message+". Eksik kayıt yerine sentetik sinyal üretmiyoruz.";
  $("selective23Current").textContent="Kaynak hatası.";
  $("selective23Table").textContent="—";
 }
}
$("selective23Restart").addEventListener("click",()=>{
 if(selective23){selective23Index=0;selective23Draw();}
});
$("selective23Next").addEventListener("click",()=>{
 if(selective23&&selective23Index<30){selective23Index++;selective23Draw();}
});
$("selective23All").addEventListener("click",()=>{
 if(selective23){selective23Index=30;selective23Draw();}
});
$("selective23DaySlider").addEventListener("input",e=>{
 if(selective23){selective23Index=Math.max(0,Math.min(30,Number(e.target.value)-1));selective23Draw();}
});
selective23Load();



/* Jan-Feb2023 real chronological GOLD CORE + AI evidence handoff dashboard.
 * This view must NOT manufacture GPT decisions or imply bank execution.
 */
let ai23=null,ai23Day=0;
const ai23Fmt=(v,dp=2)=>typeof v==="number"&&Number.isFinite(v)?
 new Intl.NumberFormat("tr-TR",{minimumFractionDigits:dp,maximumFractionDigits:dp}).format(v):"—";
function ai23Phase(p){
 return ({START:"BAŞLANGIÇ",CONTINUE:"DEVAM",PULLBACK:"DÜZELTME",
 END:"BİTİŞ",REENTRY:"YENİDEN GİRİŞ",NEUTRAL:"NÖTR",
 WARMUP:"ISINMA",GAP:"VERİ BOŞLUĞU"})[p]||"—";
}
function ai23Render(){
 if(!ai23)return;
 const days=ai23.dates.slice(0,ai23Day+1),d=days.at(-1),sum=ai23.portfolioAudit;
 const cumulative=(k)=>days.reduce((v,x)=>v+(x[k]||0),0);
 $("ai23Bars").textContent=ai23Fmt(cumulative("bars"),0);
 $("ai23Attention").textContent=ai23Fmt(cumulative("attention"),0);
 $("ai23Macro").textContent=ai23Fmt(cumulative("observedArchiveMacroWaves"),0);
 $("ai23GPT").textContent=ai23Fmt(sum.aiUsed,0);
 $("ai23Slider").value=String(ai23Day+1);
 $("ai23Next").disabled=ai23Day===58;
 $("ai23Progress").textContent=d.date+" · "+(ai23Day+1)+"/59";
 $("ai23Count").textContent=days.length+" takvim günü";
 const portRows=[
  {title:"Mevcut S1–S2–S3",usd:sum.arms.CORE.finalLiquidatableUSD,desc:"CORE araştırma konumu: NAKİT"},
  {title:"AI yorumcu",usd:null,desc:"GPT kararı henüz gelmedi; kâr puanı hesaplanmadı"},
  {title:"Hibrit",usd:null,desc:"Gerçek AI kararı ve ekonomik doğrulama bekliyor"},
  {title:"Sadece NAKİT",usd:sum.reference.cashUSD,desc:"Karşılaştırma kıstası"},
  {title:"Altın AL ve TUT",usd:sum.reference.buyHoldLiquidatableUSD,desc:"Vendor ASK/BID ve iki yönlü %0,8 ücret ile kıyas"}
 ];
 $("ai23Portfolio").innerHTML=portRows.map(x=>
  '<article><span>'+escapeText(x.title)+'</span><strong>'+
  (x.usd===null?"VERİ YOK":ai23Fmt(x.usd)+" $")+
  '</strong><small>'+escapeText(x.desc)+'</small></article>').join("");
 const s=d.core,notes=[];
 if(d.knownEconomicResearchCandidate)notes.push(
  '<p><b>Ekonomik araştırma notu:</b> '+
  escapeText(d.knownEconomicResearchCandidate)+
  '<br><small>Bu başlık geriye dönük adaydır; haber o anda doğrulanmış ve GPT tarafından yorumlanmış sayılmaz.</small></p>');
 if(d.observedArchiveMacroWaves)notes.push(
  '<p class="ai23-caution"><strong>'+d.observedArchiveMacroWaves+
  ' arşiv ekonomik yayın dalgası:</strong> ilk-baskı ve konsensüs vintage kanıtı bulunmadığı için karantinada. S1 ekonomik tahminine zorla sokulmadı.</p>');
 const att=Object.entries(d.attentionReasons||{}).map(([k,v])=>{
  const names={DAY_OPEN:"Gün değerlendirmesi",EVENT:"Ekonomik olay incelemesi",
   PHASE_CHANGE:"Hareket evresi değişimi",PRICE_WATCH:"Fiyat hareketi uyarısı"};
  return escapeText(names[k]||k)+" ×"+v;
 }).join(" · ");
 const dir=s?.s2?.direction===1?" ↑":s?.s2?.direction===-1?" ↓":"";
 let content=s?
  '<div class="ai23-metrics"><article><span>S1 · UP (+4s)</span><strong>'+
  (s.s1.ready?ai23Fmt(s.s1.pUpPct)+"%":"HAZIR DEĞİL")+'</strong>'+
  '<small>Fiyat ağırlıklı; ekonomik ORG doğrulanmadı</small></article>'+
  '<article><span>S2 · fiyat evresi</span><strong>'+escapeText(ai23Phase(s.s2.phase)+dir)+
  '</strong><small>Trend z: '+ai23Fmt(s.s2.trendZ)+'</small></article>'+
  '<article><span>S3 · matematiksel model</span><strong>NAKİT KORU</strong>'+
  '<small>'+escapeText(s.s3.reason)+"</small></article>"+
  '<article><span>GPT · ekonomik yorum</span><strong>BEKLENİYOR</strong>'+
  '<small>Gerçek GPT yanıtı yok · uydurulmuş işlem yok</small></article></div>':
  '<p>Bu tarihte tamamlanmış fiyat seansı yok. Önceki ekonomik olay ve portföy hafızası korunur; yeni tahmin veya fiyat üretilmez.</p>';
 content+=notes.join("");
 if(d.attention)content+='<p><strong>AI inceleme adayları:</strong> '+d.attention+
  ' · '+att+'</p>';
 if(d.hasSession)content+='<p>Bu seansın **sonradan ölçülen** altın getirisi: <strong>'+
  (d.observedSessionReturnPct>0?"+":"")+ai23Fmt(d.observedSessionReturnPct,3)+
  '%</strong>. Bu getiri karar öncesi GPT girdisi değildir.</p>';
 content+='<p class="ai23-caution"><strong>Deney modu:</strong> GPT ekonomik açıklama ve karşıt kanıt içeren gerekçeli yanıt göndermediği sürece AI ve hibrit araştırma emirleri üretilmeyecek.</p>';
 $("ai23Current").innerHTML='<h3>'+escapeText(d.date)+" · o ana kadar modelin kayıtları</h3>"+content;
 $("ai23Table").innerHTML=table(
  ["Gün","M15","AI kontrol","Ekonomik aday","S1 UP","S2","S3","GPT","Altın seans"],
  days.map(x=>{
   const z=x.core,macro=x.knownEconomicResearchCandidate||"—";
   return "<tr>"+cell(escapeText(x.date))+cell(x.bars)+cell(x.attention)+
    cell(escapeText(macro))+cell(z?.s1?.ready?ai23Fmt(z.s1.pUpPct)+"%":"—")+
    cell(z?escapeText(ai23Phase(z.s2.phase)):"—")+
    cell(z?"NAKİT KORU":"—")+cell("YOK")+
    cell(x.hasSession?(x.observedSessionReturnPct>0?"+":"")+
     ai23Fmt(x.observedSessionReturnPct,3)+"%":"—")+"</tr>";
  }));
 $("ai23Status").textContent="İşlenen "+ai23Fmt(cumulative("bars"),0)+
  " M15 bar · "+cumulative("attention")+" AI inceleme adayı · "+
  cumulative("observedArchiveMacroWaves")+" arşiv ekonomik açıklama dalgası. "+
  "AI/Hibrit kararları hazır değil; ekranda görülen gerçekleşmiş seans getirileri geçmiş test sonuçlarıdır.";
}
async function ai23Load(){
 try{
  const response=await fetch("/api/model/2023/jan-feb-ai-shadow",{cache:"no-store"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const x=await response.json();
  if(x.version!=="GOLD_2023_JAN_FEB_ACTUAL_CORE_WITH_GPT_HANDOFF_V1_20261017"||
   x.dates?.length!==59||x.aiProviderConnected!==false||
   x.portfolioAudit?.aiUsed!==0||x.portfolioAudit?.bankTradeAuthorized!==false||
   x.mainScientificGate!=="FAIL_NOT_BLIND_OOS")
    throw Error("AI/GOLD araştırma kaynak veya kanıt sözleşmesi uyuşmuyor");
  ai23=x;ai23Day=0;ai23Render();
  $("ai23Source").innerHTML="Kaynak: <a target='_blank' rel='noopener noreferrer' href='"+
   escapeText(x.sourceRun)+"'>2023 Ocak–Şubat gerçek fiyat yürüyüşü ve test kaydı</a>. "+
   "2022 Q4 "+x.pretrain.bars+" ön öğrenme barı; "+
   x.janFebBars+" tarihsel Ocak–Şubat barı; "+
   "ekonomik haber ilk-baskı kanıtı ve 2023'e ait GPT yanıtı mevcut değil.";
 }catch(e){
  $("ai23Status").textContent="AI deney verisi doğrulanamadı: "+e.message;
  $("ai23Current").textContent="Eksik kayıttan yapay zekâ kararı üretilemez.";
  $("ai23Portfolio").textContent="—";$("ai23Table").textContent="—";
 }
}
$("ai23Start").addEventListener("click",()=>{if(ai23){ai23Day=0;ai23Render();}});
$("ai23Next").addEventListener("click",()=>{if(ai23&&ai23Day<58){ai23Day++;ai23Render();}});
$("ai23End").addEventListener("click",()=>{if(ai23){ai23Day=58;ai23Render();}});
$("ai23Slider").addEventListener("input",v=>{
 if(ai23){ai23Day=Math.max(0,Math.min(58,Number(v.target.value)-1));ai23Render();}
});
ai23Load();


/* Research overlay: never updates S1/S2 calculations or trading decisions. */
(function(){
 const year=document.getElementById("downNewsYear"),output=document.getElementById("downNewsRows"),status=document.getElementById("downNewsStatus");
 if(!year||!output||!status)return;
 const trTime=v=>v?new Date(v).toLocaleString("tr-TR",{timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}):"Saat kanıtı yok";
 let records=[];
 function draw(){
  const selected=records.filter(r=>year.value==="all"||r.startPivotDay.startsWith(year.value));
  output.replaceChildren();
  const table=document.createElement("table"),thead=document.createElement("thead"),headers=["Düşüş dönemi / büyüklük","İlişkili haber (araştırma)","Haber saati (TSİ)","İlk ≥%0,5 gerileme (TSİ)","Zaman sırası","İlk haber kanıtı"];
  const hr=document.createElement("tr");
  headers.forEach(h=>{const th=document.createElement("th");th.textContent=h;hr.append(th);});thead.append(hr);table.append(thead);
  const tbody=document.createElement("tbody");
  selected.forEach(r=>{
   const row=document.createElement("tr");const add=t=>{const cell=document.createElement("td");cell.textContent=String(t);row.append(cell);return cell;};
   add(r.startPivotDay+" → "+r.endPivotDay+" · "+Number(r.fullLegPct).toFixed(2)+"%");
   const n=add(r.newsHeadline||"Henüz belirlenmedi");
   if(r.sourceUrl&&/^https:\/\//.test(r.sourceUrl)){const link=document.createElement("a");link.href=r.sourceUrl;link.target="_blank";link.rel="noopener noreferrer";link.textContent=" Kaynak ↗";n.append(link);}
   add(r.documentedNewsReleaseUtc?trTime(r.documentedNewsReleaseUtc):(r.newsDate||"Bilinmiyor")+" · yalnız tarih");
   add(trTime(r.firstHalfPctDrawdownUtc));
   const news=Date.parse(r.documentedNewsReleaseUtc||""),price=Date.parse(r.firstHalfPctDrawdownUtc||"");
   add(Number.isFinite(news)&&Number.isFinite(price)?(news<price?"Haber eşikten önce":news>price?"Haber eşikten sonra":"Aynı anda"): "Saat sırası doğrulanamıyor");
   add(r.newsOriginalFirstAvailableUtcCertified?"Doğrulandı":"Doğrulanmadı");
   tbody.append(row);
  });
  table.append(tbody);output.append(table);
  status.textContent=selected.length+" düşüş gösteriliyor. S1/S2 bağımsız karar üretir; bu araştırma örtüsü işlem kararını değiştirmez.";
 }
 year.addEventListener("change",draw);
 fetch("/api/research/down-news",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json();}).then(data=>{if(!Array.isArray(data.records)||data.records.length!==17)throw Error("17 olay bulunamadı");records=data.records;draw();}).catch(e=>{status.textContent="Haber/düşüş araştırması yüklenemedi: "+e.message;});
})();
