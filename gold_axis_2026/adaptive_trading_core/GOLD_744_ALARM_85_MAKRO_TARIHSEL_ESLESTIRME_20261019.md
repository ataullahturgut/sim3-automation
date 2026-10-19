# 2023–2025: 744 ilk fiyat zayıflama alarmı ve 85 tarihli makro açıklama

**19 Ekim 2026 · OLAY-02 × ETKİ-05 × native fiyat erken-uyarı gözlemcisi**

## Kullanıcının istediği sorunun ilk sayısal cevabı

Üç yılın **70.915 gerçek XAU/USD BID/ASK 15 dakikalık fiyat kaydındaki 744 ilk-zayıflama alarmı**, OLAY-02'nin **85 tarihli ABD CPI/NFP/FOMC ekonomik açıklaması** ile **gerçek zaman sırası** kullanılarak eşleştirildi. 85 duyurunun 34'ü CPI, 35'i NFP, 16'sı FOMC. **Özgün 2023–25 açıklama ilk-baskısının kaynak UTC vintage sertifikası 0/85**. Bu çalışmada arşivdeki duyuru saati kronolojik işaret olarak kullanıldı, üretim/ticaret kanıtı değildir.

| Alarmın öncesindeki arşiv açıklaması | Alarm | İleri sonuç ölçülebilen | Sonraki 480 gözlenmiş M15 içinde ≥%4 fiyat düşüşü | Oran |
|---|---:|---:|---:|---:|
| **Hiç ayrım yapmadan tüm fiyat alarmları** | 744 | 737 | 57 | **%7,73** |
| **Önceki 4 saat içerisinde CPI/NFP/FOMC** | 54 | 54 | 0 | **%0,00** |
| **Önceki 24 saat içerisinde CPI/NFP/FOMC** | 95 | 95 | 5 | **%5,26** |
| **Önceki 72 saat içerisinde CPI/NFP/FOMC** | 164 | 164 | 6 | **%3,66** |
| **Önceki 24 saatte bu üç tür haber yok** | 649 | 642 | 52 | **%8,10** |
| **İzleyen 24 saat içinde bu üç tür haber geliyor** | 68 | 68 | 7 | **%10,29** |

Bu gruplar **iç içe geçebilir**: 4s haberi olan alarm 24s ve 72s içine de girer. Gelecek 24s haberlerinin sayısı gelecekteki bilgidir, **alarm anında tahmin girdisi olamaz**. Forward 480 M15 **gözlenmiş vendor barı**dır; tatil/hafta sonları nedeniyle tam beş iş günü anlamına gelmeyebilir.

### Makro açıklama grubuna göre — önceki 24 saatte yayın

| Tür | Eşleşen alarm | İleri ≥%4 düşüş | Oran |
|---|---:|---:|---:|
| **CPI** | 43 | 3 | %6,98 |
| **NFP** | 28 | 0 | %0,00 |
| **FOMC** | 27 | 2 | %7,41 |

Bir alarm aynı 24 saatte birden fazla açıklama içeriyorsa tür satırları ayrı ayrı sayılabilir; toplamları 95'e eşit olmak zorunda değildir.

### Yıllar arası rejim duyarlılığı

| Yıl | Toplam fiyat alarmı | Sonraki ≥%4 düşüş | Önceki 24s CPI/NFP/FOMC alarmı | Bunlardan ≥%4 |
|---|---:|---:|---:|---:|
| 2023 | 219 | 5 | 33 | 1 |
| 2024 | 237 | 11 | 44 | 3 |
| 2025 | 288 | 41 | 18 | 1 |

**2025 çok farklı rejimdir**: 2023'te 219 alarmdan 5'inin, 2025'te 288 alarmdan 41'inin ardından yüzde dört yeni düşüş görünmektedir. Rejim farkı basit haber/fiyat koşullarını aynı kaba başarı oranına indirmemeyi gerektirir.

### Beş erken haber-sonrası büyük düşüş alarmı

Önceki 24s CPI/NFP/FOMC eşiğini karşılayan ve ileride ≥%4 düşüş içeren **5 fiyat alarmı** sayıldı; bunlar büyük hareketlerin **5 bağımsız başlangıcı değildir**. Bunlar özellikle 1–2 Şubat 2023 FOMC çevresi ve 2024 sonundaki birkaç enflasyon/Fed dönemi gibi kümelerde bulunabilir. Haber–fiyat ilişkisinin *nedensel başlatıcı mı, hızlandırıcı mı, tesadüfi mi* olduğu kanıtlanmamıştır.

Arşivdeki 85 ayrı makro duyurunun **63'ünden sonraki 24 saatte en az bir %0,5 fiyat zayıflama alarmı** vardı, **22'sinden sonra yoktu**. **4 duyurunun** ardından 24s içindeki en az bir fiyat alarmı daha sonra ≥%4 gerileme etiketine ulaştı; aynı makro duyurudan birden çok alarm olabilir.

## Bilimsel cevap ve sonraki eylem

**Buradan 'haberden büyük düşüşü tahmin eden kural bulundu' sonucu ÇIKMADI.** Haber tarihinden sonra %0,5 ilk zayıflamaya geçiş yaygın; 95 haber-öncüllü fiyat alarmının sadece 5'i izleyen yaklaşık 480 görülen M15 barlık ufukta -%4'e ilerledi. Daha da önemlisi, 85 açıklama **sadece CPI, NFP, FOMC**; tarife anlaşmaları, savaşlar, jeopolitik, merkez bankası rezerv alımı, likidite/teminat artışı, WGC raporları, ETF/OI, ekonomi siyaset haberleri topluca dahil edilmedi. **649 alarmın öncesinde bu üç sınıftan bir haber bulunmaması "649 alarmsuz/habersiz" değildir**.

**Arşiv ilk-baskı ve özgün piyasa beklenti vintage'ı 0/85 sertifikalı:** tarih-saatler retrospektif planlı açıklama referansı, daha önce gerçekten ilk kim tarafından ne zaman görüldüğünün maddi kanıtı değildir. Ekonomik kodu kesin K/ORG tetikleyicisi olarak canlı S1'e verilmedi.

**Kuralı ileri geçirmeden önce:** OLAY-02'nin 17 büyük DOWN bacağının başında **ilk gerçek haber/ilk fiyat zayıflaması**, CPI/NFP dışındaki kaynakların resmî ilk yayın tarihi ve saati, yeniden yayımlanan yorumlar, ve olaysız matched dönemler bağlanmalıdır. S1/S2/S3 işlem emirleri bu deneyle değiştirilmedi. %0,8 alış + %0,8 satış maliyetleri nedeniyle alarm=SAT demek doğru değil.
