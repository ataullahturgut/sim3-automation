# V46 — 2025 ORİJİNAL V22 → V43/V44 ÇIKIŞ SİNYALİ: GÜN GÜN OLAY DENETİMİ

**31 Ekim 2026 | V22 early risk NOT SELL | ARAŞTIRMA / CANLI DEĞİL**

## Veri ve yöntem

GitHub `gold_axis_2026/research/case_control_v13/outputs/v22_daily_decisions.csv` 2025 özgün V22 `effective_review` kararları kullanıldı. Toplam **232 karar günü, 20 V22 uyarı günü**; Ocak–Mart, Haziran–Eylül, Kasım–Aralık'ta bu belirli V22 araştırma günlüğünde risk yok. V22 işareti yalnız bir sonraki UTC fiyat gününün ilk gözleminden itibaren WATCH başlatabilir; 2025 için Neon HistData XAUUSD 15dk **23.606 bar** kronolojik işlenir. Giriş/yeniden giriş emri YOK. Üç kurala bakıldı: V22 anında ÇIK, V43 yapısal kırılma ve %2 tepe düzeltmesi+4 saatte %1 düşüş.

V43 kuralı: V22 WATCH + izlenen yüksekten **≥%1** geri çekilme + kesintisiz son 4 saatte **≥%1** düşüş + son **96 geçmiş 15m barın dip kapanışının altına kırılım**. Saatler `UTC`, barların ilk kayıt zamanını temsil ediyor; sonraki 15dk fiyat bir sonraki bar kapanış *araştırma fiyatı* kabul edilmiştir, banka bid/ask veya gerçekleşmiş emir değildir. Sonuç etiketi: sinyal sonrası NY17 esaslı **5 ayrı piyasa seansı** içinde ≥%4 gerileme. Ayrıca sinyalden sonra 24 takvim günündeki maksimum fiyat sadece GERİYE DÖNÜK kaçırılan yükseliş denetimi için hesaplanır; karar mekanizmasına katılmaz.

## V43 risk izleme 12 gün — iki büyük uzun birleşik risk dönemi

| İlk V22 | Sonraki V22 uyarıları | İlk V43 ÇIK (TSİ) | Bir sonraki 15m fiyat USD/ons | Sonraki 5 seansta en düşük % | Etiket |
|---|---|---|---:|---:|---|
| **04 Nisan 2025** | 7/8/11/14/15/16/17/22/23/28 Nisan; 6/7/8/9 Mayıs | **7 Nisan 20:15** | **2.974,865** | **−%0,048** | FALSE/çok erken |
| **10 Ekim 2025** | 13/17/20/21 Ekim | **17 Ekim 18:00** | **4.240,389** | **−%5,322** | TRUE |

12 günlük izleme makinesi, ilk çıkış kaydedildikten sonra aynı WATCH'ı `EXIT_RECORDED` durumunda tutup sonraki bütün V22 risk günlerini **yeniden çıkış saymaz**. **4 Nisan–9 Mayıs tek alarm dönemi olduğundan** 22 Nisan ve 6 Mayıs'ta yeni çıkış üretmedi. Bu, yanlış alarmın maliyetinin ötesinde, sonraki iyi zamanlı sinyalleri de perdeleyen tasarım kusurudur.

Nisan'da 7 Nisan 17:30 UTC tarihi fill 2.974,865 USD/ons. Fiyat 22 Nisan 07:00 UTC'de 3.497,165'e çıktı: **erken ÇIK sonrası +%17,557 ilave yükseliş**. Algoritma istenen korumayı sağlayamadı. Yakın dönem 7 Nisan tarihsel dip 2.958,795; sinyal neredeyse dipten çıkış üretti.

Ekim'de 10 Ekim risk → 17 Ekim yapısal ÇIK: fill 4.240,389. Fiyat 20 Ekim 20:45 UTC'de 4.377,848 zirvesine kadar daha **+%3,242** yükseldi; bu da tam zirveyi yakalamadı. Sonraki beş NY17 piyasası seansındaki minimum ise −%5,322: düşüşle eşleşen faydalı, ancak hâlâ yükselişten kısmen erken çıkış.

## V45/V46 — aynı model, 2025'te 6 farklı risk süresi, hiçbir eşik optimizasyonu yok

| Son V22 uyarısından sonraki WATCH süresi | Risk dönemleri | V43 ÇIK | ≥%4 düşüşle eşleşen | Sonuçsuz |
|---|---:|---:|---:|---:|
| 4 gün | 5 | 5 | **2** | **3** |
| 6 gün | 3 | 3 | **2** | **1** |
| 8 gün | 2 | 2 | **1** | **1** |
| 10 gün | 2 | 2 | **1** | **1** |
| 12 gün | 2 | 2 | **1** | **1** |
| 16 gün | 2 | 2 | **1** | **1** |

Süre 2025'e uyumlanarak seçilmemiştir. **6 günde 2/3 ile daha iyi görünmek**, gerçek kazanım kanıtı değildir: risk dönemlerini bölmenin/hangi alarmın baskılandığının etkisidir.

**4 günlük WATCH ile beş risk dönemi ayrışınca:**

