# V13 SENTEZ — özgün çok-ufuklu hibrit öğrenme ve sermaye büyütme deneyi

**16 Ekim 2026** · Araştırma dalı: `research-gold-v13-sentez-hybrid-20261016` · Bilimsel karar: **Terfi REDDEDİLDİ**.

## Kullanıcının isteği

ANN'nin geçmiş örneklerden ağırlık öğrenme gücü, ANFIS'in açıklanabilir bulanık kuralları, LSTM'nin uzun dönem unutma/hatırlama davranışını **tek bir özgün, öğrenen altın-nakit karar mekanizmasında** birleştirmek. Başarı hedefi yalnız UP/DOWN değil, bir bankada her AL ve SAT için ayrı ayrı %0,8 kesinti sonrasında portföy servetini büyütmek. Kazanç garanti edilmez; önceki kör-olmayan dönemi ezberletip başarı ilan edilmez.

## Gerçekte geliştirilen mimari

**1. ANN katmanı:** Daha önce V11 kapsamında doğrulanmış gerçek backpropagation/Adam ağını kullanır (14–12–8–2). Yıllık model yenilemesinde yalnız o yıl başlamadan vadesi tamamen dolmuş geçmiş 14 günlük getirilerle fit eder. Sinir ağı 14 günlük komisyon sonrası fırsat getirisini tahmin eder. *Bu bir ANN ağıdır.*

**2. Bulanık ANFIS-esinli katman:** UP, DOWN, STRESS, RECOVERY, RANGE, CARRY adlı altı normalized-Sugeno kuralının sabit öncül üyelikleri ve geçmiş sonuçlar olgunlaştıkça güncellenen lineer sonuç parametreleri bulunur. Kural etiketleri, gerçek nedensel ekonomik haber sınıfları oldukları anlamına gelmez. 14 ve 56 günlük net getiriyi ayrı tahmin eder. *Öncülleri uçtan uca eğitilmiş tam ANFIS değildir; ANFIS'in bulanık-karar + uyarlanan sonuç fikrinin problem için yeni birleşimidir.*

**3. Kapılı, tekrarlamalı hafıza:** Geçmiş trend/stres/toparlanma durumlarını belirlenmiş unutma/güncelleme kapılarıyla taşır; uzun vadeli bilgi kısa vadeli gürültüyle tamamen sıfırlanmaz. *Kapıları BPTT ile eğitilmiş gerçek LSTM değildir*; LSTM'den esinlenen, yeni örüntüler içeren recurrent durum özetidir.

**4. Tahmin birleştirme:** ANN'nin 14 günlük, Sugeno'nun 14 ve 56 günlük ve kapılı hafızanın 56 günlük uzman tahminleri; yalnız geçmişte sonuçlanmış öngörü hatalarından üretilen uzman ağırlıklarıyla harmanlanır. Sabit kod, ANN katkısının işe yaradığı sonucunu varsaymaz; ablation yapılır.

**5. Durumdan eyleme:** 14 günlük net getiri ve 56 günlük trend devamının birlikte fırsat göstermesi durumunda AL; riskli çıkış sinyali varsa SAT; diğer durumlarda BEKLE. Sinyal Türkiye 09.00'da oluşur, 12.00 veya sonraki ilk banka kontrol noktasında uygulanır. Mevcut karar eşiği hâlâ kısmen elle belirlenmiş olduğundan *tamamen kendi kendini optimize eden politika değildir*.

**6. Gecikmeli öğrenme:** 14 günlük geri bildirim kaynağı en çok 14 günde bir, 56 günlük geri bildirim en çok 28 günde bir seçilir. İkinci gruptaki etiketler bile 56 gün ufuk nedeniyle en çok 2 kez örtüşür. Gelecekteki etiketin zaman damgası vadesi dolmadan parametreler güncellenmez.

## Veriler ve icra

- 6.724 kronolojik geçmiş piyasa noktası; 947 geçerli 14 günlük ileri getiri; 918 geçerli 56 günlük ileri getiri. Bu kayıtlar birbirinden bağımsız 947/918 şok değildir.
- Her BUY'ta %0,8 ve SELL'de %0,8. Gerçek banka BID/ASK kotasyonu bulunmadığından yalnız MID fiyat vekili üzerinde işlem emülasyonu yapılabilir.
- Geleceği görme testi: bitiş tarihinden sonraki fiyatları değiştirince önceki alım kararlarının, geçmiş tahminlerin ve servetin değişmediği doğrulandı.
- Ekonomik OLAY-02/ÖĞREN-03 sınıflarında ilk yayımlanma/erişim saatleri tam teyitli olmadığından SENTEZ halen piyasa-teknik rejim öğrenir; haber-fundamental nedensellik iddia edilmez.

## Gerçek maliyetli portföy deneyleri

| Test | Nakit başlangıç | SENTEZ final | Pasif ALTIN final | İşlem |
|---|---:|---:|---:|---:|
| **2023 Ocak–2026 Eylül, sıfırlanmayan tek portföy** | 100,00 | **201,592579** | **224,272004** | 1 AL, 0 SAT; Eylül'de satış giderli değerleme |
| 2024 bağımsız sermaye koşusu | 100,00 | **113,867917** | **123,921763** | 1 AL |
| 2025 bağımsız sermaye koşusu | 100,00 | **160,535466** | **160,537328** | 1 AL |
| 2026 Şubat–Eylül, ayrıca 119,753917 nakit | 119,753917 | **97,295489** | **106,280709** | 1 AL |

