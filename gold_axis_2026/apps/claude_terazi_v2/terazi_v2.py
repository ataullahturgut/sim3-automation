"""TERAZİ v2 — evre (faz) modeli. TERAZI_V2_EVRE_MODELI_ON_KAYIT.md'ye birebir uygulanır.

Soru: "altın şu an yükselme evresinde mi, düşme evresinde mi?"
Kurallar P(yükselme evresi) öğrenir; karar yalnız güvene dayanır. Masraf karara girmez, NAV'a girer.
Etiket olgunlaşması: bir günün evresi, bacağın dönüşü ONAYLANDIĞINDA bilinir (sabit pencere yok).
"""
import math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "claude_deneyim_v1"))
import deneyim_states as S

# --- ön kayıtta dondurulmuş sabitler ---
THETA = 5.0                 # zigzag dönüş eşiği (%)
GATE_S = 0.5
GRID = (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)
MAX_GATES = 3
RHO = 0.995
PRIOR_W, PRIOR_P = 2.0, 0.5   # evre oranı öncülü
MIN_SUPPORT = 20.0
BIRTH_PER_MONTH = 3
DEATH_MIN_FIELD, DEATH_MIN_N = 15.0, 5.0
MAX_RULES = 60
TRUST_SHRINK = 10.0
TAU, ADMIT_MARGIN = 1.0, 1.5
C0_LO, C0_HI = -0.4, 0.9
W_MIN, LAM = 0.5, 0.5
FEE = S.FEE                   # yalnız NAV muhasebesinde


def phase_labels(P, theta=THETA):
    """Zigzag evre etiketleri ve ONAY zamanları.
    Dönüş: lab[i] ∈ {0,1} (0=düşme bacağı, 1=yükselme bacağı), conf[i] = etiketin bilinir olduğu gün indeksi.
    Bir bacak, fiyatın ucundan theta% ters hareketiyle onaylanır; bacağın TÜM günleri o anda etiketlenir.
    """
    n = len(P)
    lab = [None] * n
    conf = [None] * n
    piv = 0                      # son onaylı dönüş noktası
    ext = 0                      # mevcut bacağın uç noktası
    direction = 0                # 0 = henüz yön yok, +1 yükseliş, -1 düşüş
    for i in range(1, n):
        if direction == 0:
            up = 100 * (P[i] / min(P[:i + 1]) - 1)
            dn = 100 * (P[i] / max(P[:i + 1]) - 1)
            if up >= theta:
                direction = 1; ext = i; piv = int(np.argmin(P[:i + 1]))
                for q in range(piv, i + 1):
                    lab[q], conf[q] = 1, i
            elif dn <= -theta:
                direction = -1; ext = i; piv = int(np.argmax(P[:i + 1]))
                for q in range(piv, i + 1):
                    lab[q], conf[q] = 0, i
            continue
        if direction == 1:
            if P[i] > P[ext]:
                ext = i
            elif 100 * (P[i] / P[ext] - 1) <= -theta:
                # yükseliş bacağı ext'te bitti; ext..i düşüş bacağı olarak onaylandı
                for q in range(piv, ext + 1):
                    lab[q], conf[q] = 1, min(conf[q] if conf[q] is not None else i, i)
                for q in range(ext, i + 1):
                    lab[q], conf[q] = 0, i
                piv, direction, ext = ext, -1, i
        else:
            if P[i] < P[ext]:
                ext = i
            elif 100 * (P[i] / P[ext] - 1) >= theta:
                for q in range(piv, ext + 1):
                    lab[q], conf[q] = 0, min(conf[q] if conf[q] is not None else i, i)
                for q in range(ext, i + 1):
                    lab[q], conf[q] = 1, i
                piv, direction, ext = ext, 1, i
    return lab, conf


def gate_value(Z, j, d, c):
    return 1.0 / (1.0 + np.exp(-d * (Z[:, j] - c) / GATE_S))


class Rule:
    __slots__ = ("gates", "s", "n", "h", "k", "born", "c0", "z_birth")

    def __init__(self, gates, born, c0=0.0, z_birth=0.0):
        self.gates = tuple(sorted(gates))
        self.s, self.n = 0.0, 0.0           # indirimli toplam ve sayım; mu = (s + öncül)/(n + öncül)
        self.h, self.k = 0.0, 0.0
        self.born, self.c0, self.z_birth = born, c0, z_birth

    def fire(self, z):
        w = 1.0
        for (j, d, c) in self.gates:
            w *= 1.0 / (1.0 + math.exp(-d * (z[j] - c) / GATE_S))
        return w

    @property
    def mu(self):
        """P(yükselme evresi | bu kural tetiklendi); indirimli ağırlıklı oran + öncül."""
        return (self.s + PRIOR_W * PRIOR_P) / (self.n + PRIOR_W)

    @property
    def trust(self):
        return (2 * self.h - self.k + TRUST_SHRINK * self.c0) / (self.k + TRUST_SHRINK)

    @property
    def weight(self):
        return max(0.0, self.trust)

    def observe(self, w, y, post_birth):
        """y ∈ {0,1}: onaylanmış evre etiketi."""
        if w < 1e-6:
            return
        mu_before = self.mu
        self.s = RHO * self.s + w * y
        self.n = RHO * self.n + w
        if post_birth:
            agree = 1.0 if (mu_before >= 0.5) == (y >= 0.5) else 0.0
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
        return dict(gates=[list(g) for g in self.gates], label=self.label(),
                    p_rising=round(self.mu, 4), n=round(self.n, 2), trust=round(self.trust, 4),
                    field_k=round(self.k, 2), born_index=self.born,
                    birth_credibility=round(self.c0, 3), birth_evidence_z=round(self.z_birth, 3))


class TeraziV2:
    def __init__(self):
        self.rules = []
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
        U = math.sqrt(sum(aw * (R.mu * (1 - R.mu) / max(R.n, 1.0) + (R.mu - P) ** 2) for R, aw in fired) / W)
        return dict(P=P, U=U, W=W, n_fired=len(fired),
                    top=[(R.label(), round(R.mu, 3), round(R.weight, 2)) for R, _ in sorted(fired, key=lambda x: -x[1])[:4]])

    def action(self, pos, z):
        d = self.decide(z)
        if d is None:
            return "HOLD", None
        if pos == 0 and d["P"] - LAM * d["U"] > 0.5:
            return "AL", d
        if pos == 1 and d["P"] + LAM * d["U"] < 0.5:
            return "SAT", d
        return "HOLD", d

    def learn(self, i, z, y):
        for R in self.rules:
            R.observe(R.fire(z), y, post_birth=(i > R.born))

    def restructure(self, Zm, ym, now):
        if len(ym) < MIN_SUPPORT:
            return dict(born=[], died=[])
        pred = np.full(len(ym), PRIOR_P)
        for q, z in enumerate(Zm):
            d = self.decide(z)
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
                w *= gate_value(Zm, j, d_, c)
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
            R = Rule(gs, born=now, c0=c0, z_birth=z_ev)
            for q, zrow in enumerate(Zm):
                R.observe(R.fire(zrow), ym[q], post_birth=False)
            self.rules.append(R); self.audit["born"] += 1
            born.append(dict(label=R.label(), p_rising=round(R.mu, 3), support=round(n_eff, 1),
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
