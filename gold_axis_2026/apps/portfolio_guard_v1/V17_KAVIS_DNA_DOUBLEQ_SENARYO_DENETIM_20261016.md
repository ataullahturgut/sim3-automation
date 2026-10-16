# V17 KAVİS — Takvimden bağımsız olay öğrenmesi, çift Q ve sentetik stres denetimi

**Tarih:** 16 Ekim 2026  
**Araştırma dalı:** `research-gold-v17-event-doubleq-20261016`  
**Taban:** `research-gold-v16-sequential-decision-20261016` (eski V16 değiştirilmedi)  
**Statü:** Matematiksel araştırma prototipi; gerçek banka/altın portföyünde bilimsel üstünlük **kanıtlanmadı**, canlıya çıkarılmadı.

## 1. Kullanıcının «zaman etiketinden bağımsız» isteğinin kesin yorumu

Yıl, takvim günü, hafta içi, belirli olayın tarih adı ve «Ocak 2026» gibi
kimlikler **öğrenme girdisi değildir**. Öğrenilenler: karar anında mevcut
piyasa getirileri, kırılma/oynaklık durumu, geçmiş kapılı durum özeti ve
o ana dek yayınlanmış olduğu varsayılan olayların G01–G07 ailesidir.

**Mutlak zaman tamamen yok edilemez:** asof yayın sırası, ilk sonraki
banka fiyatında icra ve `gamma^(elapsedDays)` ile iskonto için
zaman bilgisi zorunludur. 1000 günlük ortak tarih kaydırması kararları
değiştirmemektedir (sentetik birim testi). İleriye bakmayı önleyen bu
kronoloji asla kaldırılmamalıdır.

## 2. V16 temelini bozmadan V17'de yapılan matematiksel değişiklikler

- **Double Q-learning (Van Hasselt, NeurIPS 2010):** Aynı gürültülü
  Q kestiricisinden hem maksimum eylemi seçmek hem o maksimumu
  değerlendirmek iyimserlik yanlılığı yaratabilir. V17 iki bağımsız
  `q` ve `qb` durumunu dönüşümlü günceller:
  `a*=argmax_a Q_A(s',a)` ve `TD=r+gamma*Q_B(s',a*)`.
  Bir sonraki gün roller değişir. İşlemlerde iki tahmincinin ortalaması,
  birbirine uyuşmazlığın cezası ile kullanılır.
- **Unutabilen gradyan istatistiği:** Önceki V16 birikimli AdaGrad
  katsayıları binlerce örnekten sonra çok küçük adımlara dönüşebilirdi.
  V17 ikinci momenti `v_t=0.985*v_(t-1)+0.015*g_t²` biçiminde günceller,
  böylece yeni rejim için öğrenme olanağı kapanmaz. Bu RMSProp-benzeri
  uyarlama, teorik kâr garantisi sağlamaz.
- **Rejim yeniliği:** Gelen getiriyi yalnız *önceden görülen* getiri
  ortalaması/değişkenliğiyle karşılaştırır. Üstel ağırlıklı geçmiş
  `regimeMemory=.93` ile eski rejimi yavaşça unutabilir. Bu
  **Bayesian online changepoint detection** değildir; onun yerine
  basit bir standartlaştırılmış yenilik sinyalidir.
- **Ayrı olay DNA kanalları:** Önceki toplam haber polaritesi yerine
  G01 faiz/FX; G02 ticaret; G03 jeopolitik; G04 merkez bankası/fiziki;
  G05 finansal stres; G06 pozisyon çözülmesi; G07 belirsiz olmak üzere
  7 ayrı grup girdisi. Eylemde hangi grubun etkin olduğunu Q katsayıları
  uygun gerçek etiket geldiğinde çevrimiçi öğrenebilir.
  Olayın `verifiedFirstPublication`, `firstAvailableAt <= asof`,
  `evidenceId` ve grup alanları zorunlu. **Boolean ve ID tek başına
  haberin gerçekte kanıtlandığı anlamına gelmez; kaynak denetim adapteri
  yoktur.**
- **Karar belirsizliği:** İki Q uzmanının birbirinden farklı hesapladığı
  SWITCH avantajının büyüklüğü (`criticDisagreementPenalty=.16`),
  ve piyasa değişim yeniliği (`regimePenalty=.05`) kararı daha
  temkinli kılar. Bunlar araştırma varsayımıdır, kârdan türetilmiş
  optimal katsayılar değildir.
- **Aynen korunanlar:** CASH/GOLD × KEEP/SWITCH; ilk sonraki banka
  kontrol fiyatında hayali icra; her SWITCH'te **tek** banka maliyeti;
  KEEP'te sıfır; alternatif pozisyonlar için aynı piyasa hareketinden
  ayrıştırılmış dört karşı-olgusal eğitim hedefi; V15 uzmanı ancak
  asof ve doğru pozisyon ile eşleşirse; gerçek otomatik emir **yok**.

## 3. Beş ön-tanımlı sentetik dünya: 100$ başlangıç, %0.8/her yön

| Dünya (tamamı KURGUSAL) | V16 son USD | V17 son USD | Pasif altın USD | V17 işlem |
|---|---:|---:|---:|---:|
| Yükseliş → düşüş → toparlanma | 593.503 | **630.833** | 225.903 | 3 |
| Yatay küçük oynaklık | 100.000 | **100.000** | 99.028 | 0 |
| Düzenli hızlı yön değişimleri | 419.913 | **445.404** | 102.936 | 68 |
| Ani çöküş ve toparlanma | **244.213** | 228.159 | 281.352 | 3 |
| Rastgele sert şoklar | 100.000 | **120.608** | 116.595 | 1 |

