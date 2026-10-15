# V15 KAVİS — Mimari ve bilimsel kabul sözleşmesi
**Tarih:** 16 Ekim 2026  
**Dal:** `research-gold-v15-kural-yerine-ogrenme-20261016`  
**Durum:** **ALGORİTMA-KODU / SENTETİK KONTRAT TESTİ TAMAM, TARİHSEL GERÇEK VERİ DOĞRULAMASI YOK.**  
**Önceki sürümler:** V13 SENTEZ ve V14 KOR korunur, otomatik geçiş/merge yok.  
**Canlı işlem:** Yasak. **2023–2026 PnL simülasyonu:** Bu fazda yasak.

## 1. Problem ve asıl hedef

Banka hesabında altın/nakit ikili portföyü, alışta %0,8 ve satışta %0,8 ile yönetmek.
Amaç, **tamamlanmış** geçmiş fırsat epizotlarından AL–SAT–BEKLE
kararının **alternatifine göre net log-servet üstünlüğünü** öğrenmektir.
Öngörü yönü tek başına başarı değildir. Her karar maliyeti, zamanı ve
kaçırılan karşı-kararın sonucu ile ölçülmelidir.

### Karşı-olgusal öğrenme etiketleri

Gözlenen banka-fiyat **vekilinin** epizot giriş/çıkış fiyatları `P0,P1`,
tek yön banka kesintisi `f`, log yüzde-puan birimi:

```
g = 100 ln(P1/P0)
fee_round_trip = 200 ln(1-f)              (f=.008 -> -1.6064... log yüzde puan)
Y_ENTRY(h) = g + fee_round_trip           # Nakit kalmaya kıyasla al/tasfiye
Y_EXIT(h)  = -g + fee_round_trip          # Altında kalmaya kıyasla sat/yeniden al
```

Bu **epizot sonunda ilk pozisyona dönülen eylem karşılaştırmasıdır**.
Portföyün gerçek uzun vadeli en iyi politikasının Bellman değer fonksiyonu
veya tam pekiştirmeli öğrenme çözümü olduğu iddia edilmez. Özellikle
GOLD->CASH işleminin sonunda *yeniden alım yapılmadığı* stratejinin ekonomik
karşılaştırması daha farklıdır; bu sürümde kısa düşüşten sonra tekrar
altına dönme fırsatı modellenmektedir.

### Kayıp maliyeti ayrı *elle seçilmiş eşik* değildir

İşlem maliyeti **öğrenme etiketine yalnız bir kez** girer. Son kararda
`min(predicted action net premium - confidence margin)>0` kullanılır;
%1,6 ek ve çifte sayılan farklı bir eşik yoktur.
Eşik `0`, maliyet sonrası alternatiften iyi olmanın tanımıdır.
`confidenceZ=0.35` algoritmanın seçilebilir temkinlilik ayarıdır,
piyasa tarafından bulunmuş bir katsayı değildir.

## 2. Önceki hataların zorunlu teknik karşılıkları

