# GOLD — Orta/Büyük UP–DOWN Olayları ve Aylık Kalıcı Öğrenme

> **14 Ekim 2026 SON GÜNCEL BELGE HİYERARŞİSİ:** [ANA-01](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) tek yönetim manifesti; [OLAY-02](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) **ana haber+veri+vaka araştırması manifesti**, [ÖĞREN-03](EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md) sonuç hipotez sicili, `months/YYYY-MM/STATE.json` **DURUM-04**. Bu README **teknik saklama rehberidir, beşinci manifest değildir**. Aşağıdaki 14 Ekim eski V0 notları kendi test tarihlerinde kalır; Ocak 5–13 UP/Şubat 1–24 DOWN vakalarının bağımsız araştırma dosyaları OLAY-02'de bağlıdır. Kullanıcının son talebindeki Claude **bağımsız çapraz denetimi** 14 Ekim'deki eski 'yalnız GPT' ara kaydının yerine geçer; izin/veri gizliliği ayrı kontrol edilir.

**Sürüm:** 2026-10-14 · **Durum:** JAN_2023_V0_MISALIGNED_BASELINE_ARCHIVED / EVENT_STRATEGY_NOT_RUN · **Güncel amaç:** [ana manifest](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) ve [olay odaklı yeniden başlangıç protokolü](EVENT_DRIVEN_MEDIUM_LARGE_MOVE_RESTART_CONTRACT_20261014.md).

## Tek saklama prensibi

**Ana manifest = hedef ve bilimsel kurallar, burada ise = çalışmanın üretilebilir kayıtları.** Chat mesajı, model hafızası veya tek aylık Markdown raporu algoritma hafızası değildir. Kalıcı öğrenme için verinin, hesaplamanın, kodun, kararın ve hataların izlenebilir dosya/kayıt olarak saklanması gerekir.

| Yeri | Saklanan | Değişim disiplini |
|---|---|---|
| `EVENT_REGISTRY.json` | Olay kimlikleri; 2023–2026 çapraz yıl benzerlik ve karşı-vakalar; kaynak referansları | Tek olayı farklı yıllarda yeniden kullan; fiyat kümeleri bağımsız ekonomik olay sayılmaz; eski etiket/yeni yorum ayrımı |
| `METHOD_REGISTRY.json` | Özellik ve algoritma kimlikleri; kod yolu, commit, girdi, parametre, deney, başarısız/başarılı sonuç, versiyon | Gerçek kod geliştirilince kayıt ekle; değişen sürümü eskisinin üzerine yazıp kanıtı silme |
| `months/YYYY-MM/STATE.json` | Aylık analiz durumu, olay ve kaynak kimlikleri, sayısal deney, yapay zekâ eleştirisi, test/istatistik, açık sorular ve **sonraki aya devredilecek** dersler | Başlangıçta boş durum; tarihsel bulgular araştırıldıktan sonra gerçek değerleri işle; her kayda evidence_id |
| `AI_REVIEW_PROTOCOL.md` | Yapay zekâya sunulacak kanıt şeması, ikinci görüşün soruları, durma/itiraz ve kalite testleri | Prompt sürümü değişince experiment run karşılaştırması sakla |

**Ham / yüksek hacimli ve lisanslı piyasa veri satırları GitHub'a aktarılmaz.** Kaynak veri zaten bağlı Neon/diğer izinli depoda; burada yalnız gizli veri içermeyen veri kümesi kimliği, şema, as-of/vintage açıklaması, SQL/ETL kod referansı, satır sayısı, içerik hash'i ve sayısal toplulaştırmalar bulunur. Repo kamuya açık olabilir. Erişim anahtarı, özel fiyat tablosu dökümü, kişisel işlem ve banka bilgisi GitHub'a veya haricî modele gönderilmez.

## Aylık geçiş

1. **Ocak 2023** V0 referansı arşiv olarak saklanır; olay temelli **orta/büyük UP/DOWN, başlamış hareket ve maliyet-sonrası BUY/SELL/HOLD/WAIT** yeniden çalışılmadan ay TAMAMLANDI sayılmaz. FULL_HISTORY_DISCOVERY kipinde 2024/2025/mevcut 2026 olayları açıklama ve karşı-vaka için kullanılabilir, tarihsel emir simülasyonunun önbilgisi sayılamaz.
2. Sayısal algoritmanın giriş/vintage, üretilmiş özellikler, yöntem sürümü ve test sonucu, **bulgu seviyesine uygun** şekilde kaydedilir. Kod varsa repoda gerçek dosya ve git commit hash'i gösterilir. Sadece sözel bulgu algoritma sürümü değildir.
3. Yapay zekâ ikinci incelemeyi **algoritmanın önceki kararını, kaynakları ve karşıt vakaları** görerek yapar; orijinal veriyi sessizce değiştiremez. Kaydedilen yorum `AI_REVIEW_PROTOCOL.md` sözleşmesine uyar.
4. Ay sonu `handoff_to_next_month`: desteklenen, reddedilen, henüz teyitsiz kurallar; kullanılan yöntem sürümleri; başarısızlıklar, eksik veri, araştırılacak soru ve yeni deneyler aktarılır. **Ocak olay-stratejisi tamamlandıktan sonra Şubat aynı snapshotı okuyarak** başlar; eski V0 ve yeni strateji ayrı deney olarak korunur.
5. **Kip A keşif:** Geçmişin tüm yılları kullanılabilir, sonuçlar `EX_POST_DISCOVERY` etiketlidir. **Kip B as-of:** Görülmüş yıllardaki mekanizmalardan kör performans iddia edilmez; ayrı donmuş yöntem ve görünmemiş dönem gerekir.

