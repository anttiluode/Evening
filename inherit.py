"""Reader that writes back: does the read-write loop carry a bit across generations?

One generation:
  1. A population of Cell 0 scouts writes for 4000 steps. A fraction p of them run the
     seek-first schedule (seek 2000, then avoid), the rest avoid-first.  Same genomes
     otherwise; the schedule is the only heritable thing.
  2. The scouts are removed and the material frozen (the "egg").
  3. 64 reading sites on an 8x8 grid each fire ONE local ping (source at the site,
     receiver 20 cells along x, 150-step window, sigma 0.5) and pass the heard spectrum
     through a fixed receptor -> seek-first or avoid-first.
  4. A fresh world with fresh scouts on blank material: child i takes the decision of
     site i mod 64.  p' = fraction of sites that read seek-first.
No genome is copied: the only channel from parents to children is material -> ping ->
receptor.

The receptor is frozen once, from single-pair features of the 48 confirmatory order
worlds (pure populations p = 1 and p = 0): nearest class centroid on z-scored log band
power.  Like a genetic code, it is a fixed translation table; the question is what the
LOOP does with it, not whether a table can be learned.
"""
import sys
import numpy as np
sys.path.insert(0, 'writer')
import reader as R
from cell0 import World
from signature import CFG

R.SIGMA = 0.5
T1 = 150
SITES = [(8 + 16 * i, 8 + 16 * j) for i in range(8) for j in range(8)]


def spec(tr, lo=0.3, hi=4.0, nb=12):
    w = np.fft.rfftfreq(tr.shape[-1], R.DT) * 2 * np.pi
    P = np.abs(np.fft.rfft(tr * np.hanning(tr.shape[-1]), axis=-1)) ** 2
    e = np.geomspace(lo, hi, nb + 1)
    return np.log(np.stack([P[..., (w >= a) & (w < b)].mean(-1)
                            for a, b in zip(e[:-1], e[1:])], -1) + 1e-30)


class Receptor:
    def __init__(self, path='results/spec_order.npy', ypath='results/worlds_order.npz'):
        S = np.load(path)                      # (16 pairs, 48 worlds, 12)
        y = np.load(ypath)['y']
        X = S.reshape(-1, S.shape[-1]); Y = np.tile(y, S.shape[0])
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-12
        Z = (X - self.mu) / self.sd
        self.c0, self.c1 = Z[Y == 0].mean(0), Z[Y == 1].mean(0)
        self.train_acc = float(((self.decide_z(Z) == 0) == (Y == 0)).mean())

    def decide_z(self, Z):
        return (np.linalg.norm(Z - self.c1, axis=-1) < np.linalg.norm(Z - self.c0, axis=-1)).astype(int)

    def seek_first(self, feats):               # 1 = reads as seek-first (class 0)
        return 1 - self.decide_z((feats - self.mu) / self.sd)


def ping_sites(M, sites=SITES, steps=T1, chunk=16):
    """One ping per site through the same frozen material; returns (K, steps)."""
    N = M.shape[0]
    y, x = np.mgrid[:N, :N]
    out = []
    for a in range(0, len(sites), chunk):
        ss = sites[a:a + chunk]
        psi = np.stack([np.exp(-((y - r) ** 2 + (x - c) ** 2) / (2 * R.SIGMA ** 2)) for r, c in ss])
        old = psi.copy(); V = R.V0 * M[None]
        tr = np.zeros((len(ss), steps))
        rec = [(r, (c + 20) % N) for r, c in ss]
        idx = np.arange(len(ss))
        rr = np.array([p[0] for p in rec]); cc = np.array([p[1] for p in rec])
        for t in range(steps):
            new = (2 * psi - old + R.DT ** 2 * (R.C ** 2 * R.lap(psi) - V * psi)
                   - R.GAM * R.DT * (psi - old))
            old, psi = psi, new
            tr[:, t] = psi[idx, rr, cc]
        out.append(tr)
    return np.concatenate(out)


def write(seek_first_flags, seed, T=4000, half=2000):
    """A world whose scout i runs seek-first iff flag i (flags tiled over scouts)."""
    w = World(seed=seed, g_lo=0.0, g_hi=1.0, **CFG)
    n = len(w.g)
    f = np.resize(np.asarray(seek_first_flags, int), n)
    w.g = np.abs(w.g) * np.where(f == 1, 1.0, -1.0)
    w.run(half)
    w.g = -w.g
    w.run(T - half)
    return w.M.copy()


def read(M, rec):
    return rec.seek_first(spec(ping_sites(M)))


def flags_for(p, rng, k=64):
    f = np.zeros(k, int); f[:int(round(p * k))] = 1
    return rng.permutation(f)
