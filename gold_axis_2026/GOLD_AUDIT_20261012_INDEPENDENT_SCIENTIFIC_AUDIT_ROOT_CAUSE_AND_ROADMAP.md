# Altın Araştırması — Bağımsız Bilimsel Denetim, Kök Neden Analizi ve Yeni Araştırma Yol Haritası

**Tarih:** 2026-10-12
**Hazırlayan:** Claude Code (bağımsız denetçi rolü)
**İncelenen durum:**
- `gold-execution-channel-audit-20261006` @ `7c154800`
- açık PR #83 (`r73-ovn1645-xmkt-residual-reversal` @ `e63fe2b2`)

**Kapsam ve yöntem:**
- Yeni model eğitilmedi; mevcut dosya, tablo veya manifest değiştirilmedi.
- Bu rapordaki tek yeni hesap, **piyasa verisi kullanmayan** bir sıfır-bilgi simülasyonudur. Betik: `gold_axis_2026/tools/gold_audit_20261012_label_structure_null_sim.py`, sabit tohumlu ve yeniden üretilebilir.
- Kritik iddialar kod satırına veya sonuç dosyasına bağlanmıştır.
- Kanıt sınıfları:
  - **[KANITLI]** — kod veya sonuç dosyasında doğrulandı.
  - **[KUVVETLİ ŞÜPHE]** — matematiksel/simülasyon kanıtı var, gerçek veri ölçümü yok.
  - **[İNCELENMEMİŞ]** — olasılık; kanıt yok.

---

## 0. Yönetici özeti (tek paragraf)

Projede "başarılı" sayılan sonuçların hepsi aynı yapısal dar boğazı paylaşıyor. Bu dar boğaz piyasa öngörülebilirliği değil, **etiket inşası**dır:
- aylık ChHHO / DE-ABC yönü: 23/33 ≈ %70 ve 25/33 ≈ %76;
- H3 ailesi: %63–71;
- CIG-D1: %74,4 / %80,7.

Bu modellerin hedefleri ya bir **ortalama** fiyatı (aylık ortalama, UTC gün ortalaması) ya da karar anından **önce basılmış** bir referans fiyatı (LBMA AM) kullanıyor. Özellikler ise o referanstan **sonra** gerçekleşen fiyat hareketini görebiliyor. Sıfır öngörülebilirlikli rastgele yürüyüşte, yalnızca bu yapı şunları üretiyor:
- aylık hedefte **%73,8**;
- H3'te **%58,5–69,3**;
- CIG etiketinde **%73,8** yön "başarısı".

Bu sayılar raporlanan başarılarla aynı bantta. Ekip bunun bir kısmını CIG ve H3 için zaten bulmuştu (R37, R38, R43). Bu raporun yeni katkısı şunlar:
1. Aynı mekanizmanın **aylık programın kendisinde** de bulunduğunu kodda göstermek: hedef `log(Ort[ay+1]/Ort[ay])`, VW özelliği ile bilinen kısım arasında ρ = 0,993, RW tabanı önceki ay ortalaması.
2. Mekanizmayı **tek bir kök neden** olarak birleştirmek.
3. Bundan çıkan araştırma yolunu sırayla önermek.

Gerçek, karar sonrası (işlem yapılabilir) pencerelerde ölçülen yön doğrulukları tutarlı biçimde **%47–56** aralığında ve çoğu zaman "hep UP" tabanının altında. Bu, sistemsel bir bulgudur, tekil başarısızlık değil.

Bir sonraki gerçek iyileştirme için önerim:
1. **İlk iş:** bu yapay başarıyı nicelleştiren ucuz, kesin bir "bilinen-kısım tabanı" denetimi (E1).
2. **Ardından:** ortak bir oynaklık tahmini (σ̂) üzerine kurulu iki test: oynaklık dinamiği üzerinden koşullu yön (E2) ve **büyüklük, maliyet eşiği ve işlem-yapmama** kararı (E3).
3. **Hemen, paralel:** zaman damgalı ileriye dönük test ve **banka BID/ASK kaydı** (E5).

---

## A. BUGÜNE KADAR NE YAPTIK?

### A.1 Problem ayrıştırması: hedef, karar saati, veri kesimi, gerçekleşen değer

