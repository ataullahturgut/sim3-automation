# ALTIN FOMC ŞOK MEKANİZMASI — GERÇEK VERİYLE İLK PİLOT, VERİ KABUL DENETİMİ
13 Ekim 2026. **Bilimsel statü:** gözlemsel eşzamanlı fiyat-tepkisi çalışması; **nedensel etki kanıtı, erken uyarı veya al-sat stratejisi değil**.
**GitHub:** `ataullahturgut/sim3-automation` research branch `research-gold-fomc-mechanism-pilot-20261013`, ana dal HEAD `4ecdf810e4e76fba37d20b4a94d30d0bc54b30a3`. Claude PR #118/#119, bağımsız #120 birleştirilmedi.
**Hesap öncesi sözleşme:** `GOLD_FOMC_CAUSAL_PILOT_PRECOMPUTATION_PROTOCOL_20261013.md`.
Resmî Fed: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
Resmî USMPD: https://www.frbsf.org/research-and-insights/data-and-indicators/us-monetary-policy-event-study-database/
Pencere tanımı kaynağı: https://www.frbsf.org/wp-content/uploads/wp2025-30.pdf (Acosta vd., 2026 güncellemesi, 2.2. bölüm, basılı s.8).

## 1. Veri kabul kapısı
Neon Gold Control `observations`, `gold_research_evduka_xau15m_bidask_candidate`.
- 2020–2025 USMPD takviminde **53 kayıt**; resmî takvim ile bire bir normal iletişim sınıflandırmasında **47 olağan açıklama**, **6 özel olay** (2020-03-03, 03-15, 03-19, 03-23, 03-31, 08-27). Sonuncusu strateji çerçevesi konuşması, normal toplantı değildir. 2020 Mart olağan toplantısının iptali nedeniyle 2020 yılında 7 normal açıklama vardır. 2021–2025 yıllarının her birinde 8 açıklama.
- Normal 47 açıklamanın HER BİRİNDE ±15 dakika ile pre/post 45/105 dakika altın fiyat uç noktaları var; interpolasyon yok, alım-satım fiyatı değil **bid/ask midpoint**.
- 2020-01-29 tarihinde, 2020 başlangıçlı fiyat panelinde önceki 60 uygun kapanışın yalnız **17** tanesi bulunduğundan ön durum regresyonu için çıkarıldı. **46 tam olay**.
- USMPD `MACRO_FOMC_GSS_PATH_FROZEN2015`: 2016 öncesi faktör katsayıları dondurularak geçmiş oran değişimlerinden üretilmiş policy-PATH sürprizi, birimi `percentage_points`; **10bp = 0.10 yüzde puanı**. Ölçüm kaynakları 2026'da yüklenmiştir: t-1 anında görülmüş tarihsel bir sürpriz değildir. Günlük ön durum ise olaydan önce tamamlanmış NY17 kapanışlarından çıkartıldı.
- Birincil `Y = 100 ln(P[t+15]/P[t-15])` yüzde-log getiri. Bu 30 dakikalık M15 uç nokta yaklaşımı, **USMPD resmî t-10→t+20 penceresinin aynısı DEĞİLDİR**; altın M15 ile bu pencere tam yapılamaz. Resmî pencereyi KAPSAYAN t-15→t+30, 45 dk, ayrı duyarlılık (tam eşdeğer değil).

## 2. İlk gerçek sayısal sonuçlar
**Bütün 46 normal FOMC olayı** (büyük altın hareketleri seçilmedi, küçük ve sıfıra yakın şoklar dahil):
- GSS policy-path sürprizi ile altının eşzamanlı 30 dk getirisi Pearson korelasyonu **-0.62209**.
- Yalın olay regresyonu: +10bp açıklama-çevresi politika yolu şokuyla aynı 30 dakikadaki altın getirisinin **-0.16082 yüzde puan** değişimi eşleşir (HC3 se **0.03638**; %95 normal yaklaşık aralık **[-0.2321, -0.0895]**, istatistiksel bağımsızlık ve ölçüm varsayımları koşullu). R² **0.3870**.
- Alternatif MP1 kısa hedef sürprizi: eğim **-0.44108 yüzde puan /10bp**, HC3 se **0.25818**, daha zayıf; policy path ve hedef sürprizi özdeş değildir.
- Haber ÖNCESİ placebo pencere t-60→t-15: eğim **+0.01029 yüzde puan /10bp**, HC3 se **0.00878**; güçlü ön tepki görülmedi.
- Sonraki t+15→t+120 devam getirisi: **+0.05835/10bp**, HC3 se **0.08880**, güçlü kalıcı aynı işaretli devam kanıtı yok.
- Her yılı sırayla dışarıda tutulan 5-yıl veri kümelerindeki yalın eğim **[-0.1859,-0.1411] yüzde puan/10bp**, işaret hep negatif.
- En büyük dört mutlak altın olayı sırayla çıkarılırsa 42 olayda eğim **-0.12673/10bp**; işaret negatiftir, buna rağmen olay seçerek duyarlılık testi keşifseldir.

