# GOLD-ADAPTIVE-MODEL-APP-01 — S2 ilk fiyat-hareketi yaşam döngüsü araştırma denetimi
**Tarih:** 16 Ekim 2026 · **WORKSTREAM=MODEL** · **DEV_GATE=S2_STARTED / CODE_WORKING** · **S2_SCIENCE_GATE=PENDING** · **S1_SCIENCE_GATE=FAIL** · **AL–SAT=NOT_IMPLEMENTED**

## Bağlayıcı karar
Kullanıcı, ekonomik olay kural öğreniminin (S1) bilimsel kabulünü beklemeden **S2 geliştirmesi** için manifest istisnasını onayladı. Mevcut S1 CORE ve projeyi değiştirmeden S2 yaşam döngüsü ona **bağlı bir bileşen** olarak başlatıldı; S1 hâlâ güvenilir ekonomik alpha kanıtı olmadan kalıyor. S3 AL–TUT–SAT veya uygulama geliştirmesi bu izinle onaylanmadı.

## 1. Gerçekleştirilen mekanizma
- [adaptive_phase_lifecycle_s2.js](adaptive_phase_lifecycle_s2.js): as-of tamamlanmış M15 fiyatlarından, geçmiş 16 barlık 4s hareketin gerçekleşmiş oynaklığa oranı ile iki yönlü **START, CONTINUE, PULLBACK, END, REENTRY** ve NEUTRAL/WARMUP durumlarını kronolojik işaretler. İlk yapısal eşikler **mühendislik hipotezi** (entry 1,25 z; exit 2 bar x z≤0,20; pullback 0,70 volatilite oranı); bu durum adları altın hakkında ekonomik neden-sonuç tahmini veya keşfedilmiş S1 kuralı değildir.
- Sağ sansür: hafta sonu/eksik M15 **veya kaynak kimliği değişimi** olduğunda hareket zorla tamamlanmış sayılmaz; sonu bilinmeyen hareket sağ-sansürlü kaydedilir ve olgunlaşmamış 4s tahmini puanlanmaz. Eski sonuçlar kayıp aralık üzerinden fiyat birleştirilerek üretilmez.
- **Gerçek öğrenim:** yalnızca daha önce tamamlanmış bağımsız epizotların *sürelerinden* durum/istikamet koşullu **önümüzdeki 4s içinde bitiş hazard** oranını öğrenir; şartlı destek yetersizse çekimser kalır. Karşılaştırma: aynı tarihte bilinen, durum/istikamet koşulsuz genel süre dağılımı. Her tahmin karar anında kaydedilip hedef saati geldiğinde olgunlaşır. Kayıt aralığı 4 saat; aynı hareketten gelen birden çok tahmin bağımsızmış gibi istatistiklendirilmez; epizot-küme bootstrap uygulanır.
- [adaptive_market_core_s1_s2.js](adaptive_market_core_s1_s2.js): **mevcut S1 adaptif kural motoruyla tek bileşik model**; S2 as-of evre/yaş/yön/drawdown özelliklerini S1'in piyasa bilgi şemasına bağlar. Ekonomik S1 araştırma ledger'ını kendiliğinden taşımıyor; 0 alım/satım.
- [replay_phase_lifecycle_s2.js](replay_phase_lifecycle_s2.js): özel Neon XAU M15 satırlarıyla salt-okunur yeniden çalışma; yalnız aggregate sonuçları çıktı verir, ham fiyat/özel checkpoint GitHub'a yazılmaz.

## 2. Gerçek veri — 2023 Ocak ve 2023–2025
**Veri:** `gold_research_histdata_xau15m_candidate`, geçmişte yeniden kurulmuş tamamlanmış M15 fiyatları; tarihsel orijinli **gerçek ilk canlı provider-vintage doğrulanmış değil**. 2023–24 ve 2025 **iki farklı kaynak kimliği**, geçişte sağ-sansür uygulandı. Tam 15 native minute bar şartı vardır, imputation yok.

