# GOLD V43 — V22 ERKEN RİSK VE YÜKSELİŞTEN DÜŞÜŞE GEÇİŞİN AYRI SİNYALLER OLARAK TESTİ

**31 Ekim 2026 | GERÇEK NEON 15 dakikalık fiyatlar | Araştırma, canlıya alınmadı**

## Amaç ve araştırmanın yeniden tanımı

Tek görev: **V22 önceden büyük düşüş riski verdiğinde, altın hâlâ yükseliyorsa boşuna SAT/ÇIK sinyali üretmemek; yükseliş kırıldığına dair yeterli fiyat kanıtı oluştuğunda erken ama seçici ÇIK/SAT sinyali üretmek.** Alış, yeniden alış, nakitte bekleme politikası, portföy getiri optimizasyonu **BU ÇALIŞMANIN YOK**.

Altta V22 her zamanki gibi **EARLY_RISK** olarak kalır. Ardından çıkış algoritması `WATCH` durumunda **sadece o ana kadar görülebilen** 15-dk fiyatları, son 4 saatlik getiriyi ve fiyatın son **96 gözlem çubuğundaki** en düşük seviyesini analiz eder. Yapısal kırılma koşulu:

1. V22 uyarısını izleyen ilk uygun fiyat gününde izleme başlar.
2. WATCH sırasında gözlenen en yüksek 15-dk kapanıştan güncel kapanışa gerileme **≥%1**.
3. Son dört SAATİN **kesintisiz 16 barlık** fiyat değişimi **≤−%1**.
4. Güncel 15-dk kapanışı, *önceki 96 gözlemin* en düşük kapanışının altına iner (bir yapı/destek kırılması). Hesapta bugünkü bar önceki 96 bar sınırına dahil edilmez.
5. Üç koşul aynı anda oluşursa çıkış işareti; ancak model testinde eşleşme/geçerlilik **yalnızca sonraki fiyat barından** skorlanır. İşlem emri gönderilmez.

Bu yaklaşım teknik olarak fiyatın yükselme süreci ile ardışık aşağı yönlü rejim dönüşünü ayıran **çevrimiçi fiyat yapısı ve momentum teyidi** yaklaşımıdır. *Bir sonraki kapanışın gerçek piyasada işlem yapılabilir olduğu kanıtlanmamıştır.*

## 2026 bütün mevcut V22 uyarı kümelerinin skorlanması

Veri: `public.gold_research_histdata_xau15m_candidate`, HistData XAU/USD 15m *noncanonical* araştırma arşivi **2026-01-01–2026-10-01 04:45 UTC**. V22 günleri tarihsel V33 dosyasından okunur; her V22 D gününde ilk kullanılabilir risk işareti ancak **D tarihinden sonraki fiyat günündedir**. Birbirine 8 veya daha az V33 fiyat işlem günü uzaklıktaki sinyaller **tek risk kümesine** alınır. Toplam altı risk kümesi kayıttaki intraday aralığına sığdı; 28 Eylül kümesinde gelecek beş tamamlanmış fiyat günü yok ve sinyal koşulu oluşmadı. 2026 Ekim uyarıları intraday aday seri 1 Ekim'de bittiği için skorlanamaz.

Aşağıdaki zamanlar UTC'dir; saat damgası **15-dk bar başlangıcı** olabilir, gerçek firstprint doğrulanmış değildir.

| İlk V22 risk | V43 yapısal SAT sinyali | Sonraki bar fiyatı | İşaretten sonraki beş fiyat gününde dip/işaret fiyatı | Sonuç |
|---|---|---:|---:|---|
| 22 Ocak | **29 Ocak 15:15** | **5.120,715 USD/ons** | −%13,069 | Eşleşti; 22 Ocak'ta hemen satışa göre ilave yükseliş korundu |
| 19 Mart | **20 Mart 14:15** | **4.575,655** | −%9,748 | Eşleşti |
| 17 Nisan | **21 Nisan 15:45** | **4.747,785** | **−%1,863** | **SONUÇSUZ ÇIKIŞ / FALSE ALARM** |
| 5 Haziran | **9 Haziran 15:30** | **4.300,285** | −%6,297 | Eşleşti |
| 10 Ağustos | **25 Ağustos 05:30** | **4.625,665** | −%4,818 | Eşleşti; Ağustos başındaki yükselişte hemen satış yapmadı |
| 28 Eylül | Uyarı koşulu teyit edilmedi | — | Gelecek 5g olgunlaşmamış | **Sansürlü**, yanlış alarm/başarı sayılmadı |

