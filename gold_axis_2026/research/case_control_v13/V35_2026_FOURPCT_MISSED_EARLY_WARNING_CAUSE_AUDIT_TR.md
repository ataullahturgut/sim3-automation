# 2026 | %4+ düşüşlerde V22 öncelik filtresi neden bazı olayları kaçırdı? — Kayıt denetimi

**Denetim:** 2026-10-30. **Kapsam:** 2026-01-02…2026-10-23, StakTrakr araştırma fiyatı ve V33 AM/PM şüpheli 27 Şubat senaryoları. **Statü: RESEARCH_NOT_PIT; canlı alarm değil.**

## Sabit tanım ve veri kaynağı

- **Düşüş etiketi:** Bir fiyat gününden *sonraki beş TAM fiyat işlem günü* içindeki minimum fiyatın o başlangıç gününe göre **en az %4 düşük** olması. Çakışan düşüş pencereleri birleştirilebilir; bu *bağımsız ekonomik olay* sayısı değildir.
- **Erken uyarı:** ilgili %4/5-gün penceresinin **başlangıç gününden önceki** son on fiyat işlem günündeki uyarı. Düşüş başladıktan sonra gelen kırmızı/ACTIVE bu olayı önceden yakalamış sayılmaz.
- **BASE14 RED** ile V22 `ACTIVE_REVIEW` aynı şey değildir. V22 `ORIGINAL_RED_REVIEW_ONLY` orijinal kırmızının saklandığını, fakat V22 tarafından yüksek önceliğe yükseltilmediğini ifade eder.
- Kaynaklar: `outputs/v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv`; `outputs/v22_daily_decisions.csv`; `risk_v22_slope_decision.py`; `V32_2026_JAN_SEP_FULL_DAILY_LEGACY_PLUS_MACRO_EVALUATION_TR.md`.
- AM ve PM *fiyat-tanımı sertifikalı olmayan* senaryolarda aşağıda incelenen üç olayın dönem içi alarm tarihleri ve seviyeleri arasında **uyuşmazlık çıkmadı**. Bu, verinin PIT/onaylı olduğu anlamına gelmez.

## Olay bazlı bulgular (ilk 10 işlem günü penceresi)

| Olay | Beş fiyat günü fiyat hareketi | Önceki 10 işlem gününde BASE14 | CFTC21 | V22 öncelik | Gerçek durum |
|---|---|---|---|---|---|
| **Mayıs** | 13 Mayıs 4.696,97 → 20 Mayıs 4.503,79: **-%4,1129** | 29 Nisan, 4 ve 5 Mayıs **YELLOW**; RED yok | RED/YELLOW yok | Yok | 18–19 Mayıs BASE14 YELLOW; **20 Mayıs RED**, fakat fiyat zaten %4,11 gerilemiş |
| **Haziran I** | 4 Haziran 4.474,68 → 11 Haziran 4.113,23: **-%8,0777** | 21, 22 ve 28 Mayıs **YELLOW**; RED yok | RED/YELLOW yok | Yok | **5 Haziran BASE14 RED + V22 ACTIVE**; 4 Haziran zirvesinden *sonra* |
| **Eylül** | 21 Eylül 4.353,82 → 28 Eylül 4.158,45: **-%4,4873** | **11, 14, 15, 17 Eylül RED**; 9,10,16,18 Eylül YELLOW | **11,14,15 Eylül YELLOW**, RED yok | Yok | Öncesinde **orijinal RED vardı**, V22 `ORIGINAL_RED_REVIEW_ONLY` olarak sakladı; 28 Eylül V22 ACTIVE, ancak hareket sonrası |

### Mayıs — sorun uyarının kuvveti ve yapısı

