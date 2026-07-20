# Entropy-Cauchy fusion development screen

Validated runs: 70; endpoint replay checks: 140.
Selected candidate: `rank_union`; status: `frozen_unconfirmed`; manifest SHA-256: `2b6195cd152a126843d99053b4541e22829bd72c8ee45f648495220e5b82307f`.

| Rank | Method | Gate | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | rank_union | PASS | 0.873479 | 0.819614 | 0.335950 | 0.803475 | 1.25 |
| 2 | rank_mean | PASS | 0.872511 | 0.815711 | 0.338864 | 0.802809 | 2.75 |
| 3 | rank_cauchy | PASS | 0.872025 | 0.815388 | 0.337737 | 0.802245 | 3.25 |
| 4 | entropy | PASS | 0.871214 | 0.816901 | 0.375336 | 0.811938 | 3.75 |
| 5 | rank_min | FAIL | 0.870540 | 0.813222 | 0.344490 | 0.800135 | 5.00 |
| 6 | rank_max | FAIL | 0.868063 | 0.812039 | 0.355278 | 0.800692 | 5.75 |
| 7 | rank_bonferroni | FAIL | 0.865281 | 0.810588 | 0.372239 | 0.792573 | 7.00 |
| 8 | cauchy_all | FAIL | 0.860233 | 0.798534 | 0.354302 | 0.791412 | 7.25 |

LOSO selected paths: `{'entropy': 2, 'rank_mean': 2, 'rank_union': 10}`.
This is development-only evidence; any frozen fusion requires the reserved confirmation seeds.