**Kalite kararı:** Tek aylık iyi oran yöntemi 'kanıtlanmış' yapmaz. Negatif ve olaysız kontrol, posthoc optimizasyon kaydı, kaynak ilk yayını, yıl/volatilite rejimi değişimi ve çoklu hipotezler saklanır. Sadece yazılmış kayıtlar otomatik eğitim verisi sayılmaz. Aylık yorum ya da yapay zekâ görüşü, doğrulanmış nicel modelin ağırlıklarını kendiliğinden güncellemez.

## Bugünkü gerçek durum

Bu dizinde **Ocak 2023'ün gerçek 31 günlük hesaplanmış V0 sayısal simülasyonu ve GPT kanıt eleştirisi kayıtlıdır**: [tam aylık sonuç](months/2023-01/JAN_2023_FULL_MONTH_GPT_ONLY_SCIENTIFIC_AUDIT.md), [gün gün 31 UTC](months/2023-01/JAN_2023_31_UTC_CALENDAR_DAYS_ACTIONS_NAV.csv), [20 tam/1 kısmi NY17 seansı](months/2023-01/JAN_2023_21_NY17_SESSIONS_VOL_AND_DECISIONS.csv), [simülasyon sonuç JSON](months/2023-01/JAN_2023_100USD_RESULTS.json), [Şubat devir durumu](months/2023-01/STATE.json). 100 USD → **101,9695 USD**; aynı maliyetle altın pasif **103,7589 USD**; vol-filtresi 20/20 seansta fark yaratmadı, çalışma model üstünlüğü veya gelecek şok olasılığı doğrulaması değildir. Yalnız **GPT yorumlama** kullanılmış, başka AI API çağrılmamıştır; otomatik sürekli çalışan uygulama hâlâ geliştirilmemiştir.


## 14 Ekim amaç düzeltmesi — korunmuş V0, henüz yapılmamış asıl deney

Eski V0 (`$101,9695`) **günlük momentumla pozisyon değiştirme deneyidir; ekonomik olarak anlamlı orta/büyük UP/DOWN olaylarının giriş/çıkışını araştıran strateji değildir**. `$103,7589` pasif altın karşılığıyla aynı satırda tutulur fakat bu farkı asıl sistemin başarısızlığı olarak yorumlamayız. `months/2023-01/STATE.json` içindeki `objective_alignment_audit` ve yeni deney sözleşmesi bağlayıcıdır. Şubat'a doğrulanmış strateji devri **beklemede**.

## Ocak 2023 ikinci deney — orta/büyük olay tarama V1

[31 gün eylem, kaynak/karşı kanıt ve sonuç raporu](months/2023-01/JAN_2023_EVENT3_FULL_31DAY_RESEARCH_REPLAY_20261014.md) · [Günlük NAV/olay CSV](months/2023-01/JAN_2023_EVENT3_31DAY_ACTIONS_NAV_20261014.csv) · [Maliyetli sonuç JSON](months/2023-01/JAN_2023_EVENT3_EXPLORATORY_RESULTS_20261014.json). +3/-3 beş seanslık fiyat olayı: 4 Ocak UP tespiti, 1 AL, 31 Ocak yalnız dönemsonu muhasebesi için SAT; 100 → **101,9914 USD**; aynı kaynaktan pasif altın **103,7589 USD**. **Sayılar tam çalıştırılmış tek-ay fiyat-only exploratory baseline'ıdır; GPT ekonomik olay yorumunun emirleri değiştirdiği veya maliyet-sonrası faydayı artırdığı kanıtlanmadı.** Aynı ayın önceki V0 kaydı korunur. Aylar arası strateji aktarımı yalnız sınırı doğru etiketlenmiş bilgiye dayanır.

## Gün-gün 15 dakikalık as-of kontrol (sadece ilk gün, 2 Ocak 2023)

[2 Ocak kaynak/olay/sinyal/karar raporu](months/2023-01/days/2023-01-02/JAN02_2023_SINGLE_DAY_15M_EVENT_EVIDENCE_AUDIT_20261014.md) · [96 kontrollük CSV](months/2023-01/days/2023-01-02/JAN02_2023_TRT_96X15M_ASOF_CHECKS_20261014.csv) · [kanıt JSON](months/2023-01/days/2023-01-02/JAN02_2023_TRT_EVENT_ASOF_RESULT_20261014.json). Türkiye saatiyle 96 periyotta vendor XAU BID/ASK yeni kayıt **0**, BIST yerel açık ama US/SGE tatil; 100$ nakit → 100$, işlem yok. 2 Ocak UTC 23:00 veri başlangıcı **3 Ocak Türkiye saati 02:00** olduğundan 2 Ocak bilgisi gibi kullanılamaz. **Daha sonraki günler bu as-of günlük taramada çalışılmadı.** Bu günlük karar muhasebesi, yukarıdaki geriye dönük tam-ay fiyat-only V0/V1 performansından farklı ve bağımsız çalışma katmanıdır.

