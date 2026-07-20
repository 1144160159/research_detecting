# Strict-v4 robust pseudo-unknown development

State: **frozen_unconfirmed**; runs: 18.
Selected alpha: `0.5`; minimum fold gain: `-0.125`.
Endpoint counts: `{'pseudo_unknown_learned_blend': 9, 'cauchy_modality_support_union': 9}`.
Prior failed confirmation outcomes are development evidence for this new policy.

| Cohort / suite | AUROC | AUPR | FPR95 oriented | OSCR |
|---|---:|---:|---:|---:|
| original_development/cic_ton_iot | +0.025579 | +0.025213 | +0.015145 | +0.032578 |
| original_development/cic_iot2023 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| failed_confirmation/cic_ton_iot | +0.003995 | +0.006574 | +0.003520 | +0.003740 |
| failed_confirmation/cic_iot2023 | +0.039909 | +0.016900 | +0.104332 | +0.057226 |

Frozen candidate: **true**.
Manifest: `ce2d1c98988cadb09c6ac04851fa3c20712b45ef88c95cf835bf348d50640c84`.
