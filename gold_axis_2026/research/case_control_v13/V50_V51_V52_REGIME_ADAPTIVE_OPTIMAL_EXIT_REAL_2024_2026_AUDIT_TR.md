# V50–V52 | GOLD — REJİM ÖĞRENEN, ÇIKIŞ ZAMANLAMASINI ÖĞRENEN İKİ MODEL VE FİZİKSEL DÜŞÜŞ DENETİMİ
**31 Ekim 2026 · Bağlı Gold Control Neon + GitHub · ARAŞTIRMA/İŞLEM YOK · 2024–2026 olayları daha önce araştırmada görüldü, kör test değil.**

## Gerçek problem

V22 **EARLY_RISK** = yalnız `WATCH` başlatır. Kullanıcı altın güçlü yükselmeye devam ederken ÇIK demek istemiyor; önemli düşüş başlayınca mümkün olduğunca uygun zamanda **ÇIK sinyali** gerekiyor. **ALIM, TEKRAR ALIM, NAKİT YÖNETİMİ VE PORTFÖY OPTİMİZASYONU YOK.**

Önceki V43/47/48/49 %4 düşüş sonucu ve %2 yükseliş sonucu ile **erken satılan rallinin fırsat maliyetini** yeterince hedeflemiyordu. Yeni yöntemler daha sonra iyimser varsayımlara dönüşmesin diye farklı risk politikaları önceden tanımlandı; en iyi görünen 2025/2026 senaryosu seçilip "kör başarı" denmedi.

## Kanıt ve veri

- Neon **`public.gold_research_histdata_xau15m_candidate`** yaklaşık **156.366 XAU/USD 15m aday barı**, 2020 Ocak–2026 Ekim ilk günü.
- 2024 ve 2025 V22 kararları `outputs/v22_daily_decisions.csv` **özgün araştırma `effective_review`** satırlarıdır. 2026 ise V33 senaryosundaki `model_v22_review`. Bunlar **aynı sürüm değildir** ve PIT/ilk yayın saatleri ispatlı değildir.
- WATCH, V22 uyarı gününün tamamlanmasından sonra **ilk gözlenen piyasa barında** başlar. D tarihinde V22'yi D 00:00'dan biliyormuş gibi varsaymıyoruz.
- Tahmin özellikleri yalnız mevcut ve önceki fiyat bilgilerini içerir. Gelecek fiyatlar yalnız eğitim sonucu / tarihsel sonuç değerlendirme etiketleridir.
- Sonraki bar kapanışı araştırma referansı; **bankanın işlem yapılabilir BID fiyatı değildir**, alış/satış maliyeti veya PnL modellemesi yapılmadı.

## V50 — Üç piyasa rejimi ve beş-seanslık fitted-Q optimal stopping yaklaşımı

Her ay *geçmiş 730 günün*, ilgili ay başlamadan **tamamlanmış beş piyasa seansı sonuçlarına** sahip ~3.500–4.000 adet 15m barı/samples kullanılır. Üç K-means gizli fiyat-rejimi, nedensel momentum ve volatilite özellikleriyle birlikte `HistGradientBoostingRegressor` öğrenicisine girer.

Beş adımlı geriye doğru Bellman-benzeri regresyon:
`Q_h(s) = E[log(P_next/P_now) - lambda*maxDrawdownUntilNext + max(0,Q_{h-1}(s_next)) | s]`
Burada `Q_h>0` ise BEKLE, `Q_h<=0` ise ÇIK. V22 riski bulunmazsa hiçbir ÇIK yoktur. Regresyon **yaklaşık fitted optimal stopping** olup matematiksel olarak kanıtlanmış en iyi işlem zamanı değildir. Önceden risk-cezası `lambda=0.35` ve `0.8`, 1 ve 4 ardışık bar teyidi test edildi.

### Gerçek sonuçlar — daha güçlü risk cezası ve 4 bar teyidi (`lambda=.8`)

| Yıl | V22 WATCH | CHIK sinyali | 5 seansta ≥%4 aşağı fiyat hareketiyle eşleşen | Eşleşmeyen | Gelecek veri eksik |
|---|---:|---:|---:|---:|---:|
| 2025 | 2 | 2 | **0** | 2 | 0 |
| 2026 Eylül sonuna kadar | 7 | 7 | **4** | 2 | **1** |

