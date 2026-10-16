"""TERAZİ v3 — iki kanallı karar. TERAZI_V3_IKI_KANAL_ON_KAYIT.md'ye birebir uygulanır.

Giriş kanalı: v2'nin TeraziV2 nesnesi AYNEN kullanılır (kod kopyalanmaz, import edilir),
böylece giriş davranışının v2 ile birebir aynı olduğu yapısal olarak garanti edilir.

Çıkış kanalı: ayrı bir kural tabanı, yeni ve HIZLI hedefle öğrenir —
    brk[i] = 1  ⇔  i, düşen bacağın ilk m günündendir ("tepe kırılma anı")
Olgunlaşma v2 ile aynıdır: brk[i] ancak bacağın dönüşü onaylandığında bilinir (conf[i]).

Yeni özellik (feature) EKLENMEZ. İddia şudur: hedefi hızlandırmak, elimizdeki günlük getiri
değişkeninin kural doğumunu kendiliğinden kazanmasına yeter (ön kayıttaki H1).
"""
import math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "claude_terazi_v2"))
sys.path.insert(0, os.path.join(HERE, "..", "claude_deneyim_v1"))
import terazi_v2 as T2
import deneyim_states as S

# --- v2'den devralınan, DEĞİŞMEYEN sabitler ---
THETA = T2.THETA
GATE_S, GRID, MAX_GATES = T2.GATE_S, T2.GRID, T2.MAX_GATES
RHO = T2.RHO
MIN_SUPPORT, BIRTH_PER_MONTH = T2.MIN_SUPPORT, T2.BIRTH_PER_MONTH
DEATH_MIN_FIELD, DEATH_MIN_N, MAX_RULES = T2.DEATH_MIN_FIELD, T2.DEATH_MIN_N, T2.MAX_RULES
TRUST_SHRINK, TAU, ADMIT_MARGIN = T2.TRUST_SHRINK, T2.TAU, T2.ADMIT_MARGIN
C0_LO, C0_HI, W_MIN, LAM = T2.C0_LO, T2.C0_HI, T2.W_MIN, T2.LAM
PRIOR_W = T2.PRIOR_W
FEE = S.FEE

# --- v3'ün ön kayıtta dondurulmuş yeni sabitleri ---
M_BREAK = 5          # kırılma penceresi: düşen bacağın ilk m günü
# Çıkış testi: (Q − p0)/U_Q > LAM. Bu, v2'nin (P − 0,5)/U > LAM kuralının referansı
# taban orana taşınmış halidir; yeni parametre yoktur, LAM v2'den devralınır.
# Ek-2 (TERAZI_V3_ON_KAYIT_EKI_OLCEK_HATASI.md): ön kayıttaki "Q − λU > 2·p0" yazımı bir
# ölçek hatasıydı — nadir olayda U_Q ≈ 0,85·Q olduğu için test ulaşılamaz hale geliyordu.
EXIT_LAM = LAM


def break_labels(P, theta=THETA, m=M_BREAK):
    """Kırılma etiketleri. Dönüş: brk[i] ∈ {0,1,None}, conf[i] = etiketin bilinir olduğu gün.

    conf, v2'nin zigzag onay zamanının AYNISIDIR — nedensellik katmanı değişmez.
    brk[i] = 1 yalnızca i bir bacak tepesinden sonraki ilk m gün içindeyse (onay gününde kesilir).
    """
    lab, conf = T2.phase_labels(P, theta)
    n = len(P)
    # zigzag döngüsünü tekrar koşup bacak TEPELERİNİ ve onay günlerini topla
    tops = []                     # (tepe_indeksi, onay_günü)
    piv = ext = 0
    direction = 0
    for i in range(1, n):
        if direction == 0:
            up = 100 * (P[i] / min(P[:i + 1]) - 1)
            dn = 100 * (P[i] / max(P[:i + 1]) - 1)
            if up >= theta:
                direction = 1; ext = i; piv = int(np.argmin(P[:i + 1]))
            elif dn <= -theta:
                direction = -1; ext = i; piv = int(np.argmax(P[:i + 1]))
                tops.append((piv, i))
            continue
        if direction == 1:
            if P[i] > P[ext]:
                ext = i
            elif 100 * (P[i] / P[ext] - 1) <= -theta:
                tops.append((ext, i))
                piv, direction, ext = ext, -1, i
        else:
            if P[i] < P[ext]:
                ext = i
            elif 100 * (P[i] / P[ext] - 1) >= theta:
                piv, direction, ext = ext, 1, i
    brk = [None if lab[i] is None else 0 for i in range(n)]
    for top, c in tops:
        for q in range(top + 1, min(top + m, c) + 1):
            if q < n:
                brk[q] = 1
    return brk, conf, tops


