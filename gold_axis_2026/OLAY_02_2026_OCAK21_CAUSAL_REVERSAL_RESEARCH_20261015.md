# OLAY-02 — 21 Ocak 2026 96-slot dedektif araştırması

**Yetki:** ANA-01 araştırma protokolü; OLAY-02 tarihli vaka kanıtı; ÖĞREN-03 tarih içermeyen G02/G03/G06 hipotezleri. Eski Ocak 2026 deney sonuçları kullanılmadı. **Kapsam tam gün 00:00–23:45 TRT (96 saat damgası); yalnız bu gün araştırılmıştır.** RESEARCH_ONLY, RETROSPECTIVE_NOT_BLIND_OOS, gerçek banka emri yok.

## O anda bilinebilecek haberler ve bilgi sırası
- 00:00 TRT: 19–20 Ocak tarife/grönland krizine ilişkin bilinen haber, buna karşılık 21 Ocak Davos kararı henüz yok.
- 08:45 TRT sonrası: 21 Ocak Reuters altın raporunun 00:26 EST'de (08:26 TRT) güncellenmiş versiyonu kullanılabilir. https://www.marketscreener.com/news/gold-crosses-4-800-for-the-first-time-as-us-eu-spar-over-greenland-ce7e58ddda81f322
- 18:00 TRT sonrası temkinli: 14:39 CET (16:39 TRT) başlayan Davos konuşmasının askeri güç kullanılmayacağı açıklaması erişilebilir; kelime bazlı ilk yayın dakika kaydı yok, konuşmanın tamamlanması sonrasını kullandık. https://www.presidency.ucsb.edu/documents/pool-reports-january-21-2026
- 23:00 TRT sonrası temkinli: Reuters ilk haber 14:40 EST (22:40 TRT), değişiklik 14:48 EST (22:48 TRT): Trump 1 Şubat tarifesini geri çekiyor, NATO ile çerçeve görüşme. Bu bilgiyi sabah veya öğleden sonra kararlarına geri yazmak yasak. https://www.investing.com/news/world-news/trump-says-no-tariffs-next-month-after-agreeing-outline-of-greenland-deal-4458621
- Web haberleri kapsamlı terminal haber arşivi ya da resmî ilk politika açıklaması değildir. Bu nedenle FIRSTPRINT_VERIFIED başarısı sayılmaz.

## As-of kontrol dönemeçleri
| TRT | Son tamamlanmış HistData M15 kapanışı | O andaki muhakeme |
|---|---:|---|
| 00:00 | 4756.405 | G02 tarife risk primi adayı + G06 momentum; sonraki diplomatik gelişme bilinmez |
| 08:30 | 4868.605 | G02 tarife risk primi adayı + G06 momentum; sonraki diplomatik gelişme bilinmez |
| 09:15 | 4871.315 | G02 tarife risk primi adayı + G06 momentum; sonraki diplomatik gelişme bilinmez |
| 16:15 | 4869.055 | G02 tarife risk primi adayı + G06 momentum; sonraki diplomatik gelişme bilinmez |
| 18:00 | 4851.595 | Davos askeri güç yok açıklaması, G03 prim çözülmesi / G06 dönüş riski, fakat ekonomik düşüş kalan büyüklüğü kalibre değil |
| 23:00 | 4780.995 | Tarife geri çekilme haberi var; G02 fiyat priminin ne kadarı çözülecek belirsiz |
| 23:45 | 4819.865 | Tarife geri çekilme haberi var; G02 fiyat priminin ne kadarı çözülecek belirsiz |

96 slottan 92 tam HistData M15 kaydı vardır. Başlangıç doğrulanmış gözlem 4756.405, o ana kadar gözlenmiş yüksek fiyat 4883.585; bir sonraki haber geçmişe taşınmadan olay evresi güncellenmiştir.

## Gerçek portföy muhakemesi (iki ayrı başlangıç durumu)
GOLD taşıyanın veriye dayanan pozisyonu HOLD_GOLD + G03/G02 risk primi çözüldüğünde reversal watch. CASH olanın HOLD_CASH (pahalı AL şartı yerine gelmedi). İşlem alış/satış komisyonu her yönde %0,8, tam tur için teorik %1,6194, ayrıca bankaya özgü spread ve gecikme. Buradaki bid/ask kaynaklarının bağımsız olmadığı ilk gün denetimde görüldü; dolayısıyla sıfır kurgu banka emri.

**Önemli:** G02 primini azaltan haberden sonra altının düşmesi tek neden ispatı olmaz. Aynı anda farklı mekanizmalar — G06 FOMO/kar realizasyonu, G04 rezerv talebi, G01 faiz ve dolar — çalışabilir. OLAY-02'deki eski tarihli vaka karşılaştırmaları nedensel doğrulanmış algoritma değildir.

## Bilimsel sınırlama ve takip sorusu
Bu dosya aynı 96 kontrolün veri/saat/delil izidir; her saatte bağımsız yeni GPT yorumu yapıldığı söylenmez. Gerçek bankada icra/kâr veya BLIND_OOS sonucuna dönüşmez. Ertesi gün farklı haberlerle altın yükselirse, G02 primini basit doğrusal olarak tersine çeviren SELL kuralı yanlışlanır. ANA-01, OLAY-02 ve ÖĞREN-03 değiştirilmedi.