# Harmonik — 108 aktif ürünün numune seçimi ve teknik bilgi denetimi
**Tarih:** 2026-10-30 · **Yalnız Harmonik** · **Durum: KISMİ DOĞRULAMA — makine kapasitesi onaylanmadı**

## A. Gerçek kaynak ve sayımlar

- Kaynak matris: `Reaktor_Ortak_Uretim_ve_Numune_Matrisi_2026.xlsx`, Ürün_Matrisi 135 satır; 110 Harmonik satırı, `GA5522` ve `GA5523` sıfır miktarlı olduğu için **108 aktif Harmonik satırı**; yıllık **9.316 adet**.
- Aktif satırlarda **94 farklı stok kodu**. Aynı `GA5ÖZELHARM` kodu **12 ayrı ürün açıklamasında** tekrar edilmiş; `GA5532`, `GA5526`, `GA5530` kodları da **ikişer satır**. Aynı stok kodunun aynı imalat reçetesi veya aynı üretim ürünü olduğu varsayılamaz.
- Kaynak sınıfları: **3 ilk fiziksel numune / 2.444 adet**, **5 fiziksel kıyas / 1.538 adet**, **59 sökmeden kıyas / 4.296 adet**, **41 kimlik-reçete teyidi / 1.038 adet**.
- Sekiz fiziksel adayın yıllık doğrudan üretimi: **3.982 adet = %42,74**. Bu oran **fiziksel sargı geometrisi veya sarım makinesi saatleri kapsaması değildir**.
- İkinci tarihsel iç çalışma `HARMONIK_MATRISI_2026_YENI.xlsx` ile 108 ürünün model, yıllık adet ve sayısal teknik değerleri çapraz kontrol edildi: ortak 108 ürün kaydında sayısal güç, akım, L, dış ölçüler, kg, bağlantı değerleri aynı; **THDv yazımı farklı**, çünkü eski matriste `7/8` sayı, ikincide `<%7/<%8 (katalog)` olarak ifade edilmiş. İki Excel aynı belge ailesinden türemiş olabilir; bu test **bağımsız üretici onayı yerine geçmez**.

## B. Seçilmiş 8 numunenin ürün bazlı resmî belge kontrolü

Resmî Grup Arge **2026/12 etiketli ürün listesi**, PDF sayfa 30–32 (görüntüde yazan basılı sayfa numaraları), erişim: https://www.gruparge.com/fl/tr . Aşağıdaki kodların kaynak matrisinde yer alan **akım, endüktans, bitmiş ürün dış ölçüsü, ürün toplam kg ve bağlantı tipi** değerleri bu listeyle karşılaştırıldığında uyuşuyor:

| Sınıf | Ürün kodu | Yıllık adet | Irms (A) | L (mH) | Bitmiş ürün dış ölçüsü (mm) | Bitmiş ürün kg | Bağlantı |
|---|---|---:|---:|---:|---|---:|---|
| İlk | GA5436, HRT 50/7-8 | 1.532 | 82,00 | 0,77 | 270×240×150 | 22 | Bara M8 |
| İlk | GA5426, HRT 5/7-8 | 678 | 8,20 | 7,66 | 180×175×85 | 5 | Klemens |
| İlk | GA5412, HRM 1/7 | 234 | 4,95 | 12,67 | 84×70×80 | 1,5 | Klemens |
| Kıyas | GA5636, HRT 50/7-7 | 490 | 75,00 | 0,76 | 270×240×135 | 21 | Bara M8 |
| Kıyas | GA5536, HRT 50/14 | 256 | 76,50 | 1,66 | 300×255×180 | 41 | Bara M8 |
| Kıyas | GA5429, HRT 10/7-8 | 670 | 16,38 | 3,83 | 180×175×115 | 7 | Bara M8 |
| Kıyas | GA5336, HRT 50/5,67 | 78 | 90,21 | 0,61 | 295×255×165 | 27 | Bara M8 |
| Kıyas | GA5415, HRM 5/7 | 44 | 24,77 | 2,53 | 120×100×98 | 6,5 | Bara M8 |

**Karar:** Sekiz ürünün listede görünen **dış/elektriksel katalog alanlarında belirgin uyuşmazlık tespit edilmedi**. Bu, ürünlerin fiziksel bobin adedi, iletken formu, tur sayısı, nüve, izolasyon, vernik, gerçek sarım çevrimi veya kullanılan üretim revizyonunun doğrulandığı anlamına **gelmez**.

## C. Teknik eksikler / temsil açıkları

