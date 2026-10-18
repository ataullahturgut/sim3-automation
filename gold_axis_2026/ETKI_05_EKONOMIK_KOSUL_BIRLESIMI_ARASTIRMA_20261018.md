# ETKİ-05 — Ekonomik Koşul Maddeleri: CPI + Çekirdek CPI + İstihdam + Ücret + İşsizlik

**18 Ekim 2026 · Araştırma V2 · MODEL/APP/AL-SAT değiştirilmedi · Geçmiş arşiv analizi, kör sınav değil · SCIENCE_GATE=FAIL.**

## Asıl araştırma sorusu

Kullanıcı **yeni fiyat hareketi sınıflaması veya yeni algoritma** istemiyor. İstediği *ekonomik MADDE etiketleri*: enflasyon yüksek/düşük sürprizi, istihdam güçlü/zayıf, ücret güçlü/zayıf, işsizlik beklentiden yüksek/düşük, çekirdek enflasyon sürprizi, USD/faiz/diğer göstergeler; bu etiketlerin **tek veya birkaçının** birlikte varlığıyla **altının UP/DOWN, küçük/büyük, süre ve ters örnek** dağılımının karşılaştırılması. Etiket hem **input koşuludur** hem de **olayın anlamıdır**; gelecekte gerçekleşen fiyat sonucuyla karıştırılmaz.

**2020–2022 kesinlikle eğitime/sayılara katılmadı.** 2023–2025 odak: Neon `gold_research_r72_claude_macro_analogs_v1` arşivinde NFP + ücret + işsizlik ve CPI + çekirdek CPI sürprizleri bulundu. Bu makro değerler GitHub'daki `OLAY_02_85_MAKRO_YENI_DNA_TEPKI_PLASEBO_20261014.csv` ile **timestamp ve olay türü üzerinden 69/69** eşleştirildi; **4 saat sonucu dolu 68 olay** (**34 CPI, 34 NFP**). 2023-04-07 NFP'nin 4s altın sonucu arşivinde eksik; geçersiz tam 4 saat sayılmadı. R72'nin 2023–2025 tüm makro geçmişi 93 olay içerir (FOMC dâhil), fakat bugünkü testte ücret/işsizlik ve çekirdek CPI sürprizleri olan 69 CPI/NFP'ye bakıldı. R72 2020–2022 veri taşısa da **kullanılmadı**.

**PIT uyarısı:** BLS'nin 2023-01-06 ve 2023-02-03 ilk bültenleri toplu istihdam actual ve ücret düzeylerini doğrular; Neon'daki *o tarihte piyasanın gerçek konsensüsü* henüz orijinal `consensus_vintage` ve `first_available_at` ile sertifikalı değildir. Tüm sonuçlar `RETROSPECTIVE_ONLY`. "Yüksek enflasyon" burada mutlak fiyat artışı değil **beklentiden yüksek aylık CPI sürprizi** olarak tanımlanır. `s_un>0` beklenenden **yüksek işsizlik** demektir (normalde güvercin sinyal); daha düşük işsizlik `s_un<0`.

## Tek ekonomik madde — 4 saatlik gözlem sonuçları

| Koşul etiketi | Sayı | 4s UP | 4s DOWN | ≥+%1 | ≤−%1 |
|---|---:|---:|---:|---:|---:|
| K01: CPI beklentiden yüksek | 8 | 3 | 5 | 0 | 2 |
| K02: CPI beklentiden düşük | 13 | 11 | 2 | 5 | 0 |
| K03: İstihdam beklentiden güçlü | 23 | 10 | 13 | 4 | 5 |
| K06: Ücret beklentiden yüksek | 13 | 4 | 9 | 0 | 2 |
| K07: İşsizlik beklentiden yüksek | 14 | 7 | 7 | 2 | 2 |
| K16: Çekirdek CPI beklentiden yüksek | 8 | 2 | 6 | 0 | 1 |
| K17: Çekirdek CPI beklentiden düşük | 11 | 9 | 2 | 4 | 0 |
| K18: Ücret beklentiden düşük | 13 | 7 | 6 | 3 | 1 |
| K19: İşsizlik beklentiden düşük | 12 | 5 | 7 | 2 | 2 |

