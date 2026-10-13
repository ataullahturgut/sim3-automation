# ALTIN OCAK 2026 — V4, HATALARDAN ÖĞRENEREK DÖRDÜNCÜ KEZ ARAŞTIRMA
**Çalışma tarihi:** 13 Ekim 2026. **Bilimsel statü:** geçmişte sonuçları görülen Ocak 2026 üzerinde deneysel, **prospektif/dokunulmamış OOS değil**. Bu çalışmanın amacı Ocak'ı kazandıracak eşik uydurmak değil, 2024–25'teki yanlış alarmların azaltılıp azaltılamayacağını sınamak. Önceki 2026 olay manifestinden öngörü alınmadı.
**Depo:** `ataullahturgut/sim3-automation`. Yeni branch `research-gold-jan26-two-factor-confirmation-v4-20261013` üzerinde, PR #127 ve önceki bilimsel PR'lar eski versiyonlarında korunur.

## 1. Önceki hatalardan hangi hipotezi çıkardık?
- B0 günlük kapanış / S4 yavaş trendler Ocak29-30 akşam düşüşüne karşı geç kaldı; banka Türkiye 09–17 işlem aralığı için çok geç olan NY17 kararı kullanıldı.
- V3 Türkiye **16:30TR son tamamlanmış M15 barı** A anomali ve T aşırı yükseliş göstergelerini hesapladı. 29 Ocak saat16:30 A ve T ayrık eşikleri aştı. Bunun 2024/25 için otomatik SAT sonucuna dönüşmesi ciddi zarar verdi: tek tek her alarm işlem değil.
- **Yeni ve tamamlanmadan önce kaydedilen hipotez:** A VE T aynı anda eşik aşmışsa uyarı daha seçici olabilir. Ancak A ve T **aynı altın fiyatından türetilen ilişkili değişkenlerdir**, bağımsız haber / metal / maliyet kanıtı değildir. Üstelik birlikte alarm verme hipotezi, Ocak 29'da A ve T'nin ayrı ayrı sinyal verdiği zaten görüldükten sonra kurulmuştur; Occam/fit riski yüksektir.
- Karşılaştırılacak iki sabit müdahale: (a) S4 pozisyonunun tamamını SAT ve 5 işlem günü cooldown; (b) yalnız **yarısını nakde geç**, sonraki en az 3 geçerli banka gününden sonra S4 pozitif ve yeni çift alarm yoksa tam ağırlığa dön. Ayrıca müdahalesiz S4.
- Parametreler ve seçim kapısı `GOLD_JAN2026_V4_DUAL_FACTOR_FROZEN_PROTOCOL_20261013.md` dosyasına, yeni sonuçlar hesaplanmadan önce commit edildi.

## 2. Çalıştırılan gerçek veri / as-of kuralları
- V3 araştırmasının tarih bazlı normalize **16:30TR fiyat kapanışı** ve hemen sonraki **16:45TR tamamlanan bar son fiyatı** kullanıldı. Yalnız sinyal anından **önce** tamamlanan barlarda bilinen altın fiyatı / gerileme / geçmiş 60 banka seansı getiri/medyanı özellik oldu; ertesi gün haberleri, 30 Ocak FED/Warsh ve ilerideki fiyatlar 29 Ocak modeline girmedi.
- A eşik önceki-bar-high sıralama QC uygulanmış 2022–23 EV q99 **5,676818**; T 2022–23 EV q99 **2,980590**. Her iki eşik değişmedi, 2025 veya 2026'ya göre optimize edilmedi.
- 2023–2025 EV 15 dakikalık gold bid/ask midpoint, Ocak 2026 HIST 15 dakikalık araştırma spot fiyatı. **Bankanın alım/satım kotasyonu, gerçek banka makası, işlem kabul edildiğine ilişkin veri YOK.**
- Ücret alış %0,8 + satış %0,8, ayrıca her işlem yönünde %0,15 **aleyhte** spot–banka varsayımsal fiyat farkı. %0 ve %0,30 alternatif duyarlılık. S4 başlangıç her yıl CASH, açığa satış yok. Dönem sonu eldeki altın için yalnız sonuç hesabında varsayımsal elden çıkarma kesintisi uygulanır.

