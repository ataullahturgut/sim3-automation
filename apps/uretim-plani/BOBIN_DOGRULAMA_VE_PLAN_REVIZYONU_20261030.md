# Şönt + Harmonik: Bobin kanıt denetimi ve üretim planı revizyonu
Tarih: 2026-10-30 · Durum: **TEKNİK ONAY BEKLİYOR — UYGULAMAYA YANSITILMADI**

## Karar
Önceki dört grup üretim planı **bobin/sarım kapasitesi doğrulanmış bir plan değildir**. Makine yatırımı ve kapasite hesabında kullanılmamalı. Aylık gruplama, yıllık ürün adedi ve 1/2/3/4 üretim partisiyle oluşturulmuştu.

**Ürün başına fiziksel üretim bobini adedi, 135 ürünün hiçbirinde üretici BOM'u veya onaylı sarım föyüyle tek tek kesin doğrulanmadı.** Resmî dokümanların tek/üç faz devre topolojisi ve görüntüleri tek tek sarılacak fiziksel parçaların nihai adet reçetesi yerine geçmez.

## Kaynaklar ve kanıt
- Grup Arge resmî 2026/12 liste: https://www.gruparge.com/fl/tr (s.17, 30–32); standart modelin mono/trifaze ürün sınıfını gösterir, **bobin adedi tablosu vermez**.
- Şönt kullanma kılavuzu s.6 bağlantı şemaları: https://www.gruparge.com/wp-content/uploads/2025/05/SONT-REAKTORU-KULLANMA-KILAVUZU.pdf
- Harmonik filtre kullanma kılavuzu s.9 bağlantı şemaları: https://www.gruparge.com/wp-content/uploads/2025/05/HARMONIK-FILTRE-KULLANMA-KILAVUZU.pdf
- Şönt fiziksel çizim: https://www.gruparge.com/wp-content/uploads/2025/06/MONOFAZE-SONT-REAKTORU-TEKNIK-CIZIM.pdf
- Harmonik fiziksel çizim: https://www.gruparge.com/wp-content/uploads/2025/05/HARMONIK-FILTRE-DATASHEET.pdf (s.3)
- **Bu çizimler ve elektriksel şemalar fiziksel bobin sayısı/BOM için ürün bazında onay yerine geçmez.**

## 135 ürünün mevcut durumu
| Durum | Ürün satırı | Yıllık ürün adedi | Sadece elektriksel faz/sargı yolu ön göstergesi |
|---|---:|---:|---:|
| Resmî listede doğrudan kod karşılığı bulunan tek faz standart | 21 | 34.546 | Faz başına tek sargı yolu (1 referans) |
| Resmî listede doğrudan kod karşılığı bulunan üç faz standart | 71 | 9.230 | 3 faz sargı yolu (3 referans) |
| Standart koduyla birebir eşleşmeyen G/GG ve özel üretim | 43 | 1.312 | **BİLİNMİYOR** |
| **Toplam** | **135** | **45.088** | **Fiziksel bobin sayısı doğrulanmadı** |

Doğrudan kod eşleşen 92 ürün için **yalnızca kapasite hassasiyetini karşılaştırmaya yönelik** faz-sargı yolu göstergesi:
(34.546 × 1) + (9.230 × 3) = **62.236 elektriksel sargı-yolu eşdeğeri**.
Bu sayı **sarılacak fiziksel bobin sayısı DEĞİLDİR**; kesin iş yükü veya işçilik süresi değildir. 43 özel kayıt = 1.312 ürün için katsayı bilinmiyor.

43 kayıt ayrımı: 29 G/GG varyantı = 860 ürün/yıl; 14 diğer/katalog dışı = 452 ürün/yıl. Baz standart modelin varlığı varyant bobin adedini doğrulamaz.

## Eski dört gruplu aylık taslağın yalnızca faz-sargı-yolu göstergesi ile denetimi

> Aşağıdaki çizelge **onaylanmış revize plan değildir**; önceki planın niçin makine yatırımına uygun olmadığını göstermek için hazırlanmıştır.

