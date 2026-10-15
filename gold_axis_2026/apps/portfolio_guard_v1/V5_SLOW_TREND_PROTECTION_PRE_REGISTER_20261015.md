# V5 — Uzun vadeli risk ve trend koruyucusu, önceden yazılmış hipotez

**Statü: hipotez kaydı ve deney spesifikasyonu; kesin kâr modeli DEĞİL.** V4'ün Şubat–Eylül 2026 sıralı deneyinde Eylül sonunda 96,706968 USD (başlangıç 119,753917) ile başarısız olduğu görüldükten sonra kaydedildi. V5 tasarımı 2026 Mart–Eylül gidişini **görmüş** olduğundan aynı 2026 dönemini kör OOS kanıtı kabul etmek YASAK.

## V4 hata hipotezi
Mart 2026'da iki koruyucu satış ve üç giriş yaptı, 31 Mart 09:00 Türkiye'deki alımdan sonra Eylül sonuna kadar bir daha satmadı. 15m/3h kısa sinyal evreleri geçici olarak düzeldiğinde finansal durum uzun düşüşe dönerken 5–20 işlem günü riski izlenmedi. V4'te fiyatın geçmişten görülen pikten düşmesi (drawdown) tek başına satış yaptırmıyor; yalnız kısa 3h/92 bar r4/r92 kuralı ile kombinleniyor.

## Kontrol ailesi, sınama başlamadan SABİT
1. Yavaş trend, geçmiş tamamlanmış 3 saatlik 40 ve 120 gözlem EMA'sı ile ölçülür (yaklaşık bir/üç işlem haftası; süre takvim gözlemi değil işlem kesiti sayısıdır). Gelecekteki fiyat yok.
2. V4 durum tanıma modülü korunur: CAPITULATION/FALLING/STABILIZING/RECOVERY/UP_TREND/FAILED_REBOUND/UNKNOWN. Yatırım kararı geçmiş V4 olay DNA benzerliği oranına olasılık demez.
3. AL yalnız 2 üst üste teyit; toparlanma ilk evresinde portföyün en fazla %50'si; pozitif hızlı-yavaş EMA ilişkisi ve pozitif V4 trend bilgisi olmadıkça tam altın pozisyonuna geçme.
4. GOLD'da TUT varsayılandır. İki banka kararında arka arkaya yavaş trend bozumu (`price<EMA120*0.985`, `EMA40<EMA120`, `r276<-1`) veya geçmiş alım sonrası tepeden en az %7,5 düşüş + `price<EMA40` + `r276<0` şartı sağlanırsa **koruyucu SAT**. Aşırı shock (`r4<=-3.5`, `r92<=-3`, yüksek RV) istisnai aynı karar anında SAT. Kural eşikleri 2026 sonucuna göre değiştirilmez.
5. Alımdan sonraki kısa normal gürültü için 24 saat bekleme; ciddi şokta bu bekleme geçersiz. Satış sonrası 24 saat yeniden AL kilidi. %0,8 alış + %0,8 satış komisyonu; gerçek banka kotasyonu/spread/slip henüz bilinmiyor.
6. 2020–2022 geçmiş asof M15→3h gözlemleriyle 2023, daha önceki gözlemlerle 2024, aynı şekilde 2025 tarihli karşılaştırma. 2023 fiyat kapsamı eksik. 2026 Şubat–Eylül sadece stres vakası ve kuralın işleyiş denetimi. Sonuç iyiyse yalnız başka/ileriki bağımsız gerçek veride doğrulama mümkün.
7. Tek portföy: Şubat 1 2026 başında Ocak V1'den 119,753917 USD NAKİT; pozisyon ve maliyet her ay kesintisiz devreder. 09/12/15 TR saatleri dışında emir yok. Son açık altın teorik satış komisyonuyla değerlenir. Karşılaştırmalar V4 frozen, nakit bekleme, 2 Şubat 09:00 AL/TUT ve V3 Şubat.
8. Başarı yalnız tek dönem final USD değil; max drawdown, aylık gerileme, portföy korunması, agresif düşüş kaçırma, yanlış risk satışları, kaçan UP, tur maliyeti, bankaya uygun saatler ve OOD belirsizliği de değerlendirilecek.

## Bilimsel kabul kararı
2025 güçlü altın yükselişini öldürmeden birden çok düşük/trend rejiminde V4 ve nakit ile tutma stratejilerine sağlam maliyet-sonrası kıyas üretmedikçe yeni model V1 yerine konamaz. Mart–Eylül 2026 sonucu V5 tasarımı için bilgi olduğundan bu dönemde kâr etmesi başarı kanıtı olmayacaktır. Eksik makro haberlere ve G05-C/G06-B ekonomik nedenlere kesin tanı atanmaz (UNRESOLVED).
