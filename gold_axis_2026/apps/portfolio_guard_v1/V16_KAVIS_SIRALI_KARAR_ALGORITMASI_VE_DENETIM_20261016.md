# V16 KAVİS-S — Sıralı karar öğrenmesi, mimari dondurma ve kabul raporu

**Tarih:** 16 Ekim 2026  
**Yeni dal:** `research-gold-v16-sequential-decision-20261016`  
**Taban:** `research-gold-v15-formal-audit-20261016` — V13/V14/V15 orijinalleri korunur  
**Statü:** Bağımsız algoritma araştırması. Gerçek altın portföy simülasyonu yapılmadı. Canlı emir yok. Gerçek banka bid/ask yok.  
**Sentetik teknik doğrulama:** 53 test / 53 PASS / 0 FAIL (V15: 28, V16 Q: 20, uzman köprüsü: 5).

## 1. Neden gerekliydi?

Önceki V15 modelinde ayrı kısa/uzun vadeli AL ve SAT üstünlüğü
öğrenilebiliyordu, ama **SAT sonrası ne zaman tekrar AL yapılacağı**
ve farklı kararların uzun vadeli toplam servet etkisi öğrenilmiyordu.

Yeni V16, varlığı iki durumlu (CASH/GOLD), eylemi iki seçenekli
(KEEP/SWITCH) ve sonsuz-zamanlı iskonto uygulanmış sıralı karar
problemine çevirir:

```
                         Eylem KEEP      Eylem SWITCH
  CASH                         CASH             GOLD (BUY)
  GOLD                         GOLD             CASH (SELL)
```

Şu an yalnız **iki varlık arasında tam geçiş** vardır; kısmi
pozisyon, kredi, kaldıraç, short, başka varlık, emir yönlendirme yoktur.

## 2. Matematik (tam olarak kodlanan)

Karar verildikten **sonraki banka kontrol fiyatı** P_t, sonraki kararın
gerçekleştirildiği kontrol fiyatı P_{t+1}. O aralığın bir-bank-bacağı
maliyet oranı f, işlemden sonra GOLD'da olma göstergesi I_gold.

```
r_t(p,a) = 100 * I_gold(p,a) * [ln(P[t+1]) - ln(P[t])]
           + 100 * ln(1-f) * I_switch(a)

beta(dt) = gammaPerDay ^ (dt / 24 saat)

TD_target_t(p,a) =
          r_t(p,a)
          + beta(dt) * max_a' Q(s[t+1], nextPosition(p,a), a')

Q <- Q + uyarlamalı_çevrimiçi_gradyan * (TD_target - Q)
```

Burada `s[t+1]`, **t+1 günü sinyal saatinde zaten bilinen
özelliklerden** kilitlenir; TD hedefi yalnız t+1 banka checkpoint
fiyatı gözlendiğinde kullanılır. Sinyal zamanı (TR 09:00) ile
gerçek fiyat atama zamanı (TR 12:00 vb.) ayrıdır.

**Maliyet önemli:** `KEEP` eyleminde banka kesintisi yoktur;
`CASH→GOLD` geçişinde **bir AL**, `GOLD→CASH` geçişinde
**bir SAT** kesintisi vardır. Sonradan yeniden AL yapılırsa o
ayrı tarihte ayrıca tek banka bacağı maliyeti vardır. V15'in
sonlu tur etiketiyle V16'nın sıralı ödülünü karıştırmayız.

**Öğrenme türü:** Yaklaşıklıklı, iskonto edilmiş, *model-free*
**off-policy Q-learning**, AdaGrad varyantıyla
`(pozisyon,eylem)` için 4 ayrı doğrusal fonksiyon.
Bir sonraki duruma ilişkin hedef, güncelleme başlamadan önce
**dondurulmuş mevcut Q katsayılarından** türetilir. Bu işlem
gelecekteki fiyatın erken kullanımını engeller ama bootstrap
yanlılığı ve fonksiyon yaklaştırmanın kararsızlığını garantiyle çözmez.

**Dört karşı-olgusal güncelleme:** Altının fiyat gelişiminin kullanıcının
bankadaki işlemlerinden etkilenmediği (eksojen piyasa) varsayımıyla
gözlenen bir fiyat hareketinden hem CASH hem GOLD kaynağı için,
KEEP/SWITCH'in tek-adımlık maliyet/ödül etiketleri hesaplanabilir.
Bu 4 ayrı bağımsız piyasa deneyimi değildir: **tek piyasa aralığından
türetilmiş dört ayrı eylem etiketi**dir. Uzun yollardaki karşı-olgusal
durum dinamikleri gerçekleşmiş diye iddia edilmez.

