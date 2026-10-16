# KAVİS CORE — Ocak 2023 Matematiksel Deneyim ve Ekonomik Hareket Raporu

**Tarih alanı yalnız koşu/rapor tarihidir, modelin karar girdisi değildir.** 2023 Ocak dışına geçilmedi. Başlangıç 100 USD CASH, XAU M15 HistData spot fiyat vekili, TR hafta içi 09:00–17:00, %0,8 alış + %0,8 satış. Bu fiyatlar bankanın gerçek BID/ASK kaydı değildir; haber ilk-yayın bilgileri sonradan yeniden kurulmuş bir araştırma arşividir. Sonuç kör bağımsız dönem kanıtı değildir.

## Gerçekleşen Ocak deneyinin özeti
| Ölçüt | Değer |
|---|---:|
| Gözlenen Ocak M15 altın satırları | 1.764 |
| Banka işlem penceresinde as-of karar kontrolleri | 645 |
| Olgunlaşmış çok ufuklu fiyat/olay matematiksel eğitim güncellemeleri | 5.158 |
| Sıfırdan farklı katsayı güncellemeleri | 5.158 |
| Matematiksel özellikte aktif yayımlanmış makro kayıtları | 4 |
| Haber bilgisi geçerli olduğu banka kontrolleri | 33 |
| AL / SAT emirleri | **0 / 0** |
| Başlangıç → ay sonu teorik likidasyon NAV | **100,00 → 100,00 USD** |
| Nakit karşılaştırması | 100,00 USD |
| İlk uygun seans AL, ay sonu teorik SAT (aynı vekil/maliyet) | **103,007703 USD** |
| En yüksek gerçekleşmiş risk-düzeltilmiş pozisyon değiştirme puanı | **−1,459604 log-%** |
| Minimum gözlenen puan | **−2,131663 log-%** |
| İki bacak ücreti log eşdeğeri | **1,606434 log-%** |

**Bilimsel karar:** Şimdiki KAVİS CORE V0 kendi matematiksel ağırlıklarını sürekli güncelleyebiliyor, ancak pozisyon değiştirme politikası **fırsatları yakalama açısından başarısız**: hiç altın almadı ve pasif altının yaklaşık 3,01 USD gerisinde kaldı. **Sıfır işlem yüksek strateji başarısı değildir.** Parametreleri bu Ocak sonucunu kazandırmak için değiştirip aynı ayı yeniden test ETMEDİK.

## Ekonomik olaylar nasıl kullanıldı? (tarih karar kriteri değil)
Model şu **post-release-lineage** kayıtlarını yalnız açıklama yayımlandıktan sonra gösteren ekonomik `G01_RATES_USD` özelliklerine çevirdi:
- AHE, NFP, işsizlik: 6 Ocak 2023 açıklama grubu; işaretli sürpriz sırasıyla yaklaşık −0,5 / +0,1533 / −1,0 (kayıt ölçeklendirmesine göre).
- CPI: 12 Ocak 2023; işaretli sürpriz −0,5.

Bu bilgiler modelde sabit `if(CPI)` alım veya `if(NFP)` satım kuralı yaratmadı. Güncellenen G01 katsayıları dört ufukta yaklaşık **−0,04697**, **−0,05238**, **−0,06254**, **−0,09070**. Bunlar bir olay türü için **sınırlı, korelatif regresyon ağırlıklarıdır**; dört açıklamadan nedensel etki veya gelecek yıllara genellenen bilimsel ilişki ispatlanamaz. Olayların aynı anda farklı etkileri bulunabilir. Dolar/diğer metal/NQ/ETF bilgileri bu koşuda eksik olarak işaretlendi, sahte sayı atamadık. Bütün bunlar ana manifestte ileri veri entegrasyonu için ayrı denetim gerektirir.

## Matematiksel öğrenme raporu
| Gelecek ufuk | Olgunlaşmış örnek | Ortalama mutlak hata (% log ölçeğinde) | Son G01 katsayısı |
|---|---:|---:|---:|
| 4 saat | 1.609 | 0,2613 | −0,046970 |
| 1 işlem günü (24 saat elapsed) | 1.309 | 0,5554 | −0,052379 |
| 3 gün | 903 | 0,7394 | −0,062542 |
| 1 hafta | 1.337 | 1,1555 | −0,090702 |

