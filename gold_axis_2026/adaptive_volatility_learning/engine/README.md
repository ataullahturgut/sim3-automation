# Adaptif OLAY–ÖĞREN–ÖRÜNTÜ motoru — araştırma sürümü

**Yetki/sınır:** ANA-01, OLAY-02 ve ÖĞREN-03 dosyaları değiştirilmez. Bu klasör
tarihsiz araştırma kodudur; yeni bir ana manifest değildir. Eski Ocak 2026
deney günlükleri yeniden oluşturulmaz. Emir gönderme özelliği YOKTUR.

## İçerik

- `adaptive_olay.py`: standart Python 3.10+ ile iki komut.
- `test_adaptive_olay.py`: future-news, timezone, eksik M15, etiket olgunlaşma testleri.
- `export_m15.sql`: Neon'dan salt-okunur kronolojik altın bar çıktısı.
- `events_template.csv`: kanıtlı ilk yayımlanma ve teknik erişilebilirlik damgası.
- `RETROSPECTIVE_MACRO_AUDIT_2025.json`: önden dondurulmuş ve adaptif
  2025 makro proxy denetimi (istatistikler, sınırlamalar).

## 1. Makro ön denetimi (elimizdeki gerçek dosyayla hemen çalışır)

Depo kökünden:

```sh
python gold_axis_2026/adaptive_volatility_learning/engine/adaptive_olay.py macro-audit \
  --study gold_axis_2026/GOLD_2023_2025_CPI_NFP_FOMC_M15_RELEASE_WEEKMATCH_EVENTSTUDY_20261014.csv \
  --year 2025 --mode frozen --horizon 60
python gold_axis_2026/adaptive_volatility_learning/engine/adaptive_olay.py macro-audit \
  --study gold_axis_2026/GOLD_2023_2025_CPI_NFP_FOMC_M15_RELEASE_WEEKMATCH_EVENTSTUDY_20261014.csv \
  --year 2025 --mode prequential --horizon 240
```

Sadece `arm_week_lag=0` gerçek duyurular, `overlap_other_macro_release=false`,
CPI/NFP ve sıfır olmayan manşet sürprizi kullanılır. FOMC daha ayrıntılı Fed
söylemi/SEP olmadan yanlış işaretlenebileceğinden dışarıdadır. Negatif sürpriz
`ORG01`, pozitif sürpriz `ORG02` **araştırma adayıdır**; bu dönüşüm
özellikle NFP ücret/işsizlik, CPI bileşim ve revizyonlarını içermediği için
**nedensel atama değildir**.

Her bir 2025 olayının olasılığı sadece önceki gerçek açıklamalar ve
**önceden tamamlanmış 60/240 dakikalık** getirilerle hesaplanır. Grup verisi
yetersizse (`n_group<8` veya `n_total<20`) belirsiz bırakılır. Önsel,
mevcut geçmişteki genel UP oranına 4 sözde gözlem ağırlığıyla çekilir.
`frozen`: 2023–2024 bilgisi 2025 boyunca sabit. `prequential`: 2025
içinde olgunlaşmış olaylar sonraki olayları günceller.

**2025 bulgusu, 18 uygun duyuru:**
- 60dk frozen **13/18**, karşılaştırma **10/18**; Brier **0,199769** vs **0,247058**.
- 60dk prequential **13/18**, karşılaştırma **10/18**; Brier **0,207850** vs **0,252467**.
- 240dk frozen **11/18**, karşılaştırma **10/18**; Brier **0,235022** vs **0,247139**.
- 240dk prequential **11/18**, karşılaştırma **10/18**; Brier **0,245003** vs **0,252576**.

**ÖNEMLİ:** makro actual/consensus alanları geriye dönük veri derlemesidir;
gerçek zamanlı sürüm (PIT), haberin kullanıcıya ilk erişimi, tüm NFP
bileşenleri ve DXY/faiz reaksiyonu doğrulanmış değildir. Önceki araştırmalarda
2025 de görülmüş olduğundan bu test gerçek kör OOS sayılmaz. İşlem
sinyali, yıllık getiri veya kâr başarısı olarak sunulmaz.

## 2. M15 durum geçişi ve olay katmanı

```sh
psql "$DATABASE_URL" -f \
  gold_axis_2026/adaptive_volatility_learning/engine/export_m15.sql > xau_m15.csv
cp gold_axis_2026/adaptive_volatility_learning/engine/events_template.csv events.csv
# events.csv'ye kaynaklı, yayımlanma ve erişilebilirlik UTC bilgisi ekleyin.
python gold_axis_2026/adaptive_volatility_learning/engine/adaptive_olay.py walk \
  --bars xau_m15.csv --events events.csv \
  --study gold_axis_2026/GOLD_2023_2025_CPI_NFP_FOMC_M15_RELEASE_WEEKMATCH_EVENTSTUDY_20261014.csv \
  --start 2026-01-01T00:00:00+03:00 --stop 2026-01-31T23:59:59+03:00 \
  --out research_walk.jsonl
```