**Ön bulgu:** Ücret ve çekirdek enflasyonun altınta koşullu etkisine dair araştırılabilir ayrışma var. Ancak tek etiketle güvenilir şiddet ölçüsü veya neden kanıtı yok.

## Aynı açıklamada maddeler birleştiğinde

Bunlar **aynı açıklamada birlikte bulunan** ekonomik işaretlerdir; önceki ETKİ-05'teki "45 gün önceki farklı veri" birleşiminden farklıdır.

| Ekonomik koşullar aynı açıklamada | Örnek | 4s UP | 4s DOWN | ≥+%1 | ≤−%1 |
|---|---:|---:|---:|---:|---:|
| **K02+K17:** manşet ve çekirdek CPI ikisi de beklentiden düşük | 9 | 8 | 1 | 4 | 0 |
| **K01+K16:** ikisi de beklentiden yüksek | 4 | 2 | 2 | 0 | 1 |
| **K03+K06:** istihdam ve ücret birlikte güçlü | 8 | 2 | 6 | 0 | 2 |
| **K03+K18:** istihdam güçlü, ücret beklentiden zayıf | 10 | 5 | 5 | 3 | 1 |
| **K03+K07:** istihdam güçlü, işsizlik beklenenden yüksek | 10 | 5 | 5 | 2 | 2 |
| **K03+K19:** istihdam güçlü, işsizlik beklenenden düşük | 10 | 4 | 6 | 2 | 2 |
| **K03+K06+K19:** istihdam güçlü + ücret yüksek + işsizlik düşük | 5 | 1 | 4 | 0 | 1 |
| **K03+K18+K07:** istihdam güçlü + ücret zayıf + işsizlik yüksek | 7 | 4 | 3 | 2 | 1 |

**Neden bu ayrım önemli?** 6 Ocak 2023 güçlü istihdam sürprizi (+23 bin), zayıf ücret sürprizi (−0,1 puan), beklenenden düşük işsizlik (−0,2 puan) ile sonraki 4s altın **+%1,391** gözlendi. 3 Şubat 2023 güçlü istihdam (+332 bin), beklentiye eşit ücret ve düşük işsizlik ile sonraki 4s **−%2,611**; 10 Mart 2023 güçlü istihdam (+106 bin), zayıf ücret (−0,1), yüksek işsizlik (+0,2) ile altın **+%1,551**. **Tek NFP etiketinin neden yetersiz olduğunu** gösterir; bu farkların doğrudan sebebinin ücret/işsizlik olduğuna dair bağımsız USD ve faiz teyidi halen yok.

**Karşıt örnekler:** K02+K17 içindeki **2025-06-11** CPI, 4s **−%0,250**; K03+K06 içinde bazı yıllarda yükseliş de var (toplam 2/8). Küçük tarihsel gruplardan yüzde 100 kural yazmak yasak. Ekonomik ifade ile fiyat yönünü sonradan eşleştirip mutlak kural sanma.

## 2025 kontrolü: Daha çok madde gerçekten daha iyi mi?

**Karar günü bu göstergeler açıklanabilir varsayıldığında**, geçmiş **2023–2024 (47 kayıt)** üzerinden etiket koşullu **Laplace-düzeltilmiş** olasılık `(pozitif_örnek + 1)/(grup_örneği+2)` oluşturulup **2025 (21 kayıt)** üzerinde dört seçenek kıyaslandı. Bu geriye dönük seçilmiş etiketlerin **takvim dışı hassasiyet testi**; tüm hipotezler sonrası yapıldığı için kör test/gerçek trade değil. Hedefler: sonraki 4s UP ve mutlak 4s ≥%1.

| Etiket seti | UP Brier (düşük daha iyi) | ≥%1 şiddet Brier |
|---|---:|---:|
| Yalnız CPI/NFP türü | **0,29237** | **0,20392** |
| Tür + manşet sürpriz işareti | 0,29067 | 0,23232 |
| Tür + manşet + ücret/çekirdek CPI sürprizi | **0,27675** | **0,27028** |
| Üstteki + işsizlik sürprizi (NFP) | 0,30505 | 0,27955 |

