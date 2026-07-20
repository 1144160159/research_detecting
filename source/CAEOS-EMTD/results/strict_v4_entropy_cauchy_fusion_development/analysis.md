# Strict-v4 entropy-Cauchy fusion development analysis

Runs: 30; scenario blocks: 18; endpoint replay checks: 60.
All previously opened strict-v4 results are development evidence. This report does not freeze a confirmation claim.
Development-selected candidate: `cauchy_all`; eligible: 1.

| Method | Eligible | AUROC | AUPR | FPR95 oriented | OSCR | Worst suite-metric | Worst LOSO-metric |
|---|---:|---:|---:|---:|---:|---:|---:|
| cauchy_all | true | +0.012877 | +0.020095 | +0.115397 | +0.034419 | +0.012592 | +0.008757 |
| rank_cauchy | false | +0.001253 | +0.003204 | +0.110753 | +0.036758 | -0.003161 | -0.004917 |
| rank_max | false | -0.000001 | +0.007530 | +0.112763 | +0.025398 | -0.005979 | -0.005955 |
| rank_bonferroni | false | -0.007149 | +0.006229 | +0.060089 | +0.003746 | -0.012622 | -0.013501 |
| rank_union | false | -0.001971 | -0.009939 | +0.107230 | +0.036728 | -0.020710 | -0.018323 |
| rank_mean | false | -0.015060 | -0.033981 | +0.089693 | +0.034378 | -0.060808 | -0.044032 |
| rank_min | false | -0.037497 | -0.050059 | +0.048944 | +0.024712 | -0.086668 | -0.061013 |
| entropy | false | -0.066609 | -0.068506 | +0.031615 | +0.007182 | -0.109472 | -0.079847 |
