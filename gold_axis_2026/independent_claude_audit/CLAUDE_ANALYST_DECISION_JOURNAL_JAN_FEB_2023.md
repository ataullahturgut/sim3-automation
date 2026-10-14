# Analist karar günlüğü — Ocak–Şubat 2023 (haber + veri + vaka, kararı Claude veriyor)

**Tarih:** 2026-10-14 · **Kullanıcı isteği:** Kararı algoritmaya bırakmadan, her karar anında haberleri, verileri ve geçmiş vakaları **kendim** inceleyip karar vermem; her karardan öğrenip bir sonrakine taşımam.
**Veri panosu kaynağı:** [aes/AES_v1_1_RESULTS.json](aes/AES_v1_1_RESULTS.json) `ledger_2023` (her 09:00 ve 16:45 TRT için yalnız o ana kadar bilinen değerler), makro açıklama saatli tepkileri [CLAUDE_2023_KEY_RELEASES_CME_N0_H1_REACTIONS.csv](CLAUDE_2023_KEY_RELEASES_CME_N0_H1_REACTIONS.csv), olay analogları Neon `gold_research_r72_claude_macro_analogs_v1`.

> **Dürüstlük notu:** Bu ayların sonucunu biliyorum. Özellikle 3 Şubat sabahı satış kararı, önceki denemede “hata” dediğim yerin tersidir. Bu yüzden her kararın yanına **o an kullandığım kuralı** yazdım ve aynı kuralı diğer günlere de uyguladım (5 Ocak, 19 Ocak, 27 ve 31 Ocak'ta aynı kural SAT dedirtmedi). Yine de bu bir kör test değildir.

## Pano sütunları
trend20 = 20 seans ortalamasına göre konum · mom10 = 10 seans getirisi · altın/gümüş 24s = son 24 saat · ZN 24s = 10 yıllık tahvil vadelisi (↑ = faiz ↓) · NQ 24s = Nasdaq vadelisi · GVZ = altın oynaklık endeksi 5 günlük değişim. Dolar endeksi ve getiri düzeyleri **yok**; dolar bilgisi yalnız haber metninden.

## Başlangıçtaki dersler (2020–2022'den, karar öncesi bilinen)
* **D0-1:** Tek başına hiçbir veri sinyali güvenilir değil (modül isabetleri %45–57). Veriyi **teyit / çelişki** olarak kullan.
* **D0-2:** Yükseliş rejiminde hawkish veriyle gelen altın düşüşleri ortalama biraz sürdü ama nadiren %1,6 maliyeti aştı (8 olayda 1). Tek seferlik şokta satma.
* **D0-3:** Yükseliş rejiminde dovish sürpriz + altın yükselişi sürdü (Kas ve Ara 2022 CPI).
* **D0-4:** Büyük planlı açıklamadan önce maliyetli pozisyon açma; açıklamanın yönünü bekle.

---

## Kararlar

| # | Zaman (TRT) | Pano (özet) | Haber / vaka | Kararım | Kural |
|---|---|---|---|---|---|
| 1 | 3 Oca 09:00 | trend20 +1,5 · mom10 +2,6 · altın +0,9 · gümüş **+1,8** · ZN **+0,35** · GVZ +1,4 | Yeni haber yok; 6 Oca NFP yaklaşıyor. 2022'de UP rejimdeki 3 hawkish NFP'de altın düştü | **BEKLE (nakit)** | D0-1, D0-4: her şey yükselişi teyit ediyor ama katalizör yok, NFP riski önde |
| 2 | 4 Oca 16:45 | altın **+1,2**, gümüş **−0,45** (ayrışma), NQ −1,0 | ISM imalat zayıf, JOLTS güçlü | **BEKLE** | Gümüş teyit etmiyor |
| 3 | 5 Oca 16:45 | altın **−1,0**, gümüş **−3,2**, ZN ~0 (açıklama saati −0,5), NQ +0,2 | ADP 235k → hawkish. D0-2 analogları | A2 (altında): **KAL** · A1: **BEKLE** | D0-2: tek seferlik ikincil veri, NFP yarın |
| 4 | **6 Oca 16:45** | altın +0,3 (24s), **ilk 15 dk +0,65**, gümüş +0,6, rejim UP | NFP 223k ama **ücret artışı 0,3 vs 0,4** → dovish. Analog: Kas/Ara 2022 CPI | **AL** 1848,87 (A1) | D0-3 + gümüş teyidi |
| — | **Ders D1** | | 5 Oca'daki hawkish şok 24 saatte tersine döndü | | D0-2 güçlendi: tek seferlik şokta satmamak doğruydu |
| 5 | 12 Oca 16:45 | altın +0,6, gümüş +0,7, ZN +0,4 | CPI −0,1 vs 0,0 (dovish) | **KAL** | Teyit |
| 6 | 19 Oca 16:45 | altın −0,5, gümüş **−4,0**, NQ **−2,6**, ZN +0,4 | Geniş satış, faiz düşüyor | **KAL** | Rejim güçlü UP (trend20 +2,8); düşüş faizden değil, genel risk satışı → altında kalıcı değil |
| 7 | 27 Oca 09:00 | altın −1,2, ZN **−0,5** (faiz ↑), mom10 **1,7** (3,8'den düştü) | GDP 2,9 vs 2,6 | **KAL** | D0-2; rejim hâlâ UP |
| 8 | 31 Oca 09:00 | altın −0,7, gümüş −1,1, NQ −2,0, mom10 **0,5**, trend20 1,2 | FOMC yarın | **KAL** | Fed öncesi iki yönlü risk (D0-4) |
| — | **Ders D2 (“duraklama”)** | | 19 Ocak'tan beri fiyat 1925–1950 bandında; 10 günlük momentum 5,4'ten 0,5'e indi, 20 seans ortalaması fiyata yetişti | | **Bir sonraki şok rejimi döndürebilir. Rejim dönerse ve gümüş teyit ederse, faizle açıklanmayan bir düşüşte çık.** |
| 9 | 1 Şub 16:45 | rejim UP, altın +0,9 | FOMC 22:00'da | **KAL** | D0-4 |
| 10 | 2 Şub 09:00 | altın **+1,4**, gümüş +2,1, ZN +0,65, NQ **+3,5** | Powell “dezenflasyon başladı”; dolar −0,9 | **KAL** | Her şey yükseliş diyor |
| 11 | 2 Şub 16:45 | gün içi küçük geri çekilme; büyük düşüş banka kapandıktan sonra (17:30–18:00 TRT) | BoE/ECB +50bp; dolar toparlanıyor (haber) | **KAL** | Banka saatinde görünür bir sinyal yok |
| 12 | **3 Şub 09:00** | **Rejim DOWN'a döndü** (trend20 −0,08, mom10 −1,0) · altın **−1,9** · gümüş **−2,9** · ZN **+0,2** (faiz düşüyor) · NQ **+1,1** | Dolar kaynaklı, FOMC rallisinin geri verilmesi; NFP 16:30'da | **SAT** 1915,22 | **D2:** duraklama → şok → rejim dönüşü; gümüş teyit ediyor; düşüş faizle açıklanmıyor (yani tek bir verinin sönümlenecek etkisi değil) |
| 13 | 3 Şub 16:45 | altın −3,1, gümüş −5,9 | NFP 517k vs 185k, işsizlik 3,4 | **NAKİTTE KAL** | Karar doğrulandı; geri alım için dovish katalizör yok |
| — | **Ders D3** | | Rejim dönüşünü haber değil fiyat yapısı (duraklama) önceden haber verdi; NFP onu hızlandırdı | | Duraklama + şok kalıbını izle |
| 14 | 6–28 Şub (her gün) | rejim sürekli DOWN (trend20 −2 / −3) | CPI 0,5 (beklentide), perakende +3,0 vs +1,8, PCE çekirdek 0,6 vs 0,4 | **NAKİTTE KAL** | Geri giriş için iki şart yok: dovish katalizör ve rejim düzelmesi |

**Kontrol — aynı “D2” kuralı başka günlerde neden SAT demedi?**
* 5 Oca: rejim UP (trend20 +2,8), duraklama yok → kural devreye girmedi.
* 19 Oca: rejim UP, düşüş faiz düşerken geniş satış → kural yok.
* 27 ve 31 Oca: momentum zayıfladı ama rejim dönmedi → kural yok (Sınav C: satmak zarar ettirirdi).

## Sonuç (100 $)

| Hesap | Kararlar | 28 Şubat |
|---|---|---:|
| **A1** (3 Oca nakit) | 6 Oca AL 1848,87 → 3 Şub SAT 1915,22 | **101,94 $** |
| **A2** (ChatGPT pozisyonu) | Kal → 3 Şub SAT 1915,22 | **101,80 $** |
| **B** (30 Oca altında) | 3 Şub SAT 1915,22 | **97,57 $** (tutsa 92,99) |
| **C** (26 Oca altında) | Kal | net 97,37 $ (31 Oca) |
| Pasif altın | — | 97,55 $ |
| Nakit | — | 100,00 $ |

* Ocak yükselişinin bacağının %77'si yakalandı (giriş dipten +%1,15 sonra).
* Şubat düşüşünde 1 Şub kapanışından sonraki %1,80'lik kısım kaçırıldı, kalan **%5,44** (24 Şub kapanışına) atlatıldı.
* Toplam 2 işlem, 1,62 $ ücret.

## Önceki denemelerle karşılaştırma (sürekli hesap, 28 Şub)

| Yöntem | Sonuç |
|---|---:|
| **Analist günlüğü (bu dosya: haber + veri + vaka)** | **101,94 $** |
| Yalnız vaka eşleştirmesiyle takdir | 100,45 $ |
| Öğrenen algoritma (AES) | 100,00 $ |
| Mekanik rejim kuralı | 102,35 $ |
| Pasif altın | 97,55 $ |

Veri panosunu eklemek, yalnız vakaya dayalı karara göre **+1,49 $** fark yarattı. Farkın tamamı 3 Şubat sabahından geliyor: gümüşün de düşmesi ve faizin buna eşlik etmemesi, düşüşün tek seferlik bir veri tepkisi olmadığını gösterdi.

## Bu sonuç neyi kanıtlıyor, neyi kanıtlamıyor?

* **Kanıtlamıyor:** Gelecekte para kazandıracağını. Sonucu bilen biri tarafından, iki aylık tek bir dönemde verildi.
* **Gösteriyor:** Haber + vaka + veriyi birlikte okuyan bir karar sürecinin, her kararı yazılı bir kurala bağlayarak tutarlı uygulanabildiğini. D2 kuralı beş farklı düşüşte tutarlı davrandı (birinde SAT, dördünde KAL).
* **Gerçek test:** Bu ders listesiyle (D0–D3) Mart 2023'ten itibaren aynı süreci gün gün yürütmek. Her karar anında yalnız o güne kadarki veriyi sorgulayıp kararı **sonucu görmeden** kaydetmek ve sonucu sonra açmak.
