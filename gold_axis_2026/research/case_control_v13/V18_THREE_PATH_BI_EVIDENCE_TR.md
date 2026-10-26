# V18 — ALTIN RİSK MODELİNDE ÜÇ YOLLU İŞ ZEKÂSI

**Eski BASE14/CFTC21 anormallik skorları, eşikleri, kırmızı alarm
seviyeleri ve Neon değiştirilmedi.** Tahminci değil; eski model kararlarının
bağlamını sınıflandıran ve alarm sürekliliğini koruyan bir ekran/veri eki.

## Üç orijinal-girdi temelli ekonomik yol
1. GVZ zaten BASE14 skorunu yükselten baskın nedense güçlü inceleme.
2. Mevcut 14 parametre tarihsel 2010–22 düşüş durumuna, benzer düşüşsüz
   duruma olduğundan yakınsa güçlü inceleme.
3. BASE14 RED iken CFTC21 de RED ve altın bugünkü kapanışta geriliyor,
   BASE14 skoru da önceki **bitişik** işlem gününden daha yüksekse güçlü
   inceleme (pozisyon baskısı + ivmelenen anormallik).
4. **Bir günlük devam kuralı:** Yalnız önceki bitişik BASE14 RED güçlü
   teyitliyse, bugün model YELLOW'a inmiş ve altın düşüyorsa risk
   izleme ekranında önceki güçlü durum bir gün korunur. Ertesi gün
   yeni RED yoksa tekrar YELLOW taşınamaz.
Bu kurallar yeni gelecek fiyat tahmini veya yeni geçmişten öğrenilmiş
çok değişkenli alarm modeli değildir.

## 2025 ve 2026 tarihsel karşılaştırma

|   year | policy                            |   marked_days |   false5_marked_days |   nextday3_hits |   nextday3_total |   five_day_label_clusters_hit |   five_day_label_clusters_total |
|-------:|:----------------------------------|--------------:|---------------------:|----------------:|-----------------:|------------------------------:|--------------------------------:|
|   2025 | BASE14_ORIGINAL_RED               |            32 |                   27 |               2 |                3 |                             3 |                               3 |
|   2025 | BASE14_V16_TWO_PATH               |            28 |                   23 |               2 |                3 |                             3 |                               3 |
|   2025 | V18_THREE_PATH_RED                |            28 |                   23 |               2 |                3 |                             3 |                               3 |
|   2025 | V18_THREE_PATH_WITH_ONE_DAY_CARRY |            30 |                   25 |               3 |                3 |                             3 |                               3 |
|   2026 | BASE14_ORIGINAL_RED               |            50 |                   40 |               4 |                4 |                             4 |                               4 |
|   2026 | BASE14_V16_TWO_PATH               |            28 |                   19 |               3 |                4 |                             4 |                               4 |
|   2026 | V18_THREE_PATH_RED                |            32 |                   23 |               4 |                4 |                             4 |                               4 |
|   2026 | V18_THREE_PATH_WITH_ONE_DAY_CARRY |            34 |                   24 |               4 |                4 |                             4 |                               4 |

- 2025 Mayıs 9'da BASE14 YELLOW oldu fakat önceki gün güçlü RED ve
  fiyat yumuşaması vardı; bir günlük devam kuralı düşüşten önce
  izlemeyi korudu. BASE14'ün 2025 ertesi gün >=%3 düşüş 2/3'ü,
  V18 takip katmanında 3/3 olarak işaretleniyor.
- 2026 Haziran 9'da BASE14 ve CFTC21 RED, fiyat kapanışı negatif
  ve BASE14 anormallik skoru önceki oturuma göre yükseliyordu.
  Böylece V16'da düşük öncelikli olan **ertesi gün -%3,67 düşüş
  öncesi** anormallik tekrar yüksek incelemeye alındı.
- 2026 eski BASE14 50 RED, 40 yanlış5 gün; V18 güçlü incelenen
  RED **32 gün, 23 yanlış5 gün**. Tek oturumluk YELLOW takibi dahil
  toplam inceleme 34 gün, 24 yanlış5 gün; dört 5g risk etiket
  kümesi ve dört ertesi gün >=%3 hedef gününün tamamıyla örtüşüyor.
- Bu, **gerçek kırmızı yanlış alarmların 40'tan 24'e indiği** anlamına
  GELMEZ; orijinal 50 RED ve 40 false5 gün değişmedi. V18 ayrı
  dikkat katmanı, daha yüksek öncelikli geçmiş etiket örtüşmesidir.
- 2026 y1 ve küme başarısı bağımsız kör test DEĞİLDİR; 2026 olayları
  araştırma sırasında daha önce görüldü, bu yüzden üçüncü yol ve
  YELLOW devamı doğrudan üretime alınamaz.

## Kabul öncesi kanıt şartları
- 2025 yalnız üç ayrı risk kümesi: istatistiksel örnek sınırlı.
- 2026 daha önce incelendi: başarı iddiası yalnız keşif.
- 2010–2022 tarihsel makro ilk sayısal yayımlanma/vintage henüz
  tam PIT doğrulanmış değil.
- Alarmların fiziksel düşüş başlamadan önce geldiğini kanıtlamak
  için intraday price onset gereklidir.
- Yön/etki değişkenlerinin önemli olduğu bağlamları doğrulamak için
  sonraki bağımsız dönem ve rejim-özgü kontrol şart.

## Dosyalar
- outputs/v18_daily_business_intelligence.csv
- outputs/v18_2025_2026_same_day_replay.csv
- outputs/v18_actual_drawdown_onset_timeline.csv
- outputs/v18_audit.json
- outputs/v18_tests.log
