# Piyasa Kırılganlığı V1 — Eksik Değişkenler / Düzeltici Denetim (2026-10-23)

**Düzeltme:** İlk V1, farklı göstergelerin kapsamlı testi DEĞİLDİR. Kullanıcı tarafından istenen GVZ dışındaki bağımsız ekonomi/pozisyon/likidite kanalları tamamlanmadı. Bu kontrol yanlış biçimde "geniş kapsamlı araştırma tamamlandı" diye ifade edilmeyecek.

## Gerçekten modele alınan aileler

1. Altın geçmiş günlük fiyatlarından hesaplanan 8 özellik (1,5,20 günlük getiri; RSI14; MA20 mesafe; son 20g tepeden geri çekilme; 5/20g günlük gerçekleşmiş volatilite).
2. Gümüş fiyatından 3 özellik (1,5g getiri; 5g vol), dört metalin 5g getiri ayrışması 1 özellik.
3. CBOE GVZ: seviye, 252g standardize sapma, 5g/1g değişim = 4 özellik.
Toplam 16 özellik. Aylık/haftalık fiyat modelinden tahmin sinyali veya doğru/yanlış tahmin sonucu girdi olarak kullanılmadı.

**Ayrı tutulması gerekenler:** RSI, hız, volatilite ve ortalamadan uzaklık yeni bağımsız yayınlanan ekonomi verisi değil, geçmiş fiyatın dönüşümleridir. Gümüş/platin/paladyum bağımsız piyasa fiyatlarıdır ancak CFTC/ETF/faiz/dolar/teminat yerine geçmez.

## Aday olup HENÜZ nicel modele alınmayanlar

| Aile | Örnek | Şimdiki durum |
|---|---|---|
| Fed / dolar | DXY, Fed H.10 geniş dolar endeksi DTWEXBGS | Neon DTWEXBGS_FRB_H10 2023-01..2026-10 949 satır var. Güncel sayısal gözlemin ne zaman resmi yayımlandığı H.10 takvimiyle kontrol edilmeli; aynı tarihli değerin geriye dönük tahmine sızması yasak |
| Faiz | 10y nominal DGS10; reel faiz (DFII10), 2y, eğri; faiz sürprizleri | Neon DGS10_FRB_H15 2023-01..2026-10 949 satır var. 2010 başlangıcına uygun ayrı tarihsel kaynak/ilk yayımlanma kapısı gerekiyor |
| ETF | GLD tonaj ve akımı; SLV tonaj ve akımı; GLD-SLV ayrışması | public.observations içinde CFTC/ETF/GLD/SLV adlı direkt seriler bulunmadı; dış kaynak, ham veri ve yayın tarihi doğrulanmadan girdi yapılmayacak |
| Pozisyon | CFTC COT managed-money net long / open interest | doğrudan CFTC/COT olarak adlandırılmış daily observations yok; haftalık yayımlanma kesiti + tarihli tarihsel arşiv teyidi gerekir |
| Kaldıraç | CME COMEX altın/gümüş teminat değişimi; fiyat değişimi sonrası marjin kaynaklı risk | 27 Ocak 2026 resmi gümüş teminat duyurusu kaynaklı olay kanıtı mevcut fakat 2010–2025 tarihsel *tam ve as-of* seri yok; henüz sayısal modele alınmadı |
| Altın gün içi davranışı | Zirve-dip kırılması, saatlik momentum dönmesi, gümüş-altın seans ayrışması | kullanılan StakTrakr kaynaklarında yalnız bir günlük referans fiyatı var; gerçek intraday high-low/09:00/16:00 akışı ile karıştırılmamalı |
| Dolar daha geniş sepet | diğer döviz paritelerinin aynı gün güçlenme oranı, USD breadth | Ocak 29 tarihli bankacılık raporunda örnek 12 dövizli analiz yapılmış, fakat 2010–2025 geniş kapsamlı PIT oranı henüz kurulmadı |

## 2026-10-23 Neon salt-okunur durum kontrolü

- Gold Control projesi, public.observations gözlemleri: DTWEXBGS_FRB_H10 = 949 (2023-01-03..2026-10-16), DGS10_FRB_H15 = 949 (2023-01-03..2026-10-19).
- Aynı tablo: GVZ_CBOE_FRED_MIRROR_RESEARCH_V1 = 752 (2023-01-03..2025-12-31). Bu yüzden V1 CBOE resmi tarihsel dosyayı ayrıca indirdi (4298 kapanış).
- CFTC, COT, ETF, GLD, SLV veya Fund yönelimli bir ham gözlem serisi public.observations taramasında bulunmadı; bunun bütün veritabanında hiçbir karşılığı bulunmadığının kanıtı değildir. En azından bu tablonun mevcut araştırma adaptöründe hazır değildir.
- Hem DTWEXBGS H.10 hem DGS10 H.15 datasetlerinin 2010–2022 kısmını tamamlamadan, 2010–2023 eğitilmiş çok faktörlü aynı modele doğrudan ekleyemeyiz; bu durumda veri örneklemi 2023'e küçülür ve olay azlığından bilimsel zayıflık artar.

## Karşılaştırma kuralı (gelecek çalışmalar)

1. Değişmez fiyat+GVZ V1 referans sonuçları korunur; ayrı FX, faiz, CFTC/ETF, marjin aileleri versiyonlu eklenti şeklinde işlenir.
2. İlk olarak her ailede 2010–2025 veri/kaynağı, yayın zamanı as-of, tarih uyumu, boşluk ve ilk baskı durumu tam denetlenir.
3. Aynı hedef ve tarihsel kronolojiye göre, yalnız *önceden bilinen* girdilerle tek-aile ablation, ardından çok-aile karşılaştırması yapılır; 2026 Jan30'a göre ek özellik/eşik seçimi yasak.
4. 2025'teki 3/3 kaçırılan ani sert düşüş ana kör karşılaştırma görevi; 2026 Ocak 29 sinyali retrospective olgu, prospektif başarı ilan edilemez.
5. Beş günlük hareketlerin çoklu üst üste binen hedef satırları aynı şoka aitse tek olay kabul edilir. Yanlış alarm/100 gün, duyarlılık, pozitif öngörü değeri, ilk risk işareti günü raporlanır.
6. Orijinal aylık, haftalık ve günlük modellerin hiçbirini kapsam tamamlanmadan değiştirme veya terfi ettirme.

**Şu anki doğru durum:** V1 **GVZ + metal fiyat temelli** deneydir. Çok kaynaklı gerçek ekonomik/pozisyon/teminat erken uyarı motoru henüz tamamlanmamıştır.
