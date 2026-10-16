# Ocak 2026 altın AL–SAT — saatlik gerçek veriyle geriye dönük %0,8 test sonucu

**Araştırma tarihi:** 2026-10-16. **Yeni dal:** `research-gold-jan2026-real-h1-fee008-20261016`. **Orijinal önceki dosyalar değiştirilmedi.**

## Birinci sonuç (100 USD nakitle başlandı)
| Strateji | Son net tasfiye NAV (USD) | Net getiri | Max DD |
|---|---:|---:|---:|
| V18 | **108,638137** | **+%8,638137** | %9,871093 |
| R2 soft (DD referansı %15) | **108,638137** | +%8,638137 | %9,871093 |
| R3 gated (T=1,9) | **108,638137** | +%8,638137 | %9,871093 |
| Nakitte kal | 100,000000 | %0 | %0 |
| İlk uygun seansta AL, ay sonunda tasfiye et | **113,770523** | **+%13,770523** | ayrıca ölçülmedi |

Üç modelin de tek emri aynıydı: **2026-01-12 11:00 Türkiye**, BUY; H1 karşılaştırma mid **4587,720 USD/ons**. %0,8 tek yön banka maliyetine denk gelen AL fiyatı **4624,717742 USD/ons**, ilk tasfiye NAV **98,4064 USD**. Ay boyunca **SAT yok**, 30 Ocak 16:00 Türkiye son bankacılık kontrolünde **GOLD** pozisyonunda. R2 danışman müdahalesi=0; R3 kapı açılması/müdahalesi=0. Bu çalışmada R3 sentetik başarısızlığını telafi etmedi.

**Buy & hold fırsat maliyeti:** 113,770523 − 108,638137 = **5,132386 USD**. Sistem kâr etti ama düşük işlem sayısına rağmen pasif altının gerisinde kaldı ve Ocak sonu düşüşünde nakde geçmedi.

## Veri kaynağı ve sınırlamalar

**Gerçek piyasa kaynak verisi:** Neon'daki `gold_research_dukascopy_xau_h1_monthly_source_candidate_v1` (Dukascopy XAUUSD H1 BID/ASK). Ocak 2026 için 744 saat kaydı; 24 Aralık 2025–31 Ocak 2026 dahil 936 saatlik okuma; çalışma penceresinde **168 uygun işlem noktası**. Sonuçları hesaplamak için özel kaynağa salt-okunur bağlandık. Özel ham kaynak GitHub'a yüklenmedi.

**Önemli:** `source_vintage=RETRIEVED_2026_10_08_NOT_PIT`: veri Ocak 2026'da erişilebilir olduğuna dair kanıtlanmış bir as-of arşiv değildir, **Ekim 2026'da sonradan indirilmiş tarihsel fiyat** serisidir.

**Maliyet:** Dukascopy BID/ASK'tan oluşturulan midpoint'e **%0,8 tek yön** efektif banka uygulaması; BUY cash×(1−0,008)/mid; SELL goldUnits×mid×(1−0,008). Dukascopy kaynak spread'i **ayrıca ikinci ücret gibi eklenmedi**; bu, kullanıcı bankasının gerçek BID/ASK dizisi değildir. Türkiye 09:00–17:00 sınırlaması içinde, saatlik fiyatlar nedeniyle son işlem başlangıcı 16:00, hafta sonu ve 1 Ocak yılbaşı hariç.

**Nedensellik:** Sinyal yalnız önceki tamamlanmış H1 BID/ASK mid fiyatlarından oluşturulmuş gecikmeli r4 (4h), r1 (1h), r3 (3h), rv (12h), dd (48h) kullanır. NQ ve ekonomik haber etiketleri as-of doğrulanmadığından çıkarıldı. Model 100 USD nakitle sıfır Q ağırlıklarıyla başlar ve 167 tamamlanmış H1 aralığından kademeli öğrenir. İcra fiyatı bir sonraki H1 barının OPEN midpoint'inden alınarak 1 dakika sonrası emir fiyatı gibi varsayılır; gerçek +1m banka kotasyonu olmadığından **uygulama iyimserliği riski** vardır.

**Kontrol:** 2 Ocak 09:00 ilk uygun mid 4380,760; 30 Ocak 16:00 son mid 5064,725. İlk uygun anda alıp ay sonunda iki banka bacağıyla satmak 113,770523 USD olurdu. V18/R2/R3 son GOLD pozisyonu %0,8 tasfiye maliyetiyle net değerlendi.

## Bilimsel karar

Bu yalnız **geriye dönük saatlik as-of-prefix simülasyonudur**; gerçek banka kotasyonu, tam zamanlı 15 dakika fiyat kararı, resmî ekonomi olay ilk yayın kayıtları, gerçek portföy başlangıç öğrenmesi veya banka emrinin kabulünü içermiyor. R3'ün önceki resmi sentetik PREREG sonucunun RED statüsü aynen geçerlidir. Bu Ocak sonucuna göre eşiği ayarlamak sonraki Ocak testinin kör niteliğini tamamen yok eder; bu çalışmada eşiğe dokunulmadı.

**Orijinal Ocak 2026 araştırmaları silinmedi/değiştirilmedi.** Kaynak replayer: `jan2026_h1_fee008_replay.js`; özel CSV parametreyle verilir, herkese açık GitHub ham vendor serisi tutulmaz.
