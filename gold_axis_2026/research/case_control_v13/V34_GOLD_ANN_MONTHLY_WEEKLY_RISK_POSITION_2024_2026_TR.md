# V34 — Aylık ANN + Haftalık ANN + Düşüş Riskleri + AL/TUT/ÇIK Simülasyonu

**27 Ekim 2026. Araştırma sürümü, canlı işlem değil.** Proje: ataullahturgut/sim3-automation, araştırma dalı research/gold-v34-ann-weekly-monthly-alert-position-20261027.

## Önemli sonuç

Aylık ve haftalık eski ANN modelleri gerçekten eğitildi, geçmiş tahminler hesaplandı ve kaydedildi. Eski V22 düşüş alarmları karar öncesindeki haftadan bağlandı. Yalnız 2024–2025 üzerinde seçilen işlem kuralı 2026'ya taşındı. **Kazanan kural AL/TUT çıktı; 2026 net getirisi -%11,035.** Ek aktif strateji deneyleri de net pozitif kâr üretmedi.

| Yöntem | 100 USD son değer | Net 2026 getiri | En yüksek gerileme | AL | ÇIK |
|---|---:|---:|---:|---:|---:|
| 2024–25 seçimi: HOLD | 88,965 | **-%11,035** | %25,09 | 1 | 0 |
| Buy & Hold baz | 88,965 | **-%11,035** | %25,09 | 1 | 0 |
| Tek başına haftalık ANN | 68,478 | **-%31,522** | %34,34 | 12 | 12 |
| Önceden tanımlanmış aylık+haftalık ANN ortak yön ve V22 veto | 90,077 | **-%9,923** | %12,94 | 4 | 4 |
| Nakit | 100,000 | **%0** | %0 | 0 | 0 |
| 2024–25 içinde en iyi aktif aday (2026 sonradan tasarlanmış aktif-kısıt duyarlılığı) | 81,874 | **-%18,126** | %31,06 | 5 | 4 |

**Komisyon:** Altına girişte %0,8, çıkışta %0,8. Terminal değer, açık altın varsa %0,8 varsayımsal kapanış giderini de içerir. Toplam alış–satış işlem maliyeti yaklaşık %1,6. Sermaye başlangıcı 100 USD, kaldıraç yok, short yok.

**Tarihler:** 5 Ocak–23 Ekim 2026; 42 haftalık karar/portföy gözlemi. İşlem vekili StakTrakr'ın 12:00 UTC (15:00 Türkiye) Pazartesi referans fiyatıdır, **gerçek bankanın alış/satış kotasyonu değildir**. Cuma 23 Ekim fiyatıyla net terminal değer işaretlendi. 26–27 Ekim aynı-kaynak fiyatı NOT_FOUND.

## 1. Aylık ANN — gerçekten çalıştırıldı

**MPA_ANN_ORIGINAL**, eski parametreler ve 8 dört-metal + tarihli GPR özelliği korundu. Yeni V28 gain/cap ayarları kullanılmadı. 2024 Ocak–2026 Eylül **33 aylık** gerçek orijin bazlı tahmin oluşturuldu. Hedef sonraki takvim ayının altın **ortalama fiyatı**, ay sonu veya banka işlem fiyatı değildir.

| Dönem | Tahmin sayısı | ANN MAPE | Önceki ay ortalaması naif MAPE | Doğru yön |
|---|---:|---:|---:|---:|
| 2024 | 12 | **%2,080** | %2,672 | 8/12 |
| 2025 | 12 | **%2,354** | %3,965 | 10/12 |
| 2026 Ocak–Eylül, doğrulanmamış Şubat hariç | 8 | **%4,909** | %5,040 | 5/8 |

Örnek: 2026 Haziran ortalama tahmini yaklaşık 4.547, gerçekleşen araştırma ortalaması 4.241 USD/ons; Ağustos tahmini yaklaşık 4.066, gerçekleşen ortalama 4.407. Büyük rejim değişimlerinde fiyatı ciddi yanılttı. 2026 Ekim için GPR-origin girdisi tamamlanmadığından aylık tahmin NOT_FOUND; October'e model uydurulmadı.

## 2. Haftalık ANN — gerçekten çalıştırıldı

Mevcut orijinal haftalık H=1 modelin tamamı yeniden çalıştırıldı. 16 giriş özelliği = Au, Ag, Pt, Pd × 4, 8 nöronlu tanh MLP, solver lbfgs, alpha=1, seed 1701; expanding tarihsel eğitim. Takip eden haftanın altın **haftalık ortalamasını** ve ayrıca haftanın son ortak günlük referans fiyatını tahmin eder. 2024 **53**, 2025 **52**, 2026 Ocak–Ekim **42**, toplam **147 gerçek haftalık model fit'i**.