| Ay | Tek grup | Şönt adet | Harmonik adet | Toplam ürün | 92 standart üründen faz-sargı yolu eşdeğeri | Bobin adedi bilinmeyen ürün adedi |
|---|---|---:|---:|---:|---:|---:|
| Ocak | Grup 1, 4 parti | 7.674 | 383 | 8.057 | 8.823 | 0 |
| Şubat | Boş | 0 | 0 | 0 | 0 | 0 |
| Mart | Grup 3, 2 parti | 628 | 1.587 | 2.215 | 5.379 | 230 |
| Nisan | Grup 1, 4 parti | 7.674 | 383 | 8.057 | 8.823 | 0 |
| Mayıs | Grup 2, 3 parti | 850 | 450 | 1.300 | 2.200 | 0 |
| Haziran | Grup 4, 1 parti | 1.282 | 3.262 | 4.544 | 9.604 | 852 |
| Temmuz | Grup 1, 4 parti | 7.670 | 383 | 8.053 | 8.819 | 0 |
| Ağustos | Grup 2, 3 parti | 848 | 449 | 1.297 | 2.195 | 0 |
| Eylül | Grup 3, 2 parti | 628 | 1.587 | 2.215 | 5.379 | 230 |
| Ekim | Grup 1, 4 parti | 7.670 | 383 | 8.053 | 8.819 | 0 |
| Kasım | Boş | 0 | 0 | 0 | 0 | 0 |
| Aralık | Grup 2, 3 parti | 848 | 449 | 1.297 | 2.195 | 0 |
| **TOPLAM** | | **35.772** | **9.316** | **45.088** | **62.236** | **1.312** |

Önemli: Haziran'ın 9.604 eşdeğeri **852 ürünlük bilinmeyen bobin yükünü içermez**. Bu yüzden 9.604, Haziran'ın fiziksel bobin yükü değildir. Mevcut örnekte mayıs 2.200, haziran en az farklı sınıfta 9.604 eşdeğer olduğundan aylık iş yükü dengesi gösterilememiştir.

## Takvimde yapısal çelişki
- Yılda 4 üretim partisi ve **kesin 3 ay aralık**: bir grup dört ayda, ay numarası mod 3 aynı olan aylarda üretilecek.
- Yılda 3 üretim partisi ve **kesin 4 ay aralık**: diğer grup üç ayda, ay numarası mod 4 aynı olan aylarda üretilecek.
- Bu iki takvim, hangi başlangıç ayı seçilirse seçilsin **en az bir ay çakışır** (3 ve 4 aralarında asal). Dolayısıyla aynı ay **en fazla bir grup** kuralıyla iki kesin tekrar periyodu birlikte sağlanamaz.
- Önceki Grup 2 (3 parti) Mayıs/Ağustos/Aralık üretildiği için 3/4/5 aylık eşit olmayan aralık yaratmıştır; "4 ayda bir" koşulunun sağlandığı iddia edilmemelidir.

## Sonraki kararı verebilmek için gereken üretici/BOM bilgileri
Ürün bazında ve varyant bazında: (1) fiziksel bobin sayısı, (2) elektriksel faz/sargı bağlantı düzeni, (3) bobin başına tel/folyo ve ebat, (4) üretim bobin başına sarım süresi, (5) nüve boyut/sayısı, (6) proses/vernik reçetesi, (7) bir partinin sarım ve kurutma kapasitesi, (8) kaynak parça/reçete revizyonu ve onay.

Yeni planlama hesabı ancak bobin adedi kesinleşince: `Aylık bobin = SUM(Ürün bazında aylık üretim × ürün başına fiziksel bobin sayısı)`, makine yükü ise `SUM(Bobin miktarı × doğrulanmış çevrim süresi)`.

## Yazılım durumu
- **Üretim uygulamasındaki takvim ve ham veriler değiştirilmedi.**
- Bu dosya yalnızca denetim/planlama referansıdır. Bobin bilgileri doğrulanmadan yeni aylık planı "kesin" olarak kaydetmek güvenilir değildir.