| Ayrı risk dönemi | V43 ÇIK (TSİ) | Fill USD/oz | Sonraki beş seansta en büyük düşüş | Etiket |
|---|---|---:|---:|---|
| 4 Nisan | 7 Nisan **20:15** | 2.974,865 | −%0,048 | FALSE |
| 22 Nisan | 23 Nisan **10:00** | 3.322,095 | −%1,545 | FALSE |
| 28 Nisan | 30 Nisan **13:45** | 3.273,675 | −%2,093 | FALSE |
| 6 Mayıs | 8 Mayıs **09:45** | 3.344,885 | **−%5,198** | TRUE |
| 10 Ekim | 17 Ekim **18:00** | 4.240,389 | **−%5,322** | TRUE |

**6 günlük WATCH** 4 Nisan–28 Nisan birleşik 1 FALSE, 6–9 Mayıs TRUE, 10–21 Ekim TRUE: üç çıkışta iki eşleşme. **8–16 gün** Nisan–Mayıs birleşerek Mayıs çıkışını baskılıyor. 4 günde Nisan içinde iki ek FALSE çıkış oluşuyor. Sıfır yanlış alarm gösteren V43 versiyonu **2025 verisiyle desteklenmiyor**.

## Eski V22 anında ÇIK ile karşılaştırma

**12 günlük WATCH** ile sadece ilk alarmdan sonraki fiyat gününde V22'yi doğrudan ÇIK kabul edersek:

- 4 Nisan uyarısı → 6 Nisan 23:00 UTC sinyal, sonraki fiyat ~**3.014,405**, sonraki 5 seans düşüş **−%1,359**; yine FALSE; 22 Nisan'a kadar sonraki zirveye %16,015 ilave yükseliş.
- 10 Ekim uyarısı → 12 Ekim 23:00 UTC sinyal, sonraki fiyat **4.040,035**, sonraki 5 seans içinde dip **+%1,443** (fiyat sinyal seviyesinin üstündeydi); yine FALSE; 20 Ekim zirvesine kadar %8,362 ilave yükseliş kaçırırdı.
- V43 Ekim'de erken V22 SAT'a kıyasla **daha yüksek fiyatla çıktı**, ancak Nisan'da tek başına yapısal kırılma koşulu yetmedi.

## Kritik metodolojik sınırlamalar

1. **2025 özgün V22 kaydı** geçmişte yeniden yaratılmıştır; o gün gerçekten kaydedilmiş ilk yayın/ilk sinyal olduğuna dair kanıt yok. Aynı ilk yayın sürümü 2026 V33 ile birebir aynı da değildir.
2. **2025 gözlemleri modele eşik seçmekte kullanılmadı** (bu V46’de). Ancak önceki araştırmalarda 2025 ve 2026 dönemleri görülmüştür. Dolayısıyla bağımsız kör ileri test kanıtı yoktur.
3. Önceki V43/V44 uyarı karşılaştırmaları **sinyal koşullu beş seanslık** sonuçları ölçüyor, tüm fiziksel ≥%4 altın düşüşlerinin kapsamasını ölçmüyor.
4. 5 ayrı piyasa seansında en düşük 15m fiyatı etiketi, V22 günlüğündeki eski gün sonu/%5 etiketleriyle karıştırılmamalıdır.
5. Saat damgaları bar başlangıcı olabilir. Gerçek veri erişim zamanı, bankanın alış/satış spread'i, kayma ve işlem gerçekleştirme yoktur. Sadece araştırma.
6. Bir risk epizodu içinde sinyalden sonraki V22 günleri `EXIT_RECORDED` kalıp **otomatik ikinci SAT üretmez**; görünmez kalmış Mayıs tepkisini ayrıca raporlamak gerekir.
7. **Karar:** 2025 Nisan + Mayıs yüzünden mevcut V43 doğrudan canlıya geçmez. Sinyal sonrası trendin yanlış kırılmasını ayırt etmek ve büyük trend devam ederken `EXIT_RECORDED` suppressorunun yeni V22 uyarılarını güvenle tekrar değerlendirmesi gerekir. Bu yeni kurallar 2025 üzerinde optimize edilip 2025 test diye sunulmamalıdır.

## Çalıştırma ve kanıt

- `risk_v44_three_year_v22_streaming_sell_only.py`: orijinal V22 2024–25 + 2026 yeniden oynatma, kronolojik 15m; `Stream` durum makinesi.
- `risk_v45_v22_watch_duration_robustness.py`: altı süre duyarlılığı, üç yıl.
- `risk_v46_2025_v22_exit_event_detail.py`: **2025 özgün V22 yirmi uyarı günü** ve 4/6/8/10/12/16 gün gruplarındaki ayrıntılı olay günlüğü.
- Başarılı GitHub Actions: <https://github.com/ataullahturgut/sim3-automation/actions/runs/41188605506>; 15/15 test PASS, Neon veri okuması PASS; 2025 tüm satırların JSON artifact'i içerir.
- Üretim modeline, ANN'ye, V22'ye, Neon verilerine veya gerçek işlem emirlerine dokunulmadı.

**2025'te toplam faydalı sinyal sadece Ekim ve daha kısa WATCH ile Mayıs'da görüldü.** Asıl eksik: Nisan erken yanlış dönüş; yeniden verilen uyarılar bastırılırken takip dönemine göre doğru çıkış yapamama.
