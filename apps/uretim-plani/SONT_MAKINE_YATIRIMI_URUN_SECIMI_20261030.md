# ŞÖNT — MAKİNE YATIRIMI İÇİN FİZİKSEL ÜRÜN İNCELEME SEÇİMİ
Tarih: 30 Ekim 2026 · Kapsam: yalnız Şönt, **25 ürün / 35.772 ürün-yıl** · Durum: **FİZİKSEL TEST VE ÇEVRİM ÖLÇÜMÜ BEKLİYOR**.

## Gerçek hedef ve kritik düzeltme
Ürünler kullanıcıda fiziksel olarak mevcuttur; **numune satın alma maliyeti, ilave ürün satın alma veya ürünlerin birbirini satış açısından temsili hedef değildir**. Karar: **bobin sarım makinesi, nüve/istif ve montaj ekipmanı, vernik/emprenye, kurutma/fırın, yükleme/elleçleme kapasitesini belirlemek üzere hangi eldeki ürünlerin ölçülüp gerekirse açılacağı**. Önceki 9 ürün seçiminde 6.502 adet/yıl GA5003 ile 3.914 adet/yıl GA5001 yoktu: toplam Şönt üretiminin %29,12'si ilk inceleme dışında kalıyordu. Önceki 9'a bunların eklenmesiyle ilk dalga **11 ürün / 32.654 adet / %91,28 adet kapsaması**. Bu yüzde **bobin adedi, makine-saat veya proses kapasitesi kapsaması değildir**.

### Kritik resmî kaynak sürümü uyuşmazlığı
30 Ekim 2026'da doğrudan erişilen resmî [Grup Arge /fl/tr 2026/12 PDF, basılı s.17](https://www.gruparge.com/fl/tr#page=17) **mevcut uygulamadaki `shunt-official-2026.js` katmanının 2026/12 kaynaklı dediği ölçü/bağlantı değerlerinden ayrışıyor**. Örnek: `GA5002` PDF **150×125×121, 9 kg**, eski düzeltme **150×125×110, 8 kg**; `GA5205` PDF **Pabuç M8**, düzeltme **Klemens**; `GA5207` PDF **Pabuç M10**, düzeltme **Bara**; `GA5212` PDF **530×420×260, 173 kg**, düzeltme **520×430×290, 170 kg**. İki teknik revizyonu veya PDF sürümünü birbirine karıştırarak makine boyutu seçmek yasaktır. Aşağıdaki değerler **erişilen /fl/tr PDF'nin birebir katalog referansıdır**; eldeki parçanın gerçek ölçüsü/imalat revizyonu henüz ölçülmedi. Üretici boyutların değişebileceğini yazmaktadır. **Uygulamadaki eski teknik override bu uyuşmazlık giderilmeden CAPEX hesabında kullanılmamalıdır.** Fiyat listesi bedelleri makine seçimi ölçütü değildir.

## Seçim kuralı
- **A — 11 öncelikli fiziksel inceleme/test**: Daha önce seçili dokuz (GA5002, GA5102, GA5104, GA5106, GA5108, GA5204, GA5207, GA5209, GA5212) + **GA5001 ve GA5003**. Gerekçe: SVC-R hacminin iki yüksek adetli ve boyutça farklı modeli; SRM ve SRT sınıflarında küçük, orta, büyük; klemens/pabuç/bara; 173 kg katalog üst sınırı GA5212.
- **B — 8 hedefli ikinci kontrol**: GA5103 (810 adet; ara ölçü/iş yükü), GA5105 (904; orta Pabuç M10), GA5201 (yüksek nominal L 1018,6 mH: fiziksel tur sayısı olduğu varsayılmaz), GA5205/GA5206 (SRT orta Pabuç M8, farklı nominal ölçü/ağırlık), GA5211 (SRT 25; orta-büyük yükleme/grup), GA5004/GA5006 (resmî stok kodu bulunmuyor, eldeki ürün üzerinden kimlik/ölçü çıkart). Bunlarda **önce sökmeden ölçme ve A ile kıyas**, farklı sarım/geometri/proses bulgusu varsa söküm ve proses denemesi yapılır.
- **C — 6 doğrulama ürünü**: GA5101, GA5107, GA5202, GA5203, GA5208, GA5210. **Hepsi ilk turda sökmeden ölçülür.** Eğer A/B minimum–maksimum aralıklarını aşan gerçek bobin ebatları, tel/folyo veya proses farkı varsa inceleme grubuna yükseltilir. Hiçbir ürün 'fiziksel olarak kesin kapsandı' sayılmaz.
- **A seçimi, makine teklifi istenecek nihai 11 ekipman numunesi demek değildir.** Bir makine için A+bir B ürünü, başka bir makine için yalnız uç değerler test edilebilir.

