# ALTIN — ETF, COT ve değerli metaller: 2023–2025 olayları için bağımsız kanıt ve mekanizma denetimi
**14 Ekim 2026 | Tarihsel neden–sonuç araştırması | NO AL/SAT, NO MODEL PROMOTION, NO PROVEN CAUSAL SHARE**

## Bilimsel hüküm
1. **Altın–gümüş birlikte hareketi belirgin:** Düzeltilmiş 42 V1 ZigZag bacağından gümüş uç fiyatları uygun 38'inde 37 aynı yön; platin 30, paladyum 32 bacakta aynı yön. Bu, **olay başı-sonu geriye dönük eş-hareketi**, nedensel katsayı veya ileri tahmin performansı değildir. Aynı gün farklı sağlayıcıların kapanış saatleri eşit değil, günlük metal serisi 2026'da geriye dönük arşivlenmiştir.
2. **COT tek başına güvenilir DOWN nedeni değil:** 2023–24 haftalık kökenlerinden geliştirilen yüksek vadeli managed-money net pozisyonu eşiğinde izleyen beş uygun seansta V2 DOWN ilk-bayrağı 4/27 (%14,8), diğerlerinde 9/76 (%11,8); değiştirilmemiş eşikte 2025'te sırasıyla 1/22 (%4,5) ve 7/29 (%24,1). 2025 karşılaştırması iki taraflı Fisher p=0,1165; keşifsel, yıl/rejim etkisi ve küçük n.
3. **COT raporları Ekim–Kasım 2025'te yayımlanmadı:** ABD CFTC'nin 18 Kasım ve 9 Aralık resmi bültenleri: 30 Eylül pozisyon raporu 19 Kasım, 14 Ekim raporu 25 Kasım, 21 Ekim raporu 2 Aralık yayımlandı. İleri bilinen fiyat-neden yorumu için 2025 Ekim *rapor tarihi ≠ yayın tarihi*. Araştırma haftası 20 Ekim 2025'te erişilebilir son rapor 23 Eylül; 17 Kasım 2025 itibarıyla dahi 23 Eylül. Sonradan çıkan rapor dönemin piyasa durumunu retrospektif açıklayabilir ama o tarihte gözlemlenmiş sinyal olamaz.
4. **ETF–COT ayrışması doğrulandı:** 2024 Mart'ta küresel altın ETF akışı yaklaşık −US$823mn iken WGC'ye göre COMEX money-manager net long +278 ton arttı; 2024 Nisan'da altın yaklaşık +%4 iken ETF çıkışı yaklaşık −US$2bn. 2025 Nisan'da ETF akışı +US$11bn iken COMEX altın futures toplam net long pozisyonu ay bazında %30 azaldı. Bunlar farklı pozisyon/investor/ufuk kanallarının aynı anda zıt yönde ilerleyebildiğinin kanıtıdır; bireysel alımın fon veya vadeli piyasadan diğerine aktarıldığı kanıtı **değil**.
5. **İlk ETF çıkışı altın düşüşüne neden olmuştur iddiasına karşı örnek:** 21 Ekim 2025 sert fiyat satışında Kuzey Amerika ETF'leri yaklaşık +US$334mn net giriş bildirdi; net çıkışlar sonraki günlerde geldi. Bu veri **6 Kasım'da retrospektif yayımlandı**. Olayın başlatıcısı olarak ETF itfası iddiasını zayıflatır, diğer fonların/özel hesapların satışını reddetmez.

