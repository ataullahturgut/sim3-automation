# ŞÖNT REAKTÖR — SARIM MAKİNESİ, EMPRENYE SİSTEMİ VE FIRIN ALIMI TEKNİK VERİ ŞARTNAMESİ

Tarih: 30 Ekim 2026 · Kapsam: **yalnız Şönt, 25 ürün, 35.772 ürün/yıl, tek vardiya 9 saat aktif çalışma** · Durum: **Satın alma için zorunlu fiziksel ve proses verileri kısmen eksik — makine modeli/kapasite onaylanmadı**

## 0. Amaç ve metodoloji

Bu çalışma **Grup Arge kataloğundan ürün ailesi çıkarıp makine seçmek değil**; doğrudan *makine imalatçılarının tasarım limitleri*, *elektrik yalıtım malzemesi/proses üreticilerinin teknik dokümanları* ve *fırın güvenliği ve termal yük kriterlerinden* hareketle yatırım için hangi teknik girdilerin zorunlu olduğunu belirler. Ürünler satın alınmayacak; **mevcut fiziksel Şönt ürünleri** açılabilir, ölçülebilir, denenebilir.

Şu anda yıllık **35.772 ürün** miktarı ve **9 saat aktif operatör vardiyası** biliniyor. **Fiziksel bobin adedi/ürün, gerçek sarım çevrimi, reçine türü, fırın çevrimi, yıllık çalışma günü ve güvenli gözetimsiz işlem rejimi doğrulanmadı.** Makine sayısı, tank/fırın iç ölçüsü veya VPI basıncı hakkında kesin sayı vermek bu aşamada hatalıdır.

**İki farklı kayıt disiplini:** (i) _ürün düzeyi teknik veri_ (25 kodun her biri), (ii) _proses reçetesi/parti düzeni_ (ortak olabilir ancak eşdeğerliği fiziksel test ve teknik dosya ile kanıtlanmalı). Aynı güç/kVAr, faz veya toplam reaktör ağırlığı aynı bobin ve aynı çevrim anlamına gelmez.

## 1. SARIM MAKİNESİ — satın alma için zorunlu ürün kartı

| Alan (ürün/bobin düzeyi) | Birim / tür | Kaynak/kabul kanıtı | Satın almada belirlediği |
|---|---|---|---|
| **Gerçek fiziksel bobin adedi/reaktör** | adet/ürün | söküm + imalat resmi/BOM | yıllık sarım adedi |
| **İletken biçimi** | yuvarlak tel / dikdörtgen tel / folyo / çoklu paralel | numune + sarım reçetesi | tel veya folyo makinesi / kombinasyonu |
| **İletken malzemesi** | Cu / Al / diğer | kesit, etiket, onaylı malzeme listesi | tensioner, kaynak ve iletken besleme uyumu |
| **İletken kesiti** | yuvarlak: çap mm; dikdörtgen: en×kalınlık mm; folyo: en×kalınlık mm | kalibre ölçümü/teknik resim | izin verilen tel/folyo aralığı |
| **İzolasyon ve sarım yerleşimi** | sarım izolasyonu, ara katman malzemesi/kalınlığı, en, ilerleme | reçete + numune | otomatik kılavuz, katman izolasyon besleyicisi |
| **Bobin formu ve gerçek geometrisi** | yuvarlak/oval/dikdörtgen; iç/dış çap veya en×boy, sarım genişliği mm | ürün söküm/kalıp ölçümü | mandren, merkezler arası mesafe, travers, max çap |
| **Bobin net kütlesi** | kg/bobin | tartım | mil yükü, fren torku, taşıma |
| **İletken makarası** | dış/iç çap, genişlik, kg; bobin başına kullanılan sarım makara adedi | hammadde ve stok bilgisi | açıcı, fren ve besleme sehpası |
| **Sarım tur/katman ve uç bağlantısı** | tur/katman; uç açma/sabitleme/birleştirme işlemleri | reçete + deneme | kontrolör, tel kırma, TIG/soğuk kaynak vb. |
| **Sarım süresi** | dk / gerçek bobin, işe alma/çıkarma dahil tanımlı ölçüm | zaman etüdü, farklı operatör/ürün | kapasite, makine adedi |
| **Ürün değiştirme/setup** | dk / model değişimi | deneme | yıllık kayıp saat |
| **Ret/yeniden işleme** | oran ve dakika | pilot üretim | efektif kapasite |

