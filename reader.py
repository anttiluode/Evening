"""The reader: one ping through frozen scout-written material, heard at one receiver.

The probe medium is Cell 0's own fast field with the scouts removed and the material
frozen:  psi_tt = c^2 lap(psi) - V0 * M(x) psi - gam psi_t,  on the same 128^2 torus,
same c, dt, V0 and damping.  Written material raises the local cutoff frequency, so it
scatters and partly blocks the ping.  The ping is a Gaussian pulse released at rest at
the source cell.

Causal footprint (the bulk form of WallMemoryLaw's tour law): within a listening
window that ends at step t1, the receiver can only have heard material at points x with
    d(src, x) + d(x, rec) <= c * t1 * dt      (torus distances)
because the field's top signal speed is c.  That ellipse is known from geometry before
anything is measured, and it is the whole region a window of length t1 reads.
"""
import numpy as np

C, DT, GAM, V0 = 1.0, 0.4, 0.02, 8.0      # Cell 0 / signature CFG values
N = 128
SIGMA = 1.5
SRC = (54, 64)                            # one source, one receiver, 20 cells apart
REC = (74, 64)
STEPS = 240                               # 96 time units: shorter than any wrap path


def lap(a):
    return (np.roll(a, 1, -2) + np.roll(a, -1, -2)
            + np.roll(a, 1, -1) + np.roll(a, -1, -1) - 4.0 * a)


def torus_dist(p):
    y, x = np.mgrid[:N, :N]
    dy = np.abs(y - p[0]); dy = np.minimum(dy, N - dy)
    dx = np.abs(x - p[1]); dx = np.minimum(dx, N - dx)
    return np.hypot(dy, dx)


D_SRC, D_REC = torus_dist(SRC), torus_dist(REC)
PATH = D_SRC + D_REC                      # length of the shortest single-scatter path via x


def footprint(t1, margin=0.0):
    """Material that a window ending at step t1 can have heard."""
    return PATH <= C * t1 * DT + margin


def ping(M, steps=STEPS, src=SRC, rec=REC, probes=None):
    """M: (B, N, N) frozen material.  Returns traces (B, steps) at the receiver."""
    M = np.atleast_3d(M) if M.ndim == 2 else M
    if M.ndim == 2:
        M = M[None]
    B = M.shape[0]
    y, x = np.mgrid[:N, :N]
    dy = y - src[0]; dx = x - src[1]
    pulse = np.exp(-(dy ** 2 + dx ** 2) / (2 * SIGMA ** 2))
    psi = np.broadcast_to(pulse, (B, N, N)).copy()
    old = psi.copy()                      # released at rest
    V = V0 * M
    out = np.zeros((B, steps))
    for t in range(steps):
        new = (2 * psi - old + DT * DT * (C ** 2 * lap(psi) - V * psi)
               - GAM * DT * (psi - old))
        old, psi = psi, new
        out[:, t] = psi[:, rec[0], rec[1]]
    return out


def trace_features(tr, t0=0, t1=STEPS, nbins=12):
    """Log energy in nbins equal time bins of the window [t0, t1)."""
    seg = tr[..., t0:t1]
    edges = np.linspace(0, seg.shape[-1], nbins + 1).astype(int)
    e = np.stack([(seg[..., a:b] ** 2).mean(-1) for a, b in zip(edges[:-1], edges[1:])], -1)
    return np.log(e + 1e-30)


def local_attackers(M, t1):
    """What an observer who knows the footprint but not the arrangement sees:
    mean material, and the material histogram (quantiles), inside the footprint."""
    m = footprint(t1)
    vals = M[..., m]
    mean = vals.mean(-1, keepdims=True)
    q = np.quantile(vals, [0.1, 0.25, 0.5, 0.75, 0.9, 0.99], axis=-1).T
    return mean, np.concatenate([mean, q], -1)
