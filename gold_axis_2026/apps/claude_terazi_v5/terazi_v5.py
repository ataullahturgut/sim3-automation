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
