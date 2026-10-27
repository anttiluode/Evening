"""Apply PREREG.md to results/main.json."""
import json

r = json.load(open('results/main.json'))
o, c = r['order'], r['recency']
best_scalar = max(o['global_mean'], o['union_mean'])
D = {
    'P1': o['ping16'] >= 0.90 and o['ping16_p'] < 0.01,
    'P2': (o['global_mean'] <= 0.70 and o['union_mean'] <= 0.70
           and o['ping16'] - best_scalar >= 0.20),
    'P3': o['ping8'] >= 0.85,
    'P4': c['ping16'] >= 0.75 and c['ping16_p'] < 0.05 and c['global_mean'] <= 0.70,
    'P5': o['surrogate_ping16'] >= 0.85,
    'R1': o['god_quantiles'] >= o['god_radial_shape'],
    'KILL': o['ping16'] <= best_scalar + 0.10,
}
json.dump(D, open('results/decisions.json', 'w'), indent=1)
print(json.dumps(D, indent=1))
