// Do worlds written by the JS port look like Python's to the frozen reader?
// Writes 6 worlds per order arm with evening.js, reads them, saves features + quantiles.
const E = require('./evening.js'), fs = require('fs');
const out = [];
for (const arm of [0, 1]) for (let s = 0; s < 6; s++) {
  const w = new E.World(9001 + 100 * arm + s);
  w.sign = arm === 0 ? 1 : -1;
  for (let t = 0; t < 4000; t++) { if (t === 2000) w.sign = -w.sign; w.stepOnce(); }
  const M = w.M, sorted = Float64Array.from(M).sort();
  const q = [.1, .25, .5, .75, .9, .99].map(p => sorted[Math.floor(p * (M.length - 1))]);
  out.push({ arm, feat: E.read(M), q, mean: M.reduce((a, b) => a + b, 0) / M.length });
  console.log('arm', arm, 'world', s, 'mean', out[out.length - 1].mean.toFixed(4), 'q99', q[5].toFixed(3));
}
fs.writeFileSync('results/js_worlds.json', JSON.stringify(out));
