# DeepSeek V4 Pro — R13 D1/H3 news/regime/hybrid independent referee

**Independent ideas, no execution claim.**

# Bağımsız Bilimsel İdeasyon ve Acımasız Eleştiri: XAUUSD Takvim-Horizon Etkileşimi

## Ön Kabuller ve Kısıtların Netleştirilmesi

Verilen bağlamda üç kritik çelişki tespit ediyorum: (1) 2026 önceki-ay 64.34 BA değeri, 2023–25 dönemindeki ~48–50 BA değerlerinden istatistiksel olarak anlamlı sapma göstermektedir (N=99, iki oranlı z-testi p≈0.004), ancak bu fark **2026 verisi görüldükten sonra** seçildiği için ileriye dönük kanıt değildir; (2) CPI/NFP olay günlerinde 15 dakikalık ilk impulsun yönü ~%90 doğru tahmin edilse bile, bu bilgi **sürpriz açıklanmadan önce mevcut değildir** — sadece olay-sonrası reaksiyon süresini ölçer; (3) H3/H5 hedefleri birbirini içerdiğinden (5 günlük pencere 3 günlük pencereyi kapsar) bağımsız örneklem sayısı etkin olarak artmaz, aksine otokorelasyon yapısı bozulur.

---

## Aday Mekanizma 1: Takvim-Güdümlü Koşullu Varyans Rejim Kapısı + Yön Uzlaşması (CGVR-YU)

### Mekanizma
Yön tahmini tek başına düşük sinyal-gürültü oranına sahiptir. Ancak **beklenen oynaklık ölçeklemesi altında günlük yön ile H3 yönü arasındaki tutarlılık**, rejimden rejime değişir. Temel hipotez: düşük gerçekleşen oynaklık (RV) ve düşük GVZ rejimlerinde günlük yön, H3 yönünü zayıf taşırken; yüksek RV/GVZ rejimlerinde taşıma gücü artar. Bu, **işlem maliyeti ve likidite asimetrisini** değil, **bilgi yayılım hızını** yansıtır — yüksek oynaklık dönemlerinde fiyat keşfi daha hızlı tamamlanır ve 09:00'da oluşan sinyal daha uzun ufuklara projekte edilebilir.

### Matematik
Her \( t \) işlem günü için:

\[
R_t^{DAY} = \ln(P_{17:00}) - \ln(P_{09:00}), \quad R_t^{H3} = \ln(P_{t+3,09:00}) - \ln(P_{t,09:00})
\]

Ölçeklenmiş tutarlılık sinyali:

\[
S_t = \text{sign}(R_t^{DAY}) \cdot \mathbb{1}\left[ |R_t^{DAY}| > \kappa \cdot \widehat{\sigma}_t^{RV} \right]
\]

burada \( \widehat{\sigma}_t^{RV} \) önceki 5 işlem gününün realize varyansından (09–17 penceresi, yıllıklandırılmış), \( \kappa \) geliştirme döneminde sabitlenmiş eşik (ör. 0.35).

Karar kuralı:

\[
\hat{y}_t^{H3} = 
\begin{cases}
S_t & \text{eğer } \widehat{\sigma}_t^{RV} > q_{70}(\widehat{\sigma}^{RV}) \text{ VE } GVZ_{t-1} \text{ artış trendinde} \\
\text{abstain} & \text{diğer durumlarda}
\end{cases}
\]

### Kesin Saat Disiplinli Özellik/Label Saatleri
- **Özellikler (as-of 09:00 Europe/Istanbul):** \( R_{t-1}^{DAY} \) (önceki gün 09→17), \( \widehat{\sigma}_{t-1}^{RV} \) (t-6'dan t-1'e 5 günlük pencere), \( GVZ_{t-1}^{close} \) (önceki NY kapanışı, saat farkı uyumlu), \( \Delta GVZ_{t-1} = GVZ_{t-1} - GVZ_{t-6} \), takvim işaretçisi \( C_t \) (bugün veya önümüzdeki 3 işlem günü içinde CPI/NFP/FOMC var mı, yalnızca önceden bilinen program).
- **Label:** \( \text{sign}(R_t^{H3}) \), hesaplanması t+3 günü 09:00'da tamamlanır — **gelecek bilgisi içermez**.

### Negatif Kontrol
(i) Aynı özelliklerle ancak \( \kappa = 0 \) (saf yön işareti) — yalnızca rejim kapısının katkısını izole eder. (ii) RV eşiği yerine rastgele seçilen günlerin %30'unda abstain — seçiciliğin şanstan gelmediğini doğrular. (iii) Bağımlı değişken olarak **bir sonraki günün** (t+1) yönü kullanılır — eğer mekanizma yalnızca H3 için çalışıyorsa, sinyal ufuk-spesifiktir.

### Ablasyonlar
- GVZ trend bileşenini çıkar, yalnızca RV kapısı kullan.
- Takvim işaretçisini kaldır, yalnızca oynaklık kapısı.
- \( \kappa \) değerini geliştirme setinde 0.25/0.35/0.50 olarak tara (3 değer, aşırı uyum riski düşük).

### Örneklem Sınırlamaları
2023 geliştirme: ~250 işlem günü, %30 abstain ile ~175 karar. Her yön sınıfında ~85–90 örnek. Binomial testin %50'ye karşı %60 BA'yı %80 güçle tespit etmesi için N≈100 gereklidir — yeterli, ancak yıl-içi rejim kırılmalarında kırılgan.

