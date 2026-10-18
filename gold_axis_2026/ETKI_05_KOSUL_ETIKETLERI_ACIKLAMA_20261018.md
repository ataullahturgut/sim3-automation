# ETKİ-05 — K Etiketleri: ekonomik şartların tek tek ve birleşince altın etkisi

**18 Ekim 2026 | GOLD-ADAPTIVE-MODEL-APP-01 | DURUM=ARAŞTIRMA | OTORİTE=ETİKET KÜTÜPHANESİ | CORE DEĞİŞMEDİ | SCIENCE_GATE=FAIL**

## Kullanıcı amaç düzeltmesi: yeni algoritma değil, mevcut algoritmaya verilebilecek koşul etiketleri

Önceki çalışmadaki **E01–E05 "ekonomik etki ailesi" kümelemesi kullanıcı isteğinin doğrudan karşılığı DEĞİLDİR**; 5 grup ve ORG01–ORG12 bağıntısı araştırma arka planı olabilir. Asıl amaç basit, bağımsız ve birleştirilebilir **maddeler (K etiketleri)** kurmak ve "bu koşul veya bu koşullar birlikte bulunduğunda geçmişte altın ne yönde, ne kadar, ne kadar sürede hareket etti?" sorusunu **OLAY-02 fiyat ölçümünden** cevaplamaktır. ÖĞREN-03 ekonomik neden örgüleri korunur. Etiket, sonucu veya işlemi tanımlamaz; sonradan gerçekleşen UP/DOWN ayrı hedef etiketidir.

## A. Koşullar / maddeler

| K etiketi | Açık ve test edilebilir şart | Arşiv verisinde durum |
|---|---|---|
| **K01** | Enflasyon (CPI) açıklandığında **actual > yayın öncesi consensus** | 34 CPI kaydında karşılaştırıldı; özgün ilk yayın vintage henüz sertifikasız |
| **K02** | CPI actual < consensus | Aynı |
| **K03** | İstihdam (NFP) actual > consensus | 35 NFP kaydında karşılaştırıldı; firstprint henüz sertifikasız |
| **K04** | NFP actual < consensus | Aynı |
| **K05** | CPI actual = consensus (belgelenmiş sayı yuvarlamasıyla) | Aynı |
| **K06** | Ortalama saatlik ücret actual > consensus | **EKSİK** bağımsız as-of seri |
| **K07** | İşsizlik oranı actual > consensus | **EKSİK** |
| **K08–K09** | Dolar endeksi/güvenilir USD vekili güçlenir / zayıflar | **EKSİK** aynı-UTC doğrulanmış veri |
| **K10–K11** | ABD reel tahvil faizi yükselir / düşer | **EKSİK** aynı-UTC doğrulanmış veri |
| **K12** | Finansal stres / riskten kaçış artar | **EKSİK** bağımsız zamanlı ölçüm |
| **K13** | Teminat zorunlu satışı / pozisyon çözülmesi doğrulanır | **EKSİK** ilk kaynak ve akım |
| **K14–K15** | Altın haberden önceki kesintisiz tamamlanmış 4s M15'te UP/DOWN | 84/85 açıklama için arşiv Neon fiyatından ölçülebiliyor; piyasa önkoşul etiketidir, ekonomik neden değil |

**"Enflasyon yüksek"** iki ayrı kavram olabilir: (a) mutlak enflasyon düzeyi veya (b) **beklentiden yüksek sürpriz**. Bu ilk versiyonda yalnız (b) sayısallaştırıldı; mutlak yüksek enflasyon rejimi için ayrı `CPI_YOY_LEVEL_ABOVE_REGIME_THRESHOLD` etiketi özgün yayımlanmış seviye/eşik doğrulanmadan doldurulmaz. CPI bu kaynakta aylık sürprizdir; NFP sürprizi bin kişidir, sayı büyüklükleri doğrudan aynı eşiklerle kıyaslanamaz.

## B. Tek madde gerçekleşirse arşivde ne görüldü?

**Bağımsız bir canlı tahmin değil:** Bunlar resmi açıklama tarihleri etrafındaki tarihsel 4s fiyat sonuçlarıdır; tam fiyat akışı olan **68 CPI/NFP** kaydı. İlk yayın actual/consensus as-of erişimi henüz sertifikalı değil.

| Açıklama anındaki K | Geçmiş 4s UP | Geçmiş 4s DOWN | 4s >=+%1 UP | 4s <=−%1 DOWN |
|---|---:|---:|---:|---:|
| K01 — CPI beklentiden yüksek (**8**) | 3 | **5** | 0 | 2 |
| K02 — CPI beklentiden düşük (**13**) | **11** | 2 | 5 | 0 |
| K03 — NFP beklentiden güçlü (**23**) | 10 | **13** | 4 | 5 |
| K04 — NFP beklentiden zayıf (**11 tamamlanmış**) | 6 | 5 | 2 | 0 |
| K05 — CPI beklentiyle aynı (**13**) | 3 | **10** | 0 | 2 |

**Düşük maliyet/iyi başarı iddiası YOK.** 4 saatte 1% yalnız bu deneyin kolay incelenebilir şiddet işaretidir; bankada her yön 0,8% masrafı karşılayan işlem sonucu değildir.

## C. Birden çok ekonomik madde birlikte olursa ne görüldü?

