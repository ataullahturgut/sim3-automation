# Şönt & Harmonik Üretim Planlama — simulation3

Bu dizin, SIM3 Windows otomasyonunun ana dosyalarını değiştirmeyen bağımsız bir tarayıcı uygulamasıdır. Hazırlık amacı **makine yatırımı için yıllık üretim takvimi ve parti yüklerini görünür kılmaktır**. Kesin makine kapasitesi hesabı değildir.

## Açma

1. Bu dizindeki `index.html`, `style.css`, `app.js`, `data-packed.js` dosyalarını aynı klasörde bulundurun.
2. Windows'ta `index.html` dosyasını Chrome / Edge ile açın. İnternet bağlantısı gerekmez.
3. Takvimdeki renkli üretim miktarına basın: o ayın ürünleri aşağıda listelenir. **Tüm ürünler tek tabloda alt alta görünür. Şönt kaynağındaki 19, harmonik kaynağındaki 22 özgün alanın tamamı aktarılmıştır.** Üretim ve miktarın yanında kıyas kodu/önerisi, numune/kontrol, kıyas nedeni, yapı referansı, standart/varyant, katalog/teknik veri durumu, inceleme eksikleri, kaynak ve kayıt bilgisi dahil 32 sütun vardır. Tabloda yatay/dikey kaydırma, ürün arama ve şönt/harmonik filtresi vardır; ayrı ürün detayı açılmaz.

## Temel kurallar

| Yıllık miktar | Parti sayısı | Üretim aralığı |
|---:|---:|---|
| 1–200 | 1 | Tek sefer |
| 201–500 | 2 | 6 ay |
| 501–1.000 | 3 | 4 ay |
| 1.001+ | 4 | 3 ay |
| 0 | 0 | Üretim dışı |

- İlk açılışta **1 partili ürünlerin tamamı Haziran** ayında, **2 partili ürünlerin tamamı Mart/Eylül** aylarında yer alır. Bu aylar seçeneklerden birlikte değiştirilebilir.
- **Plan A (dengeli dağılım)**: 3 ve 4 partili ürünlerin başlangıç fazlarını adet bazlı dengelemeye çalışır; referans gösterilen GA5102 ve GA5002 ürünlerinin ayları korunur.
- **Plan B (ortak başlangıç)**: Tüm 3 partilileri Mart/Temmuz/Kasım; 4 partilileri Ocak/Nisan/Temmuz/Ekim aylarında başlatır.
- Yıllık toplam **45.088 adet**, üretimde **133 satır**, üretim dışı **2 satır**, yıllık **175 parti**.
- Ürün matrisinde aynı stok kodu farklı model açıklamasıyla tekrar edebiliyor; bunlar birleştirilmeden satır bazında tutulur.
- **Veriler:** şönt matrisi 25 satır, harmonik matrisi 110 satır. Veri paketi `data-packed.js` içinde sıkıştırılmış olarak bulunur, yeniden veri indirme gerekmez. Kaynak teknik durumları ve uyarılar tablodaki ilgili sütunlarda korunur.

## Yatırım çalışması için henüz gereken veriler

Sarım işlemi süreleri, sarım tipi/iletken kesiti, nüve ve bobin boyutları, impregnasyon yöntemi (VI/VPI), fırın raf/yük düzeni ve proses sıcaklık/süre reçeteleri doğrulanmadan **makine adedi veya kurutma kapasitesi önerisi** yapılmamalıdır.

## Kontrol

`node test_app.js` komutuyla paket yükleme ve toplam sayım testi yapılabilir (Node.js 18+). Tarayıcı için son kullanıcıya Node.js gerekmez.
