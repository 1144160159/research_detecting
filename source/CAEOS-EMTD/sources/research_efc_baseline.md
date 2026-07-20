# Energy-based Flow Classifier baseline evidence

Checked: 2026-07-17.

## Primary sources

- Official implementation: https://github.com/EnergyBasedFlowClassifier/EFC-package
- Pinned upstream commit: `2b935be347abf7daf4420989ef391436db418eac`
- Open-set paper: Manuela M. C. Souza et al., "A novel open set Energy-based Flow Classifier for Network Intrusion Detection," Computers & Security 157 (2025), 104569. DOI: https://doi.org/10.1016/j.cose.2025.104569
- Original flow-classifier paper: Camila F. T. Pontes et al., "A New Method for Flow-Based Network Intrusion Detection Using the Inverse Potts Model," IEEE Transactions on Network and Service Management 18(2), 2021. DOI: https://doi.org/10.1109/TNSM.2021.3075503
- Official API documentation: https://efc-package.readthedocs.io/en/latest/generated/efc.EnergyBasedFlowClassifier.html

## Relevance decision

EFC is a domain-specific, flow-level, multiclass open-set intrusion classifier with an official BSD-3-Clause Python implementation. Unlike packet-image, raw-packet-sequence, graph, and LLM traffic methods, its input contract matches the strict-v2 tabular flow features without changing the information available to CAEOS or the other baselines.

The official multiclass decision predicts the class with minimum energy and rejects it when that energy exceeds the selected class model's training cutoff. The strict adapter retains that statistic as `minimum_energy - predicted_class_cutoff`, but selects the main operating threshold from known-validation only so all methods use the same leakage-free threshold protocol. The author's native zero-margin cutoff is retained as an auxiliary report.

## Admission gate

Run three seed-7 scenarios first: Edge-IIoT fingerprinting, NF-CSE bot, and USTC-TFC2016 Geodo. Expand to the 190-task strict-v2 matrix only if all artifacts and split fingerprints pass, no run fails, metrics are finite, and the method provides a non-redundant domain-specific comparison. A weak pilot may still be reported as a negative protocol-aligned baseline but should not consume a full matrix budget.
