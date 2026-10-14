# OLAY-02 — 96 Olayın Altı Alanlı Sayısal Karar Kayıtları
**Tek OLAY-02 kütüphanesinin alt kanıt eki; yeni manifest değildir.**

**Çalışma zamanı:** 14 Ekim 2026. **Tüm 96 kayıtta** karar öncesi altın fiyat geçmişi, ilgili haber dosyası, tahminin bilinmeyen alanları, **4s/12s/1/3/5 uygun seans** sonrası gerçekleşen MID değişimleri, banka komisyonlu vendor teklif fiyatı vekilleriyle CASH/GOLD maliyetli karşıt senaryoları ve önceki benzer/ters olaylar düzenlendi. Bu kontrol noktası fiyat bacağının **etiket başlangıcından sonraki ilk uygun 09:15 TRT M15 kapanışı**dır, haberin ilk anı değildir.

**Bağlayıcı ayrımlar:** (A) As-of bilinebilir altın geçmişi ≠ ex-post 96 şok örneklemi; (B) gelecek sonuç ve en iyi işlem yalnız sonuç ölçümüdür; (C) gerçek banka kotasyonu/PIT haber konsensusu/DXY/faiz/metallerin bire bir saat paneli eksik; (D) benzerlik altın fiyat deseninin betimleyici yakınlığıdır, eğitim/kalibrasyon veya canlı AL/SAT sinyali değildir.

**Olay Otoritesi:** [OLAY-02 Ana Manifest](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md), [96 haber–veri kaydı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md), [96 sayısal JSON](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json).

### SWING_V1_001

**1. Karar öncesi piyasa durumu:** **2023-01-03 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.124%, 4s +0.694%, 12s EKSİK; 1/3/5 uygun seans +1.282% / +1.738% / +2.609%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.055%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.259%**, CL **+0.663%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_001); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.176% · 12 saat -0.192% · 1 seans +0.280% · 3 seans -0.191% · 5 seans +1.686%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.199**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.010**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.423%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_001`; bu kontrol için orijinal etiketler: `SWING_V1_001`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 0; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `NEAREST_PRICE_PATTERN_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: **YOK**. Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_001

**1. Karar öncesi piyasa durumu:** **2023-01-12 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.032%, 4s +0.163%, 12s +0.354%; 1/3/5 uygun seans +0.045% / +0.222% / +1.532%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.082%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.044%**, CL **-0.013%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_001); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.029% · 12 saat +0.762% · 1 seans +0.543% · 3 seans +1.497% · 5 seans +1.362%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.861**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.684**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.062%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_001`; bu kontrol için orijinal etiketler: `C_CORR_001`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 0; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `NEAREST_PRICE_PATTERN_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: **YOK**. Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_002

