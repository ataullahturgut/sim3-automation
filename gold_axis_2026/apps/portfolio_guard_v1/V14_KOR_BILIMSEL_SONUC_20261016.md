# V14 KOR — Öğrenilen altın/nakit karar üstünlüğü, bilimsel sonuç

**16 Ekim 2026** — `research-gold-v14-karar-ogrenme-20261016`  
**Durum: Araştırma — KABUL/TERFİ YOK.** V13 aynen korunmuştur.  
**Amaç:** %0,8 alış + %0,8 satış maliyetini hesaba katarak AL/SAT/BEKLE kararından beklenen **net log serveti** artırmak; 2026 düşüşleri tanıyabilmek.

## Neden yeni sürüm?

V13'ün iyi yönü uzun yükselişe katılması (2023–2026 tek portföy 201,5926 USD), zayıf yönü 1 AL / 0 SAT olmasıydı. İlk V14 denemesinde 7 ve 28 gün getirileri beraber değerlendirildiğinde, 56 güne özgü bir işlem maliyetiyle uygunsuz ufuk karşılaştırması oluştu. 7 ve 28 gün ortalama beklenen getiri +%1,6064 giriş/çıkış eşiğini hiç geçmedi; V14-önce sıfır işlem yaptı. Bu başarısız sonuç silinmedi; test logunda kayıtlıdır.

Düzeltmede **56 günlük net-servet farkı** giriş için uzun ufuk olarak, 7 günlük öngörü ise kısa düşüşte çıkmanın banka maliyetine değip değmediği açısından ayrıldı. Gerçekleşen fiyat dışındaki ileri veri model güncellemelerine vadesinden önce alınmıyor.

## Matematiksel mekanizma

- **Öğrenilen çekirdek:** 7, 28 ve 56 gün sonunda altın taşımak ile nakitte kalmanın olası log-servet farkını öngören, AdaGrad uyarlamalı çevrimiçi doğrusal uzmanlar. Hata sadece ileri getiri vadesi *tamamlandığında* öğrenilir.
- **ANFIS/ANN-esinli ön tahmin:** V13'ün o ana dek bilinen bilgilerle eğitilmiş 14/56-gün tahminleri giriş uzmanına girer. V13'ün sabit kural parametreleri tamamen kaybolmamıştır.
- **Uyarlanır bellek:** Üç katsayılı unutma/güncelleme kapısı. Ertelenmiş 7 gün hedef hatasına göre yerel gradyanla öğrenir; **tam LSTM veya BPTT değildir**.
- **Dağılımın aşağı kuyruğu:** Geçmişte tamamlanmış dönemlerin gerçekleşen en kötü ara getirilerini kullanarak 7/28 gün beklenen olumsuz hareket büyüklüğünü öğrenir; bir risk ağırlığı hâlâ dışsal araştırma tercihi (%20) olduğu için her parametre otomatik öğrenilmiş değildir.
- **Portföy politikası:** `CASH→GOLD` için beklenen brüt 56 gün log üstünlüğü, `-2*100*ln(1-0.008)≈1.6064` yüzde-puanlık iki banka maliyetini aşmalıdır. `GOLD→CASH→GOLD` kısa koruma eylemi için öğrenilmiş 7 gün aşağı log getiri de aynı iki bacağı karşılamalıdır. Bu eşik optimizasyon sonucu değil, ekonomik işlem maliyetinden gelir.
- **Hata güncellemesi:** 7 gün için 7 günde bir; 28 gün için 14 günde bir; 56 gün için 28 günde bir öngörü örneği. 28/56 ufuklarda iki kere örtüşme devam eder; bağımsız deney sayısı bunlarla eşit değildir.
- **İcra:** Türkiye saati 09.00 sinyali, sonraki gözlenen banka kontrol fiyatı üzerinden sanal icra. Gerçek banka BID/ASK akışı **yoktur**; bu sadece geçmiş MID fiyat vekilidir.

## Sınanmış net portföy sonuçları