### Neden İKİ YÖNDE de Şansı Yenebilir?
Yüksek RV dönemlerinde fiyat **trend oluşturma** eğilimindedir (otokorelasyon pozitiftir); düşük RV dönemlerinde ortalama-dönüş baskındır. Aynı yön işareti her iki rejimde de görülebilir, ancak yalnızca yüksek RV'de kalıcıdır. Bu, UP tahminlerinde de DOWN tahminlerinde de simetriktir — yönü önceden bilmeyi değil, **hangi koşullarda yönün kalıcı olduğunu** modeller.

### Beklenen Başarısızlık Modu
RV eşiği ile GVZ trendi arasındaki etkileşim doğrusal değildir ve 5 günlük RV penceresi yavaş adapte olur. Ayrıca GVZ'nin İstanbul 09:00'da bilinen değeri önceki NY kapanışıdır — gece boyunca Asya seansı bilgisi eksiktir.

---

## Aday Mekanizma 2: Bayesci Yön Uyuşmazlık Büzülmesi ile Günlük-H3 Tutarlılık Sinyali (BYUB)

### Mekanizma
Günlük yön ile H3 yönü arasındaki **koşullu uyuşma olasılığı** sabit değildir; önceki tutarsızlık dizileri bilgi taşır. Eğer son 3 günde günlük yön H3 yönünü 3/3 yanlış tahmin ettiyse, bu bir **değişim noktası** göstergesidir — piyasa mikro yapısı veya likidite dengesi kaymıştır. Hipotez: tutarsızlık serisinin ardışık bağımlılığı, ham yön sinyalinden bağımsız öngörü gücü taşır.

### Matematik
Tanımlar: \( A_t = \mathbb{1}[\text{sign}(R_t^{DAY}) = \text{sign}(R_t^{H3})] \) — günlük yönün H3 yönüyle uyuşup uyuşmadığı. Bu **yalnızca t+3'te bilinir**; as-of t'de önceki değerler \( A_{t-1}, A_{t-2}, \ldots \) mevcuttur.

Ardışık uyuşmazlık sayacı:

\[
D_t = \sum_{j=1}^{4} (1 - A_{t-j})
\]

Bayesci büzülme kuralı:

\[
\hat{y}_t^{H3} = \text{sign}\left[ (1 - \lambda_t) \cdot \text{sign}(R_t^{DAY}) + \lambda_t \cdot \hat{\mu}_t^{prior} \right]
\]

burada \( \lambda_t = \frac{D_t/4}{D_t/4 + \alpha} \), \( \alpha \) geliştirmede sabitlenmiş düzenlileştirme (ör. \( \alpha=0.5 \)), ve \( \hat{\mu}_t^{prior} \) basit 20 günlük geriye dönük yön ortalaması:

\[
\hat{\mu}_t^{prior} = \frac{1}{20}\sum_{j=1}^{20}\text{sign}(R_{t-j}^{H3})
\]

Karar: \( \hat{y}_t^{H3} \) değeri sıfıra yakınsa abstain:

\[
|\hat{y}_t^{H3}| < 0.15 \Rightarrow \text{abstain}
\]

### Kesin Saat Disiplinli Özellik/Label Saatleri
- **Özellikler (as-of 09:00, t günü):** \( A_{t-1}, A_{t-2}, A_{t-3}, A_{t-4} \) (her biri ilgili H3 penceresi kapandıktan sonra bilinir — ör. \( A_{t-1} \) t+2'de bilinir, dolayısıyla t'de as-of geçerlidir), \( R_{t-1}^{DAY} \) işareti, 20 günlük H3 yön ortalaması (t-1'e kadar tamamlanmış H3 pencerelerinden).
- **Label:** \( \text{sign}(R_t^{H3}) \).

### Negatif Kontrol
(i) \( \lambda_t = 0.5 \) sabit (büzülme katsayısı bilgi taşımıyor). (ii) \( D_t \) sayacı yerine rastgele permüte edilmiş uyuşmazlık dizisi. (iii) Bağımlı değişken olarak günlük (DAY) yön — eğer sinyal yalnızca H3 için çalışıyorsa, mekanizma ufuk-spesifiktir.

### Ablasyonlar
- \( \alpha \) değerini 0.25/0.50/1.00 olarak tara.
- \( D_t \) penceresini 3 veya 5 güne değiştir.
- \( \hat{\mu}_t^{prior} \) ortalamasını 10 güne indir.

### Örneklem Sınırlamaları
H3 penceresinin kapanması 3 işlem günü sürdüğünden, etkin bağımsız örneklem sayısı günlük N'in yaklaşık 1/3'üdür. 2023–24 geliştirme döneminde ~500 gün → ~160 etkin H3 gözlemi. %20 abstain ile ~130 karar — sınırda yeterli, ancak yıl-içi heterojenlik ciddi kısıt oluşturur.

### Neden İKİ YÖNDE de Şansı Yenebilir?
Bayesci büzülme, sinyal **belirsizliğini** modeller. Uyuşmazlık sayacı yüksek olduğunda, günlük yön sinyali gürültülüdür ve önceki H3 dağılımına yaklaşmak daha güvenlidir. Bu, UP veya DOWN fark etmeksizin sinyal kalitesini ölçer — yönü değiştirmez, güveni ayarlar.

### Beklenen Başarısızlık Modu
Uyuşmazlık sayacı yavaş hareket eder; bir rejim değişimini ancak 2–3 gün sonra yakalayabilir. 3 günlük H3 penceresi, sayacın kendisiyle örtüşen bilgi içerir (otokorelasyon). Ayrıca 20 günlük önceki H3 ortalaması, uzun bellek varsayar — ancak altın getirilerinde bellek zayıftır.

---

## Aday Mekanizma 3: Üç-Durumlu Saklı Rejim ile Olay-Ufuk Etkileşimi (3S-OVE)

### Mekanizma
Piyasa, **olay öncesi sıkışma**, **olay sonrası
