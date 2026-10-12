# R70 — Mayısın doğru H3 tahminlerinden işlem stratejisine: art arda gelen tahminler

12 Ekim 2026. Uygulamalı 4-yıl strateji simülasyonu. Geliştirme/araştırma; canlı banka emri değil.

## 1. Aynı anda doğru üç H3 tahmini neden farklı işlem sonuçları doğuruyor?

| Tahmin günü | Kullanılan son gold günlük ortalaması D0 | Üçüncü fiyat gününün ortalaması D3 | Tahmin / gerçekleşen | O gün Türkiye 15:00 spot fiyatı | 15:00 girişinden ilerideki D3 ortalamasına fark |
|---|---|---|---|---:|---:|
| 7 Mayıs 2026 Perşembe | 6 Mayıs, 4675.01 | 11 Mayıs, 4701.32 | UP / UP doğru | 4735.895 | −0.730% |
| 8 Mayıs 2026 Cuma | 7 Mayıs, 4717.64 | 12 Mayıs, 4706.50 | DOWN / DOWN doğru | 4719.905 | −0.284% |
| 11 Mayıs 2026 Pazartesi | 8 Mayıs, 4718.13 | 13 Mayıs, 4696.97 | DOWN / DOWN doğru | 4664.225 | +0.702% |

Üç tahminin tamamı kendi D0→D3 günlük ortalama hedefinde doğru; tahmin başlangıç ve hedef fiyat günleri farklı, öngörü ufukları birbirinin üstüne biniyor. Dolayısıyla her birini ayrı ve yeni banka pozisyonu saymak yanlış. D3 gerçekleşen fiyatları tahmin zamanında bilinmiyordu. Spot veri Neon HistData sabit EST tarihli M15 open, gerçek banka alış-satış fiyatı değil. Modelin fiili 15:00 yayımlanma kaydı kanıtlanmış değil; saat bir araştırma varsayımı.

7 Mayıs UP sinyali saat 15 spotun önceki 6 Mayıs ortalamasından +1.302% yüksek olması nedeniyle geç alım uyarısıdır. 8 Mayıs ilk DOWN, spot önceki 7 Mayıs ortalamasının hafif üstündeyken risk azaltma fırsatını gösterir. 8 Mayıs Cuma 16:45 spot 4723.695 ile 11 Mayıs Pazartesi 09:00 spot 4671.845 arasındaki GERÇEK sonradan görülen fiyat farkı −1.098%; Cuma önceden bilinmiyordu. 11 Mayıs DOWN tekrarlandığında saat 15 spot 4664.225, önceki Cuma ortalaması 4718.13 değerinin −1.142% altındaydı; sonraki 13 Mayıs ortalaması ise bu spot fiyatının +0.702% üstünde. Zaten nakde çıkmış yatırımcıya tekrar satış emri vermek anlamsız.

## 2. Somut, test edilmiş durum-makinesi stratejisi

- Tek pozisyon: LONG veya CASH. H3 kararları birbiri üzerine binmiş olsa da aynı anda üç ayrı alış yapılmıyor.
- Yeni ALIM: iki ardışık günlük H3 UP kararı bekle. ALIM için deneysel ikinci varyant, güncel 16:45 spotun bu sinyalin kaynak D0 altın ortalamasından yüksek olmamasını şart koşuyor: fiyat yukarı kaçmışsa kovalama.
- SATIŞ/RİSK GÖZDEN GEÇİRME: elde altın varsa ilk H3 DOWN geldiğinde çık; nakitteyken tekrarlanan DOWN işlem tetiklemez. Aynı mantık 2026 Mayıs 7→8→11 zincirini üç işlem yerine tek bir pozisyon kararı olarak yorumluyor.
- Piyasa saati Türkiye 16:45, H3 araştırma saati varsayımsal 15:00; kaynak saat damgası ve bankanın yürürlükteki makası doğrulanmadan gerçek emir üretilmez.
- Piyasa spot araştırma kotasyonundan 16:45 al/sat; pozisyon tutulduğu süre boyunca sonraki kaynaklı fiyat aralığındaki fiyat farkını taşıyor, hafta sonu gap dahil; her AL ve her SAT için 12.5 baz puan, toplam 25bp varsayımsal maliyet. Yıllar ayrı başlatılıp son uygun sinyal gününde nakde çevriliyor; banka komisyonu, spread değişimi, emir kayması ve vergi yok.

