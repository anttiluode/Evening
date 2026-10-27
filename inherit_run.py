"""Confirmatory runs for PREREG_INHERIT.md.

map      p in P_GRID, REPS worlds each -> p'  (individual receptor)
lineage  start p0 in {0, 1}, NLIN lineages, G generations, receptor arm in {indiv, quorum}
"""
import json, sys, time
import numpy as np
from inherit import Receptor, write, ping_sites, spec, flags_for, SITES

P_GRID = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.50, 0.75, 0.90, 1.0]
REPS, NLIN, G = 4, 8, 8


def quorum(dec):
    """Each site adopts the majority of its 3x3 neighbourhood on the 8x8 torus of sites."""
    D = dec.reshape(8, 8)
    s = sum(np.roll(np.roll(D, a, 0), b, 1) for a in (-1, 0, 1) for b in (-1, 0, 1))
    return (s >= 5).astype(int).ravel()


def run_map(rec, base=200000):
    rng = np.random.default_rng(base)
    rows = []
    for i, p in enumerate(P_GRID):
        for r in range(REPS):
            M = write(flags_for(p, rng), seed=base + 100 * i + r)
            d = rec.seek_first(spec(ping_sites(M)))
            rows.append(dict(p=p, rep=r, p_next=float(d.mean()), p_next_quorum=float(quorum(d).mean())))
            print(f'map p={p:.2f} rep {r}: p\'={d.mean():.3f}', flush=True)
    return rows


def run_lineages(rec, arm, base):
    rows = []
    for p0 in (0.0, 1.0):
        for L in range(NLIN):
            rng = np.random.default_rng(base + 1000 * int(p0) + L)
            flags = flags_for(p0, rng)
            traj = [float(flags.mean())]
            for g in range(G):
                M = write(flags, seed=base + 100000 * int(p0) + 1000 * L + g)
                d = rec.seek_first(spec(ping_sites(M)))
                flags = quorum(d) if arm == 'quorum' else d
                traj.append(float(flags.mean()))
            rows.append(dict(arm=arm, p0=p0, lineage=L, traj=traj))
            print(f'{arm} p0={p0} lineage {L}: {np.round(traj, 2).tolist()}', flush=True)
    return rows


if __name__ == '__main__':
    what = sys.argv[1]
    rec = Receptor()
    t = time.time()
    if what == 'map':
        out = dict(receptor_train_acc=rec.train_acc, map=run_map(rec))
    else:
        out = dict(lineages=run_lineages(rec, what, base={'indiv': 300000, 'quorum': 400000}[what]))
    out['seconds'] = time.time() - t
    json.dump(out, open(f'results/inherit_{what}.json', 'w'), indent=1)