| Metrik | Ocak 2023 | Ocak 2023–Aralık 2025 |
|---|---:|---:|
| Kaynak satırı | 1.908 | 67.919 |
| Geçerli tamamlanmış M15 | 1.903 | 67.653 |
| Eksik/reddedilen M15 | 5 | 266 |
| Tamamlanmış epizot | 39 | 1.223 |
| Sağ-sansürlü epizot | 11 | 341 |
| Epizot medyan süresi | 3,5s | 3,75s |
| Değerlendirilen 4s bitiş tahmini | 15 | 1.596 |
| Brier: S2 koşullu hazard | 0,252976 | **0,241926** |
| Brier: basit geçmiş süre dağılımı | 0,252981 | **0,243622** |

S2 2023: **324** tahmin, Brier **0,259078** vs süre baz çizgisi **0,259657**.
2024: **634** tahmin, **0,232904** vs **0,235876**.
2025: **638** tahmin, **0,242182** vs **0,243175**.

Toplam açıklayıcı Brier iyileşmesi **+0,0016955** (pozitif S2 lehine); **1.205 epizot kümesiyle 1.000-bootstrap %95 [−0,000320; +0,003733]**; sıfır içerir. İlerleme **küçük ve kanıtlanmamış**. 1.596 dört-saatlik tahmin tümüyle bağımsız episode sayısı değildir. 2023–25 retrospektif analizinden elde edilen bulgular gerçekten yeni ve kör out-of-sample veri değildir. Yaşam döngüsü evre etiketlerinin doğruluğu için bağımsız ground truth yok; hazard kalibrasyonu ve çoklu ufuk (4s–2 hafta) henüz kabul koşullarını sağlamadı.

**Entegrasyon doğrulaması (gerçek Ocak 2023):** Tek bağlı S1+S2 aynı 1.903 M15 barını sırayla okudu; S1 kural motorunda **101 anchor**, **94 olgun 4s sonuç** ve **2 kural prototipi** oluştu. Bu yalnız birlikte işleyebildiklerini gösterir, finansal strateji başarısını veya S1 ekonomik alpha'yı göstermez.

## 3. Teknik denetim ve sıradaki açık bilim kapısı
- 9 yeni S2 modül/bileşik CORE testi: veri saati, geleceği reddetme, tamamlanan/sansürlenen episode ayrımı, checkpoint eşitliği, iki kaynak geçişi, araştırma/STRICT kaynağı ayırımı ve hiç al-sat yetkisi olmaması. Daha önceki 46 S1 testiyle **55/55 izole JS test PASS**. GitHub Actions workflow'a S2 adımı eklendi, CI sonucu bağımsız doğrulanmadı.
- **Geliştirme izni** başarılı: S2_DEV=IMPLEMENTED_FIRST_SLICE; 2023–25 replay yürütüldü. **S2_SCIENCE_GATE=PENDING**; 4s bitiş hazard'ın baseline'dan güçlü üstünlüğü kanıtlanmadı, 4s–2 hafta çapraz ufuk ve tam epizot/overlap validasyonu yok; şimdilik fiyat-only. S1_SCIENCE_GATE=FAIL korunur.
- **Sonraki en etkili S2 işi:** tarafsız ve kronolojik epizot etiket denetimi, 4s–2hafta süre/yeniden giriş koşullarını açma ve kaynak noktası doğruluğu; bundan sonra S2'nin S3'e bağımsız katkısı ablation ile ölçülecek. Bu ara deneyin eşikleri 2023–25 sonuçlarına bakılarak oynanmayacak.

**MODEL_GATE=FAIL | S2_DEV=STARTED_AND_CODE_WORKING | S2_ACCEPTANCE=PENDING | S3/S4/S5/S6/U1=BLOCKED_FOR_ACCEPTANCE | 0 TRADES.**
