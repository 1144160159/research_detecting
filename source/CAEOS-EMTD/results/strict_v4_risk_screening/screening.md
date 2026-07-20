# Strict-v4 fixed-risk development screening

Runs: 6; fixed risks: 46.
Development screening uses unknown test labels and is not confirmation.
Manifest: `ebbc535d5f80f698197a1ed90f0cf241e4cdd767b1517a4ca99179ebb0ca507e`.

| Suite | Candidate | AUROC | AUPR | FPR95 oriented | OSCR | LOSO paths |
|---|---|---:|---:|---:|---:|---|
| cic_iot2023 | conflict_augmented | +0.066662 | +0.145631 | +0.120911 | +0.041470 | {'cauchy_distance_lof': 1, 'conflict_augmented': 2} |
| cic_ton_iot | cauchy_all | +0.056169 | +0.047961 | +0.144775 | +0.055775 | {'cauchy_all': 2, 'cauchy_evidence': 1} |

Candidates may only be evaluated on the disjoint scenarios and seeds in the frozen manifest.