## Yöntem: bilinmeyen zamanda biliniyormuş gibi yapmama
- **Altın fiyat otoritesi:** 2023–25 774 NY17 tam geçerli seans için düzeltilmiş XAU 15-dk BID/ASK orta fiyatı; düzeltilmiş 54 V2 cluster'ının `start_first_threshold_date` değeri. V2 ilk bayrak, başlangıçta haberin ilk dakikası **değil**, çoklu ufukta %3 eşik aşma günüdür. Kaynak: [774 satır kaynak](GOLD_HISTORICAL_V2_NY17_CORRECTED_774_DAILY_HORIZON_REPLAY_20261014.csv), [54 cluster](GOLD_HISTORICAL_V2_NY17_CORRECTED_DIRECTIONAL_CLUSTERS_20261014.csv).
- **COT:** [Nokta-zamana-yakın yayın kronolojisi ve pozisyon kaynağı](GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv). Kullanılan ayrı ölçüler `fut_mm_net` (vadeli managed-money pozisyon normalize düzeyi), `opt_mm_z52` ve `d_opt_mm_net` (seçenekleri de içeren kaynak türevi). Sadece `cot_available_at_utc <= origin_date 20:00 UTC` olan rapor kullanıldı; bu NY17 kapanışından da önceye düşen **daha ihtiyatlı** cutoff'tır. Salı pozisyon ölçümü hiçbir zaman yayın tarihinin yerine konulmadı. Yayın tatil/2023-25 kesinti düzeltmeleri kaynaktan korunmuştur.
- **Gümüş/platin/paladyum:** Neon Gold Control `observations` tablosunda `XAG_STAKTRAKR_RESEARCH_DAILY_R1`/`XPT...`/`XPD...`, kaynak pinned StakTrakr `ed2e549...`, 2023–25 her metal için 758 günlük fiyat; `available_as_of` **2026-09-05**. Günlük serinin 2023'te anlık erişilebilir olduğunu kanıtlamaz. İleri haftalık istatistik için köken tarihinden **önceki** son günlük metal fiyatına ve onun beş önceki gözlemine bakıldı; yine de *historical reconstructed proxy, not verified real-time feature*.
- **Örneklem:** Her Pazartesi-başlangıç takvim haftasındaki **ilk uygun** 2023–25 NY17 seansını tek bir araştırma kökeni saydık (2023–24: 103; 2025: 51; toplam 154). İzleyen **5 uygun NY17 seans** boyunca **yeni V2 ilk-bayrak** DOWN, UP veya herhangi bir yön oluştu mu sorusu soruldu. Bu, 5 günlük kapanış düşüşüne veya aynı günkü fiyat hareketine eşit değildir. Üstelik farklı haftalardaki büyük ekonomik şoklar örtüşebilir. Vaka analizinden ekonomik atıf bağımsızdır.
- **Dondurulmuş hipotezler/filtreler:** Futures MM yüksek eşiği ilk iki yılın 75. yüzdeliği (`fut_mm_net >= 0.3065900336`); MM options z52 >=1; haftalık options MM değişimi pozitif; geçmiş beş metal seansından pozitif olan metal sayısı <=1; gümüşün altını 5 günde >=2 yüzde puan geçmesi; yüksek futures MM + zayıf metal birlikteliği. Altı hipotez × üç V2 ilk bayrak sonucu × iki dönem = **36 keşifsel hipotez kıyası**, iki taraflı Fisher exact p hiçbirinde 0,05 altına inmedi, çoklu kıyas düzeltmesi uygulanmadığından dahi *confirmatory positive* yok.
- **Farklı güvenilirlik sınaması:** yayınlanmış COT raporunun pozisyon tarihinde en fazla **14 takvim günü eski** olması koşulunu ayrıca uyguladık. 2023–24 103→94; 2025 51→41 hafta. 2025 yüksek futures MM ve sonraki DOWN: 1/22 vs 5/19, iki taraflı Fisher p≈0,0795. Negatif bağlantı yorumu güçlense bile örneklemin küçüklüğü/nedensel tanımlama yok.

## Yıl bazlı aynen taşınan COT testleri
| Ölçüm | 2023–24 kökenleri | 2025 ayrı değerlendirme |
|---|---:|---:|
| Yüksek futures MM → sonraki V2 DOWN | 4/27 = %14,8 | 1/22 = %4,5 |
| Diğer futures MM → sonraki V2 DOWN | 9/76 = %11,8 | 7/29 = %24,1 |
| Pozitif options-MM haftalık değişim → V2 DOWN | 9/49 = %18,4 | 4/16 = %25,0 |
| Diğer options-MM değişim → V2 DOWN | 4/54 = %7,4 | 4/35 = %11,4 |
| Yüksek futures MM + metal breadth<=1 → herhangi V2 yeni bayrak | 8/17 = %47,1 | 5/9 = %55,6 |
| Diğerleri → herhangi V2 yeni bayrak | 19/86 = %22,1 | 18/42 = %42,9 |

**İstatistiksel ayrım:** Son iki satır yön değil herhangi bir şokun V2 eşiği; düşük test N=9, 2025 Fisher p≈0,714. Pozitif MM-change/down ilişkisi her iki alt dönemde benzer işaret taşısa da ayrı p değerleri ≈0,138/0,240; iki yönlü şokun nedeni olarak **kanıtlanmaz**. COT yüksek net düzeyi 2025'te daha *az* DOWN başlangıcıyla örtüşmüştür; genel ‘crowded long ⇒ collapse’ öyküsü desteklenmez.