### Ön durum etkileşimi (Astra önerisi)
Son tamamlanmış NY17 seanstaki `r20`, önceki 60 seans getirisi SD (`sd60`), `z20=r20/(sd60 sqrt20)`. SD ve z örneklem ortalamasından çıkartılıp standartlaştırılır; `Y = α+βE+γ_1 sd60+γ_2 z20+θ_1 E*sd60+θ_2 E*z20`; E politika sürprizi /10bp.
- Ana politika katsayısı **-0.16085 (HC3 se 0.04493)**.
- `E×sd60` **-0.01133 (HC3 se 0.02865)**, güvenilir işaret/etkileşim kanıtı yok.
- `E×z20` **+0.04169 (HC3 se 0.03412)**, güvenilir işaret/etkileşim kanıtı yok.
- R² basit 0.387 → etkileşimli 0.416. **Bu ön durumların sürprize duyarlılığı istikrarlı biçimde değiştirdiği ispatlanamadı**. N=46 ve deney gücü sınırlı.
- Büyük zıt/istisna örneği: 2020-06-10 olayında yol faktörü neredeyse sıfırken altın +0.859% oynadı; tek mekanizma her tepkiyi açıklamaz. 2023-12-13 faktör yaklaşık -37bp ve altın +1.148%; 2024-12-18 faktör +35.5bp, altın -0.751%, çiftler yalnızca eşzamanlı örnektir.

## 3. İkinci fiyat sağlayıcısı — CİDDİ AMA SINIRLI TUTARLILIK
HistData ham `source_timezone='EST_FIXED_UTC_MINUS_05'`, `evidence_class=...NONCANONICAL`. Yaz saati boyunca New York EDT=UTC-4, HistData ise sabit UTC-5; **yaz olaylarını doğrudan aynı UTC etiketiyle eşleştirmek bir saatlik kayma yapıyor.** 2021-06-16 18:00 UTC Fed açıklamasında EV altın sıçraması 18:00 barındayken HistData'da 19:00 barında gözleniyor. Sabit-EST etiketini gerçek NY yaz saatine göre bir saat kaydırarak ayrı duyarlılık yapıldı.
- HistData'da 46 uygun olayın **42'sinde** iki uç nokta var; 2023-03-22, 05-03, 06-14, 07-26 eksik.
- Yanlış doğrudan UTC eşleştirmesinde 42 olay: slope **-0.1160**, EV aynı 42 olayda **-0.1750**, 30 dk hareket korelasyonu **0.696**.
- HistData yaz-saatine göre düzeltilmiş 42 olay: slope **-0.1230/10bp**, EV aynı 42 olayda **-0.1750/10bp**, 30 dk tepki korelasyonu **0.770**, ortalama mutlak tepki uyuşmazlığı **0.102 yüzde puan**.
- Özellikle 2022-11-02: EV +0.942% / HistData saat düzeltilmiş -0.512%. 2021-03-17: EV +0.809%, HistData +0.069%. **Hâlâ önemli fiyat feed uyuşmazlıkları var.** Dolayısıyla ikinci sağlayıcı etki büyüklüğünü teyit etmiş değildir; yalnız NEGATİF işaret iki kaynakta da bulunmuştur. Canonical price release-time clock ve feed QC tamamlanmadan **nedensel katsayı onaylanamaz**.
- Sonuç: Martingale / politika şoku dışsallığı varsayımları hâlâ ayrıca kanıtlanmalı; dolar/faiz aracı etkinin toplam yüzdesini bu veriyle atfetmek mümkün değil. USMPD piyasa faiz şoku, Fed'in saf dışsal politikasıyla Fed'in ekonomik bilgi sinyalini aynı anda taşıyabilir.

## 4. NY17 seans sınırı — AÇIK VERİ HATASI
Önceki bazı fiyat analizlerinde kullanılan `date((bar_end AT TIME ZONE NY)+7h)` formülü, tam **17:00 ET'de biten 15m barı yanlışlıkla ertesi seansa yazıyor**. Düzeltilen sınır `date((bar_end AT TIME ZONE NY)+7h-1 microsecond)` ile aynı tarihli eski/kritik kapanışlar karşılaştırıldı:
- 2020–2025 boyunca **1,549 ortak hafta içi seans**; bunların **1,494** kapanış fiyatı değişti. Ortalama mutlak kapanış farkı **0.03886%**, en fazla **0.55779%**.
- Bu, eski V2/V3/V4 tüm çalışmasının geçersiz olduğu anlamına gelmez; fakat günlük eşiklerin, epizod tarihlerinin ve saat eşleştirmelerinin **mutlaka tekrarlanması** gerekir. Eski dosyalar değiştirilmedi; yeni pilotun pre-event durumu düzeltilmiş tanımdan hesaplandı.