**Sorun:** 2025 Nisan uyarısı 4 Nisan → 6 Nisan 23:45 UTC çıkış; sonra 20 takvim gününde **%16,24 yükseliş** kaybedilebilirdi. 2025 Ekim de erken/sonuçsuz ÇIK. 2026 Ocak'ta 22 Ocak V22 uyarısını izleyen ilk fiyat günü **23 Ocak** çıkış yaptı; yirmi günde **%12,87 sonraki yükseliş** görüldü. Fitted-Q'nun seçilen aşağı yönlü risk cezası, öngörülen devam etme yararını bastırarak erken çıkışa kaydı.

Bu **başarısız deney** saklanmadan kaydedildi.

## V51 — İlk defa erken ÇIK'ın kaybettirdiği ralliyi doğrudan öğrenme hedefi yapma

2024 Ocak–2026 Eylül arasında **33 ayrı aylık öğrenme**:
- 20 takvim gününün tarihsel maksimum yükselişi → *ÇIK şimdi* kararının fırsat maliyeti için eğitim etiketidir; gerçek zamanda bu zirveyi kimse bilmez, **geçmiş eğitim etiketi olarak oracle** kullanılır.
- 5 sonraki NY17 piyasası seansının maksimum olumsuz altın hareketi → *BEKLE* kararının fiyat riski etiketi.
- Aylık geçmiş 730 günde olgunlaşmış her iki etiket üzerinden iki ayrı quantile gradient boost regression; fiyat trend/oynaklık özellikleri + üç rejim ağırlığı.
- Önceden `risk_weight = 1.0` ve `1.5`; yalın değer karşılaştırma ve yükseliş rejimi koruma katmanı; 1 veya 4 bar teyidi. Karar: `predicted_20day_upside <= risk_weight * predicted_5session_downside` ise ÇIK, aksi halde BEKLE. Rejim korumada yükseliş rejimi olasılığı yüksekse satışı geciktirir.

### 1.0 risk ağırlığı, yükseliş rejimi koruması ve 4 bar teyidi — araştırma adayı (8 önceden tanımlı aday arasından)

| Yıl | V22 WATCH | CHIK | 5 seansta ≥%4 düşüşe eşleşen | Sonuçsuz | Hiç ÇIK yok |
|---|---:|---:|---:|---:|---:|
| **2024** | 7 | 1 | **0** | 1 | 6 |
| **2025** | 2 | 1 | **1** | 0 | 1 |
| **2026** | 7 | 4 | **3** | 1 | 3 |

**Özellikle önemli 2025:** Nisan 4 V22 → **BEKLE** (erken ÇIK üretmedi, 22 Nisan zirvesine yükseliş korunabildi); Ekim 10 V22 → **17 Ekim 15:30 UTC ÇIK**, sonraki 5 seansta fiyat en az %4 düştü. Ancak Ekim ÇIK sonrasında fiyat önce **+%2'nin üzerinde yükseldi**, bu yüzden daha katı `down4-before-up2` ölçütünde başarılı değil. V22 Nisan–Mayıs aynı WATCH kümesi olduğundan *Mayıs'taki ayrı fiziksel düşüşü zamanlamış değildir*.

**2026:** Jan 22 V22 → Jan **23 erken ÇIK** (sonraki 20g yükseliş **%12,87**, ana sorun sürüyor). Mart 19 V22 → Mart 25 ÇIK ve sonraki ≥%4 düşüşe eşleşme. **Haziran** V22 → **hiç ÇIK yok** (kaçırılan önemli fiziksel düşüş). Ağustos ilk WATCH → **14 Ağustos sonuçsuz ÇIK**; sonraki WATCH → 26 Ağustos ÇIK düşüşle eşleşti. Nisan ve Eylül WATCH'ları için teyit yoktu.

**Aday seçim uyarısı:** 2025'te 1/1 görünmesi **belirli varyanta** ait. Önceden bütün varyantlar denendi, 2025/26 örnekleri önceden incelendi, sonuç **bağımsız ileri test değildir**. Yükselişi koruyan varyant, düşüş kapsamını düşürüyor.

## V52 — V22'den tamamen bağımsız fiziksel %4 fiyat düşüşü olayları