## 3. Yıllara göre tam sayısal sonuç (0,8% + 0,15% maliyet)
| Yıl | S4 | S4 + çift alarmda %100 SAT | S4 + çift alarmda %50 SAT | Aynı dönem altın tutmak |
|---|---:|---:|---:|---:|
| 2023 | 6,54% | 6,54% | 6,54% | 10,10% |
| 2024 | 23,31% | 23,31% | 23,31% | 23,83% |
| 2025 | 40,05% | 44,97% | 43,84% | 61,08% |
| Ocak 2026 | 13,04% | 23,99% | 18,51% | 13,04% |

**İleri düşüş alarmları / kontrol evreni**
| Yıl | Gerçek bank seansları | Gelecek banka seansında ≥2% fiyat-low düşüş etiketleri | İki gösterge birlikte alarm | Alarmın düşüşle eşleşmesi |
|---|---:|---:|---:|---:|
| 2023 | 257 | 5 | 0 | 0 / tanımsız hassasiyet |
| 2024 | 259 | 12 | 0 | 0 / tanımsız hassasiyet |
| 2025 | 258 | 17 | 2 | 2 |
| JAN2026 | 21 | 1 | 1 | 1 |

- 2023 **0 ortak alarm**; 2024 **0 ortak alarm** ve **12 gerçek ağır bir-sonraki banka seansı aşağı hareketi** kaçırdı. Bu durum yanlış alarmları sıfırlasa bile **sıfır uyarı ile başarı sayılmaz**.
- 2025 yalnızca **2 ortak alarm** (22 Nisan ve 17 Ekim), iki olay da 16:30TR as-of referansına göre ertesi bank günü ≥2% fiyat-low gerilemesiyle eşleşti. Örneklem yalnız 2, etiket penceresi ileri bank-gün içi M15 low. Bu 2/2 oranı güvenilir hassasiyet iddiası için yetersizdir.
- Ocak 2026 yalnızca **1 ortak alarm** (29 Ocak), ertesi gün hedef düşüş gerçekleşti; bu olay ve yöntem seçim motivasyonu **önceden bilinen** sonuçtu. A/T kesimi 2022/23 olsa da V4 yöntemi Ocak'a bakıldıktan sonra seçildi.

**Daha önceden dondurulmuş bilimsel seçim şartı**: 2024 VE 2025'te S4'e en az +0,5 getiri puanı iyileşmesi, drawdown'ın >1 puan kötüleşmemesi, <=12 ücretli emir ve yılda en az 2 ortak alarm; alarm PPV'nin o yıl baz olay oranını geçmesi. Gerçek sonuç:
- S4 + çift alarm / tam satış: 2024 net fark 0,00 puan, 2025 net fark 4,92 puan, 2024 çift alarm 0, 2025 çift alarm 2. **Son karar: geçemedi.**
- S4 + çift alarm / yarım satış: 2024 net fark 0,00 puan, 2025 net fark 3,79 puan, 2024 çift alarm 0, 2025 çift alarm 2. **Son karar: geçemedi.**
**SONUÇ: BOTH REJECT / NO_MODEL_PROMOTION.** Çünkü 2024'te ortak alarm yok ve S4'e göre net ilave iyileşme sıfır. 2025'i kazanmak bu kabul şartını değiştirmez. 2024'te yanlış alarm azlığı, etkin olay kaçırma pahasına geliyor.

## 4. Ocak 2026, gün gün yeniden çalıştırma (Türkiye 16:30 kararı)
Aşağıdaki kararlar S4+AND100 deneyindedir; iki gösterge eşzamanlı eşik aşmadığında S4 TUT/AL/SAT kararı.
| Gün | Karar | Çift alarm | 60 bank seansı getirisi | Mekanik neden |
|---|---|---|---:|---|
| 2026-01-02 | AL | — | 8,27% | S4_UP |
| 2026-01-05 | TUT | — | 8,88% | none |
| 2026-01-06 | TUT | — | 11,72% | none |
| 2026-01-07 | TUT | — | 8,78% | none |
| 2026-01-08 | TUT | — | 7,66% | none |
| 2026-01-09 | TUT | — | 6,97% | none |
| 2026-01-12 | TUT | — | 8,64% | none |
| 2026-01-13 | TUT | — | 7,15% | none |
| 2026-01-14 | TUT | — | 7,86% | none |
| 2026-01-15 | TUT | — | 8,91% | none |
| 2026-01-16 | TUT | — | 13,39% | none |
| 2026-01-19 | TUT | — | 13,70% | none |
| 2026-01-20 | TUT | — | 16,21% | none |
| 2026-01-21 | TUT | — | 20,68% | none |
| 2026-01-22 | TUT | — | 22,75% | none |
| 2026-01-23 | TUT | — | 22,71% | none |
| 2026-01-26 | TUT | — | 27,76% | none |
| 2026-01-27 | TUT | — | 26,19% | none |
| 2026-01-28 | TUT | — | 31,56% | none |
| 2026-01-29 | SAT | ORTAK ALARM | 38,55% | DOUBLE_RISK |
| 2026-01-30 | TUT | A tek alarm | 26,39% | none |