Ufuklar saat/dakika süresidir; piyasa tatili ve hafta sonu nedeniyle kayıt yaşlarının gözlemlenme sıklığı farklıdır, bu nedenle her ufukta eşit sayıda hedef yoktur.

## Önceden görülmemiş olarak sunulmayan büyük hareketlerin ex-post denetimi
*Bu hareketler sonuçları tamamlandıktan sonra aylık rapora seçildi, karar anında gelecek olarak modele verilmedi.*
- 6 Ocak 13:00–17:00 UTC: **+%1,463** (4 saat); 13:30 UTC makro açıklamalarının çevresinde. Haberle ilişkili aday açıklama, tek başına nedensellik kanıtı değil.
- 31 Ocak 12:30–16:30 UTC: **+%1,337** (4 saat).
- 5 Ocak 12:00–16:00 UTC: **−%1,059** (4 saat).
- 4 Ocak 04:30–08:30 UTC: **+%0,973** (4 saat).
- 18 Ocak 14:15–18:15 UTC: **−%0,973** (4 saat).
- 3 Ocak 07:45–11:45 UTC: **−%0,955** (4 saat).

Hareketin tamamı alınıp satılarak kazanılabilecek tutar değildir; banka penceresi ve en az %1,6 tur maliyeti uygulanır. "En büyük 4 saatlik hareketleri seç" kuralı algılayıcının tanımı yapılmadan alım/satım kuralına dönüştürülmez.

## Ocak'tan çıkan matematiksel eksikler
1. Gözlenen 5.158 **tahmin/ekskürsiyon katsayısı güncellemesi**, ekonomik işlem politikasına otomatik olarak aktarılmış **uzun vadeli yeniden giriş stratejisi** sayılmaz. Politika hâlâ tahmini net getiri + risk ölçüsüne dayalı; **cash-vs-gold karşı-olgusal karar/yeniden giriş critic'i** ve risk-düzeltilmiş ekonomik yol kredi ataması eksik.
2. Haber etkisinin matematiksel işareti 4 örnek için kırılgan; metals/ETF/hisse/tahvil/FX gerçek PIT feed eklenmeden "altın neden yükseldi" gibi kesin olay sebebi iddiası kurulamıyor.
3. Kapsam ve matematiksel kalite artırılırken dahi işlem yapmamak modelin yeterli olduğu anlamına gelmez: bu ay pasif altın +3,0077 USD, model 0.
4. Bu ayın yanlış tahmin ve fırsat kaçırma raporu sonraki algoritma sürümü için tanısal girdidir; aynı Ocak sonuçlarını görüp sonucu kazandıracak eşik/horizon seçmek **bağımsız test** değildir.
5. Modeli gerçek çok-ufuklu **optimal stopping + yeniden giriş critic + olayın yayılma/bitme süresi** yapısına dönüştürmeden Şubat'a geçilmez. Tarih içermeyen öğrenme karakteri korunur.

## Kalıcı Ocak dosyaları
- `MATH_AUDIT.json`: aylık ekonometrik kayıt, 6 ex-post önemli hareket, öngörü ufukları ve başarısızlık;
- `EVENT_ECONOMICS.jsonl`: 4 yayın-zamanlı makro kayıt, kaynak soy-ağacı;
- `DECISIONS.csv`: 645 kararın gerçekleşen as-of puan ve masraf defteri;
- `CORE_CHECKPOINT.json`: **öğrenilmiş tahmin başlığı ağırlıkları ve devam eden gecikmeli label/portföy durumu; bu V0 sürümünün ekonomik özellik kodlayıcısı sabittir, henüz eğitilmiş bir encoder değildir**, gelecek aylara taşıyabilmek için tarih-özelliksiz model state;
- `MONTH_REPORT.md`: bu insan-okunur yorum.

Koşunun tüm kanıtı: https://github.com/ataullahturgut/sim3-automation/actions/runs/38908324549
Ayrıntılı gerçek senaryo artefaktı: https://github.com/ataullahturgut/sim3-automation/actions/runs/38908324549/artifacts/12049356138

**2023 Şubat veya 2025 sonuna kadar koşu yapılmadı.** Ocak başarısızlığını düzeltecek mimari bir sonraki deney tasarımı olacak; mevcut rapor ve state bozulmadan korunur.
