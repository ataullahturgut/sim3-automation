# GOLD-ADAPTIVE-MODEL-APP-01 — S3 ilk net pozisyon-değeri katmanı (16 Ekim 2026)
**WORKSTREAM=MODEL | S3_DEV=IMPLEMENTED | S3_SCIENCE=NOT_PROVEN | S1_SCIENCE=FAIL | S2_SCIENCE=PENDING | U1=UNCHANGED**
## Kurulan
- Mevcut `adaptive_market_core_s1_s2.js` köprüsüne aynı matematiksel CORE içinde S3 `adaptive_position_value_s3.js` bağlandı; üçüncü bir bağımsız strateji/uygulama projesi **yaratılmadı**.
- Öğrenme amacı: yalnız geçmişte olgunlaşmış 15dk fiyat değişimi üzerinden `Q(state, CASH/GOLD, KEEP/SWITCH)`; gelecek getiri önceki karara sızmaz; kaynak/bar boşluğunda öğrenim yapılmaz; ekonomik firstprint eksikse S1 zorla kullanılmaz.
- S2 hızlı evre ve bir önceki tamamlanmış yavaş seans yön/evre özellikleri kullanılır. Trend yönü **AL veya SAT için elle sabit kural değildir**; iki eylemin geçmişten öğrenilen net değerleri karşılaştırılır. S2 faz/kaynak hatası as-of kapısından geçmez.
- Banka maliyeti **alışta %0,8**, **satışta %0,8**; bileşik gidiş-dönüş **%1,5936**. Kâğıt portföy başlangıcı 100 USD; net tasfiye değeri, pasif CASH ve iki-komisyonlu pasif GOLD referansları, turnover, ücret ve drawdown bilançosu. Kur farkı ve gerçek banka bid/ask fiyatı yokken bu bir **MID-proxy araştırmasıdır**.
- Seans/arşiv değişiminde shadow net değer geçersiz işaretlenir, farklı kaynak fiyatları tek pozisyon gibi zincirlenmez. `shadowResearch` isteğe bağlı ve **varsayılan kapalıdır**.
## Henüz yapılmayan
- Gerçek geçmiş veriyle S3 entegre yürüyüşü / Ocak 2023 net ücretli performans değerlendirmesi **bu commit kapsamında yapılmadı**. Testler sentetik sözleşme doğrulamasıdır; finansal kâr kanıtı değildir.
- Q critic'in 15dk güncellemeleri kendi aralarında yüksek korelasyonludur; minUpdates eşiği **bilimsel bağımsız olay desteği değildir**. Bağımsız holdout ve gerçek banka fiyatları olmadan işleme yetki verilmez.
- `action:null`, `tradeAllowed:false`, `bankTrades:0`, `scienceGate:NOT_PROVEN`. Shadow eylemi gerçek al/sat sinyali veya otomatik banka işlemi değildir.
## Sonraki deney
Yeni 2020–2025 quote-only kaynak için S2 yavaş epizot koşusunu yapıp episot/durum destek sayısı ve ablation ölç; S3'te 2023 Ocak as-of yürüyüşte CASH, GOLD-BUY-HOLD, gated critic karşılaştırmasını aynı maliyetle ölç. 2026 tamamı gizli OOS değildir. Sonucu görüp kural/eşik avı yasak.

## Ocak 2023 — GERÇEK fiyat üzerinde S3 mühendislik smoke (2026-10-16)
Aynı S1+S2+S3 tek CORE bir arada, 2023 Ocak `gold_research_evduka_xau15m_bidask_candidate` BID/ASK MID salt-okunur arşiv. **1.920 M15 bar işlendi, hata yok**; 21 yavaş seans verisi alındı, 20'si kabul edildi; S2 fast 41 tamamlanmış mikro epizot, S2 slow **0 tamamlanmış uzun epizot**, S1 105 anchor/99 olgun etiket/3 prototip. S3 1.898 gecikmeli as-of 15dk güncellemesi, 21 kaynak/hafta-sonu/gap, 60 Q-state kaydı, 46 araştırma politikası değerlendirmesi, **0 shadow al/sat işlemi**.
- 100 USD nakitte başladı: shadow strateji net **100,00 USD** (işlem yok).
- Aynı ilk ve son araştırma fiyatlarında %0,8 alım + %0,8 varsayımsal çıkış sonrası pasif GOLD **103,8057 USD**, pasif nakit 100,00 USD. **Fırsat kaçırma: 3,8057 USD** (bu veri kapsamı özelinde).
- Sonuç: **S3 modelinin bu ilk veri penceresinde kârlı fırsatı yakalayabildiği gösterilemedi**. Sonuç üzerine alpha yaratmak için eşik düşürülmedi, geçmişe göre optimize edilmedi.
- Tek kaynağa ait retrospektif fiyatlar 2026'da kurtarıldı; kaynak bankaya ait değil, ilk erişim kanıtı yok. Bu **S3 mühendislik smoke**, manifestteki Ocak 2023 **STRICT S4** değildir ve kör OOS sayılmaz.
- Yeniden üretilebilir runner: `replay_position_value_s3.js` (özel M15 ve slow JSON'unu yerelde kullanır; sadece toplu sonuç/hash basar). Ham fiyatlar ve önceden eğitilmiş kârlı model GitHub'da mevcut değildir.
