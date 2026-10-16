# V20 KAVİS–ATLAS | Claude bağımsız denetimi sonrası düzeltme R1

**Tarih:** 16 Ekim 2026. **Dal:** `research-gold-v20-audit-repair-20261016`. **PR:** #137.
**Statü:** Algoritma araştırma düzeltmesi; V20 orijinali ve V18 karşılaştırma modeli değiştirilmedi. Gerçek XAU/USD, gerçek banka BID/ASK ve canlı emir kullanılmadı.

## Neden düzeltme gerekliydi?

Bağımsız inceleme V20'de `null` limitin `0`'a dönüşüp sahte ihlal sayımı ürettiğini, risk danışmanının 128 dünyada hiç etkinleşmediğini, risk sınırının gereksiz zorunlu satışlarla sermayeyi kötüleştirdiğini, EWMA güven hesabının etkin örneklem yerine ham `n` kullandığını, uzun veri boşluğunun CVaR eğitimiyle birleştirildiğini, checkpoint shadow/lastFill alanlarının tam denetlenmediğini ve npm test kapsamının eksik olduğunu ortaya koydu.

## R1 kod düzeltmeleri

1. `breach = maxDrawdownPct !== null && drawdownPct > maxDrawdownPct` koşulu hem `gapDrawdownBreached` hem audit sayacında kullanılır. Limit yokken hiçbir sahte ihlal üretilmez.
2. `quote()` süresi dolduğunda `pendingContext`, `risk.lastFill` ve iki-aralıklı risk kaydı birlikte temizlenir. V18 `backup` bir uzun aralığı `accepted:false` döndürürse bu aralık tek-adım risk/CVaR etiketine girmez; iki-aralıklı etiket zinciri de kesilir.
3. `restore()` `lastFill`, fiyatta pozitiflik ve sonlu değer, ücret, zaman damgası, shadow pozisyonu/aile/eylem eşleşmesi ve bekleyen iki-aralıklı kayıtlarını denetler.
4. EWMA ortalaması sıfırdan başlanma yanlılığı için `1-rho^n` ile düzeltilir. Geometrik ağırlıkların etkin örneklem sayısı `ESS=((1+rho)/(1-rho))*((1-rho^n)/(1+rho^n))` olarak hesaplanır. Rho=.94 için sonsuz veri limitinde ESS yaklaşık 32.333 olur; ham örnek adedinin sonsuza gitmesi güveni sıfırlamaz. `advisorConfidence` ihtiyatlı araştırma eşiği 1.64'tür; **istatiksel garanti veya gerçek kapsama kalibrasyonu DEĞİLDİR**.
5. Gölge uzman STRESS döneminde GOLD=>SELL, CASH=>WAIT; RALLY döneminde CASH=>BUY, GOLD=>WAIT önerir, ama bu öneri uygulama yetkisi değil yalnız ayrı değerlendirme adayıdır. Altı koşullu STATE×REGIME hücresi (STRESS/RALLY/QUIET × CASH/GOLD) risk skorlarının karışmasını önler.
6. Aday ve V18 ana politika aynı bankaca gözlenen fiyata karşı işlem maliyeti SONRASI ilk fiyat aralığı ve ilk eylemi yaptıktan sonra bir sonraki aralık boyunca ek işlem YAPMAMA koşulundaki **iki-adım sabit-pozisyon** alternatifine göre değerlendirilir. Üçlü şart: yeterli karşı-olgusal gözlem, pozitif ESS-düzeltilmiş alt skor (1-adım) ve pozitif (2-adım). Bu tam dinamik yeniden giriş/çok-adımlı MDP değildir.
7. Eskiden `criticalBudget` ile olgunlaşmamış risk uzmanı doğrudan zorunlu SAT yetkisi alırdı. Bu istisna kaldırıldı. Gerçekleşmiş Drawdown eşiği aşılması uyarı oluşturur; kanıtlanmamış SAT'a otomatik izin vermez.
8. İsteğe bağlı `enforceEntryRiskBudget:true` yalnız kullanıcı bir `maxDrawdownPct` bütçesi tanımladıysa ve olgunlaşmış zarar-kuyruğu tahmini planlanan yeni ALTIN pozisyonunun riskini aşırı buluyorsa **işlem öncesi AL engeli** üretir. Varsayılan false; zarar sınırı garantisi veya koruyucu satış emri değildir.
9. Hazır olmayan Q kararında WAIT'e geçiş artık gerekçe kodunda `LEARNER_NOT_READY` olarak işaretlenir. `V19_` adları düzeltilmiştir.
10. Orijinal `npm test` betiğine dokunulmadan, araştırma paketine `npm run test:kavis-research` eklenmiştir.