**Uzman entegrasyonu:** İsteğe bağlı `v15Expert` girdisi ancak kaynak
zamanı sinyalden geç değilse ve pozisyonu eşleşiyorsa kullanılabilir.
V15 önerisi, gerçek CASH durumunda üretildiyse GOLD karşı-olgusal
öğrenme başlıklarına verilmez (ve tersi). Bu kusur ayrı regresyon
testinde ortaya çıkarılarak giderildi. **V15 ile otomatik senkronize
çalışan tek bir canlı sistem henüz kurulmamıştır.**

**Risk:** Kullanıcı `goldDownsideBudgetPct` belirtirse,
bir sonraki *tek karar aralığındaki* GOLD fiyat düşüşü üzerinden
öğrenilen basit aşağı-risk başlığı ve dual gölge cezası
kullanılır. Bu gerçek portföy MDD, CVaR veya garantili zarar
sınırı değildir. Yanlış işaretli risk etkisi önceki V15
denetimindeki gibi: girişe karşı temkin, koruyucu çıkışa destek.

## 3. Kod ve arayüz

- `v16_kavis_siralama.js`: `create, signal, quote, save, restore`
- `signal(model,{asof,featureAvailableAt,position,market,v15Expert?})`
- `quote(model,{at,price,isBankCheckpoint})`
- Model tüm fiyatları vekil olarak görür; `ordersSent=0`;
  işlemler yalnız `simulatedExecutionOnly=true` olan
  aday kayıtlarıdır.
- UTC banka kontrol saatleri varsayılan 06/09/12
  (Türkiye 09:00/12:00/15:00); ayarlanabilir ve izin
  verilmemiş saatler reddedilir.
- Girdiler timezone'lu ISO zamanı, sonlu sayı ve pozisyon
  tutarlılığı zorunludur.
- Aynı barda sinyal ve fill reddedilir.
- Önceki fill ile yeni fill arası 80 saatten uzunsa TD etiketi
  hesaplanmaz; boşluk görünür `skipped` sayacı ile tutulur.
- Model parametreleri ve kilitli emir adayları `save/restore`
  ile deterministik yeniden üretilebilir.

## 4. Gerçek veri kullanılmadan yapılan kabul testleri

**GitHub Actions: 53/53 başarı.**
- Önceki V15'in 28 kabul/stres/denetim testi aynen.
- V16'nın 20 temel testi: tek bacak komisyon hesabı; hiçbir fill'den
  önce olgunlaşmamış sonuçla öğrenmeme; gelecekteki fiyatı
  değiştirince daha önceki sinyalin değişmemesi; döviz/altın
  pozisyonu arasında 4 ayrı karşı-olgusal başlık güncellenmesi;
  uzun veri boşluğunun eğitimi engellemesi; checkpoint/restore;
  negatif/flat fiyat patolojileri ve asof V15 uzmanı filtreleri;
  altın-koruma riski; gamma Bellman bootstrap hesabı;
  GOLD'e karşı-olgusal uzman girdisi sızması yasağı;
  sentetik yükseliş → düşüş → yeniden yükselişte sıralı
  **BUY → SELL → BUY**.
- Sentetik 500 karar epizotunda örnek davranış:
  `d=11 BUY`, `d=242 SELL`, `d=410 BUY`.
  Bunlar **uydurulmuş deterministik sınama fiyatlarıdır**,
  gerçek XAU sonucu ya da kazanç verisi değildir.
- Yatay fiyat stresinde %0,8 bacak maliyeti
  nedeniyle olgunlaşmadan sonra gereksiz al/sat üretilmedi.


## 4A. V15–V16 uzman bağlantısı (ek denetim)

**Yeni kaynak:** `v16_kavis_v15_uzman_koprusu.js`  
**Yeni sentetik test:** `v16_kavis_v15_uzman_koprusu.test.js` (5 test)

1. V15 kendi **gölge öğrenme portföyü** ile olgunlaşmış işlem
   fırsatlarını öğrenmeye devam eder; bu gölge portföy V16'nın
   tercih ettiği GOLD/CASH konumu olarak **sunulmaz**.
