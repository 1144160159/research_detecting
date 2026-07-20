# Strict-v2 Edge exhaustive risk findings

## Scope and validity

- Source: 70 frozen strict-v2 CAEOS runs, covering 14 Edge-IIoT leave-one-attack scenarios and seeds `7/11/19/23/37`.
- Inference unit: scenario. The five seed repeats are averaged inside each scenario.
- Coverage: the confirmed risk plus all 43 alternative fixed reports saved by every run.
- Multiplicity: one Holm family over 43 comparisons times 4 unknown-detection metrics, for 172 hypotheses.
- Leakage guard: runtime risk selection, preprocessing, calibration and thresholds use no unknown or test labels. This exhaustive comparison is development analysis and therefore cannot replace reserved-seed confirmation.

## Main result

No alternative fixed risk is significantly better than the confirmed `cauchy_modality_support_union` under the 172-hypothesis family. The current method is itself significantly better than multiple weak component and single-view risks after the same correction.

However, the confirmed method is not the numerical optimum of the development matrix. `entropy` improves all four scenario means relative to the confirmed risk:

| Metric | Confirmed | Entropy | Directed entropy gain | 95% scenario-block CI | Holm p |
|---|---:|---:|---:|---:|---:|
| AUROC | 0.836599 | 0.871214 | +0.034615 | [-0.076788, +0.110230] | 1.000000 |
| AUPR | 0.733479 | 0.816901 | +0.083422 | [-0.022569, +0.177900] | 1.000000 |
| FPR95 | 0.517759 | 0.375336 | +0.142424 | [-0.066435, +0.329732] | 1.000000 |
| OSCR | 0.764639 | 0.811938 | +0.047299 | [-0.051763, +0.118255] | 1.000000 |

`cauchy_all` is the second Pareto candidate and also improves all four means, most strongly FPR95 by 0.163458, but none of these differences survives the full Holm family. This supports the frozen confirmation order `rank_union -> entropy -> confirmed risk`; it does not authorize replacing the confirmed risk before seeds `67/71/73/79` are evaluated.

## Modality evidence

Single-view KNN risks are substantially weaker than the confirmed multi-evidence risk. Relative to `knn_view_0`, the confirmed method improves AUROC by 0.335987, AUPR by 0.347057 and OSCR by 0.686682; all three remain significant after the 172-test Holm correction. Relative to `knn_view_2`, the corresponding gains are 0.322480, 0.359549 and 0.700855, also Holm-significant. `knn_view_1` is stronger than the other isolated views, but the confirmed method still improves OSCR by 0.223381 with Holm significance.

This provides formal evidence that no single modality explains the confirmed result. It does not prove that the current fusion rule is optimal, because entropy and `cauchy_all` remain numerically stronger development candidates.

## Component interpretation

- The confirmed union is clearly better than raw conflict, distance-only, isolated modality KNN and several local-support variants.
- Against `baseline`, `cauchy_all`, `msp` and entropy, the differences are heterogeneous across scenarios and do not survive the exhaustive family correction.
- The mechanism evidence therefore supports multi-evidence robustness over weak components, while the final choice of open-set risk remains unresolved.
- A calibration-before/after contrast must be regenerated after the final risk is selected, using the same ranking score with only its known-validation calibrator toggled. Existing fixed reports mix score definitions and cannot isolate calibration causally.

## Decision

Keep `cauchy_modality_support_union` as the confirmed reference until reserved-seed results exist. Select the final internal risk only through the pre-registered decision tree. After selection, rerun this exhaustive analysis with the selected method as the reference and add the calibration-only contrast before using the ablation as final paper evidence.
