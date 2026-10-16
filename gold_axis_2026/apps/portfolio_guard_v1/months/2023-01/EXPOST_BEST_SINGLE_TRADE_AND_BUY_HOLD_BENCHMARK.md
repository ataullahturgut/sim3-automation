# Ocak 2023 — en iyi TEK AL–SAT, altını tutma ve CORE V0 (ex-post araştırma kıyası)

**Ölçek:** $100 USD CASH, tek taraf %0.8 banka maliyet vekili, 2023 Ocak HistData 15min geçmiş XAU MID araştırma fiyatı. Gerçek bankanın BID/ASK geçmişi veya gerçekleşmiş emir kaydı DEĞİL; 2026'da bakılarak hesaplanan oracle ile bugünün 2023 öğrenilmiş modelini birbirine karıştırma.

## Ortak işlem tanımı

Kaynak `gold_axis_2026/adaptive_volatility_learning/months/2023-01/JAN_2023_EVENT_DNA_ASOF_V2_PANEL_20261015.csv`. Sinyal önceki barın tamamlanmış fiyatında, emir bir sonraki kesintisiz 15dk satırının `p` fiyatında varsayılır. **İlgili önceki sinyal ve sonraki dolumun ikisi de** Türkiye hafta içi 09:00 ≤ t < 17:00 içinde olmalıdır. Bu şartları sağlayan **645 muhtemel emir fiyatı** vardır. Bir işlemde `cash -> ounces = cash*(1-0.008)/mid`; çıkışta `ounces -> cash = ounces*mid*(1-0.008)`. Ek spread yine uygulanmaz.

## Bir tam AL+SAT için teorik optimum (**geleceği biliyormuş gibi**)
- AL: 2023-01-03 **14:45 TRT**, `p=1831.145` USD/oz (UTC 11:45). `100 * .992 / 1831.145 = 0.05417375467262287 oz`.
- SAT: 2023-01-26 **09:15 TRT**, `p=1948.525` USD/oz (UTC 06:15).
- Tam banka turu sonu nakit `100*.992*.992*1948.525/1831.145 = $104.7144440008847`.
- Kâr **$4.714444 = %4.714444**. Bu, ayın en iyi *tek tamamlanmış* AL/SAT çiftidir; tarih ve fiyat sonradan bildiği için bir sinyal modelinin başarısı olarak sunulamaz.

## Al ve tut karşılaştırması
- İlk uygun fiyat: 2023-01-03 **09:15 TRT**, `p=1842.245`.
- %0.8 AL sonrası altın `0.05384734386577247 oz`, ay sonu araştırma fiyatı `2023-01-31 21:00 UTC` (2023-02-01 00:00 TRT), `close=1928.385`.
- **ALTINI ELDE TUT, satılmamış teorik MID değeri $103.83841020059765** = +%3.83841; henüz çıkış komisyonu ödenmemiştir.
- Son fiyattan %0.8 teorik çıkış maliyeti sonrası **$103.00770291899285** = +%3.007703; BU FİYAT **TRT 00:00'da, bankanın 09–17 penceresi dışındadır**, o dakikada gerçek banka satış fiyatı gibi gösterilmemelidir.
- **Son uygun banka penceresi**: 2023-01-31 16:45 TRT, `p=1913.105`; ilk 09:15 alıştan sonra o seansta gerçekten çıkabildiği varsayılan karşılaştırma **$102.19149780403801** = +%2.191498. Diğer benchmarklarla fiyat saatinin farklı olduğu unutulmamalıdır.
- Nakit kal: $100.

## CORE V0'nin gerçekten yaptığı
- 2023-01 yalnız; **1764 bar**, **645 uygun banka kontrolü**, **5158 olgunlaşmış matematiksel head öğrenme güncellemesi**, 4 ilk yayına bağlanan makro veri satırı; **0 AL, 0 SAT**, terminal CASH **$100**.
- İleriye dönük performans belirtmez; ayın gözlenmiş fiyatlarından hesaplanan üst karşılaştırma **$104.714444** ile fark **$4.714444**.
- CORE hiç işlem yapmadığı için performansı nakitte kalmakla aynı. En iyi tek işlem için gereken alış ve satış zamanını öğrenmiş olduğunu söylemek YANLIŞ.

## Daha fazla işlem döngüsü eklemek (ex-post, gereksiz trade stress)
Aynı 645 nokta üzerinde kronolojik dinamik programlama ile **tam olarak 2 tamamlanmış tur** zorlanırsa optimum **$104.69233168050918**, **tam olarak 3 tur** zorlanırsa **$104.08569133300733**. Bu, ekstra komisyonların kazancı azaltabileceğini örnekler; çok sayıda geleceği bilen döngüyle arama yaparak modelin gerçek öğrenme başarısı elde edilemez.

**Karar:** Bu Oracle sayıları yalnız *ex-post opportunity cost* etiketidir. Ocak 2023 CORE parametrelerine geri besleme verirken tarih bazlı emir taklidi, en iyi giriş/çıkışa önceden erişim veya aynı ayı yeniden tarayıp başarılı OOS varsayımı yasak. Asıl matematiksel hedef, olgunlaşmış sonuçtan karar pişmanlığını ve uzun ufuk pozisyon değerini öğrenmektir.
