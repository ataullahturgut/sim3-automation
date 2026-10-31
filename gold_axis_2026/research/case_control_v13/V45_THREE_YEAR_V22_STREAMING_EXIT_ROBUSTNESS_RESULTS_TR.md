# V44–V45 — 2024–2026 ÜÇ YILLIK GERÇEK V22 ARAŞTIRMA KAYITLARIYLA ARDIŞIK ÇIKIŞ SİNYALİ DENETİMİ

**31 Ekim 2026 | Neon gerçek HistData XAU/USD 15m | DEĞİŞTİRİLMİŞ CANLI MODEL YOK — YALNIZ ARAŞTIRMA**

## Genişletilen kapsam (önceki V43 2026 kısa denemesinden farkı)

- İlk kez **2024'ün 254 V22 araştırma karar günü (12 riskli değerlendirme günü), 2025'in 232 karar günü (20 risk günü)** `outputs/v22_daily_decisions.csv` dosyasından gerçekten okundu. V41/V42'nin sentetik uyarı mekanizması **kullanılmadı**.
- 2026 için `outputs/v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv` V22 günlüğü kullanıldı (2026 1 Ocak–30 Eylül 44 riskli fiyat günü); **2024–2025'in ilk V22 replay sürümü ile 2026 V33 güncel replay'i aynı sürüm değil**.
- Neon `public.gold_research_histdata_xau15m_candidate`: 2024 **23.713**, 2025 **23.606**, 2026 Ekim1 erken saatine kadar **17.616**, toplam **64.935** gerçek araştırma 15m barı; fiyat **HistData noncanonical**, banka alış-satış fiyatı değil, ilk yayın zamanları sertifikasız.
- İleri tarihli geleceğin fiyatı karar anında kullanılmadı. V22 D tarihindeki risk, aynı D gününde değil, ilk sonraki UTC fiyat tarihinde WATCH olarak açıldı. Orada tepe yüksek su izi, sürekli dört saatlik getiri ve **önceki 96 adet fiyat barı** minimumu hesaplanıyor. V43 yapısal kırılma: (i) WATCH tepesinden ≥%1 geri çekilme, (ii) dört saatte ≥%1 düşüş, (iii) önceki 96 adet barın fiyat dibinin altına inme.
- Tek WATCH döneminde yalnızca **bir ÇIK işareti**, otomatik AL/yeniden AL, pozisyon getirisi/satış kârı hesaplama YOK. İşaretten sonraki fiyat barı (tam 15dk sonraki bar) tarihsel fill PROXY olarak sayılır. Sonraki **5 ayrı NY17 piyasa seansı** fiyatlarının minimumu, işaret fiyatına göre ≥%4 aşağıda ise TRUE. Sonucu henüz olgunlaşmamış işaret asla FALSE değil, UNKNOWN.
- V44 canlı/online duruma en yakın **kronolojik, bar-bar durum makinesi**: `IDLE → WATCH → EXIT_RECORDED → IDLE`; risk kapanış ve durum girişleri kronolojik kayıtlı ve imzalı. **Gerçek firstprint/PIT değil**; tarihsel model risk zaman damgası doğrulanmadı.

## V44 — tek bir 12 takvim günlük WATCH süresiyle bulunan sonuç

| Kaynak/yıl | Gerçek V22 araştırma risk dönemleri | İlk V22'de doğrudan ÇIK, doğru/sonuçsuz | Yapısal V43, doğru/sonuçsuz | V43 işareti olmayan risk dönemi |
|---|---:|---|---|---:|
| **2024** | **6** | **1/5** | **0/6** | 0 |
| **2025** | **2** | **0/2** | **1/1** | 0 |
| **2026 Ocak–Eylül** | **5** | **3/1** (+1 gelecek 5 seans sansürlü) | **4/0** | **1 (28 Eylül)** |

V43 2026'da çok iyi görünürken 2024 ve 2025'e **genellenmedi**. 2024 V22 30 Ekim uyarısında hemen çıkış sonrası beş seans dip **−%4,948** ile eşleşiyordu, V43 31 Ekim 14:30 sinyal sonrası yalnızca **−%3,163** yakaladı; teyit beklemek erken düşüşün bir bölümünü kaçırdı. 2025 Nisan WATCH'unda V43 7 Nisan işareti sonrasında düşüş **−%0,048**, Ekim 17 sinyalinde **−%5,322**. 2026 Ocak29, Mart20, Haziran9 ve Ağustos25 başlıca dört V43 çıkışıdır. Şubat, Nisan ve Eylül'e ait ayrı risk bloklarının nasıl gruplanacağı test kuralına bağımlıdır.

**Ara sonuç:** 2026'da bu kural ile 4/4 sonucu, doğru çalışan çevrimiçi filtre kanıtı DEĞİLDİR; 2024'te 0/6 ve uyarı gruplama seçimi bunun temel güvenilirlik zaafıdır.

## V45 — 4,6,8,10,12,16 günlük risk süreleriyle bağımsız sağlamlık denetimi

Tüm yılların tamamı 5 farklı fiyat sinyal kuralı (V44) ve risk-kümesi süresi 6 seçenekle kıyaslandı. Aşağıda sadece V43 yapısal kuralının **olgunlaşmış ÇIK sinyali sonrasında ≥%4 / sonuçsuz** dağılımı, 5 NY17 piyasa seansı etiketi:

