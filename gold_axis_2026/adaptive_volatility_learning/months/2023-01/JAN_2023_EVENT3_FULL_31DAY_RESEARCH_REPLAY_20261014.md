# Ocak 2023 — Olay odaklı UP/DOWN 31 gün yeniden çalışma ve komisyonlu portföy
**2026-10-14 · STATÜ: REPLAY_EXECUTED_PRICE_ONLY_EVENT_BASELINE / GPT_EVIDENCE_REVIEW_NON_NUMERIC / NON_BLIND / NO_REAL_BANK.**

> **Önceki hedef hatası düzeltildi.** Bu yeni deney 5-seans trend işareti döndüğünde al-sat yapmaz; orta/büyük %3 yönlü olay teyidi üzerinde çalışır. Altın pozisyonunda DOWN %3 teyit gelmedikçe küçük düşüşte SAT yok. **Ancak bu tek fiyat eşiği henüz maliyet-sonrası kalan hareket tahmin etmez; asıl çok etkenli GPT+sayısal olay stratejisi kanıtlanmış değildir.** Günlük giriş-çıkış yoktur, eylem için sabit saat kullanılmaz.

## Tam sayısal sonuç — başlangıç $100
| Aynı 2023 vendor BID/ASK ve AL/SAT ayrı %0,8 komisyon | Ay sonu net $ | İşlem yönü |
|---|---:|---:|
| **İlk %3 UP/DOWN olay-takip araştırma adayı** | **101.9914** | 1 AL, 1 karşılaştırma amaçlı dönemsonu SAT |
| Eski yanlış-hedefli 5-seans momentum V0 | 101,9695 | 2 AL, 2 SAT |
| Pasif altın (Jan3 ilk M15–Jan31 son NY17 M15) | 103,7589 | 1 AL, 1 SAT |
| Nakit | 100,0000 | 0 |

**Yorum:** Tek BUY 2023-01-04 08:15 UTC sırasında BID/ASK ile ask 1859,72; son NY17 likidasyon 2023-01-31 22:00 UTC, bid 1927,47. Formül `100*0.992/1859.72*1927.47*0.992=101.991366`. Kazanç **+%1.991**; pasif karşısında **-1.7675 $**. 4 Ocak teyidine dek nakitte kalmak, Ocak yükselişinin erken kısmını kaçırdı. Eski V0'dan ~2 sent farklı çıkması **model üstünlüğü anlamına gelmez**.

## Her gün tek tek — NY17 seans fiyat değişimi ve 100 $ teorik NAV
Yüzdeler **bir önceki tam NY17 seansı kapanış MID'e göre**; 16 Ocak kısmi MLK seansı kapanışı olmadığı için önceki geçerli tam seans taşınır. Günler NY17 etiketidir; bu tablo 00–24 UTC gün sonu fiyat tablosu değildir. 1–2 Ocak ve hafta sonları işlem yok. Fiyat kaydı vendor MID/BID/ASK, gerçek banka kotasyonu değil.

