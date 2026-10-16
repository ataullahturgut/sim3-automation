# V22 — YALNIZ OCAK 2023: Otonom Matematiksel Öğrenme Koşusu ve Dürüst Sonuç
2026-10-16. Research branch: `research-gold-jan2023-self-improving-math-20261016`. Historical 15min spot proxy, no actual bank BID/ASK. ÖN KAYIT ilk tek dosyalı commit: `717bb0ade2460ad5e1a1f14ccc0497d6b8965715`.

## Proje kapsamı
**Yalnız Ocak 2023**, 100 USD başlangıç CASH. 15dk altın kapanışlarını kronolojik gözlemleme; kararlar Türkiye 09:00–17:00 hafta içi, veri mevcutsa. **HİÇ Nasdaq, hisse, ETF, haber, Fed, ekonomik olay, Şubat veya başka ay yok**. Aynı tarihsel Ocak dönemi önceki araştırmalarda incelendiğinden bu araştırma OOS/kör değil. Gerçek banka emir kotasyonu yerine HistData 15m geçmiş spot fiyatı kullanıldı; alış ve satışta ayrı ayrı **%0,8** uygulandı.

## Yeni matematiksel algoritma (sadece kurala bağlı eski sistem değil)
1. 15 dakika fiyatından 8-boyutlu geçmiş-only durum x çıkar: log getiriler 1/4/16/64 önceki GÖZLENEN bar, kısa volatilite, 64 bar drawdown, ivme. Son 16 bar kesintisiz ve hiçbir veri gelecekten olamaz; uzun lookback günlük doğal source gap'lerinden geçebilir. İlk sıfır-bank-check hatası [V22_JAN2023_SOURCE_GAP_TEKNIK_DUZELTME.md](V22_JAN2023_SOURCE_GAP_TEKNIK_DUZELTME.md) içinde şeffaf kaydedildi.
2. Dört öğrenen 1,4,16,64 bar ileri log getiri tahminleyicisi: `mu_h(t)=w_h^T x(t)+bias_h`. Her tahmin yalnız gelecekteki gerçek sonuç **oluştuktan sonra** etiketle güncellenir. `e=mu-y`; ağırlıklar AdaGrad online gradient ile, bias & residual varyans EWMA ile kendiliğinden güncellenir.
3. Bir üst-seviye çevrimiçi Hedge öğrenicisi, her ufkun yalnız gerçekleşmiş geçmiş tahmin hatasına göre `p_h ∝ exp(-0.25*loss_h)` ağırlıklarını günceller. Yeniden eğitim için manuel eşik taraması yok.
4. İlgili dört uzman getirisini tahmin-belirsizlik düzeltmesiyle birleştir. CASH→BUY veya GOLD→SELL yalnız öngörülen *işlem maliyeti sonrası avantaj* teorik iki bacak %1,606434 log eşiğini aşarsa. Her işlemde gerçek sanal sermayeden %0,8 bacak kesilir. Aksi halde WAIT. Aynı anda iki karşıt emir/gelecek bilgisi yok.
5. Sadece OCAK 2023 verisi 15dk sırayla, şok günleri ve başarısızlıklar dahil ilerler. Parametre/horizon/cost sonuçtan sonra yeniden taranmaz.

## Gerçek CI koşusu
GitHub Actions: https://github.com/ataullahturgut/sim3-automation/actions/runs/38904978647
- **7/7 matematiksel nedensellik, maliyet, tarih-sınırı testleri PASS**.
- Ocak veri paneli **1764** sıra; gerçekten uygun bankacılık-saatinde **575** ayrı karar kontrolü.
- Dört ileri-horizon matematiksel modelinde **3725 olgunlaşmış label ve 3725 sıfır olmayan online katsayı güncellemesi**.
- Gerçek sanal BUY **0**, SELL **0**, CASH'te 100 USD kaldı. İşlem maliyeti ödenmedi.
- Aynı model/quote penceresi için ilk uygun banka fiyatından pasif alış ve Ocak sonu teorik satış karşılaştırması **103.007703 USD**.
- ***BUNLAR KÂRLI STRATEJİ BAŞARISI DEĞİL***. Öğrenme gerçekleşti; ama 15dk–16h öğrenilmiş kısa ufuk değerleri yaklaşık %1,6064 işlem maliyeti sınırını aşamadığı için hiç işlem yapamadı.
- 1/4/16/64 ufuk etiket sayısı sırasıyla **1320 / 1254 / 1006 / 145**; tahmin MAE sırasıyla **%0,066273 / %0,135040 / %0,306935 / %0,609759**, ağırlıkları sonunda **0,254758 / 0,253625 / 0,244386 / 0,247231**. Daha uzun horizon daha az etiket alır; kararlara önemli etki ettiği gösterilmedi.
- İlk 64 kesintisiz geçmiş verisi şartı gece kapanışlarıyla 0 banka sinyaline kilitlendiği için başlangıç koşusu STRATEJİ açısından geçersiz sayılmış, 16 yakın bar + uzun kayıtlı lookback gerçekçiliğine göre teknik clock düzeltilmiştir. Değişim sonucu görerek yapılmış yatırım eşiği optimizasyonu değildir; başka veriyle yapılacak bağımsız doğrulama gerekir.

## Matematiksel problem — açık ve net
Dört ufuklu lineer getiri modeli gelecekteki fiyat hareketinin ortalamasını ve belirsizliğini öğrenir, **uzun süre tutulacak pozisyonun ve sonradan yeniden girmenin tam değerini öğrenmez**. 4 saat/16 saat değer tahmini iki bacak %1,6 maliyeti aşamıyorsa WAIT çıkması şaşırtıcı değildir. Modelin matematiksel parametreleri geliştiği halde kârlılık artmayabilir; 'hep iyileşme garantisi' matematiksel olarak yoktur.
Yeni **ayrı** bilimsel deneme için güçlü hipotez: fiyat-only karar yazarak değil, self-financing alternatif CASH↔GOLD portföylerinin gerçekleşmiş işlem-dahil fırsat maliyetini 1g/3g/1hafta uzun vade kredi atamasıyla online **counterfactual regret-minimization** + yeniden giriş critic'i ile öğrenmek. Özellikle pozisyonları alternatif politika bazında sanal hesaplarda izlemek, bu Ocak araştırması doğrultusunda test edilebilecek sonraki modeldir. Ancak aynı Ocak sonucunu görüp threshold taraması yapmak bilimsel başarı sayılmaz.

## Çıktılar ve veri
Kod `v22_jan2023_math.js`; test `v22_jan2023_math.test.js`; data kaynağı ayrı depoda önceden var olan `JAN_2023_EVENT_DNA_ASOF_V2_PANEL_20261015.csv` (ancak V22 yalnız tarih, price-close ve sonraki-bar price-open okur, NQ/ZN/event kolonlarını tamamen atar).
Ayrıntılı **tüm 575 karar** ve günlük öğrenme/güncellenen head istatistikleri GitHub Actions artefaktında:
https://github.com/ataullahturgut/sim3-automation/actions/runs/38904978647/artifacts/12047611755

Hiçbir Şubat ya da daha sonraki ay çalıştırılmadı. Eski V21/V18/R2/R3 ve Ocak 2026 dosyaları değiştirilmedi. Canlı emir yok.
