"""TERAZİ v4 — kullanıcı seçimli hedef. TERAZI_V4_HEDEF_SECIMI_ON_KAYIT.md'ye birebir uygulanır.

Hedef: maliyetli ideal yolun net getirisi ≥ NET_MIN olan bacaklarında ALTINDA ol.
Eşik kullanıcının 24 seçiminden okundu (tuttuğu en küçük %2,51, çıkardığı en büyük %2,32).

Kural makinesi v2'den DEĞİŞTİRİLMEDEN alınır: Rule, gate_value, sabitler. Değişen tek şey
hedefin ne olduğu ve etiketin nasıl olgunlaştığı.
"""
import math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "claude_terazi_v2"))
sys.path.insert(0, os.path.join(HERE, "..", "claude_deneyim_v1"))
import terazi_v2 as T2
import deneyim_states as S
from deneyim_v1 import oracle, legs_from_positions

# --- v2'den devralınan, değişmeyen sabitler ---
GATE_S, GRID, MAX_GATES = T2.GATE_S, T2.GRID, T2.MAX_GATES
RHO, PRIOR_W, PRIOR_P = T2.RHO, T2.PRIOR_W, T2.PRIOR_P
MIN_SUPPORT, BIRTH_PER_MONTH = T2.MIN_SUPPORT, T2.BIRTH_PER_MONTH
DEATH_MIN_FIELD, DEATH_MIN_N, MAX_RULES = T2.DEATH_MIN_FIELD, T2.DEATH_MIN_N, T2.MAX_RULES
TRUST_SHRINK, TAU, ADMIT_MARGIN = T2.TRUST_SHRINK, T2.TAU, T2.ADMIT_MARGIN
C0_LO, C0_HI, W_MIN, LAM = T2.C0_LO, T2.C0_HI, T2.W_MIN, T2.LAM
FEE = S.FEE

# --- v4'ün tek yeni sabiti: kullanıcının eşiği ---
NET_MIN = 2.4          # net getiri yüzdesi; kullanıcı seçiminden okundu, taranmadı


def target_labels(rows, i_end, net_min=NET_MIN, i_start=0):
    """rows[i_start..i_end] üzerinde ideal yolu koş, net ≥ net_min olan KAPANMIŞ bacakları döndür.

    Dönüş: {gün_indeksi: 1/0} — yalnız kapanmış bacaklardan türetilmiş etiketler.
    Açık kalan son bacağın günleri sözlükte YOKTUR (etiketsiz, öğrenilmez).
    Bu fonksiyon yalnız i_end'e kadarki fiyatları okur; nedensellik buradan gelir.
    """
    pos, _ = oracle(rows, i_start, i_end)
    legs = legs_from_positions(rows, i_start, pos)
    closed = [L for L in legs if L["exit_i"] is not None]
    last_known = max((L["exit_i"] for L in closed), default=i_start - 1)
    lab = {}
    for i in range(i_start, last_known + 1):
        lab[i] = 0
    for L in closed:
        if (L["net_pct"] or 0.0) >= net_min:
            for q in range(L["entry_i"], L["exit_i"]):     # çıkış günü NAKİT sayılır
                lab[q] = 1
    return lab, closed, last_known


