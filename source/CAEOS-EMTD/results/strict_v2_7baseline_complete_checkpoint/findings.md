# Strict-v2 seven-baseline complete checkpoint

This checkpoint uses all 190 CAEOS runs, 38 scenario inference units, five seeds,
and the seven fully completed strong/legacy methods: Open-Detect, SIEVE, ARPL,
CLOSR, CADE, RoNeTC, and FOSS. It excludes the still-running modern matrix and
the queued classical OOD matrix, so it does not replace the final 20/24-baseline
claim.

The strict input audit is `complete`: CAEOS gate 190/190, strong baselines
380/380, legacy baselines 950/950, and zero failure markers. The older strong
manifest has no explicit state field, so compatibility is accepted only after
checking its exact experiment count, completed/failed/skipped counters, and all
380 per-run statuses; its effective state is `legacy_inferred_complete`.

| Metric | CAEOS | Strongest baseline | Oriented delta | 95% CI | Holm p | Confirmed |
|---|---:|---|---:|---:|---:|---:|
| AUROC | 0.839183 | Open-Detect | +0.113594 | [0.059264, 0.171714] | 0.000705 | yes |
| AUPR | 0.737376 | Open-Detect | +0.149956 | [0.096336, 0.204610] | 0.000041 | yes |
| FPR95 | 0.401565 | Open-Detect | +0.144956 | [0.044228, 0.242624] | 0.019793 | yes |
| OSCR | 0.755264 | Open-Detect | +0.117611 | [0.071625, 0.164409] | 0.000055 | yes |
| Known macro-F1 | 0.877701 | Open-Detect | +0.041226 | [0.032691, 0.050310] | 2.55e-10 | yes |

CAEOS ranks first on all five metrics globally and separately on Edge-IIoT,
NF-CSE, and USTC-TFC2016. The preregistered gate therefore permits a
comprehensive SOTA claim within this seven-baseline checkpoint. Suite-wise
significance is reported but is not uniformly attainable after family-wise
correction, especially for the ten-scenario USTC suite.

The next decision boundary remains the frozen 20-baseline finalization, followed
by the 24-baseline extended finalization. Any modern or classical method that
breaks a mean-rank or global significance gate closes the comprehensive claim.