## 3 Ocak 2023 — Küresel haber / 96×15 dakika as-of kontrol
[Detay](months/2023-01/days/2023-01-03/JAN03_2023_SINGLE_DAY_CAUSAL_MARKET_REPLAY_20261014.md) · [96 kontrolün türetilmiş gözlem/karar CSV'si](months/2023-01/days/2023-01-03/JAN03_2023_TRT_96X15M_CAUSAL_DECISION_LEDGER_20261014.csv) · [Olay/GPT meta JSON](months/2023-01/days/2023-01-03/JAN03_2023_EVENT_GPT_DECISION_RESULTS_20261014.json). TRT 00:00–23:45, **88 bar başlangıcı, 87 o güne kadar kapanmış M15**, 9 gözlemlenemeyen kontrol; XAU, ZN/NQ/CL as-of, Reuters Caixin PMI, altın/faiz, Almanya CPI, ABD imalat PMI+inşaat verisi, 2022 CPI/Fed analoğu. **BIST birincil/yardımcı XAU/USD açıklayıcısı olarak ÇIKARILDI.** İlk gün 100 USD nakit → 3 Ocak 100 USD nakit; maliyet-sonrası büyük fırsat kanıtı yetersizdi. Bugünkü GPT geriye dönük vaka kararlarının ileri tahmin ispatı olmadığı net. 4 Ocak 15m kayıt henüz çalıştırılmadı.

## 4 Ocak 2023 — karar adayı için 1 dakikaya inme, gün sonunda GOLD
[96×15m + M1 raporu](months/2023-01/days/2023-01-04/JAN04_2023_CAUSAL_GPT_BUY_REPLAY_20261014.md) · [15m gözlem/karar CSV](months/2023-01/days/2023-01-04/JAN04_2023_TRT_96X15M_EVENT_AND_MINUTE_LEDGER_20261014.csv) · [M1 olay tarama](months/2023-01/days/2023-01-04/JAN04_2023_MINUTE_EVENT_SCAN_20261014.csv) · [başlangıç/bitiş pozisyon JSON](months/2023-01/days/2023-01-04/JAN04_2023_CAUSAL_BUY_RESULT_20261014.json). 10:20 TRT **BUY (reconstructed as-of minute decision)**, 10:21 M1 BID/ASK-makas vekili $1851.34994; 0.8% alış ücreti sonrası 0.053582523 oz. End-of-day **$99.2305 BID-mark**, $98.4367 hypothetical after-sale NAV; *no sale executed*. M1 risk trigger only after M15 candidate; no hindsight minute extrema. 4 Ocak Fed 22:00 TRT minutes and ISM/JOLTS 18:00 TRT decision as-of. BIST excluded. **5 Ocak henüz yeni protokolde çalışılmadı.**

## Ocak 2023 — Büyük olay stres günlerine öncelik (5–6 Ocak)
[İki gün 192×15m + M1 haber akışı](stress_cases/2023-01/JAN_2023_TOP_VOLATILITY_DIRECTIONAL_STRESS_AUDIT_20261014.md) · [Tüm Ocak volatilite sıralama](stress_cases/2023-01/JAN_2023_VOLATILITY_RANKING_20261014.csv) · [Günler arası maliyetli alternatif NAV](stress_cases/2023-01/JAN05_JAN06_2023_STRESS_RESULTS_AND_COUNTERFACTUAL_20261014.json). Ocak 2023 en yüksek range **6 Ocak UP**, en büyük DOWN **5 Ocak**; başlangıç GOLD Jan4 0.053582523 oz. 5 Ocak teyitli DOWN sonrası satış yapmamak, 6 Ocak NFP/ISM UP sırasında hâlihazırda GOLD bulunmak: **6 Ocak BID-mark $100.0734, teorik likidasyon $99.2728**. BIST sinyali yok. Hindsight stress-date selection and GPT subjectivity explicitly marked. Other days not evaluated in new stress-mode yet.

## ÖNEMLİ DÜZELTME — asıl şok ≠ tek günlük volatilite
[Ocak 2023 15m kronolojik yönlü çok-günlü olay atlası](stress_cases/2023-01/JAN_2023_MULTIDAY_DIRECTIONAL_EVENT_ATLAS_CORRECTION_20261014.md). 5–6 Ocak daily range stresleri geçerli yardımcı incelemeler ama ana **≥%3 UP/DOWN veya ≥%2 hızlı olay** araştırma evreninin tam temsilcisi değildir. Örnek 5–13 Ocak +%5.190 UP, 11–16 Ocak +%3.131 UP, 26–31 Ocak -%2.350 DOWN; Ocak'ta -%3 olayı yok. Epizotların uçları ex-post, sinyal zamanı değildir.
