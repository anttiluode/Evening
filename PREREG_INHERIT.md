# Pre-registration 2 — does the read–write loop carry a bit across generations?

Frozen before `inherit_run.py` runs. Development (seeds 900000+, two worlds per p, the
table below) was used to design it.

## The loop (`inherit.py`)

A population of Cell 0 scouts writes for 4000 steps. A fraction p runs the seek-first
schedule, the rest avoid-first; nothing else differs. The scouts are removed. 64 reading
sites on an 8 × 8 grid each fire one local ping (σ = 0.5, receiver 20 cells along x,
150-step window). A fixed receptor — nearest centroid on z-scored log band power,
trained once on single-pair features of the 48 confirmatory order worlds of
PREREG.md (training accuracy 0.876) — turns each site's spectrum into seek-first or
avoid-first. A fresh world, fresh scouts, blank material: child i takes site i mod 64's
decision. **No genome is copied.** The only channel from one generation to the next is
material → ping → receptor.

Development map (p → p′, two worlds each): 0 → 0.11, 0.11 · 0.25 → 0.92, 0.84 ·
0.5 → 1.00, 0.98 · 0.75 → 0.98, 1.00 · 1 → 0.89, 0.78.

## What would count as heredity

The generation map f(p) has a stable fixed point near p ≈ 0.9 (seek-first). Heredity —
a lineage remembering its ancestors — requires a **second** stable state on the
avoid-first side. With one attractor, every lineage converges to the same state
whatever its ancestry: a contraction, the failure Sunday measured on Aug 31.

## Runs (fresh seeds)

- **Map:** p ∈ {0, .05, .10, .15, .20, .25, .5, .75, .9, 1}, 4 worlds each, individual
  receptor (quorum readout also computed from the same reads).
- **Lineages:** 8 lineages from p₀ = 0 and 8 from p₀ = 1, 8 generations each, in two
  arms: **individual** (each site's decision used as read) and **quorum** (each site
  adopts the majority of its 3 × 3 neighbourhood of sites; a designed amplifier,
  reported separately, never counted as emergent).

## Predictions (Claude's, stated before the run)

- **H1 (map):** f(0) ≤ 0.2 and f(0.5) ≥ 0.8 — the avoid-first signature is fragile.
- **H2 (individual arm, the main question):** NO heredity. Fewer than 6 of 8 p₀ = 0
  lineages are still below 0.5 at generation 8, while ≥ 6 of 8 p₀ = 1 lineages are above
  0.5. Reason: the dev map rises from 0.11 to ~0.88 between p = 0 and 0.25, and a stable
  low fixed point needs f(p) < p in that interval, which looks unlikely.
- **H3 (quorum arm):** heredity — ≥ 6 of 8 lineages on each side stay on their own side
  at generation 8. The majority vote pushes f(0) ≈ 0.11 down towards 0.

## Decision rule

**Heredity in an arm** = ≥ 6 of 8 p₀ = 0 lineages below 0.5 AND ≥ 6 of 8 p₀ = 1
lineages above 0.5, at generation 8. Reported per arm. If the individual arm shows
heredity, H2 is wrong and the medium itself carries the bit — the result this repo
would most like to have, and the one it predicts against.
