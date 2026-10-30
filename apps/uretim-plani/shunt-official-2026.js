/* Grup Arge Şönt 2026/12 teknik doğrulama — 2026-10-30.
  Fiyat listesi p.17: https://www.gruparge.com/fl/tr#page=17
  Katalog çizim karşılaştırması, 2023 p.31-33:
  https://www.gruparge.com/wp-content/uploads/2023/04/grup-arge-urun-katalogu.pdf
  Güncel fiyat listesi ve 2023 katalog ölçü/ağırlık/akım/L/bağlantı eşleşir.
  Eski web ürün kartı ölçüleri farklıdır; fiyat listesi + katalog esas alınır.
  İki katalog-dışı SVC (GA5004 ve GA5006) bilinçli olarak doğrulanmaz.
  Fiyatlar 2026/12 listesi USD; teklif/kesin satınalma fiyatı değildir.
  Aylar, yıllık adet, numune kararı, üretim parti sayısı burada değişmez.
*/
(()=>{'use strict';
const PRICE_URL='https://www.gruparge.com/fl/tr#page=17';
const CATALOG_URL='https://www.gruparge.com/wp-content/uploads/2023/04/grup-arge-urun-katalogu.pdf';
const COLUMNS=['kod','model','guc','akim','L','olcu','baglanti','montaj','kg','fiyatUsd'];
const RAW=[["GA5001","SVC-R 1.0",1,4.34,168.38,"120×100×102","Klemens","M8",5,70],["GA5002","SVC-R 1.5",1.5,6.52,112.25,"150×125×110","Klemens","M8",8,86],["GA5003","SVC-R 3.0",3,13.04,56.12,"192×160×134","Klemens","M8",14.5,163],["GA5101","SRM 1.0",1,4.34,168.38,"150×125×105","Klemens","M8",6.5,93],["GA5102","SRM 1.5",1.5,6.52,112.25,"150×125×120","Klemens","M8",9.5,99],["GA5103","SRM 3.0",3,13.04,56.12,"192×160×144","Klemens","M8",17.5,192],["GA5104","SRM 5.0",5,21.7,33.7,"210×270×180","Pabuç","M8",20,272],["GA5105","SRM 7.5",7.5,32.6,22.45,"210×280×210","Pabuç","M8",27,368],["GA5106","SRM 10.0",10,43.4,16.83,"260×330×200","Bara","M8",34,480],["GA5107","SRM 15.0",15,65.2,11.2,"290×380×220","Bara","M8",47,751],["GA5108","SRM 20.0",20,86.9,8.4,"290×380×250","Bara","M8",58,863],["GA5201","SRT 0.5",0.5,0.72,1018.6,"150×150×72","Klemens","M8",8,123],["GA5202","SRT 1.0",1,1.44,509,"180×175×85","Klemens","M8",11.5,148],["GA5203","SRT 1.5",1.5,2.17,339.5,"180×175×115","Klemens","M8",14.5,192],["GA5204","SRT 2.5",2.5,3.61,203.72,"240×225×100","Klemens","M8",17,258],["GA5205","SRT 5.0",5,7.22,101.86,"295×255×170","Klemens","M8",27,384],["GA5206","SRT 7.5",7.5,10.83,67.9,"295×255×180","Klemens","M8",39,472],["GA5207","SRT 10.0",10,14.43,50.92,"370×330×190","Bara","M8",48,654],["GA5208","SRT 12.5",12.5,18.04,40.75,"390×330×210","Bara","M8",57,708],["GA5209","SRT 15.0",15,21.65,33.95,"390×330×220","Bara","M8",67,780],["GA5210","SRT 20.0",20,28.86,25.46,"460×380×220","Bara","M10",80,1220],["GA5211","SRT 25.0",25,36.08,20.37,"460×380×230","Bara","M10",96.5,1370],["GA5212","SRT 50.0",50,72.2,10.18,"520×430×290","Bara","M10",170,2250]];
const VERIFIED=new Map(RAW.map(r=>[r[0],Object.fromEntries(COLUMNS.map((k,i)=>[k,r[i]]))]));
const UNVERIFIED=new Set(['GA5004','GA5006']);
const str=v=>v==null?'':String(v).replace(/\s+/g,' ').trim();
const eq=(a,b)=>str(a).replace(/×/g,'x').replace(/\s+/g,'').replace(/,/g,'.').toLocaleLowerCase('tr')===str(b).replace(/×/g,'x').replace(/\s+/g,'').replace(/,/g,'.').toLocaleLowerCase('tr');
function apply(p){
 if(!p||p.grup!=='Şönt')return p;
 const original=p.tamKayit&&typeof p.tamKayit==='object'?p.tamKayit:{};
 const s=VERIFIED.get(p.kod);
 if(!s){
  if(!UNVERIFIED.has(p.kod))throw Error('Kayıtlı Şönt kodu 2026/12 teknik listede veya doğrulanmamış kod listesinde bulunamadı: '+p.kod);
  p.tamKayit={...original,
   '2026/12 katalog durumu':'Üreticinin 2026/12 standart Şönt listesinde bu stok kodu yok; teknik föy / üretici teyidi gerekli',
   '2026/12 liste kaynak sayfası':PRICE_URL,
   '2023 katalog kaynak sayfası':CATALOG_URL,
   'Teknik veri revizyon notu':'GA5004 / GA5006 için resmî kod eşleşmesi yok; katalog değerleri türetilmedi.'};
  p.shuntOfficial={verified:false,code:p.kod,priceList:PRICE_URL,catalog:CATALOG_URL,differences:[]};
  return p;
 }
 const mismatches=[];
 function diff(k,older,newer){if(!eq(older,newer))mismatches.push({field:k,old:older==null?null:older,new:newer})}
 diff('Ölçü G×Y×D (mm)',original['Ölçü G×Y×D (mm)'],s.olcu);
 diff('Ağırlık (kg)',p.kg,s.kg);
 diff('Bağlantı tipi',original['Bağlantı tipi'],s.baglanti);
 diff('Güç (kVAr)',original['Güç (kVAr)'],s.guc);
 diff('Akım (A)',original['Akım (A)'],s.akim);
 diff('L (mH)',original['L (mH)'],s.L);
 // Tek faz SVC/SRM; trifaze SRT, üretici şönt katalog sınıfları.
 const phase=s.model.startsWith('SRT')?3:1;
 p.kg=s.kg;
 // Teknik föy ve eski plan bu düz alanları kullanır.
 p.faz=phase;p.guc=s.guc;p.akim=s.akim;p.L=s.L;p.olcu=s.olcu;p.baglanti=s.baglanti;
 p.tamKayit={...original,
  'Faz':phase,
  'Güç (kVAr)':s.guc,'Akım (A)':s.akim,'L (mH)':s.L,
  'Ölçü G×Y×D (mm)':s.olcu,'Bağlantı tipi':s.baglanti,
  'Ağırlık (kg)':s.kg,
  '2026/12 katalog durumu':'Üretici 2026/12 fiyat listesi ve 2023 ürün katalogu ile doğrulandı',
  '2026/12 şönt liste fiyatı (USD)':s.fiyatUsd,
  'Ayak montaj cıvatası':s.montaj,
  'Termik koruma':'Var (üretici 2023 teknik katalogu)',
  '2026/12 liste kaynak sayfası':PRICE_URL,
  '2023 katalog kaynak sayfası':CATALOG_URL,
  'Teknik veri revizyon notu':mismatches.length
    ?'Önceki uygulama verisine göre '+mismatches.length+' alan güncellendi. Üretici, ürün dış ölçülerinin değişebileceğini belirtiyor. Kesin seri/BOM ölçüsü imalat öncesi teyit edilmeli.'
    :'Üreticinin fiyat listesi ve ürün kataloğuyla aynı. Kesin imalat BOM/teknik resim teyidi ayrıca gereklidir.'
 };
 p.shuntOfficial={verified:true,code:p.kod,sourceYear:'2026/12',priceList:PRICE_URL,catalog:CATALOG_URL,differences:mismatches,model:s.model,mountBolt:s.montaj,priceUsd:s.fiyatUsd};
 return p;
}
function applyAll(records){
 if(!Array.isArray(records))throw Error('Şönt teknik veri tablosu liste olmalı');
 const matching=records.filter(p=>p&&p.grup==='Şönt');
 const seen=new Set(matching.map(p=>p.kod));
 if(matching.length!==25||seen.size!==25||matching.some(p=>!VERIFIED.has(p.kod)&&!UNVERIFIED.has(p.kod)))throw Error('Şönt resmî liste kapsaması eksik: '+matching.length+' ürün');
 records.forEach(apply);
 const verified=matching.filter(p=>p.shuntOfficial&&p.shuntOfficial.verified);
 const unknown=matching.filter(p=>p.shuntOfficial&&!p.shuntOfficial.verified);
 if(verified.length!==23||unknown.length!==2)throw Error('Şönt 23+2 doğrulama koşulu sağlanmadı');
 return records;
}
window.ShuntOfficial2026=Object.freeze({apply,applyAll,get:code=>VERIFIED.get(code)||null,verifiedCount:VERIFIED.size,unknownCodes:[...UNVERIFIED],source:PRICE_URL,catalog:CATALOG_URL});
})();
