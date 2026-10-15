# GOLD / GUARD — RECOVERY ENTRY + HOLD V3
**15 Ekim 2026 | Araştırma protokolü (uygulanan/ticarî onaylı model DEĞİL)**

## Kullanıcının hedefi
Ocak sonunda NAKİT olan $119.75391720039644 portföyü, Şubat 2026'da yükselişi mümkün olduğunca erken fark ederek altına taşıyabilmek; devam eden yükselişte %0.8 tek yönlü komisyon ve banka makasını ödeyerek gereksiz çık-gir yapmamak. **Şubatın ilk barını bilebilme hedefi yoktur:** İlk karar anında Şubat ayı sonucunu bilmek mümkün değildir. İstenen işlem fırsatını, *o an erişilebilir bilgiyle* tanıyan genellenebilir mekanizma gereklidir.

## Frozen as-of gerçekler
- 2026-02-02 03:45 UTC (06:45 Türkiye) ilk tam M15 karar kesiti: XAU MID c **4664.308**, işlem proxy p **4665.628**; r4 **-%2.289**, r92 **-%10.71189**, r276 **-%10.84723**, son 276 bar tepeye göre DD **-%16.49338**, RV4 **%4.16237**. Burada körlemesine %100 AL agresif bir karşı-trend kararıdır.
- V1 15m ilk girişi **2026-02-09 14:45 UTC**, fiyattan **5036.275**; Şubat'taki 4 AL + 3 SAT sonrası **114.27446809487914** USD varsayımsal net likidasyon (altında pozisyon korunuyor).
- Ocak bitimindeki $119.753917 nakitle Şubat ilk kesitte satın alıp ay sonu sadece *hipotetik* tasfiye: **132.906170** USD. Bu alternatif yalnız sonuç karşılaştırma sınırıdır; bir as-of tahmin kanıtı değildir.
- February frozen as-of panel: **1723** M15 satırı, Git blob `8e3bb94acc3d38d12778439115292388b295734f`. Gerçek banka BID/ASK ve spread yok.
- Şubat 3 Şubat 01:15 UTC (04:15 Türkiye) kesitinde r4 **+%2.91899**, r92 **+%4.02774**, r276 **-%12.15451** gözlemlendi. *Gerileme sonrası kısa vadeli olumlu dönüş* adayıdır; giriş sinyali olduğunu kanıtlamaz. Bu ilk örnekten altın alıp ay sonu tutmak geçmişten bakıldığında **128.411146** USD ederdi. **Bu Şubat'a bakılarak seçilmiş araştırma örneğidir; validasyonda başarı sayılamaz.**
- Kronoloji kontrolü: HistData 2023: **16.890** uygun intraday kesitte; 2024: **22.657**; 2025: **22.600**. Yalnız bu zaman evreninde `r276<=-5 && r92>=+2 && r4>0` koşuluna uyan geçmiş gözlem **0/62.147**. 2026 Ocak–Şubat toplamında aynı katı şablona uyan 64 bar sadece iki takvim gününde gerçekleşiyor. Aynı barlar bağımsız öğrenme örnekleri değildir. Bu, 2023–25 arşivinden şablonun olasılık/başarı oranını öğrenemeyeceğimizi gösterir.
- Hafifletilmiş `r276<=-3 && r92>=+1 && r4>0` durumuna 2025'te yalnız 3 tarihsel takvim gününde (37 bar) rastlandı, 2023–24'te sıfır. Bu eşik de yeterli vaka desteği değildir.
- Tüm sonuçlar geriye dönük araştırmadır; 2026 Şubat bugün görülmüş olduğundan sonraki V3 eşiklerini Şubat'a uydurmak **kör doğrulama değildir**.

