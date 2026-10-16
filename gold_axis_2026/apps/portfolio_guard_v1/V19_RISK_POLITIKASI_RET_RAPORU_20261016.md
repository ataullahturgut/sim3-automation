# V19 KAVİS-SİPER reddedilen risk politikası — sentetik düzeltme denetimi

16 Ekim 2026, araştırma değerlendirmesi. Gerçek altın tarihi veya banka canlı emir verisi kullanılmadı.

**Yazılım sözleşmesi:** İlk V19 113/113, nakit yeniden giriş ölü kilidi giderildikten sonra 115/115 sentetik teknik test başarılı.

**Ancak ekonomik kabul RED:** 128 kurgusal stres dünyasında V18 ortalama 173.545 USD iken ilk V19 151.219 USD oldu (26 üstün, 57 zayıf, 45 eşit). İlk tasarım CASH pozisyonu önceki toplam portföy zararını geri alamadığından sürekli giriş yasağına yol açıyordu; 13.218 kez giriş engellendi.

**Bir sonraki yapısal düzeltme:** Gerçekleşmiş düşük NAV, nakitteyken tek başına yeni AL'ı süresiz yasaklamamalıdır. CASH yeniden girişini ileriye dönük risk ve yeni toparlanma örüntüsüne bağlayan anti-deadlock değişikliği yapıldı ve testten geçti; buna rağmen 128 aynı yapay dünyada V19 ortalama **145.025 USD**, en kötü **42.610 USD**, p95 maksimum geri çekilme **%53.591** görüldü. V18 aynı dünyalarda ortalama **173.545 USD** idi. Yani risk politikası daha sık zorunlu SAT üreterek koruma hedefinin tersine çalışabildi.

**Karar:** Sabit hard stop ve salt kuyruk kaybı tahmini üzerinden direkt SILAHLI emir önerisi, kendi başına kanıtlı strateji değildir. V19 canlıya alınmaz veya V18 üzerine otorite olarak terfi edilmez.

**V20 zorunlu kabul şartı:** Risk uzmanı ve baz Double Q ayrı kalacak; uzman önerilerinin daha önceki tamamlanmış koşullu işlem aralıklarında maliyet sonrası karşı-olgusal üstünlüğü ispatlanmadıkça risk uzmanı temel politikayı değiştirmeyecek. Explicit kullanıcı zarar bütçesi varsa ancak o zaman sert müdahale ayrıca kullanıcı profiline bağlı olarak çalışacak; yine gap risk garantisi iddia edilemez.

Deney yıllarından hiperparametre seçilip kör test denemez. Kod deney dallarında korunur, başarısızlık raporu silinmez.