**Kritik 29 Ocak:** 16:30TR'deki sıraya karşı konservatif gün içi tepeden-sonraki-dip gerilemesi **−2,2292%**, A=**6,83729**, T=**4,59664**; geçmiş eğitim eşikleri 5,67682 ve 2,98059. S4 kendi başına **TUT ALTIN** (60-seans getiri yaklaşık +38,55%); V4 AND, **SAT tamamı** veya **%50 azalt** kararı üretir. 16:45 spot son fiyatıyla teorik uygulama; gerçek banka al/sat kotasyonu ve bu anda gerçekleşmiş bir emir yok.
**30 Ocak:** çok daha büyük altın düşüşü zaten yaşandı; otomatik alarm olmadan S4 tutmaya devam eder. V4'ün Ocak performans iyileşmesi, 29 Ocak müdahalesinden kaynaklanır; 2024 tanısı bunu dış dönemde doğrulamıyor.

## 5. Ek spot-kotasyon maliyeti duyarlılığı — Ocak 2026
| İşlem başına %0,8 ana komisyon üzerine | S4 | Tam SAT | Yarı SAT |
|---|---:|---:|---:|
| +%0.00 işlem yönü ek fiyat farkı | 13,37% | 24,36% | 18,87% |
| +%0.15 işlem yönü ek fiyat farkı | 13,04% | 23,99% | 18,51% |
| +%0.30 işlem yönü ek fiyat farkı | 12,70% | 23,62% | 18,16% |

Bu rakamlar dolar cinsinden araştırma spot XAU fiyat endeksine dayalıdır, TL bakiyesi veya bankadan gerçekleşmiş net getiri değildir; karşılaştırmalı maliyet duyarlılığıdır.

## 6. Teknik doğrulama, sınırlılıklar, sonraki kapı
- V4 S4 baseline'ın 2023/24/25/Ocak hesapları, eski V3 16:45 sonuçlarıyla **12/12 (4 dönem × 3 maliyet senaryosu)** tam eşleşti; max fark yaklaşık 2.4e−14 getiri puanı.
- Önceki V3 fiyat kaynağı/yaz saati ve M15 OHLC high-low sıralama QA varsayımlarının tümü geçerlidir. V4 A için strict-high metodu kullanıldı, yani aynı bar içindeki high-low sırası gelecek olarak uydurulmadı. **M1/tick sırası ayrıca yok.**
- S4 uzun vadeli trendi korumaya yarayan araştırma çıpasıdır, altını elde tutma kıyasını 2023–25'te geçmemiştir.
- V4 tek tarihli sonuç seçilip canlıya çevrilemez: özellikle Ocak2026 birçok kez araştırıldığı için bağımsız ileri dönem, farklı altın price vendor ve **09–17TR gerçek banka alış-satış spread/fill logları** gerekir. Aynı saatli doğrulanmış gümüş/platin/paladyum XAG/XPT/XPD M15 ve haberlerin resmî firstprint UTC/etki türü, geleceği görmeyen olay mekanizması için hâlâ eksik.
- Sonraki meşru test = 2020/21 ayrı eşik-dışı dönem veya yeni ayrı gerçek zaman döneminde *önceden ilan edilmiş* AND hipotezi; çok seyrek alarmlı rejimde statistical power ve missed-event penalty ölç. Eğer 2024 gibi alarm yoksa model güvenilir genel şok koruması sayılamaz.

**Bilimsel karar:** V4 her iki alarmın aynı anda olduğu **nadir kriz-benzeri durumları araştırmak için daha seçici**. Fakat 2024'te ağır hareketlerin hiçbirini uyarmadığı için otomatik SAT olarak onaylanmadı. 'Ocak +23,99%' geçmiş olay-özel başarıdır, ileri kullanılacak onaylı model getirisi değildir.