`events.csv` bir **ilk-yayım ve bilgi-erişilebilirlik sözleşmesidir**:
`event_id,firstprint_utc,available_at_utc,firstprint_status,org_candidates,kind,macro_surprise`.
Sadece `firstprint_status=VERIFIED` haber grubu adayları kullanılabilir.
`available_at_utc >= firstprint_utc`; haberin yayımlandığı tarihi bilmek,
tam erişilebilirlik saatini bildiğimiz anlamına gelmez. Eksik haber satırı
zorla eşleştirilmez. `org_candidates` 'ORG01|ORG02' biçiminde olabilir.
Haberin kaynağı ayrıca OLAY-02'de saklanmalıdır.

Her kapanmış tam M15'te son **17 ardışık bar** üzerinden:
- 1s ve 4s getiri, RV4h, yönsel yol verimi, aşağı yönlü oynaklık payı;
- açıklayıcı `CHOP / UP_FLOW / DOWN_FLOW / HIGH_VOL / MIXED` durumları;
- ilk-yayımı doğrulanmış 72 saat içindeki rakip ORG adayları;
- geçmişteki **birbirinin üzerine binmeyen dört saatlik ankrajlar** üzerinden
  yalnız olgunlaşmış ileri 4s sonuçlarla betimsel koşullu olasılık;
- gözlenmiş durum geçişleri ve açık `UNKNOWN`/yetersiz kanıt statüleri.

Durum eşikleri **deneysel sabit eşiklerdir**, optimize edilmiş veya
istatistiksel olarak doğrulanmış bir hidden-state modeli değildir.
Dört saatlik durum dağılımı için en az 40 olgunlaşmış toplam blok ve
aynı durumdan 12 blok gerekir; yoksa `p_up_next_4h=null`.
Arka arkaya 15 dakikalık kontrol anları birbirinden bağımsız etiket
olarak kullanılmaz.

`--start` çıktı başlangıcını sınırlar; **öğrenme geçmişini kesmez**.
Bu nedenle 2023'ten başlayan barları dışarı aktarmak, yalnız Ocak'ı
aktarmaktan daha sağlıklı bir başlangıçtır.

## 3. Test, güvenlik, başarısızlık kipleri

```sh
cd gold_axis_2026/adaptive_volatility_learning/engine
python -m unittest -v test_adaptive_olay.py
```

- Bütün tarih/saatler UTC offset'i içerir, Türkiye saati kıyaslaması
  UTC'ye çevrilir. Timestamp çıkarılan veya ileri doldurulan haber yok.
- `bar_start + 15m` öncesinde M15 kapanışı kullanılamaz. Eksik bar
  `MISSING` olur; hafta sonu sahte durgunluk sayılmaz.
- Forward outcome yalnız gerçekten sona erdiğinde öğrenilir;
  ileri fiyat haber/açıklama anına geri taşınamaz.
- USD, 2Y/10Y, reel faiz, ETF/CFTC, gerçek banka ASK/BID ve emir
  gecikmesi doğrulanana kadar mekanizma ataması **aday**, işlem **KAPALI**.
- 20 eski V2 derin vakanın güncel C_CORR eşleşmesi güvensizdir;
  modele kesin etiket olarak alınmaz.
- Fiyat durumundan oluşan ilişki, ekonomik nedensellik **değildir**.

## 4. İlk Ocak 2026 fiyat-katmanı incelemesinin uyarısı

Salt Neon altın M15 üzerinde 29 Aralık 2025 başlangıçlı kronolojik
betimsel yürüyüşte **34 yeterli geçmişli dört saatlik blok tahmini** elde
edildi: **18/34** doğru yön, Brier **0,266**. Aynı bloklarda temel oran
karşılaştırması da **18/34**, Brier **0,255** oldu. Yani saf fiyat durum
katmanının üstünlüğü **gösterilemedi**. Bu sayılar 2026 Ocak dosyalarından
kopyalanmış eski deneyler değildir; bu prototipin iç denetim özetidir.
Haberli adaptif birleşim henüz bağımsız şekilde doğrulanmadı.

**Bir sonraki bilimsel kapı:** haberlerin gerçek available-at bilgisi ve
makro bileşenleri, DXY/yield ve diğer metaller, negatif kontrol günleri,
epi-zot düzeyinde geçmiş-vaka ayrıştırma, kalibrasyon ve 2026 sonrası
bağımsız test. Bunlar bitmeden `AL / SAT` üretilmez.
