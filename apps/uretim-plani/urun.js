(()=>{'use strict';
const el=document.getElementById('sheet');
const esc=v=>String(v===null||v===undefined?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const printButton=document.getElementById('printSheet');
printButton.addEventListener('click',()=>window.print());
const valid=v=>v!==null&&v!==undefined&&v!==''&&v!=='UNRESOLVED';
const format=v=>!valid(v)?'Bilgi bulunmuyor':typeof v==='number'?v.toLocaleString('tr-TR',{maximumFractionDigits:6}):String(v);
const stat=(label,value)=>'<div class="sheet-stat"><small>'+esc(label)+'</small><strong>'+esc(format(value))+'</strong></div>';
const spec=(label,value)=>'<div class="sheet-spec"><dt>'+esc(label)+'</dt><dd>'+esc(format(value))+'</dd></div>';
const official='https://www.gruparge.com/fl/tr';
const ranges=[[5001,5003,17],[5101,5108,17],[5201,5212,17],[5311,5317,30],[5411,5417,30],[5511,5517,30],[5321,5339,31],[5629,5639,31],[5521,5539,32],[5421,5439,32]];
function sourcePage(code){if(!/^GA\d{4}$/.test(code))return null;const k=Number(code.slice(2));const r=ranges.find(x=>k>=x[0]&&k<=x[1]);return r?r[2]:null}
function status(code){
 const direct=sourcePage(code);if(direct)return {kind:'direct',message:'2026/12 resmî listesinde bu ürün kodunun teknik tablosu var.',page:direct};
 const match=code.match(/^GAGG?(\d{4})$/);
 const base=match?'GA'+match[1]:null;
 const page=base?sourcePage(base):null;
 if(page)return {kind:'base',base,message:'Yalnızca standart baz ürün '+base+' listede bulunuyor. Bu özel varyantın teknik bilgileri ayrıca doğrulanmış değildir.',page};
 return {kind:'missing',message:'Bu stok kodu için resmî 2026/12 tablosunda ürün bazlı doğrulanmış kaynak bulunamadı.'};
}
function render(p){
 const s=status(p.kod),full=p.tamKayit||{};
 document.title=p.kod+' · '+p.model+' | Ürüne Özel Teknik Föy';
 const rawRows=Object.entries(full).map(([key,value])=>'<tr><th scope="row">'+esc(key)+'</th><td>'+esc(format(value))+'</td></tr>').join('');
 const sourceLabel=s.kind==='direct'?'Ürünün resmî 2026/12 liste satırını içeren PDF sayfasını aç':
   s.kind==='base'?'Standart baz modelin 2026/12 liste sayfasını aç (varyant doğrulanmadı)':null;
 const sourceUrl=sourceLabel?official+'#page='+s.page:null;
 const sourceBlock=sourceUrl?'<p><a href="'+esc(sourceUrl)+'" target="_blank" rel="noopener noreferrer">'+esc(sourceLabel)+' ↗</a> · Sayfa '+s.page+'</p>':
 '<p>Bu ürün için doğrulanmış ürün bazlı resmî bağlantı bulunamadı.</p>';
 const fields=[
 ['Ürün ailesi',p.aile],['Ön inceleme sınıfı',p.altGrup],['Faz',p.faz],
 ['Güç (kVAr)',p.guc],['Akım (A)',p.akim],['Endüktans (mH)',p.L],
 ['p (%)',p.p],['THDv',p.thdv],['Dış ölçüler (mm)',p.olcu],
 ['Bağlantı',p.baglanti],['Sarım/iletken',p.sarim],
 ['Teknik inceleme durumu',p.durum],['Teknik not',p.aciklama]
 ];
 el.innerHTML='<span class="sheet-label">ÜRÜNE ÖZEL TEKNİK KART · '+esc(p.id)+'</span>'+
 '<h1>'+esc(p.kod)+' · '+esc(p.model)+'</h1><p class="sheet-lead">'+esc(p.grup)+' · Yalnızca bu ürün kaydının bilgileri</p>'+
 '<div class="sheet-status '+(s.kind==='direct'?'':'pending')+'"><b>Resmî kaynak durumu:</b> '+esc(s.message)+'</div>'+
 '<div class="sheet-overview">'+stat('Güç',valid(p.guc)?format(p.guc)+' kVAr':null)+stat('Birim ağırlık',valid(p.kg)?format(p.kg)+' kg':null)+
 stat('Dış ölçüler',p.olcu)+stat('Yıllık plan',valid(p.adet)?format(p.adet)+' adet':null)+'</div>'+
 '<h2>Bu ürünün teknik bilgileri</h2><dl class="sheet-specs">'+fields.map(([key,val])=>spec(key,val)).join('')+'</dl>'+
 '<h2>Üreticinin ürün bazlı kaynak referansı</h2><div class="sheet-source"><b>Grup Arge 2026/12 Fiyat ve Teknik Listesi</b>'+sourceBlock+
 (s.base?'<p>Referans baz kod: <b>'+esc(s.base)+'</b> — bu bağlantı '+esc(p.kod)+' varyantının datasheeti değildir.</p>':'')+
 '</div><p class="sheet-note">Kaynağın aynı sayfasında başka ürünler de bulunabilir. Ürüne özel görünen bu kart, uygulamanın ürün matrisinden oluşturulmuştur; üreticinin yayımladığı ayrı bir datasheet PDF değildir.</p>'+
 '<h2>Kaynak Excel satırındaki tüm bilgiler</h2>'+
 (rawRows?'<table class="sheet-raw"><tbody>'+rawRows+'</tbody></table>':'<p class="sheet-note">Bu kaydın tam ham matris alanları veri paketinde bulunmuyor.</p>')+
 '<p class="sheet-note">Eksik sarım, malzeme, vernik ve proses bilgileri varsayılarak doldurulmaz. Yatırım veya imalat kararları öncesi teknik resim ve üretici onayı gerekir.</p>';
}
async function start(){
 try{
  const id=new URLSearchParams(location.search).get('id');
  if(!id)throw Error('Ürün kimliği belirtilmedi.');
  const b64=window.PRODUCTS_GZIP_B64;
  if(!b64)throw Error('Ürün verisi bulunamadı.');
  const bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
  const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  const records=JSON.parse(await new Response(stream).text());
  if(!window.ShuntOfficial2026)throw Error('Şönt resmî teknik veri dosyası eksik.');
  window.ShuntOfficial2026.applyAll(records);
  const p=records.find(r=>String(r.id)===id);
  if(!p)throw Error('Bu ürün kimliği kaynak matrisinde bulunamadı: '+id);
  render(p);
 }catch(err){el.innerHTML='<div class="sheet-error"><b>Ürün teknik föyü açılamadı.</b><p>'+esc(err.message)+'</p><a href="index.html">Üretim listesine dön</a></div>';printButton.disabled=true}
}
start();
})();