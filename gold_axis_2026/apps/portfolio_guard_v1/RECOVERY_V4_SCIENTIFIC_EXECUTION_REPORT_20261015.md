# GOLD GUARD V4 — Adaptif TUT / Şok Koruma Araştırma Raporu

**Tarih:** 2026-10-15. **Durum:** Çalışan araştırma algoritması, doğrulanmış/al-sat öneren algoritma **DEĞİL**.

## Hedef ve asgari sözleşme
Ocak sonunda NAKİT kalan 119,75391720039644 dolardan Şubat toparlanmasını yakalayabilmek; Ocak sonu SELL kararlarının önemini kaybetmeden yükselişte gereksiz AL/SAT azaltmak. Tek başına Şubat getirisine göre parametre ayarlamak yasaktır. Ekonomik olay DNA'sını fiyat evresiyle karıştırma, ilk haber UTC verisi yoksa ekonomik neden UNRESOLVED.

### Kodda yapılan değişiklikler
- `recovery_v4.js`: fiyat rejimi, geçmişten oynaklık yüzde 75 ve 95'lik dilimleri, G05-C/G06-B economic hypotheses UNRESOLVED, geçmişte tamamlanmış 96 saat olay etiketleri, iki aşamalı kademeli alım, yeterince teyit edilmemiş düşüşte TUT, acil riskte koruyucu SAT.
- Yalnız tamamlanmış 3 saatlik XAU kesitlerinde ve Türkiye saatinde 09:00/12:00/15:00'te karar; gerçek banka işleme açık olduğu kanıtı değil. Alış/satış yönü başına %0,8 komisyon, gerçek ASK/BID ve slip hesaplanmadı.
- 2020–2022 -> 2023; 2020–2023 -> 2024; 2020–2024 -> 2025. Eğitimde gelecek yıl/ay fiyatını kullanma. 2026 Ocak ve Şubat geçmiş fiyatları geçmişten gören yazar için yine kör OOS değildir.
- 2023 fiyat kaynak kapsamı diğer yıllardan az (1299 3s kararı), sonuçlar dikkatle yorumlanmalı.
- 2020–2025 10.850 tarihsel 3h kontrol kesiti, 65 96h olgunlaşmış geçmiş stres başlangıcı; olay benzerliği kalibre edilmiş risk olasılığı değildir. Makro açıklama/vintage ve banka gerçek fiyatları yok.
- Orijinal V1/V3 kodları, kararları ve Jan V1 119,753917 nakit sonucu dondurulmuş olarak korunur. V4 yalnız `/api/algorithm/v4` GET'te gölge araştırma çalışması üretir.

### Tarihsel sonuçlar: her yıl bağımsız 100 dolardan

| Yıl | V3 (önceki) | V4 (yeni) | İlk işlemde AL ve son güne kadar TUT | V4 AL / SAT |
|---|---:|---:|---:|---|
| 2023* | 110,57 $ | **110,57 $** | 110,32 $ | 1 AL / 0 SAT |
| 2024 | 119,39 $ | **125,52 $** | 124,43 $ | 1 AL / 0 SAT |
| 2025 | 141,89 $ | 141,13 $ | **161,15 $** | 3 AL / 2 SAT |

*2023 veri kapsamı eksik; bütün yıl bağımsız uygulanabilir performans olarak okunamaz.

2024'te V4 gereksiz AL/SAT azaltarak V3'e ve pasif altına karşı daha iyi göründü. 2025'te V3'ten bile yaklaşık 0,77 dolar düşük kaldı ve güçlü altın yükselişinin önemli bir bölümünü kaçırdı. Bu yüzden **V4 tüm dönemlerde üstün değil**.

### Ocak ve Şubat 2026

| Aynı başlangıç senaryosu | Final | Durum |
|---|---:|---|
| Ocak V1, 100 dolarla başlangıç | 119,75 $ | CASH |
| Ocak V4, ayrıca 100 dolarla başlangıç | **109,53 $** | CASH |
| Şubat V1, Ocak V1 nakit 119,75 dolardan | 114,27 $ | GOLD |
| Şubat V3, Ocak V1 nakit 119,75 dolardan | 120,44 $ | GOLD |
| **Şubat V4**, Ocak V1 nakit 119,75 dolardan | **122,87 $** | GOLD |
| Şubat hiç işlem yapma, nakitte bekle | 119,75 $ | CASH |
| Şubat ilk uygun fiyat 06:45 Türkiye'de AL/TUT, teorik | 132,91 $ | GOLD |

**İşlem penceresi notu:** İlk uygun fiyat 06:45 Türkiye (banka alış-satış saati dışında) diye gösterilen AL/TUT yalnız fiyat evreni karşılaştırmasıdır. İlk Türkiye 09:00 fiyatından AL/TUT aynı kaynak ve komisyonla yaklaşık **136,37 $** olurdu; o noktada fiyat çok sert düşüyordu ve yükselişin geleceği bilinmiyordu. İki rakamı da başarı/öngörü diye kullanma.

Şubat V4 işlemleri:
1. **4 Şubat 2026, 09:00 Türkiye: AL** 5079,185 $/ons. `RECOVERY_CANDIDATE` + tekrar teyit; yaklaşık yarım portföy.
2. **19 Şubat 2026, 12:00 Türkiye: AL** 5016,925 $/ons. `UP_TREND` teyidi; kalan nakdi yatırma.
3. **Şubat boyunca SAT yok**. Son durumda GOLD. 122,867909 USD son tarihsel altın kapanışının **varsayımsal satış komisyonu düşülmüş değeridir**; nakit değer değildir.

Ocak V4 ilk AL 12 Ocak 12:00 Türkiye, ilk SAT 30 Ocak 12:00 Türkiye. Ocak V1 5 Ocak AL / 29 Ocak SAT'ı kaçırdığı için yaklaşık 10,22 dolar daha düşük kaldı.

### Bilimsel ve yazılımsal güvenlik testleri
- Git blob ile sabit XAU fiyat kaynakları (2020–22, 2023–25), geleceğe ait fiyat hesap özelliklerini karar satırına sokmama.
- Yalnız geçmiş yıl/kapanışa kadarki RV percentile eğitimi, 96h olgunlaşmamış ileri hedefin dışlanması.
- `HOLD` ve `WAIT` kararları meşru; henüz fiyat/haber kanıtı olmayan olaylar için kesin G05-C/G06-B nedensellik yok.
- Aynı yılın sonucunu gördükten sonra aynı yılın parametresini oynayıp bağımsız doğrulama sanma yasağı.
- Banka işlem penceresi, çift tek yönlü komisyon, detaylı karar gerekçesi, deterministik sonuç, salt okunur API ve V1 mutasyonsuz test.

### Sonraki geliştirme kapısı
V4'ün 2025 yükselişini yakalama zayıflığının hangi tarih ve kararlardan kaynaklandığını ayırmak, güçlü aylık yönle birlikte risk rejimlerini okumak, piyasa sürtünmesi ölçmek ve yalnız daha sonraki dondurulmuş dönemlerde OOS ölçmek. Bu rapor tek başına canlı portföy kararını onaylamaz. `V4` bugün bir **geliştirilebilir algoritma prototipi**, nihai ekonomik DNA algoritması değil.
