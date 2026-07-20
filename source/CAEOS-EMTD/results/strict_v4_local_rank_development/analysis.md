# Strict-v4 local-rank pseudo-unknown development

State: **frozen_unconfirmed**; runs: 30.
Policy: bins `5`, beta `1.0`, minimum fold gain `-0.05`.
Endpoint counts: `{'pseudo_unknown_local_rank_blend': 6, 'cauchy_modality_support_union': 24}`.

| Cohort / suite | AUROC | AUPR | FPR95 oriented | OSCR |
|---|---:|---:|---:|---:|
| old_development/cic_ton_iot | +0.011282 | +0.012157 | +0.002819 | +0.014788 |
| old_development/cic_iot2023 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| old_confirmation/cic_ton_iot | +0.004195 | +0.005407 | +0.006512 | +0.003350 |
| old_confirmation/cic_iot2023 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| robust_confirmation/cic_ton_iot | +0.005104 | +0.009432 | +0.045602 | +0.011578 |
| robust_confirmation/cic_iot2023 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |

Frozen candidate: **true**.
Manifest: `8c1329ab3e7b0cc3279dd8d428555c33a2fa7db824db6a7b74fe814d3afaade5`.
