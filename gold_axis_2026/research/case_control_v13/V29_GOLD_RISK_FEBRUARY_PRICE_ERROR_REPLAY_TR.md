# V29 — Şubat 2026 dört metal fiyat hatası sonrası büyük düşüş alarmı tekrar çalıştırması

**Tarih:** 27 Ekim 2026. **Durum:** İki alternatif, fiyat-tanımı onaylanmamış araştırma duyarlılık senaryosu. **Canlı alarm veya kesin temiz fiyat yeniden çalıştırması değildir.** Ana üretim, Neon, V25 fiyat karantinası ve orijinal BASE14/CFTC21/V22 parametreleri değişmedi.

## Ne yapıldı?

1. Donmuş kaynak paketi ve CFTC resmî yayın-lag düzeltmesi kullanıldı. Orijinal `gold_risk_cftc_v8_fixed.py` modeli (RobustScaler + IsolationForest 200 ağaç, random_state 1701, eğitim-skorlarından q90 YELLOW/q95 RED, 14 ve 21 parametre) çalıştırıldı.
2. **Değişmeyen 2025–2026 skorlarının 1.572/1.572 tanesi** yeniden birebir üretildi (orijinal kaynakta 4 model ailesi × 393 tarihli skor). 2026 BASE14/CFTC21 dâhil önceki 161 tarihli V22 kararının **161/161 tanesi** aynı üretildi. Herhangi bir orijinal RED kaldırılmadı.
3. 27 Şubat 2026 **tek** bozuk günde, diğer 2010–2026 veri noktalarını değiştirmeden iki **resmî kaynakla fiyat tanımı eşitliği kanıtlanmamış** alternatif dört-metal vektör sınandı:
   - `AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES`: XAU **5174.10** (LBMA AM), XAG **89.975**, XPT **2365.00** (platin AM), XPD **1818.00** (paladyum AM).
   - `PM_MIXED_CLOSE_REFERENCE_NOT_SAME_SERIES`: XAU **5222.30** (LBMA PM / dış kapanış), XAG **89.975**, XPT **2366.00**, XPD **1793.00**.
   - **Kritik:** XAG/XPT/XPD değerleri aynı session/fixing tanımında olmayabilir. Bu vektörlerden hiçbiri doğrulanmış StakTrakr orijinal seansı diye kabul edilmedi. AM ve PM etiketleri altın fiyatının referansını tanımlar; tüm metallerin ortak seans onayı değildir.
4. Orijinal risk çekirdeğindeki kod korundu. Fiyatı ikame eden hesaplama için, yalnız CI araştırma sürecinde `BAD_DAY` çekilme kontrolü `try/finally` ile geçici devre dışı bırakıldı; kod diskte/Neon'da/üretimde değişmedi. Başka günler için **tüm fiyatlar ve 21 model özelliği aynı**.
5. V15 anomali grubu medyan karşılaştırması, V16 2010–22 ön-vaka benzerliği, V18 üç açıklama yolu ve bitişik YELLOW hafızası, V21 mevcut WATCH, V22'nin **orijinal yedi P1–P7 karar dalı** aynı özellikler/parametrelerle çalıştırıldı. Tüm geçmiş kararları mekanik olarak V22 içine kopyalamakla yetinilmedi.
6. Her iki fiyat senaryosunda eski karantinadan kaynaklanan **26 ek 2026 oturumu** skorlanabilir hale geldi (20 Şubat–27 Mart 2026 civarı, gün bazında CSV). 12 Mart zirvesinden önceki 10 fiyat oturumunun **10/10'unda** araştırma skoru hesaplanabildi. Eski, sert karantina sürümünde bu 10 günün hiçbirinde karar yoktu.

## Mart 2026 — en önemli bulgu

Gerçek tarihsel altın fiyat zirvesi **12 Mart 2026**, dip **23 Mart 2026** (V24 mevcut olay defteri yaklaşık **-%15**).

| Model | AM fiyat senaryosunda ilk zirve öncesi alarm | PM fiyat senaryosunda | Orijinal karantinalı model |
|---|---|---|---|
| BASE14 original RED | **26 Şubat 2026** | **26 Şubat 2026** | Karar yok |
| CFTC21 original RED | **2 Mart 2026** | **2 Mart 2026** | Karar yok |
| V22 risk incelemesi (RED + YELLOW/WATCH haritalaması) | **26 Şubat 2026** | **26 Şubat 2026** | Karar yok |

**Yorum:** Model, şüpheli fiyat günü ekonomik açıdan makul referans senaryosuyla değiştirildiğinde Mart düşüşünden **önce** risk belirtisi gösteriyor. Bu başarı *sertifikalı, prospektif, tek-seans fiyat verisiyle doğrulanmadı*. İşlem açma/kapatma optimizasyonu yapılmadı. İlk sinyalden sonra altın zirveye kadar yükselmeye devam etti; bu sinyal hemen satış gereği anlamına gelmez.

### Şubat sonu–Mart ilk yarısı, iki senaryoda

