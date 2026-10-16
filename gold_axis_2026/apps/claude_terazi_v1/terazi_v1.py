"""TERAZİ v1 — kural tabanlı uyarlanır çıkarım ağı. TERAZI_V1_MIMARI_ON_KAYIT.md'ye birebir uygulanır.

Katmanlar: yumuşak koşul kapıları → seyrek kurallar (yumuşak VE) → olasılıksal sonuç belleği
→ sahada sınanmış güven (yalnız doğum sonrası) → maliyet duyarlı tartı.
Yapı değişimi aylık: artıklardan kural doğumu, güvenini yitiren kuralın ölümü.
Nedensellik: hiçbir sonuç olgunlaşmadan öğrenilmez; ayın kararları önceki ay sonu tabanıyla verilir.
"""
import math, os, sys
from collections import OrderedDict
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "claude_deneyim_v1"))
import deneyim_states as S
from deneyim_v1 import oracle, legs_from_positions          # ideal etiket (yalnız rapor/teşhis için)

# --- ön kayıtta dondurulmuş sabitler ---
H = 10                                   # sonuç ufku (karar günü)
GATE_S = 0.5                             # kapı yumuşaklığı (z birimi)
GRID = (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)
MAX_GATES = 3
RHO = 0.995                              # sonuç/güven indirimi
V_MIN, V0, MU0 = 0.25, 9.0, 0.0
MIN_SUPPORT = 20.0                       # kural doğumu için etkin destek
BIRTH_PER_MONTH = 3
DEATH_MIN_FIELD = 15.0                   # doğum sonrası kanıt eşiği
DEATH_MIN_N = 5.0
MAX_RULES = 60
TRUST_SHRINK = 10.0
TAU = 1.0                                # kanıt bulanıklığı (kanıt birimi)
ADMIT_MARGIN = 1.5                       # kabul tabanı: z > pen - 1.5*TAU
C0_LO, C0_HI = -0.4, 0.9                 # doğum güveni kırpma
W_MIN = 0.5
LAM = 0.5
FEE = S.FEE
C_RT = -200.0 * math.log(1 - FEE)
BUY_TH, SELL_TH = C_RT / 2, -C_RT / 2


def gate_value(Z, j, d, c):
    return 1.0 / (1.0 + np.exp(-d * (Z[:, j] - c) / GATE_S))


class Rule:
    __slots__ = ("gates", "mu", "v", "n", "h", "k", "born", "births_seen", "c0", "z_birth")

    def __init__(self, gates, born, c0=0.0, z_birth=0.0):
        self.gates = tuple(sorted(gates))
        self.c0 = c0                       # doğum güveni (dereceli kanıt), öncül
        self.z_birth = z_birth             # doğumdaki kanıt oranı
        self.mu, self.v, self.n = MU0, V0, 0.0
        self.h, self.k = 0.0, 0.0            # sahada sınanmış: isabet / toplam (doğum sonrası)
        self.born = born                      # doğduğu gün indeksi
        self.births_seen = 0

    def fire(self, z):
        w = 1.0
        for (j, d, c) in self.gates:
            w *= 1.0 / (1.0 + math.exp(-d * (z[j] - c) / GATE_S))
        return w

    def fire_all(self, Z):
        w = np.ones(len(Z))
        for (j, d, c) in self.gates:
            w *= gate_value(Z, j, d, c)
        return w

    @property
    def trust(self):
        # doğum güveni öncül; saha kanıtı (k) büyüdükçe sahada ölçülen isabet baskın gelir
        return (2 * self.h - self.k + TRUST_SHRINK * self.c0) / (self.k + TRUST_SHRINK)

    @property
    def weight(self):
        return max(0.0, self.trust)

    def observe(self, w, r, post_birth):
        """Olgunlaşmış bir sonucu öğren. post_birth: kural doğduktan sonra mı oluştu."""
        if w < 1e-6:
            return
        mu_before = self.mu
        self.n = RHO * self.n + w
        self.mu = self.mu + (w / self.n) * (r - self.mu)
        self.v = max(V_MIN, RHO * self.v + (w / self.n) * ((r - mu_before) ** 2 - self.v))
        if post_birth:
            agree = 1.0 if (mu_before > 0) == (r > 0) else 0.0
            self.h = RHO * self.h + w * agree
            self.k = RHO * self.k + w

    def label(self):
        parts = []
        for (j, d, c) in self.gates:
            f = S.FEATURES[j]
            if f in S.BINARY:
                parts.append(f"{S.LABEL_TR[f]} {'var' if d > 0 else 'yok'}")
            else:
                parts.append(f"{S.LABEL_TR[f]} {'>' if d > 0 else '<'} {c:+.1f}σ")
        return " VE ".join(parts)

    def to_dict(self):
        return dict(gates=[list(g) for g in self.gates], label=self.label(), mu=round(self.mu, 4),
                    v=round(self.v, 4), n=round(self.n, 2), trust=round(self.trust, 4),
                    field_k=round(self.k, 2), born_index=self.born,
                    birth_credibility=round(self.c0, 3), birth_evidence_z=round(self.z_birth, 3))