## Model mimarisi (V1 dondurulur, V3 ayrı araştırma sınıfı)
**Katman A — Aylık / haftalık temel yön**: Ay başlangıcında bilinen aylık XAU eğilimi/tahminini ve önceden dondurulmuş eğilim rejimini kullan; pozitifse yükselişi kaçırma maliyetini artır, ancak otomatik AL yetkisi verme. Gelecek aya ait makro/gün sonu haberleri ve daha sonra yayımlanan revizyonlar yasak.
**Katman B — Şok evresi**: Ayrı durumlar `FALLING_FAST`, `CAPITULATION`, `STABILIZING`, `RECOVERY_CANDIDATE`, `TREND_CONFIRMED`, `UNKNOWN`. 15m fiyat, RV, downside-var, dip/tepe, geçerli NQ/ZN, mümkünse doğrulanmış USD/2Y/XAG ve yayın-vintage ile *yalnız as-of* değişimleri izle. Aşırı OOD düşük risk skoru “güvenli” anlamına gelmez. Haber nedeni kanıtsızsa `UNKNOWN`.
**Katman C — Giriş**: `CASH -> WATCH_RECOVERY -> PARTIAL_GOLD -> GOLD`. Güvenilir dönüş kanıtı oluşmadan tamamını yatırma; varsayımsal parçalara ayırmayı ya da WAIT seçeneğini deney. 2023–25'te desteklenmeyen katı şok şablonunu genelleştirme. Bir girişin maliyetini ve eğer dönüş başarısızsa olabilecek zararı ayrı hesapla.
**Katman D — TUT/ÇIKIŞ**: Girişi tetikleyen 15 dakikalık titreşim tek başına hemen satışa dönmesin. **Giriş ve çıkış için ayrı eşikler (hysteresis)**, davranış evresi, kümülatif drawdown, çapraz piyasa teyidi ve *öngörülebilir kaçınılabilir kayıp* / tekrar alış maliyeti koşulunu kullan. Çok ciddi aşağı riskte bekletme kuralı devre dışı kalabilir; bu istisna ayrıca eğitilmeli/test edilmeli. Farklı risk state'lerinde gözlemleri karıştırma.
**Katman E — Maliyet/kayıp**: Alış %0.8 + satış %0.8 sabit alt sınır, gerçek ASK/BID+slippage ayrıca raporlanır. Tüm aksiyonlar GOLD/CASH pozisyonuna bağlı; satış+geri giriş ancak kaçınılabilir beklenen aşağı hareket > maliyet + muhtemel kaçırılan UP ise mantıklı. Karar verilemeyen riskte `ABSTAIN/WAIT/HOLD` geçerlidir.

## Öğrenme ve değerlendirme sözleşmesi
1. **Önce öğrenme evrenini genişlet:** 2023–2025 bu şiddette geri dönüş için örnek sunmuyor; eski 2010–2021 şoklarını yüksek kaliteli as-of XAU ve gerekiyorsa G10/makro fiyatlarla getir. Eski verinin frekansı/vintage eşdeğer değilse özellikleri sınırla, sentetik olayı gerçek diye sunma.
2. Öğrenme birimi 15m bar değil *bağımsız 24/48/96h epizot*tur. Mükerrer olay, iç içe piyasa düşüşü, ex-post seçilmiş swing yanlılığı ve yayın gecikmesini temizle.
3. İlk veri safhası: her epizod için (a) ilk belirti, (b) devam, (c) durulma, (d) toparlanma, (e) yeni yükseliş, (f) bozulan toparlanma; gerçek ekonomik katalizör kanıtı ayrı.
4. Model adayları: basit deterministik rejim/finite-state, kalibre edilmiş olasılık (lojistik/hazard/survival), rejim-switching ve geçmiş epizod benzerliği; karmaşık ANN ancak örnek yeterliyse. Bunlar ayrı ve sınırlı model ailesi olsun, FEB 2026'e eşik uydurulmasın.
5. Yürüyüş: 2023 öğren/2024 doğrula/2025 sonraki tarihli test, verinin yettiği yerde eski şoklarla daha eski originler. Sonra Jan 2026 başlangıç durumunu dondurup **Şubat'ı retrospektif stres** olarak izle; Şubat bilinmiş olduğundan kör OOS diye tanımlama. 96h hedefin olgunlaşmadığı durumda gelecek bilgi kullanılmaz.
6. Karşılaştırmalar: (i) CASH bütün Şubat, (ii) baştan GOLD buy-hold ORACLE-benzeri karşılaştırma (as-of strateji değil), (iii) V1 15m, (iv) V1 3h, (v) V3 basit rejim, (vi) V3 cost-aware TUT/çıkış. Karşılaştırmada ilk sermaye ve ortak fiyat saati/komisyon eşit olmalı; farklı işlem saati nedeniyle buy-hold'u yanlış karşılaştırma.
7. Metrikler: net son değer, maksimum ve 5% downside/DD, büyük -%3 alarm precision/recall, giriş gecikmesi, kaçan UP, gereksiz round-trip, toplam maliyet, şokta pozisyon, temerrüt/stale data ve rejim bazında worst-case.
8. Kabul: V3, önceki kronolojik dönemlerde V1 ve nakitte bekleme/altında tutma alternatiflerine göre sağlam performans göstermeden otomatik karar katmanına bağlanmaz. **Tek bir Şubat'ta $132.91 yakalaması kabul ölçütü değildir.** Çıkış maliyeti sonrası üstünlük ve stres riskini birden çok epizotta göster.
9. Öğrenme durumları ayrı kaydedilir: source_hash, model_version, train_until, as_of, entry_state, hold_state, threshold_version, label_maturity, evidence_verdict; gelecek ay aktarımı sadece olgun veriden yapılır. Değiştirilemeyen eski V1 geriye dönük korunur.

## Şu anki durum
**Ön inceleme ve V3 deney protokolü tamamlandı.** Eğitilmiş/dogrulanmış V3, geçmiş stres verisi ve banka maliyeti henüz tamamlanmadı; bu dosya getiriyi değiştirmez. Öncelik aşağı rejimlerde daha erken toparlanma tanıma ve işlem churn azaltma. Her yeni sonuca işlem ve karar defterinde hangi tarihte hangi verilere dayanıldığının yazılması zorunlu.