| Dönem | Haftalık ortalama ANN MAPE | Naif önceki hafta MAPE | Doğru haftalık ortalama yönü |
|---|---:|---:|---:|
| 2024 | %1,439 | **%1,312** | 31/53 |
| 2025 | %1,967 | **%1,825** | 31/52 |
| 2026 | **%1,935** | %2,537 | 30/42 |
| 2026 sorunlu 27 Şubat haftası ve sonraki hafta hariç | **%1,880** | %2,561 | 29/40 |

2026'da haftalık fiyat hata metriği iyileşmiş görünse bile, 2024–25 dönemlerinde naiften kötüydü. 2026'daki fiyat hatası iyileşmesi de işlem kararı olarak kâra dönüşmedi.

## 3. AL / TUT / ÇIK karar algoritması

Sinyaller hedef hafta başlamadan önce hazırlanır: (1) haftalık ANN tahmini, (2) ilgili ayın **önceki ay bitiminde** üretilmiş aylık ANN tahmini, (3) en son tamamlanmış haftadaki BASE14 ve V22 risk incelemesi. **Aynı hafta sonunda açıklanacak model riskini pazartesi saat 15:00'te zaten biliniyormuş gibi kullanmak yasak.**

Aday politika aileleri: HOLD, WEEKLY_ANN, MONTHLY_ANN, ANN_CONSENSUS, ANN_EITHER, RISK_ONLY. ANN eşikleri %0, %0,5, %1, V22 veto açık/kapalı, asgari elde tutma 1/3 hafta. Her kural altın/nakit arasında ikili pozisyon taşır.

Sadece **2024–2025** için kriter: net getiri yüzdesi eksi (0,25 × maksimum çekilme yüzdesi) eksi (0,05 × işlem aksiyonu sayısı). 2025 Aralık son haftasının **2026 Ocak fiyatı içeren etiketleri** öğrenmeden atıldı. Eski ANN modellerinin kendi geçmiş-eğitimleri kök algoritmalarının orijinal şekilde expanding devam etti, fakat meta seçim 2026 fiyatına göre yapılmadı.

**2024–25 meta seçimi HOLD:** 103 uygun hafta, %117,426 net getiri; en yüksek çekilme %6,718. Dondurulan kural 2026'da **5 Ocak 2026'da 4.436,70 USD/ons referans fiyatla AL**, sonrasında sürekli **TUT**, **23 Ekim 2026'da 4.011,03 USD/ons üzerinden varsayımsal son değer**: 100 USD → **88,965 USD**. Son tasfiye maliyeti içeride; 23 Ekimde fiilî banka satışı olmuş gibi gösterilmedi.

**Neden riske rağmen HOLD?** Öğrenme penceresindeki 2024–25 uzun altın yükselişi daha sık al-sat yapan kuralları cezalandırdı; parametre öğrenmesi yeni 2026 düşüş rejimini öngörecek genel bir koruma kuralı bulamadı. 2026 para kaybı bu başarısızlığın ölçümüdür.

## 4. Aktif, işlem yapan modelin ayrıca sınanması

Ayrı incelemede 2024–25 adayları içinden **en az iki AL + iki ÇIK** yapan en yüksek puanlı kural seçildi: ANN_EITHER, haftalık yüzde getiri eşiği 0, V22 veto kapalı, en az 3 hafta tut. 2024–25 net +%101,141; 2026 net **-%18,126**, 100 → **81,874 USD**, 5 AL, 4 ÇIK, maksimum gerileme %31,062.

| İşlem tarihi (2026) | Aksiyon | Referans ($/ons) |
|---|---|---:|
| 5 Ocak | AL | 4.436,70 |
| 27 Nisan | ÇIK | 4.699,11 |
| 25 Mayıs | AL | 4.566,51 |
| 22 Haziran | ÇIK | 4.191,22 |
| 6 Temmuz | AL | 4.158,91 |
| 27 Temmuz | ÇIK | 4.087,70 |
| 10 Ağustos | AL | 4.351,55 |
| 31 Ağustos | ÇIK | 4.439,12 |
| 7 Eylül | AL | 4.406,47 |

**Önemli:** Bu aktif işlem adaylarına asgari-işlem koşulu **önceki 2026 araştırmaları görüldükten sonra** eklendi. Bu nedenle 2026 sonucu teknik olarak geriye dönük, **tam kör model ailesi doğrulaması değildir**; 2026 parametreleri doğrudan kârı artıracak şekilde yeniden seçilmedi. Son 7 Eylül alışının satış işlemi yok; nihai değer 23 Ekim likidasyon gideri dahil mark-to-market.