| # | Problem | Gerçek hedef (kodda/belgede) | Karar / yayım saati | Özellik kesimi | Gerçekleşen değer kaynağı | Geliştirme / test |
|---|---|---|---|---|---|---|
| 1 | Aylık fiyat (ChHHO-ANFIS vb.) | `y = log(M[hedef]/M[köken])`; M = **aylık ortalama** fiyat (`tools/vw_midas_msvr_successor_v1.py:192`) | Köken ayın sonu | Köken ay sonu; VW = köken ay içi günlük getirilerin üstel (sona ağırlıklı) ortalaması (`:177-182`) | CORE5 / World Bank aylık ortalama | DEV 2022-04..2024-12 (n=33); 2025–26 açılmış |
| 2 | H3 (3 gözlem) yön | `log(P[t+3]/P[t])`; P = StakTrakr günlük **referans**: 2023–25 LBMA AM (R37), 2026 karışık; Mart–Temmuz `sqld` UTC gün **ortalaması** (R34B) | `forecast_issue_date` (t+1), yönetişim sınırı 08:00 NY ≈ 15/16 TR | IRIS: Twelve Data 1s, **t gününde 16:00 NY'ye kadar** | StakTrakr (birden çok sağlayıcı) | Ön-2025 seçim; 2025–26 retrospektif (`GOLD_SHORT_HORIZON_GLOBAL_XAU_PROJECT_MANIFEST.md` §2, §4) |
| 3 | Günlük yön (CIG-D1, %74,4) | `sign(LBMA_AM(D) − LBMA_AM(D−1))`; 2026'da dört farklı kaynak birleşik | 08:00 NY (15/16 TR) | H3 uzmanlarının **D−1 16:00 NY** durumu | StakTrakr karışık | 2026 Oca–Tem 125 sinyal (retrospektif) |
| 4 | Gündüz (Türkiye) | `09:00 → 16:45/17:00 TR` XAU orta fiyat getirisi | 08:45 / 09:00 TR | Kararın önündeki M15 çubukları | EV/Dukascopy, doğrudan Dukascopy, HistData | DEV 2023–24, 2025–26 açılmış |
| 5 | Gece (Türkiye) | `16:45 (veya 17:00) → ertesi takvim günü 09:00 TR`, Cuma hariç | 16:45 / 17:00 TR | 16:00 TR (R73) veya 17:00 TR yarım saatleri (PRAMV) | Aynı kaynaklar | DEV 2023–24 |
| 6 | Rejim, reversal, momentum, risk | Yön motoru (GOLD_CONTROL R01–R57, H01–H37); H3 aşağı-kuyruk ≥%1,5 riski (R15–R24); oturum uzmanları (RIFT, VEGA, OPAL, TURN…) | Çeşitli | Çeşitli | Çeşitli | Çeşitli |
| 7 | Karar ve işlem | R68 tek-pozisyon long/flat, R70 dönen-pozisyon senaryoları; 25 bp **varsayımsal** maliyet | 09:00 / 16:45 TR | — | Banka BID/ASK **yok** | 2023–26 retrospektif |

Ayrıca bir fırsat (MFE/MAE) hattı var: Borsa İstanbul resmi günlük altın fiyatı, 5 gözlem ufku (`GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` §2, §5A–5D).
- Burada K100 güçlü yükseliş dedektörü Brier'de yalnızca **+%1,46** iyileşme sağladı.
- MAE5 (olumsuz sapma) sürekli hedefi geçti.
- Aylık bağlamı beslemek her varyantta kötüleştirdi (Stage-4).

### A.2 Kronoloji (kısa)

- **10 Eyl – 1 Eki 2026, aylık program:**
  - ELM, ANN, ANFIS, RBFNN, GPR/MOGP, Boosting, SVR, CNN/LSTM aileleri tarandı.
  - Seçilen model ChHHO-ANFIS: DEV ΣAE 1413,03, yön 23/33.
  - Ardından rejim, alarm ve kurtarma katmanları geldi (`GOLD_MONTHLY_PROJECT_MANIFEST.md` §1–§7).
- **Eylül sonu – 5 Eki, H3 programı:**
  - CORE3 Logistic → IRIS (saatlik veri, "en büyük bilgi atılımı") → AURORA/HELIOS → SAGE/RuleFlow → SELLR, BOCPD, DPTC.
  - En iyi post-hoc sonuç DPTC-Q95 135/191 = %70,68 (`GOLD_SHORT_HORIZON_GLOBAL...` §6).
- **5–6 Eki:** CIG-D1 4/4 konsensüs 93/125 = %74,4. Aynı 125 sinyal 08:15 NY sonrası %47,2 çıktı (`GOLD_CIG_EXACT_125_CLOCK_RESCORE_RESULT_2026-10-06.md`).
- **6–9 Eki, oturum / Türkiye saatleri programı:** V5 oturum hedefleri, model-model yeniden oynatma, PRAMV V1.
  - PRAMV: %34 kapsama, BA 60,6 / 60,1 / 63,4 (2023 / 2024 / 2025).
  - CME3, GC–spot boşluğu, ZN-VPT2, DeepSeek eleştirileri; tamamı **terfisiz**.
- **10–12 Eki:**
  - R10–R14: aylıktan kısa vadeye aktarım; GPR ve dört metal başarısız.
  - R15–R27: aşağı-kuyruk risk sıralaması kısmen ilerledi; işaret çözülmedi.
  - R34–R38: CIG etiket adli analizi.
  - R40–R72: H3'ün banka saatine köprülenmesi; işlem yapılabilir başarı yok.
  - R73/R73B: ZN/NQ/CL kalıntı geri dönüşü REJECT.

Ölçek: yaklaşık bir ayda **133 ön-kayıt**, **375 sonuç** dosyası, **740 araç betiği**, **~4.800 commit**.

---

## B. NEREDE TAKILDIK? (en önemli 8 sorun)

### B1. [KANITLI + genelleştirme] "Başarı", etiketin karar anında kısmen zaten bilinmesinden geliyor

Bunun üç doğrulanmış örneği var.

**(a) CIG-D1, %74,4 / 2025'te %80,73.**
- Etiket LBMA AM'den LBMA AM'ye, yayın ise 08:00 NY (R37 §3).
- Sinyaller H3 uzmanlarının D−1 16:00 NY durumu.
- R38'de, aynı 218 sinyalin isabeti, getiri aralığının başlangıcı özellik kesiminden ileri kaydırıldıkça **monoton biçimde düşüyor**:
  - 02:00 TR başlangıç: %79,8
  - 13:00 TR: %80,3
  - 16:00 TR: %72,5
  - 18:00 TR: %63,8
  - 20:00 TR: %56,9
  - 23:00 TR: **%54,6**
  - Kaynak: `GOLD_R38_20261011_H3_TO_D1_CONSENSUS_TIME_WINDOW_DECOMPOSITION_FINAL.md`, tablo satır 15–30.