class Terazi:
    """Tek kural tabanı: P(altında ol | z). Karar v2'nin kuralı."""

    def __init__(self):
        self.rules = []
        self.p0 = PRIOR_P          # ek-1: karar referansı = öğrenilmiş etiketlerin taban oranı
        self.audit = dict(born=0, died=0, no_opinion=0)

    def decide(self, z):
        W = Pw = 0.0
        fired = []
        for R in self.rules:
            a = R.weight
            if a <= 0:
                continue
            w = R.fire(z)
            if w < 0.05:
                continue
            fired.append((R, a * w)); W += a * w; Pw += a * w * R.mu
        if W < W_MIN:
            return None
        P = Pw / W
        U = math.sqrt(sum(aw * (R.mu * (1 - R.mu) / max(R.n, 1.0) + (R.mu - P) ** 2)
                          for R, aw in fired) / W)
        return dict(P=P, U=U, W=W, n_fired=len(fired),
                    top=[(R.label(), round(R.mu, 3), round(R.weight, 2))
                         for R, _ in sorted(fired, key=lambda x: -x[1])[:4]])

    def action(self, pos, z):
        """Ek-1: referans 0,5 yerine taban oran p0. v2 kuralının z-testi biçimi korunur."""
        d = self.decide(z)
        if d is None:
            return "HOLD", None
        if d["U"] <= 0:
            return "HOLD", d
        zs = (d["P"] - self.p0) / d["U"]
        d["z"] = zs
        d["p0"] = self.p0
        if pos == 0 and zs > LAM:
            return "AL", d
        if pos == 1 and -zs > LAM:
            return "SAT", d
        return "HOLD", d

    def learn(self, i, z, y):
        for R in self.rules:
            R.observe(R.fire(z), y, post_birth=(i > R.born))

    def restructure(self, Zm, ym, now):
        """v2.restructure ile birebir aynı; hedef farklı olduğu için ayrı tutulur."""
        if len(ym) < MIN_SUPPORT:
            return dict(born=[], died=[])
        pred = np.full(len(ym), self.p0)
        for q, zrow in enumerate(Zm):
            d = self.decide(zrow)
            if d is not None:
                pred[q] = d["P"]
        res = ym - pred
        sd = float(np.std(res)) or 1.0
        have = {R.gates for R in self.rules}
        cands = []
        for j in range(Zm.shape[1]):
            grid = (0.5,) if S.FEATURES[j] in S.BINARY else GRID
            for d_ in (1, -1):
                for c in grid:
                    if ((j, d_, c),) not in have:
                        cands.append(((j, d_, c),))
        for R in self.rules:
            if len(R.gates) >= MAX_GATES:
                continue
            used = {g[0] for g in R.gates}
            for j in range(Zm.shape[1]):
                if j in used:
                    continue
                grid = (0.5,) if S.FEATURES[j] in S.BINARY else GRID
                for d_ in (1, -1):
                    for c in grid:
                        gs = tuple(sorted(R.gates + ((j, d_, c),)))
                        if gs not in have:
                            cands.append(gs)
        fam = {tuple(sorted((j, d_) for (j, d_, c) in gs)) for gs in cands}
        pen = math.sqrt(2 * math.log(max(2, len(fam))))
        scored = []
        for gs in cands:
            w = np.ones(len(Zm))
            for (j, d_, c) in gs:
                w *= T2.gate_value(Zm, j, d_, c)
            n_eff = float(w.sum())
            if n_eff < MIN_SUPPORT:
                continue
            m = float((w @ res) / n_eff)
            m_shrunk = m * n_eff / (n_eff + MIN_SUPPORT)
            z_ev = abs(m_shrunk) * math.sqrt(n_eff) / sd
            if z_ev > pen - ADMIT_MARGIN * TAU:
                c0 = max(C0_LO, min(C0_HI, math.tanh((z_ev - pen) / TAU)))
                scored.append((z_ev, gs, m, n_eff, c0))
        scored.sort(key=lambda x: -x[0])
        born = []
        for z_ev, gs, m, n_eff, c0 in scored[:BIRTH_PER_MONTH]:
            R = T2.Rule(gs, born=now, c0=c0, z_birth=z_ev)
            for q, zrow in enumerate(Zm):
                R.observe(R.fire(zrow), ym[q], post_birth=False)
            self.rules.append(R); self.audit["born"] += 1
            born.append(dict(label=R.label(), p_in=round(R.mu, 3), support=round(n_eff, 1),
                             residual_mean=round(m, 3), evidence_z=round(z_ev, 2),
                             birth_credibility=round(c0, 3), bar=round(pen, 2)))
        died, keep = [], []
        for R in self.rules:
            if (R.k >= DEATH_MIN_FIELD and R.trust < 0) or R.n < DEATH_MIN_N:
                died.append(dict(label=R.label(), trust=round(R.trust, 3), field_k=round(R.k, 1),
                                 lifetime_days=now - R.born)); self.audit["died"] += 1
            else:
                keep.append(R)
        self.rules = keep
        seen, uniq = set(), []
        for R in sorted(self.rules, key=lambda x: -x.weight):
            if R.gates in seen:
                self.audit["died"] += 1; continue
            seen.add(R.gates); uniq.append(R)
        self.rules = uniq[:MAX_RULES]
        return dict(born=born, died=died)
