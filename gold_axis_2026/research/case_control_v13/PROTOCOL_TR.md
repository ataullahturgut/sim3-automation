# V13 deney sözleşmesi — aday sonuçları hesaplanmadan yazıldı

Kaynak commit: 137c189f85a79742b9c0772e658cb9d65ff2cf32. Orijinal BASE14/CFTC21 değişmez.
Araştırma saat kuralı NY17:30; günlük referans fiyat ilk baskı veya gün içi fiyat değildir.
2000–2009 altın fiyatı için FRED kaldırılmış seri 404; BoE alternatifleri deneniyor. Kaynak yoksa kapsam eksik kalacak, fiyat üretme yok.

Fiyat olayları: sonraki 5 ortak seans minimumunda yüzde 5 kayıp veya ertesi seans yüzde 3 kayıp.
Örtüşen hedef aralıklarının birleşimi bir olay adayıdır. Başlangıç günlük proxy: olay aralığında yerel zirvenin sonraki seansı; gerçek intraday başlangıç kanıtı değildir.
Olay etrafında -30/+10 seans çıktı. Zirve öncesi 3 seans ve zirve günü pozitif öğrenme örnekleri; hedefteki gelecek fiyat yalnız örnek etiketi için.
Kontroller: aynı yıl, benzer geçmiş 20g trend/20g volatilite/dört metal 5g ayrışması; gelecekteki 10g yüzde5 veya ertesi gün yüzde3 kayıp olmayan, olaylara ve önceki kontrol pencerelerine en az 41 seans uzak adaylardan 3 adet. Bulunamazsa eksik sayılır; eşleştirme mesafesi raporlanır. Gelecek değerler mesafe/girdi değildir.

Özellikler: orijinal 21 grubuna ek 2Y nominal seviye/değişim, 10Y reel seviye/değişim, AG/PT/PD getirileri ve metal korelasyonları. Makro güncel arşivleri revizyon/ilk yayın kanıtı olmayan araştırma vekilleridir; strict mode bu girdilerle sinyal üretmez.
2010–2022 çok değişkenli olay-kontrol eğitimi. Ek tarihsel walk-forward: <=2016 ->2017–19; <=2019 ->2020–22. Olay bitişi eğitim sonundan önce; lookback sınırları ve 20 seans embargo.
Adaylar: L2 lojistik C=0.1; sığ GBM 60 ağaç, depth2, min_leaf10. Lojistik no-CFTC, no-USD, no-rates, no-GVZ ablation. Model sayısı/parametreleri 2026 sonucuyla değiştirilmeyecek.
Meta-filtre: (BASE14 kırmızı VEYA CFTC21 kırmızı) VE meta skor >= eşik. Eşikler eğitim skorunun [0,10,25,50] yüzdelikleri; sıfır yüzdelik yerine açık passthrough adayı. 2025'te 3/3 ertesi gün ve 3/3 beş gün etiket kümesini koruyanlar arasından minimum yanlış alarm günü; eşitlikte basitlik. Uygun aday yoksa iyileşme yok.
2026 yalnız dondurulmuş aday stres raporu; daha önce görülmüş olduğu için kör test değil. 2026 sonucundan model seçilmez.
Eski V8 tam reprodüksiyon ve CFTC 2023 ION gecikme-düzeltilmiş kontrol ayrı. Yeni modeller düzeltilmiş kontrolle aynı günlerde karşılaştırılır. +7g hafta vekili ilk yayın sertifikası değildir; 2013 ve2018–19 kapanma belirsizlikleri fail-closed dışlanır.
İyileşme ölçütü: büyük olay kaçırma, başlangıç öncesi günlük-proxy yakalama, yanlış kırmızı gün ve epizod birlikte. Kesin PIT gate kapalı; üretime alma yok.
