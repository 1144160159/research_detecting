# Validation-adaptive entropy/Cauchy fusion gate

Development-selected rule: `entropy_if_corr_ge_0.8_and_mad_ge_0.11`.
Decision: `rejected_development_candidate`; freeze candidate: `False`.

| Evidence | AUROC | AUPR | FPR95 | OSCR |
|---|---:|---:|---:|---:|
| Development mean | 0.875443 | 0.821011 | 0.360063 | 0.811803 |
| LOSO oriented delta vs entropy | -0.000682 | -0.002858 | +0.020087 | -0.003769 |

The adaptive rule is rejected unless every LOSO oriented metric is non-negative.