## Başarılı gerçek CI çalıştırmaları

Son CI: önceki V16–V18 ve yeni R1 adversarial sözleşmelerde **76/76**, V15–V20 bütün paket sözleşmelerinde **139/139** başarılı, 0 başarısız.
Yeni testler: `null` limitli drop, açık limitli drop sonrası zorunlu satışı reddetme, süresi dolan ve sıçrayan gecikmeli kotasyon, bozuk checkpoint shadow/price, EWMA ESS sınırı, sahte fiyat enjekte etmeme, iki aralıklı etiketin tam zamanı, `useRiskPolicy=false` ile V18 Q özdeşliği; kontrollü devamlı düşüşte gölge uzman gerçekten SELL yetkisi kazanır ve ters fiyatlı STRESS ortamında kazanamaz.

## 128 daha önce kullanılmış kurgusal dünyanın finansal sonucu

Başlangıç 100 USD; aynı 8 kurgu rejimi × 8 tohum × %0.8/%2.5 banka ücreti.
- Eski V20: ortalama **173.545**, 21,502 **yanlış** limit ihlal uyarısı, 55 tek-adım gölge etiketi, 0 danışman etkinleşmesi.
- Düzeltilmiş R1: ortalama **173.545**, **0** yanlış uyarı, **10,813** tek-adım ve **10,790** iki-adım gölge etiket; 0 danışman etkinleşmesi.
- V18 kontrol de ortalama **173.545**. Böylece R1 temiz senaryolarda V18'i geçtiği iddia edilemez.

## Özellikle Claude'un 24 dünya, %15 maksimum düşüş deneyinin yinelenmesi

Fiyat ailesi: gap_crash, whipsaw, fat_tails; 8 tohum her biri; %0.8/her yön; 100 USD başlangıç.
- Eski V20: ortalama final **188.492 USD**, ortalama max DD **%26.984**, en kötü sermaye **39.475 USD**, ortalama/birleşik çok sayıda zorunlu SAT.
- Düzeltilmiş R1 (`maxDrawdownPct:15`, ama zorunlu SAT yok): ortalama final **238.623 USD**, ortalama max DD **%14.568**, en kötü sermaye **79.863 USD**.
- Düzeltilmiş R1 + `enforceEntryRiskBudget:true`: ortalama final **236.490 USD**, ortalama max DD **%14.368**, en kötü sermaye **79.863 USD**.
- **%15 zarar bütçesi bir gerçek maksimum düşüş garantisi değildir.** R1 sonuçlarında limit aşımı örnekleri vardır; gap fiyatları ve banka maliyetleri bakanın kontrolünde değildir.

## Ayrıca bağımsız tasarlanmış yeni 64 kurgu dünya (8 rejim × 4 tohum × 2 ücret)

Bu dünyalar önceki V18 `series()` üretecini kullanmaz. Sonuç ortalama V18 **319.915145 USD**, onarılan model **319.915188 USD**, eski V20 **319.915188 USD**. 64 dünyanın 61'i eşit, 1'inde az farkla daha iyi, 2'sinde az farkla daha kötü; pratik olarak değişim yok. En kötü final onarılan model **60.848 USD**. Olgunlaşan gölge etiket sayısı 3,974 tek-adım ve 3,954 iki-adım, **0 etkin risk uzmanı**.
Bu gözlemler de bağımsız gerçek altın kör dönemi değil; sentetik ölçüm ve kod regresyon araştırmasıdır.

## Bilimsel kabul kararı

**R1 bir hata düzeltme ve öğrenme denetimi ilerlemesidir, kanıtlanmış yeni finansal alfa değildir.** Yeni gölge uzmanı kontrollü etiketli stres deneyinde çalıştırabildik; toplam 128+64 kurgu ekonomi ortamında yine gerçek karar değiştirecek kadar pozitif kanıt toplamadı. Bu kusur gizlenmemeli. Kanıt eşiğini aşırı gevşetmek yerine, bağımsız kalibre edilmiş piyasa ve banka verisine ihtiyaç vardır. Doğru sermaye, 1/2-aralık karşı-olgusal etiket ve güven ölçütleri ayrıca gerçek bid/ask ile doğrulanmalıdır.

**Banka canlı emirleri kapalı. V18/V20 orijinalleri korunmuştur.**