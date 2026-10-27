"""Write the worlds: the Aug 31 order and recency arms, run with the unchanged Cell 0.

order    FIRST-SEEK (climb the envelope, then descend) vs FIRST-AVOID (reverse);
         same genomes, same time in each mode, T = 4000, flip at 2000.
recency  SEEK-THEN-AVOID (2000 seek, 6000 avoid) vs AVOID throughout (8000);
         both arms end with 6000 steps of avoiding.
Saves M, Mx, My per world (scouts are discarded: the reader never sees them).
"""
import sys
import numpy as np
sys.path.insert(0, 'writer')
from cell0 import World
from signature import CFG


def order_arm(seed, seek_first, T=4000, half=2000):
    w = World(seed=seed, g_lo=0.0, g_hi=1.0, **CFG)
    w.g = np.abs(w.g) * (1.0 if seek_first else -1.0)
    w.run(half)
    w.g = -w.g
    w.run(T - half)
    return w


def recency_arm(seed, seek_first, P1=2000, P2=6000):
    w = World(seed=seed, g_lo=0.0, g_hi=1.0, **CFG)
    w.g = np.abs(w.g) * (1.0 if seek_first else -1.0)
    w.run(P1)
    w.g = -np.abs(w.g)
    w.run(P2)
    return w


def make(kind, n_per_arm, base):
    f = order_arm if kind == 'order' else recency_arm
    M, Mx, My, y = [], [], [], []
    for cls, seek_first in enumerate([True, False]):
        for s in range(n_per_arm):
            w = f(base + 1000 * cls + s, seek_first)
            M.append(w.M.copy()); Mx.append(w.Mx.copy()); My.append(w.My.copy()); y.append(cls)
            print(f'{kind} arm {cls} world {s}', flush=True)
    np.savez_compressed(f'results/worlds_{kind}.npz', M=np.array(M), Mx=np.array(Mx),
                        My=np.array(My), y=np.array(y))


if __name__ == '__main__':
    kind, n, base = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    make(kind, n, base)
