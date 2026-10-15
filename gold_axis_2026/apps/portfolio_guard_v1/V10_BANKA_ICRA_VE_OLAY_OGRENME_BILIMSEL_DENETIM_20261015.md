# V10 · Banka işlem saatleri, hata kökeni ve öğrenme politikası denetimi

**Tarih:** 15 Ekim 2026 | **Dal:** `research-gold-v10-execution-evidence-20261015` | **Karar:** GÖLGE ARAŞTIRMA, OTOMATİK TERFİ YOK

## Temel teknik keşif — V7 sonucu işlem zamanlamasına duyarlı

V7 geçmiş altın (`p`,`c`) verisinin o kontrol noktasındaki `c` ve türetilen göstergelerini okuyor, fakat aynı noktanın `p` fiyatından al/sat işlemi varsayıyordu. Bu, as-of bilgi ve işlemin uygulanabilirliği arasındaki fark nedeniyle iyimser ve potansiyel olarak gelecek bilgisine dayanan bir icra sözleşmesidir. Bir düzeltme olarak V7 tahmin algoritması korunarak **yalnız daha önce oluşturulan emir sinyali**, sonraki uygun Türkiye 09:00/12:00/15:00 kontrol noktasının `p` fiyatından uygulanıyor.

| Şubat–Eylül 2026, 119,753917 $ nakit başlangıcı | Eylül sonu USD |
|---|---:|
| Eski V7 (aynı kontrol noktasında sinyal+işlem) | **123,529545** |
| Aynı V7 tahminleri, sonraki banka kontrolünde icra | **116,500026** |
| V10 gecikmeli icra + 14 günlük satış-sonrası risk koruması | **130,666324** |
| İşlem yapmadan nakit | **119,753917** |
| Şubat başında al ve Eylül sonunda sat; fiyat vekili | **108,444342** |

Komisyon alışta **%0,8** ve satışta **%0,8** (fiyat değişmiyorsa bir turun bileşik maliyeti %1,5936, başabaş fiyat hareketi yaklaşık %1,6194). Gerçek banka BID/ASK ve ilave emir kayması hesaba katılmadı.

## Yeni V10 kuralı

Algoritma V7'nin 96 saatlik risk ve 336 saatlik fırsat tahminlerini, olgunlaşan öğrenme güncellemeleriyle **aynen kullanıyor**. Yenilik, ekonomik bir **NO-TRADE / reentry veto** politikası: Stres sinyali sonrası altın satıldıysa, tekrar alış yapmak için (1) en az 336 saatin geçmesi, (2) mevcut karar barında `r1>0` ve `r3>0`, (3) `r4>-0,5`, (4) o anda XAU/NQ stres teyidi bulunmaması gerekir. Bunlar sinyal anında bilinebilen piyasa metrikleridir. Sinyalden sonraki kontrol noktasında icra edilir.

**Açıklık:** Bu ilave risk kuralı, çevrimiçi regresyonla *öğrenilmiş* bir sınır değildir; öğrenen V7 tahminlerinin üstüne eklenen hipotez tabanlı bir koruma katmanıdır. 2026 olayları tasarımdan önce incelendi. 336 saat V7'nin mevcut 14 günlük hedef ufkundan alınmıştır, fakat aynı 2026 verisinde sonuçları gördüğümüz için bağımsız başarı iddiası yoktur.

### 2026 işlem günlüğü (Türkiye saati)

| Sinyalin oluşumu | V10 komisyonlu işlem | Yorum |
|---|---|---|
| 2 Şubat 09:00 | 2 Şubat 12:00 **AL** | Önceden üretilmiş 14 günlük fırsat sinyali |
| 3 Mart 12:00 | 3 Mart 15:00 **SAT** | Altın/NQ stres teyidi |
| 6–Mart sonu boyunca AL adayları | **18 kez RED** | 336 saat ufku veya trend teyidi sağlanmadı |
| Nisan–Eylül | **NAKİT** | Yeni alış koşulları oluşmadı |

Bu örneklemde 2026 V10 toplam **1 alış + 1 satış** yaptı. Gerçek zamanlı banka emri yapılmış değildir.

## Gecikme ve maliyet hassasiyeti

| Her yönde varsayımsal kesinti | 1. kontrol | 2. kontrol | 3. kontrol |
|---|---:|---:|---:|
| %0,80 | 130,6663 | 127,5903 | 126,2141 |
| %0,95 | 130,2715 | 127,2047 | 125,8327 |
| %1,05 | 130,0086 | 126,9480 | 125,5787 |

Bu hücreler aynı **önceden görülmüş 2026** fiyat yolundaki as-of kural deneyidir. Fiyat vekili gerçekte işlem gören banka kotasyonu olmayabilir. Gecikme artışına rağmen pozitif kalmak yeterli bilimsel doğrulama değildir.