## Değerli metal ilişkisini yanlışlama: 37/38 ne kadar ayırt edici?
42 V1 bacağın 38'i için altın ve gümüşün pozitif/negatif işaret eşleşmesi 37/38 (**%97,37**). Bunun kendiliğinden istisnai bir ekonomik mekanizma olduğunu varsaymadık. Her bacak için **aynı başlangıç yılı, birebir aynı sayıda NY17 seansı, ≥%3 mutlak altın değişimi** bulunan (ve olayın kendisi olmayan) tüm alternatif altın–gümüş pencereleriyle eşleştirdik. 38 olayın tamamı için kontrol bulundu; olay başına eşit ağırlıklı altın/gümüş yön uyumu tabanı **%90,22** (toplam 3.381 yoğun örtüşmeli kontrol penceresi). Bu, altın–gümüş yön uyumunun büyük hareketler için başlı başına olağan olabildiğini; %97,4 değerinden yeni nedensel mekanizma ispatlamanın yanlış olduğunu gösterir. Kontrol pencereleri **birbirinden bağımsız** değil; p-değeri veya ileri sinyal gücü olarak kullanılamaz.

**Daha ayrıştırıcı bulunan yeni vaka: 30 Nisan–20 Mayıs 2024 (`SWING_V1_015`).** Altın NY17 **+%6,141**, gümüş Stak günlük **+%19,283**, aradaki **13,142 yüzde puan gümüş lehine ayrışma**. Aynı yıl ve **14 uygun altın seansı** uzunluğunda en az %3 altın değişimi olan 85 alternatif pencerede mutlak altın–gümüş ayrışmasının **%97,65 persentilinde**; altın getiri işareti ve büyüklüğü de olayın ±2 yüzde puanı içine kısıtlandığında 41 kontrolde **%97,56 persentilinde**. Bu belirgin *relative-amplitude* bulgusu, salt aynı yönde gitmelerinden daha ayrıştırıcıdır; seçilmiş vaka ve çoklu tarama nedeniyle doğrulayıcı istatistik değildir.

**Ekonomik nedensel aday:** Reuters'ın **17 Mayıs 2024** tarihli haberi gümüşün 11 yıllık zirveye ve bakırın güçlü yükselişe ulaştığını, Çin gayrimenkul destekleri ve emtia rallisiyle aynı döneme geldiğini bildirmiştir: https://www.reuters.com/markets/tsx-futures-subdued-rate-cut-bets-decline-2024-05-17/ . Silver Institute'un **30 Ocak 2024** tarihli beklentisi 2024 endüstriyel gümüş talebinde rekor ve güneş PV/otomotiv kaynaklı büyüme öngörmüştür: https://silverinstitute.org/global-silver-demand-forecasted-to-rise-to-1-2-billion-ounces-in-2024/ . Buradan **gümüşe özgü endüstriyel talep + genel kıymetli metal trendi + muhtemel spekülatif pozisyon değişimi** bileşik mekanizması sınanabilir. Mayıs yükselişinin ilk fiyat dakikası ve Çin açıklamalarının ilk baskısı, bakır/gümüş/GOLD futures aynı UTC ve aktif gümüş ETF/COT yayın zamanlarıyla henüz ayrıştırılmadığı için bu *aday açıklamadır*, kanıtlanmış etki oranı değildir.

[38 bacak için gold-silver süre/yıl ve hareket büyüklüğü eşleşmiş kontroller](GOLD_38_V1_GOLD_SILVER_MATCHED_LENGTH_WINDOW_20261014.csv).
## Dönemsel ekonomik mekanizma karşılaştırmaları
### Mart–Nisan 2024: ETF çıkışı altın yükselişini engellemedi
- 2024 Mart WGC'nin 9 Nisan retrospektif yayını: global ETF net −US$823mn, COMEX money-manager net long **+278 ton** (491 tona); altın yükseldi. Mekanizma adayları: türev talebi / opsiyonlar / Asya fiziki ve OTC talebi / düşen dolar-fırsat maliyeti. Bir yatırımcının ETF'den futures'a geçtiği **ispat değildir**.
- 2024 Nisan WGC'nin Mayıs yayımlı verisi: ETF çıkışı −US$2bn, altın aylık +%4. WGC GRAM normal faktörlerinin açıklayamadığı rezidü olduğuna da dikkat çekti. ETF net akışı = altının mekanik neden formülü değildir.
### Nisan 2025: ETF talebi ile COMEX futures pozisyonu zıt
- WGC'nin 8 Mayıs yayımladığı 2025 Nisan özeti: global fiziksel ETF net **+US$11bn**, Asya yaklaşık **+US$7.3bn**, COMEX futures toplam net long **%30 azalarak 566 ton**. Bu, finansal altın talebinin aynı tek kurum/ürün/haber olarak etiketlenmemesinin somut nedenidir.
- NY17 2–7 Nisan altın −%4,777 ve gümüş −%10,466; S&P 500 −%10,734: kısa vadede genel satış/likidite baskısına uyumlu. 7–21 Nisan altın +%14,779; bunu nisan ayı ETF net girişiyle tek başına nedenselleştiremeyiz çünkü WGC aylık sonradan açıklanmıştır ve aynı ay iki zıt altın bacağı vardır.
### Ekim–Kasım 2025: ilk altın satışı ile fon çıkışı aynı saat değil
- NY17 20–29 Ekim altın −%9,785; aynı tarihli gümüş −%6,998, platin +%1,767, paladyum −%2,953. Tam dört-metal ortak satış yok.
- 21 Ekim şiddetli altın düşüşüne rağmen Kuzey Amerika ETF net +US$334mn. WGC, takip eden hafta US$117mn net çıkış ve sonraki gün/haftalarda daha fazla çıkış bildirdi. Bu araştırma için **fonların hareketi izlemesi/farklı bölgesel akışlar** mekanizması araştırılır; ETF işlem zamanlarıyla aynı 15dk fiyat etkisi hesaplanmadı.
- COT 14 Ekim raporu **25 Kasım'a**, 21 Ekim raporu **2 Aralık'a** kadar yayımlanmadı. 20 Ekim haftası COT güncel değil: araştırma panelimizde en son gerçekten yayımlanmış rapor 23 Eylül 2025 tarihli. 17 Kasım'da bu pozisyon verisi artık 56 gün eskimişti. O nedenle Ekim'deki pozisyon değişimini **o dönemin önceden görülen nedeni** gibi sunmak yasak.

