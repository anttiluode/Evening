"""Confirmatory run: frozen reader on fresh worlds (see PREREG.md)."""
import json, sys
import numpy as np
sys.path.insert(0, 'writer')
import reader as R
from cell0 import surrogate
from signature import radial

R.SIGMA = 0.5
T1 = 150
PAIRS = [((16 + 32 * i) % 128, (6 + 32 * j) % 128) for i in range(4) for j in range(4)]
SUB8 = [4 * i + j for i in range(4) for j in (0, 2)]


def loo(X, y):
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    X = (X - X.mean(0)) / (X.std(0) + 1e-12)
    ok = 0
    for i in range(len(X)):
        m = np.ones(len(X), bool); m[i] = False
        c0 = X[m & (y == 0)].mean(0); c1 = X[m & (y == 1)].mean(0)
        ok += int((np.linalg.norm(X[i] - c1) < np.linalg.norm(X[i] - c0)) == y[i])
    return ok / len(X)


def perm_p(X, y, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    obs = loo(X, y)
    cnt = sum(loo(X, rng.permutation(y)) >= obs for _ in range(n))
    return (cnt + 1) / (n + 1)


def spec(tr, lo=0.3, hi=4.0, nb=12):
    w = np.fft.rfftfreq(tr.shape[-1], R.DT) * 2 * np.pi
    P = np.abs(np.fft.rfft(tr * np.hanning(tr.shape[-1]), axis=-1)) ** 2
    e = np.geomspace(lo, hi, nb + 1)
    return np.log(np.stack([P[..., (w >= a) & (w < b)].mean(-1)
                            for a, b in zip(e[:-1], e[1:])], -1) + 1e-30)


def read_all(M):
    """(16, B, 12) spectral features, one row per pair."""
    S = []
    for sy, sx in PAIRS:
        tr = R.ping(M, steps=T1, src=(sy, sx), rec=(sy, (sx + 20) % 128))
        S.append(spec(tr))
    return np.array(S)


def union_footprint():
    u = np.zeros((128, 128), bool)
    for sy, sx in PAIRS:
        ds = R.torus_dist((sy, sx)); dr = R.torus_dist((sy, (sx + 20) % 128))
        u |= ds + dr <= R.C * T1 * R.DT + 4
    return u


def analyse(kind):
    d = np.load(f'results/worlds_{kind}.npz')
    M, y = d['M'], d['y']
    S = read_all(M)
    np.save(f'results/spec_{kind}.npy', S)
    u = union_footprint()
    res = dict(n=int(len(y)), union_area=float(u.mean()))
    X16, X8, X1 = S.mean(0), S[SUB8].mean(0), S[0]
    res['ping16'] = loo(X16, y); res['ping16_p'] = perm_p(X16, y)
    res['ping8'] = loo(X8, y); res['ping8_p'] = perm_p(X8, y)
    res['ping1'] = loo(X1, y)
    res['global_mean'] = loo(M.mean((1, 2)), y)
    res['union_mean'] = loo(M[:, u].mean(1), y)
    res['union_hist'] = loo(np.c_[M[:, u].mean(1),
                                  np.quantile(M[:, u], [.1, .25, .5, .75, .9, .99], axis=1).T], y)
    res['god_quantiles'] = loo(np.array([np.quantile(m, [.5, .9, .99]) for m in M]), y)
    res['god_radial_shape'] = loo(np.array([radial(m) for m in M]), y)
    res['god_quant_means'] = {str(c): np.quantile(M[y == c], [.1, .25, .5, .75, .9, .99]).tolist()
                              for c in (0, 1)}
    if kind == 'order':
        rng = np.random.default_rng(5)
        Ms = np.array([surrogate(m, rng) for m in M])
        Ss = read_all(Ms).mean(0)
        res['surrogate_ping16'] = loo(Ss, y); res['surrogate_ping16_p'] = perm_p(Ss, y)
        Mp = np.array([rng.permutation(m.ravel()).reshape(m.shape) for m in M])
        Sp = read_all(Mp).mean(0)
        res['shuffle_ping16'] = loo(Sp, y)
        np.save('results/spec_order_surrogate.npy', Ss)
    print(kind, json.dumps(res, indent=1), flush=True)
    return res


if __name__ == '__main__':
    out = {k: analyse(k) for k in sys.argv[1:]}
    old = {}
    try:
        old = json.load(open('results/main.json'))
    except FileNotFoundError:
        pass
    old.update(out)
    json.dump(old, open('results/main.json', 'w'), indent=1)