**İyileştirme süreci açıkça kaydedildi:** İlk V17 sürümü, üç rejimde
581.750 USD ve whipsaw'da 362.578 USD idi; rejim istatistikleri ve
öğrenme gradyanı unutabilen yapıya dönüştürülünce sırasıyla
630.833 ve 445.404 USD elde edildi. Ancak ani çöküşte ilk V17
259.055 iken **228.159'a geriledi**, ayrıca pasif altını da geçmedi.
Yani genel iyileşme anlatısı ile bu gerçek olumsuz sonuç birlikte
tutulmalıdır. Bunlar simülasyon kalibrasyonuna kapalı
gerçek dünya dışı, sentetik tasarım denemeleridir.

## 4. Kod dondurulduktan sonra 16 ek rastgele sentetik dünya

Yalnız geçmiş gözlenen fiyatlarla hesaplanan girdiler kullanıldı,
gelecek fiyat model tarafından okunmadı. Değişken faz uzunluğu,
trend, ani fiyat şoku ve gürültü içerir. Kaynak:
`v17_unseen_fictional_stress.js` (seed 101–116).

- **V17, V16'yı 10/16 senaryoda geçti; 6/16 senaryoda geride kaldı.**
- 16 senaryonun ortalama sonuçları: V16 **286.099 USD**,
  V17 **300.147 USD**, pasif altın **153.888 USD**.
- V17 16 senaryonun **13'ünde 100 USD nakdin** üstünde kaldı,
  **3'ünde kalmadı**.
- Bu ortalamalar birkaç büyük kazanan sentetik dünya tarafından
  etkilenebilir; medyan ve max drawdown gibi ölçüler ayrıca
  incelenmelidir. Bunlar **daha önce görülmemiş kurgu tohumlarıdır**,
  fakat bağımsız piyasa örneklemi veya gerçek kör backtest **değildir**.

İkinci grubun sonuçlarından sonra V17 katsayıları değiştirilmedi;
kötü sonuçlar aynen saklandı.

## 5. Test ve bilimsel sınırlar

CI **34/34 PASS**: mevcut V16'nın 20 testi ve V17'nin 14 sentetik
kanıt testi. Testler: takvim tarihinin 1000 gün kaydırılması,
çift Q Bellman hedefi, gerçek iki banka bacağı sayımı,
gecikmiş bilgi zamanlaması, G01/G05 olay ayrımı,
gelecekteki yayın bilgisinin engellenmesi, rejim istatistikleri,
yanlış checkpoint reddi, tarihi eksik özellik engeli,
yatay piyasa komisyonlu WAIT, checkpoint restorasyonu.

**Kesin sınırlamalar:**
1. Model **olayları yalnızca nominal PIT sözleşmesi ile** kabul ediyor.
   OLAY-02/ÖĞREN-03 arşivinin gerçek asof-kanıt doğrulaması ve
   olayların nedenselliği henüz kanıtlanmadı. Arşiv bu sürümde
   doğrudan okunmaz.
2. Fiyatlar kurgusaldır. Birim testleri ve senaryolar gerçek XAU/USD
   piyasasında kârlı bir algoritma olduğu anlamına gelmez.
3. `gammaPerDay`, uzman anlaşmazlığı katsayısı, erken örneklem
   sayısı ve öğrenme unutma katsayıları **sabit varsayımlardır**.
   Bu sürümde her parametrenin öğrenildiği iddia edilemez.
4. Q-learning yaklaşık ve bootstrap kaynaklı hataya açıktır;
   Double Q bu riski azaltabilir, tümüyle yok etmez.
5. Günlük gibi görünen sentetik fiyatlar örnek amaçlıdır; model
   gerçek 15 dk/haber akışıyla eğitilmedi. Seans-dışı gerçek makas,
   banka BID/ASK ve fiyat gecikmeleri bağlanmadı.
6. Kullanıcıyı koruyacak canlı maksimum zarar garantisi, gerçek
   risk kısıtlaması, kısmi satış ve alım emirleri **yok**.
7. Geçmiş altın test yılları 2023–2026 defalarca görülmüştür; onlar
   bundan sonraki bilimsel raporda **gerçek kör döneme dönüşemez**.

## 6. Açık karar

**V17, V16'dan türemiş teknik olarak çalışan deney sürümüdür; canlıya
terfi etmemiştir.** Sert çöküşte V16'nın gerisindedir; 16 farklı
kurgusal deneyin 6'sında da V16'yı geçemedi. Bu nedenle tek doğru
'süper algoritma' olarak seçmek yerine, olgunlaşmış sürümlerin
ayrışan güçlü yanlarını gerekçeli ablation ile izlemek gerekir.

**Sıradaki uygun bilimsel kapı:** gerçek veri adaptöründe yayım ve
erişim saatini kanıtlama → bankanın BID/ASK koşullarını tanımlama →
dondurulmuş sürümle tarihsel nedensel portföy sınaması → bağımsız yeni
ileri örneklem. Şimdiye kadar yalnız sentetik test yapıldı.

## Literatür

- Hado van Hasselt, *Double Q-learning*, NeurIPS 2010:
  https://papers.neurips.cc/paper_files/paper/2010/hash/091d584fced301b442654dd8c23b3fc9-Abstract.html
- van Hasselt, Guez, Silver, *Deep Reinforcement Learning with Double Q-learning*, AAAI 2016:
  https://doi.org/10.1609/aaai.v30i1.10295
- Gama vd., *A Survey on Concept Drift Adaptation*, ACM CSUR 2014:
  https://doi.org/10.1145/2523813
- Fujimoto, Meger, Precup, *Off-Policy Deep Reinforcement Learning without Exploration*, ICML 2019:
  https://proceedings.mlr.press/v97/fujimoto19a.html
