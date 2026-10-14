# CLAUDE_INDEPENDENT — XAU/USD orta/büyük hareket karar protokolü (PREREG)

**Tarih:** 2026-10-14 · **Yazar:** Claude (bağımsız denetçi) · **Dal:** `research-gold-claude-independent-audit-20261014` (kaynak HEAD `7a402e6`)
**Statü:** `PREREG_WRITTEN_BEFORE_ANY_DECISION_RUN` · RESEARCH ONLY · NO LIVE TRADING · NO PROMOTION

## 0. Hindsight beyanı (dürüstlük kaydı)

Bu protokolü yazarken üç vakanın **ex-post** büyüklüklerini biliyorum (kullanıcı metni ve depo atlası: 5–13 Ocak +%5,19 UP; 26–31 Ocak −%2,35 DOWN; 1–24 Şubat −%7,15 DOWN; 3 Şubat NFP +517k ilk 15dk XAU −%1,349). Ayrıca ChatGPT'nin 4 Ocak 10:20 TRT AL kaydını okudum. Bu nedenle 2023 vakaları **kör test değildir**. Bunu azaltmak için:

1. Karar kuralları ve parametreler aşağıda **2023 fiyat yolu sorgulanmadan** sabitlendi.
2. Kural varyantları arasında seçim **yalnız 2020-01-01 → 2022-12-31 geliştirme döneminde** (EV/Dukascopy M15 + 2020–2022 NFP/CPI/FOMC ilk yayımları) yapılır; 2023 sonuçları seçimi etkileyemez.
3. Seçilmeyen varyantların 2023 sonuçları da raporlanır (seçim yanlılığını görünür kılmak için).
4. 2023 sonucuna bakıp parametre değiştirirsem bu, **yeni sürüm (v2) ve yeni geliştirme vakası** olarak ayrı kaydedilir; v1 sonuçlarının üzerine yazılmaz.

## 1. Veri ve saat sözleşmesi

| Kaynak | Kullanım | Saat semantiği |
|---|---|---|
| Neon `gold_research_evduka_xau15m_bidask_candidate` (EV/Dukascopy türevi, non-PIT) | Ana XAU 15dk BID/ASK; MID=(bid+ask)/2 | `bar_start_utc` başlangıç; bar **start+15dk**'da karar girdisi olur |
| Neon `xau_intraday_research_cache_1m` (yalnız close, MID) | 2023 icra teyidi ve fill vekili | `observation_ts` başlangıç (doğrulandı: M1 close@start+14 ≡ M15 close, ort. mutlak fark 0,047$); dakika **start+1dk**'da kullanılabilir |
| Depo `GOLD_DATABENTO_GLBX_OHLCV1H_N_RAW_2022_2024.csv.gz` (`.n.0` açık pozisyon önceliği) | ZN/GC/SI/NQ/CL tanısal çapraz teyit (kurala girmez) | `ts_event` saatlik bar başlangıcı; start+60dk kullanılabilir |
| Neon `observations` MACRO_* (NFP, AHE, UNEMP, CPI ilk yayım + Investing konsensüs; FOMC USMPD path) | Makro sürpriz sınıfı | Açıklama anında (`event_ts`) kullanılabilir; FOMC path faktörü **+30dk** sonra kullanılabilir varsayılır |
| **MISSING** | DXY, 2Y/10Y getiri, TIPS, VIX/GVZ (2023), ETF/COT gün içi | FRED kabuk erişimi politika engeli, WebFetch HTTP 429. Kurala girmez. |

