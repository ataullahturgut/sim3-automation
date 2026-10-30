# V42 — V22 ERKEN UYARIYI SATIŞA DÖNÜŞTÜRME: KÂRI KORUMA VE MALİYETLİ GERİ GİRİŞ

**30 Ekim 2026 | Gold Control / GitHub sim3-automation | RESEARCH ONLY — PIT/BLIND DEĞİL**

## Değişen bilimsel hedef

V22 düşüş riskini *çok erken* görüyor: altın 22 Ocak 2026 V22 uyarısından 29 Ocak'taki tarihi zirveye kadar ciddi biçimde yükseldi. Uyarı = SAT varsayımı bu kazancı gereksiz biçimde kaçırabilir. Risk tahmini ile **çıkış eylemini ayırmak**, işlem maliyeti (alım %0,8 + satım %0,8) ve yeniden alım maliyeti dâhil *net serveti* ölçmek gerekir.

Çözüm: **RISK WATCH → TURNING-POINT CONFIRMATION → EXIT → HYSTERETIC RE-ENTRY**, V22 uyarısı tek başına satış yapmaz. Gözlenen fiyatın uyarıdan beri ulaştığı zirveden **en az %3** aşağı inmesi ve altının **4 saatlik tamamlanmış fiyat hareketinde en az %1** düşüş oluşması durumunda çıkış **sonraki 15 dakikalık gözlem kapanış fiyatıyla** taklit edilir. İkinci aşama: pozisyonu yalnızca V22'nin sönmesi, en az üç gün geçmiş olması, 4 saatlik pozitif momentum, fiyatın kısa dönem EMA üzerinde ve önceki **24 saatlik maksimum** fiyatın üzerinde olması koşuluyla yeniden aç.

Bu işlem algoritması orijinal V22, ANN, BASE14/CFTC21 veya Neon verilerini **DEĞİŞTİRMEDİ**. Yalnız ayrı tarihsel RESEARCH çalışmasıdır.

## Parametre seçimi ve veri kapsaması

- Kaynak: `public.gold_research_histdata_xau15m_candidate`; 2024, 2025 ve 2026 Eylül sonuna kadar 15 dakikalık gerçek arşiv, **non-canonical**, ilk yayın kanıtı eksik.
- V22 günlük veri: `outputs/v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv` tarihsel işaretleri. V22 D günü oluştuysa D kapanana kadar **kullanılmaz**; ilk sonraki UTC fiyat gününde WATCH başlayabilir. V22 orijinal modelinde işleyiş saati ve tarihi gerçek anlamda firstprint doğrulanmamış.
- 2024–2025'te aynı V22 uyarı günlüğü bulunmadığı için **gerçek V22 yerine sentetik volatilite/düşüş uyarısı** kondu: 5 işlem gününde %2 fiyat düşüşü veya o gün 4 saatte ≥%1,6 düşüş. Bu açık bir *domain shift* sınırıdır.
- V41'de farklı çıkış koşulları 2025 kullanılarak seçildi. Seçilen çıkış: zirveden **%3** + 4 saat düşüş **%1**. 2026 parametre seçimine katılmadı.
- V42'de 11 farklı yeniden giriş koşulu **sadece 2025 proxy** üzerinde seçildi: **24 saatlik fiyat rekoru kırılımı**, kısa EMA üstü, son 4s > +%0,25, son V22 uyarısı üzerinden 6 takvim gününden fazla ve son satıştan 3+ takvim gün.
- 2026 hem geçmiş deneylerde incelenmiş olduğundan **kör holdout değildir**, hem de eski veriler sonradan alındığı için gerçek işlem önerisi değildir.

## Maliye sonu net fiyat sonuçları (yıllar bağımsız, her birinde 100 USD başlangıç)

**2026 1 Ocak–1 Ekim sabahı** (tam Ekim değil), başlangıç ilk HistData barı ≈4.330,62 USD/ons.

| Strateji | 2026 net son USD | Net getiri | Max DD |
|---|---:|---:|---:|
| V22 sonrası hemen sat + aynı yeniden giriş kuralları (V41) | **78,2078** | **−%21,79** | **−%30,84** |
| Altını tut (işlem yapma) | **94,3972** | **−%5,60** | **−%29,15** |
| **V42** (2025 seçilmiş exit + 2025 seçilmiş histerezis) | **113,5604** | **+%13,56** | **−%10,54** |

V42: 2026 dönemi **2 satış, 1 tekrar alım** (ilk alım dâhil toplam 4 ücretli pozisyon işlemi), araştırma tahmini toplam ücret USD 3,60; önceki V41 agresif yeniden girişli kuralın 8 satış/8 alım ve 13,21 USD ücretine kıyasla çok daha az churn.

**Aynı 2026 kuralını 2024 ve 2025 sentetik WATCH altında kullanınca:**

| Yıl | V42 | Pasif altın | V42 farkı |
|---|---:|---:|---:|
| 2024 | 108,45 $ | 125,0162 $ | **−16,57 $** |
| 2025 | 140,5948 $ | 161,9234 $ | **−21,33 $** |
| 2026 | 113,5604 $ | 94,3972 $ | **+19,16 $** |

Kritik dürüstlük: **2024–2025 yükseliş piyasa yıllarında V42 pasifi geçemedi.** Bu nedenle evrensel üstünlük kanıtlanmadı; 2026 düşüş penceresindeki özel iyileşmedir. 2024–2025 sentetik uyarı V22 değil; birebir 3 yıllık aynı sinyal kıyası da değildir.

## 2026 işlem kanıtı

