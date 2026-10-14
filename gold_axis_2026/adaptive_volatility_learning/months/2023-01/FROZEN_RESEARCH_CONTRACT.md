# JAN 2023 — İlk aylık yürüyüş için sabit hesap sözleşmesi
**2026-10-14 · status: EXPLORATORY_AFTER_2023_HINDSIGHT · NOT_BLIND_OOS · GPT_ONLY**

## Deney kapsamı
2023 Ocak **1–31 bütün takvim günleri** kayda alınır; fiyat/günlük yeniden dengeleme ancak tam NY17 kapanışlı veri seanslarında yapılır. 1–2 Ocak ilk NY17 seansı başlamadan önce, 7–8 vb hafta sonları ve 16 Ocak 2023 tam NY17 bar kapanışı eksik olan kısa/tatil seansı **NO_NEW_TRADE**, o gün portföy değeri son gözlenen uygun altın BID işaretiyle taşınır. 31 Ocak son NY17 BID'inde altın varsa likiditeye çevrilir. Ocak 2023'ün iyi bilinen yükselişi ve daha sonraki 2024–26 olay araştırmaları görüldüğü için sonuç **kör başarı iddiası değildir**.

**Veri:** `public.gold_research_evduka_xau15m_bidask_candidate` EVTradingLabs/Dukascopy arşivinde fiyat; `bar_end_utc=bar_start_utc+15m`; NY17 seansı = `DATE((bar_end_utc AT TIME ZONE 'America/New_York') +7h -1 microsecond)`. Satış BID, alış ASK. Eksiksiz seans = en az 70 M15 bar **ve NY17 kapanışında gerçek M15 bar**. Kaynak 2026'da derlenmiş tarihsel vendor verisidir, o tarihte bankanın icra teklifi olduğu iddia edilmez. Veri zamanı/saati ayrıca korunur. Lisanslı ham 15m/özel fiyatlar açık GitHub'a dökülmez.

**Başlangıç ve son:** Sanal bakiye **$100**, altın ve dolar nakdi; January3 NY17 seansının **ilk 15m BID/ASK kapanışında** ilk strateji işlemi yapılabilir (piyasa yeniden açılışı 2 Ocak New York akşamıdır). Strateji önceki **tam** 2022 Aralık NY17 seansının kapanışlarından elde edilebilen işaretleri kullanır. Jan3–31 boyunca yeni seansın **ilk** tamamlanmış 15m barındaki BID/ASK ile, sadece önceki tam seansın bilgi durumuna göre hedef pozisyon güncellenir. Tatil/kısa seansında yeni pozisyon açılmaz; sonraki tam seans öncesi bilgi olarak **son tam NY17 seans** kullanılır. Aynı günün kapanışıyla aynı günün açılışında işlem yok. Son Jan31 saat 17:00 NY BID'inde pozisyon tasfiye edilerek $ nakit NAV raporlanır.

**Ücret:** Her alışta $ bakiyenin %0,8'i gider, kalanla `gold_units=(cash*0.992)/ask`; her satışta `cash=(gold_units*bid)*0.992`. Gözlenen kaynak BID/ASK makası ayrıca mevcuttur, çift ücret dışında kesilir. Faiz, vergi, kur dönüşümü, slippage ve banka fiyat farkı ayrıca bilinmediği için **katılmaz**. Gold birimi teorik XAU ons, fractional holdings serbest. Nihai banka kârı değildir.

## Baştan sabit mekanik inceleme kuralı

**5 tam seans yön:** `ret5 = CloseMID(last full NY17)/CloseMID(5 full sessions earlier)-1`.
**5 seans risk:** `a5 = mean(abs(daily log returns))` son 5 tam seans, **20 seans referans** `a20=mean(abs(daily log returns))` son 20 tam seans; risk oranı `ratio=a5/a20`.

**Risk-aware trend5 V0:** `GOLD` yalnız `ret5>0`, yeterli 20 geçerli getiri, `ratio<=2.0` ise; diğer durumda `CASH`. 2 eşiği yalnız kaba araştırma güvenlik freni, Jan ayı için ayarlandı/optimize edildiği iddia edilmez. Risk durumları `ratio<0.75 LOW`, `0.75–1.5 NORMAL`, `1.5–2 HIGH`, `>2 EXTREME` tanı içindir; bunlar kalibre edilmiş gelecek risk olasılıkları değildir.

**Karşılaştırmalar (aynı giriş, kaynak, masraf):** `ALWAYS_GOLD`: 3 Ocak NY17 ilk M15 ASK'tan satın al → 31 Ocak son NY17 BID'den sat; `ALWAYS_CASH` $100; `TREND5_ONLY`: aynı seans ve masraf, `ret5>0` ise altın, değilse nakit; `RISK_AWARE_TREND5_V0`: yukarıdaki koşul. Tüm işlem tarihleri, ücret toplamları, satın alım/satış sayısı ve günlük MTM NAV kaydedilir. İyi görünen varyantı sonuçtan sonra tek gerçek başarılı yöntem diye ilan etme.

**GPT ikinci görüş:** Kaynaklı haberler NFP/CPI/PPI/GDP/PCE ile zaman-uyumlu incelenir. GPT hangi neden açıklamasının makul/yanlışlandığını, yıl sonrası analogların açıklamaya etkisini, kağıt üzerinde simüle edilen mekanik işlemin ekonomik anlamını tartışır; **V0 mekanik emirleri geriye dönük değiştiremez**. Bu ilk ayda GPT destekli sayısal emir modeli **yoktur**. WGC Şubat 9 2023 Ocak ETF raporu retrospektif Kip A açıklamasıdır, Ocak ayı o zamanki bilgi değildir.

**Test sonu:** P&L karşılaştırması 2023 Ocak araştırma örneğidir, optimize edilen bir modelin out-of-sample başarısı değildir. Tarihsel olay açıklaması ile banka yatırım getirisi ayrı. Değer taşıyan hipotez varsa Şubat ayına `UNTETSTED` statüsüyle devredilir.