## 3. GERÇEKTEN HESAPLANAN 2023–2026 sonuçları

| Yıl | Uygun 16:45 günleri | İlk UP al, ilk DOWN sat | İki UP al, ilk DOWN sat | İki UP + D0 ortalamadan yukarı kaçanı alma, ilk DOWN sat | Aynı referans ilk-son spot pasif fiyat değişimi (brüt) |
|---|---:|---:|---:|---:|---:|
| 2023 | 178 | +0.81% | −7.37% | −1.92% | +10.89% |
| 2024 | 240 | +0.99% | +9.58% | −0.93% | +27.93% |
| 2025 | 248 | +13.89% | +6.67% | +6.90% | +64.19% |
| 2026 Ocak–Eylül | 189 | −4.22% | +2.03% | +18.62% | −2.30% |

Strateji sütunları her giriş ve çıkışta 12.5bp varsayımsal maliyet çıkarılmış birleşik (bileşik) yüzdelerdir. Pasif piyasa fiyat değişimi brüttür; maliyet ve piyasada kalınan sürenin farklılığı nedeniyle net-riske göre karşılaştırma değildir. 2023 fiyat kapsamı tüm model günlerini içermez. Başarılı görünen 2026 +18.62% varyantı aynı haliyle 2023 ve 2024'te zarar ediyor; sonradan 2026'yı seçmek canlı kârı kanıtlamaz. 2025'te pasif altın biriktirip beklemek bütün aktif senaryolardan çok daha iyi. Bu varyantların hiçbirinde dört yıl boyunca güvenilir üstünlük kanıtlanmadı.

Üç UP bekleme, iki DOWN ile çıkma, tek UP girme ve gecikmiş fiyat giriş sınırı gibi altı şeffaf varyantın tamamı; bunların 10/25/50bp duyarlılıkları, pozisyonda geçirilen gün yüzdesi ve her AL/SAT tarihi ayrı CSV/JSON kanıtlarında. Bu kurallar ve örnekler geçmiş tarihleri gördükten sonra geliştirildiği için 2025/26 temiz kör test sayılmaz.

**Dikkat:** Çok basit D0-fiyatına göre gecikmiş sinyal filtresini tek başına bir yön sınıflandırıcısı olarak R66 üzerinde de sınadık: 15:00 2025 34/74 ve 2026 34/60. Bu tek başına yön başarısını arttırmıyor. Riskli/geç girişleri azaltmaya çalışmak ile yönü doğru tahmin etmek ayrı hipotezler.

## 4. Karar

Başlangıçta sanıldığı gibi çözümsüz değil: Eski H3'ü günlük otomatik işlem değil, sürekli yenilenen **pozisyon durum sinyali** olarak kullanan, art arda UP gerektiren ve ilk DOWN'da riski gözden geçiren bir mimari kurulabilir ve gerçek veride çalıştırıldı. Kısa vadede giriş/çıkış kararı verirken en son D0 günlük ortalama ile işlem anındaki spot farkı görünür tutulmalı.

Ancak bu bir **geliştirme adayı**, onaylı gerçek banka stratejisi değil. Önemli eksikler: 2026 modelin Ekim'de geliştirilmiş olması, eski 15:00 sinyal firstprint zamanının ispatlanmamış olması, değişken banka alış-satış makası ve emir gerçekleşme fiyatlarının olmaması, önceden sabitlenmiş ileriye dönük kör testin henüz yapılmaması. Modelin 135/191 başarılı ana H3 etiketi bankadaki işlemin +%70 doğruluk veya net getiri iddiası değildir.

Kaynak eserler: GOLD_R70_20261012_H3_ROLLING_STATE_BANK_1645_STRATEGY_COMPARISON.csv; GOLD_R70_20261012_H3_ROLLING_STATE_BANK_1645_STRATEGY_ACTIONS.csv; GOLD_R70_20261012_H3_ROLLING_STATE_BANK_1645_STRATEGY_SUMMARY.json. Önceki saat-ufku risk testleri R65–R69 ayrıca muhafaza edilmiştir.