**Deneyde beş olgunlaşmış çıkış sinyalinin 4'ü, takip eden beş farklı işlem gününde ≥%4 XAU 15m kapanış düşüşüyle eşleşti**; 1 sinyal Nisan ayında karşılıksız kaldı. Günlük V22'yi doğrudan SAT kabul ettiğimiz aynı risk kümelerinde: **2 eşleşen / 3 eşleşmeyen**.

**Yükselişin V22 sonrası kaçırılması:** V22 anında SAT ile izleme kümesi kapsamında SAT sonrası görülen zirveye kadar ortalama **%4,738** ilave fiyat yükselişi bulunuyor; V43 yapısal yönteminin SAT sonrası kalan ilave yükselişi ortalama **%1,570**. Bu iki değer *örneklemde geriye dönük hesaplanmıştır*, canlı kârlılık hesabı değildir. Zirve gününü algoritma hiçbir şekilde önceden bilmez.

## Aynı dönemde önceden tanımlanmış alternatif kurallar

| Kural | Çıkış verilen kümeler | Olgunlaşmış sinyal / ≥%4 sonraki 5g | Sonuçsuz | SAT sonrası ortalama ilave yükseliş |
|---|---:|---:|---:|---:|
| V22 anında SAT | 6 | 2/5 | 3 | %4,738 |
| Yalın ≥%2 takip zirvesi geri çekilmesi | 5 | 3/5 | 2 | %3,268 |
| ≥%1,5 geri çekilme + dört saat −%1 | 5 | 3/5 | 2 | %5,352 |
| ≥%2 geri çekilme + dört saat −%1 | 5 | 3/5 | 2 | %3,419 |
| ≥%3 geri çekilme + dört saat −%1 (önceki V42 aday eşiği) | 5 | 3/5 | 2 | %2,198 |
| Volatilite normalize CUSUM + dört saat −%0,75 | 5 | 3/5 | 2 | %3,594 |
| Volatilite-adaptif tepe geri çekilmesi + dört saat −%0,75 | 6 | 3/5 | 2 | %2,620 |
| **Önceki 96 bar dip kırılması + tepe geri çekilmesi + 4 saat düşüşü** | **5** | **4/5** | **1** | **%1,570** |

Küme sayısı **azdır** ve adaylar 2026 olayları artık bilinirken araştırılmıştır. Üstteki 4/5 oranı **gerçek bağımsız ileriye dönük test / %80 doğrulanmış isabet değildir**. Gözlemleri çoğaltıp binlerce alarm gibi göstermemek için 5 temel olay kullanıldı.

## Fiyat gecikmesi stres testi — V43 yapısal sinyal

Sabit tarihli beş sinyalin her birinde aynı alım/satım davranışını simüle ETMEDEN, yalnız tarihsel bar fiyatını 15/30/60/120 dakika sonraya taşıyarak beş fiyat gününün takip dip yüzdesi yeniden ölçüldü (dinamik karar modelinin tam stres testi değildir).

| V43 çıkış örneği | Normal fill sonrası dip | +15 dk | +60 dk | +120 dk |
|---|---:|---:|---:|---:|
| Ocak | −%13,07 | −%14,09 | −%15,56 | −%17,07 |
| Mart | −%9,75 | −%9,51 | −%9,49 | −%9,85 |
| Nisan | **−%1,86** | −%1,75 | −%1,50 | **−%1,00** |
| Haziran | −%6,30 | −%6,18 | −%5,68 | −%5,23 |
| Ağustos | −%4,82 | −%5,06 | −%5,17 | −%5,07 |