| Gerçekleşme varsayımı | UTC | Fiyat |
|---|---|---:|
| V22 ilk erken uyarı | 22 Ocak | V22 günlük |
| V22 anında SAT benchmarkı | 23 Ocak 00.15 | 4.951,885 $ |
| **V42 SAT** | **29 Ocak 15.15** | **5.188,798 $** |
| V42 tekrar AL | 10 Mart 08.45 | 5.183,075 $ |
| V42 ikinci SAT | 12 Mart 20.30 | 5.072,195 $ |
| Dönem sonunda | 1 Ekim 04.45 | 4.153,93 $ (V42 nakit) |

22 Ocak uyarısı doğrudan satılmadığı için V42 çıkış fiyatı, hemen satış benchmarkının 23 Ocak 00.15 fiyatına göre **yaklaşık %4,8 daha yüksek** (ilk satış için). Ancak 29 Ocak fiyatı gün içi zirvenin de önemli ölçüde altındadır: tepeyi gerçek zamanda bilmek beklenmez.

**İlk satış sonrası piyasa riski (yalnız ex-post kontrol):** 29 Ocak 15.15 fiyatına kıyasla sonraki 5 işlem gününde altının dip 15-dk kapanışı **−%14,21** oldu. 12 Mart satışının ardından 5 işlem günlük dip kapanışı **−%10,53**, 10 işlem günlük dip kapanışı **−%18,58**. Bu fiilî satış teyidinin yalnız olay özelindeki başarısını gösterir; geleceğe aktarım garantisi değildir.

## Ek fiyat gecikmesi ve maliyet stres testi

**İşlem tarihlerini ve üç orijinal işaretin sırasını sabit tutarak** her üç fill için +0.15 / +1 gün gecikmiş ilk uygun 15-dk fiyatı ile fiyatlandırma tekrar yapıldı. Bu, gecikmiş kararın tüm durum makinesini yeniden çalıştıran tam backtest değil; **sabit sinyal zamanlı duyarlılık testi**.

| Ek gecikme, sabit işlem listesi | Orijinal %0,8/%0,8 | Ek %0,5 alış ve %0,5 satış maliyeti | Ek %1 alış ve %1 satış |
|---|---:|---:|---:|
| 0 dk | 113,561 | 111,312 | 109,107 |
| +15 dk | 112,121 | 109,901 | 107,724 |
| +1 gün | 109,272 | 107,108 | 104,987 |

Testte fiyat bazlı 0 dk +%0,5 maliyet duyarlılığı pasif altına göre pozitif kalsa da **gerçek bid/ask, banka spread, emir saati ve likidite garanti değildir.**

## Bilimsel değerlendirme

1. **V42 araştırma bulgusu**: aynı 2026 15m penceresinde V22 erken riskinin ayrı WATCH olarak tutulması, aşırı erken satışa göre ciddi iyileşme üretmiştir. 2026'da pasifi de geçmiştir; özel bir tarihsel replay sonucu.
2. **En önemli ekonomik unsur** yeniden giriş disiplinidir. V41'de 2025 seçilmiş çıkış eşiği ve agresif geri giriş 2026'da 80,9907 USD'ye inerken, V42 histerezisi **113,5604 USD** elde etti. Yani yön tahmininde ek mucize yok: gereksiz komisyon/yeniden giriş ve riskin süresini yönetmek kazandırdı.
3. 2024–2025 pasife karşı zayıf olduğu için *boğa piyasasında* koşulsuz önerilmez. 2024–2025 uyarı proxy metodolojik kusurdur; gerçek V22 akışının 2024–2025 için nasıl olacağını göstermiyor.
4. **Tam bağımsız test yok:** 2026 dönemi ve olayları zaten önceki araştırmada incelendi, parametreler dolaylı araştırmacı etkisine açık; tüm kod tarihsel fiyatları sonradan okuyor. Sistem 2026'da gerçekten o saatte satmış gibi iddia edilmez.
5. **Mikroyapı sorunu:** Alım/satım fiyatı next-bar *close* kabul edildi, broker bid/ask karşılığı değildir. Sigorta, vergi, ek spread, fiyat atlama ve emir reddi modellenmedi.
6. **Dört metal bağlamı:** Bu sürüm XAU15m fiyat + V22 risk uyarısını *çıkışa* çevirir. StakTrakr 2026 dört metal saatlik teyidi bu kuralın çıkış koşuluna eklenmedi; model çıktısını dört-metal 5/5 olay kapsamasıyla karıştırmayın.
7. **Karar:** V22'ye veya otomatik al-sat algoritmasına **yayın yok**. İlk yayın tarihleri doğrulanmış ileriye dönük shadow-mode watch/exit/entry journal ve boğa, yatay, düşüş rejimlerindeki risk-ayarlı getiri ve işlem maliyeti gerektiğinde canlılaştırılabilir.

## Tekrar üretim

- `risk_v41_v22_watch_sequential_exit_costs.py` ve `test_risk_v41_v22_watch_sequential_exit_costs.py`: 2025 çıkış kalibrasyonu + 2026 ilk replay; 8/8 test.
- `risk_v42_cost_aware_reentry_hysteresis.py` ve `test_risk_v42_cost_aware_reentry_hysteresis.py`: 2025 geriye giriş koşulu + 2026 replay; **14/14 otomatik test başarı**.
- V41 Actions: <https://github.com/ataullahturgut/sim3-automation/actions/runs/41117544878>
- V42 Actions: <https://github.com/ataullahturgut/sim3-automation/actions/runs/41117900367>
- V42 JSON artifact: <https://github.com/ataullahturgut/sim3-automation/actions/runs/41117900367/artifacts/13007101444>

**Hepsi Neon salt-okunur sorgu; model üretimine geçiş yok.**
