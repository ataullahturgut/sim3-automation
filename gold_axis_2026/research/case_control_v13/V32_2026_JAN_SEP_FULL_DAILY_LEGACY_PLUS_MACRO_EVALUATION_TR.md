# V32 | 2026 Ocak–Eylül — BASE14 / CFTC21 / V22 + V31 gerçek birleşik model karşılaştırması

**27 Ekim 2026 — uygulandı ve GitHub Actions üzerinde gerçekten çalıştırıldı.**  
**Dal:** `research/gold-risk-v32-2026-full-year-to-date-combined-audit-20261027`  
**Başarılı çalıştırma:** https://github.com/ataullahturgut/sim3-automation/actions/runs/40505428422 — 8/8 kontrol PASS, tüm geçmiş 161 orijinal V22 karar günü ve 1.572 eski risk skoru paritesi PASS, iki fiyat duyarlılık senaryosu.

## SONUÇ: Yeni V31 önceden yakalanan büyük düşüş sayısını arttırmadı

**Ocak–Eylül 2026 günlük fiyat takviminde 194 gün var.** BASE14/CFTC21/V22 orijinal model sürümleri, 27 Şubat hatasının iki *fiyat tanımı onaylanmamış* AM/PM araştırma senaryosunda **187** günde skorlandı; 22–30 Eylül'deki son **7 günlük model fiyat/skor kapsaması eksik** (`NOT_SCORED`). Bu nedenle **194 fiyat günü = 194 model alarmı değerlendirildi** demek yanlış. 2026 1 Ekim–27 Ekim tüm günler için **yeni bir doğrulanmış V31+model karşılaştırması yok**; mevcut takvim dosyasında en son 16 Ekim fiyat satırı vardır ama 2026 model risk skorunun tarihsel çalışma sınırı 21 Eylül'dür.

V31'in 2026 veri kaynağı 23 olay (9 NFP, 9 CPI, 5 FOMC):
- Makro olay saatinden 35 dakika sonra fiyat barı hesaplanabilir ve 2023–2024 aynı olay ailesi %10 alt kuyruk eşiğini geçen **3/23** olay.
- Bunların **2/23'ü (29 Nisan FOMC, 17 Haziran FOMC)** TR bankada işlem yapılabilir saatler **dışında**, **1/23'ü (5 Haziran NFP)** banka saatinde.
- **2/23** olay fiyat barları eksik (Eylül NFP ve CPI), kesinlikle tahmin olarak doldurulmadı.
- Tek banka-saati ekonomik risk olayı **5 Haziran 2026 saat 16.05 TR**. O gün BASE14 RED ve V22 `ACTIVE_REVIEW` zaten mevcut. V22 orijinal günlük kararın **16.05'te elverişli olduğu kanıtlanmamıştır**; aynı tarihli 2026 retrospektif uyarı olması, aynı saniyede görüldüğü anlamına gelmez.
- Sonuç: **V31'in eklediği yeni takvim alarm günü = 0, son 10 fiyat oturumu içinde yeni düşüş-öncesi yakalama = 0.**

## Beş seans ileride en az %5 (ve %4) araştırma hedefi

**Aynı ortak payda**: 187 BASE14/CFTC21/V22 skor günü, beş gelecek fiyat seansı tamamlanmış. `return_5d = 100 × (min(gold[t+1..t+5]) / gold[t] − 1)`. Bu hesap yalnız *sonradan sonuç ölçümüdür*, modelin girdisi değildir. Ortak payda, aynı kaynak, aynı işaret, aynı sorumlu eski alarm kodu, **hiç yeni parametre yok**.

| Senaryo | Algoritma/katman | Alarm günü | Sonraki 5 fiyat seansında düşüş >=%5 görülen | Böyle düşüş görülmeyen | >=%4 düşüş görülen |
|---|---|---:|---:|---:|---:|
| AM araştırma fiyatı | BASE14 RED | 63 | 13 | 50 | 19 |
| AM | CFTC21 RED | 43 | 9 | 34 | 14 |
| AM | **V22** | **43** | **12** | **31** | **14** |
| AM | V31 ilave banka-saati riski | **0** | 0 | 0 | 0 |
| AM | **V22+V31** | **43** | **12** | **31** | **14** |
| PM araştırma fiyatı | BASE14 RED | 63 | 13 | 50 | 19 |
| PM | CFTC21 RED | 43 | 9 | 34 | 14 |
| PM | **V22** | **42** | **12** | **30** | **14** |
| PM | V31 ilave banka-saati riski | **0** | 0 | 0 | 0 |
| PM | **V22+V31** | **42** | **12** | **30** | **14** |

**Hata sınıfı farkı:** Bu **alarm günleri** ve sonraki 5 gün etiketleridir; **bağımsız büyük düşüş olayları, stop-loss getirisi veya bankada gerçekten elde edilen PnL değildir**. Bir alarm 5 gün sonrası %-5 etiketinde başarısız olurken daha geç bir ekonomik düşüşte önceden sinyal vermiş olabilir. Tersine düşüş başladıktan sonra RED olması olayın önceden yakalandığı anlamına gelmez. Yine de yeni katmanın ortak örneklemde **hiç marjinal takvim günü** eklemediği tartışmasız.

## Önceden sabitlenmiş 2026 düşüş zirveleri (10 seans strikt öncesi)

