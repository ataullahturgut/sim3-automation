# V37 — Altın %4+ düşüşlerinde XAU 4 saat + diğer metaller + GVZ / faiz

**30 Ekim 2026 — geçmişe dönük araştırma; CANLI SİNYAL DEĞİL.** Orijinal BASE14/CFTC21/V22 değişmedi, AL/SAT yok.

## Gerçek veri kapsamı

- **Altın (XAU/USD):** 15 dakikalık HistData fiyat barları; 2024–2025 eşik öğrenme, 2026 Ocak–Eylül değerlendirme. Dört saatlik altın düşüşü bu fiyatlardan çıkarıldı.
- **Gümüş, platin, paladyum:** StakTrakr aynı kaynak günlük fiyatlar; 2024–2025 araştırma kayıtları, 2026 kayıtlarının tamamı 30 Ekim'de geriye dönük alınmış. Saatlik veya dakikalık eşzamanlı üç metal geçmişi **doğrulanmadı**.
- **GVZ:** 2024–2025 FRED aynası + 2026 Cboe günlük. 2026 Mayıs sonu bazı günler eksik.
- **ABD 10 yıllık faiz:** DGS10 FRB H.15 günlük, geriye dönük araştırma. 
- **DXY:** Doğrulanmış veri serisi bulunamadı; yeni testte kullanılmadı. CFTC/COT yalnızca orijinal V22 kapsamında ve gerçek haftalık yayımlanma penceresiyle geçerlidir.

## Donmuş öğrenme ve koşullar

- Hedef: bir günün XAU fiyatından sonraki **5 fiyat işlem gününde en az %4** düşüş (birbiriyle örtüşebilen gün etiketleri).
- 2024–2025 HistData'nın en kötü günlük 4-saat getiri dağılımının alt %5'i: **−%1,7952**.
- 2024–2025 StakTrakr üç metalin geçmiş yüzdelik eşikleri (**en kötü %10**):

| Metal | 1 iş günü | 5 iş günü |
|---|---:|---:|
| XAG | −%1,8951 | −%3,7968 |
| XPT | −%1,8227 | −%3,9717 |
| XPD | −%2,5806 | −%5,3941 |

- **Metal bağlamlı yeni aday:** V22 uyarısı varsa koru; V22 yoksa XAU'nun 4-saat kaybı eğitim alt %5 eşik altındaysa ve **önceki 4 işlem günündeki** üç metalin en az biri 1-gün veya 5-gün alt %10 eşik altına girdiyse ayrı araştırma uyarısı üret.
- GVZ/10Y bağlamında 2024–2025 üst %10 makro eşikleri, **en az iki işlem günü geriden** kullanıldı. Önceki metal fiyatı en erken bir işlem günü gecikmeli görüldü; aynı gün sonradan kapanmış fiyatı saatler öncesine geri taşınmadı.

## 2026 ortak karşılaştırma

**Örneklem:** 187 tamamlanmış ve ortak fiyat günü; bunların 35'inde sonraki 5 günde −%4 eşiği görüldü. Bunlar 35 bağımsız ekonomik düşüş değildir.

| Koşul | Uyarı günü | Gelecek %4 ile eşleşen | Sonuçsuz uyarı günü |
|---|---:|---:|---:|
| V22 orijinal | 42 | 14 | **28** |
| V22 veya yalın 4 saat | 55 | 16 | **39** |
| V22 veya (4 saat ve önceki 3 metal zayıflığı) | **52** | **16** | **36** |
| V22 veya (4 saat ve GVZ / faiz bağlamı) | 50 | 15 | **35** |
| V22 veya (4 saat ve metal ya da makro) | 55 | 16 | **39** |

**Büyük düşüş dönemleri:** İlk 10 işlem günlük uyarı tanımıyla V22 **5/8**, V22+4 saat **7/8**, metal bağlamı eklenen birleşim de **7/8**. İki yeni aday:

- **27 Mayıs:** XAU dört saatte −%1,897; daha önceki metal zayıflığıyla birlikte, Haziran ilk %8,08 düşüş dönemi başlamadan **4 işlem günü önce**.
- **16 Eylül:** XAU dört saatte −%2,309; metal 5g zayıflığı, Eylül sonu %4,49 düşüş dönemi başlamadan **3 işlem günü önce**.
- **Mayıs −%4,11:** Öncesinde dört saat eşik koşulu gerçekleşmedi; bu olay halen önceden uyarılmamış.

**Yorum:** Üç metal bağlamı, V22+yalın 4 saate kıyasla 3 adet sonuçsuz uyarı **gününü** eliyor, iki yeni düşüş dönemi korunuyor. Ancak V22'nin 28 sonuçsuz uyarı gününe göre hala **8 fazla**. GVZ/faiz katmanı bu araştırmada hem yeni iki düşüş dönemini koruyup hem yanlış alarmları azaltmayı başaramadı. Yeni modelin üstünlüğü kanıtlanmış değil.

## Bilimsel sınır ve yayın koşulu

1. Dört metalin **dördünde birden 4-saatlik veri yok**; yalnızca XAU 4-saat + üç diğer metalin **günlük** teyidi test edildi.
2. 2026 StakTrakr dört-metal verilerinin ilk kullanım zamanı kanıtlanmıyor: kaynakların bir kısmı 30 Ekim'de geriye dönük indirildi. Bu çalışma tarihsel replay'dir.
3. 2026 daha önce araştırılmış olduğu için seçeneklerin seçimi açısından **2026 kör test değil**. Eşikleri 2024–2025'te kalibre etmek tek başına bilimsel bağımsızlık sağlamaz.
4. HistData, StakTrakr ve günlük model fiyat tanımları ile timezone ve firstprint zamanı eşit değil; gerçek zamana uygun canlı alarm sertifikasyonu yapılmadı.
5. Uyarı günü eşleşmesi ekonomik bağımsız alarm/olay sayısı değil. Canlı iyileştirme kararı için ileri tarihli gerçek firstprint, alarm epizotları, yanlış alarm yükü ve dört metal intraday veri gerekir.
6. Mevcut V22/BASE14/CFTC21 üretim sinyalleri değiştirilmedi, Neon'a yeni sinyal kaydı eklenmedi, al-sat çalışılmadı.

**Tekrar üretim:** risk_v37_multimetal_macro_intraday_shadow_v1.py, test_risk_v37_multimetal_macro_intraday_shadow_v1.py ve gold-v37-multimetal-macro-intraday-shadow.yml. Neon sorguları read-only; JSON artefaktı araştırma sonuçlarını içerir. CI gerçekten başarıyla bitmeden bu kaynakları doğrulanmış üretim sistemi saymayın.
