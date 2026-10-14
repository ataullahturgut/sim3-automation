# GOLD INTRAMONTH — ORTA/BÜYÜK UP–DOWN OLAY TEMELLİ YENİDEN BAŞLANGIÇ SÖZLEŞMESİ
**Tarih:** 2026-10-14 · **Statü:** PRIMARY_RESEARCH_OBJECTIVE_FIXED / JAN2023_EVENT_STRATEGY_NOT_RUN / NO_LIVE_BANK_EXECUTION.
**Otorite:** `../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`. Eski V0 dondurulmuş hesap raporu değiştirilmeksizin karşılaştırma olarak korunur.

## 1. Amaç ve yatırım eylemi
Birincil hedef **ufak günlük oynaklığı kovalamak değil**; **orta ve büyük UP/DOWN fiyat olayı** için **net fırsat** aramaktır. Şok yaklaşırken **erken**, hareket başladığında **teyitli**, sürerken **devam kararı**, yön zayıfladığında **çıkış/tersine dönüş** değerlendirilebilir. Günlük işlem zorunluluğu ve sabit karar saati **yoktur**.

- **GOLD pozisyonunda:** Altında maliyetleri haklı çıkaracak önemli DOWN tehdidi/başlamış düşüş varsa nakde geçmeyi; düzeltme sönümlenip tekrar güçlü UP varsa altına dönmeyi değerlendir.
- **CASH pozisyonunda:** Aylık tahmin DOWN dahi olsa maliyetleri karşılayabilecek önemli UP toparlanma başlamadan önce veya başladıktan sonra altına girme fırsatını değerlendir.
- **HOLD/WAIT/ABSTAIN** başarısız karar değildir. Az işlem yapmak **amaç** değil, yalnız yanlış/gereksiz maliyetli işlemleri engelleyen araçtır.
- **Aylık tahmin:** UP/DOWN/rejim/güven, karar anında biliniyorsa bağlam olarak kullanılır; **otomatik işlem yasağı** değildir. Aylık tahmin olmasa da olay tespitinin kendi kanıtı kaydedilir.

## 2. Olay ailesi ve ölçütleri
`case_id`, yön `UP/DOWN`, şiddet `MEDIUM/LARGE`, evre `PRE_ONSET / CONFIRMED_ONSET / CONTINUATION / EXHAUSTION / REVERSAL / NO_EVENT / UNCERTAIN`, piyasa/rejim ve altın/nakit durumu ayrı tutulur. 2023–25 atlasındaki **≥%3** ve **≥%2 kısa hızlı** olay sınıfları **inceleme adaylarıdır**; doğrulanmadan evrensel mutlak tetik/otomatik emir eşiğine çevrilmez. Rejime uyarlanmış ve başlangıçta bilinen ölçekle eşik adayları ayrıca sınanabilir.

**Ücret ve fırsat:** Her alış ve satış için ücret %0,8; aynı maliyetsiz spot başlangıç/bitiş fiyatı varsayımında alış+satış başabaş yukarı hareketi `1/(0.992²)-1 ≈ %1,6194`. Gerçek alış ASK, satış BID, ek banka makası/kur, varsa slippage ve gecikme **bu eşiği yükseltir**. Bu başabaş **kârlı olacağımızın garantisi değildir**; girişten sonra kalan makul hareket, başarı olasılığı ve ters hareket riski ile karşılaştır. DOWN korumasında nakde çıkıp tekrar altına girmenin maliyetini de ayrı hesapla. Salt fiyatın geçmişte %3 oynadığı bilgisi fırsat demek değildir.

**Kayıtlı hedefler:** olayın gerçek ilk eşiğe erişmesi, sinyale kadar geçen süre, sinyalden sonraki `MFE/MAE` ve beklenen kalan yönlü hareket, alarm öncesi/sonrası kaçan kısım, `UP` ve `DOWN` için ayrı recall/false positive, uygulanabilir BID/ASK'den 100 USD net portföy. Aynı barın tepe-dibini veya sonradan bilinen dönüm noktasını geçmişte işlem saati olarak kullanma.

## 3. Olay araştırma iş akışı — TÜM GÜNLER
**Ay ay, 2023 Ocak'tan başla; tüm takvim günlerini gözden geçir** (işlem yapılamayan hafta sonu/tatil için `NO_TRADE`, gerçek risk/gelişme bilgisi ayrı). Her olayda olay **olmayan** benzer günleri de kontrol olarak tut.