- 29 Nisan, 4–5 Mayıs BASE14 YELLOW, ancak bu günlerde `previous_BI_strong=False`. V22 P6 *YELLOW ve güçlü BI* birlikte istediği için `CONTINUATION_REVIEW` üretmedi.
- 13 Mayıs düşüş penceresi başlangıcı: BASE14/CFTC21 **NORMAL**, V22 `NO_ACTIONABLE_REVIEW`.
- 18 ve 19 Mayıs BASE14 YELLOW, ama fiyat zaten düşüyor; V22'daki güçlü BI koşulu hâlâ sağlanmıyor.
- **20 Mayıs:** BASE14 **RED**, CFTC21 **YELLOW**, V22 `ORIGINAL_RED_REVIEW_ONLY`. Orijinal modelin RED'i silinmedi; `previous_BI_strong=False`, 5-gün momentum **-%4,20**, momentum ivmesi **-4,67 puan**, GVZ **25,17**, RSI **0,387**. P1–P5 koşulları sağlanmadı.
- **17 Nisan:** V22 `FRAGILITY_WATCH` bulunuyor, fakat 13 Mayıs başlangıcından **18 fiyat işlem günü önce**, takip eden süreçte sürekliliği yok; bu çalışma için **10 günlük öncü başarı sayılmamalıdır**.

### Haziran — uyarı düşüş başladıktan sonra geldi

- 21–22 Mayıs ve 28 Mayıs BASE14 **YELLOW**, BI güçlü değil; CFTC21 NORMAL. **20 Mayıs BASE14 RED** vardır ama 4 Haziran başlangıcından **11 fiyat işlem günü önce** ve ardından RED devam etmiyor; son 10 işlem günü kriterinin dışındadır.
- 4 Haziran fiyatı 4.474,68; BASE14 NORMAL, CFTC21 NORMAL, V22 `NO_ACTIONABLE_REVIEW`. O gün GVZ **23,87**, RSI **0,402**; RED çekirdeği yok.
- **5 Haziran** fiyatı 4.403,77 (bir günde **-%1,5847**); BASE14 **RED**, CFTC21 YELLOW ve V22 `ACTIVE_REVIEW`. V22 nedeni **GVZ_SHOCK**: güçlü RED + bir-günlük fiyat düşüşü ≤-%1,5 + GVZ neden etiketi. Bu olay **erken uyarı değil, başlayan düşüşün tespiti**.
- 8 Haziran CFTC21 RED olsa da V22 yalnız `ORIGINAL_RED_REVIEW_ONLY`. 9–10 Haziran V22 `CFTC_CONFIRM` ile ACTIVE; yine ilk düşüş başladıktan sonra.

### Eylül — asıl filtreleme hatası / amaç farkı

- **11, 14 ve 15 Eylül** BASE14 **RED**. CFTC21 YELLOW. V22 `ORIGINAL_RED_REVIEW_ONLY`; `previous_BI_strong=False`, dolayısıyla P1–P4 güçlü-kırmızı çekirdeği geçmez.
- **17 Eylül** BASE14 RED, orijinal neden `GVZ_ANOMALY`, bu kez `previous_BI_strong=True` ama V22'nin **hiçbir P1–P5 koşulu karşılanmadı**:
  - P1 için 5-günlük yükseliş ivmesi **>%1 puan** gerekli; gözlenen **+0,6625 puan**.
  - P2 için `CFTC_CONFIRMED_RISK_ACCELERATION` nedeni gerekli; yok.
  - P3 için günlük fiyat hareketi **≤-%1,5** + GVZ nedeni gerekli; gözlenen **+%0,3151**.
  - P4 için **GVZ≥35** ve **RSI≥0,55** gerekli; gözlenen GVZ **24,98**, RSI **0,287**.
  - P5 için önceki RED çekirdek sürekliliği ve pozitif 5-günlük momentum gerekli; yok.
  - P6 güçlü YELLOW'a, P7 BASE14 NORMAL kırılganlık durumuna mahsus; kırmızı gününe uygun değil.
