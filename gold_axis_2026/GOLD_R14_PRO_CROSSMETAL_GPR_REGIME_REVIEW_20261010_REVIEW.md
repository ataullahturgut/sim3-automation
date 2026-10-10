# Real DeepSeek V4 Pro R14 external independent research opinion
**Hypotheses only; no executed backtest by DeepSeek.**

Türkçe yanıt:

**Tek model:** GPR koşullu altın-farkı (Gold-minus-industrial-metals) yenilik sinyali.

**Formül:**

\[
S_{t,h} = \operatorname{sign}\left(\sum_{i=1}^{k} w_i \cdot I_{t,i}^{Au} - \sum_{j=1}^{m} v_j \cdot \bar{I}_{t,j}^{Ag,Pt,Pd}\right) \cdot (1 + \gamma \cdot GPR_{t-l}^{\text{vintage}})
\]

Burada \(I_{t,i}^{Au}\): son 16×15 dakikalık XAU getiri yenilikleri (04:45–08:30 TR, her bar log-fark); \(\bar{I}_{t,j}^{Ag,Pt,Pd}\): aynı pencerede Ag/Pt/Pd ortalama getiri yeniliklerinin ilk iki temel bileşeni; \(GPR_{t-l}^{\text{vintage}}\): yalnızca \(available\_as\_of \le t\) kayıtlarından seçilen, en az 1 tam iş günü gecikmeli GPR seviyesi (aylık PIT). \(w_i,v_j\) ridge ile daraltılmış; \(\gamma\) işaret-tersinme etkileşim katsayısı. \(h\)=H3: 09 TR’den itibaren üç iş günü 09 TR. Hedef: gerçekleşen BID ve ASK getiri işaretlerinin **her ikisi de** aynı yönde olmalı, aksi halde örnek dışlanır (transport kaybı raporlanır).

**Karşı-hipotez:** GPR yüksekken altının sanayi metallerinden pozitif sapması **güvenli liman** etkisiyle tersine döner; düşük GPR’de ise beta-takipçisi davranır. Bu, katsayı tersinmesi (\(\gamma<0\)) demektir. Ekonomik olarak savunulur çünkü yüksek jeopolitik riskte sanayi metalleri talep şokuyla düşerken altın hedge talebiyle yükselir; düşük riskte ise ortak makro döngü baskındır. Ancak saldırı: GPR’nin **gerçek zamanlı** ölçümü aylık ve gecikmeli olduğundan, işlem anında “yüksek risk” bilgisi eskimiş olabilir; ayrıca altın-sanayi farkı, GPR’den bağımsız döviz/faiz şoklarına aşırı duyarlıdır.

**Zamanlama ve veri:**  
- Kaynak: Dukascopy türevi XAU BIDASK M15 + StakTrakr dört metal günlük (Neon `observations`, yalnızca `available_as_of` kanıtıyla).  
- Saat: 09 TR = 06 UTC (yaz saati yok varsay). H3 = 09 TR pazartesi–cuma, sonraki 3 iş günü 09 TR.  
- Gecikme: GPR vintage’ı, yayın tarihi `t`’den en az 1 tam takvim günü önce olan en son değer; aylık seri enterpolasyonsuz.  
- Eğitim: 2023-01-02 → 2024-12-31 (yalnızca o dönemde mevcut vintage’lar). Test: 2025-01-01 → 2026-10-07 (açılmış; yalnızca işlem günü itibarıyla bilinenler). Asıl doğrulama: 2027 perspektif kaynak onaylı.

**Örneklem kapıları:**  
- Minimum 300 H3 hedefi eğitimde, 100 testte. BID/ASK işaret uzlaşması ≥%90.  
- GPR vintage kapsamı ≥80% işlem günü.  
- Dört metal M1 tamlık kapısı ≥99%.

**Ablasyonlar:**  
1. Altın tek başına (w_i ile).  
2. Yalnızca sanayi metalleri (v_j ile).  
3. GPR etkileşimsiz (γ=0).  
4. Önceki ay ortalaması yerine son 5 iş günü yenilikleri.  
5. Rejim geçişi (GPR yüksek-düşük eşik) yerine sürekli GPR seviyesi.

**Negatif kontroller:**  
- Her zaman UP (sürekli +1) ve fiyat-öncesiz sabit sinyal karşılaştırması.  
- Sahte kaynak: GPR’yi rastgele 1–30 gün geciktir; performans farkı ≤ şans sınırı olmalı.  
- Zaman eşleşmeli dört metal fiyatını karıştır (permütasyon); H3 doğruluğu %50 ± %5 içinde olmalı.

**Başarı ölçütü:** Dengeli doğruluk (BA) > %55 ve DOWN recall (altın H3 düşüş yakalama) > %55. Özellikle GPR yüksek rejimde işaret tersinme testi: \(\operatorname{sign}(\hat{S})\) ile gerçekleşen H3 yönü arasındaki korelasyon, düşük GPR’de pozitif, yüksek GPR’de negatif olmalı; eğer monoton pozitif kalırsa model reddedilir.

**İki en güçlü başarısızlık nedeni:**  
1. GPR’nin aylık ve gecikmeli yapısı, H3 içi gerçek jeopolitik şokları (ör. hafta sonu haberleri) yakalayamaz; sinyal çoğunlukla gürültü olur.  
2. Altın-sanayi farkı, GPR dışında faiz beklentisi ve dolar endeksi gibi eşzamanlı değişkenlerle yüksek korelasyonlu olduğundan, kalıntı sinyali zayıf ve kararsız kalır; ridge daraltması aşırı büzüşür, işlem maliyeti avantajı yok eder.

**Falsifikasyon:** 2025–26 açık testte BA < %55 veya DOWN recall < %55 veya yüksek GPR rejiminde işaret tersinmesi yoksa model terk edilir. 2027’ye kadar NO_PROMOTION; bağımsız kaynak sertifikalı canlı veri olmadan sonuç bildirilmez.

**Kısa özet:** Bu model, düşük kapasiteli ridge + tek etkileşim terimi ile GPR koşullu altın-sanayi farkı işaretini öngörür. Eğitim 2023–24, test 2025–26 açık, asıl kanıt 2027. H3 hedefi BID/ASK uzlaşmasıyla netleştirilir; aylık ortalama ChHHO düşük frekans kalıcılığından kesin biçimde ayrılır.