## 25 ürünün adet ve katalog teknik tarama tablosu
A ve B/C kodları yukarıdaki fiziksel inceleme önceliğidir; stok ürünü satın alma statüsü değildir. Boyutlar **tamamlanmış ürün** katalog dış ölçüsü; sarım bobini veya fırın sepeti ölçüsü değil.

| Kod | Aile/model | Adet/yıl | Katalog G×Y×D mm | Ürün kg | Bağlantı | İnceleme |
|---|---|---:|---|---:|---|:---:|
| GA5001 | SVC-R 1.0 | 3.914 | 120×105×103 | 5 | Klemens | A |
| GA5002 | SVC-R 1.5 | 13.462 | 150×125×121 | 9 | Klemens | A |
| GA5003 | SVC-R 3.0 | 6.502 | 192×164×131 | 15 | Klemens | A |
| GA5004 | SVC-R 5.0 | 112 | — | — | Doğrulanmadı | B |
| GA5006 | SVC-R 10.0 | 162 | — | — | Doğrulanmadı | B |
| GA5101 | SRM 1.0 | 172 | 120×105×111,5 | 6 | Klemens | C |
| GA5102 | SRM 1.5 | 832 | 150×125×121 | 9 | Klemens | A |
| GA5103 | SRM 3.0 | 810 | 192×164×136 | 16 | Klemens | B |
| GA5104 | SRM 5.0 | 2.632 | 210×315×145 | 20 | Pabuç M8 | A |
| GA5105 | SRM 7.5 | 904 | 210×260×165 | 26 | Pabuç M10 | B |
| GA5106 | SRM 10.0 | 4.178 | 255×315×155 | 32 | Bara M8 | A |
| GA5107 | SRM 15.0 | 54 | 290×365×185 | 50 | Bara M10 | C |
| GA5108 | SRM 20.0 | 342 | 290×365×205 | 62 | Bara M10 | A |
| GA5201 | SRT 0.5 | 52 | 150×125×105 | 8 | Klemens | B |
| GA5202 | SRT 1.0 | 108 | 150×127×130 | 11.5 | Klemens | C |
| GA5203 | SRT 1.5 | 168 | 192×164×144 | 14.5 | Klemens | C |
| GA5204 | SRT 2.5 | 314 | 215×265×144 | 17 | Klemens | A |
| GA5205 | SRT 5.0 | 296 | 325×260×135 | 29 | Pabuç M8 | B |
| GA5206 | SRT 7.5 | 56 | 325×260×155 | 38 | Pabuç M8 | B |
| GA5207 | SRT 10.0 | 304 | 380×315×155 | 48 | Pabuç M10 | A |
| GA5208 | SRT 12.5 | 14 | 380×315×165 | 55 | Bara M8 | C |
| GA5209 | SRT 15.0 | 120 | 380×315×175 | 63 | Bara M8 | A |
| GA5210 | SRT 20.0 | 90 | 460×365×175 | 82 | Bara M10 | C |
| GA5211 | SRT 25.0 | 120 | 460×365×185 | 93 | Bara M10 | B |
| GA5212 | SRT 50.0 | 54 | 530×420×260 | 173 | Bara M10 | A |

**Kontrol toplamı:** A = 11 ürün / 32.654 adet (%91,28); B = 8 / 2.512 (%7,02); C = 6 / 606 (%1,69). Toplam = 25 / 35.772. Yuvarlama yüzünden yüzdeler 100,00 etmeyebilir.

## Makineye göre fiziki ölçüm ve kabul kanıtları

