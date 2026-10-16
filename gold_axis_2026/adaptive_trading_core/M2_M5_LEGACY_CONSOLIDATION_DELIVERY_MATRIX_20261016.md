# GOLD-ADAPTIVE-MODEL-APP-01 — Birleşik öğrenme denetimi (16 Ekim 2026)

**Tek proje, tek CORE; MODEL_GATE=FAIL; gerçek banka emri YOK.**

## Geçmiş araştırmadan korunacak ve reddedilecek teknikler

| Sürüm | Gerçek araştırma bulgusu | M2–M5 mühendislik kararı |
|---|---|---|
| V7–V10 | V7 2026 Şubat–Eylül 123,53$, sonraki fiyatla icra düzeltmesinde 116,50$. | Aynı karar barından emir fiyatı varsayma; sonraki M15 araştırma fiyatını kullan |
| V12 REHBER | 2023–2025 uzun yükselişine katılamadı. | Kaçırılan fırsat geri bildirimi M5'e eklendi |
| V13 SENTEZ | 14/56 gün + hafıza etkili görünüyordu, ANN ek yararı gösterilemedi; 2023–Eyl2026 201,59$, pasif altın 224,27$. | S3'e 14/56 takvim günü, gecikmeli sonuç, kapılı piyasa hafızası eklendi; ANN kuruldu denmiyor |
| V14 KOR | Net pozisyon öğrenimi kısmi; kârlı SAT yeteneği doğrulanmadı. | Olgunlaşmış net gold/cash getirilerinden uzman düzeltmesi, başarılı terfi iddiası yok |
| V16–V17 | Q/Double-Q çoğunlukla sentetik araştırma. | Mevcut kısa M15 critic korunur; gerçek piyasa üstünlüğü varsayılmaz |
| V20 R3 | 200 null senaryonun 15'inde yanlış kapı açılması (%7,5); önkayıt şartı %5 idi, reddedildi. | Null test / bağımsız validasyon olmadan strateji terfisi YOK |

## Bugün aynı CORE içinde gerçekten eklenenler

- `adaptive_long_cycle_s3.js`: 14 ve 56 takvim-günlü, ancak vadesi bitince öğrenen GOLD-vs-CASH getiri kaydı. Alışta ve satışta %0,8. 14g kaynak orijinleri en az 14g, 56g orijinleri en az 28g ayrılır; 56g etkin destek 56g ayrık orijinlerle ölçülür.
- Uzun dönem kalıcı trend/stres/geri çekilme özeti, geçmiş olgunlaşan sonuçlarla güncellenen AdaGrad kapılı trend uzmanı ve geçmiş hata üzerinden koşullu/global/kapılı uzmanın ağırlıklandırılması. Bu ANN veya tam LSTM değildir.
- M5: gecikmeli `missedUp`, `avoidedLoss`, `falseHold`. Bunlar toplam PnL değildir.
- Mevcut S3 `INTEGRATED_LONG_RESEARCH` gölge modu; eski iki araştırma modu korunmuştur. Sinyal ancak **bir sonraki gözlenen M15** fiyatında gölge işleme geçer; saat filtresi yoktur; gap/source uyuşmazlığında bekleyen emir iptal edilir.
- `replay_s3_monthly_challengers.js`: aynı M15, aynı maliyet, 3 mod, ay/işlem kayıtları, input SHA-256; ham lisanslı veriyi repo içine yazmadan yeniden üretim. GitHub CI sentetik/kronolojik sözleşme testleri PASS.

## Gerçek 2023 ve kapsam sınırlaması

2023'ün **23.544 M15** gözlemi tek kaynakla, başlangıç **100$ CASH**, ücret **%0,8 AL + %0,8 SAT**, banka saat filtresi olmadan kronolojik tekrarlandı.

| Karşılaştırma | Net 2023 sonu | AL/SAT |
|---|---:|---:|
| Eski M15 critic | 100,00$ | 0/0 |
| Beş seanslık karar | 100,00$ | 0/0 |
| **Yeni 14/56g bütünleşik sürüm** | **100,00$** | **0/0** |
| Altını ilk/son veri fiyatından alıp tutma | 111,104608$ | Varsayımsal 1 tur |

Geriye dönük 248 kabul edilen slow seans, **25 adet olgun 14g ve 11 adet olgun 56g** etiket üretti. 56g `effectiveN=6`, ilk hazır 56g öngörü **20 Haziran 2023**, `ALL#56` ortalama fee-net log getiri yaklaşık **−%0,567**. Gecikmeli `missedUp=13`, `avoidedLoss=23`; etiketler bağımsız değil. Kapılı 56g uzmanı 11 olgun sonuçla güncellendi. Pozitif 56g öngörü çıkan 2.382 M15 kayıt olsa da güven/risk eşiği nedeniyle yine 0 BUY. **2023'e göre eşik gevşetilip görünüşte kazanç üretilmedi.**

Bu sonuç modelin öğrenme altyapısının geliştiğini, **fakat AL/TUT/SAT stratejisinin 2023 yatırım başarısının hâlâ başarısız olduğunu** gösterir. Gerçek 2023 ekonomik ilk-vintage makro girdisi 0; haber/kural M2 bilimsel başarısı yok; M4 pozisyonun gerçek değişken süresini optimize etmiyor; immutable aylık CORE checkpoint zinciri yok; FIRSTPRINT, gerçek banka BID/ASK ve kör OOS yok.

## Tek otoriter sonraki kabul sırası

1. M2: İlk erişim zamanı doğrulanmış haber + çapraz-piyasa + olaysız/karşıt kontrol koşullarında ekonomik kuralların S1'e gerçek aktarımı ve yararı.
2. M3: Geçerli uzun trendin **kalan süresi ve büyüklüğü** için güvenilir koşullu dağılım; sadece sabit 56g getiri değil.
3. M4: CASH→GOLD, GOLD→GOLD, GOLD→CASH ve CASH→CASH eylemlerini **gelecekteki öz-finansmanlı portföy değerine** göre öğrenmek; mevcut 56g otomatik tasfiye varsayımını aşmak.
4. M5: Gerçek aylık immutable state start/end, gecikmiş label/policy/hata etkisi için ayrı ablation. 
5. Başarı kapısı: aynı ücret+fiyatlı nakit/pasif altın/SENTEZ/S3 karşılaştırması, null yanlış-alarm, ileriye dönük sabitlenmiş dönem; başarısızlıklar silinmez.

**Kural: Yeni dal/yeni UI/isim değil, aynı `adaptive_trading_core`. Teknik PASS bilimsel/kârlılık PASS değildir.**