1. **HRM p=%5,67 ve p=%14** sınıflarında ilk sekiz fiziksel numune **yoktur**. Aktif kaynakta HRM p=%5,67 **2 ürün / 30 adet**, HRM p=%14 **2 ürün / 8 adet** bulunur. İnceleme adayları **GA5313 (18 adet)** ve **GA5514 (6 adet)**; katalog görünüşü benzer olsa bile iç bobin ve malzeme eşdeğerliği doğrulanmadı.
2. **HRT 100 kVAr, bitmiş ürün gövde ve ağırlık sınırı:** `GA5339` (4/yıl, **355×310×190 mm, 44 kg**) ve `GA5639` (26/yıl, **350×310×180 mm, 44 kg**) mevcut 8 adayın üst ağırlığını aşar. Gerçek sargı makinesi üst sınırı için bunlardan en az birini fiziksel/bobin kontrolü; diğerini de farklı p/THDv sınıfı nedeniyle yapı kıyası için gündeme alın. Ayrıca `GA5438` (124/yıl, **295×255×205 mm, 40 kg**) mevcut seçime göre derinlik/ölçü üst sınırı olarak kontrol edilmelidir. Bunların **bitmiş cihaz ölçüleri** olduğu ve bobin makine kapasitesiyle birebir karşılaştırılamayacağı unutulmamalıdır.
3. **41 özel/varyant ve reçete bekleyen ürün satırı / 1.038 adet:** Bunların 3B güç sınıfı, sarım malzemesi, bobin sayısı ve boyutları katalog baz modelinden kopyalanamaz. `GAG...`, `GAGG...` ve `GA5ÖZELHARM` ürünleri için ayrı lot/teknik resim/BOM/doğrulama gerekiyor.
4. **THDv**: Standart HRT p=%7 ürünlerinde `7-7` ve `7-8` soneki **tasarım eşik sınıfı** anlamında `THDv<%7` ve `THDv<%8` diye yazılmalıdır; sayısal `7` veya `8` tek başına sınır eşitsizliğini göstermez. Özel G/GG varyantlarında kaynak açıklamalarındaki 12/15 gibi değerler **ürün standardı olarak onaylanmamıştır**.
5. **Numune seçiminde en az set optimizasyonu tamam değil:** Birbirine benzeyen gövdelerin farklı iletken/sarım iç yapıları olabileceğinden, sekiz ürün için `tam 108 ürünü temsil ediyor` denemez. Yeni adaylar fiziksel kanıta göre eklenecek, mevcut sekiz otomatik silinmeyecek.
6. **Teknik değer eksikliği:** Aktif Harmoniklerin 41 tanesinde katalogla eşleştirilebilen akım, endüktans, ölçü, kg, bağlantı ve diğer ürün bazlı kesin alanlar yoktur. Eksik değere 0 veya baz modelin sayısı yazılmaz.

## D. Uygulama düzeltmeleri ve veri güvenliği

`simulation3/apps/uretim-plani/plan2027-samples.js` üzerinde mevcut **Numune ve Teknik Kapsam** sayfasında (yeni sekme yok):
- HRM ailesi `HRM 5,67` / `HRM 7` / `HRM 14` alt grupları olarak ayrıldı. HRT `5,67 / 7-7 / 7-8 / 14` de stok kodu + sınıfına göre ayrılır.
- Kaynakta **3 ilk + 5 fiziksel kıyas + 59 doküman kıyası + 41 kimlik teyidi** ayrı etiketlerle korunur; numune sayısı **değiştirilmez**.
- Standart HRT 7/7 ve 7/8 için THDv eşikleri doğru biçimde `<%7 / <%8` yazılır. Özel varyantların `p/THDv` sayıları **sipariş açıklaması; teyitsiz** diye işaretlenir; orijinal ham veriler değiştirilmez.
- Yinelenen stok kodlu Harmonik satırlarında yeni sarım/emprenye girişleri **ürünün benzersiz satır id'sine** yazılır. Tekil stok kodlarında eski kayıtların anahtarı korunur. `GA5ÖZELHARM` gibi önceden **tek koda topluca** kaydedilmiş bir teknik veri varsa orijinal JSON saklanır ama hangi satırın olduğu ispatlanamadığından **otomatik olarak 12 satırın hepsine uygulanmaz**; kullanıcı eski yedeği incelemelidir.
- Şönt, 2027 aylık üretim planı, 28 sütun düzeni ve kaynak Excel dosyası **değiştirilmedi**.

## E. Yatırım için karar

**Numune seçimi ve katalog sayıları: kısmen doğru. Fiziksel üretim reçetesi ve tüm 108 ürünün makine kapsamı: doğrulanmadı.**

Sıradaki teknik karar: küçük HRM p5,67/p14 adaylarını, HRT üst gövde/üst yük adaylarını ve G/GG/özel ürünlerin kimlik-reçete doğrulama gereksinimini mevcut 8'in yanına hangi **inceleme kategorisiyle** ekleyeceğimize karar vermek. Bu rapor tek başına yeni fiziksel numune veya makine alımı talimatı değildir.

**Birincil kaynak:** https://www.gruparge.com/fl/tr (resmî PDF, 2026/12 etiketli, basılı sayfa 30–32). **İç kaynak:** `Reaktor_Ortak_Uretim_ve_Numune_Matrisi_2026.xlsx` ve `HARMONIK_MATRISI_2026_YENI.xlsx`; bunlar uygulamanın ürün-kod/üretim envanterini sağlar.
