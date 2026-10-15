# CASH→GOLD→CASH — Ocak 2026 strateji araştırması / 15 Ekim 2026

**Durum:** RETROSPEKTİF ARAŞTIRMA, CANLI STRATEJİ ONAYI YOK.
**Dal:** `research-gold-cash-gold-strategy-20261015`.
**Amaç:** 1 Ocak 2026'da 100 USD nakitte başla; sonraki kapanmış veriyle
AL / ALTIN TUT / SAT / NAKİTTE BEKLE; kısa satış veya kaldıraç yok.
**Hedef:** 4 saatlik yön tahmini değil, değişken süreli pozisyon yönetimi.

## 1. Kural ve veri sözleşmesi

XAUUSD M15, Neon `gold_research_histdata_xau15m_candidate`. Yalnız
`native_minute_bars=15` ve veri kesintisizken türetilmiş **3 saatlik**
karar noktaları. Karar (t) yalnızca `bar_end <= t` tamamlanmış
barlara dayanır; varsayımsal fill `t` saatinde başlatılan ilk tam
M15 barının `open_price` değeridir. Banka ASK/BID veya piyasa
emir gecikmesi kayıtları değildir.

- AL: Son 92 tam bar getirisi en az **+%1**, son 276 bar getirisi
  en az **%0**, son 16 tam bar getirisi >= **−%0,25**,
  son üç günün gözlenen zirvesinden uzaklık >= −%3,5,
  son 92 bar fiyat aralığı <= %4, son satıştan 12 saat bekleme.
- SAT: Pozisyondaki gözlenen fiyat zirvesinden **%3,5** geri çekilme;
  VEYA 16-bar fiyat hareketi <= −%2;
  VEYA 92-bar getiri <= −%2 ve 16-bar getiri negatif;
  VEYA 276-bar getiri < −%2 ve 16-bar getiri < −%0,5.
- Doğrulanmış makro açıklama takvimine göre giriş öncesi 6 saat ve
  sonrası 3 saatlik **ayrı ve opsiyonel** giriş engeli test edildi.
  2023–2024 seçiminde en iyi politika bu kapıyı **kapalı** seçti.
  Bu nedenle aşağıdaki Ocak ticaret başarısını OLAY/ÖĞREN'in
  nedensel tahmini olarak göstermek **YANLIŞTIR**.
- Sinyal sonrasında fiyat 15 dakikalık ilk barın açılışından
  gerçekleşmiş varsayılır; satım kararının fiyatıyla
  kapanışta önceden işlem yapılmış kabul edilmez.
- Her alış/satışta nakit tutarından veya satış hasılatından
  ayrı ayrı **%0,8** kesilir. **Banka makası, USD/TRY ve
  bankanın kendi gram altın fiyatı, vergi, slipaj YOK**.
  Sonuç bu nedenle iyimser bir *XAUUSD vekil portföyüdür*.

**Parametre seçimi:** 2023 ve 2024 üzerinden çoklu kural grid
araması + minimum yıllık kâr / iki yıllık ortalama / max drawdown /
işlem sayısı cezası; **Ocak 2026 fiyatı seçim fonksiyonuna sokulmadı**.
2025 ayrı doğrulama, Ocak 2026 retrospektif ileri dönem denemesi.
Buna rağmen Ocak fiyatları daha önce araştırıldığı için tam kör
OOS olduğu iddia edilemez.

## 2. 2026 Ocak: Gerçek karar günlüğü (TSİ)

| Saat | Durum | Sinyal açıklaması | XAUUSD vekil fill |
|---|---|---|---:|
| **5 Ocak 2026, 18:00** | **NAKİT→ALTIN AL** | 92-bar getiri +%1,900; 276-bar +%1,485; 16-bar −%0,002; yükseliş teyidi | **4435,998 USD/oz** |
| 6 Ocak–29 Ocak 18:00 | **ALTIN TUT** | Satış koşulu görülene kadar bekle | — |
| **29 Ocak 2026, 21:00** | **ALTIN→NAKİT SAT** | 16-bar getiri −%3,190; zirveden dinamik geri çekilme >=%3,5 | **5334,475 USD/oz** |
| 29 Ocak sonrası–31 Ocak | **NAKİTTE BEKLE** | Yeni giriş koşulu yok | — |

**Komisyonlu portföy:** 100,00 USD → **118,33785 USD (+%18,33785)**,
bir AL + bir SAT. Ocak boyunca strateji örneklemindeki maksimum
varsayımsal tasfiye-edilebilir özkaynak geri çekilmesi yaklaşık **%4,096**.
Gerçek banka ASK/BID ile teyit edilmemiştir.