**Tedarikçi RFQ**: çalışma aralığı [min–max iletken], [min–max bobin iç/dış ölçüsü], bobin kg, hızın **yük altındaki** değeri, tork-hız eğrisi, gerginlik aralığı/doğruluğu, tur sayımı, takım/mandren değişimi, çoklu bobin ve paralel tel desteği, izolasyon beslemesi, Cu/Al kaynak/ekleme, kalıp listesi, sarım reçetesi yazılımı, iş güvenliği/koruma, elektrik/yerleşim/floor load, garanti/bakım ve demo/FAT.

**Önemli:** Üreticiler farklı hatlara özel tek ve çoklu tel, folyo ve karışık yapılar tasarlar; fiyat listesi veya ürün dış ölçüsünden 'tek makine yeter' kararı verilemez. Örnek teknik yetenek ve ölçüt kaynakları: [Broomfield Wire](https://www.broomfieldusa.com/coil-winding-machine/), [LAE Wire](https://www.lae-srl.com/en/soluzione/wind-winding-machines/hv-wire-winding-machines/), [LAE Foil](https://www.lae-srl.com/en/soluzione/wind-winding-machines/foil-winding-machines/).

## 2. EMPRENYE — önce yöntem, sonra kazan

**Karar kapısı E0:** Nihai ürün için emprenye gerçekten gerekli mi, ürünün hangi aşamasında yapılıyor (tek bobin, 3 bobin grubu, nüveli komple reaktör)? Yanıtı bilinmeden tank alınmaz. Aynı aile içinde farklı prosesler varsa bağımsız reçete açılır.

| Alan | Birim/tür | Nereden | Satın almada belirlediği |
|---|---|---|---|
| Emprenye edilen parçanın **gerçek** ölçü/kütlesi | mm/kg | fiilî proses ürünü | tankın faydalı ölçüsü ve kaldırma |
| Şekil ve sepet yerleşim testi | adet/sepet; boşluk mm; kg/parti | fiziksel yerleşim | tank çap/yükseklik + aparat |
| Malzeme kimliği | üretici/ürün kodu, TDS, SDS, parti/lot | vernik/reçine sağlayıcısı | vakum/metal/seal uyumluluğu, güvenlik |
| Viskozite / sıcaklık / katı oranı / pot-life | ilgili TDS birimleri | malzeme TDS | pompa, ısıtma/soğutma, filtrasyon, geri dönüş |
| Proses tipi | atmosferik dip + bake / vakum daldırma / VPI / başka | yalıtım sistemi doğrulama, pilot test | basınçlı kap zorunluluğu |
| Kurutma/vakum/ıslak vakum/pozitif basınç | mbar abs veya kPa abs, bar(g), sıcaklık, süre | **seçilen reçineye özel** onaylı proses | pompa ve basınçlı kap sınıfı, otomasyon |
| Doldurma/bekleme/boşaltma/damlama | dk/parti | pilot deneme | **tam gerçek tank çevrimi** |
| Islak reçine tutma/akıtma | kg/parti | tartım/test | tüketim, tank stok ve filtrasyon |
| Temizlik, kimyasal değişimi, atık | zaman/malzeme | pilot/SDS | yardımcı tesisler |
| Ses/ısı/yalıtım ve elektriksel kabul | ürün test prosedürü | ürün mühendisliği | prosesin yeterliliği |

**Zorunlu RFQ:** çelik/conta/malzeme kimyasal uyumluluğu, iç faydalı alan ve sepet aparatı, kaldırma yükü, basınç-vakum dayanımı **seçilen proses verisine göre**, pompa kapasitesi/pumpdown süresi, resin storage/mixing/filtration, dozaj/drenaj, izleme/kayıt, sıcaklık-viskozite kontrolü, solvent/vakum egzozu ve yangın güvenliği, tank temizliği, üretici pilot testleri ve kabul.

**VPI her Şönt reaktöründe zorunlu değildir.** HEDRICH teknik olarak farklı reçineler ve müşteri şartlarına göre vakum basınçlı reçine sistemlerini tasarlar. [HEDRICH VPI](https://www.hedrich.com/en/products/technologies/equipment-for-vacuum-pressure-impregnation). **ELANTAS PG-127** ise yalnız belirli kuru tip trafo VPI epoksi süreci için örnek sıcaklık/vakum/basınç/kurutma aşamaları verir ve rakamların **genel makine spesifikasyonu olmadığı** uyarısını yapar. [ELANTAS PG-127](https://www.elantas.com/fileadmin/elantas/companies/elantas_pgd/about_us/service/pg-127_vpi_epoxy_process_guide_for_dry_type_transformers.pdf). Bu tablodaki hiçbir set noktası Şönt ürünlerine otomatik aktarılmaz.

## 3. FIRIN / KURUTMA / KÜRLEME — tank ile ayrı ayrı kapasite hesabı

| Alan | Birim/tür | Nereden | Satın almada belirlediği |
|---|---|---|---|
| Fırına fiilen giren ürün/parça | bobin/komple reaktör/tepsi | gerçek üretim akışı | kabin/şasi/raf |
| **Faydalı yerleşim geometrisi ve toplam yüklü kütle** | mm, kg/parti, raf yüksekliği/boşluğu | yükleme provası | kabin ölçüsü, raf/araba kapasitesi |
| Proses görevi | ön kurutma / damlatma sonrası solvent uçurma / kimyasal kürleme | reçete | bir ya da birden çok fırın |
| TDS ile doğrulanmış sıcaklık / bekleme reçetesi | °C, dk | kimyasal TDS + teknik onay | sıcaklık aralığı |
| Ürün içi ısınma süresi (boş fırın değil) | dk/parti, ağır/yoğun yükte ölçüm | termokupllu deneme | ısıtma gücü, hava sirkülasyonu |
| Soğuma ve çıkarma | dk/parti | deneme | toplam işgal süresi |
| Sıcaklık homojenliği kabul kriteri | °C tolerans, yük altında test | ürün/proses doğrulama | homojen hava kanalları ve kontrol |
| **Solvent/SDS, VOC kg/parti ve açığa çıkış hızı** | kg/parti, kg/saat | SDS/TDS + deneme | egzoz, LEL izleme, patlama/yangın güvenliği |
| Yükleme-boşaltma ve kayıt | araba, operatör, süre; reçete ve termokupl log | tesis ve üretim | ergonomi, izlenebilirlik |

**Zorunlu RFQ:** yük altında min/max °C ve sıcaklık uniformite garantisi, iç faydalı ölçü (net raf/araba boyutları), nominal ve maksimum yük kg, enerji kW **ısıtma hesabı**, gerçek yüklü ürünün hedef sıcaklığa ulaşma süresi, reçete programlama/data logging, havalandırma/hava akışı, kapı/taşıma/servis, yerleşim ve enerji bağlantıları, güvenlik, FAT yük testi.

**ÇOK KRİTİK:** Malzeme SDS'sine göre **yanıcı uçucular/solvent** oluşuyorsa sıradan kurutma fırını satın alınmamalı; uygun havalandırma, purge, güvenlik kilidi ve ilgili mevzuat/standart uygunluğu değerlendirilmelidir. [Despatch Class A](https://www.despatch.com/blog/understanding-class-a-ovens/). **NFPA 86**, ilgili uygulamalar için güvenlik referansıdır; Türkiye'deki yasal uygunluğu ayrıca tedarikçi ve yetkili mühendis doğrulamalıdır. [Despatch oven selection](https://www.despatch.com/blog/guide-selecting-right-industrial-oven-processing-application/); [Wisconsin Oven 2026 transformatör reçine kürleme örneği](https://www.wisoven.com/news/wisconsin-oven-ships-curing-oven-manufacturer-in-power-industry).

## 4. ÜRETİM KAPASİTESİ ve vardiya

**Bilinen:** Şönt = 25 SKU, 35.772 reaktör/yıl. Aktif çalışma = bir vardiya **9 saat/gün**. **Bilinmeyen:** yılda fiilî üretim günü, kullanılabilirlik, bobin/ürün, gerçek çevrimler, gereken üretim partileri/reçete, ürünün **gerçek** per-batch istifi, fırın sürecinin gözetimsiz çalışma izni.

Ürün k için:
- **Yıllık bobin adedi:** \`B_k = Yıllık_ürün_k × Gerçek_bobin_adedi_k\`.
- **Sarım yıllık makine saati:** \`Σ(B_k × fiili_dk/bobin_k)/60 + Σ(ürün_değişimleri × fiili_setup_dk)/60 + kalite/yeniden işleme\`.
- **Bir sarım makinesinin fiilî yıllık üretken saatleri:** \`9 saat × gerçek üretim günü × kanıtlanmış kullanılabilirlik\`; paralel operatör/makine etkileşimi ayrıca kısıtlanır.
- **Kazan/fırın bir üretim partisindeki gerekli batch:** \`ceil(partide proses gören parça adedi / fiziksel sepete güvenli yerleşen parça adedi)\` (karma ürün kombinasyonlarında gerçek yerleşim planı).
- **Kazan / fırın takvim işgali:** \`Σ(batch sayısı × doğrulanmış bütün çevrim saati)\` + boşaltma/temizlik/diğer hazırlık. Ayrı ekipmanlar zincirinin bekleme ve devreler arası transferi kapasiteyi etkiler.
- Fırın **tek vardiya personel** altında güvenli, yetkili ve izlenen gözetimsiz çevrim çalıştırabiliyorsa takvim işgali 9 saat/günle sınırlı olmak zorunda değildir; bunun **tesis yetkisi, risk analizi, güvenlik kilitleri ve işletme kararı** olmadan mümkün olduğu varsayılmaz.
- Yıllık değil **aylık ve yoğun gün yükü** ayrıca hesaplanmalı; 4 parti/3 parti vb. plan varsayımları kapasiteyi tek başına doğrulamaz.

**Makine adedi, kapasite veya tank hacmi için henüz doğrulanmış sayısal teklif parametresi yok.** 35.772 ürün/yıl ve 9 saat vardiya tek başına yeterli değildir.

## 5. 25 SKU için veri toplama protokolü

- **Tüm 25 ürün:** ürün kodu/lot/revizyon/üretim adedi; dış ölçü/kg (yalnız ürün karşılaştırması); *fiziksel bobin adedi/ürün*; malzeme tipi ve iletken biçimi; ayrı bobin iç-dış form/ölçü/turn/kütle; izolasyon; işleme giren nesne; vernik kimliği. Her değer için _kaynak_: fiziki ölçüm + foto/ölçen, onaylı BOM/iş emri, malzeme TDS/SDS veya doğrulanmış üretici çizimi. Bilinmiyorsa: **“Ölçüm bekliyor”**; boş veri bir sayıya çevrilmez.
- **Öncelikli 11 Şönt ürün:** gerçek sarım + makine ayar ve setup süre etüdü, söküm/foto/ölçü, emprenye sepet provası, ısıtma/soğutma/proses pilotu. Mevcut 11 seçimi yalnız **yıllık adedin %91,28'ini** oluşturan ürünlerin ilk turu; makine boyut sınırının tamamını temsil ettiğine ilişkin kanıt yok.
- **Diğer 14 ürün:** önce sökmeden dış ölçü, elektrik bağlantı, bobin görünümü ve iletken gözlemi; en küçük/en büyük bobin, nadir iletken ve proses/basket sınırına çıkanlar **otomatik detaylı teste yükseltilir**. 11'den daha küçük büyük teknik uç değer olabileceği için "dışlanan 14" denemez.
- **Bağımsız seçim setleri:** sarım makinesi uç değer örnekleri / tank maksimum gerçek yük ve geometri örnekleri / fırın en yoğun ve en ağır gerçek kürleme yükü örnekleri **birbirinin aynı olmak zorunda değil**. Makine teklifinde her ekipmanın kendi test zarfı kullanılır.

### Alan için karar/kanıt etiketleri

1. \`DOĞRULANDI\` — ürün kodu/lotuna göre ölçüm kaydı veya onaylı BOM/teknik çizim; ölçüm tarihi ve yapan belirtilir.
2. \`REÇETE TDS/SDS\` — malzeme koduna özgü üretici belge/revizyonu, fiziksel ürünle uyum denetimi.
3. \`ÖLÇÜM BEKLİYOR\` — fiziksel verisi kayıtsız; **0, 1, 3, standart değer yazma**.
4. \`KAYNAK ÇELİŞKİSİ\` — dış ölçü/bağlantı gibi iki belge arasında fark; kaynak/fiziksel parti çözülmeden makine limit değeri sayılamaz.

## 6. Teklif toplama ve kabul için son kontrol listesi

1. **Sarım üreticisine** 11 pilot + 14 sınır kontrolünden elde edilen gerçek bobin/iletken matrisi ve yük/performans zarfı; örnek bobin üzerinde **FAT**, tork/hız/tur/izolasyon/yapı kabul kriterleri ve gerçek çevrim.
2. **Emprenye üreticisine** seçilmiş kimyasal TDS/SDS + işlem gören parça + net sepet yerleşimi + doğrulanmış proses vakum/basınç/zaman reçetesi; **FAT proses gösterimi**, güvenlik ve temizlik.
3. **Fırın üreticisine** gerçek ağır/en geniş/yüksek proses partisi + TDS sıcaklık-zaman eğrisi + solvent salım verisi; **yük altında sıcaklık uniformite ve süre FAT/SAT**; malzemeye uygun solvent güvenliği.
4. Her tedarikçiden **ürün başına gerçek saatlik kapasite taahhüdü** ve 9 saat aktif vardiya koşullarında darboğaz hesabı, kurulum, saha hizmeti, yedek parça, enerji ve toplam sahip olma maliyeti istenir.
5. **IEC 60076-6** şönt dahil reaktörlere uygulanır; **IEC 60085** malzeme ile yalıtım *sistemi* sınıflandırmasını ayırır; **IEC 61558-1** kapsamdaki bazı kuru tip reaktörlerin güvenlik gereklerini ele alır. Uygulanacak ürün standardı ve sertifikasyon kapsamı ürünün kullanımına göre ayrıca kararlaştırılır.

## Bağımsız üretici/otorite kaynakları
- https://www.broomfieldusa.com/coil-winding-machine/
- https://www.lae-srl.com/en/soluzione/wind-winding-machines/hv-wire-winding-machines/
- https://www.lae-srl.com/en/soluzione/wind-winding-machines/foil-winding-machines/
- https://www.hedrich.com/en/products/technologies/equipment-for-vacuum-pressure-impregnation
- https://www.elantas.com/fileadmin/elantas/companies/elantas_pgd/about_us/service/pg-127_vpi_epoxy_process_guide_for_dry_type_transformers.pdf
- https://www.despatch.com/blog/guide-selecting-right-industrial-oven-processing-application/
- https://www.despatch.com/blog/understanding-class-a-ovens/
- https://www.wisoven.com/news/wisconsin-oven-ships-curing-oven-manufacturer-in-power-industry
- https://webstore.iec.ch/en/publication/604
- https://webstore.iec.ch/en/publication/666
- https://webstore.iec.ch/en/publication/26261

**Yasak çıkarımlar:** reaktör dış kg => bobin kg; faz => fiziksel bobin adedi; kVAr => tel/folyo biçimi; 155 °C yalıtım sınıfı => kürleme fırını set sıcaklığı; katalog dış ebat => tank iç ölçüsü; 35.772 ürün/yıl => makine sayısı.