## 5. Eski düşüş alarmları ve V31

Eski BASE14, CFTC21 ve V22 model parametreleri değiştirilmedi. 2026 gün sonuçları önceki V33 çalıştırmasından alındı; V34 pozisyonlama girdisi **önceki tamamlanmış hafta V22**. V31 ekonomik olay katmanı 2026 önceden yakalama başarısını iyileştirmemişti ve Ekim tarihi olay verisi mevcut değil; bu nedenle bağımsız onaylı işlem veto sinyali olarak kullanılmadı.

**23 Ekim 2026 V33'te BASE14/CFTC21 RED ve V22 ACTIVE_REVIEW**, ama haftalık işlem kuralının bir sonraki uygulama günü **26 Ekim** olacaktı. O günün aynı kaynak banka-öncesi spot referansı **NOT_FOUND** olduğundan o tarihte kârlı bir ÇIK yapılmış gibi yeniden yazılmadı.

## 6. Kaynak ve model güvenilirlik sınırları

- StakTrakr 27 Şubat dört-metal bozuk kayıt için dış referans **2026-02-27 PM duyarlılık senaryosu** kullanıldı; aynı fiyat seansı, aynı benchmark veya canlı ilk-yayın otoritesi olduğunu kanıtlamaz.
- Geçmiş model fiyatlarının 12:00 UTC sağlayıcı etiketi, banka hesaplarındaki gerçek 15:00 TR alım/satım spread veya fiyat garantisi değildir. Satış/alış maliyeti **sabit %0,8** model varsayımıdır; gerçek bankanın fiyat farkının tutarını ayrı doğrulamadık.
- Geçmiş ilk yayın PIT belgeleri ve V31 Ekim makro olay/sürpriz arşivi eksik; 2026 geriye dönük sonuçları gerçek ileriye dönük başarı gibi göstermiyoruz.
- 2026 Ekim aylık ANN yok; aylık girdiyi kullanan kurallar Ekim'de yeni AL/ÇIK sinyali türetmek yerine **ABSTAIN, mevcut pozisyonu tut** yapıyor.
- Neon, ana üretim alarmları, orijinal ANN ve düşüş modeli dosyaları değiştirilmedi.

**Deney kararı:** Kod ve sayı sonucu **TAMAMLANDI**; gerçek para için **PROMOTION BLOCKED**. Üretilen modeller arasında 2024–25 öğrenilmiş ve 2026'daki **komisyon sonrası kârlı, kanıtlı bir AL/ÇIK sistemi yoktur.**

## 7. Denetlenebilir GitHub kayıtları

- Ana gerçek ANN ve 2026 strateji icrası başarılı: https://github.com/ataullahturgut/sim3-automation/actions/runs/40522147491
- Orijinal ANN tahmin kaynakları: https://github.com/ataullahturgut/sim3-automation/actions/runs/40520584007
- Genişletilmiş ANN hata analizi ve aktif işlem listesinin başarılı koşusu: https://github.com/ataullahturgut/sim3-automation/actions/runs/40523048467
- Python kaynak dosyaları: gold_v34_ann_replay.py, gold_v34_position_backtest.py, gold_v34_original_ann_accuracy_and_active_policy_audit.py
- Tahminler: outputs/v34_monthly_MPA_ANN_ORIGINAL_2024_2026_33_month_predictions.csv, outputs/v34_weekly_ANN_ORIGINAL_shard0..3.csv, outputs/v34_ANN_monthly_weekly_accuracy_2024_2025_2026.csv
- Meta öğrenme: outputs/v34_2024_2025_META_STRATEGY_SELECTION_NO_2026.csv
- 2026 net bütün politikalar: outputs/v34_2026_ANN_RISK_POSITION_NET_PNL_COMPARISON.csv
- 2026 haftalık tüm ana kararlar: outputs/v34_2026_SELECTED_AL_TUT_CIK_EXECUTIONS.csv
- Aktif alternatifin işlemleri: outputs/v34_2026_BEST_2024_2025_ACTIVE_POLICY_TRADES.csv
- Tam kaynağı: outputs/v34_weekly_monthly_risk_joint_input_ASOF.csv ve çıktılar için manifestler.

**Kontrol ve Uyum Özeti:** Sayılar gerçek model iş akışı, bağımsız GitHub Actions koşuları, 2024–25 dondurulmuş meta seçim ve %0,8 + %0,8 komisyonlu 2026 yürüyüşünden alınmıştır. Eksik/olgunlaşmamış fiyat sonuçları doğru kabul edilmedi, hisse/altın bankacılık işlemi gerçekleşmiş gibi gösterilmedi.
