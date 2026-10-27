# Pre-registration — can a wave read a history that scouts wrote?

Frozen before any confirmatory world is generated. Everything before this file
(development worlds, seeds 50000–51005 and 60000–61005) was used to design the reader.

## Background

On Aug 31 (BlackBoxLab, `Claude/order.py`, `recency.py`) Cell 0 scouts wrote material
whose final map separated two histories that had **matched totals**: seek-then-avoid
vs avoid-then-seek (order), and seek-then-avoid vs avoid-throughout (recency). Mean
material was at chance. But the separation was measured by looking at the whole map
— a god's-eye reader. The named next gate was "it needs a READER".

WallMemoryLaw (Oct 27) built a reader for wall memories: a ping, a listening window,
and a footprint known from geometry. This repo joins them: **can a ping through the
frozen material tell which history wrote it?**

## Frozen setup

- **Writer:** `writer/cell0.py` and `writer/signature.py` copied unchanged from
  BlackBoxLab (Aug 31), same CFG. Order arms T = 4000 with a flip at 2000; recency arms
  2000 + 6000. Scouts discarded after writing.
- **Confirmatory worlds:** order 24 per arm, seeds 70000+ / 71000+; recency 16 per arm,
  seeds 80000+ / 81000+. None generated before this file is committed.
- **Reader** (`reader.py`): Cell 0's own field with the material frozen and the scouts
  removed (c = 1, dt = 0.4, V₀ = 8, γ = 0.02), on the same 128² torus. Gaussian ping with
  σ = 0.5, released at rest. **16 source–receiver pairs**: source (16 + 32i, 6 + 32j),
  receiver 20 cells along x; i, j ∈ 0…3, pair k = 4i + j. Window 150 steps.
- **Features:** log power in 12 log-spaced bands of ω ∈ [0.3, 4.0] (Hann window),
  averaged over the pairs used. Classifier: leave-one-out nearest centroid on z-scored
  features, the same as Aug 31. Permutation p from 2000 label shuffles.
- **Footprint** (Gate 0): a window ending at step t₁ hears only material with
  d(src, x) + d(x, rec) ≤ c·t₁·dt + 4 cells; outside it the trace changes by ≤ 1.2e-8 of
  its peak (`results/gate0.json`).

## Predictions

- **P1 (order, 16 pairs):** ping LOO ≥ 0.90 and permutation p < 0.01.
- **P2 (the scalar attacker):** global mean material LOO ≤ 0.70, and mean material inside
  the union of the 16 footprints LOO ≤ 0.70. Ping LOO exceeds both by ≥ 0.20.
- **P3 (smaller arrays, order):** 8 pairs (j ∈ {0, 2}) LOO ≥ 0.85. 1 pair (k = 0) is
  reported, with no prediction.
- **P4 (recency, 16 pairs):** ping LOO ≥ 0.75 with p < 0.05, and global mean LOO ≤ 0.70.
- **P5 (what it reads, order):** on phase-randomised surrogates (same power spectrum and
  same value histogram, arrangement destroyed; `cell0.surrogate`, one per world), the
  16-pair ping still separates the arms with LOO ≥ 0.85, i.e. the reader reads the
  material's statistics, not its specific layout. Pixel-shuffled maps (histogram only)
  are reported, with no prediction.
- **R1 (correction to Aug 31):** on the god's-eye side, quantiles alone separate the
  order arms at least as well as the radial spectrum shape alone. Development: 1.00 vs
  0.79. If this holds, Aug 31's "the record is in the arrangement, not the amount"
  should read "the record is in how the amount is distributed".

## Kill condition

If at 16 pairs the ping LOO is ≤ the better scalar attacker + 0.10 on the order arms,
the ping is not a reader of this history, and the README says so.

## Not claimed in advance

That the reader reads arrangement. P5 predicts it does not need it. Nor inheritance:
reading is the precondition for a reader that writes back.
