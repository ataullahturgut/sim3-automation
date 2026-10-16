# S1 — Ekonomik kural keşfi, bağımsız vaka ve negatif kontrol denetimi
**Proje:** GOLD-ADAPTIVE-MODEL-APP-01 | **WORKSTREAM=MODEL** | **CURRENT_STAGE=S1** | **16 Ekim 2026** | **MODEL_GATE=FAIL**

## Değişmeyen sözleşme
Bu, aynı matematiksel adaptif modelin S1 aşamasındaki **araştırma/kanıt testidir**; yeni ana algoritma, yeni branch, S2 veya UYGULAMA değildir. OLAY-02/ÖĞREN-03 ve eski makro ledger salt-okunur bilgi kaynağıdır. Öğrenme ve bağımsız karşılaştırma, geleceği bilmeyen Ocak 2023 ticaret koşusu sayılmamalıdır. **DISCOVERY_FULL_ARCHIVE**; gerçek ilk erişim ve konsensüs kaydı bağımsız doğrulanmadığı için **STRICT_WALK_FORWARD** değildir. 2023–2025 sonuçları, 2026'da arşivden geriye kurulan araştırmadır.

## Gerçek veri sözleşmesi ve kapsam
- Makro ledger: GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv; NFP/AHE/UNEMP ortak yayımdaki **tek bağımsız istihdam açıklamasıdır**; CPI ayrı yayım. 155 satırın içinden 139 pair-complete makro bileşen, 69 yayın dalgası; diğerleri (ör. timestamp-only FOMC) sürpriz eğitimine sokulmaz.
- Neon: gold_research_histdata_xau15m_candidate tablosu, 2023–2025, XAU M15. 2023 20.600 bar (20.436 tam M15), 2024 23.713 (23.657 tam), 2025 23.606 (23.560 tam).
- Açıklama saatinden **en az 60 dk sonra** tamamlanmış fiyat çıpası ve sonraki **tam 16×M15 = 4 saat** ile önceki **4×M15 = 1 saat** kesintisiz veri gerekir. Haber sonrası ilk 60 dakikalık fiyat tepkisi tahminin başlangıcı değildir; sonuç daha sonraki devam/düzeltme bölümüne ilişkindir.
- **69 yayımdan 57'si** tamamlanmış fiyat koşulunu karşılıyor: 29 istihdam + 28 CPI; **12 olay** kaynak kapsaması nedeniyle dışarıda, uydurulan fiyat veya olay yok.
- Kontroller, olaydan 24 saat önce/sonra başka yayın bulunmayan, **aynı UTC saat ve dakika**, olay anı için önceki 1 saatlik XAU hareketine en yakın **dört** fiyat çıpası. Sadece **önceden ölçülen** değişkenle eşleştirildi; sonraki fiyat işaretine göre eşleştirme yapılmadı. **228 kontrol ataması 178 ayrı çıpaya dayanıyor; 50 tekrar atama var**; kontroller birbirinden tamamen bağımsız değildir.
- Teknik kaynak sınırı: BLS 6 ve 12 Ocak ilk açıklamaları ayrıca denetlendi; 2023–2025 bütün ledger'ın ilk baskı/ilk erişim/ön-yayın konsensüs PIT sertifikası **yok**. Bu nedenle bu çalışmanın hiçbir sonucu gerçek canlı alpha onayı sayılamaz. CME continuous future ve XAG/FX/rates ek koşullu PIT verileri burada kullanılmadı.

## 57 bağımsız olayın geçmişteki karakteri
| Ekonomik aile | Fiyatı ölçülebilen bağımsız vaka | Sonraki 4 saat UP | DOWN/UP dışı | Ortalama XAU log-% | Aynı saat/ön durum kontrolleri log-% | Olay−kontrol farkı |
|---|---:|---:|---:|---:|---:|---:|
| İstihdam (NFP + AHE + UNEMP) | 29 | 12 | 17 | -%0,0482 | -%0,0727 | +0,0245 yüzde puanı |
| Enflasyon (CPI) | 28 | 16 | 12 | +%0,1458 | +%0,0026 | +0,1432 yüzde puanı |

29 istihdam olayının **28'inde**, 28 CPI olayının **27'sinde**, karşıt UP/DOWN işareti taşıyan en az bir olaysız kontrol vardı. Bu, ekonomik yayın türünün sonraki altın yönünü **tek başına belirleyemediğini** gösterir. Ayrıca CPI'nin pozitif ortalama olay-kontrol farkı bile, kaydedilmiş aynı-saat kontrollerinin bağımlılığı ve makro haber/diğer piyasa karmaşası nedeniyle nedensel etki değildir.

## Öğrenilen ekonomik sürpriz S1 araştırma deneyi

