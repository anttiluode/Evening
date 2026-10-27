import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
r = json.load(open('results/main.json')); o, c = r['order'], r['recency']
fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
labels = ['1 ping', '8 pings', '16 pings', 'mean material\n(attacker)', '16 pings on\nscrambled maps']
ov = [o['ping1'], o['ping8'], o['ping16'], o['global_mean'], o['surrogate_ping16']]
cv = [c['ping1'], c['ping8'], c['ping16'], c['global_mean'], np.nan]
x = np.arange(len(labels)); w = 0.38
ax[0].bar(x - w/2, ov, w, label='order (seek→avoid vs avoid→seek), 48 worlds', color='#d08c3a')
ax[0].bar(x + w/2, cv, w, label='recency (seek→avoid vs avoid throughout), 32 worlds', color='#4f8fb0')
ax[0].axhline(0.5, color='k', lw=0.8, ls=':'); ax[0].set_xticks(x); ax[0].set_xticklabels(labels, fontsize=9)
ax[0].set_ylim(0, 1.05); ax[0].set_ylabel('leave-one-out accuracy'); ax[0].legend(fontsize=8, loc='lower left')
ax[0].set_title('Can a ping tell which history wrote the material?')
S = np.load('results/spec_order.npy').mean(0); y = np.load('results/worlds_order.npz')['y']
e = np.geomspace(0.3, 4.0, 13); cen = np.sqrt(e[:-1] * e[1:])
for cls, col, lab in ((0, '#d08c3a', 'seek→avoid'), (1, '#4f8fb0', 'avoid→seek')):
    for s in S[y == cls]: ax[1].plot(cen, s, color=col, alpha=0.15, lw=0.8)
    ax[1].plot(cen, S[y == cls].mean(0), color=col, lw=2.5, label=lab)
ax[1].set_xscale('log'); ax[1].set_xlabel('ω (band centre)'); ax[1].set_ylabel('log power heard (16-pair mean)')
ax[1].set_title('What the receivers hear (order arms, every world)'); ax[1].legend(fontsize=9)
plt.tight_layout(); plt.savefig('results/evening.png', dpi=110); print('saved')
