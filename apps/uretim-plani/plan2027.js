(()=>{'use strict';
const MONTHS=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
// Setup kuralı: iki şönt ayı, ardından bir harmonik ayı, yıl boyunca tekrar.
const FAMILIES=['Şönt','Şönt','Harmonik','Şönt','Şönt','Harmonik','Şönt','Şönt','Harmonik','Şönt','Şönt','Harmonik'];
const STORAGE_KEY='simulation3.production2027.matrix.v1';
const CHECKPOINT_KEY=STORAGE_KEY+'.checkpoint';
const RECOVERY_KEY=STORAGE_KEY+'.unmatched-backup';
const UPPER_BACKUP_KEY=STORAGE_KEY+'.before-upper-optimization';
const SNAPSHOT_FORMAT='simulation3-uretim-plani-2027';
const SNAPSHOT_VERSION=2;
const $=id=>document.getElementById(id);
const fmt=x=>Number(x||0).toLocaleString('tr-TR');
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let products=[],byId=new Map(),history=[],rowOrder=[],initialOrder=[],optimizedPlan=new Map(),groupKeys=[],allGroupsVisible=false,search='',familyFilter='all',active=null,drag=null,rowDrag=null,toastHandle=null,storageEnabled=true,restorationWarning='',hasCheckpoint=false;
async function unzipBase64(b64){
 if(typeof DecompressionStream==='undefined')throw Error('Bu tarayıcı veri sıkıştırma biçimini desteklemiyor. Güncel Chrome/Edge kullanın.');
 const data=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
 return JSON.parse(await new Response(new Blob([data]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
}
function monthlyTotal(i){return products.reduce((n,p)=>n+p.monthly[i],0)}
function totalAnnual(){return products.reduce((n,p)=>n+p.annual,0)}
function firstMonth(p){return p.monthly.findIndex(v=>v>0)}
function pattern(p){return p.monthly.map((v,i)=>v>0?i:null).filter(v=>v!==null).join('-')}
function monthsName(p){return p.monthly.map((v,i)=>v>0?MONTHS[i]:null).filter(Boolean).join(' · ')}

const GROUP_PALETTE=[
 ['#DCEAFF','#275DA5','#BDD5FA'],['#F0E2FB','#7A45A1','#DEC6F2'],
 ['#DAF2E7','#23815A','#B6E4D0'],['#FFF0D6','#9F671C','#F4D6A7'],
 ['#E4EDF4','#52748D','#CADBE8'],['#FCE5E0','#A6534B','#F2C7C0'],
 ['#DCF3F6','#217A88','#B9E3EB'],['#F9E7EF','#A74E75','#EFC8DA'],
 ['#ECF0D7','#677C27','#DAE3AE'],['#E7E5F9','#6662AE','#D0C9EE']
];
// Üretim yapılan aylar ve ürün ailesi aynıysa aynı grup/rengi kullanılır.
function groupKey(p){return p.family+'|'+pattern(p)}
function ensureGroup(key){let i=groupKeys.indexOf(key);if(i<0){groupKeys.push(key);i=groupKeys.length-1}return i+1}
function groupInfo(p){
 const id=ensureGroup(groupKey(p));
 let colors=GROUP_PALETTE[id-1];
 if(!colors){const hue=Math.round(((id-11)*137.508+207)%360);colors=['hsl('+hue+',65%,92%)','hsl('+hue+',55%,32%)','hsl('+hue+',49%,80%)']}
 return {id,colors};
}
function groupStyle(g){return '--group-bg:'+g.colors[0]+';--group-ink:'+g.colors[1]+';--group-border:'+g.colors[2]}
function initializeGroups(){
 const totals=new Map();
 for(const p of products){const key=groupKey(p);totals.set(key,(totals.get(key)||0)+p.annual)}
 groupKeys=[...totals.keys()].sort((a,b)=>totals.get(b)-totals.get(a)||a.localeCompare(b,'tr'));
}
function groupsFromBackup(saved){
 if(!Array.isArray(saved))return;
 for(const key of saved)if(typeof key==='string'&&key.length<100&&key.includes('|'))ensureGroup(key);
}
function renderGroupLegend(){
 const used=new Map();
 for(const p of products){
  const g=groupInfo(p),key=groupKey(p);
  const entry=used.get(key)||{id:g.id,colors:g.colors,qty:0,count:0,family:p.family,months:monthsName(p)};
  entry.qty+=p.annual;entry.count++;used.set(key,entry);
 }
 const entries=[...used.values()].sort((a,b)=>a.id-b.id);
 const shown=allGroupsVisible?entries:entries.slice(0,6);
 const body=shown.map(g=>'<span class="group-key" style="'+groupStyle(g)+'" title="'+esc(g.family+' · '+g.months+' · '+g.count+' ürün · '+fmt(g.qty)+' adet')+'"><strong>G'+g.id+'</strong><span>'+esc(g.months)+'</span></span>').join('');
 $('groupLegend').innerHTML=body+(entries.length>6?'<button class="group-expand" type="button">'+(allGroupsVisible?'Daha az göster':'Tüm '+entries.length+' grubu göster')+'</button>':'');
}

function cloneRows(){return Object.fromEntries(products.map(p=>[p.id,p.monthly.slice()]))}
function validOrder(order){return Array.isArray(order)&&order.length===products.length&&new Set(order).size===products.length&&order.every(id=>byId.has(id))}
const UPPER_GROUP_ORDER=['SVC-R','SRM','SRT','HRM','HRT 5,67','HRT 7/8','HRT 7/7','HRT 14','HRT-G varyant','HRT-GG varyant','Özel Harmonik'];
function upperGroup(p){
 const model=String(p.model||'').toUpperCase(),code=String(p.kod||''),kind=String(p.altGrup||'');
 if(p.family==='Şönt'){
  if(model.startsWith('SVC-R'))return 'SVC-R';
  if(model.startsWith('SRM'))return 'SRM';
  if(model.startsWith('SRT'))return 'SRT';
  return 'Diğer Şönt';
 }
 if(code.startsWith('GAGG'))return 'HRT-GG varyant';
 if(code.startsWith('GAG'))return 'HRT-G varyant';
 if(code==='GA5ÖZELHARM'||(!model.startsWith('HRM')&&!model.startsWith('HRT')))return 'Özel Harmonik';
 if(model.startsWith('HRM'))return 'HRM';
 if(kind.includes('5,67'))return 'HRT 5,67';
 if(kind.includes('14'))return 'HRT 14';
 if(kind.includes('<%7'))return 'HRT 7/7';
 return 'HRT 7/8';
}
function upperRank(p){
 const i=UPPER_GROUP_ORDER.indexOf(upperGroup(p));return i<0?99:i;
}
function defaultCompare(a,b){
 return (a.family==='Şönt'?0:1)-(b.family==='Şönt'?0:1)
  ||upperRank(a)-upperRank(b)||firstMonth(a)-firstMonth(b)
  ||pattern(a).localeCompare(pattern(b))||b.annual-a.annual||a.kod.localeCompare(b.kod,'tr');
}
function sortedUpperIds(){
 return products.slice().sort(defaultCompare).map(p=>p.id);
}
function countGroupMonth(monthlyLookup){
 const used=new Set();
 for(const p of products){
  const m=monthlyLookup(p);
  for(let i=0;i<12;i++)if(m[i]>0)used.add(upperGroup(p)+'|'+i);
 }
 return used.size;
}
function upperPlanIsActive(){
 return products.length>0&&products.every(p=>optimizedPlan.has(p.id)&&p.monthly.every((x,i)=>optimizedPlan.get(p.id)[i]===x));
}
function updateUpperControls(){
 const isActive=upperPlanIsActive(),current=countGroupMonth(p=>p.monthly),proposed=countGroupMonth(p=>optimizedPlan.get(p.id)||p.monthly);
 $('applyUpper').disabled=isActive;
 try{$('returnBeforeUpper').disabled=!localStorage.getItem(UPPER_BACKUP_KEY)}catch(e){$('returnBeforeUpper').disabled=true}
 $('groupPlanSummary').textContent='Üst grup optimizasyonu: '+current+' → '+proposed+' grup-ay üretim bloğu · '+(isActive?'Yeni grup planı etkin.':'Mevcut kayıtlı plan korunuyor; uygulamak için düğmeye basın.')+' · Bobin değerleri ön tahmindir.';
}
function sortUpperGroups(){
 const desired=sortedUpperIds(),before=rowOrder.slice();
 if(before.every((x,i)=>x===desired[i])){toast('Ürünler zaten üst gruplarına göre sıralı.');return}
 history.push({kind:'full-order',order:before});
 rowOrder=desired;save();render();toast('Ürünler SVC-R / SRM / SRT ve Harmonik üst gruplarına göre sıralandı.');
}
function applyUpperOptimization(){
 if(upperPlanIsActive()){toast('Üst grup optimizasyonu zaten etkin.');return}
 if(!confirm('133 ürünün üretim ayları grup bazlı optimizasyona göre değiştirilecek. Mevcut miktarlar ve satır sırası güvenli yedeğe alınacak. Devam edilsin mi?'))return;
 let previous;
 try{
  previous=JSON.stringify(snapshot());
  localStorage.setItem(UPPER_BACKUP_KEY,previous);
  if(localStorage.getItem(UPPER_BACKUP_KEY)!==previous)throw Error('Önceki planın yedeği doğrulanamadı.');
 }catch(e){note('İşlem iptal: mevcut planın kurtarma kaydı oluşturulamadı. Önce JSON yedeğini indirin. '+e.message,'error');return}
 products.forEach(p=>p.monthly=optimizedPlan.get(p.id).slice());
 rowOrder=sortedUpperIds();history=[];
 if(!save()){
  applySnapshot(JSON.parse(previous),false);
  note('Kayıt doğrulanamadı; önceki plan geri yüklendi. JSON yedeği alın.','error');
  render();return;
 }
 render();toast('2027 üst grup planı uygulandı; önceki planınız ayrıca saklandı.');
}
function returnBeforeUpper(){
 try{
  const raw=localStorage.getItem(UPPER_BACKUP_KEY);
  if(!raw)throw Error('Kurtarma noktası bulunamadı.');
  const obj=JSON.parse(raw);
  if(!confirm('Üst grup optimizasyonundan önceki üretim miktarlarını ve satır sırasını geri yüklemek istiyor musunuz?'))return;
  applySnapshot(obj,false);if(!save())throw Error('Tarayıcı kaydı başarısız.');
  render();toast('Optimizasyondan önceki üretim planı geri yüklendi.');
 }catch(e){note('Geri dönüş başarısız: '+e.message,'error')}
}
function visibleRows(){return rowOrder.map(id=>byId.get(id)).filter(p=>p&&(familyFilter==='all'||p.family===familyFilter)&&(p.kod+' '+p.model).toLocaleLowerCase('tr-TR').includes(search.toLocaleLowerCase('tr-TR')))}
function repositionRow(id,targetId,after){
 if(id===targetId||!byId.has(id)||!byId.has(targetId))return false;
 const beforeIndex=rowOrder.indexOf(id);if(beforeIndex<0)return false;
 rowOrder.splice(beforeIndex,1);
 const targetIndex=rowOrder.indexOf(targetId);
 rowOrder.splice(targetIndex+(after?1:0),0,id);
 if(rowOrder[beforeIndex]===id)return false;
 history.push({kind:'row',id,fromIndex:beforeIndex});save();render();
 toast(byId.get(id).kod+' satırı '+(after?'aşağı':'yukarı')+' taşındı.');
 return true;
}
function moveRowStep(id,direction){
 const shown=visibleRows(),index=shown.findIndex(p=>p.id===id);
 const next=shown[index+direction];
 if(index<0||!next)return;
 repositionRow(id,next.id,direction>0);
}
function sumsValid(rows){if(!rows||typeof rows!=='object')return false;for(const p of products){const m=rows[p.id];if(!Array.isArray(m)||m.length!==12||m.some((q,i)=>!Number.isSafeInteger(q)||q<0||(q>0&&FAMILIES[i]!==p.family))||m.reduce((a,b)=>a+b,0)!==p.annual)return false}return true}
function snapshot(){
 for(const p of products)ensureGroup(groupKey(p));
 return {format:SNAPSHOT_FORMAT,version:SNAPSHOT_VERSION,savedAt:new Date().toISOString(),
  identity:products.map(p=>({id:p.id,kod:p.kod,model:p.model,annual:p.annual,family:p.family})),
  monthly:cloneRows(),order:rowOrder.slice(),groupKeys:groupKeys.slice(),history:history.slice(-100)};
}
function note(message,kind='ok'){
 const n=$('saveNotice');if(n){n.textContent=message;n.className='save-notice'+(kind==='ok'?'':' '+kind)}
}
function updateCheckpointButton(){
 try{hasCheckpoint=!!localStorage.getItem(CHECKPOINT_KEY)}catch(e){hasCheckpoint=false}
 $('restoreCheckpoint').disabled=!hasCheckpoint;
}
function save(makeCheckpoint=false){
 if(!storageEnabled){note('Tarayıcı kaydı kullanılamıyor. Lütfen “Plan yedeği (.json)” dosyasını indirin.','error');return false}
 try{
  const data=JSON.stringify(snapshot());
  localStorage.setItem(STORAGE_KEY,data);
  if(localStorage.getItem(STORAGE_KEY)!==data)throw Error('Kayıt doğrulanamadı.');
  if(makeCheckpoint)localStorage.setItem(CHECKPOINT_KEY,data);
  const time=new Date().toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit'});
  note((makeCheckpoint?'Plan kaydedildi':'Otomatik kaydedildi')+' · '+time+' · Aynı tarayıcıda tekrar açıldığında geri gelir.');
  updateCheckpointButton();
  return true;
 }catch(e){
  storageEnabled=false;note('Kaydetme başarısız: '+e.message+'. Plan yedeği indirip saklayın.','error');return false;
 }
}
function validHistory(h){
 return Array.isArray(h)?h.filter(x=>x&&((x.kind==='full-order'&&validOrder(x.order))||(byId.has(x.id)&&((x.kind==='row'&&Number.isInteger(x.fromIndex)&&x.fromIndex>=0&&x.fromIndex<products.length)||((!x.kind||x.kind==='qty')&&Number.isInteger(x.qty)&&x.qty>0&&Number.isInteger(x.from)&&Number.isInteger(x.to)))))).slice(-100):[];
}
function mergedOrder(saved){
 if(!Array.isArray(saved))return initialOrder.slice();
 const current=saved.filter(id=>byId.has(id));
 const unique=[...new Set(current)];
 return unique.concat(initialOrder.filter(id=>!unique.includes(id)));
}
function applySnapshot(obj,allowPartial=false){
 if(!obj||!obj.monthly||typeof obj.monthly!=='object'||Array.isArray(obj.monthly))throw Error('Yedek dosyasında aylık üretim verisi bulunamadı.');
 const applied=[],skipped=[];
 for(const p of products){
  const m=obj.monthly[p.id];
  const ok=Array.isArray(m)&&m.length===12&&m.every((q,i)=>Number.isSafeInteger(q)&&q>=0&&(q===0||FAMILIES[i]===p.family))&&m.reduce((a,b)=>a+b,0)===p.annual;
  (ok?applied:skipped).push(p.id);
 }
 const extra=Object.keys(obj.monthly).filter(id=>!byId.has(id));
 if(!allowPartial&&(skipped.length||extra.length))throw Error('Yedek, mevcut ürün listesiyle uyuşmuyor: '+skipped.length+' eksik/değişmiş ürün, '+extra.length+' artık bulunmayan ürün. Mevcut plan korunuyor.');
 if(!applied.length)throw Error('Geçerli ürün kaydı bulunamadı; plan değiştirilmedi.');
 products.forEach(p=>{if(applied.includes(p.id))p.monthly=obj.monthly[p.id].slice()});
 rowOrder=mergedOrder(obj.order);
 groupsFromBackup(obj.groupKeys);
 history=skipped.length||extra.length?[]:validHistory(obj.history);
 return {loaded:applied.length,skipped:skipped.length,extra:extra.length};
}
function restore(){
 let raw=null;
 try{
  raw=localStorage.getItem(STORAGE_KEY);
  const savedPoint=localStorage.getItem(CHECKPOINT_KEY);
  updateCheckpointButton();
  if(!raw&&!savedPoint){note('Başlangıç planı yüklendi. Değişiklikler otomatik kaydedilecek; önemli planlar için JSON yedeği alın.','warn');return}
  let obj,usedCheckpoint=false;
  try{obj=JSON.parse(raw||savedPoint);usedCheckpoint=!raw}
  catch(parseError){
   // Bozuk asıl kayıt silinmez; son sağlam elle kayıt noktası varsa kurtarılır.
   if(raw&&!localStorage.getItem(RECOVERY_KEY))localStorage.setItem(RECOVERY_KEY,raw);
   if(!savedPoint)throw parseError;
   obj=JSON.parse(savedPoint);usedCheckpoint=true;
  }
  const result=applySnapshot(obj,true);
  if(result.skipped||result.extra){
   const archived=raw||savedPoint;
   if(!localStorage.getItem(RECOVERY_KEY))localStorage.setItem(RECOVERY_KEY,archived);
   restorationWarning=result.loaded+' ürün geri yüklendi; '+result.skipped+' eksik/değişmiş, '+result.extra+' eski ürün eşleşmedi. Eski kayıt ayrı saklandı; JSON yedeğini koruyun.';
   note(restorationWarning,'warn');
  }else if(usedCheckpoint)note('Önceki otomatik kayıt okunamadı; son elle kaydedilen sağlam plan açıldı.','warn');
  else note('Önceki kayıtlı plan açıldı: üretim adetleri ve ürün sıralamanız korundu.');
 }catch(e){
  restorationWarning='Kayıt okunamadı ('+e.message+'). Eski kayıt silinmedi. “Son kayıtlı plan” veya JSON yedeğini kullanın.';
  note(restorationWarning,'error');
 }
}
function manualSave(){
 if(save(true))toast('Plan ve ürün sıralaması kaydedildi. Güvenlik için JSON yedeği de indirebilirsiniz.');
}
function downloadSnapshot(){
 const name='2027_Uretim_Plani_Yedek_'+new Date().toISOString().slice(0,10)+'.json';
 const json=JSON.stringify(snapshot(),null,2);
 const url=URL.createObjectURL(new Blob([json],{type:'application/json;charset=utf-8'}));
 const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),2000);
 toast('JSON plan yedeği indirildi: '+name);
}
function restoreCheckpoint(){
 try{
  const raw=localStorage.getItem(CHECKPOINT_KEY);
  if(!raw)throw Error('Kayıtlı plan bulunamadı.');
  const obj=JSON.parse(raw);
  // Kayıtlı plan, ana verideki eksik veya yeni ürünlerle karıştırılmaz.
  applySnapshot(obj,false);
  if(save()) {render();toast('Son elle kaydedilen plan geri yüklendi.')}
 }catch(e){note('Kayıtlı plan açılamadı: '+e.message,'error')}
}
async function importSnapshot(file){
 if(!file)return;
 if(file.size>10*1024*1024){note('Yedek dosyası 10 MB sınırını aşıyor.','error');return}
 try{
  const obj=JSON.parse(await file.text());
  if(obj.format!==SNAPSHOT_FORMAT||obj.version!==SNAPSHOT_VERSION)throw Error('Bu dosya uygulamanın desteklediği 2027 JSON yedeği değil.');
  if(!obj.identity||!Array.isArray(obj.identity))throw Error('Yedekte ürün kimlik bilgileri yok.');
  // Doğrulama, onaydan önce yapılır; uyumsuz bir dosya mevcut planı değiştiremez.
  for(const p of products){
   const id=obj.identity.find(x=>x.id===p.id);
   if(!id||id.annual!==p.annual||id.family!==p.family)throw Error('Ürün kimliği, yıllık miktar veya sınıf uyuşmuyor: '+p.kod);
  }
  for(const p of products){
   const m=obj.monthly?.[p.id];
   if(!Array.isArray(m)||m.length!==12||m.some((q,i)=>!Number.isSafeInteger(q)||q<0||(q>0&&FAMILIES[i]!==p.family))||m.reduce((a,b)=>a+b,0)!==p.annual)throw Error('Ürünün yıllık/aylık planı geçersiz: '+p.kod);
  }
  if(Object.keys(obj.monthly).length!==products.length)throw Error('Yedekte mevcut ürün sayısından farklı sayıda kayıt bulunuyor.');
  if(!confirm(file.name+' içindeki kayıtlı plan, mevcut aylık üretim ve satır sırasının yerine yüklensin mi?'))return;
  applySnapshot(obj,false);
  if(!save(true))return;
  render();toast('Yedekten üretim planı ve satır sırası geri yüklendi.');
 }catch(e){note('Yedek yüklenemedi: '+e.message+' Mevcut plan korunuyor.','error')}
}
function sortRows(){return visibleRows()}
function paintStats(){
 const max=Math.max(...MONTHS.map((_,i)=>monthlyTotal(i)));
 const figures=[['Yıllık üretim',fmt(totalAnnual()),'Şönt + Harmonik'],['Ürün kaydı',fmt(products.length),'Kaynak 135 · 2 üretimsiz'],['En yüksek ay',fmt(max),'Yıllık ürün adedi karşılaştırması'],['Yapılan aktarım',fmt(history.length),'Bu tarayıcıdaki plan değişiklikleri']];
 $('metrics').innerHTML=figures.map(x=>'<div class="metric"><label>'+x[0]+'</label><strong>'+x[1]+'</strong><small>'+x[2]+'</small></div>').join('');
 $('changeCount').textContent=fmt(history.length);$('undo').disabled=!history.length;
}
function render(){
 paintStats();
 updateUpperControls();
 renderGroupLegend();
 $('matrixHead').innerHTML='<tr><th class="col-order">Sıra</th><th class="col-group">Grup</th><th class="col-code">Ürün kodu</th><th class="col-model">Ürün adı / Model</th><th class="col-upper">Üst grup</th><th class="col-coil">Bobin*</th>'+
  MONTHS.map((m,i)=>'<th class="col-month"><button type="button" class="month-open'+(window.ProductionMonthDetails&&window.ProductionMonthDetails.month()===i?' is-selected':'')+'" data-month="'+i+'" title="'+m+' ayının tüm teknik özelliklerini ve datasheet bağlantılarını aç">'+m+'<span class="month-type '+(FAMILIES[i]==='Şönt'?'s':'h')+'">'+FAMILIES[i]+'</span><span class="month-sum">'+fmt(monthlyTotal(i))+'</span><span class="month-action">Detay ▾</span></button></th>').join('')+'<th class="col-total">Yıllık</th></tr>';
 $('matrixFoot').innerHTML='<tr><th></th><th></th><th>TOPLAM</th><th></th><th></th><th></th>'+MONTHS.map((_,i)=>'<th>'+fmt(monthlyTotal(i))+'</th>').join('')+'<th>'+fmt(totalAnnual())+'</th></tr>';
 let html='',shown=sortRows();
 for(let i=0;i<shown.length;i++){
  const p=shown[i],g=groupInfo(p),prev=shown[i-1],groupStart=!prev||upperGroup(prev)!==upperGroup(p),link='urun.html?id='+encodeURIComponent(p.id);
  const label=esc(p.kod)+(p.coil===null?'':' ('+p.coil+'B*)');
  const up=i===0?' disabled':'',down=i===shown.length-1?' disabled':'';
  html+='<tr class="product-row'+(groupStart?' group-transition':'')+'" style="'+groupStyle(g)+'" data-id="'+esc(p.id)+'"><td class="col-order"><div class="order-controls">'+
   '<button type="button" class="order-arrow move-up" title="Satırı yukarı taşı" aria-label="'+esc(p.kod)+' satırını yukarı taşı"'+up+'>↑</button>'+
   '<button type="button" class="order-arrow move-down" title="Satırı aşağı taşı" aria-label="'+esc(p.kod)+' satırını aşağı taşı"'+down+'>↓</button>'+
   '<span class="row-handle" draggable="true" role="img" aria-label="Satırı sürükleyerek taşı" title="Satırı tutup başka satırın üzerine sürükle">⠿</span>'+
   '</div></td><td class="col-group"><span class="group-chip" title="'+esc(p.family+' · '+monthsName(p))+'">G'+g.id+'</span></td><td class="col-code"><a class="product-link" href="'+link+'" title="Ürün teknik föyünü aç" target="_blank" rel="noopener">'+label+'</a></td>'+
   '<td class="col-model" title="'+esc(p.model)+'"><a class="model-link" href="'+link+'" target="_blank" rel="noopener">'+esc(p.model)+'</a></td>'+
   '<td class="col-upper" title="'+esc(upperGroup(p))+'"><span class="upper-label">'+esc(upperGroup(p))+'</span></td>'+
   '<td class="col-coil" title="'+(p.coil===null?'Fiziksel bobin sayısı bilinmiyor':'Yalnızca üretici tip çizimi ön verisi; kesin üretim reçetesi değil')+'">'+(p.coil===null?'<span class="uncertain">?</span>':p.coil+'B*')+'</td>';
  for(let m=0;m<12;m++){const v=p.monthly[m];html+='<td class="month-cell" data-id="'+esc(p.id)+'" data-month="'+m+'">'+
   (v?'<button type="button" draggable="true" class="qty group-qty" aria-label="'+esc(p.kod)+' '+MONTHS[m]+' '+fmt(v)+' adet; başka aya taşı" title="Aktarmak için tıklayın veya aynı ürünün başka ayına sürükleyin">'+fmt(v)+'</button>':'<span class="empty">·</span>')+'</td>'}
  html+='<td class="col-total">'+fmt(p.annual)+'</td></tr>';
 }
 $('matrixBody').innerHTML=html;
 if(window.ProductionMonthDetails)window.ProductionMonthDetails.refresh(products,rowOrder);
}
function toast(message){const t=$('toast');t.textContent=message;t.classList.add('show');clearTimeout(toastHandle);toastHandle=setTimeout(()=>t.classList.remove('show'),3300)}
function setSourceOptions(p){$('from').innerHTML=MONTHS.map((m,i)=>'<option value="'+i+'" '+(i===active.from?'selected':'')+' '+(!p.monthly[i]?'disabled':'')+'>'+m+' ('+fmt(p.monthly[i])+')</option>').join('')}
function setTargetOptions(){ $('to').innerHTML=MONTHS.map((m,i)=>'<option value="'+i+'" '+(i===active.to?'selected':'')+'>'+m+' · '+FAMILIES[i]+'</option>').join('') }
function openDialog(id,month,to){
 const p=byId.get(id);if(!p||!p.monthly[month])return;
 active={id,from:month,to:Number.isInteger(to)?to:FAMILIES.findIndex((f,i)=>i!==month&&f===p.family),qty:p.monthly[month]};
 $('selectedCode').textContent=p.kod+(p.coil===null?'':' ('+p.coil+'B*)');$('selectedCode').href='urun.html?id='+encodeURIComponent(id);
 $('selectedModel').textContent=p.model;$('selectedFamily').textContent=p.family;
 setSourceOptions(p);setTargetOptions();$('quantity').value=active.qty;
 $('backdrop').classList.add('open');preview();$('quantity').focus();$('quantity').select();
}
function closeDialog(){$('backdrop').classList.remove('open');active=null}
function validate(){
 if(!active)return {ok:false,msg:'Ürün seçilmedi.'};
 const p=byId.get(active.id),from=active.from,to=active.to,q=active.qty;
 if(from===to)return {ok:false,msg:'Kaynak ay ile hedef ay farklı olmalı.'};
 if(FAMILIES[to]!==p.family)return {ok:false,msg:'Setup kısıtı: '+MONTHS[to]+' yalnız '+FAMILIES[to]+' üretimi için ayrılmış. '+p.family+' aktarılamaz.'};
 if(!Number.isSafeInteger(q)||q<1||q>p.monthly[from])return {ok:false,msg:'1 ile '+fmt(p.monthly[from])+' arasında tam sayı girin.'};
 const oldParts=p.monthly.filter(v=>v>0).length;
 const newParts=p.monthly.map((v,i)=>i===from?v-q:i===to?v+q:v).filter(v=>v>0).length;
 return {ok:true,msg:fmt(q)+' adet '+MONTHS[from]+' → '+MONTHS[to]+' taşınacak. Yıllık '+fmt(p.annual)+' adet aynı kalır.'+(oldParts!==newParts?' Üretim partisi '+oldParts+' → '+newParts+' olacak.':'')};
}
function preview(){
 if(!active)return;const p=byId.get(active.id),v=validate();
 $('notice').className='notice'+(v.ok?'':' error');$('notice').textContent=v.msg;
 $('confirm').disabled=!v.ok;
 $('beforeAfter').innerHTML='<div><span>'+MONTHS[active.from]+' · Sonra</span><b>'+fmt(p.monthly[active.from]-(Number.isFinite(active.qty)?active.qty:0))+'</b></div><div><span>'+MONTHS[active.to]+' · Sonra</span><b>'+fmt(p.monthly[active.to]+(Number.isFinite(active.qty)?active.qty:0))+'</b></div>';
}
function applyMove(){
 const valid=validate();if(!valid.ok){preview();return}
 const p=byId.get(active.id),h={kind:'qty',id:active.id,from:active.from,to:active.to,qty:active.qty};
 p.monthly[h.from]-=h.qty;p.monthly[h.to]+=h.qty;history.push(h);save();closeDialog();render();
 toast(p.kod+': '+fmt(h.qty)+' adet '+MONTHS[h.from]+' → '+MONTHS[h.to]+' aktarıldı.');
}
function undo(){
 const h=history.pop();if(!h)return;const p=byId.get(h.id);
 if(h.kind==='full-order'){
  rowOrder=h.order.slice();save();render();toast('Önceki ürün sıralaması geri yüklendi.');return;
 }
 if(h.kind==='row'){
  const at=rowOrder.indexOf(h.id);
  if(at<0){history.push(h);toast('Satır sıralaması geri alınamadı.');return}
  rowOrder.splice(at,1);rowOrder.splice(h.fromIndex,0,h.id);
  save();render();toast('Son satır sıralaması geri alındı.');return;
 }
 if(!p||p.monthly[h.to]<h.qty){history.push(h);toast('Son değişiklik geri alınamadı.');return}
 p.monthly[h.to]-=h.qty;p.monthly[h.from]+=h.qty;save();render();toast('Son üretim aktarımı geri alındı.');
}
function reset(){
 if(!confirm('Bu tarayıcıdaki üretim değişiklikleri başlangıç planına döndürülecek. Son elle kaydedilen plan kurtarma için korunacak. Devam edilsin mi?'))return;
 // Önceden elle kaydedilmiş bir kayıt yoksa, sıfırlama öncesi otomatik kurtarma noktası oluştur.
 if(!hasCheckpoint&&!save(true)){toast('Kurtarma kaydı oluşturulamadığı için sıfırlama iptal edildi. Önce JSON yedeğini indirin.');return}
 products.forEach(p=>p.monthly=p.initial.slice());rowOrder=initialOrder.slice();history=[];save();render();toast('Başlangıç planına dönüldü; son kaydedilen plana geri dönebilirsiniz.');
}
function exportCSV(){
 const rows=[['Sıra','Ürün kimliği','Stok kodu','Model','Ürün ailesi','Bobin ön değeri','Bobin doğrulama','Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık','Yıllık adet']];
 for(const [i,id] of rowOrder.entries()){const p=byId.get(id);rows.push([i+1,p.id,p.kod,p.model,p.family,p.coil===null?'':p.coil,p.coil===null?'Doğrulanmadı':'Tip çizimi ön değeri; reçete onayı yok',...p.monthly,p.annual])}
 const csv='\ufeff'+rows.map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(';')).join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='2027_Uretim_Matrisi_Duzenlenmis.csv';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);toast('Güncel plan CSV dosyası olarak indirildi.');
}
function clearDragStyles(){document.querySelectorAll('.row-drop-before,.row-drop-after,.row-dragging,.drop-ok,.drop-warn').forEach(x=>x.classList.remove('row-drop-before','row-drop-after','row-dragging','drop-ok','drop-warn'))}
function bindEvents(){
 $('matrixHead').addEventListener('click',e=>{const btn=e.target.closest('.month-open');if(!btn)return;if(!window.ProductionMonthDetails){toast('Teknik detay modülü yüklenemedi. plan2027-detail.js dosyasını kontrol edin.');return}window.ProductionMonthDetails.open(Number(btn.dataset.month),products,rowOrder)});
 $('search').addEventListener('input',e=>{search=e.target.value;render()});
 $('family').addEventListener('change',e=>{familyFilter=e.target.value;render()});
 $('clearFilter').addEventListener('click',()=>{search='';familyFilter='all';$('search').value='';$('family').value='all';render()});
 $('sortUpper').addEventListener('click',sortUpperGroups);
 $('applyUpper').addEventListener('click',applyUpperOptimization);
 $('returnBeforeUpper').addEventListener('click',returnBeforeUpper);
 $('groupLegend').addEventListener('click',e=>{if(e.target.closest('.group-expand')){allGroupsVisible=!allGroupsVisible;renderGroupLegend()}});
 $('undo').addEventListener('click',undo);$('reset').addEventListener('click',reset);$('export').addEventListener('click',exportCSV);
 $('savePlan').addEventListener('click',manualSave);
 $('downloadBackup').addEventListener('click',downloadSnapshot);
 $('loadBackup').addEventListener('click',()=>$('backupFile').click());
 $('backupFile').addEventListener('change',async e=>{const file=e.target.files?.[0];await importSnapshot(file);e.target.value=''});
 $('restoreCheckpoint').addEventListener('click',restoreCheckpoint);
 $('matrixBody').addEventListener('click',e=>{
  const arrow=e.target.closest('.order-arrow');
  if(arrow){const row=arrow.closest('tr.product-row');moveRowStep(row.dataset.id,arrow.classList.contains('move-up')?-1:1);return}
  const btn=e.target.closest('.qty');if(!btn)return;const cell=btn.closest('.month-cell');openDialog(cell.dataset.id,+cell.dataset.month);
 });
 $('matrixBody').addEventListener('dragstart',e=>{
  const handle=e.target.closest('.row-handle');
  if(handle){const row=handle.closest('tr.product-row');rowDrag={id:row.dataset.id};drag=null;row.classList.add('row-dragging');if(e.dataTransfer){e.dataTransfer.setData('text/plain',rowDrag.id);e.dataTransfer.effectAllowed='move'}return}
  const btn=e.target.closest('.qty');if(!btn)return;const cell=btn.closest('.month-cell');drag={id:cell.dataset.id,month:+cell.dataset.month};rowDrag=null;if(e.dataTransfer){e.dataTransfer.setData('text/plain',drag.id);e.dataTransfer.effectAllowed='move'}
 });
 $('matrixBody').addEventListener('dragover',e=>{
  if(rowDrag){const row=e.target.closest('tr.product-row');if(!row)return;e.preventDefault();const rect=row.getBoundingClientRect();const below=e.clientY>rect.top+rect.height/2;document.querySelectorAll('.row-drop-before,.row-drop-after').forEach(x=>x.classList.remove('row-drop-before','row-drop-after'));if(row.dataset.id!==rowDrag.id)row.classList.add(below?'row-drop-after':'row-drop-before');return}
  const cell=e.target.closest('.month-cell');if(!drag||!cell)return;e.preventDefault();cell.classList.add(cell.dataset.id===drag.id&&FAMILIES[+cell.dataset.month]===byId.get(drag.id).family?'drop-ok':'drop-warn')
 });
 $('matrixBody').addEventListener('dragleave',e=>{const cell=e.target.closest('.month-cell');if(cell)cell.classList.remove('drop-ok','drop-warn')});
 $('matrixBody').addEventListener('drop',e=>{
  if(rowDrag){const row=e.target.closest('tr.product-row');if(!row)return;e.preventDefault();const id=rowDrag.id,target=row.dataset.id;const rect=row.getBoundingClientRect(),after=e.clientY>rect.top+rect.height/2;rowDrag=null;clearDragStyles();repositionRow(id,target,after);return}
  const cell=e.target.closest('.month-cell');if(!drag||!cell)return;e.preventDefault();cell.classList.remove('drop-ok','drop-warn');const d=drag;drag=null;if(d.id!==cell.dataset.id){toast('Adet taşımak için aynı ürünün farklı ayını seçin.');return}openDialog(d.id,d.month,+cell.dataset.month)
 });
 $('matrixBody').addEventListener('dragend',()=>{drag=null;rowDrag=null;clearDragStyles()});
 $('close').addEventListener('click',closeDialog);$('cancel').addEventListener('click',closeDialog);
 $('backdrop').addEventListener('click',e=>{if(e.target===$('backdrop'))closeDialog()});
 document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDialog()});
 $('from').addEventListener('change',e=>{if(!active)return;active.from=+e.target.value;active.qty=Math.min(active.qty,byId.get(active.id).monthly[active.from]);$('quantity').value=active.qty;preview()});
 $('to').addEventListener('change',e=>{if(!active)return;active.to=+e.target.value;preview()});
 $('quantity').addEventListener('input',e=>{if(!active)return;active.qty=Number(e.target.value);preview()});
 $('allQty').addEventListener('click',()=>{if(!active)return;active.qty=byId.get(active.id).monthly[active.from];$('quantity').value=active.qty;preview()});
 $('hundred').addEventListener('click',()=>{if(!active)return;active.qty=Math.min(100,byId.get(active.id).monthly[active.from]);$('quantity').value=active.qty;preview()});
 $('confirm').addEventListener('click',applyMove);
}
async function boot(){
 try{
  if(!window.PRODUCTS_GZIP_B64||!window.PRODUCTION_PLAN_2027_GZIP_B64||!window.UPPER_GROUP_OPTIMIZED_2027_GZIP_B64)throw Error('Ürün, mevcut plan veya üst grup optimizasyon dosyası eksik.');
  const [records,plan,upperPlan]=await Promise.all([unzipBase64(window.PRODUCTS_GZIP_B64),unzipBase64(window.PRODUCTION_PLAN_2027_GZIP_B64),unzipBase64(window.UPPER_GROUP_OPTIMIZED_2027_GZIP_B64)]);
  optimizedPlan=new Map(upperPlan);
  const data=new Map(records.map(p=>[p.id,p]));
  products=plan.map(([id,monthly,coil])=>{
   const p=data.get(id);if(!p||p.adet<=0)throw Error('Eksik veya uyumsuz ürün kimliği: '+id);
   const proposed=optimizedPlan.get(id);
   if(!Array.isArray(proposed)||proposed.length!==12||proposed.some(x=>!Number.isSafeInteger(x)||x<0)||proposed.reduce((a,b)=>a+b,0)!==p.adet)throw Error('Üst grup optimizasyonunun ürün verisi uyumsuz: '+id);
   return {...p,annual:p.adet,monthly:proposed.slice(),initial:proposed.slice(),previousDefault:monthly.slice(),family:p.grup,coil};
  });
  byId=new Map(products.map(p=>[p.id,p]));
  initialOrder=products.slice().sort(defaultCompare).map(p=>p.id);rowOrder=initialOrder.slice();
  initializeGroups();
  if(products.length!==133||byId.size!==133||optimizedPlan.size!==133||!sumsValid(cloneRows())||totalAnnual()!==45088)throw Error('Kaynak veya optimize edilen plan tutarlılık kontrolünden geçmedi.');
  restore();bindEvents();render();$('status').textContent='133 ürün · 45.088 adet';
 }catch(e){$('status').textContent='Veri yükleme hatası';$('matrixBody').innerHTML='<tr><td colspan="19" style="text-align:left;padding:18px;color:#a33">Plan açılamadı: '+esc(e.message)+'</td></tr>';console.error(e)}
}
boot();
})();