| Gün | XAU NY17 % | Olay / somut gözlem | Karar | 100$ NAV |
|---|---:|---|---|---:|
| 01 | — | Yılbaşı; XAU işlemi yok | Nakit tut | $100.00 |
| 02 | — | Bankada mesai varsayımıyla yeni pozisyon yok; Jan3 NY17 seansı UTC 23:00'te açıldı | Nakit tut | $100.00 |
| 03 | 0.850% | İlk tam NY17 seansı; 5-seans +%3 olay teyidi henüz yok | Nakit tut | $100.00 |
| 04 | 0.829% | 5-seans +%3 UP ilk M15 teyidi 08:00Z; sonraki kapanmış M15 08:15Z ASK ile AL. JOLTS 15:00Z, FOMC tutanağı 19:00Z SONRA; alımın nedeni olamaz | **AL** | $98.88 |
| 05 | -1.169% | NY17 -%1,169: tek günlük DOWN, komisyon+makas üzerinde yeni tam tur fırsatının kanıtı yok | Altın tut | $97.76 |
| 06 | 1.800% | NFP 13:30Z; 1s +%0,544 / 4s +%1,401; mevcut UP pozisyonu korunur | Altın tut | $99.51 |
| 07 | — | Hafta sonu; emir yok | Altın tut | $99.51 |
| 08 | — | Hafta sonu; emir yok | Altın tut | $99.51 |
| 09 | 0.302% | UP devam; yeni alım gerekmiyor | Altın tut | $99.80 |
| 10 | 0.293% | UP küçük devam; HOLD | Altın tut | $100.08 |
| 11 | -0.077% | Hafif çekilme; HOLD | Altın tut | $100.01 |
| 12 | 1.149% | ABD CPI 13:30Z; 1s +%0,258 / 4s +%0,452; HOLD, nedeni izole değil | Altın tut | $101.15 |
| 13 | 1.223% | Güçlü UP devamı; fiyat yolu pozisyonu teyit eder ama ayrı işlem yok | Altın tut | $102.38 |
| 14 | — | Hafta sonu; emir yok | Altın tut | $102.38 |
| 15 | — | Hafta sonu; emir yok | Altın tut | $102.38 |
| 16 | — | MLK tatili/kısmi seans; NY17 tam kapanış yok; yeni karar yok, son tam kapanış NAV taşındı | Altın tut | $102.38 |
| 17 | -0.599% | 17 Ocak -%0,599 (13 Ocak son tam kapanışa göre); orta/büyük DOWN net fırsatı teyit edilmedi | Altın tut | $101.79 |
| 18 | -0.246% | PPI ve ABD perakende satış aynı 13:30Z; XAU 1s +%0,238 ama 4s -%0,773: tek haber-tek yön kuralı reddedilir | Altın tut | $101.52 |
| 19 | 1.470% | +%1,470 UP toparlanması; erken küçük DOWN SAT yanlış olabilirdi | Altın tut | $103.01 |
| 20 | -0.313% | -%0,313 küçük geri çekilme; HOLD | Altın tut | $102.70 |
| 21 | — | Hafta sonu; emir yok | Altın tut | $102.70 |
| 22 | — | Hafta sonu; emir yok | Altın tut | $102.70 |
| 23 | 0.258% | UP/konsolidasyon; HOLD | Altın tut | $102.99 |
| 24 | 0.325% | UP/konsolidasyon; HOLD | Altın tut | $103.31 |
| 25 | 0.459% | Yukarı yön devam; HOLD | Altın tut | $103.79 |
| 26 | -0.877% | GDP +%2,9 ilk tahmin 13:30Z; XAU 4s -%0,559, fakat 5-seans -%3 DOWN yok; HOLD | Altın tut | $102.87 |
| 27 | -0.054% | PCE 13:30Z; XAU 4s -%0,344; HOLD | Altın tut | $102.82 |
| 28 | — | Hafta sonu; emir yok | Altın tut | $102.82 |
| 29 | — | Hafta sonu; emir yok | Altın tut | $102.82 |
| 30 | -0.268% | -%0,268; V0'da işlem tekrar vardı, burada yok; HOLD | Altın tut | $102.53 |
| 31 | 0.283% | 5-seans alt eşik geçişi 2% fakat 3% değil; 13:30Z ECI sonrası 4s +%0,932. Gün sonu kapanış tasfiyesi deney muhasebesi için, DOWN sinyali değil | **Ay-sonu tasfiye** | $101.99 |

