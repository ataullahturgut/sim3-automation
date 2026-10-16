# V20 KAVİS–ATLAS — Nihai araştırma mimarisi ve bilimsel kabul

16 Ekim 2026 | Dal: research-gold-v20-atlas-regret-gated-20261016
Durum: DONDURULMUŞ ARAŞTIRMA ADAYI. Gerçek XAU/USD simülasyonu, kanıtlanmış yatırım üstünlüğü, üretime geçiş veya canlı banka emri YOK.

## Tamamlanan mantıksal mimari

1. V18 veri bekçisi: kesin as-of sırası, banka kontrol noktası, veri bayatlığı, bozuk kotasyon karantinası, bağımsız kaynak iddiası denetimi ve dinamik banka masrafı.
2. Yedi ayrı olay ailesi (G01–G07): ilk yayın/erişilebilirlik saatine göre korunmuş öğrenme özellikleri. Gerçek kaynak sertifikasyon adaptörü yok.
3. Double Q-learning: CASH/GOLD × KEEP/SWITCH durum–eylem değerini iki bağımsız tahminciyle olgunlaşan fiyat aralıklarından öğrenir.
4. Rejim istatistiği ve yerel hafıza: tarih kimliği değil, piyasada değişimin örüntüsü ve koşullu mevcut bilgi kullanılır.
5. Risk tarafı: gerçekleşmiş likidasyon NAV'ı, zirve–sermaye düşüşü, yalnız olgunlaşmış altın kaybının koşullu tek-aralık ampirik CVaR değeri ve kuyruk belirsizliği.
6. V20 ATLAS karşı-olgusal uzman karşılaştırması: risk danışmanı yalnız daha önceki aynı rejimde tamamlanmış, işlem maliyeti sonrasındaki kanıtlarla ana Double Q karardan daha iyi olduğunu göstermişse müdahale hakkı kazanır.
7. Kullanıcı maksimum düşüş limiti vermemişse keyfî bir %12 gibi sert koruma kuralı uygulanmaz. Açık kullanıcı limiti varsa gözlenen NAV temelinde acil çıkış önceliği vardır; gelecekteki gap kaybı garantiyle engellenemez.
8. V15 ANN/Sugeno/yerel hafıza çıktısı ancak bağımsız ve as-of doğrulanmış uzman girdisi şeklinde, opsiyonel olarak kullanılabilir. Uçtan uca LSTM ya da Transformer eğitildiği ileri sürülmez.

## Matematiksel karar özeti

Tamamlanmış iki banka kontrol noktası P_t → P_(t+1) arasında altın log getirisi g=100 ln(P_(t+1)/P_t), işlem başına ücret f_t:

r(a) = 1[next-position=GOLD]·g + 1[position changes]·100 ln(1−f_t)
delta_t = r(risk adviser) − r(Double-Q baseline)
m_t = ρ m_(t−1) + (1−ρ) clip(delta_t,−35,+35)
v_t = max(0.01, ρ v_(t−1) + (1−ρ)(clip(delta_t)−m_(t−1))²)
advisor may override when n ≥ 16 and m_t − z sqrt(v_t/n) > 0.

Değerler gelecek fiyatı sinyal anında kullanmaz, yalnız sonraki tamamlanan banka checkpoint'inde öğrenilir. delta yalnız bir aralığın karşı-olgusal farkıdır; tam portföy yolu optimalitesi veya teorik regret bound DEĞİLDİR.

## İtirazlı V19 deneyi — başarısızlık gizlenmedi

Önceki V19 sürümü risk uzmanını direkt karar merciine koymuştu. 128 sentetik dünyada V18 ortalama 173.545 USD iken ilk V19 151.219 USD oldu. Nakit yeniden giriş ölü kilidi düzeltildikten sonra V19 daha da bozuldu: 145.025 USD ortalama, en kötü 42.610 USD, p95 maximum-DD %53.591.
V19 bu nedenle ekonomik kabulden REDDEDİLDİ. Ayrı kaynak: V19_RISK_POLITIKASI_RET_RAPORU_20261016.md.

## V20 tam sentetik bilimsel kontrol

GitHub Actions: V15–V20 birleşik 126/126 test geçti, 0 hata. 128 zor dünya = sekiz hayali rejim × sekiz örnek × iki masraf düzeyi (%0.8 ve %2.5 her işlem yönü). Her deney başlangıcı 100 USD.
V20 ile V18 arasında 128/128 net sermaye sonucu EŞİT. Ortalama 173.545 USD, medyan 165.7755 USD, en kötü 67.9925 USD. Medyan maksimum geri çekilme %16.171, p95 maksimum geri çekilme %26.687. 80/128 dünya pasif altın vekilini geçti; 22/128 dünya nakitten daha kötü kapandı.
Risk danışmanı 56 kez aday öneri sundu. 55 tamamlanmış karşı-olgusal uzman kıyas etiketi öğrenildi. Danışman 56 kez yeterli güvenilir üstünlüğü kanıtlamadığı için reddedildi ve sıfır kez asıl kararı değiştirdi.
Bu yeni yöntem güvenli varsayılanı başarıyla KORUDU; V18'e karşı ek kâr veya gelişmiş drawdown gösterilmedi. 128 senaryo yalnız sentetiktir ve gerçek dünyada kör doğrulama sayılamaz.

## Akademik seçimler

Double Q: van Hasselt 2010; risk-kısıtlı RL/CVaR: Chow ve arkadaşları, JMLR 2018; kuantil dağılımsal RL: Dabney ve arkadaşları, AAAI 2018; robust dynamic programming: Iyengar 2005; online expert regret: Cesa-Bianchi ve arkadaşları 2006; çoklu deneme yanlılığı: Bailey ve arkadaşları 2017.
Bu yayınlardan fikir alınması V20'ye o çalışmaların kanıtlanmış optimum veya dağılım-dışı performans garantilerini kazandırmaz.
Kaynak: https://www.jmlr.org/papers/v18/15-636.html
Kaynak: https://ojs.aaai.org/index.php/AAAI/article/view/11791
Kaynak: https://pubsonline.informs.org/doi/abs/10.1287/moor.1040.0129
Kaynak: https://escholarship.org/uc/item/4w1110bb

## Açık bilimsel engeller

Gerçek geçmiş piyasa as-of veri adaptörü, kaynak ilk yayım denetimi, gerçek banka BID/ASK ve makas, V15 uzmanının V20 ile uçtan uca doğrulanan bağlantısı, tam durum-bağımlı portföy/likidite risk kısıtı, bağımsız yeni ileri örneklem ve üretim emir kontrolü henüz yok.
2023–2026 tarihleri önceki projelerde görüldüğünden o yılları tekrar kullanmak gerçekten kör dönemi oluşturmaz. V20 ancak parametreleri kilitli halde gerçek veriye bağlanıp sonra bağımsız yeni dönemde değerlendirildiğinde ekonomik güven düzeyi yükseltilebilir.

Karar: V20 KAVİS–ATLAS en son tamamlanmış bütünleşik araştırma adayıdır; yatırım için uygunluğu kanıtlanmış nihai ticari model DEĞİLDİR.