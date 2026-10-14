# OLAY-02: 20 Ocak 2026 tam-gün M15 as-of araştırma defteri (yeniden başlangıç)

**Kapsam:** Türkiye saatiyle 20 Ocak 2026 00:00–23:45, tam 96 **planlı** kontrol. **Tek gün tamamlandı; 21–31 Ocak incelenmiş sayılamaz.**
**Kanıt sınıfı:** HISTORICAL_REPLAY_NOT_BLIND_OOS, RESEARCH_ONLY; artık geçmiş veriler bilindiği için prospektif veya kör test değildir.
**Üst belge otoritesi:** [ANA-01](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) → [OLAY-02](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) → [ÖĞREN-03](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md).
**Ek:** [96 kontrolün makine-okunur karar/kanıt cetveli](OLAY_02_2026_OCAK20_96_ASOF_RESEARCH_LEDGER_20261015.csv).
**Silinmiş Ocak 2026 deneyinin sonuçları bu analizin girdi verisi olarak kullanılmadı.** Sadece ayrı kaynak ham geçmiş fiyat ve 2023–2025 ekonomik hipotezler kullanıldı.

## 1. Başlangıç koşulları ve karar sorusu
Araştırmacı **20 Ocak 00:00 TRT** noktasındadır. Birleşik açıklama 19 Ocak'tan kalma ABD–Avrupa Grönland/tarife gerilimidir. Başka bir ülkeden gelen risk ile genel riskten kaçış, USD/ABD varlıklarından kaçış, tahvil piyasası likiditesi ve tamamen pozisyon kaynaklı momentum ayrıştırılacak. Mevcut portföy kullanıcının kaydında kesinleşmediği için **iki koşullu portföy durumu** ayrı yürütülür: zaten GOLD tutan kişi ve CASH tutan kişi. Tarihsel işlem kararı kullanıcı hesabında uygulanmış sayılmaz.

Uygulama maliyet sözleşmesi: alışta %0,8, satışta %0,8; iki yönlü teorik fiyat eşiği **%1,6194 + ASK/BID, slipaj, kur ve banka saati sürtünmesi**. İşlem yapılmadığında dahi karar ve fırsat maliyeti ölçülür. İşlem adayını gerçek emirden ayrıştır: `RESEARCH_ONLY`.

## 2. Veri ve bağımsız kaynak uyarıları (koşunun temel bulgusu)
Neon tablosu: `public.gold_research_histdata_xau15m_candidate`, `public.gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` ve `public.gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c`; erişim salt okunur. 96 kontrol saatinde HistData tam 15-dakika: **86**; cari fiyat yok: **9**; doğrulanmamış ayrı BID serisinden gelen geçerli-asıl-fiyat-dışı kontrol: **0**. NQ/ZN saatlik temkinli `ts_event+60m<=slot` bilgisi **89** kontrol noktasında gözlenebiliyor (bu, vendor yayın gecikmesinin bağımsız doğrulaması değildir).

**Bağımsız kaynak gibi gösterme yasağı:** Tam Ocak ortak saatli 1.644 fiyat eşleşmesinin 1.643'ünde `dukascopy.bid_close==histdata.close_price` (kayan nokta tam eşit); `m1_matched=1` kaydı **0**; `source_vintage` 2026-10-08, dolayısıyla geçmiş 20 Ocak'ta indirilmiş orijinal veri değildir. Bu etiketli BID/ASK serisi **BAĞIMSIZ DUKASCOPY DOĞRULAMASI/GERÇEK BANKA KOTASYONU DEĞİLDİR**. 20 Ocak özelinde 82 ortak saatten 82 tanesinde BID=HistData görünür. `SI.c.0` saatlik örnekleri çok düşük hacimli ve seyrektir, tek başına bağımsız gümüş teyidi olarak kullanılmaz. `ZN.c.0` **tahvil vadeli FİYAT serisidir**, tahvil faizi/reel faiz değildir. Fiyat barı, interval **başlangıcına** yazılmış; sadece bitiminde (`+15 dakika`) alınır.

**00:00 TRT:** o noktada geçerli tamamlanmış yeni M15 bar yok. 19 Ocak 22:00 TRT son geçerli HistData barı ile 00:00 arası taze fiyat boşluğu vardır; 19 Ocak 22:15 barının `native_minute_bars=14` olması nedeniyle kullanımı yasak. İlk gün içi 15m tam kaynak 02:15'te gelen **4670.348** HistData close; otomatik işlem kotasyonu sayılmaz.