- Yani kesimden önce gerçekleşmiş parça %85,8 isabetle "tahmin ediliyor"; kesimden sonraki parça %49,8–50,9.
- Bu, bilgi örtüşmesinin ders kitabı imzasıdır.

**(b) H3.**
- Hedefin başlangıç fiyatı P[t] 2023–25'te LBMA AM (~10:30 Londra); IRIS özellikleri ise t günü 16:00 NY'ye kadar gidiyor.
- Yani P[t] basıldıktan sonra yaklaşık 10 saatlik hareket özelliklerin içinde.
- R38: 08:00 NY yayınından sonra orijinal H3 bitişine kadar 120/218 = **%55,05**; hep-UP 124/218 = **%56,88**.

**(c) Aylık [YENİ BULGU — kodda KANITLI yapı, etkisi KUVVETLİ ŞÜPHE].**
- Hedef `y = log(M[target]/M[p])`; M ayın günlük fiyatlarının **ortalaması** (`tools/vw_midas_msvr_successor_v1.py:147,192`).
- Köken ay sonu.
- Rastgele yürüyüşte `Ort[ay+1] − Ort[ay]` farkı, köken anında bilinen `P_son − Ort[ay]` parçasını içerir (Working 1960 ortalama etkisi).
- Simülasyon (sıfır öngörülebilirlik, 21 işlem günü):
  - `sign(P_son − Ort[ay])` yön doğruluğu: **%73,8**.
  - Projedeki VW özelliğinin ağırlıklarıyla (λ = 0,1) kurulan özellik ile bu bilinen parça arasındaki korelasyon: **0,993**.
  - Bu özelliğin tek başına yön doğruluğu: **%73,6**.
- ChHHO 23/33 = %69,7, DE-ABC 25/33 = %75,8. İkisi de bu sıfır-bilgi bandının içinde.
- **Henüz gerçek veride ölçülmedi.** Bu nedenle E1'in ilk testi olarak öneriyorum.

**Genel ilke.** Bir ortalama veya önceden basılmış referans fiyatına göre tanımlanan etiket, karar sonrası (işlem yapılabilir) getiri değildir. Böyle etiketlerde %70'in üzerindeki başarılar beklenen sonuçtur ve öngörü gücü kanıtlamaz.

### B2. [KANITLI] Aylık "RW'yi yeniyoruz" kıyası yapısal olarak garantili

Tüm aylık araçlarda taban `rw = core_gold[p]`, yani **önceki ayın ortalaması**. Örnekler:
- `tools/vw_midas_msvr_successor_v1.py:221`
- `tools/vw_midas_estimator_headswap_v1.py:113`
- `tools/vw_midas_fmrvr_v1.py:156`

Bir ortalamanın rastgele yürüyüşte optimal tahmini ise **son gözlenen fiyat**tır. Simülasyonda "son fiyat" tahmininin MAE'si, "önceki ortalama" tahmininin **0,73 katı**: %27 "kazanç" hiçbir model olmadan geliyor.

Depoda son-fiyat tabanını raporlayan bir aylık sonuç dosyası bulamadım. Arama `last_price | P_end | end_of_month | month_last` desenleriyle yapıldı; bulunan kullanımlar yine `core_gold[p]`.

### B3. [KANITLI] Etiket serilerinde kaynak karışımı ve sağlayıcıya bağlı etiket gürültüsü

- **2026 CIG etiketleri** dört farklı sözleşmenin birleşimi: LBMA, MetalPriceAPI, StakTrakr anlık görüntüsü, `sqld` UTC gün ortalaması (R34B tablo).
  - Aynı 125 sinyal sonraki Stak sürümüne karşı %70,4 veriyor (R34B).
- **R73:** 16:45 → 09 gecelerinde EV/Dukascopy ile R67/HistData işaretleri DEV gecelerinin **%14,8**'inde uyuşmuyor.
  - Kaynak: `GOLD_R73_20261012_OVN1645_CROSSMARKET_RESIDUAL_REVERSAL_RESULT.md`, PR #83.
  - Küçük hareketlerde yön etiketi sağlayıcıya bağlı. Bu, ulaşılabilir doğruluğun üstüne bir tavan koyar ve yüzde-isabet ölçütünü gürültülü yapar.

### B4. [KANITLI] Dokunulmamış test verisi kalmadı

- 2025 ve 2026 onlarca çalışmada açıldı. Manifestler bunu tekrar tekrar not ediyor: "2025/2026 repeatedly opened", "2027 lockbox binding" (R28–R30).
- Tarihsel veriyle yeni bir bağımsız doğrulama mümkün değil. Tek temiz test **ileriye dönük** veridir.
- Bunu sistematik olarak kuran bir altyapı (yayın anında commit edilen tahmin defteri) bulamadım. Shadow ve prospective yönetişim metinleri var, ama günlük, zaman damgalı tahmin kaydı göremedim.

### B5. [KUVVETLİ ŞÜPHE] Çoklu karşılaştırma zarfı, "umut verici" sonuçların çoğunu kapsıyor

N = 200–250 örnek ve K = 50–375 test için, saf şansla beklenen **en iyi** doğruluk %57–60. Bu değerin %95 üst sınırı %60–63 (simülasyon).

Projenin "umut verici ama terfisiz" sonuçlarının çoğu bu bandın içinde. Örnekler:
- PRAMV: %60–63, N = 82–89, yani daha da geniş zarf.
- JDR4: %50–56.
- K25: %56–59.
- R27 2026: %52,8.

