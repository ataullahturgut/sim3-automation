# V33 — 2026 TAM KAPSAM DENETİMİ (27 Ekim itibarıyla): BASE14 / CFTC21 / V22 / V31

**Tarih:** 27 Ekim 2026. **Rapor statüsü:** En güncel **aynı-kaynak** araştırma fiyatlarına kadar geriye dönük yeniden çalıştırma; **canlı veya ilk-yayın PIT performansı değildir**. Ana model parametreleri ve Neon değiştirilmedi. Çalıştırma ayrıntıları ve çıktı: [GitHub Actions](https://github.com/ataullahturgut/sim3-automation/actions/runs/40515918275), düzeltme sonrası **9/9 test PASS**.

## 1. Önceki araştırmada yanlış kalan kapsamın düzeltilmesi

Eski kod `for i in range(260,len(days)-5)` ve `2026-09-21` bitişi nedeniyle son günlerin **gelecek 5 fiyat seansı bitmeden** hiçbir risk skoru üretmiyordu. V33 ayrı araştırma fonksiyonunda **orijinal 14/21 risk özelliklerini, 200 ağaç IsolationForest modelini, RobustScaler'ı, 0.90 YELLOW ve 0.95 RED eşiklerini, V22 P1–P7 kurallarını değiştirmeden** skor hesabını sonuç olgunluğundan ayırdı. **187/187 eski 2026 risk/karar gününün değeri iki senaryoda da birebir aynı kaldı**.

- 1 Ocak–27 Ekim 2026'da **214 takvim-hafta içi**: StakTrakr'da **211 kaynak fiyat günü**, **211/211 BASE14/CFTC21/V22 skor günü**, diğer 3 hafta içi = **1 Ocak piyasada fiyat kaydı yok**, **26–27 Ekim tek-kaynak fiyat NOT_FOUND**.
- Son aynı kaynak fiyat ve araştırma risk skoru tarihi **23 Ekim 2026**. Son tarihsel **5 seans sonrası** gerçek sonucu tam hesaplanabilir sinyal tarihi **16 Ekim 2026**. 19–23 Ekim sonuçları `UNMATURED`: başarısız diye sayılmaz.
- Ekim 2026 için güncel StakTrakr Oct1–16 verileri Neon `gold_monthly_h1.staktrakr_2026_git_snapshot_daily_v1` sabit commit `02964d...`; Oct19–23 **aynı lbruton/StakTrakr deposunun** `9933d45e4fc185e7cefe8ec56740b3974ec8d4a2` sabit Git commit'inden eklendi. Oct1–16 fiyatları yeni Git sürümüyle **4 metalde birebir** örtüştü. Kaynak sürekli değişebilir; bu iki komit araştırma için donduruldu.
- GVZ, 10 yıllık H.15 ve dolar endeksi H.10 Ekim kaynakları Neon'dan yalnız **SELECT** ile, gerçek `available_as_of` metaverileriyle alındı; Ekim'de erken erişilebilir olmayan H.10/H.15 gözlemleri özellik vektörüne sokulmadı. CFTC dondurulmuş tarihsel GC/SI raporlarıyla sürüm korundu; 20 Ekim CFTC raporunun `available=2026-10-27` etiketi, 23 Ekim için önceden bilinmiş gibi kullanılamaz.
- 27 Şubat 2026 dört metal fiyatını **onaylanmamış iki dış referans senaryosu** (AM/PM) üzerinden hesaplama sürüyor. Aynı fixing seansları kesin eşleşmiş değil; Mart tarihsel erken uyarısı kesin kaynak sertifikası almadı.
- Ekim V31 NFP/CPI/FOMC kayıtları mevcut 108 olay arşivinde **yok**; 2026'nın bilinen olay kaydı **11 Eylül'de** bitiyor. Ekim V31 performansını **0 alarm = doğru** saymak yasak. Bunun yerine `EVENT_SOURCE_ENDS_2026_09_11` ibaresi tüm Ekim günlerinde bulunur.

## 2. Gün gün sonuç — aylık dökümün nasıl okunacağı

Aşağıdaki `X/Y`: X = o ayın **risk/inceleme uyarı günü sayısı**, Y = **uyarı gününden SONRAKİ 5 fiyat seansında fiyat en az %5 düşmüş gün sayısı**. Bu yalnızca **alarm-günü etiketi**; bağımsız ekonomik düşüş olaylarının veya uygulanabilir kârın sayısı değildir.

**AM dört-metal araştırma fiyat senaryosu.** PM senaryosu Ekim'de aynı, toplam V22 için AM'den **1 uyarı günü az**.

| 2026 ayı | Fiyat/skor günü | BASE14 RED uyarı / 5g doğru | CFTC21 RED uyarı / 5g doğru | V22 inceleme / 5g doğru | V31 ilave banka saati uyarısı |
|---|---:|---:|---:|---:|---:|
| Ocak | 21 | **7 / 5** | **6 / 5** | **7 / 5** | 0 |
| Şubat | 20 | 13 / 0 | 9 / 0 | 10 / 0 | 0 |
| Mart | 22 | 11 / 3 | 10 / 2 | 8 / 2 | 0 |
| Nisan | 22 | 4 / 0 | 2 / 0 | 4 / 0 | 0 |
| Mayıs | 21 | 1 / 0 | 0 / 0 | 0 / 0 | 0 |
| Haziran | 22 | 17 / 3 | 13 / 1 | 7 / 2 | 0 yeni (5 Haziran zaten V22 uyarıydı) |
| Temmuz | 23 | 0 / 0 | 0 / 0 | 0 / 0 | 0 |
| Ağustos | 21 | 6 / 2 | 3 / 1 | 7 / 3 | 0 |
| Eylül | 22 | 8 / 0 | 1 / 0 | 1 / 0 | 0 (olay verisi 11 Eyl'de bitti) |
| **Ekim (1–23)** | **17** | **5 / 0*** | **1 / bekliyor** | **1 / bekliyor** | **UNRESOLVED — Ekim olay arşivi yok** |
| **Toplam** | **211** | **72 uyarı** | **45 uyarı** | **45 uyarı** (PM:44) | **bilinen dönem için +0** |

*** Ekim BASE14:** 5 RED'in 4'ünde gelecek 5 fiyat seansı tamamlandı ve %5 düşüş olmadı; **23 Ekim'in RED uyarısının sonucu henüz olgunlaşmadı**. CFTC21'in ve V22'nin Ekim tek RED/aktif uyarısı da **23 Ekim**, yani `UNMATURED`. Bundan ayrıca gerçek zamanlı 23 Ekim bankada görünmüş alarm olduğu sonucu çıkarılamaz.

### Toplamda aynı olgunlaşmış hedefler

| Model | 2026 toplam uyarı günü | Beş seans sonucu olgunlaşan uyarılar | ≥%5 düşüşle örtüşen | Örtüşmeyen | Henüz olgunlaşmayan |
|---|---:|---:|---:|---:|---:|
| BASE14 | 72 | 71 | **13** | **58** | 1 |
| CFTC21 | 45 | 44 | **9** | **35** | 1 |
| V22 (AM) | 45 | 44 | **12** | **32** | 1 |
| V22 (PM) | 44 | 43 | **12** | **31** | 1 |
| V22 + mevcut V31 | V22 ile aynı | V22 ile aynı | V22 ile aynı | V22 ile aynı | 1 |

**Çıkarım:** 2026 Ocak–Eylül ve Ekim erişilebilen günlerde V31 mevcut sürümünün **belgelenmiş yeni büyük-düşüş öncül uyarı başarısı yok**. Ekim için olay arşivi eksik olduğundan, `V31 kesin hiçbir alarm vermedi` ifadesi kullanılamaz.

## 3. 2026 dört bağımsız büyük düşüş ailesi (zirve öncesi)

| Aile | Zirve | Eski V22 ilk zirve öncesi uyarı | V31'in ek kazancı | Uyarı hükmü |
|---|---|---|---|---|
| Ocak | 29 Ocak | 22 Ocak | 0 | V22 erken |
| Mart | 12 Mart | **26 Şubat**, yalnız fiyat ikame senaryosuyla | 0 | koşullu erken |
| **Haziran (ilk bacak)** | **4 Haziran** | **YOK** | **YOK** | **önceden kaçırıldı** |
| Ağustos | 25 Ağustos | 11 Ağustos | 0 | V22 erken |

Haziran ikinci bacak 17 Haziran için 5 Haziran V22 ve V31 olay-sonrası şok tepkisi var, fakat aynı ekonomik düşüş ailesinin parçasıdır, ayrı beşinci doğru olay diye sayılmaz. NFP 5 Haziran **16:05 TR** piyasa hareketinin **sonrası**; 4 Haziran zirvesinden önce bildirim sayılamaz.

## 4. Ekim son beş fiyat günü — kullanıcıya gerekli gerçek sayılar

| 2026 tarihi | Altın araştırma fiyatı, USD/ons | BASE14 | CFTC21 | V22 | Sonraki beş seans gerçekleşmesi |
|---|---:|---|---|---|---|
| 19 Ekim | 4161.04 | NORMAL | NORMAL | uyarı yok | UNMATURED |
| 20 Ekim | 4127.52 | NORMAL | NORMAL | uyarı yok | UNMATURED |
| 21 Ekim | 4126.54 | NORMAL | NORMAL | uyarı yok | UNMATURED |
| 22 Ekim | 4069.97 | YELLOW | YELLOW | uyarı yok | UNMATURED |
| **23 Ekim** | **4011.03** | **RED** | **RED** | **ACTIVE_REVIEW** | **UNMATURED** |
| **26 Ekim** | **NOT_FOUND** | hesaplanamadı | hesaplanamadı | hesaplanamadı | NOT_FOUND |
| **27 Ekim** | **NOT_FOUND / tam gün henüz bitmedi** | hesaplanamadı | hesaplanamadı | hesaplanamadı | NOT_FOUND |

Bu referans, StakTrakr farklı gün tanımı / UTC 12:00 tarihli günlük kaynak fiyatıdır, bankanın 16:45'te kesin görülen spot alış/satış fiyatı değildir. `2026-10-23 RED` geriye dönük modellerce üretilmiş bir **araştırma puanıdır** ve 23 Ekim tarihinde canlı işlem öncesi hazır olduğuna delil değildir.

## 5. Hangi model daha iyi?

**Şu anda kazanan ilan etmeyin.** BASE14 daha çok RED veriyor; 2026'da **71 değerlendirilebilir RED gününden yalnız 13'ünü** takip eden beş fiyat seansında %5 düşüş izledi. CFTC21 44 günden 9, V22 44 günden 12 (AM). Ancak bunlar birbirinden bağımsız 71 olay değil, üst üste gelen uyarı günleri, kötü kesin fiyatla ikame olan Şubat, ve takvimde geriye dönük veriler var. Prospektif ve same-price-definition PIT belge olmadığı için bunlardan ticaret kârlılığı, satış kararı veya gerçek canlı başarı çıkarılamaz.

V31, birinci Haziran büyük düşüşünü **öngöremedi**. Önceden yayımlanan olay takviminden yeni bir `SAT` sinyali türetmek için 2025 doğrulamasında fazladan katkı, diğer 2023–2026 anons günlerinde yanlış alarm kontrolü, tarihli ilk konsensüs sürümü ve olay sonrası DXY/faiz/petrol kaynakları gerekecek.

## 6. Kanıt / çıktılar

- Gerçek araştırma kodu: `risk_v33_2026_full_asof_oct27_replay.py`; tarih kaynak denetimi: `risk_v33_price_macro_cftc_coverage_audit.py`; bağımsız kapı testleri `test_risk_v33_full2026.py`.
- **Tüm günler** (iki senaryo × 214 hafta içi = **428 satır**): `outputs/v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv`.
- **10 ay** (2 senaryo × 10 ay × 4 aile = **80 satır**): `outputs/v33_2026_jan_oct27_MONTHLY_all_models_and_outcomes.csv`.
- Model karşılaştırması (8 satır): `outputs/v33_2026_jan_oct27_SUMMARY_all_models.csv`.
- `outputs/v33_full_2026_asof_audit_manifest.json` denetim SHA'ları / parite / 26-27 Ekim kaynak boşluğu.
- Son kaynak eşleşmesi: `outputs/v33_staktrakr_4metals_2026_10_19_to_10_23_FIXED_COMMIT.csv`; 2026 Oct1–16 araştırma fiyatlarından 4 metalde eski ve yeni kaynağın birebir uyumu.
- Ekim H.10/H.15/GVZ: `outputs/v33_oct2026_gvz_h15_h10_release_aware_neon_select.csv`, ilk retrieval saatleri.
- **En son düzeltilmiş V33 CI**: https://github.com/ataullahturgut/sim3-automation/actions/runs/40515918275 **SUCCESS, 9/9 test PASS**.

**Güvenlik ve veri kararı:** Ana model (BASE14, CFTC21, V22) eski parametre ve eşiklerle korunur. Neon/üretim hiç değiştirilmedi. 27 Şubat aynı fiyat sözleşmesinde onaylanmış gerçek fiyat, 26–27 Ekim dört metal fiyatları, Ekim makro takvimi/konsensüs ilk yayın arşivi olmadan **tam kaynak sağlıklı 2026'ya kadar performans sertifikası verilemez**. Bu sınırlar dosyalarda `NOT_FOUND` ve `UNMATURED` olarak gösterilir.
