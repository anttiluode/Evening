"""Apply PREREG_INHERIT.md and draw the figure."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

mp = json.load(open('results/inherit_map.json'))
arms = {a: json.load(open(f'results/inherit_{a}.json'))['lineages'] for a in ('indiv', 'quorum')}
P = sorted({r['p'] for r in mp['map']})
f = {p: [r['p_next'] for r in mp['map'] if r['p'] == p] for p in P}
fq = {p: [r['p_next_quorum'] for r in mp['map'] if r['p'] == p] for p in P}

out = dict(receptor_train_acc=mp['receptor_train_acc'],
           map={str(p): dict(mean=float(np.mean(f[p])), sd=float(np.std(f[p])), quorum_mean=float(np.mean(fq[p])))
                for p in P})
out['H1'] = bool(np.mean(f[0.0]) <= 0.2 and np.mean(f[0.5]) >= 0.8)
for a, rows in arms.items():
    lo = [r['traj'][-1] for r in rows if r['p0'] == 0.0]
    hi = [r['traj'][-1] for r in rows if r['p0'] == 1.0]
    n_lo, n_hi = int(sum(x < 0.5 for x in lo)), int(sum(x > 0.5 for x in hi))
    out[a] = dict(p0_0_below_half=n_lo, p0_1_above_half=n_hi, heredity=bool(n_lo >= 6 and n_hi >= 6),
                  final_p0_0=lo, final_p0_1=hi)
out['H2_no_heredity_individual'] = not out['indiv']['heredity']
out['H3_heredity_quorum'] = out['quorum']['heredity']
json.dump(out, open('results/inherit_decisions.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'map'}, indent=1))
print({p: round(out['map'][str(p)]['mean'], 3) for p in P})

fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
m = [np.mean(f[p]) for p in P]; s = [np.std(f[p]) for p in P]
ax[0].errorbar(P, m, yerr=s, fmt='o-', color='k', label="individual receptor")
ax[0].plot(P, [np.mean(fq[p]) for p in P], 's--', color='#888', label='quorum readout (same reads)')
ax[0].plot([0, 1], [0, 1], ':', color='#c33', label="p' = p")
for p in P:
    ax[0].scatter([p] * len(f[p]), f[p], s=8, color='k', alpha=0.4)
ax[0].set_xlabel('parents: fraction seek-first p'); ax[0].set_ylabel("children: fraction p'")
ax[0].set_title('Generation map'); ax[0].legend(fontsize=8)
for k, (a, title) in enumerate((('indiv', 'Lineages, individual receptor'), ('quorum', 'Lineages, quorum (designed amplifier)'))):
    for r in arms[a]:
        ax[k + 1].plot(r['traj'], color='#d08c3a' if r['p0'] == 1.0 else '#4f8fb0', alpha=0.7)
    ax[k + 1].axhline(0.5, color='k', lw=0.6, ls=':')
    ax[k + 1].set_ylim(-0.03, 1.03); ax[k + 1].set_xlabel('generation'); ax[k + 1].set_ylabel('fraction seek-first')
    ax[k + 1].set_title(title)
plt.tight_layout(); plt.savefig('results/inherit.png', dpi=110)