**1. Karar öncesi piyasa durumu:** **2023-02-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.024%, 4s +0.068%, 12s -0.190%; 1/3/5 uygun seans +0.684% / +0.081% / -0.008%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.021%**, CL **-0.076%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **-0.010%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_002); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.108% · 12 saat -0.008% · 1 seans +1.318% · 3 seans -2.539% · 5 seans -2.521%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.890**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.679**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.951%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_002`; bu kontrol için orijinal etiketler: `SWING_V1_002`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 1; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `NEAREST_PRICE_PATTERN_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_001](#c_corr_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_002

**1. Karar öncesi piyasa durumu:** **2023-02-03 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.013%, 4s -0.073%, 12s +0.095%; 1/3/5 uygun seans -1.875% / +0.098% / -0.502%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.027%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.047%**, CL **-0.079%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_002); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.221% · 12 saat -2.802% · 1 seans -1.969% · 3 seans -1.951% · 5 seans -2.885%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.470**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.266**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.344%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_002`; bu kontrol için orijinal etiketler: `C_CORR_002`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 2; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `NEAREST_PRICE_PATTERN_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_001](#c_corr_001), [SWING_V1_001](#swing_v1_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_003

**1. Karar öncesi piyasa durumu:** **2023-02-24 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.034%, 4s -0.065%, 12s +0.269%; 1/3/5 uygun seans -0.215% / -0.721% / -0.075%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.004%**, CL **-0.171%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_003); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.182% · 12 saat -0.848% · 1 seans -0.866% · 3 seans +0.401% · 5 seans +0.830%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.783**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.597**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.006%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_003`; bu kontrol için orijinal etiketler: `SWING_V1_003`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 3; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `NEAREST_PRICE_PATTERN_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_001](#c_corr_001), [C_CORR_002](#c_corr_002), [SWING_V1_001](#swing_v1_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_003

**1. Karar öncesi piyasa durumu:** **2023-03-13 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.030%, 4s +0.328%, 12s EKSİK; 1/3/5 uygun seans +2.732% / +3.797% / +1.478%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.162%**, CL **+0.013%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_003); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.191% · 12 saat +1.418% · 1 seans +1.547% · 3 seans +1.969% · 5 seans +5.446%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$100.324**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$101.150**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.507%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_003`; bu kontrol için orijinal etiketler: `C_CORR_003`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 4; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 1. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_001](#swing_v1_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_004

**1. Karar öncesi piyasa durumu:** **2023-05-04 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.209%, 4s -0.172%, 12s +0.744%; 1/3/5 uygun seans +1.290% / +2.970% / +2.095%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.013%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.000%**, CL **+0.377%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_004); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.058% · 12 saat +0.245% · 1 seans +0.319% · 3 seans -0.684% · 5 seans -0.433%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.718**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.522**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.931%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_004`; bu kontrol için orijinal etiketler: `SWING_V1_004;C_CORR_004` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 5; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 2. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_001](#swing_v1_001), [C_CORR_003](#c_corr_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_004

**1. Karar öncesi piyasa durumu:** **2023-05-04 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.209%, 4s -0.172%, 12s +0.744%; 1/3/5 uygun seans +1.290% / +2.970% / +2.095%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.013%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.000%**, CL **+0.377%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_004); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.058% · 12 saat +0.245% · 1 seans +0.319% · 3 seans -0.684% · 5 seans -0.433%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.718**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.522**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.931%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_004`; bu kontrol için orijinal etiketler: `SWING_V1_004;C_CORR_004` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 5; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 2. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_001](#swing_v1_001), [C_CORR_003](#c_corr_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_005

**1. Karar öncesi piyasa durumu:** **2023-06-28 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.026%, 4s +0.040%, 12s +0.235%; 1/3/5 uygun seans -0.488% / +0.029% / -0.823%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.101%**, CL **+0.368%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_005); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.400% · 12 saat -0.174% · 1 seans -0.602% · 3 seans +0.001% · 5 seans +0.401%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.391**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.200**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.608%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_005`; bu kontrol için orijinal etiketler: `SWING_V1_005`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 6; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `SAME_PRICE_CONTEXT_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_002](#swing_v1_002), [C_CORR_002](#c_corr_002). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_006

**1. Karar öncesi piyasa durumu:** **2023-07-18 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.079%, 4s +0.084%, 12s +0.182%; 1/3/5 uygun seans +0.245% / +0.050% / +1.487%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.046%**, CL **-0.107%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_006); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.209% · 12 saat +0.859% · 1 seans +1.030% · 3 seans +0.615% · 5 seans +0.095%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.993**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.807**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.211%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_006`; bu kontrol için orijinal etiketler: `SWING_V1_006`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 7; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 3. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_001](#swing_v1_001), [SWING_V1_004](#swing_v1_004), [C_CORR_003](#c_corr_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_005

**1. Karar öncesi piyasa durumu:** **2023-09-29 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.160%, 4s +0.069%, 12s +0.247%; 1/3/5 uygun seans -0.429% / -2.380% / -2.985%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.116%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.103%**, CL **-0.087%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_005); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.273% · 12 saat -0.948% · 1 seans -1.457% · 3 seans -2.591% · 5 seans -2.528%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.837**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.628**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.009%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_005`; bu kontrol için orijinal etiketler: `C_CORR_005`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 8; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 1. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_003](#swing_v1_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_007

**1. Karar öncesi piyasa durumu:** **2023-10-05 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.191%, 4s -0.171%, 12s +0.309%; 1/3/5 uygun seans +0.245% / -0.909% / -2.771%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.092%**, CL **-0.142%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_007); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.094% · 12 saat -0.234% · 1 seans -0.180% · 3 seans +1.919% · 5 seans +3.030%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$100.278**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$101.104**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.462%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_007`; bu kontrol için orijinal etiketler: `SWING_V1_007`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 8; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 1. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_005](#swing_v1_005). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_006

**1. Karar öncesi piyasa durumu:** **2023-10-13 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.021%, 4s +0.206%, 12s +0.396%; 1/3/5 uygun seans -0.145% / +0.943% / +3.066%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.002%**, CL **+0.036%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_006); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.587% · 12 saat +2.850% · 1 seans +2.057% · 3 seans +3.281% · 5 seans +5.434%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$101.618**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$102.453**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -4.736%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_006`; bu kontrol için orijinal etiketler: `C_CORR_006`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 10; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 1. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_005](#swing_v1_005). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_008

**1. Karar öncesi piyasa durumu:** **2023-10-27 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.022%, 4s +0.003%, 12s +0.133%; 1/3/5 uygun seans +0.142% / +0.538% / +0.473%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.015%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.037%**, CL **+0.106%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_008); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.094% · 12 saat +0.827% · 1 seans +0.582% · 3 seans -0.377% · 5 seans -0.058%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.024**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.829**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.238%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_008`; bu kontrol için orijinal etiketler: `SWING_V1_008`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 11; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 4. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_006](#swing_v1_006), [SWING_V1_001](#swing_v1_001), [SWING_V1_004](#swing_v1_004), [C_CORR_003](#c_corr_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_009

**1. Karar öncesi piyasa durumu:** **2023-11-10 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.009%, 4s -0.068%, 12s -0.254%; 1/3/5 uygun seans +0.369% / -0.802% / -1.485%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.010%**, CL **-0.079%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_009); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.182% · 12 saat -1.060% · 1 seans -0.928% · 3 seans +0.534% · 5 seans +1.391%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.915**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.731**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.136%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_009`; bu kontrol için orijinal etiketler: `SWING_V1_009`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 12; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 3. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_007](#swing_v1_007), [SWING_V1_005](#swing_v1_005), [C_CORR_006](#c_corr_006). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_007

**1. Karar öncesi piyasa durumu:** **2023-12-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.079%, 4s -0.008%, 12s +0.183%; 1/3/5 uygun seans -0.064% / +1.276% / +2.427%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.003%**, CL **+0.066%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.010%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_007); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.215% · 12 saat +1.281% · 1 seans +2.196% · 3 seans -0.826% · 5 seans -0.560%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.573**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.374**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.785%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_010`; bu kontrol için orijinal etiketler: `SWING_V1_010;C_CORR_007` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 13; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 3. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_006](#c_corr_006), [SWING_V1_005](#swing_v1_005), [SWING_V1_007](#swing_v1_007). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_010

**1. Karar öncesi piyasa durumu:** **2023-12-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.079%, 4s -0.008%, 12s +0.183%; 1/3/5 uygun seans -0.064% / +1.276% / +2.427%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.003%**, CL **+0.066%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.010%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_010); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.215% · 12 saat +1.281% · 1 seans +2.196% · 3 seans -0.826% · 5 seans -0.560%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.573**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.374**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.785%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_010`; bu kontrol için orijinal etiketler: `SWING_V1_010;C_CORR_007` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 13; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 3. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_006](#c_corr_006), [SWING_V1_005](#swing_v1_005), [SWING_V1_007](#swing_v1_007). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_008

**1. Karar öncesi piyasa durumu:** **2023-12-04 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.040%, 4s +0.100%, 12s EKSİK; 1/3/5 uygun seans +2.196% / +2.068% / +3.720%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.106%**, CL **-0.150%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_008); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.922% · 12 saat -2.982% · 1 seans -2.524% · 3 seans -2.842% · 5 seans -4.243%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.592**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.379**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.272%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_008`; bu kontrol için orijinal etiketler: `C_CORR_008`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 14; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 5. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_001](#swing_v1_001), [SWING_V1_004](#swing_v1_004), [C_CORR_003](#c_corr_003), [SWING_V1_006](#swing_v1_006), [SWING_V1_008](#swing_v1_008). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_009

**1. Karar öncesi piyasa durumu:** **2023-12-08 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.049%, 4s -0.127%, 12s -0.031%; 1/3/5 uygun seans +0.149% / -0.177% / -0.560%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.058%**, CL **+0.355%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_009); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.039% · 12 saat -1.626% · 1 seans -1.589% · 3 seans -2.603% · 5 seans +0.283%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.828**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.617**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.020%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_009`; bu kontrol için orijinal etiketler: `C_CORR_009`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 14; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 1. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_002](#c_corr_002). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_011

**1. Karar öncesi piyasa durumu:** **2023-12-12 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.101%, 4s +0.294%, 12s +0.529%; 1/3/5 uygun seans -0.467% / -1.902% / -2.222%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.054%**, CL **+0.028%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_011); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.139% · 12 saat -0.450% · 1 seans -0.566% · 3 seans +2.380% · 5 seans +1.804%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$100.730**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$101.560**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.897%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_011`; bu kontrol için orijinal etiketler: `SWING_V1_011`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 14; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `SAME_PRICE_CONTEXT_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_005](#c_corr_005), [SWING_V1_003](#swing_v1_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_010

**1. Karar öncesi piyasa durumu:** **2023-12-19 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.042%, 4s -0.024%, 12s -0.173%; 1/3/5 uygun seans +0.112% / -0.610% / +1.804%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.016%**, CL **+0.207%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_010); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.096% · 12 saat +0.635% · 1 seans +0.878% · 3 seans +1.198% · 5 seans +2.017%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.568**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.389**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.777%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_010`; bu kontrol için orijinal etiketler: `C_CORR_010`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 16; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 5. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_010](#swing_v1_010), [C_CORR_006](#c_corr_006), [SWING_V1_005](#swing_v1_005), [SWING_V1_009](#swing_v1_009), [SWING_V1_007](#swing_v1_007). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_012

**1. Karar öncesi piyasa durumu:** **2023-12-27 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.034%, 4s -0.018%, 12s +0.325%; 1/3/5 uygun seans +0.109% / +1.474% / +2.017%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.045%**, CL **-0.027%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_012); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.128% · 12 saat +0.851% · 1 seans +0.953% · 3 seans +0.463% · 5 seans -0.972%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.844**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.656**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.061%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_012`; bu kontrol için orijinal etiketler: `SWING_V1_012`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 17; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 6. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_008](#swing_v1_008), [SWING_V1_006](#swing_v1_006), [SWING_V1_004](#swing_v1_004), [SWING_V1_001](#swing_v1_001), [C_CORR_008](#c_corr_008). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_013

**1. Karar öncesi piyasa durumu:** **2024-02-14 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.023%, 4s -0.009%, 12s -0.127%; 1/3/5 uygun seans -1.451% / -2.017% / -2.036%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.008%**, CL **-0.064%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_013); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.075% · 12 saat +0.051% · 1 seans +0.030% · 3 seans +1.470% · 5 seans +1.878%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.833**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.653**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.031%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_013`; bu kontrol için orijinal etiketler: `SWING_V1_013`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 19; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 2. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_005](#c_corr_005), [SWING_V1_003](#swing_v1_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_011

**1. Karar öncesi piyasa durumu:** **2024-03-04 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.083%, 4s +0.052%, 12s EKSİK; 1/3/5 uygun seans +1.760% / +2.502% / +2.480%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.007%**, CL **-0.075%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_011); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.080% · 12 saat +1.689% · 1 seans +1.673% · 3 seans +3.449% · 5 seans +4.588%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$101.789**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$102.626**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -4.897%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_011`; bu kontrol için orijinal etiketler: `C_CORR_011`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 20; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 7. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_008](#c_corr_008), [SWING_V1_004](#swing_v1_004), [SWING_V1_001](#swing_v1_001), [C_CORR_003](#c_corr_003), [SWING_V1_012](#swing_v1_012). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_012

**1. Karar öncesi piyasa durumu:** **2024-04-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.043%, 4s +0.191%, 12s EKSİK; 1/3/5 uygun seans +2.994% / +4.058% / +4.002%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.042%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.089%**, CL **+0.060%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.226%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_012); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.395% · 12 saat -0.974% · 1 seans -0.294% · 3 seans +1.551% · 5 seans +3.137%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.918**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.739**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.110%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_012`; bu kontrol için orijinal etiketler: `C_CORR_012`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 20; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 7. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_003](#c_corr_003), [C_CORR_008](#c_corr_008), [SWING_V1_004](#swing_v1_004), [SWING_V1_001](#swing_v1_001), [SWING_V1_012](#swing_v1_012). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_013

**1. Karar öncesi piyasa durumu:** **2024-04-12 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.024%, 4s -0.343%, 12s +1.037%; 1/3/5 uygun seans +2.076% / +1.707% / +4.622%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.072%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.009%**, CL **+0.245%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_013); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.510% · 12 saat -1.298% · 1 seans -1.052% · 3 seans -0.441% · 5 seans -0.081%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.965**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.772**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.180%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_013`; bu kontrol için orijinal etiketler: `C_CORR_013`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 20; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 7. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_008](#c_corr_008), [SWING_V1_004](#swing_v1_004), [SWING_V1_001](#swing_v1_001), [SWING_V1_012](#swing_v1_012), [C_CORR_003](#c_corr_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_014

**1. Karar öncesi piyasa durumu:** **2024-04-19 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.057%, 4s -1.193%, 12s +0.099%; 1/3/5 uygun seans +0.269% / -0.078% / -0.081%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.101%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.020%**, CL **+0.226%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_014); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.075% · 12 saat +0.428% · 1 seans -0.750% · 3 seans -2.341% · 5 seans -1.884%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.088**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.882**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.743%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_014`; bu kontrol için orijinal etiketler: `SWING_V1_014`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 22; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 6. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_009](#swing_v1_009), [C_CORR_010](#c_corr_010), [SWING_V1_005](#swing_v1_005), [SWING_V1_007](#swing_v1_007), [SWING_V1_010](#swing_v1_010). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_014

**1. Karar öncesi piyasa durumu:** **2024-04-24 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.105%, 4s +0.352%, 12s -0.013%; 1/3/5 uygun seans +0.992% / -2.341% / -1.988%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.072%**, CL **+0.096%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_014); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.443% · 12 saat -0.220% · 1 seans -0.345% · 3 seans +0.175% · 5 seans -1.728%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.560**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.372**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.778%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_014`; bu kontrol için orijinal etiketler: `C_CORR_014`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 23; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 6. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_009](#swing_v1_009), [SWING_V1_007](#swing_v1_007), [SWING_V1_005](#swing_v1_005), [C_CORR_010](#c_corr_010), [SWING_V1_010](#swing_v1_010). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_015

**1. Karar öncesi piyasa durumu:** **2024-04-30 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.174%, 4s -0.334%, 12s -0.872%; 1/3/5 uygun seans -0.425% / +0.094% / +0.738%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.078%**, CL **-0.097%** (WTI vadeli, Brent değil), SI **-0.372%** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_015); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.201% · 12 saat -1.134% · 1 seans -1.481% · 3 seans -0.772% · 5 seans -0.067%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.633**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.433**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.843%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_015`; bu kontrol için orijinal etiketler: `SWING_V1_015`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 24; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 6. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_010](#c_corr_010), [SWING_V1_005](#swing_v1_005), [SWING_V1_009](#swing_v1_009), [SWING_V1_010](#swing_v1_010), [C_CORR_006](#c_corr_006). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_015

**1. Karar öncesi piyasa durumu:** **2024-05-15 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.068%, 4s +0.063%, 12s -0.014%; 1/3/5 uygun seans +0.668% / -0.066% / +1.772%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.057%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.016%**, CL **+0.102%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_015); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.482% · 12 saat +1.188% · 1 seans +1.277% · 3 seans +3.849% · 5 seans +2.432%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$102.185**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$103.026**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -5.261%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_015`; bu kontrol için orijinal etiketler: `C_CORR_015`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 26; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `SAME_PRICE_CONTEXT_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_010](#c_corr_010), [SWING_V1_002](#swing_v1_002), [SWING_V1_010](#swing_v1_010), [C_CORR_009](#c_corr_009), [C_CORR_006](#c_corr_006). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_016

**1. Karar öncesi piyasa durumu:** **2024-05-20 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.413%, 4s +0.698%, 12s EKSİK; 1/3/5 uygun seans +2.747% / +3.849% / +4.215%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.031%**, CL **+0.325%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_016); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.311% · 12 saat -0.575% · 1 seans -1.353% · 3 seans -3.582% · 5 seans -4.346%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$94.865**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$95.643**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +2.048%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_016`; bu kontrol için orijinal etiketler: `SWING_V1_016`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 26; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 10. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_012](#c_corr_012), [C_CORR_003](#c_corr_003), [C_CORR_008](#c_corr_008), [C_CORR_011](#c_corr_011), [SWING_V1_001](#swing_v1_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_016

**1. Karar öncesi piyasa durumu:** **2024-05-23 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.461%, 4s -0.449%, 12s -1.039%; 1/3/5 uygun seans -2.248% / -3.582% / -1.133%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.070%**, CL **-0.156%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_016); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.231% · 12 saat -1.112% · 1 seans -0.937% · 3 seans -0.611% · 5 seans -1.477%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.785**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.591**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.002%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_016`; bu kontrol için orijinal etiketler: `C_CORR_016`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 27; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 3. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_013](#swing_v1_013), [C_CORR_005](#c_corr_005), [SWING_V1_003](#swing_v1_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_017

**1. Karar öncesi piyasa durumu:** **2024-06-07 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.208%, 4s +0.238%, 12s +0.298%; 1/3/5 uygun seans +0.490% / +1.145% / +1.467%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.018%**, CL **-0.145%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_017); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -1.709% · 12 saat -3.068% · 1 seans -3.465% · 3 seans -2.640% · 5 seans -2.817%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.793**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.578**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.060%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_017`; bu kontrol için orijinal etiketler: `SWING_V1_017;C_CORR_017` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 29; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `SAME_PRICE_CONTEXT_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_012](#swing_v1_012), [SWING_V1_006](#swing_v1_006), [C_CORR_001](#c_corr_001), [SWING_V1_008](#swing_v1_008), [SWING_V1_004](#swing_v1_004). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_017

**1. Karar öncesi piyasa durumu:** **2024-06-07 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.208%, 4s +0.238%, 12s +0.298%; 1/3/5 uygun seans +0.490% / +1.145% / +1.467%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.018%**, CL **-0.145%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_017); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -1.709% · 12 saat -3.068% · 1 seans -3.465% · 3 seans -2.640% · 5 seans -2.817%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.793**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.578**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.060%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_017`; bu kontrol için orijinal etiketler: `SWING_V1_017;C_CORR_017` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 29; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `SAME_PRICE_CONTEXT_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_012](#swing_v1_012), [SWING_V1_006](#swing_v1_006), [C_CORR_001](#c_corr_001), [SWING_V1_008](#swing_v1_008), [SWING_V1_004](#swing_v1_004). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_018

**1. Karar öncesi piyasa durumu:** **2024-06-13 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.083%, 4s -0.103%, 12s -0.593%; 1/3/5 uygun seans -0.115% / +0.737% / -2.276%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.056%**, CL **-0.115%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_018); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.235% · 12 saat -0.448% · 1 seans -0.066% · 3 seans +0.346% · 5 seans +1.298%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.726**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.537**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.944%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_018`; bu kontrol için orijinal etiketler: `C_CORR_018`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 30; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 9. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_005](#swing_v1_005), [SWING_V1_009](#swing_v1_009), [SWING_V1_007](#swing_v1_007), [SWING_V1_015](#swing_v1_015), [SWING_V1_014](#swing_v1_014). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_019

**1. Karar öncesi piyasa durumu:** **2024-07-16 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.006%, 4s +0.136%, 12s +0.311%; 1/3/5 uygun seans +0.985% / +2.046% / +2.765%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.005%**, CL **-0.147%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_019); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.520% · 12 saat +1.490% · 1 seans +1.456% · 3 seans -0.543% · 5 seans -1.632%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.854**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.661**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.073%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_018`; bu kontrol için orijinal etiketler: `SWING_V1_018;C_CORR_019` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 31; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 11. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_011](#c_corr_011), [SWING_V1_001](#swing_v1_001), [SWING_V1_012](#swing_v1_012), [SWING_V1_004](#swing_v1_004), [C_CORR_008](#c_corr_008). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_018

**1. Karar öncesi piyasa durumu:** **2024-07-16 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.006%, 4s +0.136%, 12s +0.311%; 1/3/5 uygun seans +0.985% / +2.046% / +2.765%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.005%**, CL **-0.147%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_018); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.520% · 12 saat +1.490% · 1 seans +1.456% · 3 seans -0.543% · 5 seans -1.632%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.854**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.661**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.073%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_018`; bu kontrol için orijinal etiketler: `SWING_V1_018;C_CORR_019` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 31; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 11. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_011](#c_corr_011), [SWING_V1_001](#swing_v1_001), [SWING_V1_012](#swing_v1_012), [SWING_V1_004](#swing_v1_004), [C_CORR_008](#c_corr_008). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_020

**1. Karar öncesi piyasa durumu:** **2024-07-25 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.062%, 4s +0.022%, 12s -1.317%; 1/3/5 uygun seans -1.760% / -1.030% / -3.647%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.099%**, CL **+0.065%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_020); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.041% · 12 saat -0.894% · 1 seans -0.252% · 3 seans +0.522% · 5 seans +2.931%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.908**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.719**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.121%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_019`; bu kontrol için orijinal etiketler: `SWING_V1_019;C_CORR_020` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 32; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 4. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_013](#swing_v1_013), [C_CORR_005](#c_corr_005), [C_CORR_016](#c_corr_016), [SWING_V1_003](#swing_v1_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_019

**1. Karar öncesi piyasa durumu:** **2024-07-25 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.062%, 4s +0.022%, 12s -1.317%; 1/3/5 uygun seans -1.760% / -1.030% / -3.647%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.099%**, CL **+0.065%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_019); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.041% · 12 saat -0.894% · 1 seans -0.252% · 3 seans +0.522% · 5 seans +2.931%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.908**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.719**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.121%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_019`; bu kontrol için orijinal etiketler: `SWING_V1_019;C_CORR_020` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 32; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 4. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_013](#swing_v1_013), [C_CORR_005](#c_corr_005), [C_CORR_016](#c_corr_016), [SWING_V1_003](#swing_v1_003). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_021

**1. Karar öncesi piyasa durumu:** **2024-08-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.076%, 4s -0.115%, 12s +0.977%; 1/3/5 uygun seans +1.139% / +2.153% / +2.931%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.108%**, CL **-0.025%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_021); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.478% · 12 saat -0.294% · 1 seans +0.783% · 3 seans -2.005% · 5 seans -2.096%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.416**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.210**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.403%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_021`; bu kontrol için orijinal etiketler: `C_CORR_021`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 33; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 12. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_018](#swing_v1_018), [C_CORR_011](#c_corr_011), [SWING_V1_004](#swing_v1_004), [C_CORR_008](#c_corr_008), [C_CORR_013](#c_corr_013). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_022

**1. Karar öncesi piyasa durumu:** **2024-08-12 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.105%, 4s +0.371%, 12s EKSİK; 1/3/5 uygun seans +0.697% / +1.798% / +0.114%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.007%**, CL **+0.052%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_022); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.301% · 12 saat +1.395% · 1 seans +1.087% · 3 seans +0.924% · 5 seans +2.829%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.296**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.115**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.511%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_022`; bu kontrol için orijinal etiketler: `C_CORR_022`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 33; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 12. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_008](#swing_v1_008), [SWING_V1_012](#swing_v1_012), [SWING_V1_018](#swing_v1_018), [SWING_V1_001](#swing_v1_001), [SWING_V1_006](#swing_v1_006). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_023

**1. Karar öncesi piyasa durumu:** **2024-09-13 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.144%, 4s +0.028%, 12s +0.383%; 1/3/5 uygun seans +1.722% / +2.313% / +1.782%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.019%**, CL **-0.043%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_023); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.119% · 12 saat +0.721% · 1 seans +0.890% · 3 seans +0.138% · 5 seans +1.292%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.528**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.337**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.743%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_023`; bu kontrol için orijinal etiketler: `C_CORR_023`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 33; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 12. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_011](#c_corr_011), [SWING_V1_004](#swing_v1_004), [SWING_V1_018](#swing_v1_018), [C_CORR_008](#c_corr_008), [SWING_V1_001](#swing_v1_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_024

**1. Karar öncesi piyasa durumu:** **2024-09-24 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.380%, 4s +0.025%, 12s +0.009%; 1/3/5 uygun seans -0.049% / +1.980% / +1.785%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.027%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.154%**, CL **+0.000%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **-0.027%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_024); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.141% · 12 saat +0.985% · 1 seans +1.037% · 3 seans +1.470% · 5 seans +0.589%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.837**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.657**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.033%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_024`; bu kontrol için orijinal etiketler: `C_CORR_024`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 33; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 10. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_010](#swing_v1_010), [C_CORR_006](#c_corr_006), [SWING_V1_015](#swing_v1_015), [C_CORR_010](#c_corr_010), [SWING_V1_005](#swing_v1_005). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_025

**1. Karar öncesi piyasa durumu:** **2024-10-22 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.073%, 4s +0.107%, 12s +0.474%; 1/3/5 uygun seans +0.302% / +1.890% / +3.336%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.042%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.010%**, CL ****EKSİK**** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_025); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.079% · 12 saat +0.485% · 1 seans +0.726% · 3 seans -0.210% · 5 seans +0.692%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.189**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.995**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.402%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_025`; bu kontrol için orijinal etiketler: `C_CORR_025`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 33; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 12. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_012](#swing_v1_012), [SWING_V1_018](#swing_v1_018), [SWING_V1_004](#swing_v1_004), [SWING_V1_006](#swing_v1_006), [SWING_V1_001](#swing_v1_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_020

**1. Karar öncesi piyasa durumu:** **2024-10-30 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.231%, 4s +0.222%, 12s +0.588%; 1/3/5 uygun seans +1.247% / +2.162% / +1.213%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.056%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.037%**, CL **+0.074%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.198%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_020); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.015% · 12 saat +0.111% · 1 seans -0.003% · 3 seans -1.710% · 5 seans -1.901%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.712**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.504**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.102%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_020`; bu kontrol için orijinal etiketler: `SWING_V1_020`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 37; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 15. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_022](#c_corr_022), [SWING_V1_018](#swing_v1_018), [C_CORR_011](#c_corr_011), [C_CORR_021](#c_corr_021), [SWING_V1_001](#swing_v1_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_026

**1. Karar öncesi piyasa durumu:** **2024-11-06 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.235%, 4s -0.407%, 12s -0.339%; 1/3/5 uygun seans -0.054% / -0.875% / -1.901%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.086%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.066%**, CL **-0.478%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_026); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.326% · 12 saat -2.414% · 1 seans -2.856% · 3 seans -2.253% · 5 seans -4.690%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.172**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.963**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.659%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_026`; bu kontrol için orijinal etiketler: `C_CORR_026`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 39; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 5. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_003](#swing_v1_003), [C_CORR_005](#c_corr_005), [SWING_V1_013](#swing_v1_013), [SWING_V1_019](#swing_v1_019), [C_CORR_016](#c_corr_016). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_021

**1. Karar öncesi piyasa durumu:** **2024-11-15 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.370%, 4s -0.415%, 12s -0.512%; 1/3/5 uygun seans -0.021% / -1.906% / -4.946%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.092%**, CL **-0.206%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_021); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.258% · 12 saat +0.184% · 1 seans +1.081% · 3 seans +2.865% · 5 seans +5.106%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$101.208**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$102.041**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -4.349%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_021`; bu kontrol için orijinal etiketler: `SWING_V1_021`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 39; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 5. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_005](#c_corr_005), [SWING_V1_013](#swing_v1_013), [SWING_V1_019](#swing_v1_019), [SWING_V1_003](#swing_v1_003), [C_CORR_016](#c_corr_016). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_027

**1. Karar öncesi piyasa durumu:** **2024-11-20 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.187%, 4s -0.392%, 12s +0.076%; 1/3/5 uygun seans +0.329% / +2.865% / +1.015%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.043%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.028%**, CL ****EKSİK**** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_027); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.287% · 12 saat +0.688% · 1 seans +1.088% · 3 seans +1.384% · 5 seans +0.401%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.752**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.573**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.953%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_027`; bu kontrol için orijinal etiketler: `C_CORR_027`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 41; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 17. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_012](#swing_v1_012), [SWING_V1_004](#swing_v1_004), [SWING_V1_018](#swing_v1_018), [C_CORR_025](#c_corr_025), [C_CORR_023](#c_corr_023). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_022

**1. Karar öncesi piyasa durumu:** **2024-11-22 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.007%, 4s +0.318%, 12s +0.637%; 1/3/5 uygun seans +1.079% / +2.515% / +5.106%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.209%**, CL **-0.199%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_022); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.717% · 12 saat +0.770% · 1 seans -0.778% · 3 seans -1.740% · 5 seans -0.826%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.677**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.471**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.133%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_022`; bu kontrol için orijinal etiketler: `SWING_V1_022`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 41; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 17. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_018](#swing_v1_018), [C_CORR_025](#c_corr_025), [C_CORR_021](#c_corr_021), [C_CORR_008](#c_corr_008), [C_CORR_013](#c_corr_013). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_028

**1. Karar öncesi piyasa durumu:** **2024-11-25 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.223%, 4s -1.284%, 12s EKSİK; 1/3/5 uygun seans -0.778% / +1.384% / +3.173%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.026%**, CL **-0.254%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_028); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.113% · 12 saat -1.653% · 1 seans -1.596% · 3 seans -1.293% · 5 seans -1.629%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.118**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.917**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.321%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_023`; bu kontrol için orijinal etiketler: `SWING_V1_023;C_CORR_028` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 41; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 11. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_015](#swing_v1_015), [SWING_V1_010](#swing_v1_010), [SWING_V1_014](#swing_v1_014), [C_CORR_024](#c_corr_024), [C_CORR_006](#c_corr_006). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_023

**1. Karar öncesi piyasa durumu:** **2024-11-25 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.223%, 4s -1.284%, 12s EKSİK; 1/3/5 uygun seans -0.778% / +1.384% / +3.173%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.026%**, CL **-0.254%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_023); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.113% · 12 saat -1.653% · 1 seans -1.596% · 3 seans -1.293% · 5 seans -1.629%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.118**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.917**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.321%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_023`; bu kontrol için orijinal etiketler: `SWING_V1_023;C_CORR_028` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 41; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 11. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_015](#swing_v1_015), [SWING_V1_010](#swing_v1_010), [SWING_V1_014](#swing_v1_014), [C_CORR_024](#c_corr_024), [C_CORR_006](#c_corr_006). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_029

**1. Karar öncesi piyasa durumu:** **2024-12-11 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.476%, 4s -0.290%, 12s -0.083%; 1/3/5 uygun seans +0.921% / +2.053% / +1.662%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.004%**, CL **+0.116%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_029); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.223% · 12 saat +1.001% · 1 seans +0.660% · 3 seans -1.486% · 5 seans -1.727%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.904**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.749**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.149%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_024`; bu kontrol için orijinal etiketler: `SWING_V1_024;C_CORR_029` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 44; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 1. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_001](#c_corr_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_024

**1. Karar öncesi piyasa durumu:** **2024-12-11 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.476%, 4s -0.290%, 12s -0.083%; 1/3/5 uygun seans +0.921% / +2.053% / +1.662%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.004%**, CL **+0.116%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_024); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.223% · 12 saat +1.001% · 1 seans +0.660% · 3 seans -1.486% · 5 seans -1.727%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.904**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.749**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.149%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_024`; bu kontrol için orijinal etiketler: `SWING_V1_024;C_CORR_029` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 44; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 1. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_001](#c_corr_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_030

**1. Karar öncesi piyasa durumu:** **2024-12-18 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.008%, 4s -0.156%, 12s -0.010%; 1/3/5 uygun seans -0.201% / -1.534% / -1.727%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.028%**, CL **-0.029%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_030); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.113% · 12 saat -0.325% · 1 seans -1.537% · 3 seans -0.717% · 5 seans -0.711%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.682**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.485**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.904%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_025`; bu kontrol için orijinal etiketler: `SWING_V1_025;C_CORR_030` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 45; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `SAME_PRICE_CONTEXT_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_026](#c_corr_026), [SWING_V1_011](#swing_v1_011), [SWING_V1_003](#swing_v1_003), [C_CORR_005](#c_corr_005), [SWING_V1_013](#swing_v1_013). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_025

**1. Karar öncesi piyasa durumu:** **2024-12-18 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.008%, 4s -0.156%, 12s -0.010%; 1/3/5 uygun seans -0.201% / -1.534% / -1.727%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.028%**, CL **-0.029%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**SI.n.0 gümüş H1 kaynağı GitHub arşivinde VAR (2022–24); bu vakaya ait tam kapanmış 05:00–06:00 UTC bar henüz ham `.gz` üzerinden hesaplanmadı. `SI.c.0` boşluğu gümüş veri yokluğu değildir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_025); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.113% · 12 saat -0.325% · 1 seans -1.537% · 3 seans -0.717% · 5 seans -0.711%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.682**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.485**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.904%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_025`; bu kontrol için orijinal etiketler: `SWING_V1_025;C_CORR_030` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 45; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 0. **Kullanılan eşleştirme katmanı:** `SAME_PRICE_CONTEXT_ONLY`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_026](#c_corr_026), [SWING_V1_011](#swing_v1_011), [SWING_V1_003](#swing_v1_003), [C_CORR_005](#c_corr_005), [SWING_V1_013](#swing_v1_013). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_031

**1. Karar öncesi piyasa durumu:** **2025-02-05 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.153%, 4s +0.210%, 12s +0.498%; 1/3/5 uygun seans +1.563% / +2.271% / +3.537%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.102%**, CL **+0.304%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_031); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.410% · 12 saat +0.435% · 1 seans +0.361% · 3 seans +0.841% · 5 seans +1.152%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.207**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.044**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.442%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_031`; bu kontrol için orijinal etiketler: `C_CORR_031`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 46; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 19. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_011](#c_corr_011), [C_CORR_008](#c_corr_008), [SWING_V1_018](#swing_v1_018), [C_CORR_021](#c_corr_021), [SWING_V1_022](#swing_v1_022). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_026

**1. Karar öncesi piyasa durumu:** **2025-02-24 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.091%, 4s +0.343%, 12s EKSİK; 1/3/5 uygun seans +0.316% / +0.111% / +1.560%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.084%**, CL **+0.114%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_026); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.166% · 12 saat +0.216% · 1 seans -0.052% · 3 seans -1.490% · 5 seans -2.483%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.921**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.724**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.125%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_026`; bu kontrol için orijinal etiketler: `SWING_V1_026`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 47; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 20. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_006](#swing_v1_006), [SWING_V1_008](#swing_v1_008), [SWING_V1_012](#swing_v1_012), [C_CORR_022](#c_corr_022), [C_CORR_025](#c_corr_025). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_027

**1. Karar öncesi piyasa durumu:** **2025-02-28 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.026%, 4s -0.396%, 12s -0.790%; 1/3/5 uygun seans -1.079% / -2.502% / -2.244%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.042%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.032%**, CL **-0.071%** (WTI vadeli, Brent değil), SI **-0.270%** (gümüş vadeli, spot XAG değil), GC **+0.133%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_027); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.032% · 12 saat -0.701% · 1 seans +0.071% · 3 seans +1.968% · 5 seans +1.629%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$100.325**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$101.154**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.513%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_027`; bu kontrol için orijinal etiketler: `SWING_V1_027`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 48; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 7. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_013](#swing_v1_013), [C_CORR_005](#c_corr_005), [SWING_V1_019](#swing_v1_019), [C_CORR_026](#c_corr_026), [C_CORR_016](#c_corr_016). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_032

**1. Karar öncesi piyasa durumu:** **2025-03-13 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.174%, 4s -0.100%, 12s +0.105%; 1/3/5 uygun seans +0.623% / +0.949% / +0.552%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.087%**, CL **-0.222%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_032); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.217% · 12 saat +1.534% · 1 seans +1.552% · 3 seans +2.619% · 5 seans +3.771%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$100.967**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$101.795**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -4.121%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_032`; bu kontrol için orijinal etiketler: `C_CORR_032`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 49; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 21. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_008](#swing_v1_008), [SWING_V1_006](#swing_v1_006), [SWING_V1_012](#swing_v1_012), [SWING_V1_026](#swing_v1_026), [C_CORR_022](#c_corr_022). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_033

**1. Karar öncesi piyasa durumu:** **2025-03-31 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.486%, 4s +0.837%, 12s EKSİK; 1/3/5 uygun seans +1.439% / +3.307% / +3.521%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.047%**, CL **+0.319%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.144%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_033); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.314% · 12 saat -0.157% · 1 seans +0.191% · 3 seans +0.201% · 5 seans -3.131%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.584**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.398**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.806%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_033`; bu kontrol için orijinal etiketler: `C_CORR_033`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 49; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 21. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_016](#swing_v1_016), [C_CORR_031](#c_corr_031), [SWING_V1_001](#swing_v1_001), [SWING_V1_020](#swing_v1_020), [C_CORR_011](#c_corr_011). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_028

**1. Karar öncesi piyasa durumu:** **2025-04-02 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.036%, 4s -0.550%, 12s -0.044%; 1/3/5 uygun seans -0.488% / +1.137% / +2.999%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.112%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.166%**, CL **-0.182%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_028); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.470% · 12 saat +0.252% · 1 seans +0.500% · 3 seans -2.842% · 5 seans -3.046%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.590**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.379**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.269%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_028`; bu kontrol için orijinal etiketler: `SWING_V1_028`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 50; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 12. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_010](#swing_v1_010), [C_CORR_006](#c_corr_006), [SWING_V1_023](#swing_v1_023), [SWING_V1_015](#swing_v1_015), [C_CORR_024](#c_corr_024). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_034

**1. Karar öncesi piyasa durumu:** **2025-04-04 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.177%, 4s -0.169%, 12s +0.006%; 1/3/5 uygun seans -0.753% / -0.743% / +0.877%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.097%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.862%**, CL **+0.333%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **-0.045%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_034); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.389% · 12 saat -2.676% · 1 seans -2.592% · 3 seans -2.797% · 5 seans +2.817%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.632**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.421**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.217%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_034`; bu kontrol için orijinal etiketler: `C_CORR_034`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 51; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 2. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_009](#c_corr_009), [C_CORR_002](#c_corr_002). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_029

**1. Karar öncesi piyasa durumu:** **2025-04-07 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.088%, 4s -0.852%, 12s EKSİK; 1/3/5 uygun seans -2.592% / -2.842% / -3.131%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.124%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.158%**, CL **-0.265%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **-0.135%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_029); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.010% · 12 saat -1.846% · 1 seans -0.737% · 3 seans +3.254% · 5 seans +6.730%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$101.587**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$102.425**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -4.715%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_029`; bu kontrol için orijinal etiketler: `SWING_V1_029`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 51; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 8. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_016](#c_corr_016), [SWING_V1_027](#swing_v1_027), [SWING_V1_013](#swing_v1_013), [SWING_V1_019](#swing_v1_019), [C_CORR_005](#c_corr_005). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_035

**1. Karar öncesi piyasa durumu:** **2025-04-09 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.166%, 4s +0.436%, 12s +1.341%; 1/3/5 uygun seans +0.530% / -2.797% / -3.046%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.057%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.421%**, CL **+0.877%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_035); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.684% · 12 saat +1.054% · 1 seans +3.471% · 3 seans +6.955% · 5 seans +8.911%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$105.225**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$106.100**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -8.015%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_035`; bu kontrol için orijinal etiketler: `C_CORR_035`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 51; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 12. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_014](#c_corr_014), [SWING_V1_007](#swing_v1_007), [SWING_V1_009](#swing_v1_009), [SWING_V1_005](#swing_v1_005), [C_CORR_018](#c_corr_018). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_030

**1. Karar öncesi piyasa durumu:** **2025-04-21 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.154%, 4s +0.314%, 12s EKSİK; 1/3/5 uygun seans +1.720% / +5.021% / +6.043%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.136%**, CL **+0.393%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.119%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_030); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.262% · 12 saat +0.934% · 1 seans +3.227% · 3 seans -1.909% · 5 seans -2.825%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.505**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.301**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.301%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_030`; bu kontrol için orijinal etiketler: `SWING_V1_030`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 54; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 23. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_012](#c_corr_012), [SWING_V1_016](#swing_v1_016), [SWING_V1_022](#swing_v1_022), [C_CORR_033](#c_corr_033), [C_CORR_031](#c_corr_031). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_036

**1. Karar öncesi piyasa durumu:** **2025-04-23 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.895%, 4s -1.646%, 12s -2.383%; 1/3/5 uygun seans -5.170% / -0.427% / +2.805%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.085%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.084%**, CL **+0.187%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_036); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.366% · 12 saat -0.926% · 1 seans +0.206% · 3 seans -0.731% · 5 seans -0.250%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.664**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.472**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.891%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_036`; bu kontrol için orijinal etiketler: `C_CORR_036`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 56; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 14. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_023](#swing_v1_023), [SWING_V1_015](#swing_v1_015), [SWING_V1_028](#swing_v1_028), [C_CORR_024](#c_corr_024), [SWING_V1_005](#swing_v1_005). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_037

**1. Karar öncesi piyasa durumu:** **2025-05-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.273%, 4s -0.072%, 12s -2.079%; 1/3/5 uygun seans -2.120% / -1.646% / -2.566%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.100%**, CL **+0.086%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.379%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_037); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.708% · 12 saat -0.641% · 1 seans +0.513% · 3 seans +3.831% · 5 seans +3.307%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$102.151**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$102.999**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -5.239%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_031`; bu kontrol için orijinal etiketler: `SWING_V1_031;C_CORR_037` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 56; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 9. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_019](#swing_v1_019), [SWING_V1_027](#swing_v1_027), [SWING_V1_029](#swing_v1_029), [SWING_V1_013](#swing_v1_013), [C_CORR_016](#c_corr_016). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_031

**1. Karar öncesi piyasa durumu:** **2025-05-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.273%, 4s -0.072%, 12s -2.079%; 1/3/5 uygun seans -2.120% / -1.646% / -2.566%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.100%**, CL **+0.086%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.379%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_031); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.708% · 12 saat -0.641% · 1 seans +0.513% · 3 seans +3.831% · 5 seans +3.307%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$102.151**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$102.999**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -5.239%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_031`; bu kontrol için orijinal etiketler: `SWING_V1_031;C_CORR_037` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 56; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 9. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_019](#swing_v1_019), [SWING_V1_027](#swing_v1_027), [SWING_V1_029](#swing_v1_029), [SWING_V1_013](#swing_v1_013), [C_CORR_016](#c_corr_016). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_038

**1. Karar öncesi piyasa durumu:** **2025-05-06 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.106%, 4s -0.600%, 12s +1.384%; 1/3/5 uygun seans +3.141% / +3.831% / +1.488%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.252%**, CL **-0.241%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_038); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.622% · 12 saat +1.486% · 1 seans +0.915% · 3 seans -1.263% · 5 seans -3.301%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.149**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.948**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.356%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_032`; bu kontrol için orijinal etiketler: `SWING_V1_032;C_CORR_038` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 57; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 24. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_003](#c_corr_003), [C_CORR_012](#c_corr_012), [C_CORR_011](#c_corr_011), [C_CORR_023](#c_corr_023), [C_CORR_008](#c_corr_008). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_032

**1. Karar öncesi piyasa durumu:** **2025-05-06 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.106%, 4s -0.600%, 12s +1.384%; 1/3/5 uygun seans +3.141% / +3.831% / +1.488%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.252%**, CL **-0.241%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_032); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.622% · 12 saat +1.486% · 1 seans +0.915% · 3 seans -1.263% · 5 seans -3.301%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.149**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.948**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.356%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_032`; bu kontrol için orijinal etiketler: `SWING_V1_032;C_CORR_038` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 57; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 24. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_003](#c_corr_003), [C_CORR_012](#c_corr_012), [C_CORR_011](#c_corr_011), [C_CORR_023](#c_corr_023), [C_CORR_008](#c_corr_008). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_039

**1. Karar öncesi piyasa durumu:** **2025-05-09 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.246%, 4s +1.300%, 12s +0.331%; 1/3/5 uygun seans -0.763% / -1.263% / +1.996%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.045%**, CL **-0.033%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_039); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.204% · 12 saat +0.580% · 1 seans -1.203% · 3 seans -2.603% · 5 seans -2.746%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.822**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.614**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.017%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_039`; bu kontrol için orijinal etiketler: `C_CORR_039`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 58; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 15. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_010](#c_corr_010), [C_CORR_006](#c_corr_006), [SWING_V1_005](#swing_v1_005), [SWING_V1_010](#swing_v1_010), [SWING_V1_015](#swing_v1_015). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_033

**1. Karar öncesi piyasa durumu:** **2025-05-14 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.261%, 4s -0.169%, 12s -0.403%; 1/3/5 uygun seans -0.550% / -2.603% / -4.705%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.045%**, CL **+0.079%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_033); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.029% · 12 saat -1.763% · 1 seans -3.290% · 3 seans -0.199% · 5 seans +2.511%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.189**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.004**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.415%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_033`; bu kontrol için orijinal etiketler: `SWING_V1_033`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 58; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 9. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_005](#c_corr_005), [SWING_V1_027](#swing_v1_027), [SWING_V1_013](#swing_v1_013), [SWING_V1_021](#swing_v1_021), [SWING_V1_019](#swing_v1_019). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_040

**1. Karar öncesi piyasa durumu:** **2025-05-15 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.404%, 4s -1.505%, 12s -1.555%; 1/3/5 uygun seans -3.290% / -4.661% / -6.526%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.029%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.248%**, CL **-0.519%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **-0.258%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_040); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +1.505% · 12 saat +3.124% · 1 seans +3.250% · 3 seans +2.874% · 5 seans +6.599%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$101.220**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$102.058**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -4.360%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_040`; bu kontrol için orijinal etiketler: `C_CORR_040`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 59; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 10. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_029](#swing_v1_029), [C_CORR_016](#c_corr_016), [SWING_V1_027](#swing_v1_027), [SWING_V1_019](#swing_v1_019), [SWING_V1_031](#swing_v1_031). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_041

**1. Karar öncesi piyasa durumu:** **2025-05-21 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.441%, 4s +0.513%, 12s +0.862%; 1/3/5 uygun seans +3.037% / +2.662% / +2.511%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.043%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.124%**, CL **-0.158%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_041); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.095% · 12 saat -0.043% · 1 seans +0.566% · 3 seans +0.953% · 5 seans -0.433%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.323**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.142**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.540%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_041`; bu kontrol için orijinal etiketler: `C_CORR_041`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 60; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 25. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_016](#swing_v1_016), [C_CORR_003](#c_corr_003), [C_CORR_012](#c_corr_012), [C_CORR_008](#c_corr_008), [C_CORR_031](#c_corr_031). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_042

**1. Karar öncesi piyasa durumu:** **2025-06-13 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.084%, 4s -0.221%, 12s +1.125%; 1/3/5 uygun seans +1.509% / +3.034% / +1.765%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.124%**, CL **-0.367%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_042); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.067% · 12 saat +0.320% · 1 seans -0.096% · 3 seans -1.110% · 5 seans -2.166%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.298**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.099**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.506%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_034`; bu kontrol için orijinal etiketler: `SWING_V1_034;C_CORR_042` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 63; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 26. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_004](#swing_v1_004), [C_CORR_011](#c_corr_011), [C_CORR_023](#c_corr_023), [C_CORR_021](#c_corr_021), [SWING_V1_018](#swing_v1_018). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_034

**1. Karar öncesi piyasa durumu:** **2025-06-13 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.084%, 4s -0.221%, 12s +1.125%; 1/3/5 uygun seans +1.509% / +3.034% / +1.765%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.124%**, CL **-0.367%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_034); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.067% · 12 saat +0.320% · 1 seans -0.096% · 3 seans -1.110% · 5 seans -2.166%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.298**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.099**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.506%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_034`; bu kontrol için orijinal etiketler: `SWING_V1_034;C_CORR_042` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 63; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 26. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_004](#swing_v1_004), [C_CORR_011](#c_corr_011), [C_CORR_023](#c_corr_023), [C_CORR_021](#c_corr_021), [SWING_V1_018](#swing_v1_018). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_035

**1. Karar öncesi piyasa durumu:** **2025-06-27 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.027%, 4s -0.698%, 12s -1.179%; 1/3/5 uygun seans -1.141% / -0.903% / -1.596%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.089%**, CL **+0.061%** (WTI vadeli, Brent değil), SI **+0.302%** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_035); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.185% · 12 saat -0.613% · 1 seans -0.138% · 3 seans +1.292% · 5 seans +1.428%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.661**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.483**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.865%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_035`; bu kontrol için orijinal etiketler: `SWING_V1_035`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 64; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 12. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_027](#swing_v1_027), [SWING_V1_019](#swing_v1_019), [C_CORR_026](#c_corr_026), [SWING_V1_013](#swing_v1_013), [SWING_V1_031](#swing_v1_031). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_043

**1. Karar öncesi piyasa durumu:** **2025-07-22 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.071%, 4s -0.098%, 12s -0.242%; 1/3/5 uygun seans +0.566% / +1.581% / +0.685%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.056%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.035%**, CL **+0.135%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_043); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.039% · 12 saat +1.291% · 1 seans +1.108% · 3 seans -0.853% · 5 seans -1.948%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.553**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.356**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.765%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_036`; bu kontrol için orijinal etiketler: `SWING_V1_036;C_CORR_043` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 65; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 27. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_032](#c_corr_032), [SWING_V1_008](#swing_v1_008), [SWING_V1_012](#swing_v1_012), [C_CORR_022](#c_corr_022), [C_CORR_027](#c_corr_027). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_036

**1. Karar öncesi piyasa durumu:** **2025-07-22 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.071%, 4s -0.098%, 12s -0.242%; 1/3/5 uygun seans +0.566% / +1.581% / +0.685%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.056%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.035%**, CL **+0.135%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_036); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.039% · 12 saat +1.291% · 1 seans +1.108% · 3 seans -0.853% · 5 seans -1.948%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.553**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.356**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.765%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_036`; bu kontrol için orijinal etiketler: `SWING_V1_036;C_CORR_043` (**kısa/uzun ufuk yönü çelişiyor; H3 sonuç aynıdır**). **Karar anından önce tamamlanmış bağımsız aday havuzu:** 65; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 27. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_032](#c_corr_032), [SWING_V1_008](#swing_v1_008), [SWING_V1_012](#swing_v1_012), [C_CORR_022](#c_corr_022), [C_CORR_027](#c_corr_027). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_044

**1. Karar öncesi piyasa durumu:** **2025-07-29 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.145%, 4s +0.058%, 12s +0.259%; 1/3/5 uygun seans -0.667% / -1.645% / -1.948%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.042%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.019%**, CL **+0.150%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_044); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.130% · 12 saat +0.246% · 1 seans +0.122% · 3 seans -0.750% · 5 seans +1.533%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.653**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.456**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.866%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_044`; bu kontrol için orijinal etiketler: `C_CORR_044`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 66; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 13. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_005](#c_corr_005), [SWING_V1_013](#swing_v1_013), [SWING_V1_003](#swing_v1_003), [SWING_V1_027](#swing_v1_027), [C_CORR_026](#c_corr_026). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_037

**1. Karar öncesi piyasa durumu:** **2025-07-30 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.093%, 4s -0.159%, 12s -0.124%; 1/3/5 uygun seans +0.122% / -0.985% / -2.905%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.001%**, CL **-0.202%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **-0.069%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_037); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.204% · 12 saat -0.740% · 1 seans -0.646% · 3 seans +1.058% · 5 seans +1.550%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.418**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.234**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.631%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_037`; bu kontrol için orijinal etiketler: `SWING_V1_037`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 66; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 16. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_007](#swing_v1_007), [SWING_V1_009](#swing_v1_009), [C_CORR_018](#c_corr_018), [SWING_V1_005](#swing_v1_005), [C_CORR_014](#c_corr_014). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_045

**1. Karar öncesi piyasa durumu:** **2025-08-07 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.011%, 4s -0.098%, 12s +0.248%; 1/3/5 uygun seans +0.093% / +0.580% / +2.305%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.042%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.078%**, CL **-0.139%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_045); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.024% · 12 saat +0.383% · 1 seans +0.476% · 3 seans -0.888% · 5 seans -0.570%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.512**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.315**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.727%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_045`; bu kontrol için orijinal etiketler: `C_CORR_045`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 67; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 28. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_012](#swing_v1_012), [SWING_V1_006](#swing_v1_006), [SWING_V1_008](#swing_v1_008), [SWING_V1_026](#swing_v1_026), [C_CORR_025](#c_corr_025). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_046

**1. Karar öncesi piyasa durumu:** **2025-09-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.227%, 4s +0.691%, 12s EKSİK; 1/3/5 uygun seans +2.079% / +3.044% / +3.407%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.006%**, CL **+0.110%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_046); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.365% · 12 saat -0.166% · 1 seans +0.228% · 3 seans +1.422% · 5 seans +3.217%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.787**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.610**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.989%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_046`; bu kontrol için orijinal etiketler: `C_CORR_046`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 68; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 28. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_033](#c_corr_033), [C_CORR_031](#c_corr_031), [SWING_V1_016](#swing_v1_016), [C_CORR_008](#c_corr_008), [C_CORR_011](#c_corr_011). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_047

**1. Karar öncesi piyasa durumu:** **2025-09-23 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.219%, 4s +0.291%, 12s +0.233%; 1/3/5 uygun seans +1.457% / +3.228% / +1.947%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.037%**, CL **-0.048%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_047); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.840% · 12 saat +0.611% · 1 seans +0.501% · 3 seans -0.086% · 5 seans +2.987%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.313**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.118**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.518%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_047`; bu kontrol için orijinal etiketler: `C_CORR_047`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 68; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 28. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_020](#swing_v1_020), [C_CORR_011](#c_corr_011), [C_CORR_031](#c_corr_031), [SWING_V1_018](#swing_v1_018), [C_CORR_023](#c_corr_023). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_048

**1. Karar öncesi piyasa durumu:** **2025-10-01 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.144%, 4s -0.231%, 12s +0.461%; 1/3/5 uygun seans -0.208% / +2.860% / +2.260%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.050%**, CL **-0.272%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC **+0.127%**. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_048); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.785% · 12 saat +0.031% · 1 seans +0.342% · 3 seans +1.741% · 5 seans +4.372%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$100.106**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.927**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.293%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_048`; bu kontrol için orijinal etiketler: `C_CORR_048`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 68; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 16. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_024](#c_corr_024), [SWING_V1_010](#swing_v1_010), [SWING_V1_028](#swing_v1_028), [C_CORR_006](#c_corr_006), [SWING_V1_023](#swing_v1_023). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_049

**1. Karar öncesi piyasa durumu:** **2025-10-17 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.205%, 4s +0.720%, 12s +1.730%; 1/3/5 uygun seans +3.243% / +6.024% / +9.762%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.187%**, CL **-0.035%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_049); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.476% · 12 saat -2.879% · 1 seans -2.639% · 3 seans -5.076% · 5 seans -6.319%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$93.391**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$94.164**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +3.651%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_049`; bu kontrol için orijinal etiketler: `C_CORR_049`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 68; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 28. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_030](#swing_v1_030), [C_CORR_012](#c_corr_012), [SWING_V1_016](#swing_v1_016), [SWING_V1_022](#swing_v1_022), [C_CORR_013](#c_corr_013). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_038

**1. Karar öncesi piyasa durumu:** **2025-10-20 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.416%, 4s -0.442%, 12s EKSİK; 1/3/5 uygun seans -2.639% / +1.238% / +4.385%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.005%**, CL **-0.279%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_038); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.234% · 12 saat +2.428% · 1 seans +2.015% · 3 seans -2.686% · 5 seans -3.867%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$95.745**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$96.535**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +1.105%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_038`; bu kontrol için orijinal etiketler: `SWING_V1_038`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 71; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 16. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_023](#swing_v1_023), [SWING_V1_028](#swing_v1_028), [C_CORR_006](#c_corr_006), [SWING_V1_015](#swing_v1_015), [C_CORR_024](#c_corr_024). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_039

**1. Karar öncesi piyasa durumu:** **2025-10-29 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.322%, 4s +0.049%, 12s +0.228%; 1/3/5 uygun seans +0.330% / -2.812% / -4.085%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.055%**, CL **+0.183%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_039); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +1.349% · 12 saat +0.371% · 1 seans -0.159% · 3 seans +1.160% · 5 seans -0.098%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$99.530**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$100.350**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.738%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_039`; bu kontrol için orijinal etiketler: `SWING_V1_039`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 73; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 18. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_035](#c_corr_035), [C_CORR_014](#c_corr_014), [SWING_V1_037](#swing_v1_037), [SWING_V1_007](#swing_v1_007), [SWING_V1_009](#swing_v1_009). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_050

**1. Karar öncesi piyasa durumu:** **2025-11-10 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.438%, 4s +0.572%, 12s EKSİK; 1/3/5 uygun seans +1.821% / +2.605% / +1.328%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.000%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.071%**, CL **+0.166%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_050); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.327% · 12 saat +0.904% · 1 seans +1.626% · 3 seans +3.393% · 5 seans -0.229%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$101.730**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$102.566**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -4.836%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_050`; bu kontrol için orijinal etiketler: `C_CORR_050`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 75; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 32. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_047](#c_corr_047), [SWING_V1_020](#swing_v1_020), [C_CORR_046](#c_corr_046), [C_CORR_033](#c_corr_033), [SWING_V1_001](#swing_v1_001). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_040

**1. Karar öncesi piyasa durumu:** **2025-11-12 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.042%, 4s -0.673%, 12s -0.084%; 1/3/5 uygun seans -0.675% / +2.777% / +3.569%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.108%**, CL **-0.049%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_040); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.471% · 12 saat +2.281% · 1 seans +2.431% · 3 seans -1.158% · 5 seans -0.223%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$97.254**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$98.050**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -0.454%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_040`; bu kontrol için orijinal etiketler: `SWING_V1_040`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 75; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 19. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_028](#swing_v1_028), [C_CORR_048](#c_corr_048), [SWING_V1_023](#swing_v1_023), [SWING_V1_010](#swing_v1_010), [C_CORR_024](#c_corr_024). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_051

**1. Karar öncesi piyasa durumu:** **2025-11-14 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.011%, 4s -0.100%, 12s -0.294%; 1/3/5 uygun seans -0.385% / +1.347% / +4.870%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **+0.261%**, CL **+0.101%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_051); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.579% · 12 saat -2.265% · 1 seans -3.130% · 3 seans -2.215% · 5 seans -3.293%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$96.210**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$97.003**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +0.621%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_051`; bu kontrol için orijinal etiketler: `C_CORR_051`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 76; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 20. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_028](#swing_v1_028), [C_CORR_006](#c_corr_006), [SWING_V1_010](#swing_v1_010), [C_CORR_048](#c_corr_048), [C_CORR_024](#c_corr_024). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_041

**1. Karar öncesi piyasa durumu:** **2025-11-17 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.339%, 4s -0.753%, 12s EKSİK; 1/3/5 uygun seans -3.130% / -1.158% / -0.229%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.115%**, CL **+0.067%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_041); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.705% · 12 saat +0.345% · 1 seans -1.132% · 3 seans +0.364% · 5 seans -0.216%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.752**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.562**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -1.963%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_041`; bu kontrol için orijinal etiketler: `SWING_V1_041`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 76; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 14. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_016](#c_corr_016), [SWING_V1_029](#swing_v1_029), [SWING_V1_035](#swing_v1_035), [SWING_V1_013](#swing_v1_013), [SWING_V1_031](#swing_v1_031). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_052

**1. Karar öncesi piyasa durumu:** **2025-11-28 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.025%, 4s -0.135%, 12s +0.647%; 1/3/5 uygun seans +0.735% / +0.879% / +3.259%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN ****EKSİK**** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ ****EKSİK****, CL ****EKSİK**** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_052); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.255% · 12 saat +0.751% · 1 seans +1.179% · 3 seans +0.572% · 5 seans +0.998%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$98.947**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$99.766**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -2.167%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_052`; bu kontrol için orijinal etiketler: `C_CORR_052`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 79; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 33. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_045](#c_corr_045), [C_CORR_025](#c_corr_025), [SWING_V1_018](#swing_v1_018), [C_CORR_021](#c_corr_021), [SWING_V1_012](#swing_v1_012). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_053

**1. Karar öncesi piyasa durumu:** **2025-12-22 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.058%, 4s +0.527%, 12s EKSİK; 1/3/5 uygun seans +1.770% / +1.546% / +1.398%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.014%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.026%**, CL **+0.246%** (WTI vadeli, Brent değil), SI **-0.240%** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_053); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.233% · 12 saat +0.750% · 1 seans +1.539% · 3 seans +2.476% · 5 seans -0.693%. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$100.827**; NAKİT TUT: **$100**. Ex-post karşılaştırmada AL+SAT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$101.658**. Ex-post karşılaştırmada ALTIN TUT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı -3.987%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_053`; bu kontrol için orijinal etiketler: `C_CORR_053`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 79; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 33. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [SWING_V1_001](#swing_v1_001), [SWING_V1_020](#swing_v1_020), [C_CORR_023](#c_corr_023), [C_CORR_011](#c_corr_011), [SWING_V1_018](#swing_v1_018). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### SWING_V1_042

**1. Karar öncesi piyasa durumu:** **2025-12-26 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s +0.079%, 4s +0.139%, 12s EKSİK; 1/3/5 uygun seans +0.446% / +2.476% / +4.113%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **-0.056%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.010%**, CL **+0.017%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_042); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat +0.134% · 12 saat +0.112% · 1 seans -0.148% · 3 seans -4.733% · 5 seans EKSİK. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: NAKİT $100 → H3'e kadar AL+SAT: **$93.731**; NAKİT TUT: **$100**. Ex-post karşılaştırmada NAKİT TUT daha yüksek. ALTIN BID-mark $100 → şimdi SAT: **$99,200 NAKİT**; ALTIN TUT, H3'te SAT: **$94.501**. Ex-post karşılaştırmada ŞİMDİ SAT daha yüksek. H3'te yeniden AL olursa altın miktarı farkı +3.277%. Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `SWING_V1_042`; bu kontrol için orijinal etiketler: `SWING_V1_042`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 80; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 34. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_025](#c_corr_025), [SWING_V1_022](#swing_v1_022), [SWING_V1_018](#swing_v1_018), [C_CORR_021](#c_corr_021), [C_CORR_031](#c_corr_031). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**

---

### C_CORR_054

**1. Karar öncesi piyasa durumu:** **2025-12-29 06:15:00 UTC / 09:15 TRT**, başlangıç fiyat etiketi sonrasındaki ilk uygun fiyat günü. Geçmiş XAU MID: 1s -0.190%, 4s -0.022%, 12s EKSİK; 1/3/5 uygun seans -0.148% / +0.774% / +4.136%. **Gerçek DXY/2Y/10Y, spot gümüş/platin/paladyum/Brent, 12s gerçekleşen volatilite ve kalibre trend olasılığı: EKSİK.** Bunlar ileride veri eklendikçe güncellenecek.

**Karar öncesi eşzamanlı vadeli H1 kontrolü:** Son tamamlanmış 05:00–06:00 UTC CME barının önceki H1 kapanışa değişimi: ZN **+0.028%** (10 yıllık tahvil vadeli *fiyatı*, tahvil getirisi değil), NQ **-0.138%**, CL **+0.122%** (WTI vadeli, Brent değil), SI ****EKSİK**** (gümüş vadeli, spot XAG değil), GC ****EKSİK****. Kaynak-vintage ve 2023 gerçek-time erişim teyidi olmadığı için tarihsel H1 fiyat vekilidir; boş kontrat/bar değeri üretilmez. [96 fiyat olayının H1 karşılaştırma CSV'si](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv).

**2025 için yakın-kontrat SI.n.0 ham H1 arşivinin aynı kapsamı teyit edilmedi; mevcut SI.c.0 satır sayısı düşük olabilir.**

**2. Haber ve ilk tepki:** [Haber ve veri kaynağı](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_054); açıklama ve yayın tarihleri kaynak fişinde. Fiyat bacağını başlatan haberin tam UTC ilk yayımlanması ve bütün ilgili piyasaların ilk 15dk tepkisi **doğrulanmamış**; 09:15 TRT sonrasındaki duyuru sonuçları bu sabahın girdisi değildir.

**3. Karar anı değerlendirme:** `P(UP/DOWN/DEVAM/DÖNÜŞ)` ve **beklenen kalan hareket kalibre edilmedi**. Geçerli otomatik `AL/SAT/TUT` sinyali **ÜRETİLMEDİ**. Pozisyon ve gerçek banka makası bilinmiyorsa **ABSTAIN**; geçmiş doğru aksiyonun gerçekleşmiş olması öngörü demek değildir.

**4. Karardan sonra gerçekleşen, yalnız ex-post:** 4 saat -0.769% · 12 saat -3.917% · 1 seans -2.949% · 3 seans EKSİK · 5 seans EKSİK. Bunlar **sabit 09:15 kontrolünden sonraki** sonuçlardır, etiketli fiyat bacağının tamamı veya karar sırasında bilinebilen beklenti değildir.

**5. Aynı başlangıç pozisyonu, komisyonlu alternatif:** Ücret %0,8 AL + %0,8 SAT; vendor BID/ASK ve kontrolü izleyen M15 OPEN vekil fiyatları. 3 uygun seans değerlendirmesi: **EKSİK** **EKSİK** Diğer dört ufkun sonuçları [sayısal sonuç dosyasında](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). **Gerçek bankanın uygulanabilir fiyatı değil.**

**6. Benzer ve ters olaylar — MÜKERRERLİK DÜZELTİLDİ:** Bu dosyada daha önce gösterilen **fiyat-only yakın ve karşıt vaka listesi GEÇERSİZDİR**; aynı 09:15 kontrolü için V1/V2 iki kez sayılıyordu. Güncel bağımsız örnek sicili [84 tekil kontrol/96 kaynak kimliği](OLAY_02_BENZERLIK_DUPLIKE_TEMIZ_84_KONTROL_20261014.csv) dosyasındadır. **Tekil gözlem:** `C_CORR_054`; bu kontrol için orijinal etiketler: `C_CORR_054`. **Karar anından önce tamamlanmış bağımsız aday havuzu:** 81; **aynı planlı CPI/NFP/FOMC altkümesi ve as-of altın fiyat rejimi:** 22. **Kullanılan eşleştirme katmanı:** `SAME_SCHEDULED_MACRO_CLASS_AND_PRICE_CONTEXT`. Yakın, mükerrerlik temizlenmiş tarihsel kontrol örnekleri: [C_CORR_006](#c_corr_006), [C_CORR_051](#c_corr_051), [SWING_V1_028](#swing_v1_028), [SWING_V1_010](#swing_v1_010), [C_CORR_024](#c_corr_024). Bunlar **yalnız altın fiyat rejimi + önceden planlanmış makro takvimine dayalı sınırlı analoglardır**; gerçek haber firstprint, gümüş SI.n saatlik veri ve tahvil faizi entegre edilmeden **nedensel olay benzerliği veya AL/SAT sinyali olarak geçerli değildir**. **ÖĞREN-03'e doğrulanmış kural aktarılmadı.**