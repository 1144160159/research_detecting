# Strict-v4 pairwise boundary pseudo-unknown confirmation

State: **confirmed**; runs: 12; scenario blocks: 6.
Endpoint counts: `{'cauchy_modality_support_union': 7, 'pseudo_unknown_learned_blend': 5}`.

| Metric | Reference | Candidate | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.701935 | 0.701935 | +0.000000 | [+0.000000, +0.000000] | 0/6/0 | NA |
| unknown_auroc | 0.799028 | 0.801085 | +0.002057 | [+0.000195, +0.004528] | 3/3/0 | 1 |
| unknown_aupr | 0.562558 | 0.565154 | +0.002596 | [-0.001045, +0.008179] | 2/3/1 | 1 |
| unknown_fpr95 | 0.518136 | 0.474451 | +0.043685 | [-0.002288, +0.105536] | 2/3/1 | 1 |
| oscr | 0.558342 | 0.565010 | +0.006668 | [+0.000749, +0.016647] | 3/3/0 | 1 |
| known_acceptance_rate | 0.946833 | 0.948806 | +0.001973 | [-0.000630, +0.005984] | 2/3/1 | NA |
| unknown_rejection_rate | 0.292262 | 0.295450 | +0.003188 | [-0.013000, +0.025063] | 1/3/2 | NA |

Frozen gate: **PASS**.
