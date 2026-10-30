> **KAYNAK ÇELİŞKİSİ UYARISI — 30.10.2026:** Bu rapordaki '2026/12 listesiyle düzeltildi' olarak sunulan sayısal ölçü/ağırlık/bağlantı değerleri, doğrudan açılan [Grup Arge /fl/tr 2026/12 PDF s.17](https://www.gruparge.com/fl/tr#page=17) ile **uyuşmuyor** (örn. GA5002 PDF 150×125×121/9 kg, bu rapor 150×125×110/8 kg; GA5205 PDF Pabuç, bu rapor Klemens). Bu belgenin verileri ve ilgili `shunt-official-2026.js` override'ı, revizyon kaynağı açıklığa kavuşturulmadan **makine yatırımı/kazan/fırın boyutlandırması için onaylı veri kabul edilmez**. Yeni ürün inceleme amacı ve 25 ürün kontrolü: [SONT_MAKINE_YATIRIMI_URUN_SECIMI_20261030.md](SONT_MAKINE_YATIRIMI_URUN_SECIMI_20261030.md). Eski karşılaştırma tarihseldir.

# Grup Arge — Şönt Reaktör 25 Ürün Teknik Kaynak Karşılaştırması ve Düzeltme

Denetim tarihi: **30 Ekim 2026**. Kapsam: **25 Şönt ürün**, **35.772 adet/yıl**. **Harmonikler kapsam dışı ve değiştirilmedi.**

## Kaynak önceliği
1. **Grup Arge fiyat listesi 2026/12**, basılı sayfa **17**, resmi [PDF](https://www.gruparge.com/fl/tr#page=17). Ürün koduna göre güç, akım, L, dış ölçü, kg, bağlantı tipi, ayak montaj cıvatası ve USD liste fiyatı.
2. **Grup Arge 2023 ürün kataloğu**: [PDF](https://www.gruparge.com/wp-content/uploads/2023/04/grup-arge-urun-katalogu.pdf), şönt teknik özellikler ve çizim sayfaları 31–33. 21 ortak modelde ölçü, ağırlık, akım, L ve bağlantı aynı; GA5107/GA5108 bu katalogda yok, 2026 listesi esas alındı.
3. Üreticinin [web Şönt ürün sayfası](https://www.gruparge.com/urun/sont-reaktorleri/) bazı modellerde daha farklı/eskimiş ölçü ve ağırlık veriyor. Tarihli PDF ve çizim aynı olduğundan, bu web sayfası yeni sayısal alanlar için seçilmedi.
4. Eski uygulama Excel matrisiyle farklar satır bazında aşağıda. Üreticinin dış ölçülerin değişebileceği uyarısı nedeniyle fiyat listesi boyutlarının **somut satınalma revizyonu / imalat BOM ölçüsü olduğu iddia edilmez**.

## Kontrol sonucu
- **23/25** ürünün teknik satırı 2026/12 üretici listesinde mevcut. **GA5004 ve GA5006** için aynı kodla teknik satır bulunamadı: **değer türetilmedi, doğrulama gerekli**.
- Eski matrise göre **23/23 ölçü**, **16/23 ağırlık**, **3/23 gerçek bağlantı tipi** farklı; **13/23 bağlantı metni** ayrıca değişir (M8/M10 ayak cıvatası ayrı alana taşındığı için). Güç farkı 0; akım farkı 0; L farkı 0.
- Ürün katalogunda ayrıca 21 ortak model için **nominal kablo kesiti** ve teknik çizimlerde varsa **D/E ölçüleri** alındı; SRM 1.0 için çizimin D/E alanları kaynakta boş olduğundan sayısal değer türetilmedi. GA5107/GA5108 katalogda yer almadığından bunların kablo ve D/E değerleri çıkarılmadı. Genel katalogdaki hava aralıklı demir nüve, Al/Cu sarım olasılığı ve sınıf F izolasyon yalnızca **ürün ailesi genel bilgisi** olarak ürün föyüne yazıldı; modelin gerçek malzeme/izolasyon BOM'u olarak kabul edilmedi.
- Güncellenen uygulama alanları: `p.kg`, `p.faz`, `p.guc`, `p.akim`, `p.L`, `p.olcu`, `p.baglanti` ve bunların `tamKayit` içindeki teknik eşleri. 2026 liste fiyatı (USD), ayak cıvatası, resmî PDF referansı ve orijinal kaynağa göre revizyon notu eklenmiştir.
- 45.088 genel yıllık adet, 35.772 Şönt adedi, ürün kimlikleri, üretim ayları, numune önerileri, sıralama ve tarayıcıda kaydedilen kullanıcı planı **değiştirilmedi**. Kaynak sıkıştırılmış arşiv korunur; her uygulama ekranının veri yüklemesinde ortak `shunt-official-2026.js` düzeltme katmanı devreye girer.

## 25 ürünün tamamı

| Kod | Model | Yıllık adet | Kanıt | Eski ölçü (mm) | Düzeltilen ölçü (mm) | Eski kg | Düzeltilen kg | Eski bağlantı | Bağlantı tipi | Ayak cıvata | kVAr | A | L(mH) | Liste USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GA5002 | SVC-R 1.5 | 13462 | 2026 fiyat listesi + 2023 katalog | 150×125×121 | 150×125×110 | 9.0 | 8 | Klemens | Klemens | M8 | 1.5 | 6.52 | 112.25 | 86 |
| GA5003 | SVC-R 3.0 | 6502 | 2026 fiyat listesi + 2023 katalog | 192×164×131 | 192×160×134 | 15.0 | 14.5 | Klemens | Klemens | M8 | 3 | 13.04 | 56.12 | 163 |
| GA5001 | SVC-R 1.0 | 3914 | 2026 fiyat listesi + 2023 katalog | 120×105×103 | 120×100×102 | 5.0 | 5 | Klemens | Klemens | M8 | 1 | 4.34 | 168.38 | 70 |
| GA5006 | SVC-R 10.0 | 162 | Katalog doğrulanmadı | — |  | — |  | — |  | — | — | — | — | — |
| GA5004 | SVC-R 5.0 | 112 | Katalog doğrulanmadı | — |  | — |  | — |  | — | — | — | — | — |
| GA5102 | SRM 1.5 | 832 | 2026 fiyat listesi + 2023 katalog | 150×125×121 | 150×125×120 | 9.0 | 9.5 | Klemens | Klemens | M8 | 1.5 | 6.52 | 112.25 | 99 |
| GA5103 | SRM 3.0 | 810 | 2026 fiyat listesi + 2023 katalog | 192×164×136 | 192×160×144 | 16.0 | 17.5 | Klemens | Klemens | M8 | 3 | 13.04 | 56.12 | 192 |
| GA5101 | SRM 1.0 | 172 | 2026 fiyat listesi + 2023 katalog | 120×105×111,5 | 150×125×105 | 6.0 | 6.5 | Klemens | Klemens | M8 | 1 | 4.34 | 168.38 | 93 |
| GA5104 | SRM 5.0 | 2632 | 2026 fiyat listesi + 2023 katalog | 210×315×145 | 210×270×180 | 20.0 | 20 | Pabuç M8 | Pabuç | M8 | 5 | 21.7 | 33.7 | 272 |
| GA5106 | SRM 10.0 | 4178 | 2026 fiyat listesi + 2023 katalog | 255×315×155 | 260×330×200 | 32.0 | 34 | Bara M8 | Bara | M8 | 10 | 43.4 | 16.83 | 480 |
| GA5105 | SRM 7.5 | 904 | 2026 fiyat listesi + 2023 katalog | 210×260×165 | 210×280×210 | 26.0 | 27 | Pabuç M10 | Pabuç | M8 | 7.5 | 32.6 | 22.45 | 368 |
| GA5108 | SRM 20.0 | 342 | 2026 fiyat listesi | 290×365×205 | 290×380×250 | 62.0 | 58 | Bara M10 | Bara | M8 | 20 | 86.9 | 8.4 | 863 |
| GA5107 | SRM 15.0 | 54 | 2026 fiyat listesi | 290×365×185 | 290×380×220 | 50.0 | 47 | Bara M10 | Bara | M8 | 15 | 65.2 | 11.2 | 751 |
| GA5204 | SRT 2.5 | 314 | 2026 fiyat listesi + 2023 katalog | 215×265×144 | 240×225×100 | 17.0 | 17 | Klemens | Klemens | M8 | 2.5 | 3.61 | 203.72 | 258 |
| GA5203 | SRT 1.5 | 168 | 2026 fiyat listesi + 2023 katalog | 192×164×144 | 180×175×115 | 14.5 | 14.5 | Klemens | Klemens | M8 | 1.5 | 2.17 | 339.5 | 192 |
| GA5202 | SRT 1.0 | 108 | 2026 fiyat listesi + 2023 katalog | 150×127×130 | 180×175×85 | 11.5 | 11.5 | Klemens | Klemens | M8 | 1 | 1.44 | 509 | 148 |
| GA5201 | SRT 0.5 | 52 | 2026 fiyat listesi + 2023 katalog | 150×125×105 | 150×150×72 | 8.0 | 8 | Klemens | Klemens | M8 | 0.5 | 0.72 | 1018.6 | 123 |
| GA5207 | SRT 10.0 | 304 | 2026 fiyat listesi + 2023 katalog | 380×315×155 | 370×330×190 | 48.0 | 48 | Pabuç M10 | Bara | M8 | 10 | 14.43 | 50.92 | 654 |
| GA5205 | SRT 5.0 | 296 | 2026 fiyat listesi + 2023 katalog | 325×260×135 | 295×255×170 | 29.0 | 27 | Pabuç M8 | Klemens | M8 | 5 | 7.22 | 101.86 | 384 |
| GA5206 | SRT 7.5 | 56 | 2026 fiyat listesi + 2023 katalog | 325×260×155 | 295×255×180 | 38.0 | 39 | Pabuç M8 | Klemens | M8 | 7.5 | 10.83 | 67.9 | 472 |
| GA5209 | SRT 15.0 | 120 | 2026 fiyat listesi + 2023 katalog | 380×315×175 | 390×330×220 | 63.0 | 67 | Bara M8 | Bara | M8 | 15 | 21.65 | 33.95 | 780 |
| GA5208 | SRT 12.5 | 14 | 2026 fiyat listesi + 2023 katalog | 380×315×165 | 390×330×210 | 55.0 | 57 | Bara M8 | Bara | M8 | 12.5 | 18.04 | 40.75 | 708 |
| GA5211 | SRT 25.0 | 120 | 2026 fiyat listesi + 2023 katalog | 460×365×185 | 460×380×230 | 93.0 | 96.5 | Bara M10 | Bara | M10 | 25 | 36.08 | 20.37 | 1370 |
| GA5210 | SRT 20.0 | 90 | 2026 fiyat listesi + 2023 katalog | 460×365×175 | 460×380×220 | 82.0 | 80 | Bara M10 | Bara | M10 | 20 | 28.86 | 25.46 | 1220 |
| GA5212 | SRT 50.0 | 54 | 2026 fiyat listesi + 2023 katalog | 530×420×260 | 520×430×290 | 173.0 | 170 | Bara M10 | Bara | M10 | 50 | 72.2 | 10.18 | 2250 |

## İmalat için henüz doğrulanmayanlar
- Fiziksel bobin adedi (1B/3B çizimden türetilmiş ön kabul kesin BOM değildir), nüve tipi, sarım tel/folyo biçimi, sarım süresi, izolasyon, vernik/emprenye, gerçek montaj ölçü toleransları.
- GA5004 ve GA5006 ürün kodlarının geçerli imalat/tedarik referansı ve kesin teknik föyü.
- SRT 20/25 kVAr için GA5211 kıyas referansı numune adayları arasında bulunmuyor; **ayrı numune alınması gerektiği henüz doğrulanmış değildir**.
- Liste fiyatları **USD fiyat listesi değerleridir**, teklif/iskonto/güncel alım fiyatı değildir.

## Test ve kontrol
- Kaynak Excel'de 135 satır, 25 Şönt, 110 Harmonik; pozitif miktarlı 133 ürün vardır.
- Aile toplamı 35.772 Şönt + 9.316 Harmonik = 45.088 adet.
- Üretim planı, aylık teknik detay, numune ana tablosu, ürün teknik föyü ve eski plan ekranı aynı teknik düzeltme kaynağına bağlandı.
