# 2027 Üst Ürün Grubuna Göre Üretim Optimizasyonu — 30.10.2026

## Karar ve koruma
Şönt / Harmonik üretim ayları ayrı kalır. 133 ürün, **45.088 adet**, **175 üretim partisi**, ürün bazında yıllık adet ve parti sayısı korunur.
Önerilen üretim takvimi `plan2027-upper-groups-data.js` dosyasındadır; ürün kimlikleri `data-packed.js` üzerinden doğrulanır. Kullanıcının tarayıcıya kaydettiği plan **otomatik değiştirilmez**. `Üst grup planını uygula` ile önce kurtarma kaydı alınır, sonra yeni takvim aktif olur; `Önceki plana dön` ile eski takvim geri gelir.

## Gruplar
- **Şönt:** SVC-R (5 ürün), SRM (8 ürün), SRT (12 ürün).
- **Harmonik:** HRM (10 ürün), HRT 5,67 (16), HRT 7/8 (18), HRT 7/7 (11), HRT 14 (9), HRT-G varyant (14), HRT-GG varyant (15), Özel Harmonik (15).
- Üst grup anahtarı ürünün katalog kaynaklı `model`, `altGrup` ve `kod` alanlarından türetilir. İkincil G1/G2 renk etiketleri **ay döngüsünü** ifade eder, üst ürün grubunu değil.
- Liste varsayılan olarak Ürün ailesi → Üst grup → ilk üretim ayı → üretim döngüsü şeklinde sıralanır. Kullanıcının kendi satır sırası silinmez; `Üst gruba göre sırala` ile isteğe bağlı yeniden sıralanır.
- Ay detayındaki eski teknik/kaynak alanlarının tamamı korunur; yeni `Üst ürün grubu` sütunuyla **41 sütun** vardır.

## Optimizasyon
Referans: 30.10.2026 tarihli onaylanan `Sont_Harmonik_2027_Bobin_Yuku_Optimize_Oneri_20261030.xlsx` (133 ürün, 45.088 adet). Önce ürün başına **mevcut 1–4 üretim partisi sayısı** korunarak, yalnız aynı ürün ailesine tahsisli aylardan alternatif üretim desenleri üretildi. 4 partili Şönt ürünlerinin ayları çeyrek dönemli tutuldu; 2 partililer uygun aralıklarla dağıtıldı. 1–3 bobin belirsizlik senaryoları için ayrı aylık yük kısıtları uygulanarak karma tamsayılı optimizasyon yapıldı. Amaç, aynı üst grubun yıl boyunca aktif olduğu farklı ayların sayısını azaltmak ve hesaplanan bobin yükünü dengelemekti.

### Grupların farklı aylara dağılması
| Gösterge | Referans plan | Üst grup önerisi |
|---|---:|---:|
| Şönt üst grup-ay eşleşmesi | 24 | **18** |
| Harmonik üst grup-ay eşleşmesi | 31 | **16** |
| **Toplam** | **55** | **34** |
| Ürünlerin değişen ay deseni | — | **68** |
| Yıllık toplam adet | 45.088 | 45.088 |
| Toplam üretim partisi | 175 | 175 |

*Bu eşleşme sayıları makine hazırlık süresi veya gerçek setup sayısı değildir; sadece kaç ayrı ayda ilgili üst grup üretiminin bulunduğunu gösterir.*

### Yeni aylık üretim
| Ay | Aile | Yeni adet | 2B senaryosu bobin eşdeğeri |
|---|---|---:|---:|
| Ocak | Şönt | 3.895 | 4.953 |
| Şubat | Şönt | 4.856 | 4.856 |
| Mart | Harmonik | 2.203 | 6.343 |
| Nisan | Şönt | 4.257 | 4.981 |
| Mayıs | Şönt | 4.909 | 4.909 |
| Haziran | Harmonik | 2.409 | 6.381 |
| Temmuz | Şönt | 3.902 | 4.976 |
| Ağustos | Şönt | 4.949 | 4.949 |
| Eylül | Harmonik | 2.190 | 6.338 |
| Ekim | Şönt | 4.121 | 4.931 |
| Kasım | Şönt | 4.883 | 4.883 |
| Aralık | Harmonik | 2.514 | 6.360 |

*Uyarı: Yukarıdaki Şönt 2B değerleri görsel özet amacıyla değil, son hesap algoritmasının çıktısı olarak ayrıca test edilmeli; gerçek karşılaştırma için optimize veri setini ve 1/2/3B senaryo kontrollerini esas alın.*

### Bobin belirsizliği ve riskler
90 ürün için 1B/3B elektriksel yol ön değerlendirmesi, 43 ürün için bilinmeyen bobin adedi vardır (Şönt 2; Harmonik 41). Bilinmeyenlerin 1/2/3B olması ayrı senaryolardır, kesin fiziksel bobin sayısı değildir.

| Senaryo | Şönt aylık min–maks | Harmonik aylık min–maks |
|---|---|---|
| Bilinmeyenler 1B | 4.769–4.976 | 6.040–6.161 |
| Bilinmeyenler 2B | 4.856–4.981 | 6.338–6.381 |
| Bilinmeyenler 3B | 4.856–5.093 | 6.570–6.680 |

Fiziksel bobin sayısı, izolasyon sarım adımları, tel/folyo seçimi, sarım çevrim süresi ve makine setup süreleri onaylı BOM ve operasyon talimatlarından doğrulanmadığı için bu yalnızca **grup/elektriksel sargı eşdeğeri** optimizasyonudur; makine yatırımı için kesin kapasite onayı değildir.
