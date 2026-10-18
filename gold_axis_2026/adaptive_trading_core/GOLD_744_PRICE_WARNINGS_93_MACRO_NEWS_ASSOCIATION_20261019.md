# 2023–2025: 744 altın düşüş alarmı × 93 GERÇEK TARİHLİ makro haber

**19 Ekim 2026. GOLD-ADAPTIVE-MODEL-APP-01. Tam fiyat arşivi tarandı; ilk haber nedenselliği kanıtlanmadı.**

## Kullanıcının talebi ve sayım birimi

744 alarm **haber değil**: Gerçek XAU/USD `gold_research_evduka_xau15m_bidask_candidate` kaynağından 2023–2025 **70.915 M15** kapanmış MID barına, `downside_news_onset_v1.js` gözlem kurallarıyla uygulanan **ilk ≥%0,5 gerileme/gap başlangıcı** gözlem sayısıdır. Eski fiyat-only replay ile karşılaştırmada **744/744 alarm**, 6 gap-down dahil, SQL denetiminde yeniden üretildi.

Haber evreni: Neon `gold_research_r72_claude_macro_analogs_v1`, 2023–2025 **93 ayrı tarihli ABD ekonomik açıklama satırı**: **34 CPI, 35 NFP, 24 FOMC**. Önceki `OLAY_02_85_MAKRO_YENI_DNA_TEPKI_PLASEBO_20261014.csv` 85 kayıt (34 CPI, 35 NFP, 16 FOMC) içeriyordu; Neon'a bakıldığında ilave 8 FOMC satırı var. Tarih/saatleri araştırmada olay-saati vekilidir: özgün ilk yayımlanma sürümü/vintage, Reuters zaman damgası ya da olayları gören kullanıcının bilgi erişim saati **bağımsız sertifikalı DEĞİL**. Haber gerçekleşmiş *actual vs consensus* değeri S1'e beslenmedi.

**KAPSAM ÖNEMLİ:** Bu araştırma **93 tarihli makro haberin tamamını 744 alarma eşleştiriyor, 2023–2025 dünyadaki bütün haberleri değil**. Jeopolitik, tarife, Çin/ECB/BoE, merkez bankası altın alımı, ETF, marjin, fizikî/OTC ve münferit medya haberlerinin tamamı bu 93 satırda yoktur. `NO_MACRO_24H` hiçbir haber gelmedi demek değildir.

## 1. Alarmın önceki saatlerinde CPI/NFP/FOMC haberi var mı?

| Alarmla haber zamanı | İlgili alarm sayısı | Sonraki 480 gözlenmiş M15 bardaki ≥%4 ilave düşüş | Gözlemlenmiş koşullu oran |
|---|---:|---:|---:|
| Son 4 saatte CPI/NFP/FOMC | **57** | **0/57** | **%0,00** |
| Son 24 saatte CPI/NFP/FOMC | **109** | **6/109** | **%5,50** |
| Son 72 saatte CPI/NFP/FOMC | **187** | **10/187** | **%5,35** |
| Son 24 saatte bu üç tip makro haber YOK | **635** | **51/628** (7 sonuca henüz erişemedi) | **%8,12** |
| **Bütün 744 alarm** | **744** | **57/737** (7 sonuca henüz erişemedi) | **%7,73** |

**Makro haberi görüp bir alarm üretmek** ile **haber büyük düşüşü önceden öngörüyor** farklı şeydir. 57/57 dört saatlik haber-öncelikli alarmın hiçbirinin ardındaki aynı yaklaşık ufukta yeni −%4 düşüş yok: bu sonuç yalnız bu arşiv ve sabit gözlem tanımı için geçerlidir. 24 saatte makro eşleşme oranı %5,50 ile haber eşleşmeyenlerin %8,12'sinden **daha iyi değil**; ancak bağımlı/örtüşen gözlemler ve başka haber eksikleri sebebiyle nedensel karşılaştırma sayılmaz.

`480` yalnız **480 daha sonra kaydedilmiş M15 bar**, 5 kesin borsa seansı veya her zaman 5 takvim günü değildir. Sonraki hareket yalnız değerlendirme etiketidir; karar anında **kesinlikle bilinemez**. Yüzde dört sonuç önceden seçilmiş büyük düşüş bacağına değil, *alarm fiyatına göre gelecekteki yeni −%4 minimum fiyat* ölçüsüne dayanır.

## 2. Haber türleri ayrı ne yapıyor?

| Alarmdan önceki 24s içindeki makro tip | Alarmlar | Sonraki yeni −%4 |
|---|---:|---:|
| CPI | **43** | **3/43 (%6,98)** |
| FOMC | **41** | **3/41 (%7,32)** |
| NFP | **28** | **0/28 (%0,00)** |

43+41+28 toplamının 109'dan büyük olması **aynı alarmın 24s içinde birden fazla açıklama** görmesinden kaynaklanır; bu üç alt grup birbirini dışlamaz.