| Fiyat olay grubu | Zirve | Eski V22 ilk inceleme | V31 ilk banka-saati olayı | Birleşik sonuç |
|---|---|---|---|---|
| Ocak | 29 Ocak | 22 Ocak | yok | Eski uyarı korunuyor, V31 katkı yok |
| Mart | 12 Mart | **26 Şubat, yalnız AM/PM karantina duyarlılık varsayımıyla** | yok | **Koşullu** eski uyarı, V31 katkı yok |
| **Haziran ilk bacak** | **4 Haziran** | **yok** | **yok** | **Kaçırıldı** |
| Haziran ikinci bacak | 17 Haziran | 5 Haziran | 5 Haziran | Eski uyarı zaten vardı; **aynı ekonomik aile, yeni bağımsız başarı değil** |
| Ağustos | 25 Ağustos | 11 Ağustos | yok | Eski uyarı korunuyor, V31 katkı yok |

Haziran olay sonrası erken tanı: 5 Haziran NFP 15.30 TR açıklandı, ilk 30 dakika XAU **-%1.2072**, V31 geçmiş veriyle **16.05 TR** riski işaretler; 4 Haziran zirvesinden **sonra** olduğundan ilk bacak prepeak erken yakalama değildir.

**Ekonomik aile ayrımı:** 2026'da 4 bağımsız tarihsel ekonomik düşüş ailesi (Ocak/Mart/Haziran/Ağustos). Eski V22 üç ailede **koşullu** prepeak (Mart fiyat senaryosu henüz sertifikalı değil); Haziran ilk bacak kaçırıldı. V31 artış **0/4**. Haziran ikinci bacağı ayrıca beşinci bağımsız başarı gibi sayılmaz. Bu dört tarihsel olay önceden analiz edildiği için 3/4 de kör veya gerçek zamanlı başarı tahmini değildir.

## 2026 saat ve kaynak bütünlüğü

- V31 yalnız **NFP/CPI/FOMC tarihli olay** etrafındaki 5dk altın tepkisini görür. **JOLTS/ADP** Haziran öncülleri bağlamsaldır ve tarihsel konsensüsün yayın öncesi güncellenme saatleri bağımsız kanıtlanmadığı için otomatik RED değildir.
- 2023–2024 sabit NFP 30dk alt kuyruk eşiği `-0.99341445%`; CPI `-0.461499928%`, FOMC `-0.384683918%`. 2025 ve 2026 etiketleri eşik ayarlamak için kullanılmadı.
- 2026 verisi **sadece tarihsel yeniden oynatma**. Twelve Data 5m geçmiş fiyatları **8 Eylül 2026'da geriye dönük temin edilmiş**; olayların yayın öncesinde bunlar canlı alınmış olduğuna kanıt yok. NFP/CPI piyasa konsensüsü için de orijinal pre-release güncelleme/sunum zamanı sertifikalı değil.
- Eski V22'nin day-end/CSV skorundan hesaplama saatini çıkarmak yasaktır. Buradaki V22/V31 birleşimi takvim günü düzeyindedir, **gerçek bankadan al-sat performansı hesaplanmadı**. Kullanıcının toplam %1.6 komisyon kuralı uygulanmamış olmasının sebebi bu çalışmanın trade simulation değil, alarm karşılaştırması olmasıdır.
- 27 Şubat 2026 dört-metal kötü fiyatı `AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES` veya `PM_MIXED_CLOSE_REFERENCE_NOT_SAME_SERIES` ile *araştırma amaçlı* ikame edildi; ikisi de aynı fixer benchmark olarak onaylanmadı. Neon eski tabloları, orijinal kodlar ve çalışan modeller **dokunulmadı**.
- Ekim 2026 günleri ve Eylül'ün son 7 günü **skorlanabilir gerçek eşlenmiş 14/21 fiyat/makro paneliyle** doğrulanmadan Eylül sonrası başarı iddiası yapılmamalıdır.

## Buradan çıkarılması gereken geliştirme kararı

**V31 mevcut haliyle günlük büyük-düşüş erken uyarı modelinin doğruluğunu artırmamıştır.** Bilgi katmanı olarak elde tutulabilir, ancak “2026 büyük düşüşleri yakalayan yeni üstün model” diye terfi edilemez. Sorun **mimari özelliği**: V31 yalnız fiyat *düştükten sonra* açıklama sonrası 30 dk tepkiyi ölçer. İlk Haziran zirvesinden önce ekonomik risk sinyali yaratacak **önceden görülebilen haber konsensüsü, yayın öncesi fiyat/kur/faiz/petrol akışı**, özellikle JOLTS/ADP bağlamı olmadan yeni pre-peak kazanç beklemek yanlış. Bunları eklemek yeni kontrol grubu ve as-of kayıtları gerektirir; geriye dönük Haziran'a özel kırmızı eşik ayarlamak bilimsel olmaz.

## Kalıcı kanıtlar

- GitHub workflow **SUCCESS, 8/8 test**: https://github.com/ataullahturgut/sim3-automation/actions/runs/40505428422
- Kod: `risk_v32_2026_full_calendar_joint_replay.py`, test `test_risk_v32_full_2026_joint_replay.py`.
- Commit edilmiş V32 karşılaştırma `outputs/v32_2026_original_vs_new_joint_5session_metrics_COMMITTED.csv`.
- Commit edilmiş V32 beş zirve `outputs/v32_2026_all_five_prepeak_comparison_COMMITTED.csv`.
- Tam çıktılar: workflow artifact `gold-v32-all-Jan-Sep-2026-base14-cftc21-v22-v31` (2026 AM/PM **388 günlük karar satırı**, 23 olay-zamanı, alarm episode kümeleri, parametre/eşik/data manifesti). Artifakt erişimi GitHub Actions indirmeyle; GitHub'da ana branch'e otomatik birleştirme yapılmadı.

**SON HÜKÜM: Araştırma V32 PASS; yeni erken düşüş başarı katkısı = 0; operasyonel canlı hazır = BLOCKED.**
