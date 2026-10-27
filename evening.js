// Evening core: Cell 0 writer (port of writer/cell0.py) + the ping reader (port of
// reader.py).  Runs in the browser and in node (for the numerical check against Python).
(function (root) {
  const N = 128, N2 = N * N, DT = 0.4, GAM = 0.02, ENVA = 0.02, DECAY = 0.0008,
    REGROW = 0.004, METAB = 0.0006, UPTAKE = 0.02, CAP = 0.25, V0 = 8, DEP = 0.08,
    R0 = 0.6, EMIT = 0.01, SIG_BLUR = 6;

  // Gaussian blur, sigma 6 cells, periodic: the same smoothing as cell0.py's FFT kernel
  const KR = 18, KER = new Float64Array(2 * KR + 1);
  (function () { let s = 0; for (let d = -KR; d <= KR; d++) { KER[d + KR] = Math.exp(-d * d / (2 * SIG_BLUR * SIG_BLUR)); s += KER[d + KR]; }
    for (let i = 0; i < KER.length; i++) KER[i] /= s; })();
  function gblur(src, dst, tmp) {
    for (let r = 0; r < N; r++) { const o = r * N;
      for (let c = 0; c < N; c++) { let s = 0; for (let d = -KR; d <= KR; d++) s += KER[d + KR] * src[o + ((c + d + N) % N)]; tmp[o + c] = s; } }
    for (let c = 0; c < N; c++)
      for (let r = 0; r < N; r++) { let s = 0; for (let d = -KR; d <= KR; d++) s += KER[d + KR] * tmp[((r + d + N) % N) * N + c]; dst[r * N + c] = s; }
  }

  function makeRng(seed) { let s = seed | 0 || 1;
    const u = () => { s = (s * 1664525 + 1013904223) | 0; return ((s >>> 8) & 0xffffff) / 0x1000000; };
    const g = () => { let a = 0; for (let i = 0; i < 6; i++) a += u(); return (a - 3) * Math.SQRT2; };
    return { u, g }; }

  class World {
    constructor(seed, ns = 2500) {
      const R = makeRng(seed); this.rng = R; this.NS = ns;
      this.psi = new Float64Array(N2); this.old = new Float64Array(N2); this.nxt = new Float64Array(N2);
      this.E = new Float64Array(N2); this.Eb = new Float64Array(N2); this.M = new Float64Array(N2);
      this.Rs = new Float64Array(N2).fill(R0); this.src = new Float64Array(N2); this.tmp = new Float64Array(N2);
      for (let i = 0; i < N2; i++) { this.psi[i] = R.g() * 1e-3; this.old[i] = this.psi[i]; }
      const f = k => new Float64Array(k);
      this.x = f(ns); this.y = f(ns); this.vx = f(ns); this.vy = f(ns); this.st = f(ns);
      this.w = f(ns); this.g = f(ns); this.fr = f(ns); this.ph = f(ns); this.alive = new Uint8Array(ns);
      for (let k = 0; k < ns; k++) {
        this.x[k] = R.u() * N; this.y[k] = R.u() * N; this.vx[k] = R.g() * .05; this.vy[k] = R.g() * .05;
        this.st[k] = 0.05; this.w[k] = 0.5 + R.u(); this.g[k] = R.u() * 6; // magnitudes; sign = mode
        this.fr[k] = 0.40 + R.u() * 0.20; this.ph[k] = R.u() * 2 * Math.PI; this.alive[k] = 1;
      }
      this.sign = 1; this.t = 0; this.step = 0;
    }
    stepOnce() {
      const { psi, old, nxt, E, Eb, M, Rs, src, NS } = this, dt2 = DT * DT, R = this.rng;
      const ix = new Int32Array(NS), iy = new Int32Array(NS);
      for (let k = 0; k < NS; k++) { ix[k] = Math.floor(this.x[k]) % N; iy[k] = Math.floor(this.y[k]) % N; }
      src.fill(0);
      for (let k = 0; k < NS; k++) if (this.alive[k]) src[ix[k] * N + iy[k]] += EMIT * Math.sin(this.fr[k] * this.t + this.ph[k]);
      for (let r = 0; r < N; r++) { const rn = ((r + 1) % N) * N, rp = ((r - 1 + N) % N) * N, o = r * N;
        for (let c = 0; c < N; c++) { const i = o + c;
          const l = psi[o + ((c + 1) % N)] + psi[o + ((c - 1 + N) % N)] + psi[rn + c] + psi[rp + c] - 4 * psi[i];
          nxt[i] = 2 * psi[i] - old[i] + dt2 * (l - V0 * M[i] * psi[i] + src[i]) - GAM * DT * (psi[i] - old[i]); } }
      this.old = psi; this.psi = nxt; this.nxt = old;
      const P = this.psi;
      for (let i = 0; i < N2; i++) E[i] += ENVA * (Math.abs(P[i]) - E[i]);
      if (this.step % 5 === 0) gblur(E, Eb, this.tmp);
      for (let i = 0; i < N2; i++) { const d = DECAY * M[i] * DT; M[i] -= d; Rs[i] += d; Rs[i] += REGROW * (R0 - Rs[i]) * DT; }
      const Msnap = M.slice();                         // cell0.py reads M once per step
      for (let k = 0; k < NS; k++) {
        const a = ix[k], b = iy[k];
        const gx = (E[((a + 1) % N) * N + b] - E[((a - 1 + N) % N) * N + b]) * 0.5;
        const gy = (E[a * N + ((b + 1) % N)] - E[a * N + ((b - 1 + N) % N)]) * 0.5;
        const sc = 1 / (Math.abs(gx) + Math.abs(gy) + 1e-6), gk = this.sign * this.g[k];
        this.vx[k] = (this.vx[k] + gk * gx * sc * DT * 0.2) * 0.96;
        this.vy[k] = (this.vy[k] + gk * gy * sc * DT * 0.2) * 0.96;
        const sp = Math.hypot(this.vx[k], this.vy[k]);
        if (sp > 0.6) { this.vx[k] *= 0.6 / sp; this.vy[k] *= 0.6 / sp; }
        this.vx[k] += R.g() * .006; this.vy[k] += R.g() * .006;
        this.x[k] = ((this.x[k] + this.vx[k] * DT * 4) % N + N) % N;
        this.y[k] = ((this.y[k] + this.vy[k] * DT * 4) % N + N) % N;
      }
      for (let k = 0; k < NS; k++) {
        const i = ix[k] * N + iy[k];
        if (this.alive[k]) { const take = Math.min(UPTAKE * DT * Rs[i], Math.max(CAP - this.st[k], 0)); Rs[i] -= take; this.st[k] += take;
          this.st[k] -= METAB * DT; }
      }
      for (let k = 0; k < NS; k++) {
        if (!this.alive[k]) continue;
        const i = ix[k] * N + iy[k];
        const drive = Math.min(Math.max(E[i] / (Eb[i] + 1e-12) - 1, 0), 3);
        const room = Math.max(1 - Msnap[i], 0);
        const put = Math.min(DEP * this.w[k] * drive * room * DT, 0.05 * Math.max(this.st[k], 0));
        this.st[k] -= put; M[i] += put;
      }
      for (let i = 0; i < N2; i++) if (M[i] > 1) M[i] = 1;
      for (let k = 0; k < NS; k++) if (this.alive[k] && this.st[k] <= 0) { this.alive[k] = 0; this.st[k] = 0; }
      this.t += DT; this.step++;
    }
  }

  // ---------------- reader ----------------
  const T1 = 150, SIGMA = 0.5;
  const PAIRS = []; for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) PAIRS.push([(16 + 32 * i) % N, (6 + 32 * j) % N]);

  function ping(M, src, rec, steps = T1, onFrame) {
    let psi = new Float64Array(N2), old = new Float64Array(N2), nxt = new Float64Array(N2);
    for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
      const dr = r - src[0], dc = c - src[1]; psi[r * N + c] = Math.exp(-(dr * dr + dc * dc) / (2 * SIGMA * SIGMA)); }
    old.set(psi);
    const out = new Float64Array(steps), dt2 = DT * DT;
    for (let t = 0; t < steps; t++) {
      for (let r = 0; r < N; r++) { const rn = ((r + 1) % N) * N, rp = ((r - 1 + N) % N) * N, o = r * N;
        for (let c = 0; c < N; c++) { const i = o + c;
          const l = psi[o + ((c + 1) % N)] + psi[o + ((c - 1 + N) % N)] + psi[rn + c] + psi[rp + c] - 4 * psi[i];
          nxt[i] = 2 * psi[i] - old[i] + dt2 * (l - V0 * M[i] * psi[i]) - GAM * DT * (psi[i] - old[i]); } }
      const s = old; old = psi; psi = nxt; nxt = s;
      out[t] = psi[rec[0] * N + rec[1]];
      if (onFrame) onFrame(psi, t);
    }
    return out;
  }

  // log band power, 12 log-spaced bands of omega in [0.3, 4], Hann window (reader.py/main.py spec)
  function spec(tr) {
    const n = tr.length, nf = Math.floor(n / 2) + 1, P = new Float64Array(nf);
    for (let k = 0; k < nf; k++) { let re = 0, im = 0;
      for (let t = 0; t < n; t++) { const w = 0.5 - 0.5 * Math.cos(2 * Math.PI * t / (n - 1)), a = -2 * Math.PI * k * t / n;
        re += tr[t] * w * Math.cos(a); im += tr[t] * w * Math.sin(a); }
      P[k] = re * re + im * im; }
    const e = []; for (let i = 0; i <= 12; i++) e.push(0.3 * Math.pow(4.0 / 0.3, i / 12));
    const out = [];
    for (let b = 0; b < 12; b++) { let s = 0, c = 0;
      for (let k = 0; k < nf; k++) { const om = k / (n * DT) * 2 * Math.PI; if (om >= e[b] && om < e[b + 1]) { s += P[k]; c++; } }
      out.push(Math.log(s / c + 1e-30)); }
    return out;
  }

  function read(M, onPair) {
    const feats = PAIRS.map(([r, c], k) => { const tr = ping(M, [r, c], [r, (c + 20) % N]); const f = spec(tr); if (onPair) onPair(k, tr); return f; });
    return feats[0].map((_, b) => feats.reduce((s, f) => s + f[b], 0) / feats.length);
  }

  const api = { N, World, ping, spec, read, PAIRS, T1 };
  if (typeof module !== 'undefined') module.exports = api; else root.Evening = api;
})(this);