Bu aşamada yanlış başarı oranı üretmeme amaçlandı: V22 uyarı kümelerini kullanmadan, aday XAU 15m fiyatından son **beş gerçek NY17 seansı** içindeki en yüksek fiyatın en az **%4 altına ilk geçildiği** kayıtlar çıkarıldı. %2'den az fiyat geri çekilmesiyle yeniden ayrı olay başlatma kuralı vardır. İlgili %4 ilk geçişinden **önceki 10 takvim gününde** V22 WATCH'ın kullanıma açılmış olması veya adayın ÇIK vermiş olması sayılır. V22 D tarihlemesi **D günü 00:00'da var sayılmaz**, D sonrası ilk gözlenen fiyat barına ötelenir (firstprint yine sertifikalı değil).

| Yıl | Bağımsız tanımlı fiziksel ≥%4 düşüş olayı | Kullanılabilir V22 uyarısı öncesinde var | V51 1.0 rejim-koruyan ÇIK öncesinde var |
|---|---:|---:|---:|
| 2024 | **7** | **1** | **1** |
| 2025 | **10** | **6** | **3** |
| 2026 Eylül'e kadar | **15** | **10** | **3** |

Bu olaylar "bütün altın düşüşlerinin tek doğru evrensel sayısı" değildir: beş seanslık tepe takibi, %4 eşik, %2 yeniden-kurma ve 10 günlük eşleşme penceresi parametreleri sayıyı etkiler. **Fakat önemli karşı-kontrol şudur:** Sadece verdiği CHIK sinyallerinin ardından fiyat düştü mü diye bakarsak model iyi görünür; **bütün gerçek düşüşleri** bağımsız tanımlayınca düşüş kapsamı belirgin eksik. Ayrıca düşüş başlamadan önce V22'nin hiç uyarmadığı olayları hiçbir V22-şartlı yöntem yakalayamaz.

### Artık sağlam bilinen teknik sınır

1. Sadece **V22 risk verdiğinde** çıkış zamanını öğrenmek, V22'nin uyarı vermediği 2024/2025/2026 fiziksel düşüşleri tespit edemez. Bu *yeni exit öğrenicisinin değil, üst risk-gate'in kapsama sınırıdır*.
2. Erken ÇIK'ı azaltan fiyat-temelli öğrenme, bazı gerçek düşüşlerde ÇIK vermemeye kayar; **yanlış alarm vs kaçırılan düşüş** iki taraflı maliyet gerekir.
3. Modelin gerçek V22 olayına koşullu öğrenmesi için aynı V22 sürümünün 2020–26 döneminde as-of tekrarının üretilmesi şarttır. Mevcut "tüm piyasa fiyatlarından öğren, V22 günlerinde uygula" veri dağılımı farklılığını kapatamıyor.
4. Etiketler ve kararlarda birbirini izleyen %4 düşüş olayları bağımsız olmayabilir; 7/10/15 örneklerle parametrik başarı iddiası kurulamaz.
5. Bilinmeyen 15m ilk görülme anı, banka alım-satım spread ve emir gecikmesi varken gerçek SAT fiyatı hesabı yapılamaz. CANLIYA alınmadı.

## Deney kodu ve doğru sonuçlar

- V50 `risk_v50_regime_fitted_optimal_stopping.py`; unit tests 10 PASS;
  GitHub Actions **başarılı**: https://github.com/ataullahturgut/sim3-automation/actions/runs/41195519886
- V51 `risk_v51_learned_foregone_rally_regret.py`: 33 ay geçmişten öğrenme, 3 yıl gerçek dönem;
- V52 `risk_v52_physical_decline_episode_recall.py`: ayrı fiyat olayları ve ilk uygun V22 uyarı zamanlarını test;
- Son **V51+V52** yeniden çalıştırma: **21/21 birim test PASS**, gerçek Neon ve her olay için denetim artifact arşivi:
  https://github.com/ataullahturgut/sim3-automation/actions/runs/41196286631
- GitHub Actions artifact isimleri:
  `gold-v50-five-session-fitted-q-regime-research`;
  `gold-v51-missed-rally-cost-aware-exit-2024-26` (V51 ve V52 JSON ikisi birlikte).
- **NO BUY / no reentry / no portfolio / no live deployment / no Neon write / no execution order**.

**Sonuç:** Bilimsel açıdan iki tamamlanmış yeni öğrenme yöntemi (V50 ve V51) ve bunların sınırlamalarını ortaya çıkaran bağımsız fiziksel düşüş denetimi (V52) oluşturuldu. V51 belirli ayarda 2025 Nisan erken satışını önlese de 2024 ve 2026 hata/kaçırma problemi çözülemedi. Uygun çıkış algoritması hâlâ araştırma aşamasında, canlı sistem değiştirilmedi.