Testler bağımsız olmadığı için etkin K daha küçük; ama 2025/26 tekrar tekrar açıldığından yanlılık ters yönde de artıyor. White Reality Check veya Hansen SPA türünde **aile-boyu** bir düzeltme hiç uygulanmamış.

### B6. [KANITLI] Yükseliş yanlılığı ham isabeti şişiriyor; rejim tersine dönünce çöküyor

Hep-UP oranı:
- 2023 DEV: %59,7–61,3
- 2024: %54–56
- 2025: %54–55
- 2026: %46–49

Kaynak: R73/R73B tabloları; H3 2025 UP %63,1, 2026 %38,8 (R23).

Yüksek UP-recall'lu modeller 2023–25'te iyi görünüp 2026'da bozuluyor. Proje BA kullanıyor (iyi), ama "hep-UP'u yenmek" ve "2026 DOWN recall" tutarlı biçimde başarısız. Örnek: R28 2026 DOWN recall %22,6.

### B7. [KUVVETLİ ŞÜPHE] Konsensüs ve hibritler aynı bilgiyi tekrar sayıyor

CIG'in dört uzmanı aynı H3 bilgi kümesine dayanıyor. 4/4 uzlaşı, büyük olasılıkla **bilinen parçanın büyük olduğu** günleri seçiyor; %74,4 bu yüzden tekil uzmanlardan (%70–71) yüksek.

Benzer biçimde PRAMV'deki M4 ile RFR, aynı son iki yarım saati kullanıyor. Bu manifestte kabul edilmiş: "M4 and RFR are not feature-independent".

### B8. [KANITLI] İstatistiksel başarı ile işlem yapılabilir başarı arasındaki sistematik fark: maliyet eşiği hiç bilinmiyor

Banka BID/ASK geçmişi yok; tüm getiriler 25 bp **varsayımsal** maliyetle (R68, R70). Yönlü işlemin pozitif beklenti vermesi için gereken minimum isabet, ortalama mutlak hareket m ve gidiş-dönüş maliyeti c ile `p* = 0,5 + c/(2m)`. m değerleri R65 tablosundan:

| Pencere (R65) | m | c = 0,10% | c = 0,20% | c = 0,30% | c = 0,50% |
|---|---|---|---|---|---|
| Gece 2025 | 0,654% | %57,6 | %65,3 | %72,9 | %88,2 |
| Gündüz 2025 | 0,484% | %60,3 | %70,7 | %81,0 | >%100 |
| Gece 2026 | 1,060% | %54,7 | %59,4 | %64,2 | %73,6 |

Karar sonrası gözlenen isabetler %47–56. Banka gidiş-dönüş maliyeti %0,1'in üstündeyse, **hiçbir mevcut yön modeli kâr eşiğine yakın değil.** Bu, B1'den bağımsız ikinci bir kök neden.

---

## C. NEYİ GÖREMEDİK?