## Dış kanıt kaynakları ve as-of (ilk yayın saatini otomatik ispatlamaz)
- CFTC resmî yayın durması ve ilk yenileme takvimi (18 Kasım 2025): https://www.cftc.gov/PressRoom/PressReleases/9138-25
- CFTC resmî güncellenmiş takvim (9 Aralık 2025): https://www.cftc.gov/PressRoom/PressReleases/9147-25
- CFTC COT salı pozisyonu / cuma yayını açıklaması: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm
- WGC Mart 2024 ETF ve futures: https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2024/04
- WGC Nisan 2024 ETF: https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2024/05
- WGC Nisan 2024 gold commentary: https://www.gold.org/goldhub/research/gold-market-commentary-april-2024
- WGC Nisan 2025 ETF, COMEX 566t: https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2025/05
- WGC Ekim 2025 ETF daily first-drop: https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2025/11
- WGC ETF veri sıklığı/yayımlanması: https://www.gold.org/goldhub/data/gold-etfs-holdings-and-flows

## Sayısal kanıt dosyaları
- [154 NY17 weekly origin, COT yayın PIT ve tarihsel metal breadth](GOLD_COT_METAL_WEEKLY_ORIGIN_2023_2025_NY17_PIT_RESEARCH_20261014.csv)
- [36 hipotez/p-value sayısal tablo](GOLD_COT_METAL_HYPOTHESIS_DEV2023_24_TEST2025_20261014.csv)
- [42 V1 gold vs XAG/XPT/XPD endpoint karşılaştırması](GOLD_HISTORICAL_42_V1_PRECIOUS_METALS_ENDPOINTS_20261014.csv)
- [24 satır COT data age <=14 sensitivity](GOLD_COT_WEEKLY_PIT_STALENESS_SENSITIVITY_20261014.csv)

## Bundan sonraki *bilimsel* eksik kanıt
1. Veri vintage tarihi olan günlük gerçek ETF birim yaratma/itfa dosyalarını, gün sonu ilk yayımlanma saatiyle (iShares/State Street/fund filing), global aylık WGC rakamına karıştırmadan topla.
2. COT'un **2025 Ekim shutdown** takvimini test evreninden ayrı tut; Ekim için sonradan yayımlanan pozisyonlara ex-post *mechanism diagnostic* dışında kullanım verme.
3. Saatli CME GC/SI ve XAU aynı-kapanış barları, GC OI ve options gamma/vol, EFP ile USD nominal/reel faiz için **aynı UTC pencere** kur ve haber ilk baskıyla eşleştir; Neon's CME GC/SI boşluklarını asla doldurulmuş kabul etme.
4. Mar2024/Apr2025/Oct2025'in üç rekabetçi mekanizmasını karşıt-event ve sessiz kontrol ile yanlışlamayı dene. EFT ve COT fiyat artışı sonrası görülen endojen cevap olabilir. Genişliği, seçilmiş geçmiş olaylardaki korelasyonu ve zaman sırasını ayrı raporla.

**Karar:** `CO-MOVEMENT_DESCRIPTIVELY_SUPPORTED / ETF_FUTURES_CHANNEL_DIVERGENCE_SUPPORTED / COT_SHUTDOWN_ASOF_CRITICAL / SHORT_HORIZON_CAUSAL_DIRECTION_NOT_PROVED / RESEARCH_ONLY`.
