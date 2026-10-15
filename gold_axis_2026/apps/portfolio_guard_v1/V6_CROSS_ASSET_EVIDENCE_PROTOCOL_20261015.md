# V6 – Ekonomik örgü kanıt filtresi ve çapraz-piyasa karar araştırması

**Statü: Model hipotezi — işlem sonuçları okunmadan önce dondurulan deney kararı.** V6'nın 2024–2026 dönemi geçmiş strateji sonuçlarını araştırmacı zaten görmüştür: sonuçlar kör OOS kabul edilmez. V1–V5 mutasyonsuz korunur.

## Veri gözlemleri
- OLAY-02 96 vakanın `onset_firstprint_verified` ve `mechanism_caused_proven` alanlarının 96/96'sı NO. İlgili Git blob `4b6c8fd84ea291ae22ddc9b0d5d545ce2d8fa527`. Ekonomik örgü sınıflaması yalnız hipotez; kanıtsız G05-C/G06-B veya G01-Fed sınıfı hiçbir alım-satımı zorla tetikleyemez.
- NQ.c.0 (Nasdaq futures), ZN.c.0 (10yr Treasury Note futures), SI.c.0 (gümüş futures), kaynak DATABENTO_GLBX_MDP3_OHLCV_1H_CALENDAR_CONTINUOUS_C_SOURCE_V1. Yalnız her barın bitiş saati (ts_event + 1 saat) geldiğinde kullanılır. 6 saat geriye getiri yalnız 6 önceki saat barı zaman farkı <=8 saat ise, aksi halde bilinmiyor. SI çok eksiktir; herhangi bir saatte değeri yoksa 0 diye doldurulmaz. Vadeli sürekli sözleşme geçişleri olası sapma riski.
- XAU fiyat veri özellikleri V3/V4'ün as-of M15→3h sabit paneli. Karar yalnız 09,12,15 Türkiye saatinde, önceki uygun gözlemlerle; banka kotasyonu değil. 0,8% tek yönlü alış + 0,8% tek yönlü satış ücret ve gerçek banka ASK/BID eksikliği açık.

## V6 sabit ekonomi/piyasa durumu haritası
- `EQUITY_BOND_SELL_OFF`: NQ 6h <= -0.8% ve ZN 6h <= -0.08%. Eşzamanlı hisse+tahvil değer kaybı; faiz yükseliyor *olabilir*, ancak vadeli fiyatından gerçek getiri serisi olmadan nedensel Fed/yield sıfatı verme.
- `SAFE_HAVEN_ROTATION`: NQ 6h <= -0.8% ve ZN 6h >= +0.08%. Hisse riski ve tahvil güvenli liman dinamiği, XAU yönü belirsiz.
- `YIELD_HEADWIND`: NQ 6h >= +0.3% ve ZN 6h <= -0.08%. Altına karşı potansiyel nominal getirili ortam, kesin DOWN değil.
- `CROSS_RISK_ON`: NQ 6h >= +0.6% ve ZN 6h >= 0.00%. Ortak risk fiyatlarına göre iyileşme, kesin UP değil.
- `NO_CONSENSUS_OR_STALE`: iki seri birlikte yoksa ya da eşikleri tutmuyorsa macro gate abstains. SI 6h <= -0.5% olduğunda, NQ <= -0.8% ile aynı anda gözlenirse `METALS_LIQUIDATION_CONFIRM` ek gözlem olabilir; SI eksikse tahmin kesinliği artmaz.

## Denenecek karar etkisi; sonuçlara göre geriye dönük oynatılmaz
- Başlangıç motoru V5 (EMA40/120 trend ve tasarlanmış stop). V6 fiyat giriş şartları korunur, yeni ekonomik filtreler sadece kararı nitelendirir. V5 `BUY_GOLD` adayında `EQUITY_BOND_SELL_OFF` ve XAU r92 < 0 ise girişi erteler (`WAIT_EQUITY_BOND_STRESS`). `YIELD_HEADWIND` ve XAU r276<0 ise AL kademesini yarıya sınırlar. Diğer hallerde V5 ile aynı AL yetkisi.
- V5 `SELL_TO_CASH` adayı `SAFE_HAVEN_ROTATION` iken XAU r4>0 ve r92>0 ise, satışın altına ters olma tehlikesi nedeniyle yalnız acil stop dışındaki satışı bir karar kesiti erteler; ayrı ek maliyet hesaplanır. `EQUITY_BOND_SELL_OFF` ve XAU r92< -1 ise satış koruma teyidini bir kere öne çeker ama XAU yavaş trend negatif veya drawdown <= -5 olmadan anlık tamamını SAT yapmaz.
- `NO_CONSENSUS` ve SI eksikliği öğrenilmiş P(UP) veya P(DOWN) uydurmaz; V5 fiyat kararları korunur. DNA 96 örneğin hiçbirinin mekanizması confirmed sayılmaz.
- V6 üzerindeki ücret ve portföy kararları V5'ten ayrı çalışır, aynı ay başlangıcı 100$ eski yıllar, Şubat 2026 başında Ocak V1 son 119.753917 USD CASH ve kesintisiz 2026 Eylül sonu.

## Kabul/kabul etmeme
- İlk değerlendirme: kapsamlı 2024–2025 bağımsız başlangıç, 2023 kapsam eksikliği belirgin; 2026 Şubat–Eylül retrospektif stres, kör ileri test değil. V5 ve V4, nakitte bekleme ve AL/TUT kontrollerine karşı son değer, max drawdown, işlem sayısı, kaçırılan UP, en kötü ay, macro eksikliği, olay kanıt seviyesi.
- Yeni V6 en az 2024 VE 2025'te V5 karşısında net değer/drawdown ile güçlü sonuç göstermediği ve veri-zaman kanıtı bulunmadığı sürece otomatik kullanıma alınmayacak; gerçek banka alış/satış fiyatı ve ilk haber doğrulaması yine sert blokajdır.
- Beklenen sonuç kazanma vaadi değil; **ekonomik durum sınıfının fiyat tabanına istatistiksel ve karar düzeyi ek değer katıp katmadığını yanlışlamak**. Başarısızlık bilimsel olarak saklanacak.