## 3. İlk yayımlanma/erişilebilirlik kontrollü haber sicili
- **19 Ocak önceden bilinebilir:** Reuters piyasa haberi, Grönland bağlamındaki ABD'nin Avrupa'ya yeni tarifeleri, altının güvenli liman olarak yükselişi, hisse vadeli endekslerinin kaybı ve doların zayıflaması. Kaynak (19 Ocak güncellendi): https://www.investing.com/news/stock-market-news/wall-street-futures-skid-dollar-dips-on-us-tariff-threats-4453255
- **20 Ocak 07:15 TRT'den itibaren temkinli:** Reuters'ın yayımlanma zamanı 01:44 GMT ve *değiştirilmiş içeriği* 04:04 GMT (07:04 TRT) olan altın haberi: https://uk.marketscreener.com/news/gold-holds-near-record-high-as-trade-war-risks-sour-global-sentiment-ce7e58dcdb8df422
- **20 Ocak 09:45 TRT'den itibaren temkinli:** Reuters Singapur piyasa raporu 19 Ocak 21:10 EST'de yayımlandı, 20 Ocak 01:42 EST'de (09:42 TRT) değiştirildi. Tam değişmiş versiyon ancak bu andan sonra kullanılabilir: https://www.marketscreener.com/news/stocks-slide-dollar-struggles-as-trump-s-greenland-gambit-rattles-markets-ce7e58dcdb8cf721
- **20 Ocak 16:15 TRT'den itibaren temkinli:** Reuters Avrupa piyasa raporu 06:01 EST'de yayımlandı, 08:00 EST'de (16:00 TRT) değişti: https://www.marketscreener.com/news/european-stocks-fall-dollar-drops-markets-focus-on-trump-s-tariff-threats-ce7e58dcdc80f625
- Bu haberler **gazetecinin sonraki açıklamasıdır; tarife politikasının resmî ilk duyurusu değildir**. Değiştirilmiş yazı, ilk yayımlanma saatine geri taşınamaz. Daha kapsamlı orijinal firstprint yayını, dakika bazlı tüm haber akışı, CFTC/ETF verisinin o andaki mevcudiyeti ve DXY/UST2Y/reel faiz aynı UTC çaprazı **eksik**. Dolayısıyla `NO_SOURCE_VERIFIED_FIRSTPRINT` asla 'o dakika haber hiç yoktu' anlamına gelmez.

## 4. Zaman boyunca dedektifin gerçekleşmiş *as-of* muhakemesi
Her 15 dakikalık kayıt işlenmiştir; **derin yorum yeni maddi fiyat/ekonomik kanıt görülen kontrol aralıklarında** yapılmıştır. Satır sayısı kadar bağımsız GPT analizi yapıldığı iddia edilmez.

| Kontrol (TRT) | Tamamlanmış XAU 15m (HistData close, USD) | O ana kadar öğrenilebilir şema ve rakip | Eğer GOLD / eğer CASH |
|---|---:|---|---|
| 00:00 | Kayıt yok | 19 Ocak tarifesi G02/G03 adayı, fakat bu kontrol için taze fiyat yok. **Haber biliniyor; yeni teyit yok.** | WAIT / WAIT |
| 02:15 | 4670.348 | İlk tamamlanmış fiyat. 19 Ocak risk primi devam ediyor olabilir; NQ/ZN taze H1 açık değil. | HOLD_GOLD / HOLD_CASH |
| 04:00 | 4660.095 | İlk gün içi zayıflık, tarife→kesintisiz UP otomatik kuralını reddet. G06 geri çekilme rakibi. | HOLD_GOLD / HOLD_CASH |
| 07:15 | 4680.185 | Reuters güncel yorum mevcut; G02 politika riski UP adayı. Bağımsız *yeni resmî ilk haber* yok; NQ tepki yönü henüz tekil kesinlik sağlamıyor. | HOLD_GOLD / HOLD_CASH |
| 09:15 | 4712.905 | Fiyat 4.700 üstüne çıktı. G02/G03 devam adayı; tarihten sonraki fiyatlar bu karara karışmadı. Kalan hareketin komisyonu aşması kalibre değil. | HOLD_GOLD / HOLD_CASH |
| 11:15 | 4724.305 | NQ.c.0 önceki tamam H1 saatlik fiyatı 25284.2500, ZN.c.0 111.56250: hem hisse risk hem tahvil fiyatı zayıflarken altın güçlü. **G01 salt düşen faiz açıklaması zayıflıyor; G02/G03 güvenli liman rakibi güçleniyor, doğrudan nedensel ispat yok.** | HOLD_GOLD / HOLD_CASH |
| 16:15 | 4723.298 | Avrupa geriliminin sonraki haberleri; gün içi konsolidasyon/dönüş riski. G06 pozisyonlanma rakibi sürüyor; sırf haber sayısına AL olmaz. | HOLD_GOLD / HOLD_CASH |
| 20:15 | 4753.825 | Güçlü yukarı devam görülüyor ama önceki artış yeni beklenen kazanç değildir. NQ kısmen toparlıyor, doğrudan güvenli liman korelasyonu mutlak değil. | HOLD_GOLD / HOLD_CASH |
| 23:45 | 4749.525 | Gün sonu ölçümü yalnız **karar sonrası test** olarak kaydedildi. Bu fiyat daha önceki kontrollere tahmin girdisi yapılamaz. | HOLD_GOLD / HOLD_CASH |

