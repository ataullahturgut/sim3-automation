# DOĞRU STRES OLAYI TANIMI — Ocak 2023 yönlü çok günlük epizot atlası
**2026-10-14** · Araştırma düzeltmesi. Önceki [5–6 Ocak günlük volatilite deneyi](JAN_2023_TOP_VOLATILITY_DIRECTIONAL_STRESS_AUDIT_20261014.md) korunur ama **ana şok sınıflandırması olmadığı** belirtilir.

## Kayda geçen araştırma hedefi
Orta/büyük **yönlü** UP/DOWN hareketi, tek günün ASK HIGH–BID LOW farkı ile eşdeğer değildir. Asıl olay sıralama `%3+ yönlü` veya `%2+ hızlı yönlü` **araştırma adayları**; **işlem için otomatik eşik değil**. 15 dakikalık XAU MID kapanışlarının zaman sırasıyla önce görülen dip→sonraki tepe (UP) / önceki tepe→sonraki dip (DOWN), ileri gerçekleşen toplam hareket etiketidir. Piyasa haberleri, fiyat başlangıcı ve alış/satış gereksinimleri farklı zamandır. Olay seçimi **EX_POST**; tetikleyici yapmak **lookahead** olur.

## Neon 15m MID üzerinden doğrulanmış örnek zaman sıraları
| Araştırma vakası | Önceki uç (UTC) | Sonraki uç (UTC) | MID baş→son | Yönlü gerçekleşen hareket |
|---|---|---|---|---:|
| JAN23_U_MID_FULL | 2023-01-05 16:00 | 2023-01-26 06:15 | 1826.900→1948.705 | +6.667% |
| JAN23_U_240H | 2023-01-05 16:00 | 2023-01-13 18:45 | 1826.900→1921.715 | +5.190% |
| JAN23_U_120H | 2023-01-11 16:30 | 2023-01-16 03:00 | 1869.880→1928.430 | +3.131% |
| JAN23_D_MID_FULL | 2023-01-26 06:15 | 2023-01-31 12:30 | 1948.705→1902.920 | -2.350% |
| JAN23_D_72H | 2023-01-04 08:30 | 2023-01-05 16:00 | 1863.885→1826.900 | -1.984% |
| JAN23_U_72H | 2023-01-11 16:30 | 2023-01-13 18:45 | 1869.880→1921.715 | +2.772% |

Bunlar **altı bağımsız olay** değildir. +%5.190 epizodu +%6.667 uzun UP içinde, +%3.131 epizodu da geniş uzun UP döneminin alt bölümünde gerçekleşir; farklı pencere maksimumları çakışabilir. Aynı fiyat dalgasını defalarca bağımsız başarı saymak bilimsel hata olur. Altın 3–31 Ocak içindeki en büyük **kronolojik geçmiş zirve→sonraki dip** DOWN **-%2.350**: bu ayda **-%3 DOWN örneği yok**. 4 Ocak→5 Ocak **-%1.984 / 31.5 saat**, hızlı %2'ye yakın DOWN kontrol vakasıdır. Jan25 günlük aralık şok olmasa bile Jan5→Jan26 UP olayı büyüktür. Tarihler **işlem sinyali değil yalnız ex-post dip/tepe etiketleridir**.

## Doğru bilimsel test sıralaması
1. Önce **olayın tamamını** vaka olarak seç: `Jan5→Jan13 UP +%5.19`; `Jan11→Jan16 UP +%3.131`; `Jan26→Jan31 DOWN -%2.35` **near-threshold negative stress**. En uzun Jan5→Jan26 UP +%6.667 aynı çizgiye ait daha geniş başlık olabilir. Gerçek **-%3 veya daha büyük DOWN** araştırması için başka ay/yıl gerekebilir; Ocak 2023'te olmayan büyük düşüşü yaratmayın.
2. Olay öncesini kapsayan dönemde **her 15 dakikada gözlenebilir fiyat/çapraz piyasa/haber** ile riskin nasıl geliştiğini incele. Her 15 dk işlem zorunluluğu yok; sadece AL/SAT adayı doğunca dakikalık teyit, **en erken sonraki fiyat** ve **gerçekten elde bulunan as-of kanıt**.
3. **Kalan kazanç/kayıp ve komisyon**: %0.8 AL + %0.8 SAT, bid–ask makas, gerçek bankanın saat/fiyat kaydı yoksa proxy ayrı. Model sinyal verdiği anda sonraki gerçek yönlü hareket ne kadardı ve getiri kaçırılan kısmı ne? Olayın sonradan görülen toplam %5'i modelin %5 kazanacağı anlamına gelmez.
4. Aynı haber türünün **şok oluşturmayan** karşı örnekleri ve ekonomik mekanizma analojileri birlikte değerlendir. Arşivdeki fiyatı sonraki haberle açıklayıp daha önce AL emri yazma.
5. Şok testini yalnız Ocak 2023'teki UP sonuçlarıyla doğru ilan etme: örneklem **DOWN -%3'tan yoksun**, farklı yıl (örneğin 2026 Jan şoku) ve negatif kontroller ayrıca çalışılmalı. Çalışma statüsü `DIAGNOSTIC_HINDSIGHT_EXPOSED_NOT_VALIDATED`.

## Eski günlük volatilite tablosu için koruma notu
6 Ocak TRT tek gün ask-high vs bid-low range %2.187 / ilk→son MID +%1.834, 5 Ocak %1.842 / -%1.257; bunlar **gün içi piyasa stresi** için faydalı, ancak **asıl büyük yönlü olayların maksimumu diye kullanmak yanlış**. 5–6 Ocak GPT SELL yerine GOLD koru portföy örneği 4 Ocak girişinden kaynaklanan açık pozisyon zincirine bağlıdır, gerçek %3+ DOWN yakalama başarısı hakkında delil değildir.

**Veri kapsamı:** Özel Neon `public.gold_research_evduka_xau15m_bidask_candidate`, 3 Ocak 02.00 TRT–31 Ocak; M15 bar kapanış MID. Tek barın OHLC uçları sıralı sanılmaz; **bar kapanışlarını kronolojik** kullandık. UTC zaman işaretleri doğru olup Türk yerel dönüşümü UTC+03. Her pencere yalnız o aralıktaki en iyi *ex post* uçları gösterir. Başka vendor ve banka spot fiyatları ile karşılaştırma henüz tamamlanmadı.