- 23–25 Şubat: BASE14 **RED**, CFTC21 **RED**, V22 **ACTIVE_REVIEW**.
- 26 Şubat: BASE14 **RED**, CFTC21 **YELLOW**, V22 **ACTIVE_REVIEW**.
- 27 Şubat: AM’de BASE14 **YELLOW**, CFTC21 **NORMAL**, V22 **CONTINUATION_REVIEW**; PM’de BASE14 **YELLOW**, CFTC21 **YELLOW**, V22 **NO_ACTIONABLE_REVIEW**. Dolayısıyla **27 Şubat tek gün kararı fiyat-seansı seçimine duyarlı**.
- 2 Mart: İki senaryoda BASE14/CFTC21 **RED**, ancak V22 seviyesi `ORIGINAL_RED_REVIEW_ONLY` (asıl RED korunuyor, öncelik filtresi dışında).
- 3 Mart: BASE14 **YELLOW**, V22 bir günlük `CONTINUATION_REVIEW`.
- 10–12 Mart: BASE14 ve CFTC21 `NORMAL`, V22 yeni inceleme yok. Dolayısıyla erken WATCH'ın düşüş zamanlaması kesin yakınlığı kanıtlanmıyor.

## Yıllık sinyal hacmi ve 10-oturum etiketleri

2026'nın orijinal karantinalı 161 karar günüyle, alternatif fiyat ortamında 187 karar gününü **doğrudan aynı örneklemle oran olarak karşılaştırmamak gerekir**.

| Senaryo | Risk katmanı | Skorlu gün | Toplam uyarı/inceleme günü | Kurtarılan 26 gündeki uyarı | Sonraki 10 tam oturumda ≥%5 düşüş | Sonraki 10 tam oturumda yok |
|---|---|---:|---:|---:|---:|---:|
| AM | BASE14 orijinal RED | 187 | **63** | 13 | 18 | 45 |
| AM | CFTC21 orijinal RED | 187 | **43** | 11 | 13 | 30 |
| AM | V22 öncelikli inceleme (RED sayılmaz) | 187 | **43** | 11 | 15 | 28 |
| PM | BASE14 orijinal RED | 187 | **63** | 13 | 18 | 45 |
| PM | CFTC21 orijinal RED | 187 | **43** | 11 | 13 | 30 |
| PM | V22 öncelikli inceleme (RED sayılmaz) | 187 | **42** | 10 | 15 | 27 |

**Sonraki 10 tam fiyat oturumu** ölçütü yalnız sonuç skorlamasıdır; model tahmin girdisi değildir. “Yok” hücresi uyarı **günü** sayısıdır, bağımsız ve yanlış ekonomik alarm olaylarının sayısı değildir. Çok erken olan ama daha sonra düşüşle örtüşen uyarı, 10 oturum ölçütünde “false” olabilir. Bu nedenle **olay bazlı zirve öncesi başarı** aşağıda ayrıca gösterilir.

## Önceden seçilmiş yedi ekonomik düşüş ailesi

| Aile | İlk gerçek zirve | Son 10 fiyat oturumunda ilk V22 uyarısı | Hüküm |
|---|---|---|---|
| 2024 Kasım | 30.10.2024 | Yok, zirve günü WATCH var | Kaçırıldı |
| 2025 Nisan–Mayıs | 22.04.2025 | 04.04.2025 | Erken |
| 2025 Ekim | 17.10.2025 | 10.10.2025 | Erken |
| 2026 Ocak | 29.01.2026 | 22.01.2026 | Erken |
| **2026 Mart** | **12.03.2026** | **26.02.2026 (yalnız ikame fiyat duyarlılığı)** | **Koşullu erken; tam onay YOK** |
| 2026 Haziran (ilk düşüş) | 04.06.2026 | Yok | Kaçırıldı |
| 2026 Ağustos | 25.08.2026 | 11.08.2026 | Erken |

2025 Nisan/Mayıs ve 2026 Haziranın birden fazla bacağı **tek ekonomik aile** sayılır. V24'teki 7 ailenin **4 erken + 2 kaçırılmış + 1 skorlanamaz** durumu, bu **varsayımsal** senaryoda **5 koşullu erken + 2 kaçırılmış** oluyor. Bu 5/7 bir ileriye dönük başarı tahmini veya onaylı model başarısı **değildir**.

## Kanıt ve fail-closed statü

- **CI başarı:** https://github.com/ataullahturgut/sim3-automation/actions/runs/40486482498 — orijinal model gerçek kodu çalıştı; **7/7 araştırma denetimi geçti**.
- Orijinal/hypotetik skor CSV (tam): GitHub Actions artifact `gold-v29-BASE14-CFTC21-V22-original-replay`.
- Kalıcı teyit edilmiş özet: `outputs/v29_2026_original_models_scenario_COMMITTED.csv`.
- Kalıcı Şubat/Mart kararı: `outputs/v29_feb_mar_restored_original_signals_COMMITTED.csv`.
- Yedi ekonomik aile listesi: `outputs/v29_seven_economic_families_sensitivity_COMMITTED.csv`.
- Araştırma kodu: `risk_v29_fourmetal_price_replay.py`, bağımsız fail-closed test: `test_risk_v29_fourmetal_price_replay.py`.
- **Fiyat düzeltmesi Neon'a uygulanmadı, karantina kaldırılmadı**. Resmî as-of fiyat tip/saat ve sayısal GVZ/CFTC/H10/H15 vintage PIT tam kontrolü henüz yok; orijinal model ya da üretim ekranında Mart için geriye dönük alarmlar açılmamalıdır.

**Operasyonel hüküm:** Mart 2026 önceki boşluğu ham fiyat hatasına bağlıdır; alternatif referanslar modelin zirve öncesinde anormallik uyarısı verebildiğini gösteriyor. Ancak **fiyat sağlığı sertifikası / gerçek operasyonel yeniden yayın** için aynı seans standartlı dört-metal veri düzeltmesi ve fonksiyon bazlı yeni test gerekiyor. Üretim alarm yetkisi verilmedi.