**Haberden alarma tersten bakarsak:** 34 CPI'den 21'i / 24s içinde 26'sı, 35 NFP'den 21'i / 24s içinde 22'si, 24 FOMC'den 9'u / 24s içinde 22'si bir fiyat-zayıflama alarmından **önce** oluşmuş. Şöyle okumalıyız: “CPI sonrası 4s alarm var” **21/34** ve CPI sonrası 24s alarm var **26/34**; bu alarmın mutlaka sürdürülebilir satış veya haber kaynaklı fiyat etkisi olduğu anlamına gelmez. Fiyat alarmının öncesinde değil sonrasında gelecek makro haber 744 içinden **79** alarmda 24 saat içinde yer almış; bu 79 haber **alarm anındaki modelin girdisi olamaz**.

## 3. 2023, 2024, 2025 farkı

| Yıl | Bütün fiyat-zayıflama alarmları | Sonraki −%4 görülen | Öncesinde 24s makro haber olan alarm | Bu alt grupta −%4 |
|---|---:|---:|---:|---:|
| **2023** | **219** | **5** | **33** | **1** |
| **2024** | **237** | **11** | **44** | **3** |
| **2025** | **288** | **41** | **32** | **2** |

2025'te −%4 sonuçlarının çok büyük kısmı tarife/jeopolitik/akım çözülmesi gibi ekonomi olayları açısından ayrıca araştırılmalı; **“geri kalanlarda haber yok” diye yorumlanmamalı**. Yalnız makro *tür* takvimi bu dönemde yeterli değildir.

## 4. OLAY–ÖĞREN–ETKİ üzerinden mekanizma yorumu

- `K CPI/NFP/FOMC actual vs consensus` — özgün konsensüs vintage sertifikalı değilse habere `K02,K03,K20...` “o an kesin sürpriz” etiketi **atamayız**. Şimdiki eşleşme sadece olayın tarihte duyurulduğunu kontrol ediyor.
- `ORG01/02` faiz/USD aktarımı, `ORG03/04` güvenli liman, `ORG06/07` tarife, `ORG08/12` nakit/fonlama, `ORG10` pozisyon çözülmesi **araştırma mekanizması adaylarıdır**; bugünkü 744 eşleşmesinde gerçek DXY/gerçek reel yield/OI bağlanmadı ve mekanizma yönünü açıklamaya yetmez.
- 17 geçmiş büyük ana düşüş için [ilk haber saatli olay kronolojisi](../ETKI_05_17_BUYUK_DUSUS_ILK_HABER_TAM_ZAMAN_ARASTIRMASI_20261018.md) var. Örneğin 3 Şubat 2023 ABD istihdamı seçilmiş düşüş bacağı başladıktan sonra geldi; 2025 Aralık CME kararının 29 Aralık sert satışından önceki resmî takvimi ayrı, bu 93 makro saatinden **BAĞIMSIZ**. Bunları otomatik CPI/NFP/FOMC kapsamında saymak yanlış olur.
- “Haber düşüşü başlattı mı?” bilim kapısı `t_original_release_first_access <= t_first_new_price_weakness`, ilk bar tepkisi, rakip haberler ve olmadığında kontrol. Fiyat daha önce düştüyse sonraki haber **başlatıcı değil**, olası `ACCELERANT`dır.
- Araştırma sonucu: **Sadece CPI/NFP/FOMC öncelik bilgisi**, 744 zayıflama alarmından gelecekteki büyük düşüşleri diğer uyarılara kıyasla güvenilir biçimde filtreleyemedi. “Haber analizi gereksiz” ya da “bütün 744 alarmı haberlerle açıkladık” anlamına GELMEZ.

## 5. Üretim ve yeniden çalıştırma durumu

[**Tek SELECT ile alarm alarm 744 satırın tamamını yeniden üreten SQL**](adaptive_trading_core/gold_744_down_alert_vs_macro_clock_v1.sql) GitHub'da yer alır: `alarm_utc,macro_before_4h,macro_before_24h,macro_before_72h,macro_after_24h_FUTURE_LABEL_ONLY, new_4pct_fall_in_next_480_observed_M15_FUTURE_LABEL_ONLY`. Neon sorgu sonuçları 744 alarm ve 6 gap alert doğruladı; 93 macro event tür kontrolü ve 24/4/72 saat agregasyonları da veritabanı üzerinde çalıştırıldı.

Bu ilk tablolarda **CANLI haber API/otomatik Reuters ingest yok**, **ilk haber 2023–2025 tüm olaylar seviyesinde kaynak sertifikasyonu eksik**, **S1/S2/S3 emir modeli değiştirilmedi**, **gerçek AL/SAT veya banka maliyeti sonrası getiri başarısı yok**. Bir sonraki bilim adımı haber evrenine ekonomik olayların gerçek ilk yayım zamanı (tarife, savaş, CME, merkez bankası altın akımı) ile negatif/pozitif/olaysız matched kontrolleri eklemek, ardından 2023–2025 geçmişten geleceğe öğrenmede **yalnız yeni görülen** bilgileri kullanmaktır.
