"""Gate 0 for the reader.

G0a  the copied Cell 0 is unchanged and still conserves its budget.
G0b  causal footprint: replace everything OUTSIDE footprint(t1) + margin with a
     different world's material; the receiver trace up to t1 must not change beyond a
     tolerance.  The explicit stencil spreads 1 cell/step (2.5 c), so exponentially
     small precursors are expected; the margin that holds them under 1e-6 of the
     trace's peak is measured here and frozen in PREREG.md.
G0c  stability with the sharp pulse (sigma 0.5) on the densest material map.
"""
import json, sys
import numpy as np
sys.path.insert(0, 'writer')
import reader as R
from cell0 import World
from signature import CFG

out = {}
# G0a
w = World(seed=7, g_lo=0.0, g_hi=1.0, **CFG)
tot0 = w.total()
w.run(1500)
resid = w.total() - (tot0 + w.regrown - w.burned)
out['G0a_budget_residual_rel'] = float(abs(resid) / tot0)
print('G0a budget residual', out['G0a_budget_residual_rel'])

# G0b
R.SIGMA = 0.5
d = np.load('results/dev_order.npz')
M = d['M']
A, B = M[0], M[-1]
rows = []
for t1 in (100, 150):
    for margin in (0.0, 4.0, 8.0, 12.0):
        inside = R.footprint(t1, margin)
        H = np.where(inside, A, B)
        tr = R.ping(np.stack([A, H]), steps=t1)
        rel = float(np.abs(tr[0] - tr[1]).max() / np.abs(tr[0]).max())
        rows.append(dict(t1=t1, margin=margin, rel_diff=rel, area_frac=float(inside.mean())))
        print(f'G0b t1={t1} margin={margin:4.1f}  max|diff|/peak = {rel:.2e}  area {inside.mean():.3f}')
# sanity: a swap INSIDE the footprint must change the trace a lot
inside = R.footprint(150, 8.0)
H = np.where(inside, B, A)
tr = R.ping(np.stack([A, H]), steps=150)
out['G0b_inside_swap_rel'] = float(np.abs(tr[0] - tr[1]).max() / np.abs(tr[0]).max())
print('G0b control: swapping the inside changes the trace by', out['G0b_inside_swap_rel'])
out['G0b'] = rows

# G0c
dense = M[np.argmax(M.mean((1, 2)))]
tr = R.ping(dense[None], steps=400)
out['G0c_max_abs_400'] = float(np.abs(tr).max())
out['G0c_finite'] = bool(np.isfinite(tr).all())
print('G0c finite', out['G0c_finite'], 'max', out['G0c_max_abs_400'])
json.dump(out, open('results/gate0.json', 'w'), indent=1)