class RuleB:
    """v2'nin Rule'ü ile aynı; tek fark: öncül oran (prior) dışarıdan verilir.

    Dengesiz hedefte (taban oran ≈ %10) "0,5 tarafını tuttun mu" testi anlamsızdır:
    her kural neredeyse hep 0 der ve bedava güven kazanır. Bu yüzden saha testinin
    referansı 0,5 yerine TABAN ORANDIR: "bu kural, koşulsuz orandan yüksek dedi mi?"
    """
    __slots__ = ("gates", "s", "n", "h", "k", "born", "c0", "z_birth", "p0")

    def __init__(self, gates, born, p0, c0=0.0, z_birth=0.0):
        self.gates = tuple(sorted(gates))
        self.s, self.n = 0.0, 0.0
        self.h, self.k = 0.0, 0.0
        self.born, self.c0, self.z_birth, self.p0 = born, c0, z_birth, p0

    def fire(self, z):
        w = 1.0
        for (j, d, c) in self.gates:
            w *= 1.0 / (1.0 + math.exp(-d * (z[j] - c) / GATE_S))
        return w

    @property
    def mu(self):
        """P(kırılma | bu kural tetiklendi); indirimli ağırlıklı oran + taban oran öncülü."""
        return (self.s + PRIOR_W * self.p0) / (self.n + PRIOR_W)

    @property
    def trust(self):
        return (2 * self.h - self.k + TRUST_SHRINK * self.c0) / (self.k + TRUST_SHRINK)

    @property
    def weight(self):
        return max(0.0, self.trust)

    def observe(self, w, y, post_birth):
        if w < 1e-6:
            return
        mu_before = self.mu
        self.s = RHO * self.s + w * y
        self.n = RHO * self.n + w
        if post_birth:
            agree = 1.0 if (mu_before >= self.p0) == (y >= 0.5) else 0.0
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
                    p_break=round(self.mu, 4), n=round(self.n, 2), trust=round(self.trust, 4),
                    field_k=round(self.k, 2), born_index=self.born,
                    birth_credibility=round(self.c0, 3), birth_evidence_z=round(self.z_birth, 3))


class BreakBase:
    """Çıkış kanalı kural tabanı. Makine v2 ile aynı; hedef ve öncül farklı."""

    def __init__(self, p0):
        self.p0 = float(p0)
        self.rules = []
        self.audit = dict(born=0, died=0, no_opinion=0)

    def decide(self, z):
        W = Qw = 0.0
        fired = []
        for R in self.rules:
            a = R.weight
            if a <= 0:
                continue
            w = R.fire(z)
            if w < 0.05:
                continue
            fired.append((R, a * w)); W += a * w; Qw += a * w * R.mu
        if W < W_MIN:
            return None
        Q = Qw / W
        U = math.sqrt(sum(aw * (R.mu * (1 - R.mu) / max(R.n, 1.0) + (R.mu - Q) ** 2)
                          for R, aw in fired) / W)
        return dict(Q=Q, U=U, W=W, n_fired=len(fired),
                    top=[(R.label(), round(R.mu, 3), round(R.weight, 2))
                         for R, _ in sorted(fired, key=lambda x: -x[1])[:4]])

    def learn(self, i, z, y):
        for R in self.rules:
            R.observe(R.fire(z), y, post_birth=(i > R.born))

    def restructure(self, Zm, ym, now):
        if len(ym) < MIN_SUPPORT:
            return dict(born=[], died=[])
        pred = np.full(len(ym), self.p0)
        for q, zrow in enumerate(Zm):
            d = self.decide(zrow)
            if d is not None:
                pred[q] = d["Q"]
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
            R = RuleB(gs, born=now, p0=self.p0, c0=c0, z_birth=z_ev)
            for q, zrow in enumerate(Zm):
                R.observe(R.fire(zrow), ym[q], post_birth=False)
            self.rules.append(R); self.audit["born"] += 1
            born.append(dict(label=R.label(), p_break=round(R.mu, 3), support=round(n_eff, 1),
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


def macro_confirms(mrow):
    """Ön kayıt 2.4: reel faiz VEYA kısa faiz altına karşı dönmüş olmalı.
    Eksik değer o koşulu YANLIŞ sayar; ikisi de eksikse onay yoktur."""
    rr = mrow.get("rr_d5")
    y2 = mrow.get("y2_d5")
    return bool((rr is not None and rr > 0) or (y2 is not None and y2 > 0))


class TeraziV3:
    """Giriş: v2 nesnesi aynen. Çıkış: hızlı kırılma kanalı VEYA v2'nin yavaş kanalı."""

    def __init__(self, p0, exit_lam=EXIT_LAM):
        self.entry = T2.TeraziV2()          # giriş kanalı — v2 koduyla birebir aynı
        self.exitb = BreakBase(p0)
        self.exit_lam = float(exit_lam)

    @property
    def p0(self):
        return self.exitb.p0

    def action(self, pos, z, mrow):
        """Dönüş: (karar, bilgi_sözlüğü)."""
        de = self.entry.decide(z)
        dx = self.exitb.decide(z)
        zq = None
        if dx is not None and dx["U"] > 0:
            zq = (dx["Q"] - self.p0) / dx["U"]      # v2'nin z-testi, referans p0
        info = dict(P=None if de is None else de["P"], U=None if de is None else de["U"],
                    Q=None if dx is None else dx["Q"], UQ=None if dx is None else dx["U"],
                    zq=zq, lam=self.exit_lam, macro=macro_confirms(mrow),
                    entry_top=None if de is None else de["top"],
                    exit_top=None if dx is None else dx["top"], reason=None)
        if pos == 0:
            if de is not None and de["P"] - LAM * de["U"] > 0.5:
                info["reason"] = "yavaş kanal: yükselme evresine emin"
                return "AL", info
            return "HOLD", info
        # pozisyondayız: hızlı kanal önce sınanır
        if zq is not None and info["macro"] and zq > self.exit_lam:
            info["reason"] = "hızlı kanal: bacak kırıldı + makro onayı"
            return "SAT", info
        if de is not None and de["P"] + LAM * de["U"] < 0.5:
            info["reason"] = "yavaş kanal: düşme evresine emin"
            return "SAT", info
        return "HOLD", info
