"""TERAZİ v5 hedefi: gecikmeye dayanıklı hareketler.

İdeal yolun dönüş noktaları (dipler = bacak başları, tepeler = bacak sonları) alınır.
Gerçek zamanlı bir algoritma her dönüşü K gün geç fark eder; bu yüzden bir hareket
(dip_i → tepe_j, j ≥ i) giriş dip_i+K, çıkış tepe_j+K fiyatlarıyla değerlendirilir.
Örtüşmeyen (dip, tepe) çiftlerinden NAV'ı en büyük yapan dizi DP ile seçilir.
Bu, kısa hareketleri ya eler ya da komşu uzun harekete birleştirir.
Etiket: seçilen hareketlerin [dip, tepe) günleri = ALTINDA ol.
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "claude_deneyim_v1"))
import deneyim_states as S
from deneyim_v1 import oracle, legs_from_positions

K_LAG = 2          # algılama gecikmesi (işlem günü); önceden beyan, duyarlılık K=3
FEE = S.FEE


def robust_moves(rows, i_start, i_end, k=K_LAG):
    """rows[i_start..i_end] içinde, yalnız bu aralığın fiyatlarıyla, seçilen hareketler.
    Dönüş: [(dip_i, tepe_i, gecikmeli_net_yüzde)], kapanmış (tepe+k ≤ i_end) olanlar."""
    pos, _ = oracle(rows, i_start, i_end)
    legs = [L for L in legs_from_positions(rows, i_start, pos) if L["exit_i"] is not None]
    n = len(legs)
    if n == 0:
        return []
    B = [L["entry_i"] for L in legs]; T = [L["exit_i"] for L in legs]
    def logm(i, j):                      # dip_i'de gir, tepe_j'de çık, ikisi de +k gecikmeli
        e, x = B[i] + k, T[j] + k
        if x > i_end or e >= x:
            return None
        return 2 * math.log(1 - FEE) + math.log(rows[x]["bid"]) - math.log(rows[e]["ask"])
    # best[t] = ilk t bacak kullanılarak elde edilen en iyi log servet; seçimler örtüşmez
    best = [0.0] * (n + 1); choice = [None] * (n + 1)
    for t in range(1, n + 1):
        best[t], choice[t] = best[t - 1], None           # bacak t-1'i dahil etme
        j = t - 1                                         # hareket tepe_j'de biter
        for i in range(0, j + 1):                         # dip_i'de başlar
            v = logm(i, j)
            if v is None or v <= 0:
                continue
            c = best[i] + v
            if c > best[t]:
                best[t], choice[t] = c, i
    out = []; t = n
    while t > 0:
        if choice[t] is None:
            t -= 1
        else:
            i = choice[t]; j = t - 1
            out.append((B[i], T[j], 100 * (math.exp(logm(i, j)) - 1)))
            t = i
    return list(reversed(out))


def target_labels(rows, i_end, k=K_LAG, i_start=0):
    """Ay sonuna kadarki fiyatlarla hedef etiketleri; yalnız kapanmış bölge etiketlenir."""
    moves = robust_moves(rows, i_start, i_end, k)
    pos, _ = oracle(rows, i_start, i_end)
    legs = [L for L in legs_from_positions(rows, i_start, pos) if L["exit_i"] is not None]
    last_known = max((L["exit_i"] for L in legs), default=i_start - 1)
    last_known = min(last_known, i_end - k)              # tepe+k gözlenmiş olmalı
    lab = {i: 0 for i in range(i_start, last_known + 1)}
    for b, t, _ in moves:
        if t <= last_known:
            for q in range(b, t):
                lab[q] = 1
    return lab, moves, last_known