Kronolojik (her olay yayınından **önce tamamlanmış** bağımsız olay sonuçlarını kullanan) 8 en yakın geçmiş benzer vaka tahmini; yakınlık yalnızca açıklama anında artık bilinebilen **NFP/AHE/UNEMP veya CPI actual−consensus sayısal sürprizleri** ve haberden 60 dakika sonraki önceki bir saat altın hareketine dayanır. İki kol **aynı yayın ailesi, aynı eğitim olayları, aynı anchor, aynı sabit k=8, aynı smoothing ve bandwidth** kullanır:
- **Sürprizli S1 araştırma tahmini:** iş gücü/CPI sayısal sürprizleri + fiyatın önceki 1 saat hareketi.
- **Sürprizsiz karşılaştırma:** aynı istihdam/CPI yayın ailesi + fiyatın önceki 1 saat hareketi, ancak actual−consensus sürprizleri **yok**.
- Üçüncü kontrol: ilgili yayın ailesi için yalnız geçmiş olgunlaşmış UP oranı (sürpriz/altın kondisyonu yok).
- İlk **8 olgun bağımsız olay** oluşmadan aile için tahmin yapılmaz. 2023 ısınma/veri kapsama; skorlar 2024–2025'te başlar. Model matematiksel olarak sürpriz işaretinin altın üzerindeki yönünü önceden sabitlemez. Bütün hiperparametreler bu koşuda sonuç üzerine optimize edilmedi.

| Değerlendirme | Ekonomik sürpriz + fiyat geçmişi | Aynı aile, yalnız fiyat geçmişi | Yalnız tarihsel yayın-aile UP oranı |
|---|---:|---:|---:|
| Değerlendirilen bağımsız 2024–2025 yayın | **41** | **41** | **41** |
| Doğru yön | **20/41** | **19/41** | Sadece Brier referansı |
| Olasılık Brier hatası (küçük daha iyi) | **0,295443** | **0,281137** | **0,257885** |

2024 (21 olay): ekonomi 10/21, fiyat 9/21; Brier sırasıyla 0,307950 ve 0,290214.
2025 (20 olay): ekonomi 10/20, fiyat 10/20; Brier 0,282310 ve 0,271606.

Ekonomik sürpriz modelinin Brier iyileşmesi karşılaştırmaya göre **−0,014306** (daha kötü). Bağımsız *yayım dalgası* düzeyinde 1.000 bootstrap deneyinin açıklayıcı %95 aralığı **[−0,0541; +0,0231]**: sıfırı içeriyor, iyileşme kanıtı yok. Ayrıca aile-önceki oranı daha güçlü basit referans; ilave ekonomik yakınlık fayda kanıtlamadı.

Bu deney bağımsız yıl-sıralı bilimsel keşif denetimidir; **makro firstprint sertifikası olmadığı ve 2026 yılında retrospektif araştırmayla kurulduğu için gerçek yayın-öncesi kör out-of-sample performans sayılamaz**. Bağımsız vaka sayısı/tekrarlanan kontroller ve habere sonradan erişim riski sonuçları sınırlar.

## Asıl öğrenilen / çürütülen şey
1. Arşivin 69 yayımlanma olayına kadar genişletilmesi Ocak'taki iki olayın tek örnek engelini araştırma düzeyinde kaldırdı; ancak güçlü ekonomik yön kestirimi sağlamadı.
2. Ekonomik olayın **hangi tür olduğu** ile gerçek fiyat devam/düzeltme mekanizması aynı şey değil. Kontrollerde zıt işaretler yaygın ve ekonomik-açık Brier kötüdür.
3. Kural örüntüsü geliştirilirken gümüş, faiz, USD, reaksiyon hızının dağılımı, durumun bitişi ve ekonomik karşıt mekanizmalar gibi koşullu kanıtlar incelenmeli; elimizdeki geri derlenmiş sürpriz sayıları tek başına yetmiyor.
4. **Ekonomik nedensellik veya kâr başarısı çıkmadı. S1 bilim kapısı FAIL.** S2 yaşam döngüsü / S3 pozisyon critic / S4 Ocak için tam 15dk trade modeli / S5–S6'e geçiş onaylanmadı.

## Kod, yeniden üretim ve test kanıtı
- [independent_event_research_query_s1.js](independent_event_research_query_s1.js): makro ledger içinden 69 yayını çıkarır, Neon için **read-only SELECT** üretir; fiyat verisini yayımlamaz. Ön ve sonraki fiyat barı tamlık kontrolleri, UTC eşleme, haber ±24h negatif-control blackout içerir.
- [independent_event_learning_s1.js](independent_event_learning_s1.js): tek yayıma tek label, data-defined nearest-neighbor economic-on/off ve aile UP kontrolü; destek, karşıt işaret ve belirsizlik raporu, stage firewall.
- [replay_independent_event_learning_s1.js](replay_independent_event_learning_s1.js): özel derive sonuç JSON'uyla tekrarlanabilir tek komut; hash'li DISCOVERY run_id, özel satırları print/commit etmez.
- [independent_event_learning_s1.test.js](independent_event_learning_s1.test.js): 8 yeni koruma ve sentetik koşullu örnek öğrenim testi; mevcut GitHub Actions akışına dahil edildi.
- Eski S1 deneylerini veya geçmiş OLAY-02/ÖĞREN-03 kaynaklarını değiştirmedik. Lisanslı ham barlar GitHub'a commit edilmedi.

**WORKSTREAM=MODEL | STAGE=S1 | INPUT=139 reconstructed macro components, 69 release waves, read-only 2023–25 XAU M15 | WRITTEN=4 S1 research audit assets + manifest + CI | REAL_RUN=57 complete waves, 41 scored | SCIENCE=FAIL | MODEL_GATE=FAIL | LIMIT=firstprint/consensus PIT uncertified; controls not independent; 12 incomplete markets | NEXT=improve condition features with audited XAG/USD/rates plus pre-release state and episode phase; recheck economic mechanism against independent controls before advancing S2.**