Kesintisiz model **29 Kasım 2023 Türkiye 12.00**'de ALTIN alıp 2026 Eylül sonuna kadar tutmuştur. Son değerleme bankanın hayal edilmiş MID vekilinden sonra satış maliyeti kesilmiş tasfiye değeridir; gerçek bankaya SAT emri atılmamıştır.

Yıllık yeniden başlatılmış nakit portföyleri, kesintisiz 100 dolarlık koşuyla birleştirilemez. Önceki V12 REHBER kesintisiz 2023–2026 100,076881 USD ile karşılaştırıldığında yükselişe katılma tarafı iyileşti. Ancak **pasif altın 224,272004 USD ile daha iyidir**.

## ANN / bulanık kural / kapılı hafıza / 56 gün ayrıştırma sonuçları

| Kapalı katman | 2023–2026 tek portföy USD | 2024 100 USD | 2025 100 USD | 2026 119,75 USD |
|---|---:|---:|---:|---:|
| Tam SENTEZ | **201,5926** | 113,8679 | 160,5355 | 97,2955 |
| ANN çıkarıldı | 201,5926 | 116,7023 | 160,5355 | 97,2955 |
| Öğrenen bulanık Sugeno çıkarıldı | 186,1061 | 126,0493 | 160,5355 | 97,2955 |
| Recurrent kapılı hafıza yerine yalnız anlık piyasaya bakıldı | 114,6479 | 95,0792 | 122,9759 | 88,5028 |
| 56 günlük ufuk çıkarıldı; sadece 14 günlük politika kaldı | 86,9189 | 100,0000 | 100,0000 | 104,0888 |

**Dürüst çıkarımlar:**

- 56 günlük hedef ve geçmişi taşıyan hafıza bu deney setinde uzun trendi yakalamayı sağladı. Ancak geriye dönük testte oluşan bir fark tek başına ileri piyasa kârı garantisi değildir.
- ANN'nin **ek işlem getirisi gösterilmedi**; aynı 2023–2026 sonuçları ANN kapalıyken de elde edildi. 2024'te ANN'siz biraz daha iyi. ANN'yi yararlı ilan etmek bilimsel olarak yanlış.
- Öğrenen bulanık sonuç katmanı kesintisiz koşunun servetini artırsa da 2024'te onu çıkarmak daha iyi performans verdi. Katkı yıl bağımlı; genelleme kanıtı yok.
- Kapılı hafıza yerine kısa anlık özelliklerin kullanılması daha sık ve zararlı işlem üretmiştir; ancak iki alternatifin giriş politikalarının tamamıyla eşdeğer olduğunu iddia etmiyoruz.
- **SAT karar mekanizması halen yetersiz.** Kesintisiz koşuda yalnız 1 AL, 0 SAT gerçekleşmesi, 'maksimum kâr sağlayan öğrenilmiş strateji' değil, büyük ölçüde iyi bir girişten sonra altını tutma politikası ürettiğimizi gösterir.

## Başarısız satış hipotezinin negatif araştırma kaydı

2026'da gelecekteki 56 günlük net getiri tahmini negatife düştüğünde NAKİT'e geçme kararının ayrı denemesi **119,753917 → 78,050779** USD hesapladı; ana hibrit 97,295489 USD idi. Kesintisiz koşuda da 201,5926 yerine 145,6831 USD görüldü. Bu kural ekonomik gerekçeli olsa bile çok geç satış / yanlış yeniden giriş / fazla maliyet yüzünden sonuç kötüleşti; **ana modele eklenmedi**. Bu deneme geçmiş 2026 sonuçları görüldükten sonra yapıldığı için keşif niteliğindedir.

## Bilimsel kabul kararı

**V13 TERFİ REDDEDİLDİ.** Hem 2024 hem 2025'te pasif altını yenme şartı sağlanmadı; 2026 Şubat–Eylül başlangıcında nakitten de geride kaldı. 2023–2026 zaten incelenmiş bir örneklem olduğundan gerçek ileri kör sınama yoktur. Gerçek banka fiyatı, olayların makro ilk yayın zamanı ve kabul öncesi yeni bölünmüş deneyler bulunmadığından hiçbir yatırım tavsiyesi ya da otomatik emir oluşturulmaz.

## Çalışan dosyalar

- `v13_sentez_core.js`: ANN / Sugeno / gated state / vade-sonrası öğrenen uzman güveni.
- `v13_sentez_run.js`: geriye doğru bilgi okumayan 09→12 TR işlem simülasyonu, 14/56 gün getirisi, beş yapısal karşı deney, net servet.
- `v13_sentez.test.js`: data contract, vadesi dolmamış sonucu kullanma yasağı, gelecek bozulması testi, dondurulmuş PnL kontrolleri, sürüm güvenliği.
- `GET /api/algorithm/v13/sentez`: yalnız test ve rapor okur. Sol menüde **V13 SENTEZ hibrit öğrenen model** bölümü.

**Bir sonraki bilimsel adım:** Hazır trend tahmini yerine işlem eylem tercihinin (beklenen gelecek log servet değişimi, maksimum kayıp, yeniden giriş maliyeti) kendisini geçmiş tamamlanmış portföy epizotlarından öğrenen politika başlığı. Bu çalışmada bu başlık henüz yok; hiçbir gelecek kârı garantilemez.