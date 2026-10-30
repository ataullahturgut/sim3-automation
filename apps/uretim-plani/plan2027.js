(()=>{'use strict';
const MONTHS=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
// Setup kuralı: iki şönt ayı, ardından bir harmonik ayı, yıl boyunca tekrar.
const FAMILIES=['Şönt','Şönt','Harmonik','Şönt','Şönt','Harmonik','Şönt','Şönt','Harmonik','Şönt','Şönt','Harmonik'];
const STORAGE_KEY='simulation3.production2027.matrix.v1';
const CHECKPOINT_KEY=STORAGE_KEY+'.checkpoint';
const RECOVERY_KEY=STORAGE_KEY+'.unmatched-backup';
const SNAPSHOT_FORMAT='simulation3-uretim-plani-2027';
const SNAPSHOT_VERSION=2;
const $=id=>document.getElementById(id);
const fmt=x=>Number(x||0).toLocaleString('tr-TR');
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let products=[],byId=new Map(),history=[],rowOrder=[],initialOrder=[],search='',familyFilter='all',active=null,drag=null,rowDrag=null,toastHandle=null,storageEnabled=true,restorationWarning='',hasCheckpoint=false;
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
function cloneRows(){return Object.fromEntries(products.map(p=>[p.id,p.monthly.slice()]))}
function validOrder(order){return Array.isArray(order)&&order.length===products.length&&new Set(order).size===products.length&&order.every(id=>byId.has(id))}
function defaultCompare(a,b){return firstMonth(a)-firstMonth(b)||a.family.localeCompare(b.family,'tr')||pattern(a).localeCompare(pattern(b))||b.annual-a.annual||a.kod.localeCompare(b.kod,'tr')}
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
 return {format:SNAPSHOT_FORMAT,version:SNAPSHOT_VERSION,savedAt:new Date().toISOString(),
  identity:products.map(p=>({id:p.id,kod:p.kod,model:p.model,annual:p.annual,family:p.family})),
  monthly:cloneRows(),order:rowOrder.slice(),history:history.slice(-100)};
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
 return Array.isArray(h)?h.filter(x=>x&&byId.has(x.id)&&((x.kind==='row'&&Number.isInteger(x.fromIndex)&&x.fromIndex>=0&&x.fromIndex<products.length)||((!x.kind||x.kind==='qty')&&Number.isInteger(x.qty)&&x.qty>0&&Number.isInteger(x.from)&&Number.isInteger(x.to)))).slice(-100):[];
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
 history=skipped.length||extra.length?[]:validHistory(obj.history);
 return {loaded:applied.length,skipped:skipped.length,extra:extra.length};
}
function restore(){
 let raw=null;
 try{
  raw=localStorage.getItem(STORAGE_KEY);
  if(!raw)raw=localStorage.getItem(CHECKPOINT_KEY);
  updateCheckpointButton();
  if(!raw){note('Başlangıç planı yüklendi. Değişiklikler otomatik kaydedilecek; önemli planlar için JSON yedeği alın.','warn');return}
  const obj=JSON.parse(raw);
  const previewMissing=products.some(p=>!obj.monthly||!Object.hasOwn(obj.monthly,p.id));
  const result=applySnapshot(obj,true);
  if(result.skipped||result.extra||previewMissing){
   // Otomatik dönüşüm yapmadan önce, önceki ham verinin ayrı bir kopyasını koru.
   if(!localStorage.getItem(RECOVERY_KEY))localStorage.setItem(RECOVERY_KEY,raw);
   restorationWarning=result.loaded+' ürünün kayıtları geri yüklendi; '+result.skipped+' değişmiş/eksik, '+result.extra+' eski ürün kaydı eşleşmedi. Eski veri ayrıca korundu; JSON yedeğinizi saklayın.';
   note(restorationWarning,'warn');
  }else note('Önceki kayıtlı plan açıldı: üretim adetleri ve ürün sıralamanız korundu.');
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
 $('matrixHead').innerHTML='<tr><th class="col-order">Sıra</th><th class="col-code">Ürün kodu</th><th class="col-model">Ürün adı / Model</th><th class="col-coil">Bobin*</th>'+
  MONTHS.map((m,i)=>'<th class="col-month">'+m+'<span class="month-type '+(FAMILIES[i]==='Şönt'?'s':'h')+'">'+FAMILIES[i]+'</span><span class="month-sum">'+fmt(monthlyTotal(i))+'</span></th>').join('')+'<th class="col-total">Yıllık</th></tr>';
 $('matrixFoot').innerHTML='<tr><th></th><th>TOPLAM</th><th></th><th></th>'+MONTHS.map((_,i)=>'<th>'+fmt(monthlyTotal(i))+'</th>').join('')+'<th>'+fmt(totalAnnual())+'</th></tr>';
 let html='',shown=sortRows();
 for(let i=0;i<shown.length;i++){
  const p=shown[i],link='urun.html?id='+encodeURIComponent(p.id);
  const label=esc(p.kod)+(p.coil===null?'':' ('+p.coil+'B*)');
  const up=i===0?' disabled':'',down=i===shown.length-1?' disabled':'';
  html+='<tr class="product-row" data-id="'+esc(p.id)+'"><td class="col-order"><div class="order-controls">'+
   '<button type="button" class="order-arrow move-up" title="Satırı yukarı taşı" aria-label="'+esc(p.kod)+' satırını yukarı taşı"'+up+'>↑</button>'+
   '<button type="button" class="order-arrow move-down" title="Satırı aşağı taşı" aria-label="'+esc(p.kod)+' satırını aşağı taşı"'+down+'>↓</button>'+
   '<span class="row-handle" draggable="true" role="img" aria-label="Satırı sürükleyerek taşı" title="Satırı tutup başka satırın üzerine sürükle">⠿</span>'+
   '</div></td><td class="col-code"><a class="product-link" href="'+link+'" title="Ürün teknik föyünü aç" target="_blank" rel="noopener">'+label+'</a></td>'+
   '<td class="col-model" title="'+esc(p.model)+'"><a class="model-link" href="'+link+'" target="_blank" rel="noopener">'+esc(p.model)+'</a></td>'+
   '<td class="col-coil" title="'+(p.coil===null?'Fiziksel bobin sayısı bilinmiyor':'Yalnızca üretici tip çizimi ön verisi; kesin üretim reçetesi değil')+'">'+(p.coil===null?'<span class="uncertain">?</span>':p.coil+'B*')+'</td>';
  for(let m=0;m<12;m++){const v=p.monthly[m];html+='<td class="month-cell" data-id="'+esc(p.id)+'" data-month="'+m+'">'+
   (v?'<button type="button" draggable="true" class="qty '+(p.family==='Harmonik'?'h':'')+'" aria-label="'+esc(p.kod)+' '+MONTHS[m]+' '+fmt(v)+' adet; başka aya taşı" title="Aktarmak için tıklayın veya aynı ürünün başka ayına sürükleyin">'+fmt(v)+'</button>':'<span class="empty">·</span>')+'</td>'}
  html+='<td class="col-total">'+fmt(p.annual)+'</td></tr>';
 }
 $('matrixBody').innerHTML=html;
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
 if(!confirm('Bu tarayıcıda yaptığınız bütün üretim değişiklikleri silinsin ve başlangıç 2027 planı yüklensin mi?'))return;
 products.forEach(p=>p.monthly=p.initial.slice());rowOrder=initialOrder.slice();history=[];save();render();toast('Üretim miktarları ve satır sırası başlangıç planına döndü.');
}
function exportCSV(){
 const rows=[['Sıra','Ürün kimliği','Stok kodu','Model','Ürün ailesi','Bobin ön değeri','Bobin doğrulama','Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık','Yıllık adet']];
 for(const [i,id] of rowOrder.entries()){const p=byId.get(id);rows.push([i+1,p.id,p.kod,p.model,p.family,p.coil===null?'':p.coil,p.coil===null?'Doğrulanmadı':'Tip çizimi ön değeri; reçete onayı yok',...p.monthly,p.annual])}
 const csv='\ufeff'+rows.map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(';')).join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='2027_Uretim_Matrisi_Duzenlenmis.csv';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);toast('Güncel plan CSV dosyası olarak indirildi.');
}
function clearDragStyles(){document.querySelectorAll('.row-drop-before,.row-drop-after,.row-dragging,.drop-ok,.drop-warn').forEach(x=>x.classList.remove('row-drop-before','row-drop-after','row-dragging','drop-ok','drop-warn'))}
function bindEvents(){
 $('search').addEventListener('input',e=>{search=e.target.value;render()});
 $('family').addEventListener('change',e=>{familyFilter=e.target.value;render()});
 $('clearFilter').addEventListener('click',()=>{search='';familyFilter='all';$('search').value='';$('family').value='all';render()});
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
  if(!window.PRODUCTS_GZIP_B64||!window.PRODUCTION_PLAN_2027_GZIP_B64)throw Error('Ürün veya 2027 plan dosyası bulunamadı.');
  const [records,plan]=await Promise.all([unzipBase64(window.PRODUCTS_GZIP_B64),unzipBase64(window.PRODUCTION_PLAN_2027_GZIP_B64)]);
  const data=new Map(records.map(p=>[p.id,p]));
  products=plan.map(([id,monthly,coil])=>{
   const p=data.get(id);if(!p||p.adet<=0)throw Error('Eksik veya uyumsuz ürün kimliği: '+id);
   return {...p,annual:p.adet,monthly:monthly.slice(),initial:monthly.slice(),family:p.grup,coil};
  });
  byId=new Map(products.map(p=>[p.id,p]));
  initialOrder=products.slice().sort(defaultCompare).map(p=>p.id);rowOrder=initialOrder.slice();
  if(products.length!==133||byId.size!==133||!sumsValid(cloneRows())||totalAnnual()!==45088)throw Error('Kaynak plan tutarlılık kontrolünden geçmedi.');
  restore();bindEvents();render();$('status').textContent='133 ürün · 45.088 adet';
 }catch(e){$('status').textContent='Veri yükleme hatası';$('matrixBody').innerHTML='<tr><td colspan="17" style="text-align:left;padding:18px;color:#a33">Plan açılamadı: '+esc(e.message)+'</td></tr>';console.error(e)}
}
boot();
})();