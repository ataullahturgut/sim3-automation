/* Şönt makine yatırımı için eldeki 25 ürünün fiziksel inceleme öncelikleri.
   Makine/model/çevrim kapasitesi onayı değildir; Harmonik ve üretim planı değişmez. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
const fmt=x=>Number(x||0).toLocaleString('tr-TR');
const pct=(n,d)=>d?(100*n/d).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%':'—';
const esc=x=>String(x==null?'':x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const DATA=[["GA5001","A","SVC-R alt güç sınırı; küçük gövde, bobin kalıbı ve sarım süresini ölç","Sarım kalıbı · bobin eni · çevrim"],["GA5002","A","13.462 adet/yıl ile ana üretim yükü; tekrar eden işlemin gerçek çevrim süresini ölç","Sarım süresi · setup · proses parti adedi"],["GA5003","A","6.502 adet/yıl ve GA5002'den farklı güç/gövde; kapasite modelinde ayrı çevrim gerekir","Bobin ölçüsü · sarım süresi · kalıp"],["GA5004","B","SVC-R 5 ürün kodunun resmî liste karşılığı belirsiz; eldeki ürün kimliğini ve gerçek yapısını ölç","Kimlik/etiket · gövde · sarım"],["GA5006","B","SVC-R 10 ürün kodu resmî listede eşleşmiyor; eldeki ürünün gerçek teknik yapısını belirle","Kimlik/etiket · bobin · işlem"],["GA5101","C","Küçük SRM; ilk turda sökmeden GA5102 ile gerçek dış ölçü, uç ve yapı karşılaştırması","Dış ölçü · bağlantı · fark kontrolü"],["GA5102","A","SVC-R ile benzer güç düzeyine rağmen SRM gövdesi farklı; hat/kalıp ortaklığını sınırla","Sarım kalıbı · nüve · çevrim"],["GA5103","B","SRM ara güç ve 810 adet/yıl; GA5102'ye göre sarım çevrimi ve nüve farkını karşılaştır","Bobin eni · nüve · süre"],["GA5104","A","SRM pabuç bağlantı sınıfının ve orta gövdenin referansı","Bağlantı işlemi · sarım · montaj"],["GA5105","B","SRM 7,5 güç ve bağlantı/gövde varyasyonu; GA5104/GA5106 ile gerçek yapı farkını kontrol et","Pabuç · kalıp · bobin"],["GA5106","A","4.178 adet/yıl SRM 10 sınıfı; önemli sarım ve montaj iş yükü","Sarım süresi · nüve · bara montajı"],["GA5107","C","SRM 15; GA5108'e göre farklılık ve fiziksel yük sınırı sökmeden kontrol edilsin","Dış ölçü · bağlantı · yük"],["GA5108","A","Büyük SRM gövde sınıfı; ekipmanın büyük bobin ve taşıma sınırını araştır","Bobin ölçüsü · ağırlık · taşıma"],["GA5201","B","SRT düşük güç / yüksek endüktans sınıfı; tur sayısı ve küçük bobin geometrisi ölçülmeden varsayılmaz","Tur sayısı · bobin geometrisi · sarım"],["GA5202","C","SRT küçük güç; GA5204 ile gerçek montaj ve bobin farkı ön kontrol","Dış ölçü · bobin sayısı · montaj"],["GA5203","C","SRT küçük-orta güç; GA5204 öncesi boyut ve işlem farkı kontrolü","Gövde · nüve · montaj"],["GA5204","A","SRT küçük gövde grubunun 3-fazlı yapı/montaj ön referansı","Fiziksel bobin adedi · kalıp · montaj"],["GA5205","B","SRT orta güç grubu; eski uygulama bağlantı verisiyle resmî liste arasında uyuşmazlık var","Bağlantı · bobin · proses"],["GA5206","B","SRT 7,5; GA5205 ile bobin/bağlantı farkını karşılaştırarak işlem kapsamını belirle","Bağlantı · bobin ağırlığı · kalıp"],["GA5207","A","SRT orta güç sınıfı; üç fazlı montaj ve sepet yerleşimi kontrolü","Bobin adedi · montaj · yerleşim"],["GA5208","C","SRT 12,5; GA5209 ile boyut/taşıma ve bobin farkı kontrol","Dış ölçü · yük · fark testi"],["GA5209","A","SRT 15 orta-büyük gövde ve montaj sınıfı; parti yerleşimini karşılaştır","Bobin · yükleme · kurutma sepeti"],["GA5210","C","SRT 20; GA5211 ve GA5212 ile gerçek geometri farkı sökmeden ölçülsün","Ölçü · ağırlık · yükleme"],["GA5211","B","SRT 25; 50 kVAr GA5212 ile aynı makine kapasite sınırında kabul edilmez","Bobin boyutu · ağırlık · sepet"],["GA5212","A","SRT 50 yüksek gövde/ağırlık ucu; fırın, emprenye ve elleçleme sınırı","Gerçek proses yükü · kaldırma · fırın"]];
const INFO=new Map(DATA.map(([code,priority,reason,focus])=>[code,Object.freeze({priority,reason,focus})]));
if(INFO.size!==25||DATA.filter(x=>x[1]==='A').length!==11||DATA.filter(x=>x[1]==='B').length!==8||DATA.filter(x=>x[1]==='C').length!==6)throw Error('Şönt yatırım inceleme seti 11+8+6 geçersiz');
const LABELS={A:'1 · Öncelikli fiziksel inceleme',B:'2 · Hedefli yapı kontrolü',C:'3 · Sökmeden ön doğrulama'};
let all=[],priority='all',family='all',search='',ready=false;
function upper(p){const m=String(p.model||'');return m.startsWith('SVC-R')?'SVC-R':m.startsWith('SRM')?'SRM':m.startsWith('SRT')?'SRT':'Diğer';}
function filtered(){
 return all.filter(p=>{
  const d=INFO.get(p.kod);return !!d&&(priority==='all'||d.priority===priority)&&(family==='all'||upper(p)===family)&&(p.kod+' '+p.model+' '+d.reason+' '+d.focus).toLocaleLowerCase('tr-TR').includes(search.toLocaleLowerCase('tr-TR'));
 });
}
function render(){
 if(!ready)return;
 const total=all.reduce((sum,p)=>sum+p.annual,0);
 const grouped={A:{count:0,qty:0},B:{count:0,qty:0},C:{count:0,qty:0}};
 for(const p of all){const d=INFO.get(p.kod);grouped[d.priority].count++;grouped[d.priority].qty+=p.annual;}
 $('shuntMachineMetrics').innerHTML=
  '<div><small>Şönt portföyü</small><strong>'+all.length+' ürün</strong><span>'+fmt(total)+' adet/yıl</span></div>'+
  '<div><small>1 · Öncelikli inceleme</small><strong>'+grouped.A.count+' ürün</strong><span>'+fmt(grouped.A.qty)+' adet · '+pct(grouped.A.qty,total)+'</span></div>'+
  '<div><small>2 · Hedefli kontrol</small><strong>'+grouped.B.count+' ürün</strong><span>'+fmt(grouped.B.qty)+' adet · '+pct(grouped.B.qty,total)+'</span></div>'+
  '<div><small>3 · Ön doğrulama</small><strong>'+grouped.C.count+' ürün</strong><span>'+fmt(grouped.C.qty)+' adet · '+pct(grouped.C.qty,total)+'</span></div>';
 const seen=filtered().sort((a,b)=>INFO.get(a.kod).priority.localeCompare(INFO.get(b.kod).priority)||b.annual-a.annual||a.kod.localeCompare(b.kod,'tr'));
 $('shuntMachineCount').textContent=seen.length+' / '+all.length+' ürün gösteriliyor';
 const rows=[];
 for(const p of seen){
  const d=INFO.get(p.kod),state=d.priority;
  rows.push('<tr><td><a class="shunt-code" href="urun.html?id='+encodeURIComponent(p.id)+'" target="_blank" rel="noopener">'+esc(p.kod)+'</a></td>'+
  '<td>'+esc(p.model)+'</td><td>'+esc(upper(p))+'</td><td class="shunt-num">'+fmt(p.annual)+'</td>'+
  '<td class="shunt-num">'+pct(p.annual,total)+'</td>'+
  '<td><span class="shunt-level level-'+state+'">'+esc(LABELS[state])+'</span></td>'+
  '<td>'+esc(d.reason)+'</td><td>'+esc(d.focus)+'</td></tr>');
 }
 $('shuntMachineBody').innerHTML=rows.join('')||'<tr><td colspan="8" class="sample-empty">Bu ölçütlere uyan Şönt ürünü bulunamadı.</td></tr>';
}
function exportCsv(){
 const total=all.reduce((s,p)=>s+p.annual,0),head=['Kod','Model','Üst grup','Yıllık adet','Şönt pay (%)','Makine inceleme önceliği','Neden incelenecek','Ölçüm odağı','Durum'];
 const rows=[head,...filtered().sort((a,b)=>INFO.get(a.kod).priority.localeCompare(INFO.get(b.kod).priority)||b.annual-a.annual).map(p=>{
 const d=INFO.get(p.kod);return [p.kod,p.model,upper(p),p.annual,pct(p.annual,total),LABELS[d.priority],d.reason,d.focus,'Fiziksel ölçüm bekliyor'];
 })];
 const csv='\ufeff'+rows.map(r=>r.map(x=>'"'+String(x==null?'':x).replace(/"/g,'""')+'"').join(';')).join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 const a=document.createElement('a');a.href=url;a.download='sont-makine-yatirimi-urun-inceleme.csv';document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
}
function init(products){
 if(!Array.isArray(products))throw Error('Şönt makine inceleme için ürün listesi eksik');
 all=products.filter(p=>p.grup==='Şönt');
 if(all.length!==25||new Set(all.map(p=>p.kod)).size!==25||all.some(p=>!INFO.has(p.kod)||!Number.isFinite(p.annual))||all.reduce((t,p)=>t+p.annual,0)!==35772)throw Error('Şönt CAPEX inceleme 25 ürün / 35.772 adet doğrulaması sağlanamadı');
 if(all.filter(p=>INFO.get(p.kod).priority==='A').reduce((s,p)=>s+p.annual,0)!==32654)throw Error('Öncelikli 11 ürün yıllık adet kontrolü başarısız');
 $('shuntMachinePriority').addEventListener('change',e=>{priority=e.target.value;render()});
 $('shuntMachineGroup').addEventListener('change',e=>{family=e.target.value;render()});
 $('shuntMachineSearch').addEventListener('input',e=>{search=e.target.value||'';render()});
 $('shuntMachineClear').addEventListener('click',()=>{
  priority='all';family='all';search='';
  $('shuntMachinePriority').value='all';$('shuntMachineGroup').value='all';$('shuntMachineSearch').value='';
  render();
 });
 $('shuntMachineExport').addEventListener('click',exportCsv);
 ready=true;render();
}
window.ShuntMachineInvestment=Object.freeze({init,render,get:code=>INFO.get(code)||null,count:INFO.size});
})();