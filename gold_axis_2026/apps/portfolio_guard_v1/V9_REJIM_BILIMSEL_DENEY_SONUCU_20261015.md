# V9 · Rejim geçişi, maliyet ve çevrimiçi hata öğrenmesi

**15 Ekim 2026 | Salt okunur deney | Mevcut V7 korunmuştur**

## Araştırma sorusu

Altını Türkiye 09:00/12:00/15:00 işlem penceresinde, her AL ve SAT işleminden %0,8 maliyet kesilerek, geleceği kullanmadan kârlı biçimde yönetebilir miyiz? Geçmişte sonradan görülen aylık optimum stratejiler yalnızca eğitim teşhisidir; uygulanabilir işlem kuralı değildir.

## Gerçek kod geliştirmeleri

- `v9_state_transition.js`: Dört fiyat/çapraz piyasa uzmanı ve CASH seçeneğini çevrimiçi harmanlayan model. Gecikmiş 96 ve 336 saat sonuçlarından öğrenir; örtüşen günlük eğitim etiketlerinin etkin örnek sayısını düşürür. Sık alım-satım yaptığı için negatif.
- `v9_episode_guard.js`: Ayrı AL/SAT eşikleri, ardışık teyit, stres freni, minimum tutma, komisyon ve soğuma aralığı. 336 saatlik etiketleri en az 336 saat arayla oluşturarak örtüşmeyi azaltır.
- `v9_shadow_selector.js`: BASE, SLOW_EXIT, STRICT_ENTRY, POSTERIOR ve nakit gölge stratejilerinin yalnız önceki gerçekleşmiş, işlem maliyeti kesilmiş sonuçlarına bakar. Geçmişte en iyi uzmanın gelecekte de en iyi olacağını varsaymaz; bunu test eder.
- Bütün yeni deneylerde sinyal aynı barın alış fiyatından işleme girmez; emir varsayımı sonraki uygun banka kontrol noktasına aktarılır. V7'nin eski yürütme sözleşmesi farklı olduğundan doğrudan üstünlük kanıtı yoktur.
- `v9_research_audit.js`: Çok yıllı deney kayıtları ve model kabulünün otomatik engellenmesi. `v9_scientific_gate.test.js`: ileriyi görmeme, olgunlaşmış etiket, veri kaynak bütünlüğü, komisyon, API salt okunurluğu ve önceki sürümlerin regresyon testleri.

Toplam 6.724 kronolojik üç saatlik kayıt kullanıldı. 2025'te çakışan 1.892 altın fiyat kaydı iki tarihsel kaynak arasında birebir tutarlı. Bunlar gerçek banka ASK/BID kayıtları değil, araştırma MID fiyatları.

## 2024 ve 2025 negatif kontroller

| Dönem ve strateji | 100 $ başlangıçtan son bakiye | Pasif altın aynı yıl |
|---|---:|---:|
| 2024 V9 histerezis BASE | 125,1291 $ | 123,8497 $ |
| 2025 V9 histerezis BASE | 143,0611 $ | 160,4153 $ |
| 2025 V9 yavaş çıkış | 148,0311 $ | 160,4153 $ |
| 2024 V9 42 gözlem gölge uzman seçimi | 103,479 $ | 123,8497 $ |
| 2025 V9 42 gözlem gölge uzman seçimi | 109,614 $ | 160,4153 $ |

2024'te sınırlı üstünlük bulunsa da hiçbir V9 politika ailesi ve parametre seçeneği hem 2024 hem 2025 pasif altını aynı anda yenemedi. Eski V8'in 2024 sonucu 117,9761 $, 2025 sonucu 145,6746 $ idi; yöntemlerin zamanlama sözleşmeleri tam aynı olmadığından kıyas nedensel üstünlük iddiası taşımaz.

## 2026 Şubat–Eylül stres deneyi

Ocak sonunda önceki V1 deneyinden gelen 119,753917 dolar NAKİT başlangıcı:

