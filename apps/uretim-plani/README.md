# Şönt & Harmonik Üretim Planlama — simulation3

Bu modül, ana SIM3 Windows otomasyonunu değiştirmeyen bağımsız bir tarayıcı uygulamasıdır. **Makine yatırımı için ürün bazlı üretim partilerini görünür kılar; makine kapasitesini henüz hesaplamaz.**

## Uygulamayı açma

`apps/uretim-plani` içindeki `index.html`, `app.js`, `style.css`, `data-packed.js` dosyalarını **aynı klasöre** indirin. Windows'ta `index.html` dosyasını Chrome veya Edge ile açın. İnternet bağlantısı ve Excel gerekli değildir.

Takvimde renkli üretim adedine tıklayın: o ayın üretilecek ürünleri aşağıda listelenir. **Bütün ürünler tek tabloda alt alta görünür.** Teknik özellikler ayrı sütunlardadır; ürün arama ve şönt/harmonik filtreleme yapılabilir. Hiçbir ürün için ayrı bir İncele işlemine gerek yoktur. Arama ve planı CSV olarak indirme seçenekleri de vardır.

## Parti kuralları

| Yıllık adet | Parti | Aralık |
|---:|---:|---|
| 1–200 | 1 | Tek sefer |
| 201–500 | 2 | 6 ayda bir |
| 501–1.000 | 3 | 4 ayda bir |
| 1.001 ve üzeri | 4 | 3 ayda bir |
| 0 | 0 | Üretim yok |

1 partili **108 ürünün hepsi Haziran** ayında; 2 partili **14 ürünün hepsi Mart ve Eylül** aylarında olacak şekilde başlar. İlgili aylar kullanıcı tarafından birlikte değiştirilebilir. 3 ve 4 partili ürünlerin fazları için Plan A (adet bazında dengeli) veya Plan B (ortak başlangıç) seçilebilir.

## Veriler ve güvenilirlik

2026 şönt ürün matrisinden **25**, harmonik ürün matrisinden **110** satır içeren **135 satırlık** veri paketi kullanılır: 35.772 şönt + 9.316 harmonik = **45.088 yıllık adet**. Üretimi olan 133 satır için yıllık 175 üretim partisi planlanır. Sıfır adetli iki satır üretim dışıdır. Aynı kodla farklı açıklamalar satır bazında korunur.

Elektriksel değerler, ölçüler, ağırlık, bağlantı, teknik veri durumu ve kaynak alanları matristeki içerikten taşınmıştır. Sarım tipi ve proses reçetesi gibi doğrulanmamış alanlar **Doğrulanmadı** olarak gösterilir.

**Sınır:** Yıllık toplamları ve parti aylarını hesaplar; sarım, kurutma, VI/VPI, kürleme ve fırın kapasitesi için çevrim süreleri, yük geometrisi ve proses reçeteleri ayrıca doğrulanmalıdır.