| Önceki hata | V15 mekanizması | Denetim |
|---|---|---|
| V13 bir AL, hiç SAT | `ENTRY` ve `EXIT` için **ayrı** action-value modelleri | Sentetik yükseliş + düşüşte hem BUY hem SELL |
| V14 yanlış 7/28–56 ufuk karşılaştırması | 1, 3, 7, 28 ve 56 gün için **bağımsız** etiket, uzman ve kalibrasyon | Ufuk ayrı kaydedilir; karışım yalnız aynı ufukta |
| El yazımı AL/SAT eşikleri | Online öğrenilen net karşı-olgusal eylem üstünlüğü | Sigortalı çıktı: skor, ufuk ve gerekçe |
| Sabit hafıza kapıları | Gecikmeli net sonuç hatasından çevrimiçi güncellenen lokal kapı parametreleri | Gradient güncellemesi testi |
| ANN eklendiği için işe yaradı varsayımı | Lineer, Sugeno-benzeri bulanık ve MLP uzmanlarına **vadeye göre hata ağırlığı** | Ağırlık öğrenme testi; katkı kanıtı sadece gelecekteki ablasyon |
| Düşüşte rejim kayması | Anlık gözlenebilir standartlaştırılmış yenilik + öğrenen trend/stres hafızası | Gelecek veriyi görmeden durum güncellemesi |
| Ortalama getiri olunca al | Ayrı 0.1-alt kuantil uzmanı + isteğe bağlı kayıp bütçeli dual mekanizma | Risk bütçesi, kuantil, kısıt testi |
| Şimdi aldım ama 09→12 dolduruluyor | `signal` ve **ilk sonraki banka kontrol noktası** `receiveQuote` ayrıdır | Aynı saatte emülasyon yasak, kronoloji testi |
| Gerçek banka kotasyonu yok | `price` sadece vekil; emir/gerçek BID/ASK yok | `orderSent=false`, live yasağı |
| OLAY/ÖĞREN ilk yayın saatleri eksik | Onaylı `verifiedFirstPublication` ve `firstAvailableAt<=asof` **zorunlu** | Gelecek/teyitsiz olay engeli |
| Gelecek etiketin erken öğrenilmesi | Epizot yalnız gelecekteki fiyat geldiğinde ve ufku dolduğunda öğrenilir | Önce/sonra etiket ve dondurulmuş geçmiş testi |
| Aynı kronolojiden 1000 bağımsız örnek uydurma | 1/3/7 gün en az ufuk kadar, 28/56 için 14/28 gün etiket giriş aralığı | `lastOriginByH` / overlap açıklaması |
| 2026'ya tekrar tekrar bakıp algoritma ayarlama | V15 kabulde **gerçek altın PnL yasak**, yalnız sentetik birim/kontrat testleri | V15 CI tarihsel test modülü çalıştırmaz |
| Başarısız denemeleri başarılı sunma | Terfi kilidi, şeffaf test çıktısı, önceden ilan edilmiş gerçek veri sınaması | Bilimsel kabul sözleşmesi |

## 3. Matematiksel uzmanlar (gerçekten kodlandı)

1. **Adaptif durum belleği (RNN fikri)**: Trend ve stres için unutma/güncelleme
   sigmoid kapıları. Sonucu tamamlanan **1 günlük** örnekten hesaplanan lokal
   türevle güncellenir. **Tam LSTM/BPTT değildir**.
2. **Doğrusal çevrimiçi uzman**: AdaGrad uyarlamalı gradyanla ileri tamamlanmış
   eylem-üstünlüğü etiketine fit edilir.
3. **Sugeno-benzeri bulanık uzman**: Beş yumuşak üyelik, aynı ufukta lineer
   kural sonuçları ve yalnız olgunlaşmış epizottan güncellenen merkezler.
   **Tam uçtan uca ANFIS değildir**.
4. **Gerçek MLP uzmanı**: 14 giriş, 6 `tanh` gizli ünite, eğitilen iki
   katman, geri yayılım ve uyarlanır gradyan.
5. **Hata ağırlıklı birleştirme**: Aynı eylem ve **aynı zaman ufku**
   uzmanlarının vadeye girmiş gerçek hatalarına göre softmax ağırlıkları.
6. **Alt kuantil uzmanı**: Pinball (`alpha=0.1`) kaybıyla olası kötü eylem
   sonuçları için ayrı lineer kuantil tahmini.
7. **Kayıp bütçeli dual güncelleme (isteğe bağlı)**: Kullanıcı açık bir
   `maxHypotheticalDownsidePct` verirse, 28 gün içindeki altın tutma
   karşı-olgusal en kötü ara fiyat kaybına göre risk gölge bedeli artıp azalır.
   Bu **gerçek portföy maksimum geri çekilmesi değildir**.

## 4. Girdi sözleşmesi

`signal(model, {asof, featureAvailableAt, position, market, events?, legacy?})`

- `market.r4,market.r1,market.r3`: karar anında gerçekten bilinen
  geçmiş altın yüzde getirileri (zorunlu), `rv,dd,nq6` isteğe bağlı.
- `featureAvailableAt <= asof`: geçmişten gelen gerçek veri ve hesap
  yayımlanma/erişim zamanı ayrı tutulur.
- `events` sadece `verifiedFirstPublication=true` ve
  `firstAvailableAt <= asof` ise kullanılabilir. Bu boolean ayrıca
  kaynak bağımsız doğrulanmalıdır; sırf kullanıcının `true` girmesi
  tarihsel olayın gerçekten kanıtlandığı anlamına gelmez.