### 1. Sarım makinesi (tel/folyo henüz doğrulanmadı)
Her A ürününden, gerekirse B/C ile sınır testinden: bobin gerçek iç/dış çapı veya dikdörtgen ölçüleri, sarım genişliği/yüksekliği, bobin net ağırlığı, gerçek iletken bakır/alüminyum ve tel/levha geometrisi, tel/folyo kesiti, sarım tur sayısı, katman/ara izolasyon, sarım yolu ve bobin sayısı, mandren/kalıp, germe/tork ihtiyacı, bobin başı gerçek çevrim ve model değiştirme ayar süresi, hurda/yeniden işleme. **Nihai reaktör dış ölçüsü ve toplam 173 kg, sarım makinesinin mil yükü/gerçek bobin kütlesi sayılamaz.** Üretici örneği: [Calotron tel sarım makineleri](https://www.calotron.com/en/wire-winding-machines/) makine seçiminde tel çapı, sarım eni/çapı, tork, çalışma hızı ve bobin kütlesinin ayrı limitler olduğunu gösterir. 11 ürünün gerçek iletken yapısı bilinmeden 'tek tel/folyo makinesi yeter' denemez.

### 2. Nüve/istif ve mekanik montaj
A ve B ürünlerinde çekirdek laminasyon şekli, boy/en, sac kalınlığı, istif yüksekliği, paket ağırlığı, hava aralığı ve bağlama/izolasyon yöntemi, bağlama/pabuç/bara işlemi ve operatör hareketleri kaydedilmeli. SRM ve SRT'nin aynı nüve veya ortak kesim takımı kullandığı **varsayılmaz**.

### 3. Vernik, emprenye ve kurutma/fırın
Fiilen hangi aşamanın emprenye edildiği (bobin mi montajlı reaktör mü), vernik türü/viskozitesi, uygulanacak vakum/basınç ihtiyacı, fiilî sepet ölçüsü, parça yerleşimi, sepette adet, toplam yük kg, daldırma/damlama/kurutma çevrimi ve proses sıcaklık/süre reçetesi ürün üzerinde ölçülmeli. [Vyvos](https://vyvos.cz/en/vacuum-pressure-impregnation/) VPI ekipmanının müşteri ihtiyacına göre tank geometrisi ve vakum/basınçla tasarlandığını belirtir. [Despatch fırın seçimi](https://www.despatch.com/blog/guide-selecting-right-industrial-oven-processing-application/) yük, hava akımı, sıcaklık homojenliği ve çevrim süresinin temel boyutlandırma değişkenleri olduğunu vurgular. **Salt GA5212 ürün dış ölçüsü, kazan/fırın iç hacmini veya sepet başına adedi belirlemez.** Aktif çalışma **tek vardiya, günde 9 saat**.

### 4. Kapasite hesabı — henüz veri eksik
Yıllık sarım saati = Σ(ürün adedi × gerçek bobin adedi/ürün × ölçülmüş sarım dk/bobin)/60 + ölçülmüş setup ve kayıp saatleri. 
Gerekli sarım tezgâhı adedi = ceil[yıllık sarım saati / (9 saat/gün × gerçek üretim günü × ölçülmüş kullanılabilirlik)].
Fırın/VPI: ayrı ayrı parti sepet adetleri × gerçek yükleme/boşaltma + çevrim + bekleme; doluluk ve eşzamanlı kürleme/kurutma kısıtlarıyla darboğaz hesabı.
**Üretim günü, bobin adedi, sarım dakika, VPI ve fırın reçete/dolum verileri yok:** makine modeli/adedi veya çevrim/hacim henüz kesinleştirilmedi. Mevcut aylık planın da gerçek bobin yüküne göre onaylandığı iddia edilemez.

## İnceleme sırasında doldurulacak zorunlu fiş (her ürün × proses)
`Ürün kodu | fiziksel numune revizyonu/lot | gerçek ürün ölçü/kg | gerçek bobin adedi | bobin geometri/ağırlık | tel/folyo Cu/Al kesiti | sarım tur | sarım dk/bobin | değişim/setup dk | nüve tip/istif | emprenye edilen parça | vernik reçetesi | sepet yerleşimi ve adet | VPI dk/parti | kurutma/kurleme °C ve dk/parti | operatör sayısı | güvenilirlik/ölçümü yapan`.

## İş kararı ve sınırlar
**İlk fiziksel inceleme A = 11, sonra B'den sınır/bağlantı/proses açısından farklı çıkanlar dahil edilir.** Ürünler elde; satın alma bütçesi yok. Üreticilerin makine örnekleri doğrudan model satın alma tavsiyesi değildir. Makine teklifi için ancak ölçülen bobin yükü/hızı, VPI sepeti ve fırın çevriminden kapasite zarfı çıkartılacak. Eski 9'luk 'kapsama' raporu **makine yatırımı için yeterlilik kararı değildir**; bu dosya bu amaçta esas alınmalıdır.