* Türkiye saati = UTC+3 (2023'te sabit). NY17 seansı: `date((bar_start+15dk) @ America/New_York + 7s − 1µs)` (17:00 ET biten bar önceki seansa).
* **Banka icra penceresi (birincil varsayım):** hafta içi 09:00–17:00 TRT = 06:00–14:00 UTC. Pencere dışı sinyal kuyruğa alınır, açılışta yeniden geçerlilik kontrolü yapılır. Duyarlılık: 7/24 (piyasa açıkken) icra.
* **Maliyet:** AL ve SAT başına %0,8 komisyon; AL ASK'tan, SAT BID'den. 2023'te M1 yalnız MID olduğu için fill = M1 MID ± (son tamamlanmış M15 BID/ASK makası)/2 → `PROXY_FILL`. Gerçek Türk banka kotasyonu DEĞİL.

## 2. Özellikler (her M15 bar kapanışında, yalnız tamamlanmış barlar)

* `σ15`: son 1.920 M15 log getirisinin std'si (yalnız ardışık 15dk barlar; hafta sonu/boşluk getirileri hariç).
* `r4 = ln(P_t/P_{t−16 bar})`, `r12 = ln(P_t/P_{t−48 bar})` (işlem-zamanı); `z4 = r4/(σ15·4)`, `z12 = r12/(σ15·√48)`.
* Günlük rejim (son tamamlanmış NY17 seans kapanışı S): `trend20 = C_S/SMA20_S − 1`, `mom10 = C_S/C_{S−10} − 1`. `REG=UP` iki pozitif, `DOWN` iki negatif, aksi `NEUTRAL`.
* Makro sınıfı (NFP+AHE+UNEMP aynı saat tek olay; CPI; FOMC): sürpriz bileşen işaretleri altın-yönüne çevrilir (NFP↑, AHE↑, UNEMP↓, CPI↑, FOMC path↑ ⇒ altın için **hawkish/−**). Açıklamadan sonraki ilk **60 dk** içinde, açıklama öncesi son tamamlanmış M15 MID'e göre XAU hareketi ≥ **+%0,40** ve en az bir bileşen dovish ise `MACRO_UP`; ≤ **−%0,40** ve en az bir bileşen hawkish ise `MACRO_DOWN`. Sinyal, eşiğin ilk aşıldığı M15 kapanışında oluşur (en geç release+60dk).

## 3. Olay evresi etiketleri

* `ONSET_UP`: z12 ≥ +2,0 (yeniden silahlanma: önceki ONSET_UP'tan sonra z12 < +1,0 görülmüş olmalı). `ONSET_DOWN` simetrik.
* `REG_FLIP_UP / REG_FLIP_DOWN`: seans kapanışında REG yeni UP/DOWN olduğunda.
* Aşama raporu (kural dışı, tanısal): `PRE_ONSET` (|z12|<1), `ONSET`, `CONTINUATION` (aynı yönde REG ve |z12|≥1), `EXHAUSTION` (aynı yönde REG fakat z4 ters işaretli ≥1), `REVERSAL` (REG ile z12 ters ≥2), `UNCERTAIN`.

## 4. Kural varyantları (hepsi önceden sabit)

| Varyant | NAKİT → AL | ALTIN → SAT |
|---|---|---|
| **V-A FULL** | `MACRO_UP` (her rejim) **veya** `ONSET_UP` ∧ REG≠DOWN **veya** `REG_FLIP_UP` | `MACRO_DOWN` (her rejim) **veya** `ONSET_DOWN` ∧ REG≠UP **veya** `REG_FLIP_DOWN` |
| **V-B MACRO+REGIME** | `MACRO_UP` veya `REG_FLIP_UP` | `MACRO_DOWN` veya `REG_FLIP_DOWN` |
| **V-C REGIME ONLY** | `REG_FLIP_UP` | `REG_FLIP_DOWN` |

Ek kurallar (tüm varyantlar): pozisyon tam (100% altın / 100% nakit), kaldıraç yok. Kuyruktaki sinyal, pencere açılışında aynı yöndeki sinyalin geçersizleşmediğini (AL için MID ≥ sinyal MID −%0,5; SAT için ≤ +%0,5) kontrol eder; aksi halde düşer.

**2023 1dk icra kapısı (geliştirme döneminde M1 yok, bu yüzden yalnız 2023 testinde):** karar anındaki son tamamlanmış M1 MID, tetikleyen M15 MID'in AL için −%0,15'inden düşük **veya** +%0,30'undan yüksekse (geri alma / sıçrama kovalama) icra ertelenir; sonraki 15 dakika boyunca her dakika yeniden bakılır; geçemezse sinyal sonraki M15 kontrolüne kalır (en fazla 4 kontrol). SAT simetrik. Fill = kapının geçtiği dakikanın **sonraki** M1 kapanışı (1 dk gecikme).

## 5. Seçim ölçütü (yalnız 2020–2022)

Her varyant 2020-01-02 → 2022-12-30 sürekli 100$ ile çalıştırılır (icra: sinyalden sonraki ilk pencere-içi M15 barın BID/ASK açılışı). Seçim: **net NAV / maksimum düşüş** oranı en yüksek ve net NAV > maliyetli pasif-altın **veya** > nakit olan varyant. Hiçbiri nakit 100$'ı geçemezse sonuç `NO_VARIANT_PASSES_DEV`; 2023'e yine V-A/V-B/V-C tanısal olarak uygulanır, fakat “seçilmiş strateji” denmez.

## 6. 2023 vakaları ve raporlama

* **A1:** 2023-01-03 00:00 UTC'de 100$ nakit, 3–16 Ocak; **A2:** 4 Ocak 07:21 UTC 0,05358252 ons devralınmış (ChatGPT ortak başlangıç) ile 4–16 Ocak. **C:** 26–31 Ocak (sürekli koşu ve 26 Ocak altın-başlangıç varyantı). **B:** 30 Ocak–28 Şubat (sürekli koşu ve 30 Ocak altın-başlangıç varyantı).
* Benchmark: maliyetli pasif altın (başlangıçta ASK+%0,8, sonda BID−%0,8) ve nakit.
* Her işlem: TRT/UTC saat, sinyal sınıfı, son erişilebilir veri zamanı, fill kaynağı, ons, komisyon; açık pozisyonda BID işaretli değer ve “şimdi satılsa” net değer ayrı.
* Kanıt seviyesi L0–L4; 2023 için en fazla **L2–L3** (L4 ancak dokunulmamış ileri dönemde).

## 6A. v1 geliştirme sonucu ve v2 ön kaydı (2023 koşusundan ÖNCE yazıldı)

**v1 dev 2020-01-02→2022-12-31 (100$, banka penceresi, %0,8+%0,8):** V-A net 59,27$ (39 AL/38 SAT, ücret 49,98$, maxDD −%50,6); V-B 65,40$ (36/35, 49,69$, −%50,0); V-C 72,84$ (27/26, 37,13$, −%44,8). Nakit 100$, maliyetli pasif altın 118,02$. **Hüküm: `NO_VARIANT_PASSES_DEV`.** Teşhis: işlem devir hızı (yılda ~9 tam tur × ~%1,62) maliyeti yapısal olarak karşılayamıyor; 15dk/z-şok ve 20 seanslık rejim dönüşleri bu maliyet yapısında aşırı sık.

**v2 ailesi (yalnız dev'de seçilecek; 2023 hiçbir v1/v2 koşusu henüz görülmedi):** Histerezisli yavaş rejim. `UP` durumu C_S > SMA_L·(1+h), `DOWN` durumu C_S < SMA_L·(1−h); bant içinde önceki durum korunur. AL = durum DOWN/yok → UP geçişi; SAT = UP → DOWN geçişi. Izgara: L ∈ {20, 50} seans, h ∈ {%1, %2, %3} → 6 yapılandırma. Makro ve 15dk şok sinyalleri v2'de **işlem tetiklemez**; 15dk/1dk katman yalnız icra kalitesi ve olay evresi kaydı içindir.
Seçim kuralı: dev'de nakdi geçen yapılandırmalar arasında net/|maxDD| en yüksek olan. Hiçbiri nakdi geçemezse `V2_NO_PASS` ve 2023'te yalnız tanısal raporlanır.

### v2 dev sonucu (2023 koşusundan ÖNCE)

| Yapılandırma | AL/SAT | Ücret $ | Net (satılsa) $ | maxDD | 2020 / 2021 / 2022 |
|---|---|---:|---:|---:|---|
| L20_H1 | 19/18 | 26,86 | 78,24 | −%36,7 | −5,7 / −9,1 / −7,9 |
| L20_H2 | 13/12 | 18,91 | 82,93 | −%32,2 | +3,0 / −15,2 / −4,3 |
| L20_H3 | 7/6 | 9,70 | 87,76 | −%28,4 | +2,9 / −13,8 / −0,3 |
| L50_H1 | 10/9 | 14,87 | 96,19 | −%23,4 | +2,6 / −9,8 / +4,8 |
| **L50_H2** | 6/5 | 8,67 | **103,05** | −%21,9 | +6,5 / −10,9 / +9,4 |
| L50_H3 | 5/4 | 7,25 | 97,12 | −%25,7 | +9,6 / −13,7 / +3,6 |

Nakit 100$, maliyetli pasif altın 118,02$. **Seçilen: L50_H2** (nakdi geçen tek yapılandırma). Uyarı: pasif altının 15 $ gerisinde ve komşu yapılandırmalar 96–97$ → seçim **kırılgan**; 2023 testinde başarılı çıksa bile genelleştirilebilir üstünlük iddiası yapılmaz.

**Hesap başlangıcı yorumu (2023'ten önce sabitlendi):** Birincil = protokol metnindeki gibi yalnız **durum geçişinde** işlem (A1 nakitle başlarken mevcut UP durumu AL üretmez). İkincil/tanısal = hesabın ilk pencere fırsatında mevcut duruma uyması (“state-follow”). Birincil sonuç değiştirilmeyecek.

## 7. Yasaklar

Geleceği görerek dip/tepe seçimi; açıklama öncesi sürpriz kullanımı; BIST/Türkiye hisse verisi; ham Neon fiyatlarının depoya yüklenmesi (yalnız türetilmiş karar/özet); ChatGPT kararlarının kopyalanması.