## 5. Resmî makro açıklama takvimi — KISMİ ONARIM
Önceki PR #120'deki 249 satırlık CPI/NFP/FOMC takviminin **en az 5 resmî eksik açıklaması** teyit edildi:
- 2016-01-08 NFP; 2016-01-20 CPI; 2020-09-04 NFP; 2026-09-11 CPI; 2026-09-16 FOMC.
- Bunların hepsi önceki 1,429 takvim kontrol adayı listesinde yanlışlıkla açıklamasız gün sayılmış; ±1 gün kuralı altında **12 aday** etkilenmiş. Tam takvimde başka eksikler olabilir; bu, **tam yeniden inşa değildir**. Kayıt `GOLD_FOMC_PILOT_MACRO_CALENDAR_MISSING_FIVE_20261013.csv` içinde resmî BLS/Fed linkleri ve ilk bilinen açıklama saatleriyle saklandı.
- BLS 2020-09-04 emek raporu 2020-09-23'te teknik gerekçeyle yeniden yayımlandı; arşiv erişim tarihi / veri vintage'ı farklı.

## 6. Olmayan sonuçlar ve sonraki bilimsel kapılar
Şu anda doğrulanan: ***Fed politika-yolu beklentisi sürprizleriyle eşzamanlı altın fiyat tepki ilişkisi***. Şu anda doğrulanmayan: ***belirli ön rejimin etkisi büyüttüğü, sürprizin önceden bilinebildiği, tek başına Fed'in altın hareketlerine neden olduğu, %3 hareketin geliş zamanı veya banka al-sat kârlılığı***.

Geçiş kapısı:
(1) EV/HistData XAU M15 yayın saatini ve yüksek fiyat tepki uyuşmazlıklarını detaylı kaynak onarımı; mümkünse orijinal M1 ya da tick ile **gerçek t-10→t+20** fiyat ölçümü.
(2) DXY/TIPS/OIS/S&P'nin aynı FOMC statement ve konferans penceresindeki kaynak/vintage ayrı seri ve **politika şoku ile Fed bilgi şokunu** ayıran önceden sabit tasarım; ön haber ve fiyat arasındaki as-of koşulu korunacak.
(3) Altın tüm hareketler ve quiet controls için olay zamanlarını birlikte inceleyen tasarım, haber öncesi zarar görmemiş risk kümesi ve çıktıdan bağımsız örnekleme. FOMC placebo dışındaki mekanizmalar kendi özgün verileri olmadan tek ana modele eklenmeyecek.
(4) Resmî BLS/Fed 2016–2026 takvimini eksiksiz anti-join ile yeniden oluştur; NY17 farklı sürümler için önceden belirlenmiş yeniden üretim.

## 7. Yeni dosyalar
- `GOLD_FOMC_CAUSAL_PILOT_PRECOMPUTATION_PROTOCOL_20261013.md` (analiz sözleşmesi).
- `GOLD_FOMC_PILOT_2020_2025_EVENT_LEVEL_V1_20261013.csv` (53 kayıt; 46 eligible; ham vendor fiyatları tutulmadı).
- `GOLD_FOMC_PILOT_2020_2025_MODEL_DIAGNOSTICS_20261013.json` (HC3 ve etkileşimler).
- `GOLD_FOMC_PILOT_2020_2025_REPRODUCE_20261013.py` (yalnız Python stdlib, kaynak CSV'den).
- `GOLD_FOMC_PILOT_2020_2025_SOURCE_QUERIES_20261013.sql` (Neon SELECT).
- `GOLD_FOMC_PILOT_2020_2025_45MIN_ENCLOSING_USMPD_SENSITIVITY_20261013.json`.
- `GOLD_FOMC_PILOT_2020_2025_HISTDATA_ALTERNATE_SOURCE_QC_20261013.json`.
- `GOLD_FOMC_PILOT_MATCHED_VENDOR_RESPONSE_COMPARISON_20261013.json`.
- `GOLD_FOMC_PILOT_HISTDATA_FIXED_EST_DST_CORRECTED_QC_20261013.json`.
- `GOLD_FOMC_PILOT_INFLUENCE_SENSITIVITY_20261013.json`.
- `GOLD_FOMC_PILOT_MACRO_CALENDAR_MISSING_FIVE_20261013.csv`.

**PR #118/#119/#120 değişmedi, ana çalışma dalı değişmedi; bu pilot için yeni dal/PR açılacak.**