## Daha eski yıllarda bağımsız ve negatif kontrol

2025 aynı veri/öğrenme sözleşmesi, 100 USD başlangıç:

- V7 sonraki banka kontrolünde icra: **101,436571 USD**.
- V10 336h koruması: **101,436571 USD**; koruma **0** alış denemesini engelledi.
- 2025 pasif altın: **160,415265 USD**.

2023 geçmişi ekleyip aynı yöntemi (farklı eğitim başlangıcı, aynı kaynak fiyat kontratı) sınayınca:

- 2024 V10: **108,614611 USD** vs pasif altın **123,849710 USD**.
- 2025 V10: **110,663496 USD** vs pasif altın **160,415265 USD**.
- 2026 V10: **130,666324 USD**, fakat 2026 tasarım sırasında incelenmişti.

**En önemli sınırlama:** 2024 ve 2025 negatif kontrollerinde aynı korumanın ekonomik katkısını bağımsız olarak gösteremedik. Yalnız 2026 Mart'ta devreye girip sonucu iyileştirmesi, *keşif niteliğinde bir hipotez* olarak değerlendirilmelidir. Kesin ve tekrarlanabilir al-sat avantajı henüz gösterilmedi.

## Hatalardan öğrenme yol haritasında kaydedilen düzeltmeler

1. Öğrenme hedefi yalnızca fiyata yön vermek değildir; **komisyon sonrası net kullanılabilir fırsatı**, gerçekleşme zamanı ve işlem penceresiyle birlikte etiketlemek gerekir.
2. Geçmiş olayı gördükten sonra seçilen kuralın aynı olayla tekrar ölçülmesine performans doğrulaması denemez.
3. Satış sonrası geri giriş bir *yeni ekonomik rejim iddiasıdır*; önceki yükselişin hâlâ sürdüğü varsayımıyla aynı anda işlem yapılmamalıdır.
4. Hata ve fırsat kayıtları olgunlaştığında güncellenir; eşzamanlı 96/336 saat gözlemlerini bağımsız şok vakaları olarak saymak sahte kesinliğe yol açar.
5. OLAY-02 / ÖĞREN-03 olay DNA vakalarında haberin erişilebilir ilk yayın zamanı doğrulanmadan **haber kaynaklı tahmin yapıldı** denemez. Şu anda güvenli veri sözleşmesine uyumlu 0/96 ekonomi firstprint kaydı var.
6. Gerçek banka kotasyonu ve 15 dakika çözünürlüklü emir disiplini henüz yok. Fiyat vekilinden banka kârı çıkarımı yapılamaz.

## Literatürle ilişki

İşlem maliyeti bulunduğunda küçük fiyat/sinyal değişimlerinde işlem yapmamak (no-transaction region) bilimsel olarak yerleşik bir yaklaşımdır: Delgado, Dumas ve Puopolo, *Hysteresis bands on returns, holding period and transaction costs*, Journal of Banking & Finance (2015), https://doi.org/10.1016/j.jbankfin.2014.12.015. V10 sadece basit kural tabanlı bir yaklaşım kullanır, teorik optimum çözmüş değildir.

Rejim kırılmalarına daha bilimsel çevrimiçi yaklaşım olarak Adams & MacKay (2007) *Bayesian Online Changepoint Detection*, https://arxiv.org/abs/0710.3742 düşünülebilir. **BOCPD henüz V10'da uygulanmadı.** Ek veri ve olay firstprint gerektiren araştırma adayıdır.

## Kod, test ve uygulama

`v10_lagged_v7_engine.js` eski V7'yi değiştirmeden gecikmeli icra ve yeniden alım filtresi içerir. `v10_execution_audit.js` geçmişi ve maliyet/giriş/gecikme karşı deneylerini kaynak SHA sabitleriyle çalıştırır. `v10_execution_audit.test.js` eski V1–V9 kodunun yanında geleceği okumama, pozisyon büyüklüğü, test yılı, maliyet stres, 1–3 kontrol noktalı gecikme ve **başarısız-terfi** kontrolünü çalıştırır. Salt-okunur API: `GET /api/algorithm/v10/evidence`; arayüz: `V10 işlem zamanı ve koruma denetimi`.

**Karar:** GÖLGE ÇALIŞMA. Yeni model V7'nin yerine canlı uygulamada atanmaz, eski dal veya manifestler değiştirilmez ve banka emri verilmez. Yeni ilk yayımlanma zamanı doğrulanmış makro vakalar, gerçek banka fiyatları ve daha sonra görülmemiş tarihsel dönem olmadan otomatik terfi yok.