1. **Ortalama etkisi (Working 1960) aylık programın tamamında hiç adlandırılmamış** [KANITLI: depoda "Working" veya "averaging-induced" araması boş].
   - VW'nin "zaman ağırlıklandırması başarısı" büyük olasılıkla bu etkinin yeniden keşfi.
   - Aylık başarının kısa vadeye "taşınamaması" (R10–R14, H3'te ChHHO başarısızlığı) bu yüzden şaşırtıcı değil: taşınacak bir sinyal yok, taşınan şey etiket yapısı.
2. **Volatilite ile işaret arasındaki teorik köprü kullanılmadı** [KANITLI: "Christoffersen" araması boş].
   - Christoffersen & Diebold (2006): beklenen getiri sıfırdan farklıysa, oynaklığın öngörülebilirliği **yön** öngörülebilirliği üretir.
   - P(r > 0) = Φ(μ/σ_t). Etki düşük σ_t dönemlerinde en güçlü.
   - Projede risk/oynaklık ile yön hep ayrı modellendi; bu mekanizma test edilmedi.
3. **Planlı makro takvimin büyüklük için kullanımı test edilmedi.**
   - PRAMV makroyu *gerçekleşmiş* sürprizle bir *yön vetosu* olarak kullandı.
   - MRHIE (DeepSeek önerisi) "tentative" olarak kaldı.
   - Önceden bilinen olay takvimiyle **pencere-büyüklüğü / işlem-yapmama** tahmini yapılmadı.
   - Literatür, 08:30 NY açıklamalarının metal oynaklığını ve hacmini belirgin biçimde artırdığını gösteriyor (Elder, Miao & Ramchander 2012).
4. **Asya fiziki talep kanalı (SGE / Şanghay primi) hiç test edilmedi** [KANITLI: SGE yalnızca piyasa yapısı açıklamalarında geçiyor; prim özelliği yok].
   - 16:45 → 09 penceresi Asya seansını kapsıyor.
5. **Etiket tasarımında "ölü bölge" yok.** %14,8 kaynak uyuşmazlığı küçük hareketlerde yoğunlaşıyor; maliyet altındaki hareketler zaten işlem değeri taşımıyor. Üç sınıflı (UP / FLAT / DOWN, maliyet eşikli) hedef denenmedi.
6. **Gerçek ileriye dönük kayıt yok.** Tahminler yayın anında değiştirilemez biçimde (commit veya hash) kaydedilmiyor. Banka kotasyonları da toplanmıyor; bu veri geriye dönük üretilemez.

---

## D. BAŞARILI MODELLERDEN NE ÖĞRENEBİLİRİZ? (sentez)

| Çizgi | Rapor edilen en iyi | Karar sonrası / işlem yapılabilir karşılığı | Başarının asıl kaynağı (değerlendirmem) |
|---|---|---|---|
| Aylık ChHHO / DE-ABC | yön %70 / %76; RW'ye karşı ΣAE kazancı | Ölçülmedi | **Ortalama etiketi + bilinen kısım (VW).** Mimari önemsiz: 8 aile 1413–1460 ΣAE bandında (`GOLD_MONTHLY_PROJECT_MANIFEST.md` §1.2) |
| H3 (HELIOS, DPTC) | %63–71 (2026) | %55,05 vs hep-UP %56,88 (R38) | P[t] referansı ile 16 NY kesimi arasındaki **bilinen parça**, artı yükseliş yanlılığı |
| CIG-D1 | %74,4 / %80,7 | 08:15 NY sonrası %47,2 | Kesim öncesi gerçekleşen parça (R38 tablosu) |
| PRAMV (17:00 → 09) | BA %60–63, %34 kapsama | Zaten karar sonrası; ama 17:00 girişi ve banka makası doğrulanmadı | Olası gerçek mikro-yapı etkisi (ilk-dürtü geri dönüşü), **ancak** çoklu-test zarfında; 2026'da M3 uyumu tersine döndü |
| Risk (R15–R24, MAE5) | Brier iyileşmesi, üst/alt dilim ayrışması | Yön değil, büyüklük | **Oynaklık kümelenmesi.** Literatürde en sağlam öngörülebilirlik bu |
| R73 kalıntı | DEV BA %56 | REJECT | Faktör payı küçük; işaret = ham hareket |

**Ortak ders:**
- Projede **gerçekten** öngörülebilir olan şey **büyüklük ve risk**; yön, karar sonrası pencerelerde tutarlı biçimde şans düzeyinde.
- Mimari, hibrit ve konsensüs denemeleri bu tabloyu değiştirmedi. Değişken çeşitliliği (GPR, metaller, COT, GVZ, ZN/NQ/CL) da değiştirmedi.
- Bu, darboğazın **bilgi**de ve **hedef tanımında** olduğuna işaret ediyor; model ailesinde değil.

---

## E. YENİ BİLİMSEL ARAŞTIRMA ÖNERİLERİ (en fazla 5)

Her öneri ön-kayıtla, 2023–24 geliştirmesiyle ve 2025–26'nın yalnızca retrospektif raporlanmasıyla yürütülür; aylık işler için aylık DEV tanımı geçerlidir. Başarısız olursa eşik, saat veya model taraması yapılmaz.

### E1 — Bilinen-Kısım Tabanı Denetimi (KNOWN-SEGMENT BASELINE AUDIT)

- **Çözdüğü problem:** Geçmiş "başarıların" ne kadarının etiket yapısından geldiğini kesin olarak ölçmek. Böylece aynı yanılgı bir daha tekrarlanmaz.
- **Mekanizma:** Ortalama veya önceden basılmış referans etiketlerde `y = (P_karar − Ref_köken) + (Ref_hedef − P_karar)`. İlk terim karar anında biliniyor. Rastgele yürüyüşte bile yön doğruluğu %58–74.
- **Neden çözemedik:** CIG/H3 için kısmen bulundu (R38, R43). Aylık programda taban hep önceki ortalamaydı; son-fiyat tabanı hiç kurulmadı.
- **Kullanılabilir veri:** Mevcut, değiştirilmeyecek dondurulmuş tahmin dosyaları (aylık governed satırlar, H3 sonuç satırları, CIG 125/218); StakTrakr günlük ve CORE5 aylık seriler; Twelve Data 1s.
- **Yeni veri:** Gerekmez.
- **Sızıntı riski:** Yok. Taban yalnızca köken anında bilinen fiyatı kullanır. Ay sonu fiyatı köken anında bilinir.
- **Test:** Kendi DEV'i ve aynı tarihler üzerinde:
  - Aylık: ChHHO ve DE-ABC'yi tahmin `Ort[ay+1] = P_son(ay)` ve yön `sign(P_son − Ort)` tabanlarıyla karşılaştır. ΣAE ve yön için Diebold–Mariano / McNemar.
  - H3: HELIOS ve DPTC'yi `sign(P_kesim − P[t])` ile karşılaştır.
  - CIG: aynı.
  - Ayrıca her modelin **kalıntı becerisi**: bilinen kısım kontrol edildikten sonra hedef, model tahmini üzerine logit regresyonla açıklanıyor mu?
- **Başarı/başarısızlık:**
  - Model, bilinen-kısım tabanını DEV'de DM p < 0,05 ile yenerse **gerçek beceri vardır**; aylık → kısa vade aktarımı yeniden değerlendirmeye değer.
  - Yenemezse ilgili çizginin "başarısı" etiket yapısı olarak kayda geçer; o çizgiden yapılacak aktarım araştırmaları durdurulur.
- **Maliyet:** Çok düşük; birkaç saat, CPU.

### E2 — Oynaklık Dinamiği Üzerinden Koşullu Yön (Christoffersen–Diebold, CD-VOL)

- **Çözdüğü problem:** Yön öngörüsünü, projede **kanıtlanmış öngörülebilir** tek bileşene, oynaklığa bağlamak.
- **Mekanizma:**
  - P(r_pencere > 0 | F_t) = Φ(μ_t / σ_t).
  - σ_t; HAR-RV (M15'ten), önceki gün GVZ ve önceden bilinen olay takviminden tahmin edilir.
  - μ_t yavaş değişen bir sürüklenme tahminidir (ör. 250 günlük ortalama, ön-kayıtla sabit).
  - Yön sinyali en çok σ_t düşük ve |μ| belirgin olduğunda oluşur.
  - Teori, sinyalin günlük frekansta zayıf, ara ufuklarda güçlü olacağını öngörüyor; bu da test edilebilir.
- **Neden çözemedik:** Risk ve yön hep ayrı modellendi. Rejim kapıları (R23–R27) oynaklığı **kapı** olarak kullandı; olasılık **formülü** olarak kullanmadı.
- **Kullanılabilir veri:** EV/Dukascopy 2020–25, doğrudan Dukascopy 2026 M15, Neon `observations` GVZ.
- **Yeni veri:** Olay takvimi (BLS/BEA/Fed; geçmiş tarihleri kamuya açık ve önceden ilan ediliyor).
- **Sızıntı riski:** Düşük. σ ve μ yalnızca karar öncesi verilerle; takvim önceden bilinir.
- **Test:**
  - 09:00 → 16:45 ve 16:45 → ertesi 09:00 için ayrı ayrı, DEV 2023–24.
  - Brier ve BA, iki tabana karşı: (i) hep-UP, (ii) sabit Φ(μ/σ̄).
  - Ek olarak, σ̂ dilimlerine göre isabet profili. Tahmin: düşük σ̂ dilimlerinde isabet daha yüksek.
- **Başarı:**
  - DEV'de Brier'in sabit σ̄ tabanına göre iyileşmesi ve ay-blok bootstrap güven aralığının 0'ı dışlaması;
  - σ̂ dilimlerinde önceden belirtilen monotonluk;
  - 2025 ve 2026'da işaretin tersine dönmemesi.
  - Aksi halde REJECT.
- **Maliyet:** Düşük. İki parametreli formül; öğrenme yok, aşırı uyum riski minimal.

### E3 — Maliyet-Eşikli Büyüklük ve İşlem-Yapmama Modeli (VOL-HURDLE)

- **Çözdüğü problem:** "Bugün işlem yapmaya değer mi?" sorusu. Banka makasıyla doğrudan ilgili ve yön öngörüsünden bağımsız değer üretir.
- **Mekanizma:**
  - Oynaklık kümelenmesi.
  - Planlı makro açıklamalarda oynaklığın sıçraması (Elder ve diğ. 2012).
  - Gece penceresinin gündüzden sistematik olarak büyük olması (R65: gece/gündüz ortalama |hareket| 2025'te 0,654% / 0,484%).
- **Hedef:** `Y = 1{|r_pencere| > c}`. c, ön-kayıtla sabit maliyet senaryoları: 0,10 / 0,20 / 0,30% gidiş-dönüş. Ek olarak koşullu beklenen |r|.
- **Neden çözemedik:**
  - R15–R24 yalnızca H3 **aşağı** kuyruğunu (≥%1,5) modelledi.
  - MAE5 ise Borsa günlük fiyatında.
  - İki yönlü pencere büyüklüğü ve işlem-yapmama, banka saatleri için kurulmadı.
- **Veri:** E2 ile aynı; olay takvimi bir özellik olarak eklenir.
- **Sızıntı riski:** Düşük; olay **içeriği** değil yalnızca **zamanlaması** kullanılır.
- **Test:**
  - DEV 2023–24.
  - Brier/log-loss karşılaştırması: klimatoloji tabanı ve R18 RV+GVZ tabanı.
  - Üst/alt beşte-bir dilimde gerçekleşen |r| oranı.
- **Başarı:** Her eşikte DEV Brier'de ≥%5 iyileşme (blok-bootstrap güven aralığı 0'ı dışlamalı) ve her yıl üst/alt dilim |r| oranı ≥1,5.
- **Kullanım:** E2 veya başka bir yön sinyaliyle birleşince "yalnızca beklenen hareket > maliyet iken işlem" kuralı olur; gerisi işlem yapmamak.
- **Maliyet:** Düşük.

### E4 — Asya Fiziki Talep Kanalı: SGE/Şanghay Primi (SGE-PREM), gece penceresi için

- **Çözdüğü problem:** 16:45 → 09 gecesinin yönü için **altın fiyat yolundan bağımsız** yeni bilgi. B1 ve R73, kendi fiyat yolundan türetilen sinyallerin tükendiğini gösteriyor.
- **Mekanizma:**
  - Çin iç talebi ve ithalat kotaları Şanghay–Londra fiyat farkını (prim) oluşturur.
  - Prim değişimi fiziki talep baskısının göstergesidir.
  - Bu baskı, gece penceresinin büyük kısmını oluşturan Asya seansında uluslararası fiyata aktarılabilir.
  - WGC notu primin ortalamaya dönüşünü ve yerel talebe bağlılığını tartışıyor; prim ile **getiri öngörüsü** arasında hakemli bir kanıt bulamadım. Bu yüzden özgün ve tamamen yanlışlanabilir.
- **Neden çözemedik:** SGE yalnızca piyasa-yapısı metinlerinde geçiyor; hiçbir özellik setinde yok.
- **Yeni veri:**
  - SGE Au99.99 veya Shanghai Gold Benchmark günlük değerleri.
  - USD/CNY (CFETS orta kur, 09:15 Pekin ≈ 04:15 TR'de ilan edilir).
  - Kaynak, lisans ve **ilk yayın zamanı** denetimi şart.
- **Sızıntı riski:**
  - **Yüksek dikkat gerektirir.** SGE gece seansı 20:00–02:30 Pekin = 15:00–21:30 TR; hedef penceresiyle çakışır.
  - Yalnızca 16:45 TR'den önce yayınlanmış gündüz kapanışı veya benchmark kullanılabilir.
  - Sürüm ve ilk-yayın kanıtı yoksa test BLOCKED kalmalı; değer uydurulmamalı.
- **Test:** DEV 2023–24, tek özellikli (prim z-skor değişimi) düşük kapasiteli logit. Hep-UP ve klimatolojiye karşı BA ve Brier; ayrıca aynı günün altın getirisine göre ortogonallik.
- **Başarı:** DEV'de BA > hep-UP ve McNemar p < 0,05. Yoksa REJECT.
- **Maliyet:** Orta. Veri temini ve PIT denetimi işin büyük kısmı.

### E5 — Zaman Damgalı İleriye Dönük Test ve Banka Kotasyonu Kaydı (PROSPECTIVE LOCKBOX)

- **Çözdüğü problem:** B4 (temiz test kalmadı) ve B8 (maliyet bilinmiyor).
- **Hipotez:**
  - **(a)** Dondurulmuş, değiştirilmemiş tek bir aday, ileriye dönük 120 iş gününde hep-UP ve klimatolojiyi yener. Bu E2/E3'ün geliştirme sonrası dondurulmuş sürümü olabilir; ya da orijinal saatinde PRAMV V1 (17:00), çünkü 3 yılda tutarlı tek seçici aday.
  - **(b)** Banka gidiş-dönüş maliyeti c ölçülür ve B8 tablosundaki p* hesaplanır.
- **Yöntem:**
  - 08:45 ve 16:30 TR'de çalışan bir GitHub Actions işi tahmini üretir ve **pencere başlamadan önce commit eder**. Commit zaman damgası, değiştirilemez kayıt olur.
  - Banka alış/satış kotasyonları 09:00, 16:45 ve 17:00 sonrasında günlük olarak manuel ya da otomatik kaydedilir.
- **Sızıntı riski:** Yok; tanım gereği ileriye dönük.
- **Başarı:** 120 iş günü sonunda, önceden yazılmış ölçütlerle BA, Brier ve maliyet sonrası beklenti.
- **Maliyet:** Düşük. Takvim süresi uzun (~6 ay); başlamak için bekleme gerekmez.

---

## F. ÖNCELİK SIRASI

Puanlar 1–5 arası; yüksek daha iyi.

| Sıra | Öneri | Bilimsel fayda | Uygulanabilirlik | Test maliyeti (düşük = 5) | Özgünlük | Veri güvenilirliği | Toplam |
|---|---|---|---|---|---|---|---|
| 1 | **E1 Bilinen-kısım tabanı** | 5 | 5 | 5 | 4 | 5 | **24** |
| 2 | **E2 Christoffersen–Diebold koşullu yön** | 4 | 5 | 5 | 4 | 4 | **22** |
| 3 | **E3 Maliyet-eşikli büyüklük** | 4 | 5 | 4 | 3 | 4 | **20** |
| 3 | **E5 İleriye dönük + banka kotasyonu** | 5 | 4 | 4 | 2 | 5 | **20** |
| 5 | E4 SGE primi | 3 | 2 | 2 | 5 | 2 | 14 |

- **E2 ve E3 aynı σ̂ modelini kullanır:** HAR-RV + önceki gün GVZ + olay takvimi. Bu model bir kez kurulur ve tek bir ön-kayıtta iki ayrı hedefle sınanır.
- **E5 hemen ve paralel başlatılmalı:** puanı ne olursa olsun takvim süresine bağlıdır ve banka verisi geriye dönük toplanamaz.

---

## G. NİHAİ GÖRÜŞ

**İlk sırada E1'i yapmalıyız.** Gerekçeler:

1. **Ölçeği en büyük olan belirsizliği kapatır.** "Aylıkta işe yarayan yöntemi kısa vadeye taşıyalım" fikri R10–R14 boyunca birçok deneye mal oldu. Aylık başarının kaynağı ortalama etkisiyse, bu yol baştan kapalıdır. E1 bunu bir günde ve yeni veri olmadan ölçer.
2. **Projenin değerlendirme standardını düzeltir.** Bundan sonra her ön-kayda "karar anında bilinen kısım" tabanı ve "karar sonrası getiri" hedefi zorunlu girmeli. Bu tek kural CIG, H3 ve aylık yanılgılarını önceden engellerdi.
3. **Sonucu her iki yönde de değerlidir.** Aylık model tabanı yenerse, gerçek bir ekonomik sinyal kanıtlanmış olur ve aktarım (frekans hiyerarşisi) araştırması sağlam bir temele oturur. Yenemezse, kaynaklar ortak σ̂ üzerine kurulu E2/E3'e (oynaklık üzerinden koşullu yön ve maliyet-eşikli büyüklük) ve ileriye dönük teste (E5) yönlendirilir.

**Tekrar yaşanmaması için farklı yapacaklarımız:**
- **Hedef sözleşmesi:** Her hedef `P(karar sonrası ilk işlem yapılabilir fiyat) → P(çıkış)` olarak tanımlanır. Ortalama veya önceden basılmış referans etiketler yalnızca açıkça adlandırılmış ikincil hedef olabilir.
- **Zorunlu tabanlar:** hep-UP, klimatoloji ve **bilinen-kısım** tabanı; hepsi aynı tarihlerde.
- **Çoklu test muhasebesi:** Her çalışma ailesine kümülatif test sayacı tutulur. Terfi için Reality-Check veya SPA türü aile-boyu düzeltme gerekir.
- **Kaynak kilidi:** Etiket serisi tek sağlayıcı ve tek sürümle dondurulur. Sağlayıcı-uyuşmazlık oranı her sonuçta raporlanır.
- **Değer ölçütü:** Yön isabeti yerine maliyet sonrası beklenti ve işlem-yapmama oranı. Banka kotasyonları toplanmadan kârlılık iddiası yoktur.
- **Yeni hiçbir yön modeli** E1 ve E5 altyapısı kurulmadan geliştirilmemeli.
- **Yasak:** Aynı bilgi kümesi üzerinde yeni router, consensus veya kapı varyantları. B7 ve yön motorunun kapalı yollar kaydı gerekçedir.

---

## Ekler

### Ek-1 Sıfır-bilgi simülasyon çıktısı

Komut: `python3 gold_axis_2026/tools/gold_audit_20261012_label_structure_null_sim.py`

**Aylık (21 gün):**
- `sign(P_son − Ort)` yön: 0,7382
- `sign(VW)` yön: 0,7359
- corr(VW, bilinen kısım): 0,9928
- MAE(son fiyat) / MAE(önceki ortalama): 0,7316

**H3:**
- AM etiketi, `sign(P_kesim − P_t)`: 0,6194
- Gün-ortalaması etiketi, `sign(P_kesim − P_t)`: 0,5847
- Gün-ortalaması etiketi, `sign(P_08NY − P_t)`: 0,6930

**CIG** (AM → AM etiketi, `sign(P_kesim(D−1) − AM(D−1))`): 0,7384

**Şans zarfı** (beklenen en iyi doğruluk / %95 üst sınır):

| N | K = 50 | K = 375 |
|---|---|---|
| 200 | 0,579 / 0,610 | 0,604 / 0,630 |
| 250 | 0,571 / 0,596 | 0,593 / 0,616 |

**Kâr eşiği isabeti:** B8 tablosu.

Simülasyon gerçek veri değildir. Gerçek ölçüm E1'in konusudur.

### Ek-2 Doğrulayamadıklarım ve sınırlar

- 939 Markdown, 740 betik ve 685 iş akışının tamamını satır satır okumadım. Önce proje haritası çıkarıldı; ardından kritik iddiaların kodu ve sonuç dosyaları derinlemesine incelendi:
  - aylık `vw_midas_*`;
  - CIG R34B/R37/R38;
  - H3 manifesti §2/§4/§6;
  - R65, R67, R73/R73B;
  - fırsat Stage 2–5;
  - yön motoru §3–§6/§12.
- Aylık governed tahmin satırlarının ay sonu fiyatlarıyla birleşimi yapılmadı (E1). Bu nedenle B1(c) **kuvvetli şüphe** düzeyindedir.
- PRAMV'nin 17:00 girişinin ve banka makasının uygulanabilirliği doğrulanmadı (manifest de belirtiyor).
- SGE verisinin kamuya açık, PIT-güvenli geçmişi doğrulanmadı.
- Hansen (2005) SPA DOI'si web aramasıyla doğrulanamadı; aşağıda "doğrulanmadı" diye işaretli.

### Ek-3 Kaynaklar

| Kaynak | Rapordaki rolü |
|---|---|
| Working, H. (1960). Note on the Correlation of First Differences of Averages in a Random Chain. *Econometrica* 28(4), 916–918. JSTOR 1907574 (DOI aramada doğrulanamadı) | Ortalama etkisi, B1(c) |
| Christoffersen, P. & Diebold, F. X. (2006). Financial Asset Returns, Direction-of-Change Forecasting, and Volatility Dynamics. *Management Science* 52(8), 1273–1287. DOI 10.1287/mnsc.1060.0520 | E2 |
| Elder, J., Miao, H. & Ramchander, S. (2012). Impact of Macroeconomic News on Metal Futures. *Journal of Banking & Finance* 36(1), 51–65. DOI 10.1016/j.jbankfin.2011.06.007 | E3 olay takvimi |
| Lou, D., Polk, C. & Skouras, S. (2019). A Tug of War: Overnight versus Intraday Expected Returns. *Journal of Financial Economics* 134(1), 192–213. DOI 10.1016/j.jfineco.2019.03.011 | Gece/gündüz ayrışması bağlamı |
| Caldara, D. & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review* 112(4), 1194–1225. DOI 10.1257/aer.20191823 | Projede kullanılan GPR verisinin kaynağı |
| Erb, C. B. & Harvey, C. R. (2013). The Golden Dilemma. *Financial Analysts Journal* 69(4), 10–42. DOI 10.2469/faj.v69.n4.1 | Altın–reel faiz ve uzun vadeli değerleme bağlamı |
| Hansen, P. R. (2005). A Test for Superior Predictive Ability. *JBES* 23, 365–380 (DOI doğrulanmadı) | B5 ve G'de aile-boyu düzeltme önerisi |
| White, H. (2000). A Reality Check for Data Snooping. *Econometrica* 68(5), 1097–1126 (künye bellekten; DOI doğrulanmadı) | B5 ve G'de aile-boyu düzeltme önerisi |
| World Gold Council Goldhub (2022). *Sky high: recent surge in the Shanghai–London gold price spread* — https://www.gold.org/goldhub/gold-focus/2022/10/sky-high-recent-surge-shanghai-london-gold-price-spread | E4 için arka plan; getiri öngörüsü kanıtı değildir |