class Terazi:
    def __init__(self):
        self.rules = []
        self.audit = dict(born=0, died=0, no_opinion=0, conflict_hold=0)

    # --- katman 5: tartı ---
    def decide(self, z):
        W = Ew = 0.0
        fired = []
        for R in self.rules:
            a = R.weight
            if a <= 0:
                continue
            w = R.fire(z)
            if w < 0.05:
                continue
            fired.append((R, a * w))
            W += a * w; Ew += a * w * R.mu
        if W < W_MIN:
            return None
        E = Ew / W
        # belirsizlik: ORTALAMANIN standart hatası + kurallar arası çelişki (düzeltme eki)
        U = math.sqrt(sum(aw * (R.v / max(R.n, 1.0) + (R.mu - E) ** 2) for R, aw in fired) / W)
        return dict(E=E, U=U, W=W, n_fired=len(fired),
                    top=[(R.label(), round(R.mu, 2), round(R.weight, 2)) for R, _ in sorted(fired, key=lambda x: -x[1])[:4]])

    def action(self, pos, z):
        d = self.decide(z)
        if d is None:
            return "HOLD", None
        if pos == 0 and d["E"] - LAM * d["U"] > BUY_TH:
            return "AL", d
        if pos == 1 and d["E"] + LAM * d["U"] < SELL_TH:
            return "SAT", d
        return "HOLD", d

    # --- katman 3+4: olgunlaşmış sonucu öğren ---
    def learn(self, i, z, r):
        for R in self.rules:
            R.observe(R.fire(z), r, post_birth=(i > R.born))

    # --- aylık yapı değişimi ---
    def restructure(self, Zm, rm, idxm, now):
        """Zm/rm/idxm: olgunlaşmış günlerin durumları, sonuçları ve indeksleri (yalnız geçmiş)."""
        if len(rm) < MIN_SUPPORT:
            return dict(born=[], died=[])
        # artıklar: modelin o günkü görüşü (görüş yoksa 0)
        pred = np.zeros(len(rm))
        for q, z in enumerate(Zm):
            d = self.decide(z)
            if d is not None:
                pred[q] = d["E"]
        res = rm - pred
        sd = float(np.std(res)) or 1.0
        have = {R.gates for R in self.rules}
        cands = []
        for j in range(Zm.shape[1]):
            grid = (0.5,) if S.FEATURES[j] in S.BINARY else GRID
            for d_ in (1, -1):
                for c in grid:
                    g = (j, d_, c)
                    if (g,) not in have:
                        cands.append((g,))
        for R in self.rules:                      # hayatta kalanlara bir kapı ekle
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
        # etkin bağımsız deneme: eşik ızgarası tek aile sayılır (komşu eşikler korelasyonlu)
        fam = {tuple(sorted((j, d_) for (j, d_, c) in gs)) for gs in cands}
        M = max(2, len(fam))
        pen = math.sqrt(2 * math.log(M))
        scored = []
        for gs in cands:
            w = np.ones(len(Zm))
            for (j, d_, c) in gs:
                w *= gate_value(Zm, j, d_, c)
            n_eff = float(w.sum())
            if n_eff < MIN_SUPPORT:
                continue
            m = float((w @ res) / n_eff)
            m_shrunk = m * n_eff / (n_eff + MIN_SUPPORT)      # küçültme
            z = abs(m_shrunk) * math.sqrt(n_eff) / sd          # kanıt oranı
            if z > pen - ADMIT_MARGIN * TAU:                   # dereceli kabul tabanı
                c0 = max(C0_LO, min(C0_HI, math.tanh((z - pen) / TAU)))
                scored.append((z, gs, m, n_eff, c0))
        scored.sort(key=lambda x: -x[0])
        born = []
        for z, gs, m, n_eff, c0 in scored[:BIRTH_PER_MONTH]:
            R = Rule(gs, born=now, c0=c0, z_birth=z)
            for q, zrow in enumerate(Zm):          # doğum anındaki bölge özetini kur (oy hakkı vermez)
                R.observe(R.fire(zrow), rm[q], post_birth=False)
            self.rules.append(R); self.audit["born"] += 1
            born.append(dict(label=R.label(), mu=round(R.mu, 3), support=round(n_eff, 1), residual_mean=round(m, 3),
                             evidence_z=round(z, 2), birth_credibility=round(c0, 3), bar=round(pen, 2)))
        # ölüm
        died = []
        keep = []
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