G03 (jeopolitik) ve G02 (ticaret) birbiriyle örtüşebilir; mekanizma çatışmasında G01 düşen faiz yorumu tahvil **fiyatı** sinyaliyle karşıtlık gösterdi. G06 kaynaklı devam/yorulma doğrudan emir/pozisyon verisi olmadan ispatlanmaz. `P0/P2/P3` etiketleri olasılık veya kesin evre doğrulaması değildir.

## 5. Sayısal sonuç ve yatırım kararının sınırı
Bu günün ilk geçerli gözlemi **4670.348**, 23:45'te son erişilebilir kapanış **4749.525**. Gözlenen kaynak içi değişim **%1.695**. 09:15 (4712.905) → 23:45 (4749.525) sonraki değişim **%0.777**; bu aralıkta gerçekte işlem yaptığı iddia edilmiyor. 09:15'te alıp yalnız aynı gün 23:45'te satmak varsayımı, salt fiyat farkı düzeyinde bile **%1,6194 komisyon eşiğinin altında**; ASK/BID eklenince daha da zorlaşır. 23:45'i ex-post zorunlu tasfiye saati yapmak analitik bir duyarlılık analizidir, önceden seçilen gerçek SAT değildir.

**Dürüst ekonomik karar:** Daha önce GOLD taşıyan portföyde **HOLD_GOLD**, yalnız CASH portföyünde **HOLD_CASH / gün içi yeni AL yok**. Bir günlük risk primi artışının daha çok gün süreceği kalibre edilmediği ve 'Dukascopy' ASK/BID gerçek/bağımsız doğrulanmadığı için açık `BUY/SELL` talimatı üretmek bilimsel gerekçesiz olur. Kaçırılan yükselişin fırsat maliyeti ayrıca etiketlenir: bu, kararın *mutlaka iyi* olduğu anlamına gelmez; gelecekte bağımsız daha iyi kural için karşılaştırma sinyalidir.

**Kesin sonuç olmayanlar:** 20–31 Ocak 12 günlük yatırım getirisi, 31 Ocak nihai NAV, ilk politika haberi ile fiyat hareketi arasında ispatlanmış nedensellik, gerçek banka kotasyonuna göre kâr, canlı işlem emri, çoklu-ay OOS başarı. Hiçbiri bu tek günlük defterle yapılmış sayılmaz.

## 6. Araştırma denetimi ve aktarım protokolü
- İçgörü, ÖĞREN-03'ün mevcut sözlüğüne *doğrudan doğrulanmış kural olarak eklenmez*. 'ABD kaynaklı tarife/kurumsal şoklarda altın yükselirken tahvil fiyatları düşebilir; G01 ters-faiz sinyali ile G02/G03 güvenli liman kanallarını ayrı incele' araştırma hipotezi burada tarihli OLAY-02 altında kalır.
- Aynı 2023–2025'te G02/G03 olarak sınıflandırılmış benzer/ters olaylar ve hiçbir şok olmayan kontrol günleri ile ilk-haber/çapraz-varlık saatlerini tutarlı eşleştirmeden yeni banka alım yetkisi açılmaz.
- `HISTDATA==DERIVED_BID` kaynak çoğaltması bağımsız 2 teyit gibi sayılmaz. Gerçek banka ASK/BID ve 1m teyidi eksikken de `EXECUTABLE=FALSE`.
- Sonraki gün için saklanan salt hipotez: eskalasyon sürer mi, NQ/ZN ayrışması genişler mi, fizikî/rezerv akışı farklı mı, diplomatik gevşeme geldiyse G02 primi söner mi? **21 Ocak haber/fiyatı bu defterin önceki kararlarına asla geri yazılmaz.**

### Kaynak ve yeniden üretim notu
Rakamlar sorgu tarihinde Neon salt okunur tablolardan, iki tarih damgası eşit olan barlar ve H1 için varsayılan tam bar kapatma gecikmesiyle çıkarılmıştır. Tablonun üretim kökeni ek delil olmadan bağımsız sanılmamalı. CSV 96 sıralı TRT kontrolünü ve veri/kanıt/gerekçe ayrımlarını muhafaza eder. Analiz kaynakları yalnız 19–20 Ocak'ta o anda erişilebilirliği makul biçimde sağlanmış makalelerdir; kapsamlı bir haber terminali arşivi değildir.