**Sonuç:** Manşet+ücret/çekirdek ile **yön hata skoru iyileşti**, ancak **büyük hareketi tahmin etme hatası daha da kötüleşti**. En ayrıntılı üçlü istihdam/ücret/işsizlik kombinasyonları yön testinde de kötüleşti. Çift grupta 2025'in **5/21** olayı, üçlüde **6/21** olayı eğitimde hiç görünmeyen kombinasyondur; aşırı ayrıntılı etiketler veriyi seyreltiyor. Kullanıcının aradığı maddeleri kaydetmek doğru; **tüm kombinasyonları bağlayıcı kural olarak birden eğitmek doğru değil**.

Fiyatın %1 hareketi bu çalışmada **kolay anlaşılır geçici büyüklük tarifi**, modelin küçük/büyük fiyat etkisini rejime uygun öğrendiği ispatı değildir; normal volatilite ve matched placebo kontrolüyle ufuk bazlı normalize ölçek gerekir.

## Aşamalar ve eksik maddeler

1. **Maddeler tamam:** K01–K19, aynı haber alt-bileşenleri ve önceki olay bağlamı ayrı tutuluyor. İlk çalışmadaki K06 (ücret yüksek) ve K07 (işsizlik yüksek) için daha önce "ölçülmedi" yazıyordu; Neon R72 geçmiş ekonomik sürprizleri bulunarak `RETROSPECTIVE_PROXY` seviyesine yükseltildi, *ilk yayın doğrulandı* anlamında değil. K16/17 çekirdek CPI, K18/19 karşı işaretleri ayrı kodlandı.
2. **Eksik gerçek ekonomi:** K08/K09 USD ve K10/K11 **gerçek reel faiz** simultane doğrulanmadı. Neon'da CME `ZN.c.0` **tahvil vadeli fiyatıdır**, doğrudan ABD tahvil getirisi değildir; `GC/SI/NQ/CL` sürekli vadeli H1 serileri saat kapsamı kısıtlıdır. Bunları gerçek USD/reel faiz diye etiketleme. K12/13 stres/marjin ilk haber doğrulaması yok.
3. **Ekonomik anlam:** Ücret, işsizlik, çekirdek CPI tek bir `NFP_HAWK` kuralına otomatik çökmemeli. Görüşler ve karşıt kanıtlar ÖĞREN-03'ün ORG ekonomik örgüleriyle *referans* ilişki taşıyabilir, ancak K-etiket kökü bağımsız ve tarihsizdir.
4. **Bundan sonraki gerçek kabul:** Orijinal konsensüs vintage + ilk haber saatini doğrula, eşzamanlı USD/reel faiz/metal değişimi ve olaysız/plasebo karşı örneklerini bağla, basit etiketlerin OUT-OF-TIME ve yeni olaylarla kalibre edilmiş koşullu dağılımını ölç, küçük/büyük şiddet testinde baseline'ı geçmedikçe S1/S2/S3 işlem kararı için kullanım yok.

**Veri otoriteleri**: Neon `gold_research_r72_claude_macro_analogs_v1` (read-only); [85 olayın tarihli M15 fiyat/karşı hafta sicili](OLAY_02_85_MAKRO_YENI_DNA_TEPKI_PLASEBO_20261014.csv); [OLAY-02](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md); [ÖĞREN-03](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md); [K koşul etiketleri](ETKI_05_KOSUL_ETIKETLERI_V1_20261018.json); [detaylı makineli grup sonuçları](ETKI_05_EKONOMIK_KOSUL_BIRLESIMI_V2_20261018.json).

**Resmi ilk-bülten tarihli örnekler**: [BLS 6 Ocak 2023 NFP](https://www.bls.gov/news.release/archives/empsit_01062023.htm), [BLS 3 Şubat 2023 NFP](https://www.bls.gov/news.release/archives/empsit_02032023.htm), [BLS 10 Mart 2023 NFP](https://www.bls.gov/news.release/archives/empsit_03102023.htm). Bunlar **actual rakamlarına** ilk yayın kontrolüdür; belirtilen consensus-vintage üçüncü taraf piyasa beklentilerinin kaynak zamanı henüz doğrulanmış değil.

**Bilim kapısı:** K etiketleri = ARŞİV ARAŞTIRMA SÖZLÜĞÜ. `MODEL_SCENTIFIC_CAUSAL_RULE=NOT_PROVEN`, `TRADE_ALLOWED=FALSE`, `CORE_UNMODIFIED=TRUE`, `FIRSTPRINT_EXPECTATIONS=UNVERIFIED`.
