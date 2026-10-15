# V6 — Ekonomik aktarım sinyali yarar testi: ön kayıt

**2026-10-15.** Bu tasarım ve veri yolları sonuçlar hesaplanmadan yazılmıştır. Analiz salt okunur risk tahmin deneyi; gerçek banka emri, kurumsal ekonomik haber nedensellik analizi veya otomatik AL/SAT değil.

## Hipotez ve bilimsel sınır
Ekonomik OLAY-02/ÖĞREN-03 DNA'sı (G01 faiz-dolar, G05 likidite, G06 çözülme) doğrulanmış ilk haber ve kaynak ilk-yayın-zamanı bulunmadıkça sadece **olası neden**; işlem girdisi değildir. CME vadeli NQ (risk iştahı vekili), ZN (tahvil fiyatı vekili; **faiz getirisi değil**), CL (petrol şok vekili) altın kriz riski sınıflandırmasına fayda sağlayabilir. Test bilinmeyen 24 saatte altının en az **%2 düşmesi** etiketine odaklanır. Bu hedef banka çift yön %1,6 maliyeti aşabilecek hareketlerle ilgilidir ama tek başına işlemin kârlı olması anlamına gelmez.

## Dondurulmuş karşılaştırma
- Birim her **işlem günü Türkiye 09:00** (UTC06:00) karar zamanı. Tek gün 3 karar noktasından 3 bağımsız olay türetilmez. Fiyat 3h as-of satırında 09:00 kapanışa denk gelen önceki XAU M15 verisidir, işlem vekili takip eden barın açılışıdır.
- Label: gözlem anından sonraki 24 saat içerisinde, sonraki en az 5 tamamlanmış üç saatlik XAU kapanışından **en düşük değer** 09:00 gözlem kapanışının <=%98'i ise `DOWN_2PCT_24H=1`, aksi `0`. Gelecekte en az 21h sonrasına uzanan fiyat kaydı bulunmayan gün haftasonu/kapanış sebebiyle değerlendirilmez. Label yalnız sonucu 24h sonra olgunlaştırır; karara girmez.
- Predictor A (kontrol): XAU tamamlanmış `r4`,`r92`,`r276`,`rv`,`ds` (hiçbir haber veya future label yok). Predictor B: aynı 5 XAU alanı + NQ 1h/6h, ZN 1h/6h, CL 1h/6h return; bu serilerde yalnız karar saatinden **en az 1 saat önce açılmış, karar saatinde bitmiş bar** kullanılır. Bir varlık o saat işleme açıksa ve 1h/6h geçmişi varsa örnek B için kabul edilir; **eksikliği sıfır doldurma yok**. A ve B aynı tam-veri günlerinde hesaplanır; seleksiyon şeffaf.
- Lojistik regresyon: sabit L2 ile saf JS gradient descent, eğitim verisine özgü standardizasyon (medyan/standart sapma değil, eğitim mean/std), 0'dan başlangıç; 400 iterasyon, sabit learning rate 0.03, penalty 0.1, intercept cezasız. 2024 için yalnız 2023, 2025 için 2023–24; 2026 için 2023–25 eğitim. Eğitimde test yılına yakın son **96 saatin etiketleri** dışlanır.
- Ana karşılaştırma: saf eğitim prevalansı sabit olasılık tahminine karşı Brier ve logloss; XAU-only vs XAU+cross. 2024 ve 2025 hem Brier hem logloss iyileşmesi; yeterli bağımsız günlük >=10 pozitif test ve >=10 negatif; örnek en az 100/gün yıl bazında; 2026 retrospektif stres destekleyici. 2023 fiyat kapsaması eksik; model kalibrasyonuna güven azaltır.
- Ek hata denetimi: 24h etiket prevalansı, örnek sayısı, bağımsız pozitif gün sayısı, 95% blok bootstrap belirsizliği (korelasyon günlük); gerçek banka komisyon, MID fiyat serileri, alım satım gecikmesi. Bu analiz salt sınıflandırma; **alım-satım getiri vaat etmez**.
- Tamamen yeni otomatik işlem modeline geçiş için: bağımsız ileriki aylar, tarih damgalı Fed/CPI/NFP ilk yayınları, gerçek ASK/BID/spread, kaynak-yıl tamamlık; testte kötü sonuç görürsek `NO_EDGE / REJECT_AUTO_TRADING`. Başarısızlık varsa model saklanır, başka veriyle optimize edilmiş tarihi kazanım iddia edilmez.

## Kaynak güvenliği
- 2023/24/25/26 Nasdaq, ZN, CL as-of saat verileri ayrı Git blob SHA ile `data/V6_CME_NQ_ZN_CL_1H_ASOF_YYYY.csv`.
- NQ C calendar-continuous futures, ZN ve CL continuous futures roll sınırlarını içerebilir, gerçek USD DXY veya tahvil getirisi değildir. SI gümüş 3h karar saatlerinde çok seyrek olduğundan V6 dışında. R71 ve R72 Claude makro sürpriz tablolarında ilk yayın vintage ispatı olmadığından predictor değil.

**Durum:** Test başarılı olsa bile `PROBABILITY_NOT_CAUSAL` ve `LIVE_EXECUTION_NOT_READY`; başarısızsa basit fiyat A veya baz prevalans B kontrolünden üstünlük iddiası yok.