Veri kaynağında CPI ve NFP aynı saniyede açıklanmıyor. "Birlikte" deyince açık bir **as-of sözleşmesi** zorunlu:
- **Aktif madde**: o gün açıklanan CPI veya NFP sürpriz etiketi.
- **Önceki madde**: *farklı türdeki en son yayımlanmış* CPI/NFP sonucu, **45 günü aşmamış** olmalı; bu ikinci etiket yeni anlık duyuru değil, **önceden bilinebilen ekonomik bağlam**.
- 45 gün yalnız ilk araştırma geçerlilik penceresidir, öğrenilmiş ekonomik etki ömrü değildir. Kayıt yoksa `UNKNOWN`, geçmişte açıklanmamış sonraki haber asla kullanılmaz.
- Aşağıdaki örnekler ancak **ilk yayın ve consensus-vintage orijinal olarak doğrulandıktan sonra** canlı/as-of koşul kabul edilebilir. Bugün yalnız retrospektif araştırmadır.

| Güncel açıklama + önceki bağlam | Geçmiş 4s UP | Geçmiş 4s DOWN | Şiddet tanısı (abs≥%1) |
|---|---:|---:|---|
| **K01 + eski K03** (CPI yüksek, yakın tarihli güçlü NFP) **6 örnek** | 1 | **5** | 2 kez büyük DOWN |
| **K02 + eski K04** (CPI düşük, yakın tarihli zayıf NFP) **5 örnek** | **5** | 0 | 2 kez büyük UP |
| **K03 + eski K02** (NFP güçlü, yakın tarihli düşük CPI) **10 örnek** | 1 | **9** | 4 kez büyük DOWN |
| **K03 + eski K01** (NFP güçlü, yakın tarihli yüksek CPI) **3 örnek** | 2 | 1 | 1 kez büyük UP |

Bu çarpıcı görünen sonuçlar **seçilmiş kural** değildir: 2023–2025 sonuçlarına bakarak bu etiket kombinasyonlarını öne çıkardık, örnekler az, dönem rejimi değişiyor. Örneğin *K03 + eski K02* zamanlar arasında 2023'te 3/3, 2024'te 1/2, 2025'te 5/5 DOWN: hiçbir durumda en az destek/ilk haber/doğrulanmış nedeni veya kör test şartlarını geçtiği kanıtlanmış değildir. Aynı haber ailesindeki ters vakalar saklanır.

**Örnek ekonomik cümle:** `K03=TRUE` (beklentiden güçlü istihdam), `K08=TRUE` (dolar güçleniyor) ve `K10=TRUE` (reel faiz artıyor) → önceki benzer ve zıt vakaları bul → belirlenmiş ufuktaki UP/DOWN/SMALL/LARGE dağılımını göster. Şu anda K08/K10 as-of veri eksik olduğundan bu üçlü etiketin sayısal sonuç tablosu **YOKTUR**. Gerçekmiş gibi gösterme.

## D. Mevcut algoritmanın kullanacağı sözleşme

1. Etiketleme modülü olay kaydı/eşzamanlı piyasa verisinden **`asof, label_id, true|false|unknown, source, availability, vintage`** üretir. Etiket **K** kodu tarih bağımsız şarta işaret eder, olay tarihi değil.
2. Kurallar **AND**, **OR**, `NOT` ile birleştirilir; `UNKNOWN` bir `FALSE` yerine geçmez; gecikmiş veri geriye doğru güncellenip sanki o dakikada varmış gibi kullanılamaz.
3. ETKİ-05 zaman bağımlı gözlenen **sonuçları** `XAU_4h_direction`, `XAU_4h_magnitude`, `continuation`, `reversal`, `invalidations` olarak saklar; bunların **olgunlaştığı zamandan önce** öğrenme girişi olamaz.
4. Zamanı gelmiş vakalardan hem olumlu hem başarısız hem olaysız kontrollerle koşul → etki ilişkisi ölçülür; minimum örnek, rejim normalize ölçek, güven aralığı, yıl bazlı bozulma, düşük destek için çekimser etiketi zorunlu.
5. Mevcut ANN/ANFIS/LSTM ilhamlı CORE zaten tek model hattıdır; **yeni fiyat tahmin algoritması kurulmadı**. ETKİ-05 ileride modelin okuyacağı koşul sözlüğüdür. S1/S2/S3 öğrenme, üretim, BUY/SELL veya performansı bu kayıtla değiştirilmedi. İşlem kararı ekonomik kanıt ve banka maliyetine ait ayrı kapıda kalır.

**Doğru tasarım:** `K etiketleri (input şartları)` + `kombinasyonlar` + `OLAY-02 karşıt geçmiş sonuçlar` + `ÖĞREN-03 neden hipotezi` → mevcut modellerin eğitiminde kullanılabilecek, ancak bugün henüz doğrulanmamış koşullu etki bilgisi.

**Makine kayıt dosyası:** [K etiket sözlüğü ve bütün gözlenen iki-madde kombinasyonları](ETKI_05_KOSUL_ETIKETLERI_V1_20261018.json). K01–K15 tarifi ve eksik veri maskesi içerir. Eski 5 ekonomik aile çalışması fizikî olarak korunur ama bu kullanıcı amacının tanımı yerine geçmez.