Tüm bu **sabit-sinyal** gecikme senaryolarında aynı 4/5 eşleşme korunuyor. Fakat bankanın ask fiyatları/bid fiyatları, 15m kapanışın gerçek zamanlı yayın erişimi ve varyasyonlu spread yok.

## Akademik çerçeve

- *Trading to Stops*, Imkeller ve Rogers, SIAM Journal on Financial Mathematics (2014), DOI 10.1137/130911706: iz süren stopların ve maliyetlerin zamanlamayla ilişkisi.
- *When do stop-loss rules stop losses?*, Kaminski ve Lo, Journal of Financial Markets (2014), DOI 10.1016/j.finmar.2013.07.001: fiyat momentum rejiminde stop kurallarının artı veya eksi değer üretmesi.
- *A note on online change point detection*, 2023/2024, DOI 10.1080/07474946.2023.2276170: CUSUM ve çevrimiçi değişim tespiti çerçevesi.

Literatür algoritmanın **bu belirli parametrik hali için başarı iddia etmiyor**; yalnız yöntem sınıflarının bilimsel altyapısını sağlar.

## Kesin sınırlamalar ve gereken doğrulamalar

1. Verinin ilk yayın zamanları, V22'nin canlı üretildiği gerçek gün/saat ve XAU 15-dk aday kapanışı *ilk-izlenebilir* olarak doğrulanmamış.
2. Bu 2026 dönemi daha önce çok defa incelendi; *araştırmacı aşırı uyumu (selection bias)* riski yüksek. **4/5 oranı hipotez üreticidir.**
3. V22'nin bulunmadığı **Mayıs gibi dönemlerde V43 hiç risk izlemeye başlayamaz**. Bu çalışma **riskten çıkış teyidini** iyileştirir; V22'nin olay yakalama oranını tek başına artırmaz.
4. 2024–2025 için birebir gerçek V22 sinyal günlüğü bulunmuyor. V41/V42'deki sentetik V22 benzeri uyarılarla bu araştırmanın kalibrasyonu kanıtlanamaz. Aynı gerçek V22 modelini 2024–25 üzerinde ilk yayın bilgisine sadık biçimde yeniden çalıştırmak veya prospektif ilk-yayın gölge günlüğü tutmak gerekir.
5. Alım/yeniden giriş ve portföy performansı hesaplamadık. %1,6 maliyet yalnız muhtemel işlem avantajının çok dar düşüşlerde anlamsız kalabileceğini gösteren **ekonomik eşik** olarak değerlendirildi.
6. Nisan yanlış satış işaretini azaltmak için 2026 verisine bakıp bir eşik daha ilave etmek **mevcut değerlendirmenin bağımsızlığını tamamen bozar**. Eşikler dondurulmalı; farklı ve ileri dönemlerde yeniden denenmeli.
7. Geriye dönük kümeler, V22 günleri arasında en çok 8 işlem gün boşluk olması kuralıyla birleştirildi; gerçek sürekli izleme (streaming) **anlık durum makinesi** ve sinyal denetim kaydı henüz tamamlanmış değildir.
8. İşlem emri yok, model üretimine geçiş yok. Veritabanı salt-okunur.

## Tekrar üretim

Kod: `gold_axis_2026/research/case_control_v13/risk_v43_watch_exit_event_audit.py`
Test: `gold_axis_2026/research/case_control_v13/test_risk_v43_watch_exit_event_audit.py`
Workflow: `.github/workflows/gold-v43-watch-to-exit-episode-audit.yml`
Actions: https://github.com/ataullahturgut/sim3-automation/actions/runs/41181490249

**11/11 birim test**, Neon gerçek fiyat sorgusu ve bütün sonuç dosyası GitHub Actions üzerinde çalıştı. Her iki kaynağın gerçek signal/PIT sertifikası eksik olduğundan araştırma taslak tutulacaktır.