## Olay/yön/evre ve GPT kanıt denetimi
- **4 Ocak:** İlk `UP3` teyidi **08:00 UTC = 11:00 TRT**. Alış **08:15 UTC = 11:15 TRT** kapanmış sonraki M15 ASK. Aynı gün **15:00 UTC JOLTS** ve **19:00 UTC FOMC tutanağı** daha sonra geldi; erken AL emrinin nedeni olamaz. Ocak 4 erken Reuters değerlendirmesi doların gevşemesi ve Fed beklentileri bağlamını sağlar, ancak ilk olay için eş-UTC DXY/US yield fiyat paneli doğrulanmış değildir. [BLS takvim](https://www.bls.gov/schedule/2023/01_sched_list.htm), [Fed minutes orijinal sayfa](https://www.federalreserve.gov/monetarypolicy/fomcpresconf20221214.htm).
- **5 Ocak:** -%1,169 NY17 aşağı reaksiyon, orta/büyük maliyet-sonrası DOWN işlemini kanıtlamaz; **HOLD**.
- **6 Ocak NFP** 13:30Z. M15 release öncesi fiyat→+1s **+%0,544** ve +4s **+%1,401**. UP güçlü ama pozisyon zaten altın; ikinci işlem yok. [BLS istihdam](https://www.bls.gov/news.release/archives/empsit_01062023.htm).
- **12 Ocak CPI** 13:30Z, +1s **+%0,258**, +4s **+%0,452**, NY17 +%1,149; kalıcı tek-neden atfetme. [BLS CPI](https://www.bls.gov/news.release/archives/cpi_01122023.htm).
- **13 Ocak** +%1,223 yükseliş devam; haber kaynak tam taraması yapılmadığından belli bir nedeni dayatma.
- **16–18 Ocak:** MLK kısmi işlem, 17 Ocak -%0,599. **18 Ocak 13:30Z PPI ve perakende satış EŞ ZAMANLI** (PPI -%0,5, perakende -%1,1). Altın ilk saat **+%0,238**, dört saat **-%0,773**: ilk tepki ve izleyen fiyat yönü farklı. Yalnız PPI'ye sebep atfetme. [BLS PPI](https://www.bls.gov/news.release/archives/ppi_01182023.htm), [Census satış](https://content.govdelivery.com/accounts/USCENSUS/bulletins/343758c).
- **19 Ocak** +%1,470 geri yükseliş; 17–18 Ocak küçük DOWN nedeniyle nakde çıkışın fırsat maliyetini gösteren karşı-vaka.
- **26 Ocak GDP** 13:30Z Q4 2022 advance +%2,9; +4s XAU **-%0,559**. 27 Ocak PCE +4s **-%0,344**. İkisi de **tek başına %3 DOWN teyidi değildir**; yine de 26–31 aralığı **kısa-vade DOWN/reversal risk araştırması** olarak saklanır. [BEA GDP](https://www.bea.gov/news/2023/gross-domestic-product-fourth-quarter-and-year-2022-advance-estimate), [BEA PCE](https://www.bea.gov/news/2023/personal-income-and-outlays-december-2022).
- **31 Ocak:** Beş-seans as-of fiyat hareketi gün içi **-%2,226** seviyesine gerileyebilir, ancak **-%3 aşağı olay teyidi yoktur**; eşik-%2 alternatif SAT 08:45Z tetiklenip 09:00Z BID vekiliyle uygulansaydı, bu kuralın Ocak NAV'i **101.7000 $** olurdu. Ay sonu **13:30Z ECI** ile XAU +4s **+%0,932**, zamanlama riskini gösterir. **31 Ocak sonundaki SAT sadece deney sonunda kapalı portföy karşılaştırması içindir.** [BLS 2023 takvimi](https://www.bls.gov/schedule/2023/01_sched_list.htm).
- **Şubat ayında yayımlanan WGC geriye dönük gözlem:** Altın +%6,1, global ETF -1,6 milyar USD/26 ton; zayıf USD ve düşen ABD faizleri genel aylık açıklama adayları. **Bu 9 Şubat'taki açıklama 4 Ocak AL girdisi değildir.** [WGC Ocak yorum](https://www.gold.org/goldhub/research/gold-market-commentary-january-2023), [WGC ETF](https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2023/02).

## Kullanılan hedef ve sınırlamalar
**Araştırma hipotezi, önceden ispatlanmış strateji değil:** Mevcut pozisyon CASH ise 15 dakika tamamlanmış MID'in dört önceki tam NY17 seans kapanış MID'ine oranı **≥ +%3** ise UP orta/büyük olay teyidi ve en erken sonraki tamamlanan M15 ASK'dan BUY. GOLD ise aynı oran **≤ -%3** ise en erken sonraki M15 BID'dan SELL. Diğer durumda HOLD; günde en az bir işlem zorunlu değildir. Mevcut seanstan henüz kapanmamış bar veya gelecekteki haber sinyalde yok. İleri fiyatlar sadece gerçekleşen getirinin hesabında. Jan31 NY17 kapanışında tüm açık altın, pasif benchmark'la aynı yöntemle muhasebesel kapanır. **4 seans önceki kapanış bazının ekonomik en iyi pencere olduğu kanıtlanmadı**; bu eşik 2023 Ocak ve sonraki fiyatların zaten görülmüş olduğu ortamda çalıştırıldı.

- Bu fiyat tabanlı %3 **olay teyidi**, hareketten **sonra kalan kısmın** spread+komisyonu karşılayacağını otomatik bilmez. Gerçek olay sistemi için ilk-bariyer `time-to-event`, fiyatın son görülen tepe/dibinden hareketi, olay öncesi/sonrası MFE/MAE, sert DOWN kaçırma ve karşıt ekonomik kaynaklar eklenecek.
- **Bankacılık icrası:** Giriş 11:15 TRT için varsayımsal bankacılık mesaisiyle uyumlu olsa bile **ay sonu 22:00Z=01:00 TRT** kapanışı gerçek banka alım/satımı değildir. Yalnız **09–17 Türkiye teorik bankacılık** kısıtı eklenip 31 Ocak 17:00 TRT'ye işaretlenen aynı giriş/çıkış fiyatında %3 strateji **101.5696 $** olur; bu **başka bitiş saatidir**, V0/buyhold 22:00Z kıyasıyla birbirine karıştırılmaz.
- Makro fiyat çevresi çalışması M15 release öncesi MID ve t+1h/t+4h MID'dir; başka eş-saatli USD/UST/metal/ETF/COT tam paneli bağlanmadığından **neden-sonuç kesin değildir**. Gösterilen kaynaklar seçili ilk yayımlar; **her gün tüm haberler tarandı iddiası yoktur.**
- **Önceki 2026 Ocak V4** 2024 12 DOWN olayından sıfır alarm sonucu yüzünden doğrulanmış şok politikası değildir. Yeni fiyat %3 örneği onun başarılı halefi ilan edilemez.
- **Bu deney GPT+ekonomik olay yorumunun ticari etkisini SAYISAL test etmez**; GPT bu raporda karşıt kanıtları kaynakla ayırmıştır. Karar formülü yalnız fiyat kuralıdır. Test edilmemiş hipotezler Şubat'a doğrulanmış algoritma olarak aktarılmaz.

**Üretilebilir kanıt bağlantıları:** [31 günlük karar/NAV CSV](JAN_2023_EVENT3_31DAY_ACTIONS_NAV_20261014.csv) ve [özet parametre/sonuç JSON](JAN_2023_EVENT3_EXPLORATORY_RESULTS_20261014.json). Önceki `JAN_2023_FULL_MONTH_GPT_ONLY_SCIENTIFIC_AUDIT.md` V0 deneyini değiştirmeden korur.
