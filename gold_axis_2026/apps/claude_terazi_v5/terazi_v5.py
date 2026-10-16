"""TERAZİ v5 modeli: v4 makinesi + saha güveni taban orana göre (TERAZI_V5_ON_KAYIT.md §2).

Tek değişiklik v4'e göre: kural güveni `(μ ≥ p0) == (y ≥ 0,5)` ile ölçülür. v4'te referans
0,5 idi; taban oran ~0,4 iken "hep nakit" diyen kurallar bedava güven kazanıyordu.
"""
import os, sys
from contextlib import contextmanager
HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("claude_terazi_v4", "claude_terazi_v2", "claude_deneyim_v1"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import terazi_v2 as T2
import terazi_v4 as T4

_BaseRule = T2.Rule


class RuleV5(_BaseRule):
    __slots__ = ()
    REF = 0.5                      # Terazi5 her öğrenmeden önce taban orana ayarlar

    def observe(self, w, y, post_birth):
        if w < 1e-6:
            return
        mu_before = self.mu
        self.s = T2.RHO * self.s + w * y
        self.n = T2.RHO * self.n + w
        if post_birth:
            agree = 1.0 if (mu_before >= RuleV5.REF) == (y >= 0.5) else 0.0
            self.h = T2.RHO * self.h + w * agree
            self.k = T2.RHO * self.k + w


@contextmanager
def _v5_rules():
    """v4.restructure yeni kuralı T2.Rule ile yaratır; bu blokta RuleV5 yaratsın."""
    T2.Rule = RuleV5
    try:
        yield
    finally:
        T2.Rule = _BaseRule


class Terazi5(T4.Terazi):
    def learn(self, i, z, y):
        RuleV5.REF = self.p0
        super().learn(i, z, y)

    def restructure(self, Zm, ym, now):
        RuleV5.REF = self.p0
        with _v5_rules():
            return super().restructure(Zm, ym, now)


def rebuild_rules(net, Zm, ym, days):
    """Ek-1: her kuralın s, n, h, k istatistiklerini güncel etiketlerle baştan, sırayla yeniden kur.
    RuleV5.observe ile birebir aynı güncelleme; post_birth = gün > kuralın doğduğu gün."""
    import numpy as np
    RuleV5.REF = net.p0
    RHO, PW, PP = T2.RHO, T2.PRIOR_W, T2.PRIOR_P
    ref = net.p0
    N = len(ym)
    for R in net.rules:
        w = np.ones(N)
        for (j, d, c) in R.gates:
            w *= T2.gate_value(Zm, j, d, c)
        s = n = h = k = 0.0
        born = R.born
        for t in range(N):
            wt = w[t]
            if wt < 1e-6:
                continue
            y = ym[t]
            mu_b = (s + PW * PP) / (n + PW)
            s = RHO * s + wt * y
            n = RHO * n + wt
            if days[t] > born:
                agree = 1.0 if (mu_b >= ref) == (y >= 0.5) else 0.0
                h = RHO * h + wt * agree
                k = RHO * k + wt
        R.s, R.n, R.h, R.k = s, n, h, k


class Terazi6(Terazi5):
    """Ek-2. strong=True → D1 (yalnız w ≥ 0,5 kurallar oy verir). stable=True → D2 (istikrar testi).
    restructure çağrılmadan önce self.years (öğrenilmiş günlerin yılı) ayarlanmalıdır."""

    def __init__(self, strong=True, stable=True):
        super().__init__()
        self.strong, self.stable = strong, stable
        self.years = None

    def decide(self, z):
        import math
        W = Pw = 0.0
        fired = []
        wmin = 0.5 if self.strong else 0.05
        for R in self.rules:
            a = R.weight
            if a <= 0:
                continue
            w = R.fire(z)
            if w < wmin:
                continue
            fired.append((R, a * w)); W += a * w; Pw += a * w * R.mu
        if W < T4.W_MIN:
            return None
        P = Pw / W
        U = math.sqrt(sum(aw * (R.mu * (1 - R.mu) / max(R.n, 1.0) + (R.mu - P) ** 2)
                          for R, aw in fired) / W)
        return dict(P=P, U=U, W=W, n_fired=len(fired),
                    top=[(R.label(), round(R.mu, 3), round(R.weight, 2))
                         for R, _ in sorted(fired, key=lambda x: -x[1])[:4]])

    def restructure(self, Zm, ym, now):
        import math
        import numpy as np
        RuleV5.REF = self.p0
        S_ = T4.S
        if len(ym) < T4.MIN_SUPPORT:
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
            grid = (0.5,) if S_.FEATURES[j] in S_.BINARY else T4.GRID
            for d_ in (1, -1):
                for c in grid:
                    if ((j, d_, c),) not in have:
                        cands.append(((j, d_, c),))
        for R in self.rules:
            if len(R.gates) >= T4.MAX_GATES:
                continue
            used = {g[0] for g in R.gates}
            for j in range(Zm.shape[1]):
                if j in used:
                    continue
                grid = (0.5,) if S_.FEATURES[j] in S_.BINARY else T4.GRID
                for d_ in (1, -1):
                    for c in grid:
                        gs = tuple(sorted(R.gates + ((j, d_, c),)))
                        if gs not in have:
                            cands.append(gs)
        fam = {tuple(sorted((j, d_) for (j, d_, c) in gs)) for gs in cands}
        pen = math.sqrt(2 * math.log(max(2, len(fam))))
        if self.stable:
            yrs = np.asarray(self.years)
            uy, code = np.unique(yrs, return_inverse=True)
        scored = []
        for gs in cands:
            w = np.ones(len(Zm))
            for (j, d_, c) in gs:
                w *= T2.gate_value(Zm, j, d_, c)
            n_eff = float(w.sum())
            if n_eff < T4.MIN_SUPPORT:
                continue
            m = float((w @ res) / n_eff)
            m_shrunk = m * n_eff / (n_eff + T4.MIN_SUPPORT)
            z_ev = abs(m_shrunk) * math.sqrt(n_eff) / sd
            if z_ev <= pen - T4.ADMIT_MARGIN * T4.TAU:
                continue
            if self.stable:
                wy = np.bincount(code, weights=w, minlength=len(uy))
                ry = np.bincount(code, weights=w * res, minlength=len(uy))
                okyrs = wy >= T4.MIN_SUPPORT
                if okyrs.sum() < 2:
                    continue
                if not np.all(np.sign(ry[okyrs] / wy[okyrs]) == np.sign(m)):
                    continue
            c0 = max(T4.C0_LO, min(T4.C0_HI, math.tanh((z_ev - pen) / T4.TAU)))
            scored.append((z_ev, gs, m, n_eff, c0))
        scored.sort(key=lambda x: -x[0])
        born = []
        for z_ev, gs, m, n_eff, c0 in scored[:T4.BIRTH_PER_MONTH]:
            R = RuleV5(gs, born=now, c0=c0, z_birth=z_ev)
            for q, zrow in enumerate(Zm):
                R.observe(R.fire(zrow), ym[q], post_birth=False)
            self.rules.append(R); self.audit["born"] += 1
            born.append(R.label())
        died, keep = [], []
        for R in self.rules:
            if (R.k >= T4.DEATH_MIN_FIELD and R.trust < 0) or R.n < T4.DEATH_MIN_N:
                died.append(R.label()); self.audit["died"] += 1
            else:
                keep.append(R)
        self.rules = keep
        seen, uniq = set(), []
        for R in sorted(self.rules, key=lambda x: -x.weight):
            if R.gates in seen:
                self.audit["died"] += 1; continue
            seen.add(R.gates); uniq.append(R)
        self.rules = uniq[:T4.MAX_RULES]
        return dict(born=born, died=died)
