# 2027 ana ekran: düzenlenebilir 12 aylık üretim matrisi (30.10.2026)

**Güncel giriş:** \`index.html\`. Şönt ve Harmonik üretim planının 133 aktif ürün / 45.088 adet içeren 12 aylık matrisi doğrudan açılır. Ürünler ilk üretim ayı ve aynı aylarda üretim paternine göre alt alta sıralanır. Kaynak teknik bilgiler \`data-packed.js\`, onaylanan aylık üretim planı ve bobin ön değerleri \`plan2027-data.js\` üzerinden gelir.

- **Grup renkleri (30.10.2026):** Aynı ürün ailesinde (**Şönt / Harmonik**) aynı üretim ayları kombinasyonunu paylaşan ürünlerin G1, G2... etiketi ve miktar hücresi rengi aynıdır. Grup için ayrı başlık satırı yoktur. Ürün satırı yukarı/aşağı taşındığında grup rengi sabit kalır. Bir ürünün üretim ayları değişirse yeni kombinasyonun grubuna geçer. Grup kimlikleri otomatik kayıtta ve JSON yedeğinde ek alan olarak korunur (önceki v2 yedekler de açılır). En büyük altı grubun döngüsü tablonun üzerinde kısa açıklamalarla gösterilir; diğer gruplar isteğe bağlı açılır.
- **Ürün kodu/model bağlantısı:** \`urun.html?id=<benzersiz ürün kimliği>\` ile mevcut ürüne özgü teknik föy açılır; aynı kod altında farklı açıklama bulunan kayıtlar kaybolmaz.
- **Satır sıralaması:** Her ürün satırının solundaki **↑ / ↓** okları satırı bir adım hareket ettirir (mobilde de çalışır). **⠿ tutma kolundan** başka bir ürün satırının üstüne/altına sürükleyerek istediğiniz konuma yerleştirebilirsiniz. Satır taşıma ürün miktarını veya üretim ayını değiştirmez. Ürün sırası tarayıcıda saklanır; CSV çıktısı da aynı sıra ile oluşturulur. **Geri al** son satır veya adet değişikliğini geri alır; **Başlangıç planı** miktarlarla birlikte sırayı da ilk haline döndürür.
- **Adet hücresi:** Kaynak ay, hedef ay ve aktarılacak miktarı seçerek yıllık toplamı koruyan üretim kaydırması; aynı ürün satırının başka ay hücresine sürükle-bırak da mümkün.
- **Setup kuralı:** Ocak/Şubat, Nisan/Mayıs, Temmuz/Ağustos, Ekim/Kasım yalnız Şönt; Mart/Haziran/Eylül/Aralık yalnız Harmonik. Çapraz aile taşıması engellenir.
- **Hareket geçmişi:** Son işlemi geri al, başlangıç planına dön, düzenlenmiş planı Excel'de açılabilen UTF-8 CSV olarak dışarı aktar.
- **Otomatik kayıt:** Her üretim aktarımı ve ürün satırı sıralaması \`localStorage\` içine anında kaydedilir. Aynı Chrome profili, aynı \`file://\` dosya yolu ve silinmemiş site verisiyle tekrar açıldığında miktar/satır sırası geri yüklenir.
- **Kaydet:** Üstteki \`Kaydet\` düğmesi güncel planı kaydeder, ek olarak \`Son kayıtlı plan\` için ayrı bir kayıt noktası oluşturur. Düzenleme/yanlış sıfırlama sonrasında bu düğmeyle son elle kaydedilmiş noktaya dönülebilir.
- **Plan yedeği (.json) / Yedeği yükle:** Planı tüm ürünlerin aylık miktarları, kimlikleri ve **elle ayarlanmış sıra bilgisi** dahil dosyaya indirin; başka bilgisayarda veya tarayıcı verisi silinince yükleyin. \`CSV indir\` rapor içindir, **geri yükleme dosyası değildir**.
- **Güncelleme güvenliği:** Önceki kayıttaki ürün kimliği/adedi değiştiğinde kayıt dosyası **sessizce silinmez**; eşleşebilen ürünler okunur, uyumsuz eski ham plan ayrıca yerel kurtarma anahtarında korunur ve ekranda uyarı gösterilir. Ürün listesinin değiştiği durumlarda kapsamlı veri aktarımı ayrıca kontrol gerektirir.
- **Kayıt sınırı:** Bu sürüm **Neon/GitHub sunucusuna merkezi kayıt yapmaz**. Tarayıcıya/cihaza özgüdür; özel gezinti, farklı tarayıcı profili, tarayıcı verilerini silme veya \`index.html\` dosyasını farklı bir yola taşıma, otomatik geri yüklemeyi engelleyebilir. Güvenli koruma için her önemli plan revizyonundan sonra JSON yedeğini ayrı yerde saklayın.
- **Bobin bilgisi:** \`(nB*)\` etiketleri tip çizimi ön verisidir. Gerçek bobin üretim reçetesiyle doğrulanmadı; bilinmeyenler **?**.
- **Eski otomatik parti senaryosu:** \`legacy.html\` üzerinden hâlâ erişilebilir. 2027 ana matrise bu eski senaryonun ay seçimleri uygulanmaz.

\`index.html\`, \`plan2027.js\`, \`plan2027.css\`, \`data-packed.js\`, \`plan2027-data.js\`, \`urun.html\`, \`urun.js\` aynı dizinde bulunmalı. Güncel Chrome/Edge önerilir (\`DecompressionStream\` desteği gerekir).

---

# Şönt & Harmonik Üretim Planlama — simulation3

Bu dizin, SIM3 Windows otomasyonunun ana dosyalarını değiştirmeyen bağımsız bir tarayıcı uygulamasıdır. Hazırlık amacı **makine yatırımı için yıllık üretim takvimi ve parti yüklerini görünür kılmaktır**. Kesin makine kapasitesi hesabı değildir.

## Açma

1. Bu dizindeki `index.html`, `style.css`, `app.js`, `data-packed.js` dosyalarını aynı klasörde bulundurun.
2. Windows'ta `index.html` dosyasını Chrome / Edge ile açın. İnternet bağlantısı gerekmez.
3. Takvimdeki renkli üretim miktarına basın: o ayın ürünleri aşağıda listelenir. **Tüm ürünler tek tabloda alt alta görünür. Şönt kaynağındaki 19, harmonik kaynağındaki 22 özgün alanın tamamı aktarılmıştır.** Üretim ve miktarın yanında kıyas kodu/önerisi, numune/kontrol, kıyas nedeni, yapı referansı, standart/varyant, katalog/teknik veri durumu, inceleme eksikleri, kaynak ve kayıt bilgisi dahil 37 sütun vardır. Tabloda yatay/dikey kaydırma, ürün arama ve şönt/harmonik filtresi vardır; ayrı ürün detayı açılmaz.

## Temel kurallar

| Yıllık miktar | Parti sayısı | Üretim aralığı |
|---:|---:|---|
| 1–200 | 1 | Tek sefer |
| 201–500 | 2 | 6 ay |
| 501–1.000 | 3 | 4 ay |
| 1.001+ | 4 | 3 ay |
| 0 | 0 | Üretim dışı |

- İlk açılışta **1 partili ürünlerin tamamı Haziran** ayında, **2 partili ürünlerin tamamı Mart/Eylül** aylarında yer alır. Bu aylar seçeneklerden birlikte değiştirilebilir.
- **Plan A (dengeli dağılım)**: 3 ve 4 partili ürünlerin başlangıç fazlarını adet bazlı dengelemeye çalışır; referans gösterilen GA5102 ve GA5002 ürünlerinin ayları korunur.
- **Plan B (ortak başlangıç)**: Tüm 3 partilileri Mart/Temmuz/Kasım; 4 partilileri Ocak/Nisan/Temmuz/Ekim aylarında başlatır.
- Yıllık toplam **45.088 adet**, üretimde **133 satır**, üretim dışı **2 satır**, yıllık **175 parti**.
- Ürün matrisinde aynı stok kodu farklı model açıklamasıyla tekrar edebiliyor; bunlar birleştirilmeden satır bazında tutulur.
- **Veriler:** şönt matrisi 25 satır, harmonik matrisi 110 satır. Veri paketi `data-packed.js` içinde sıkıştırılmış olarak bulunur, yeniden veri indirme gerekmez. Kaynak teknik durumları ve uyarılar tablodaki ilgili sütunlarda korunur.

## Yatırım çalışması için henüz gereken veriler

Sarım işlemi süreleri, sarım tipi/iletken kesiti, nüve ve bobin boyutları, impregnasyon yöntemi (VI/VPI), fırın raf/yük düzeni ve proses sıcaklık/süre reçeteleri doğrulanmadan **makine adedi veya kurutma kapasitesi önerisi** yapılmamalıdır.

## Kontrol

`node test_app.js` komutuyla paket yükleme ve toplam sayım testi yapılabilir (Node.js 18+). Tarayıcı için son kullanıcıya Node.js gerekmez.

## Gruplama ve sıralama (ürün tablosu)

- **Grupla:** Şönt / Harmonik (başlangıç görünümü), ürün ailesi, aylık parti adedi aralığı, birim ağırlık aralığı, en büyük dış ölçü aralığı veya gruplama yok.
- **Sırala:** bu ay üretilecek adet, yıllık adet, birim ağırlık, toplam parti ağırlığı, dış ölçünün en büyük kenarı, yaklaşık geometrik dış hacim, güç veya stok kodu. Küçükten büyüğe / büyükten küçüğe yönü seçilebilir.
- Her grup başlığında **ürün sayısı, üretim adedi, bilinen toplam parti kg** ve ağırlığı eksik ürün sayısı yer alır. Ağırlık ve ölçüsü eksik olan ürünler ayrıca *Bilgisi olmayanlar* grubuna alınır; sıralamada her iki yönde de sona yerleştirilir.
- Gruplama ve sıralama yalnızca liste görünümünü etkiler, 45.088 adet/yıl ve üretim ayları değişmez. Aralıklar yatırım amacıyla geçici inceleme sınıflarıdır; malzeme türü, fiilî fırın yerleşimi ve sarım çevrimi bunlardan çıkarılamaz.

## İsteğe bağlı sütunlar (çoklu tik)

- Ürün listesinin üstündeki **Sütun ekle / çıkar (X/32)** açılır menüsü kaynak matrisleri ve üretim hesaplarındaki 37 sütunu gruplar halinde gösterir. İstenenler tiklenir; seçili olmayanlar tabloda gizlenir. Her tık anında aynı tabloyu günceller.
- **Stok kodu** ve **Ürün modeli** sabit kalan iki sütundur; diğer 35 sütun ayrı ayrı eklenip çıkarılabilir.
- **37 sütunun tamamı** ve **Yalnızca kod ve model** hazır kontrolleri, sütun adı araması ve mevcut hızlı **Sütun grubu** şablonları vardır. Özel seçim ay veya üretim partisi değiştiğinde korunur.
- Sütunları gizlemek veya göstermek veri paketini ve üretim planını değiştirmez; CSV dışa aktarımı tam 37 sütunu korur.


## Sütun başlığına tıklayarak sıralama ve çoklu filtre
- Tabloda **herhangi bir sütun başlığına** basılması grupların içindeki ürünleri o sütuna göre sıralar; ikinci basış artan/azalan yönünü değiştirir. Aktif başlık ▲ / ▼ simgesiyle gösterilir. Boş değerler her iki yönde de sondadır. Ölçü sütunu en büyük dış kenarı esas alır.
- Üst araç çubuğundaki **Ek filtreler** panelinden sınırsız sayıda sütun koşulu eklenebilir. 32 görünür sütunun tamamı filtrelenebilir; ayrıca en büyük dış ölçü ve yaklaşık geometrik hacim filtre alanı bulunur.
- Sayısal koşullar: >, ≥, <, ≤, eşit, eşit değil, boş, dolu. Metin koşulları: içerir, içermez, eşit, eşit değil, ile başlar, boş, dolu. Ondalık değerler Türkçe virgülle yazılabilir (örn. 14,5).
- Farklı koşullar **VE (hepsi)** veya **VEYA (herhangi biri)** yöntemiyle birleştirilir. Ürün grubu seçimi ve genel arama ek filtrelerle VE olarak çalışır.
- Filtreler yalnızca ürünlerin listelenmesini etkiler; aylık/yıllık üretim planı, ham veriler ve tüm sütunları içeren CSV dışa aktarımı değişmez.

## Resmî teknik datasheet PDF'leri (28.10.2026)

- Ürün tablosundaki **Resmî datasheet (grup PDF)** sütunu, her Şönt ürünü için [Şönt Reaktör Datasheet](https://www.gruparge.com/wp-content/uploads/2025/05/SONT-REAKTORU-DATASHEET.pdf); her Harmonik ürünü için [Harmonik Filtre Datasheet](https://www.gruparge.com/wp-content/uploads/2025/05/HARMONIK-FILTRE-DATASHEET.pdf) bağlantısını gösterir.
- Bu PDF'ler üreticinin **ürün grubu** dokümanlarıdır. Her stok kodunun kendisine ait ayrı PDF olduğu veya her modelin mevcut sayfalarda birebir yer aldığı doğrulanmış **değildir**. Bağlantı linkine göre doğru teknik değer olduğu varsayılmamalıdır.
- Eski kaynak bağlantısı sütunu korunur; yeni sütun tıkla-sırala, çoklu filtre, sütun tik seçimi ve CSV indirmeye dahildir. Toplam **37 sütun** vardır.
- 135 satırın 92'sinde daha önce ürün bazlı olmayan genel site URL'si, 41'inde yalnızca CSV kaynağı, 2'sinde boş kaynak bağlantısı vardı. Resmî kategori PDF bağlantısı bu eksikliği kısmen giderir; ürün bazlı model/eşleşme denetimi ayrı gereklidir.

## Resmî 2026/12 fiyat listesinin teknik verileri ile 135 ürün denetimi (28.10.2026)

**Resmî kaynak:** https://www.gruparge.com/fl/tr (2026/12 sürüm etiketli fiyat listesi, PDF s.17, 30–32). Ayrıca 2025 tarihli iki grup datasheeti ayrı tutulmaktadır.

- **92/135 kayıt:** aynı stok kodu resmî 2026/12 listesinde var; matrisin **akım, endüktans, ölçüler, ağırlık ve bağlantı** alanları beşer beşer eşleşti (460/460 alan). Bunun 23'ü Şönt, 69'u Harmonik satırı. Üç satırın ürün modeli uzun açıklama içine gömülüdür, doğru model açıklamada bulunur.
- **43/135 kayıt:** listede aynı stok kodu bulunamadı. 29 G/GG varyantı, 12 `GA5ÖZELHARM` açıklamalı satır ve iki SVC modelidir (`GA5004`, `GA5006`). Bunlar toplam **1.312 adet/yıl**; doğrulama için üreticiye sorulmalıdır. Liste dışında olmak ürünün üretilmediğini göstermez.
- **Kaynak sürüm farkı:** 2025 datasheet çizimleri ile 2026/12 tablosundaki bazı A/B/C ve G/Y/D ölçüleri farklı. 2026/12 katalog verileri matristeki ölçülerle uyumludur. Belge tarihleri arasında karşılaştırma yapmadan tek bir kesin tasarım ölçüsü kabul edilmemelidir.
- Uygulamaya **2026/12 teknik doğrulama**, **kontrol notu**, **kaynak PDF sayfası**, **resmî 2026/12 teknik liste** sütunları eklendi. Bunlar çoklu tik, sıralama ve filtreleme ile kullanılabilir. Eski 2025 **grup datasheeti** bağlantısı korunmuştur.
- Sütun etiketlerinin `5/5 teknik alan uyumlu` olması ilgili 5 **katalog alanının** eşleşmesini ifade eder. Gerçek üretim malzemesi, sarım, impregnasyon ve proses çevrimlerinin doğrulandığı anlamına gelmez.
- **İşlem:** Ham ürün verisi, miktar, üretim kuralları ve raporlanan değerler değiştirilmedi; 2026/12 bilgileri kontrol katmanı olarak eklenmiştir.

## 2026 resmî liste + güncel yayımlanan katalogla ikinci tur doğrulama (28.10.2026)
- Üreticinin resmî [2026 fiyat listesi](https://www.gruparge.com/fl/tr) 17, 30–32. sayfalarındaki ürün kodları yeniden kontrol edildi. [Ürün katalogları](https://www.gruparge.com/dokumanlar/kataloglar/) bölümünde halka açık bağlantı 2023 ürün kataloğuna işaret eder; 2026 fiyat listesi tercih edildi.
- **92 ürün satırı / 43.776 yıllık adet:** doğrudan stok kodu eşleşmesi ve akım, L, ölçü, ağırlık, bağlantı değerleri matrisle uyumlu.
- **29 G/GG varyant satırı / 860 yıllık adet:** `GAG` veya `GAGG` öneki çıkarıldığında karşılık gelen standart `GA` modelinin resmî 2026 listesinde bulunduğu doğrulandı. **Bu, G/GG varyantının teknik değerlerini doğrulamaz.** Teknik değerler standart baz modelden otomatik kopyalanmaz. Uygulamada varyant için **Standart baz ürün kodu (referans)** ve **Baz ürün teknik liste bağlantısı** gösterilir.
- **14 satır / 452 yıllık adet:** 12 özel üretim (178 adet), SVC-R 5.0 `GA5004` (112 adet) ve SVC-R 10.0 `GA5006` (162 adet) üreticinin mevcut 2026 listesinde aynı stok koduyla bulunamadı.
- 2026 fiyat listesi s.27'de üretici **güçlendirilmiş filtreler** ve **siparişe özel üretimler** için kendisiyle iletişim kurulmasını açıkça istiyor. Bu yüzden özel ürünlere katalogda olmadığı halde standart ürün ölçü/ağırlık bilgisi atanmaz.
- Durumlar üç seviyelidir: **5/5 teknik alan uyumlu / Standart baz model var; varyant doğrulanmadı / Ürün kodu resmî tabloda yok**. 39 bilgi sütununun hepsi filtrelenebilir; üretim planı ve 45.088 adet/yıl değişmedi.

### Ek resmî kaynak: 2024 ürün kataloğu
- Üreticinin İngilizce sitesinde [2024 Product Catalog](https://www.gruparge.com/wp-content/uploads/2024/03/grup-arge-product-catalog-2024.pdf) (96 sayfa) bulunmaktadır. Şönt/harmonik ürün ailelerine ilişkin teknik çizim ve bağlantı şeması karşılaştırması için yardımcı referanstır.
- Bu katalogda **GAG/GAGG varyant stok kodu** ve **GA5004/GA5006** için birebir teknik satır saptanmadı. Bu yüzden 2026 listeye kıyasla özel varyantlar için doğrulama düzeyini yükseltmek uygun değildir.

## Doğrudan ürüne özel teknik föy (28 Ekim 2026)

- Artık **Stok kodu** tıklandığında ya da **Ürüne özel teknik föy** sütunundaki bağlantıya basıldığında `urun.html?id=<ürün_kayıt_id>` açılır. Bu ayrı ekran **yalnızca seçilen tek ürünün** teknik alanlarını gösterir; Şönt/Harmonik toplu broşürüne götürmez.
- `urun.html`, aynı klasördeki `urun.js`, `data-packed.js` ve `style.css` ile internet olmadan çalışır. Ürün ID'si kullanıldığı için aynı stok koduyla farklı kayıtlar birbirine karışmaz. Ürün başlığı, temel elektrik/mekanik bilgiler, yıllık plan, bütün kaynak matris alanları ve üretici kaynağı bulunur.
- İsteğe bağlı **Yazdır / PDF kaydet** düğmesiyle sadece bu tek ürüne ait yerel teknik kart PDF olarak kaydedilebilir. **Bu PDF üreticinin yayımladığı orijinal datasheet değil, uygulamanın kaynak matristen oluşturduğu teknik özet** olduğundan açıkça etiketlidir.
- Üreticinin resmî 2026/12 listesindeki ilgili sayfa ayrı kaynak bağlantısı olarak korunur. Yayınlanmamış özel G/GG varyantları ve katalog dışı ürünler için doğrulanmış üretici PDF'i varmış gibi davranılmaz.
- **Toplam 40 sütun**. Gruplama, tik seçimi, sütun sıralama, çoklu filtre ve yıllık üretim planı korunur.