- `legacy` isteğe bağlı, `availableAt<=asof`, `net14,net56`
  alanları vardır; V13 kendiliğinden çağrılmaz ve onun gelecek etiketleri
  okunmaz. Eski ANN/ANFIS girdilerinin yararı ayrıca ablasyonla gösterilmelidir.
- `position`: yalnız `CASH` veya `GOLD`.
- `receiveQuote(model, {at,price,isBankCheckpoint})`: sadece o anda
  bilinen pozitif piyasa **vekili** fiyatını alır. İlk sonraki kontrol
  noktasında henüz olmayan gerçek emir YOK; dönülen `fills` adaydır.
- `checkpoint`/`restore`: karar öncesi uzman parametreleri, bekleyen
  sonuçlar, öğrenme durumu ve kaynak zamanları eksiksiz saklanır.

**Önemli:** Bu kodun `r4/r1/r3` isimli kaynak özelliklerinin gerçekten
işaret ettikleri zaman dilimleri, gerçek veri dosyası adaptöründe **ayrıca**
doğrulanmalıdır. V15 kodu otomatik geçmiş veri sürücüsü barındırmaz.

## 5. Faz kapıları

**Faz A (bu talep):** Kod ve sadece sentetik/deterministik matematik testleri.
Kabul edilen: 14/14 GitHub testi, tarihsel getiriler kullanılmadan. ✓

**Faz B (SONRA):** Önceden dondurulmuş koda gerçek piyasa verisini bağlayan
ve **kaynak anını denetleyen** adaptör; gerçek banka BID/ASK eksikse
vekil varsayımı ayrı etiketlenir. Nedensel veri sözleşmesini test etmeden
portföy sonucu çıkarılmaz.

**Faz C (SONRA):** İlk tarihsel kronolojik yürüyüş ve bağımsız
karşılaştırmalar: 2023, 2024, 2025, 2026 Şubat–Eylül, kesintisiz
2023–Eylül 2026, V13, V14, pasif ALTIN, hep nakit; 09/12 icra, %0,8
her banka bacağı, duyarlılık, drawdown, aksi yöndeki kaçırılmış kâr,
işlem defteri, ufuk ve uzman ablasyonları. **Bu yıllar zaten araştırmada
görüldüğü için asla gerçek kör doğrulama denmez.**

**Faz D (SONRA):** Önceden seçilmemiş yeni ileri dönem, öğrenen politika
başarı kapıları (portföy net servet > pasif, tatmin edici aşağı kayıp
davranışı, işlem kararlılığı); canlı emir izni **bu sürümde yoktur**.

## 6. Bilimsel özgünlük sınırı

KAVİS = **K**arşı-olgusal **A**daptif **V**arlık/portföy **İ**şlem
**S**eçici. Öğrenen kapı, bulanık çıkarım, MLP, çevrimiçi uzman
ağırlıkları, kuantil risk ve masraflı portföy kararı özgün bir
uygulama mimarisinde birleştirilmiştir. Ancak yapı taşları literatürde
bulunmaktadır. Matematiksel teoremin veya finansal üstünlüğün özgünlüğü
kanıtlanmış **değildir**.

Başvuru ilkeleri:
- Muhle-Karbe, Reppen, Soner (2017), *A Primer on Portfolio Choice with Small Transaction Costs*.
- Pitera (2023), *Discrete-time risk sensitive portfolio optimization with proportional transaction costs*.
- Adams & MacKay (2007), *Bayesian Online Changepoint Detection* (**uygulanan algoritma BOCPD değildir; yalnız 'rejim değişimi' probleminin bağlamıdır**).
- Guo, Gu, Fok, Ching (2023), *Online portfolio selection with state-dependent price estimators and transaction costs*.

**Kesin hüküm:** Matematiksel araştırma çekirdeği kuruldu, sentetik birim
kontratları geçti, koda geçmiş piyasa simülasyonu bağlanmadı. Bütün
parametrelerin piyasa tarafından öğrenildiği, en iyi politikayı bulduğu,
canlı işlemin güvenilir olduğu veya yeni kâr üstünlüğü bulunduğu
iddia edilmez.
