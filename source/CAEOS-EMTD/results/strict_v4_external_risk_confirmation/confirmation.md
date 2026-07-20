# Strict-v4 external-risk confirmation

State: **confirmed**; runs: 12; scenario blocks: 6.

| Metric | Base CAEOS | Fused CAEOS | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.729267 | 0.729267 | +0.000000 | [+0.000000, +0.000000] | 0/6/0 | NA |
| unknown_auroc | 0.747864 | 0.766443 | +0.018579 | [+0.003594, +0.034816] | 5/0/1 | 0.125 |
| unknown_aupr | 0.499260 | 0.519460 | +0.020200 | [+0.007340, +0.033303] | 5/0/1 | 0.125 |
| unknown_fpr95 | 0.565273 | 0.503131 | +0.062142 | [+0.033212, +0.091649] | 6/0/0 | 0.125 |
| oscr | 0.550608 | 0.570219 | +0.019611 | [+0.009581, +0.031127] | 6/0/0 | 0.125 |
| known_acceptance_rate | 0.948348 | 0.951644 | +0.003297 | [+0.001365, +0.005255] | 5/0/1 | NA |
| unknown_rejection_rate | 0.166122 | 0.238230 | +0.072109 | [-0.010225, +0.209359] | 3/0/3 | NA |

Frozen gate: **PASS**.
A failed gate rejects this frozen fusion without post-confirmation retuning.
