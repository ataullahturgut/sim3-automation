# Harmonik ürünleri — kaynak envanteri, 30 Ekim 2026

## Bu dosyanın kapsamı
Şönt 25 ürünün numune denetiminden sonra Harmonik grubuna geçmeden önce başlangıç envanteri oluşturuldu. **Bu dosya henüz Harmonik ürünleri için tam fiyat listesi/katalog teknik alan denetimi veya güncellemesi değildir.** Veri değiştirilmedi.

Kaynak: `Reaktor_Ortak_Uretim_ve_Numune_Matrisi_2026.xlsx`, `simulation3/apps/uretim-plani` ürün verisi. Grup Arge [2026/12 resmî fiyat listesi](https://www.gruparge.com/fl/tr) PDF sayfa 29–31 başlıkları; Grup Arge 2023 [ürün kataloğu](https://www.gruparge.com/wp-content/uploads/2023/11/Grup-Arge-2023-Urun-Katalogu.pdf).

## Gerçek aktif envanter
- Kaynak Excel'de **110 Harmonik satır** vardır; GA5522/GA5523 **0 adet** olduğundan 2027 uygulamasında **108 aktif Harmonik ürün satırı** bulunur.
- Aktif satırlarda **94 farklı stok kodu** vardır; örneğin GA5ÖZELHARM ortak stok kodu birden fazla farklı siparişe özel açıklamada tekrar kullanılıyor. **Kod tek başına benzersiz kimlik değildir.**
- Toplam **9.316 adet/yıl**.
- Kaynak numune sınıfları:
  - **3 ilk fiziksel numune**, toplam **2.444 adet** üretim.
  - **5 fiziksel kıyas numunesi**, toplam **1.538 adet** üretim.
  - **59 sökmeden/katalog kıyası**, toplam **4.296 adet** üretim.
  - **41 üretici kimliği veya sipariş reçetesi doğrulaması bekleyen satır**, toplam **1.038 adet**.
- Harmonik 8 fiziksel numune adayı: GA5436, GA5636, GA5536, GA5429, GA5426, GA5336, GA5412, GA5415. Bunların doğrudan üretimi **3.982 adet**, Harmonik toplamında yaklaşık **%42,74**. **Fiziksel teknik temsil yüzdesi değildir**.
- 2026 resmî listesi tek faz HRM (%5,67/%7/%14), trifaze HRT (%5,67/%7 THDv<%7/%7 THDv<%8/%14) ailelerinde standart kodlar sunar. G/GG varyantına veya `GA5ÖZELHARM` koduna standart baz model sayısal değerleri **kopyalanmamalı**.

## Sonraki denetim için sabit kurallar
1. 108 aktif satırın her biri stok kodu **+ model açıklaması + ürün sınıfı** ile benzersiz kaydedilecek; tekrarlı özel kodlar birleştirilmeyecek.
2. Üretici 2026/12 PDF'nin tüm HRM/HRT tabloları ürün kodu bazında karşılaştırılacak: p/THDv sınıfı, güç, Irms, L, ölçü, kg, bağlantı, fiyat.
3. 2023 katalog / üretici teknik çizim ile doğrulanan alanlar ayrı belirtilecek; farklı ürün revizyonunda kaynak seçimi açıklanacak.
4. 41 kimlik/reçete satırı için **kaynak talep edilecek**; kurgusal G/GG teknik özellikleri üretilemeyecek.
5. Harmonik 8 numunenin yeterliliği, Şönt'te yapılan gibi, kaynak fiziksel kıyas kodu ve bağlantı ailesi üzerinden incelenecek. Ortak bobin/nüve/sarım **BOM ve fiziksel inceleme olmadan varsayılmayacak**.
6. Yıllık adet **9.316**, Şönt **35.772** ve toplam **45.088** korunacak; mevcut Şönt teknik katmanı değiştirilmeyecek.

**Durum: Envanter ve ön kaynak taraması tamam; Harmonik katalog teknik düzeltmesi ve numune optimizasyonu tamam değil.**