| Kesit | Başlangıç | V13 SENTEZ | V14 KOR | Pasif ALTIN | V14 işlemi |
|---|---:|---:|---:|---:|---:|
| 2023–2026 Eylül kesintisiz | 100.00 | 201.5926 | **204.5932** | 224.2720 | 3 |
| 2024 bağımsız | 100.00 | 113.8679 | **107.0564** | 123.9218 | 1 |
| 2025 bağımsız | 100.00 | 160.5355 | **160.5355** | 160.5373 | 1 |
| 2026 Şubat–Eylül bağımsız | 119.753917 | 97.2955 | **97.8131** | 106.2807 | 1 |

V14 tek portföy maksimum geri çekilmesi yaklaşık **%35,27**. 2026 Şubat–Eylül V14 başlangıç nakdi olan 119,753917 USD'nin de gerisinde kaldı. Yıllık bağımsız koşular kesintisiz koşuyla birleştirilemez.

**Ablasyon:** Uzun kesintisiz koşuda adaptif hafıza kapısı çıkarıldığında 204.5932, risk cezası çıkarıldığında 204.5932, kısa vade çıkış başlığı çıkarıldığında 204.5932: **katkıları bu deneyde kanıtlanamadı.** 2024'te risk başlığını çıkarmak sonucu 118.4559'a artırdı; risk tercihi ayrıca ele alınmalıdır. Sonuç farkı tek başına mekanizma nedenselliği kanıtlamaz.

## Test ve yöntem sınırları

GitHub CI'da **8/8 V14 testi başarılı**: pozisyon/komisyon matematiği, olgunlaşmayan etiket güncellemesi yasağı, güncellenebilir katsayılar, sentetik giriş-çıkış, sanal banka zamanı, gelecekteki fiyatlar değiştirilince eski kararların sabit kalması, 2023–2025 gerçek veri yolu ve maliyetli geçmiş koşu.

Teknik testlerin geçmesi yatırım başarısı değildir. V14 tüm 2023–2026 dönemleri görüldükten sonra inşa edildi; bu yıllarda gerçekleşen sonuçlar **gerçek ileri-kör test değildir**. Çapraz-yıl yeniden test, seçme yanlılığı ve 2026'ya özel ayar riski taşır. Makro OLAY-02/ÖĞREN-03 ilk-yayın saatleri doğrulanmadığı için nedensel haber girdisi kullanılmaz. Live trade ve otomatik emir kapalıdır.

## Bilimsel hüküm

**V14 deney olarak saklanır; V13 yerine otomatik terfi reddedilir.** 2023–2026 toplamda V13'ü 3,00 USD geçmiş ama pasif altının 19,68 USD altında ve 2024 performansını azaltmıştır. Satış becerisi 2026 için hâlâ güvenilir değildir. Model bilinen çevrimiçi optimizasyon, hafıza, çok-ufuklu tahmin ve maliyetli portföy ilkelerinin göreve özel birleşimidir; literatürde hiç görülmemiş matematiksel yöntem olduğu kanıtlanmış değildir.

**Gerekli sonraki araştırmalar:** yeni ve seçimde kullanılmamış gerçek ileri dönem; rejim ve olay etiketlerinin ilk erişim saatlerinin doğrulanması; gerçek banka BID/ASK; maksimum geri çekilme ve log servet üzerinde bölüm sonu karar/pişmanlık geri bildirimi; ağ katmanlarının ve risk/ufuk katkılarının ayrı ablasyonu; 2026 başarısına bakarak eşik ayarlamama.

Literatür dayanakları:
- Uziel & El-Yaniv (2020), Long-and Short-Term Forecasting for Portfolio Selection with Transaction Costs, AISTATS.
- Bai vd. (2025), A Review of Reinforcement Learning in Financial Applications, Annual Review of Statistics and Its Application.
- Cesa-Bianchi, Dekel & Shamir (2013), Online Learning with Switching Costs and Other Adaptive Adversaries, NeurIPS.
