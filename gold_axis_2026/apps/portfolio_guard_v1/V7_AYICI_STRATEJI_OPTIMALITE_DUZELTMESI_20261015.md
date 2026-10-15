# 2026 aylık ALTIN/NAKİT performansı — kritik düzeltme

**15 Ekim 2026 · EX_POST hindsight diagnostic · not a trading algorithm**

## Önceki "en iyi strateji" ifadesinin kapsamı

Daha önce sunulan "Ocak altın, Şubat altın, Mart–Haziran nakit, Temmuz/Ağustos altın, Eylül nakit" tablosu yalnız **ayın ilk 09:00 kontrolünde altın alıp ay sonuna kadar tutmak veya nakitte durmak** seçeneklerinin karşılaştırmasıydı. Ay içi giriş/çıkışlara bakılmadığı için o ayların en iyi stratejileri değildi. Kullanıcı haklı olarak bu sınırı sorguladı.

Bu düzeltilmiş deney aynı 2025–Eylül 2026 3511 satırlık kaynak panelin 2026 gözlemleriyle ve **Türkiye 09:00/12:00/15:00 üç saatlik kontrol noktaları** ile ay başı NAKİT/ay sonu NAKİT döngüsünü eniyiliyor. Her alış ve satış bacağı %0,8; banka gerçek alış-satış kotasyonları, emir kayması yok.

Dinamik programlama nakit/altın portföy durumunu ve izin verilen **tamamlanmış AL+SAT turu** sayısını izler. Aynı kontrol noktasında hem alış hem satış yapılamaz. Çoklu tur opsiyonları 1, 2, en fazla 15 tam tur; ayrıca en fazla 15 tur ve en az 24 saat açık pozisyon hassasiyeti ayrı hesaplanır. Her ay tamamlandığında teorik terminal CASH değerleri raporlanır.

### Net 100 dolar başlangıçlı aylık fiyat-yolu eniyilemesi

| 2026 Ayı | Ay boyu altın tut veya nakdin en iyisi | En iyi tek tam AL+SAT | En fazla 2 tam AL+SAT | En fazla 15 tam tur |
|---|---:|---:|---:|---:|
| Ocak | 115,3665 | 124,9635 | 124,9635 | 124,9635 |
| Şubat | 112,2176 | 112,5602 | 115,8365 | 119,1930 |
| Mart | 100,0000 | 105,9882 | 107,7235 | 108,5704 |
| Nisan | 100,0000 | 102,9341 | 103,4738 | 103,8268 |
| Mayıs | 100,0000 | 102,9581 | 105,1526 | 105,9584 |
| Haziran | 100,0000 | 104,8312 | 105,1488 | 105,4466 |
| Temmuz | 100,3338 | 103,4268 | 105,4919 | 105,6824 |
| Ağustos | 107,8536 | 112,8387 | 113,2400 | 113,2400 |
| Eylül | 100,0000 | 102,4304 | 103,4440 | 103,4481 |

**Örnekler (Türkiye saati):**
- **Ocak:** 2 Ocak 09:00 AL, 29 Ocak 09:00 SAT → +%24,9635. Bu başka bir panelle yapılan Ocak V1'in 119,75 $ sonuç sözleşmesinin yerine geçmez.
- **Mart:** 23 Mart 12:00 AL, 25 Mart 15:00 SAT → +%5,9882. Mart boyunca altın tutmak net yaklaşık −%16,61 olduğundan, yalnız nakitte kalmak her anlamda optimal değildi.
- **Haziran:** 11 Haziran 09:00 AL, 16 Haziran 15:00 SAT → +%4,8312; Haziran ay boyu altın taşımak negatif.
- **Ağustos:** 3 Ağustos 15:00 AL, 24 Ağustos 15:00 SAT → +%12,8387.
- **Eylül:** 2 Eylül 09:00 AL, 4 Eylül 12:00 SAT → +%2,4304; ay boyu altın tutmak negatif.

### Şubat–Eylül 2026 kesintisiz karşı-olgusal nakit, başlangıç 119,753917 USD

| Her ay sonunda CASH'e dönen hindsight strateji ailesi | Eylül sonu |
|---|---:|
| Yalnız aylık nakit/altın seçimi | **145,422810 $** |
| Her ay en fazla 1 tam alış + satış turunun geleceği bilinen en iyisi | **189,741346 $** |
| Her ay en fazla 2 turun geleceği bilinen en iyisi | **211,263653 $** |
| Her ay en fazla 15 turun geleceği bilinen en iyisi | **222,564109 $** |
| En fazla 15 tur + en az 24 saat pozisyon kuralı | **221,403143 $** |

Eski aylık tek AL/TUT seçimi yaklaşık **145,427924** idi; yeni 145,422810 $ olmasının nedeni eski son fiyat tanımında son barın \`c\` sütunu, bu benzerlik-denetiminde ise **tamamen aynı kontrol noktalarında işlem görebileceği varsayılan \`p\` fiyatı** kullanılmasıdır. Kaynağın \`p\` fiyatının gerçek banka emrine uygulanabilirliği doğrulanmamıştır.

Bu rakamlar sadece **matematiksel en-iyi-olabilirdi** tanımlarıdır. Bir ayın gelecekteki fiyat noktalarının tamamını gören ve kusursuz tepe/dip seçen imkânsız bir geriye dönük algoritmayı tarif eder. Hiçbirisi V7'nin kazancı, beklenen getirisi veya geleceğe taşınacak gerçekçi hedef olarak ilan edilemez. İşlem maliyeti daha ağır veya icra saatleri farklıysa ideal sonuç değişir.

## Başarıyı nasıl ölçeceğiz?

- **İlk derece:** AS-OF olarak üretilmiş V4/V5/V7 işlemlerinin aynı veri ve maliyet sözleşmesi ile nakit ve altın referanslarına göre net parasal kazancı, maliyeti, maks drawdown, işlem sıklığı, kötü rejim davranışı.
- **Aylık teşhis:** Ay sonu ekonomik rejim kimliği, fiyat büyük hareketleri, ay içi en fazla bir tamamlanmış tur hindsight fırsat haritası, alınamayan fırsatın nedeninin veriye dayalı açıklaması, karar anında bilinen ekonomik olay ve çapraz varlık durumu.
- **Ek öğrenme katmanı:** Yalnızca geçmişte bitmiş ayların etiket ve hatalarıyla 24/96/336 saat kalan hareketin dağılımını güncelle. Bir ayın hindsight optimum zamanlarını aynı ay içinde model feature olarak kullanmak gelecek sızıntısı olur.
- **İleri test:** Önceden kilitlenmiş algoritmayı henüz görülmemiş dönemlerle test et; banka BID/ASK fiyatlarını doğrula. Önceden bilinen 2026 senaryolarını yeni kör doğrulama olarak sunma.

## Program

Dal: \`research-gold-portfolio-v7-adaptive-app-20261015\`. Kaynak: \`intramonth_oracle_v7.js\`, birim ve regresyon kontrolü \`intramonth_oracle_v7.test.js\`, salt okunur API \`GET /api/algorithm/v7/intramonth-oracle\`.

Sol menüde V7 adaptif öğrenme (araştırma) → **Ay içindeki en avantajlı işlem aralıklarını incele**.

Eski modeller ve ANA-01, OLAY-02, ÖĞREN-03 manifestlerine dokunulmamıştır; canlı bankacılık/alım-satım emri yoktur.
