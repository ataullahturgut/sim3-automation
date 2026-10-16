# KAVİS V20 R2 — GERÇEK TARİHSEL FİYAT PİLOTU | SABİT MANİFEST

## Zaman, sermaye ve yürütme
- Başlangıç: 2023-01-03 09:00 Europe/Istanbul = 2023-01-03T06:00:00Z.
- İlk pilot bitişi: 2023-01-31 17:00 Europe/Istanbul = 2023-01-31T14:00:00Z (en son banka fiyatı vekili 15:00 TSİ/12:00Z olabilir).
- Sermaye 100 USD, başlangıç CASH; aylık reset yok. Şubat'a aktarım yalnız açık yeni koşu yetkisiyle yapılır.
- Türkiye işlem seansında sinyal 09:00 veya 12:00 TSİ = UTC 06/09. Sadece bir sonraki 12:00/15:00 TSİ = UTC 09/12 fiyat kotasyonu vekilinde (sinyalden kesin sonra) fill. 15:00 TSİ son karar yok; gece emir yok.
- Haber/olay/monetary as-of ilk yayın zamanları bağımsız doğrulanmadığı için `events=[]`, `nq6` boş, `v15Expert` boş; haber varmış gibi veri girişi yasak.
- Her banka yürütme bacağında varsayımsal %0,8 maliyet uygulanır; MID vekili gerçek banka alış/satış kotasyonu değildir, slippage dahil değil.
- Ana politika: V20 R2 `riskMode=alert`. İsteğe bağlı %15 soft_penalty bu pilot için gerçek yatırım kuralı değildir; varsayılan gerçek fiyat yürüyüşünde otomatik açılmaz.
- V18 kontrol, 100 USD sabit CASH ve ilk uygun fiyattan banka %0.8+%0.8'e tabi pasif gold kıyasları ayrıdır.

## Kaynak ve epistemik statü
- Önceki fiyat gözlemleri: data/RECOVERY_HIST_3H_2020_2022_V1.csv, Git blob `e19d69fbbf4a825420a07d7e5f678899d1e0f805`.
- 2023 fiyat gözlemleri: data/RECOVERY_HIST_3H_2023_2025_V1.csv, Git blob `a588b6745f893fcafc935fa486328a6349caa658`.
- Bu dosyalardaki `p` alanı bir **CME geçmişinden türetilmiş XAU/USD MID fiyat vekilidir**. Orijinal banka BID/ASK değil, doğrudan kesin spot XAU da değil. `c` veya önceden hesaplanmış r4/r92/rv/ds/eff/loc alanlarından gelecek bilgisini kaçırmamak için tek başına fiyat `p` kullanılır.
- As-of özellikler yalnız son `tt < signal.asof` fiyatlarından hesaplanır. Başlangıçta yalnız 2022 tarihli geçmiş piyasa fiyatı ısınma için görülebilir; 2023 fiyatları t anı geldiğinde kronolojik açılır.
- Kaynaklar daha önce diğer araştırmalarda incelendiği için 2023 dönemi gerçek fiyat geçmişi ama KÖR YATIRIM BAŞARI SINAVI DEĞİLDİR.

## Bilimsel sözleşme
- Sonradan ay sonu geleceğe bakma, 2026 Ocak silinen test dosyalarını kullanma, uydurma olay ilk yayım zamanı, gerçek banka spreadi olduğunu söyleme yasak.
- Akış: bank row 06/09/12 UTC at t fiyat gözlemi => önce önceki sinyali fill; yalnız 06 ve 09 saatlerinde t'den ÖNCE gözlenmiş fiyatlarla yeni sinyal; tekrar t+3 saat sonra fill. t=12'de geceye açık emir verilmez.
- Hata halinde fail closed; reset veya sentetik doldurma yok. Her AL/SAT/BEKLE gerekçesi, pozisyon, Q öğrenme aralık sayısı ve fiyat kaynağı günlük deftere girer.
- Pilot hedef 2023 Ocak; işlem çıkmazsa 0 trade/100 USD de bir sonuçtur; geçmiş bilgiyi ileri taşıyarak kâr yazılamaz.
- Test: 2023-01-03 06UTC ilk asof, fill strictly later, no future-price feature, no nighttime fills, bankFee=.008, 2022/2023 SHA pin, checkpoint count ve frozen R2 action parity, terminal net NAV.

Bu manifest gerçek veri fiyat PILOTU başlarken, sonuç görülmeden önce kaydedilmiştir. Parametre ayarlaması için önceden görülmüş Ocak 2023 fiyatı kullanılmayacak.