| Strateji | Eylül 2026 sonu |
|---|---:|
| V9 anlık uzman karışımı (çok işlem) | 103,8724 $ |
| V9 rejim histerezisi BASE | 95,7654 $ |
| V9 42 kontrol noktası geçmiş performans seçici | 114,709 $ |
| V9 84 kontrol noktası seçici | 119,7539 $ (işlem yapmadı) |
| V9 maliyet-sonrası posterior koruma | 119,7539 $ (işlem yapmadı) |
| V8 hata öğrenmesi | 117,3323 $ |
| V7 eski araştırma referansı | **123,5295 $** |
| Sadece nakit | 119,7539 $ |

V9 seçicilerin hiçbiri bu önceden görülmüş tarihsel panelde V7'yi aşmadı. V7'nin önceki deneyle aynı-bar vekil fiyatı kullandığı, V9'un ise sonraki banka kontrolünde icra varsaydığı unutulmamalıdır. Hiçbir sonuç gerçek banka kotasyonuna dayanmıyor.

## Ekonomik ve bilimsel çıkarım

1. **Çevrimiçi hata öğrenmesi çalıştı, fakat işlem politikası kârlı hâle gelmedi.** Başarılı eğitim güncellemeleri başarı kanıtı değildir.
2. **İşlem maliyeti baskın.** Fiyat yönüne iyi tepki veren küçük hareketler bile %1,6194 başabaş fiyat hareketini aşmadıkça al/sat için ekonomik değer taşımayabilir. 2024/2025 naif uzman karışımı 100 doları yaklaşık 77,43 / 74,36 dolara indirdi.
3. **Histerezis başka rejime taşınmıyor.** 2024'teki pozitif sonuç 2025 ve 2026'daki kaybı gizleyemez.
4. **Geçmiş performans en iyi uzmanı güvenilir seçemedi.** Nakit seçeneği gereksiz zararları kısmen sınırlandırdı ama Ağustos gibi yükselişleri kaçırdı.
5. **Sinyal zamanı ile icra zamanı ayrıldı.** Sinyali oluşturan barın kendi fiyatından doldurma varsayımı azaltıldı. Bu, V7 ile karşılaştırma için de daha adil yeni bir sözleşme ihtiyacını ortaya koyuyor.
6. **Gerçek haber kanıtı henüz yok.** 96 OLAY-02 vakasının ilk erişilebilir yayın zamanları doğrulanmadığından habere dayalı nedensel öğrenme eklendiği söylenemez; gerçek banka BID/ASK ve 15 dakika emir yürüme verisi eksik.

## Sonraki araştırmanın bilimsel geçiş şartı

Aynı 2026 sonuçlarına göre tekrar tekrar eşik seçip sözde yüksek performans ilan etmek yerine, gerçek banka fiyatları ve makro bilgi vintageleri edinilmeli; 15 dakikalık karar öncesi veri ile olay evresi (başlama, yayılma, sönme, toparlanma) ayrıştırılmalı; hedef olgunlaşma/çakışma için purging ve embargo uygulanmalı; 2026'nın kör test olmadığı açıkça belirtilmeli. Araştırma altyapısına metodolojik dayanak: López de Prado (2018), *Advances in Financial Machine Learning* ve [purged validation](https://python.financial/concepts/purged-cross-validation/). Ek bir inceleme yönü [Oancea (2026), Dynamic Regime-Aware Conformal Calibration](https://arxiv.org/abs/2608.17079); conformal yöntem **henüz uygulanmadı**.

## Nihai karar

**V9 TERFİSİ REDDEDİLDİ.** Test edilen V9 modellerinin 2024 ve 2025 boyunca tutarlı üstünlüğü ve 2026 stres döneminde ikna edici başarısı kanıtlanmadı. V7 ve önceki sürümler değiştirilmedi. Banka işlem bağlantısı veya canlı al/sat yürütümü yok. Kaydedilmiş kod ve başarısız sonuçlar gelecekteki araştırmalarda değişmez karşı kontrol olarak tutulur.
