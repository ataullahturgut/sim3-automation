# Şönt numune temsil denetimi — 25 ürün, 2026-10-30

## Denetimin sorusu
Mevcut 9 Şönt numunesi 25 ürünün fiziksel nüve, bobin, sarım, montaj ve üretim prosesi açısından yeterli temsili midir? **Yalnız katalogdan bu kesin olarak kanıtlanamaz**. Bu kayıt, kanıtlanmış eşleşmeleri değil, seçimi ve açıklığa kavuşturulması gereken bağlantı/ürün kodu ayrımlarını ortaya koyar.

## Kaynaklar
- 2026 numune ve kıyas seçimleri: `Reaktor_Ortak_Uretim_ve_Numune_Matrisi_2026.xlsx` (25 Şönt ürün, 35.772 adet).
- [Grup Arge 2026/12 resmî fiyat listesi](https://www.gruparge.com/fl/tr) (stok kodu, 230/400 V aile, kVAr, A, L, ölçü, kg, bağlantı, montaj).
- [Grup Arge 2023 ürün kataloğu](https://www.gruparge.com/wp-content/uploads/2023/11/Grup-Arge-2023-Urun-Katalogu.pdf) ve [Şönt kullanım kılavuzu](https://www.gruparge.com/wp-content/uploads/2025/05/SONT-REAKTORU-KULLANMA-KILAVUZU.pdf) (Tip 1/Tip 2 çizimler ve D/E montaj ölçüleri; kesin imalat BOM'u değil).
- Uygulamadaki doğrulanmış stok kodu katmanı: `shunt-official-2026.js`.

## Kesin bulgular
- **9 fiziksel numune adayı**: 3 ilk fiziksel numune ve 6 fiziksel kıyas; bunların **22.238 adet/yıl** üretimi vardır (**%62,17**).
- Diğer 16 ürün: **9 katalog/çizim kıyası** (11.794 adet), **3 yanlış bağlantı grubuna yönlendirilmiş kıyas** (1.256 adet), **2 fiziksel referansı bulunmayan kıyas** (210 adet), **2 ürün kodu doğrulanmamış** (274 adet).
- Bu sınıflandırma, ürünlerin birbirinin fiziksel üretim eşdeğeri olduğunu **kanıtlamaz**.
- İlk numune kodları **GA5002, GA5106, GA5212**; fiziksel kıyas kodları **GA5102, GA5104, GA5108, GA5204, GA5207, GA5209**.
- Üreticinin katalogunda bobin malzemesi **bakır veya alüminyum**, nüve ailesi **hava aralıklı silisli sac** olarak açıklanır; **stok koduna özgü sarım metodu, tur sayısı, reçete, nüve laminasyonu ve bobin kalıbı yoktur**.

## Karar gerektiren üç teknik ayrım
1. **SRM 7,5 / GA5105 (904 adet):** Kaynak GA5106 Bara ile kıyaslamış; GA5105 Pabuç. Mevcut GA5104 Pabuç olsa da 5/7,5 kVAr ürünlerin iç yapı eşitliği kanıtlanmadı. **GA5105 fiziksel inceleme ihtiyacı koşullu**; öncelik: GA5104'e ait nüve/kalıp ve bağlantı çizimi ile karşılaştırma.
2. **SRT 5–7,5 / GA5205–GA5206 (352 adet):** Kaynak GA5207 Bara ile kıyaslamış; ikisi de Klemens. Seçilen GA5204 klemens ama daha küçük güç/gövde. **Orta SRT klemens grubu için GA5206 veya GA5205 numunesi koşullu olarak değerlendirilmeli**; tek bir kodun ikisini temsil etmesi ayrıca doğrulanmalı.
3. **SRT 20–25 / GA5210–GA5211 (210 adet):** Kaynak GA5211 referansına dayanıyor ama 9 numunede GA5211 yok. GA5212 aynı Bara/M10 bağlantıya sahip olsa da 50 kVAr ve gövdesi daha büyük. **GA5211 için fiziksel numune ihtiyacı koşullu olarak değerlendirilmeli**; 20/25 grubunun iç çekirdek ve kalıp uyumu kanıtlanmalı.

Ayrıca **GA5004 / GA5006 (274 adet)** üreticinin kod bazlı 2026 listesinde yok; üretici kimlik/teknik föy doğrulaması olmadan 9 numune ile karşılandığı varsayılmaz.

## Ürün bazında 25 satır
| Kod | Model | Yıllık adet | Bağlantı | Montaj | Kaynak kıyas kodu | Denetim sınıfı | İncelenecek konu |
|---|---|---:|---|---|---|---|---|
| GA5002 | SVC-R 1.5 | 13.462 | Klemens | M8 | GA5002 | İlk fiziksel numune | İlk fiziksel numune. SVC-R iç yapısının diğer güçleri temsil ettiği henüz doğrulanmadı. |
| GA5003 | SVC-R 3.0 | 6.502 | Klemens | M8 | GA5002 | Katalog/çizim kıyası | SVC-R / Klemens M8; güç ve gövde ölçüsü farklı. GA5002 ile iç yapı ortaklığı doğrulanmadı. |
| GA5001 | SVC-R 1.0 | 3.914 | Klemens | M8 | GA5002 | Katalog/çizim kıyası | SVC-R / Klemens M8; aynı aile ve bağlantı, farklı güç/ölçü. İç nüve ve sarım eşitliği doğrulanmadı. |
| GA5006 | SVC-R 10.0 | 162 | Doğrulanmadı | — | — | Üretici kodu doğrulanmadı | SVC-R 10.0, Grup Arge 2026/12 listesinde aynı kodla doğrulanmadı; üretici teknik çizimi gerekli. |
| GA5004 | SVC-R 5.0 | 112 | Doğrulanmadı | — | — | Üretici kodu doğrulanmadı | SVC-R 5.0, Grup Arge 2026/12 listesinde aynı kodla doğrulanmadı; üretici teknik çizimi gerekli. |
| GA5102 | SRM 1.5 | 832 | Klemens | M8 | GA5002 | Fiziksel kıyas numunesi | SRM tek faz Klemens M8. GA5002 aynı güç/akım/L olsa da ölçü ve kütle farklı; fiziksel kıyas korunmalı. |
| GA5103 | SRM 3.0 | 810 | Klemens | M8 | GA5102 | Katalog/çizim kıyası | SRM / Klemens M8; daha büyük güç/gövde. Fiziksel sarım/nüve ortaklığı kanıtlanmadı. |
| GA5101 | SRM 1.0 | 172 | Klemens | M8 | GA5102 | Katalog/çizim kıyası | SRM / Klemens M8; farklı güç/ölçü. Bobin ve nüve eşdeğerliği doğrulanmadı. |
| GA5104 | SRM 5.0 | 2.632 | Pabuç | M8 | GA5104 | Fiziksel kıyas numunesi | SRM Pabuç M8 grubunun fiziksel numune adayı; 7,5 kVAr sınıfına otomatik taşınamaz. |
| GA5106 | SRM 10.0 | 4.178 | Bara | M8 | GA5106 | İlk fiziksel numune | SRM Bara M8; 10 kVAr ilk numune. Üst güç sınıfı ve GA5108 tasarım eşitliği teyit bekliyor. |
| GA5105 | SRM 7.5 | 904 | Pabuç | M8 | GA5106 | Kaynakta bağlantı grubu farklı | Kaynak kıyası GA5106 Bara, GA5105 Pabuç. Mevcut GA5104 Pabuç ile de 5/7,5 kVAr iç tasarım eşitliği doğrulanmalı. |
| GA5108 | SRM 20.0 | 342 | Bara | M8 | GA5108 | Fiziksel kıyas numunesi | SRM Bara M8; 20 kVAr fiziksel kıyas adayı. 2023 katalogda aynı kod yok. |
| GA5107 | SRM 15.0 | 54 | Bara | M8 | GA5108 | Katalog/çizim kıyası | SRM Bara M8; 15 kVAr. 2023 katalogda bu model yok; 2026 listesi üzerinden kıyas, nüve/bobin onaysız. |
| GA5204 | SRT 2.5 | 314 | Klemens | M8 | GA5204 | Fiziksel kıyas numunesi | SRT Klemens M8 küçük güç sınıfı; 5/7,5 kVAr büyük Klemens tasarımını kanıtlamaz. |
| GA5203 | SRT 1.5 | 168 | Klemens | M8 | GA5204 | Katalog/çizim kıyası | SRT Klemens M8; daha küçük güç/ölçü. İç yapı ortaklığı kanıtlanmadı. |
| GA5202 | SRT 1.0 | 108 | Klemens | M8 | GA5204 | Katalog/çizim kıyası | SRT Klemens M8; daha küçük güç/ölçü. İç yapı ortaklığı kanıtlanmadı. |
| GA5201 | SRT 0.5 | 52 | Klemens | M8 | GA5204 | Katalog/çizim kıyası | SRT Klemens M8; daha küçük güç/ölçü. İç yapı ortaklığı kanıtlanmadı. |
| GA5207 | SRT 10.0 | 304 | Bara | M8 | GA5207 | Fiziksel kıyas numunesi | SRT Bara M8 orta güç örneği; GA5205/06 Klemens bağlantılı olduğundan doğrudan temsil etmez. |
| GA5205 | SRT 5.0 | 296 | Klemens | M8 | GA5207 | Kaynakta bağlantı grubu farklı | Kaynak kıyası GA5207 Bara, ürün GA5205 Klemens. GA5204 küçük Klemens gövdesi de eşdeğer değil; yeni inceleme gerekli. |
| GA5206 | SRT 7.5 | 56 | Klemens | M8 | GA5207 | Kaynakta bağlantı grubu farklı | Kaynak kıyası GA5207 Bara, ürün GA5206 Klemens. 5/7,5 kVAr orta Klemens sınıfı fiziksel örnek ihtiyacı değerlendirilmeli. |
| GA5209 | SRT 15.0 | 120 | Bara | M8 | GA5209 | Fiziksel kıyas numunesi | SRT Bara M8; 15 kVAr fiziksel numune. 12,5 kVAr için yalnız katalog kıyası. |
| GA5208 | SRT 12.5 | 14 | Bara | M8 | GA5209 | Katalog/çizim kıyası | SRT Bara M8 12,5 kVAr; 15 kVAr GA5209 ile çizim/katalog kıyası, fiziksel eşitlik kanıtlanmadı. |
| GA5211 | SRT 25.0 | 120 | Bara | M10 | GA5211 | Kaynak referansı fiziksel numunede yok | SRT 25 kVAr Bara M10. Kaynak referans kendisi, fakat fiziksel numune seçilmemiş; 20/25 kVAr ara sınıfı teyit edilmeli. |
| GA5210 | SRT 20.0 | 90 | Bara | M10 | GA5211 | Kaynak referansı fiziksel numunede yok | Kaynak GA5211 ile kıyas öneriyor; GA5211 9 numune içinde yok. GA5212 M10 olsa da 50 kVAr ve gövde farklı. |
| GA5212 | SRT 50.0 | 54 | Bara | M10 | GA5212 | İlk fiziksel numune | SRT 50 kVAr Bara M10 ilk numune; GA5210/11 daha küçük M10 tasarımını aynı nüve/sarım olarak kanıtlamaz. |

## Satın alma için güvenli karar ve iş akışı
- **Şimdilik 9 numune önerisi korunur**; sırf dış ölçüler, akım veya bağlantı biçimi benziyor diye azaltılmaz.
- Her numune için üreticiden imalat çizimi, 1 veya 3 bobinli gerçek yapı, çekirdek kesiti/istif kalınlığı, bakır/alüminyum seçimi, tel/folyo kesitleri, tur sayısı, bobin izolasyon ve emprenye reçetesi, bobin kalıbı ve montaj fişi istenir.
- Özellikle **GA5105, GA5205/GA5206 ve GA5211** için üreticiden ortak nüve/sarım/kalıp teyidi alınır. Belgeler bu üç boşluğu kapatmazsa ilave fiziksel numune kararı yeniden verilir; **9'dan 10–12'ye çıkmak henüz onaylanmış değildir**.
- Şönt ürünlerinin sarım/emprenye/fırın yatırımı için kesin kapasite ve makina adedi, bu fiziksel tasarım bilgileri olmadan hesaplanamaz. Üretim adedinden tek başına makine kapasitesi çıkarılamaz.

## Uygulama kontrolü
`plan2027-samples.js` üzerinden 25 ürün için denetim notu gösterilir; 3 ilk ve 6 fiziksel kıyas ayrı etiketlenir. `shunt-sample-review-2026.js` 25 kaydın ve alt sınıf adetlerinin otorite kayıt katmanıdır. Numune önerileri, 2027 üretim planı ve Harmonik teknik verileri **değiştirilmemiştir**.