2. V16'nın gerçek araştırma karar pozisyonuna göre V15 uzman
   görüşü, mevcut V15 bilgi durumunun **bağımsız kopyasından**
   ve yalnız günün `asof` özellikleriyle üretilir.
3. V15 uzman çıktısı sadece öğrenen V16 Q başlığı için
   koşullu bir açıklayıcı değişkendir. V16 dışındaki
   hiçbir modül al/sat eylemini devralmaz.
4. Girdi, olay/yayın veya banka checkpoint hatasında iki modelin
   durumu atomik olarak önceki checkpoint'e geri alınır.
5. Sentetik çok günlük işleyiş, V15 gölge ve V16 karar portföyü
   farklılaştığında bile hatasız; koşullu V15 uzman girdisinin
   yalnız olgunlaştıktan sonra aktifleşmesi ve kaydedilip
   yeniden başlamanın deterministik olması ayrı ayrı test edildi.
6. **Henüz gerçek altın fiyat adaptörüne bağlanmadı.**
   5 başarılı test ekonomik katkı kanıtı değildir. Uzman görüşü
   kullanılan ve kullanılmayan sürümler ileride ablasyonla
   karşılaştırılmalıdır.

## 5. Tamamlanmamış teknik ve bilimsel riskler

1. **Orijinal Q ile sonraki Q aynı sistemin tahminlerinden
   bootstrap alır:** Yaklaşık Q-learning aşırı tahmin ve
   hedef kaymasına açık. Target network / Double Q /
   conservative Q güncelleme adayları ileride objektif
   sentetik adversarial test ile değerlendirilebilir.
2. `gammaPerDay=.94`, `minimumMaturedIntervals=12`,
   `uncertaintyScale=.10` **hazır varsayımlardır**; tarihsel
   veride optimum seçilmiş veya kanıtlanmış değildir.
3. 1 günlük vs olay-bazlı 3/7/28/56 gün sonuçları V15'te
   kalır. V16 09:00 sinyal, ilk sonraki 12:00 fiyatı ve
   sonraki sinyal/fill çiftleri için ardışık karar alır.
   Bir hafta tutma veya yıllarca tutma eylemlerini
   açıkça modellemeyen, iskonto edilmiş devam problemidir.
4. Portföy durumunda işlemden bu yana geçen süre,
   elde tutma yaşı, gerçekleşmiş zarar, reentry cooldown
   gibi **yola bağımlı** bilgiler şu an yoktur.
   Eklenmeleri mevcut karşı-olgusal 4-başlık kabulünü
   otomatik olarak geçerli bırakmaz; ikincil durum modellemesi
   gerekir.
5. Gerçek fiyatların exogenous olması, maliyetlerin sabit
   olması, fiyat serisinin bağımsız olmaması, model
   değişmesi, sert rejim kırılmaları, alış/satış kotasyonları
   ve makro kaynakların ilk yayın güveni çözümlenmedi.
6. V15 uzman görüşü için asof ve farklı gölge pozisyonları
   güvenli şekilde ayıran **inference-only bağlantı eklendi**.
   Ancak açıklayıcı değişken olarak katkısı, gerçek kaynakların
   güveni, makro yayın kontrolü ve bankanın BID/ASK ölçümü
   henüz tarihsel dış örneklemde gösterilmedi.
7. Bu sürüm işlem sonucunu doğrudan gerçek yıllık altın
   fiyatında denemedi. Teknik testlerden yatırım
   üstünlüğü çıkarılamaz.

## 6. Son karar

**V16 KAVİS-S araştırma modeli, sıralı AL–BEKLE–SAT–yeniden AL
kararını öğrenen bir matematiksel çekirdek olarak inşa edildi.**
Ancak tam portföy-optimal veya yeni keşfedilmiş matematiksel teori
olduğu, gerçek makasla kâr ürettiği, 2026 rejiminde koruyucu
SAT'ları doğru bulduğu **kanıtlanmış değildir**. Terfi/canlı emir
girişi kapalı tutulacaktır.

Algoritma öncesi kalite kontratı: portföy simülasyonundan önce
inference-only V15 entegrasyonunu çöz, kaynak ve ilk erişim saatlerini
doğrula, varsa gerçek banka bid/ask eşleşmelerini belirt,
varsayımları ve sabit parametreleri mühürle. **2023–2026
yıllarına bakarak parametre seçmek gerçek kör test değildir.**
