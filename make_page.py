"""Inject the confirmatory reader (centroids, z-scoring) and the results table into index.html."""
import json
import numpy as np

S = np.load('results/spec_order.npy').mean(0)            # (48, 12): 16-pair mean features
y = np.load('results/worlds_order.npz')['y']
r = json.load(open('results/main.json'))
D = json.load(open('results/decisions.json'))
e = np.geomspace(0.3, 4.0, 13)
o, c = r['order'], r['recency']
yes = lambda b: 'pass' if b else '<b>fail</b>'
html = f"""<h2 style="font-size:17px;margin:0 0 4px">Pre-registered result (48 + 32 fresh Python worlds)</h2>
<table>
<tr><th>reader</th><th>order: seek→avoid vs avoid→seek</th><th>recency: seek→avoid vs avoid throughout</th></tr>
<tr><td>16 pings, spectrum</td><td>{o['ping16']:.3f}</td><td>{c['ping16']:.3f}</td></tr>
<tr><td>8 pings</td><td>{o['ping8']:.3f}</td><td>{c['ping8']:.3f}</td></tr>
<tr><td>1 ping</td><td>{o['ping1']:.3f}</td><td>{c['ping1']:.3f}</td></tr>
<tr><td>mean material (the attacker)</td><td>{o['global_mean']:.3f}</td><td>{c['global_mean']:.3f}</td></tr>
<tr><td>16 pings on phase-scrambled maps</td><td>{o['surrogate_ping16']:.3f}</td><td>—</td></tr>
</table>
<p>Leave-one-out accuracy; 0.5 is chance. Decisions: P1 {yes(D['P1'])}, P2 {yes(D['P2'])}, P3 {yes(D['P3'])},
P4 {yes(D['P4'])}, P5 {yes(D['P5'])}, R1 {yes(D['R1'])}; kill condition {'fired' if D['KILL'] else 'did not fire'}.
Full ledger in the <a style="color:#e8e4dc" href="https://github.com/anttiluode/Evening">README</a>.
The page's writer is a JavaScript port with its own random numbers; how well the Python-trained reader
classifies its worlds is measured separately (README, "the page").</p>"""
model = dict(c0=S[y == 0].mean(0).tolist(), c1=S[y == 1].mean(0).tolist(),
             mu=S.mean(0).tolist(), sd=(S.std(0) + 1e-12).tolist(),
             centres=np.sqrt(e[:-1] * e[1:]).tolist(), html=html)
page = open('index.html').read()
start = page.index('const MODEL = ') + len('const MODEL = ')
end = page.index(';', start)
page = page[:start] + json.dumps(model) + page[end:]
open('index.html', 'w').write(page)
print('injected')
