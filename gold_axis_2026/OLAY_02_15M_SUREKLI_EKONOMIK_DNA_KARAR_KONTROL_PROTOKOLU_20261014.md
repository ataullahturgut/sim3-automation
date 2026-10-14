# OLAY-02 — Her Yeni Veride Ekonomik DNA Değerlendirmesi (Kronolojik Karar Makinesi)

**Uygulama kuralı:** ANA-01'in dört temel adımını tek dosyalı fiyat alarmına indirgeme. Bu, 2023–2025'ten ölçülmüş fiyat alarm büyüklüğü + ÖĞREN-03'ün tarih dışı G/ORG olay hikâyeleri + gerçekten yayımlanmış haberlerle **her kontrol anında** çalışan araştırma mantığıdır. Ayrı manifest değildir.

## Zaman ve işlem sırası

- Türkiye saatiyle 1 Ocak 00:00'dan başlayarak 15 dakikada bir `state(t-1)→new_inputs(t)→active_episode→hypothesis_and_rivals→action_now→state(t)`. 31×96=2976 kontrol; piyasa kapanışında kontrol kaydı sürer ama fiyat uydurulmaz.
- **Her yeni girdide** (M15 tamamlanması, H1 tamamlanması, yayımlanmış ve erişilebilir resmî açıklama, ilgili ilk kaynaklı haber, banka/komisyon değişimi) değerlendirme tetiklenir. 15 dakikadan önce gelen önemli haber bir sonraki planlı slota taşınmazsa ayrıca olay anı `NEWS_ARRIVAL` kaydı gerekir.
- Aynı `EPISODE_ID` yeni bilgi geldiği sürece **birden fazla gün** sürdürülür; bir haber ve onun fiyat tepkisi farklı şeylerdir. Belirsizlikte `candidate`, ters kanıtta `contested`, açık sonuç yoksa `unresolved`. P0→P1→P2→P3→P4→P5 *otomatik kesin kabul edilmez*, ancak hangi kanıtın hangi geçişi desteklediği kaydedilir.
- Bir olay olmadan fiyatın tarihsel aşırılığı görülebilir: **`UNEXPLAINED_VOLATILITY`** kaydı yeni kaynak arama işidir; `ORG10` ya da güvenli liman ekonomik nedeni uydurulmaz.

## Anomali denetimi yalnız 2023–2025'ten sabitlendi

Neon'da 2023–2025 tam HistData M15 ve *gerçekten kesintisiz* 15 dakikalık eşleşmeler: 66.179 gözlem, medyan mutlak M15 log-getiri %0,04279, p95 **%0,19597**, p99 **%0,36041**. Kesintisiz dört barla hesaplanan 1h abs log-getiri 61.996 gözlem, p95 **%0,40093**, p99 **%0,73046**. Bu **tetik-sonrası kanıt inceleme alarmıdır**, otomatik işlem eşiği değildir. 1h/4h kesintisiz yoksa olay kabul edilmez/uydurulmaz; haber kendi başına da inceleme başlatır.

## As-of durum güncelleme: 7 zorunlu alan

1. **Yeni ne geldi?** `received_at, bar_end, source, value, quality, old/new`; aynı spot HistData BID ve Duka BID fiyatı çift bağımsız doğrulama sayılmaz.
2. **Bu yeni bilgi neyi değiştirdi?** Önceki `GOLD/CASH`, eski aktif olay, önceki mekanizma yönü, kanıtı güçlendiren veya çürüten yeni bilgi. Yeni veri yoksa `NO_CHANGE_EVALUATED` fakat fiyat eskiyse `STALE`.
3. **Hangi ekonomik olay?** Resmî açıklama varsa tarihli haber `EPISODE_ID`; yoksa fiyat alarmı `UNEXPLAINED_VOLATILITY`; haber ilk yayımı yalnız takvimden çıkarılamaz. `Firstprint unknown` ise ekonomik başlangıç kanıtlanmaz.
4. **Neden ve karşı neden?** ÖĞREN-03'ten `trigger/transmission/amplifier` ayrı, alternatif USD/faiz/metal/petrol/pozisyon, zıt işaret. Spot haber sonrası M15 ve yeni tamamlanmış H1 gerek. `ZN` vadeli **fiyat** artışı gerçek getiri kanıtı değildir; `SI` H1 kaydı gelmediyse sıfır tepki sayılamaz.
5. **Olayın devamı ve geçişi?** `NEW_INFO, EARLY_REACTION, CONTINUATION_OBSERVED, COUNTER_MOVE, WATCH_CONTINUATION, INSUFFICIENT_INFO, MARKET_CLOSED`. Geçmişte görülen tepe/dip canlı `P4/P5` değildir.
6. **Şimdi ne karar?** `BUY, SELL, HOLD_GOLD, HOLD_CASH, WAIT`, `decision_reason`, `confidence`, `execution_eligible`. `DESTEKLENEN` mekanizma seviyesindeki tartışma `BUY` yetkisi vermez: **kalan** net büyüklük (%0,8 her yönde ve BID/ASK üzeri) önceki bağımsız kanıtla makul gösterilmeli. Güçlü fiyat artışından sonra giriş için önceden geçmiş artışı yeni kazanç yazma.
7. **Karar ne zaman bozulacak?** `invalidation / next_review_at / current_paper_position`; tekrar gözden geçir. Her 15dk etkin kanıta göre değişiklik yoksa önceki karar korunur; `cash and no action` ile `could not evaluate due to missing data` farklı alanlardır.

## İlk tarihsel kalan-hareket kanıtı ve sınırı

Sadece ön-2026 OLAY-02'deki **85 tarihli makro haber**, Neon 15m önceki fiyat kaynağıyla ölçüldü; *t+1h son tamamlanmış bar* ile *t+120h yakınındaki ilk tam 15m bar* arasındaki **kalender beş gün** getirisi, **geleceği karara koymak için değil**, tarihsel dağılım örneklemi içindir: CPI 34 olayın 24'ü +120h fiyatı içerir, koşulsuz medyan +%0,851; NFP 35'in 34'ü fiyat içerir, medyan −%0,067; FOMC 16'nın 16'sı fiyat içerir, medyan +%0,056. NFP'nin +24h örneği hafta sonu yüzünden yalnız 3/35, CPI'nin +72h örneği yalnız 11/34. **Şartlı fırsat modeli değildir**, yanlış yöndeki ve olaysız kontrol farkı sınanmadan `expected_remaining` tahmini gibi kullanılmaz. Hiçbiri sabit her yönde %0,8 bankaya karşı işleme izin vermez.

## Mevcut araştırma kullanımı

Birinci uygulama `PER_SLOT_ECONOMIC_REVIEW`: olay eksik haber kapsamı işaretli iken **her kontrol noktasında mutlaka bir pozisyon kararı ve gerekçe**; ekonomik olgunun kaynak güveni, fiyat/H1 tepkisi, alternatif açıklama ayrı alan. **Bu araştırma girdileri ve düzeni tamamlamadan “31 gün ticaret simülasyonu bitti” denmeyecek.** Kişinin önceden bildiği Ocak sonuçları nedeniyle giriş/çıkışta hindsight ihtimali devam ediyor; doğrulanmış kör OOS sayılmaz. Ekonomik haber eksikse şimdilik alım/satımın kanıt statüsü `NOT_ACTIONABLE_NEEDS_EVENT_RESEARCH` olmalı; “Ocak'ta hiç olay yoktu” yazılamaz.