| WATCH yenilenme/sönme süresi | 2024 eşleşen/sonuçsuz | 2025 eşleşen/sonuçsuz | 2026 eşleşen/sonuçsuz |
|---|---:|---:|---:|
| 4 takvim günü | 0 / 2 | 2 / 3 | 4 / 4 |
| 6 takvim günü | 0 / 4 | 2 / 1 | 4 / 3 |
| 8 takvim günü | 0 / 6 | 1 / 1 | 4 / 1 |
| 10 takvim günü | 0 / 6 | 1 / 1 | 4 / 1 |
| 12 takvim günü | 0 / 6 | 1 / 1 | 4 / 0 |
| 16 takvim günü | 0 / 5 | 1 / 1 | 3 / 0 |

Dikkat: **4 günün 2024'te 0/2 olması başarının arttığı anlamına gelmez.** Toplam 8 risk dönemi vardı, **6 tanesinde ÇIK işareti ÜRETİLMEDİ**. Sinyal yokluğu ve eksik epizotlar ayrıca takip edilmeli.

2026, 12 günle **4/4 / false0** görünüyor; 4 günle **4/8 / false4**. Bu farkın bir bölümü aynı risk dalgası içindeki uyarıların tek epizot halinde birleştirilmesinden kaynaklanıyor: Mart19 V22 dalgası Nisan6'ya kadar uzadığında Nisan17 V22, 12 günlük sönme süresi dolmadan gelmiş oluyor ve **ikinci bağımsız çıkış sayılmıyor**. Önceki V43 offline 8 seans kümelemede Nisan21 **YANLIŞ** çıkıştı. Sayımı değiştirerek yanlış alarmı yok etmek bilimsel başarı değildir.

## Sistem geliştirme kararı

1. **Henüz canlı SAT/ÇIK modelini değiştirme**: V43'nin 2024 testinde 0/6, 2025'te 1/2, uyarı sürelerinde aşırı dalgalanma var. Kullanıcının hedefi olan "erken yükselişi koruma + gerçek düşüşe geçişi yakalama + düşük false alarm" doğrulanmadı.
2. **Uyarıların süresini rastgele 4–16 güne göre iyileştirme**: 2026 sonuçları görüldükten sonra seçilen 12 gün "en iyi" diye dondurulamaz. Yeni araştırmada uyarı sönmesini **gerçek fiyat yapısı toparlandıktan sonra** başlatmak ve sürekli yeni risk sinyalleri geldiğinde yanlış alarmı nasıl saydığımızı sabitlemek gerekir.
3. **2024 ve 2025 gerçek V22 as-of**: Sinyal kayıtları var ama verinin o gün ilk yayım UTC sertifikası yok. V22 tarihsel dosyası 2026 deneyindeki V33 sürümüyle eşdeğer değil. Sürüm ile tarihsel uygunluk ayrılmadan 3-yıllık başarı iddia edilemez.
4. **Geleceğe dönük izleme için V46**: StakTrakr dört metal quote ilk *bizim toplayıcımızca görülme* kayıtları ayrı tablada başladı. Provider gerçek ilk yayım sertifikası ve canlı V22 yoksa yalnız fiyat-kaynağı gölgesi; **asla canlı EXIT** değil.
5. **Öncelikli teknik iyileştirme**: Birincil düşüş riskinden bağımsız, satışın doğrulandığı akışı ve güvenlik kısıtlarını kurmak; sonra bağımsız prospektif karşılaştırma. Sadece erken V22 + saniyelik osilatör eşiği yeterli değil; 2024–25 başarısızlığı gösteriyor.
6. **Kapsama eksikliği**: V22 hiç uyarı vermediği Mayıs 2026 dönemleri bu katmanda ÇIK sinyali üretmez; V22 kapsam eksikliği ayrı araştırma konusu.

## Tekrar üretim ve gerçek yürütme

- V44: `risk_v44_three_year_v22_streaming_sell_only.py`, `test_risk_v44_three_year_v22_streaming_sell_only.py`, `.github/workflows/gold-v44-three-year-streaming-exit.yml`. [Actions 41181937366](https://github.com/ataullahturgut/sim3-automation/actions/runs/41181937366) **14/14 TEST PASS**, gerçek Neon, tam rapor JSON artifact.
- V45: `risk_v45_v22_watch_duration_robustness.py`, `test_risk_v45_v22_watch_duration_robustness.py`, `.github/workflows/gold-v45-three-year-robustness.yml`. [Actions 41182060644](https://github.com/ataullahturgut/sim3-automation/actions/runs/41182060644) **17/17 TEST PASS**, üç yıl altı süre tam JSON artifact.
- V46: [main branch PR #177 merged](https://github.com/ataullahturgut/sim3-automation/pull/177); 15dk public source gözlemlerini ayrı, append-only Neon tablosunda; **V22 ilk-yayın gate BLOCKED, otomatik BUY/EXIT yok**.

**Sonuç:** Bir yıl ve tek seçilmiş epizot kuralında kazanılan mucizevi başarıya güvenmiyoruz; 3-yıllık sonuçlar V43'ü henüz **araştırma adayına** indirgememizi gerektiriyor.