1. **Gözlem:** XAU BID/ASK fiyat yolu (NY17 seans etiketini gerçek UTC işlem saatinden ayrı tut), altın metaller XAG/XPT/XPD, USD/DXY, 2Y/10Y/reel faiz, Fed beklentisi, VIX/GVZ, hisseler, petrol, COT/ETF ve ekonomik haber firstprint. Veri yoksa `MISSING`; zaman uyumsuzsa neden ilişkisini kurma.
2. **Ayrıştırma:** Ön koşul → ilk tetikleyici → USD/faiz/likidite/risk/metal aktarımı → XAU cevabı → karşıt haber/koşullar. Bazı şoklar **habersiz** veya birden fazla mekanizma ile gelişir. Gerçekleşen fiyatı olay sınıfı için kullanırken bunun `EX_POST` olduğu açık olsun.
3. **Aday karar:** Altın mı nakit mi? Olayın yönü ve evresi ne? **Önceden/başladıktan sonra** hangi kanıtla ve en erken hangi erişilebilir fiyattan teorik emir verilebilir? Ücret ve fırsat maliyeti çıkartılır; güven yetmiyorsa `HOLD/WAIT`.
4. **GPT ikinci görüş:** Kaynağa bağlı neden/sonuç hipotezlerini ve ters örnekleri sorgular; sayısal fiyat, komisyon, emir zamanı icat edemez. DeepSeek/Gemini kullanılmaz.
5. **Günlük kayıt:** `case_id, event_time_utc, firstprint_utc, decision_time_utc, executable_quote_time_utc, mode, known_at, future_outcome_visible, position_before, event_direction, severity, stage, signal_evidence_ids, opposing_evidence, candidate_action, action_status, total_cost, price_fill_proxy, pnl, missed_move, method_version`.
6. **Ay sonu:** 100 USD başlangıç + tam komisyon/spread/gerçekçi icra varsayımıyla fiyat hesabı; **BUY/HOLD**, **CASH**, **aylık rejim pasif** benchmarkları; işlem başı net katkı; yanlış al-sat, kaçan fırsat ve drawdown. Başarı iddiası ancak karşılaştırma ve güvenilir testle.

## 4. Hangi bilgi hangi deneyde serbest?
- **Kip A `FULL_HISTORY_DISCOVERY`:** 2024–2026 ve sonraki yayımlanmış tüm olayları 2023 vaka kimliklerini yeniden anlamlandırmak, sınıflandırmak, algoritma hipotezi kurmak için kullan. Olayın sonradan bilinen sonucu **etiket** olabilir. Bununla doğrudan geçmişte işlem yapılmış gibi NAV hesaplamak **yasaktır**.
- **Kip B `AS_OF_DECISION_EVALUATION`:** Karar sırasında bilinmeyen aynı olaya ait sonuç ve haber **girdi olarak yasak**; model zaten tüm gelecekteki olaylarla geliştirildiyse tarihsel performansı kör/OOS diye raporlayamazsın. Hindsight maruziyetini kaydet. Testi izinsiz optimize ederek tekrar tekrar Ocak'a uyarlama.
- **İki kip birlikte:** Bilimsel vaka açıklaması ve uygulanabilir işlemin sayısal simülasyonu ayrı alanlar/tablolar taşır. Yalnız birini başarı sanma.

## 5. Ocak 2026 deneyinden doğru devredilecekler
- B0 kapanış-only şokun gün içindeki başlangıcını kaçırabiliyordu; başlayan hareketin **teyidi** araştırma hedefi olmalı.
- V3 tekil `A OR T` yanlış SAT nedeniyle maliyet yarattı; V4 `A AND T` Ocak 2026'nın **önceden görülen** 29 Ocak düşüşünde retrospektif iyi, fakat 2024'teki 12 büyük banka-sonrası DOWN olayına karşı **0 alarm** ve performans eşiği **FAIL**. Bu işlevsel kural **canlıya/promosyonla devredilemez**.
- A ve T aynı XAU fiyat yolundan türemişti; **bağımsız iki kaynaktan onay** değildir. Fiyat+hâlihazırda yayınlanmış makro ve eşzamanlı metaller/FX/faiz sinyali ayrı hipotezdir, henüz kanıtlanmış çözüm değildir.
- Banka 09:00–17:00 Türkiye örneği gerçek emir penceresi ise 16:30/16:45 deney saatleriyle kıyas yapılabilir; **araştırmanın tek karar saati 16:30 diye dondurulmaz**. Fiyat kaynağı BID/ASK ve teorik banka kotasyonu aynı şey değildir.

## 6. Ocak 2023 düzeltme defteri
Mevcut `JAN_2023_FULL_MONTH_GPT_ONLY_SCIENTIFIC_AUDIT.md`: **V0 maliyetli momentum** $101,9695; aynı başlangıç/bitişle pasif altın $103,7589; nakit $100; 2 AL + 2 SAT ve vol gate 0/20. Bu veri değişmez, ama **kullanıcının talep ettiği olay stratejisi değildir**.

**Henüz yapılmayanlar:** tüm Ocak 2023 günleri için çift-yönlü orta/büyük olay evreleri, post-onset pozisyon fırsatları ve kaçan hareketler; piyasa kaynaklarıyla mekanizma doğrulama; maliyet sonrası uygulanabilir yeni aday kararlar; olay stratejisine ait net $100 hesap. `STATE.json` şimdilik `primary_event_driven_status=NOT_YET_RUN`, Şubat ana strateji aktarımı `BLOCKED`. Yeni sonuçlar için ayrı kimlik ve ayrı hesap dosyaları oluşturulmalı; V0 rakamını sessizce üzerine yazma.

**Kabul kapısı:** Yalnız açıklayıcı hikâye değil, yön/şiddet/evre hata ölçümü ve maliyetli karar kıyası. 2023 Ocak sonradan iyi çalışırsa bile geçmiş ve 2026 görülmüş olduğu için OOS/kanıtlanmış üstünlük ilan etme.