**Eş ankrajlı buy-and-hold** (araştırma kodunun ilk ve son uygun
3-saatlik checkpoint fill/close zamanı) 100,00 → **110,57807**
(**+%10,57807**) çıktı; başlangıçta kısa 1 Ocak tatil parçası
bulunuyor. Daha doğal bir normal seans kıyası olarak ilk 2 Ocak
seans açılışı 4323,698 ve 31 Ocak 01:00 TSİ tam altın bar kapanışı
4891,195 kullanılırsa aynı iki komisyonla 100 → **111,32250** olur.
Bunlar iki ayrı ankrajdır, birbirleri yerine gösterilemez.

**Maliyet duyarlılığı (gerçek banka makası değil, SENARYO):**
Ek +%0,2 her yön: 117,87; ek +%0,5 her yön: 117,16;
ek +%1 her yön: 115,99. Bu düzeltmeler basit fiyat kotasyon
makası senaryolarıdır; gerçek bankanın gram/TRY alış-satış ekranının
yerine geçmez.

## 3. Aynı seçilmiş politika: Ön dönem performansı

| Yıl | Strateji % (komisyon sonrası) | Aynı başlangıçlı altın tutma % | Tur |
|---|---:|---:|---:|
| 2023 (**parametre geliştirme**) | **−%5,30** | +%10,98 | 10 |
| 2024 (**parametre geliştirme**) | **+%7,37** | +%25,14 | 9 |
| 2025 (**ayrı doğrulama**) | **+%15,48** | +%62,13 | 15 |
| Ocak 2026 (**retrospektif ileri test**) | **+%18,34** | +%10,58 (aynı saat) | 1 |

**Kritik hüküm:** Ocak 2026'daki iyi sonuç, stratejinin
2023–2025 döneminde sürekli altın tutmayı belirgin ölçüde
geride bırakamaması nedeniyle **robust kârlılık kanıtı değildir**.
2023'te doğrudan zarar etmiş; 2025'te %20,9 seviyesinde
portföy max drawdown üretmiştir. Kullanıcıya henüz canlı
AL/SAT sistemi olarak önerilmez.

## 4. OLAY-02 / ÖĞREN-03 bağının gerçek durumu

Olay takvimi `MACRO_RELEASE_CLOCKS_RESEARCH.csv` dosyasında
88 makro olay saatinden oluşuyor: 2023–2025 araştırması için
85 geçmiş CPI/NFP/FOMC tarihi, Ocak 2026 için resmi BLS NFP
(9 Ocak 16:30 TSİ), CPI (13 Ocak 16:30 TSİ), Fed açıklaması
(28 Ocak 22:00 TSİ). Bu saatler pozisyon adayında
yaklaşan-bilinen-olay risk engeli olarak kullanılabilir; ancak
seçilmiş araştırma kuralı bu özelliği etkinleştirmedi.

**OLAY-02'deki 96 olay → ÖĞREN-03'ün 12 ORG mekanizması → 15 dk
oranlar → maliyetli portföy kararı** henüz doğrulanmış
nedensel bir uzman karışımına dönüştürülmemiştir.
Tüm geçmiş olayların ilk yayın saati, USD/reel-faiz/metal
karşı tepkisi ve banka kotasyonu eksiktir.
Gerçek ekonomik neden kanıtı olmayan olaylar `UNKNOWN`.
9 Ocak NFP için eşleşme fikri var, fakat Ocak politikasındaki
5 Ocak AL / 29 Ocak SAT kararlarını bu bilgi vermedi.

Bu nedenle **fiyat tabanlı risk yönetimi prototipi** ile
**tarihli ekonomik olay öğrenmesi** birbirine karıştırılmayacak.
İkinci katmanın değerini göstermek için fiyat-kuralı üzerinde
ayrı, kilitli, OOS performans artışı gerekir.

## 5. Denetim ve dosya otoritesi

- Kod: `cash_gold_policy.py`
- Doğrudan Neon'dan as-of türetilmiş girdiler:
  `ASOF_3H_XAU_CHECKPOINTS_2023_JAN2026.csv` (5999 kontrol).
- Makro açıklama saatleri: `MACRO_RELEASE_CLOCKS_RESEARCH.csv`.
- Fiyatı önceden bilen karar yasağı, çift yön ücretleri,
  tatil ve eksik bar kısıtları: `test_cash_gold_policy.py`.
- Tam rapor ve tüm günlerin durumları CI çıktısı
  `strategy_result.json` olarak GitHub Actions artifact'inde;
  ayrıca stdout'ta işlenen politika ve 2026 işlem defteri mevcut.
- Bu dosya **yeni manifest değildir**. ANA-01, OLAY-02,
  ÖĞREN-03 veya geçmiş Ocak deney kayıtlarına dokunulmamıştır.