- Bu nedenle **BASE14 erken tehlike işaretini üretti, V22 yüksek öncelikli kabul etmedi**. 17 Eylül orijinal kırmızı, 21 Eylül %4/5-gün penceresi başlangıcından **2 fiyat işlem günü önce**. İlk RED 11 Eylül'de, **6 işlem günü önce**.
- **28 Eylül** BASE14 RED + CFTC21 RED + V22 ACTIVE görüldü; o noktada 21 Eylül'e göre altın **-%4,49**. Öncesini yakalama sayılamaz.

## 2026 %4/5-gün günlük sonuç ölçütü: öncelik–kapsama dengesi

**Tek senaryo: AM; geçmişe bakılarak belirlenmiş 2026, kör test değildir.** Olgunlaşmış **206** işlem fiyat günü var; bu günlerin **32'si**, sonraki 5 işlem gününde ≥%4 düşüş etiketi taşıyor. Bu **32 bağımsız kriz** anlamına gelmez.

| Algoritmik uyarı katmanı | Uyarı günü | ≥%4 ile eşleşen uyarı günü | Eşleşmeyen uyarı günü | 32 etiketli günün kapsaması |
|---|---:|---:|---:|---:|
| V22 öncelikli (ACTIVE/CONTINUATION/WATCH) | **44** | **14** | **30** | **%43,75** |
| BASE14 RED | **71** | **19** | **52** | **%59,375** |
| BASE14 RED veya YELLOW | **124** | **25** | **99** | **%78,125** |
| CFTC21 RED | **44** | **14** | **30** | **%43,75** |

PM fiyat senaryosunda V22 öncelikli **43/14/29**; BASE14 RED **71/19/52**. %4/5-gün verisinde daha geniş uyarı kademesi kapsama artırırken **çok daha fazla sonuçsuz uyarı** verir. Bu oranlar aynı olayın birden çok gününden oluşur: **bağımsız ekonomik düşüş başarı oranı değildir**. Gelecek fiyatı yalnız sonradan skorlamak için kullanıldı.

## Teknik karar

1. **Orijinal BASE14 RED'i koru ve UI'da V22 önceliğinden ayrı göster.** Eylül'e ilişkin önceki "**V22 yakalayamadı, uyarı yok**" ifadesi yanıltıcı: yalnız *V22 öncelikli incelemesi* yok; BASE14 RED mevcut. Veri ve model kodu değiştirilmedi.
2. **Erken risk / aktif teyit / düşüş başladı** kademelerini ayrı tut. Mayıs/Haziran'da YELLOW, Haziran 5'te gecikmiş GVZ_SHOCK ve Eylül'de önceliklenmeyen RED bunu gerektiriyor.
3. V22 P1–P7'nin başlangıç tasarımı **momentum artışı, GVZ şoku ve CFTC teyidi** üzerine odaklı. **Aşağı yönlü ivmelenmenin başlangıcında**, BI strong=False veya fiyat-zirve/şok koşulları yokken bazı düşüşleri öne çıkarmaz.
4. Şimdi Eylül 2026'yı kurtarmak için P1 eşiğini 1'den 0,66'ya indirmek veya genel BASE14 RED'i otomatik V22 ACTIVE yapmak **yasaklanmalıdır**: 2026 sonucu görülmüştür; 52 sonuçsuz BASE14 RED günü nedeniyle aşırı uyum / yanlış alarm riski vardır. Olası değişiklik ancak 2024–2025 kronolojik geliştirme + dokunulmamış, PIT doğrulanmış ileri testle değerlendirilmelidir.
5. **Hedef:** İleri 5 işlem gününde ≥%4 düşüş. 10 işlem günü önceki uyarı penceresi ayrı analitik ölçümdür; fiyat ilk %4'e ulaştıktan sonraki sinyaller erken uyarı olarak sayılmaz.

**Bilimsel sınır:** Şubat 27 dört-metal düzeltmesi onaysız; veri kaynağının ilk yayımlanma zamanı ve canlı sinyal saati tam sertifikalı değil. Bu belge yeni bir algoritma, al-sat optimizasyonu, banka emri veya başarı sertifikası üretmez.
