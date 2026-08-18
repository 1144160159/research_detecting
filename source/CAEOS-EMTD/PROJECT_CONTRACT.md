# CAEOS-EMTD Project Contract

Version: `caeos_delivery_contract_v1`  
Frozen: 2026-07-29

The machine-readable source of truth is
`contracts/caeos_delivery_contract_v1.json`. Code must load it through
`project_contract`; experiment scripts must not redefine the gates with
local constants.

## Delivery lines

| Line | Representation | Mandatory acceptance |
|---|---|---|
| Engineering | Existing flow statistics, packet-length sequence, and inter-arrival sequence are allowed | `engineering_safety_95_5` |
| Paper | Statistical or temporal backbone plus payload semantics, communication graph, or application behavior | `paper_full_open_set_95_5`, three-layer metrics, modality/conflict ablations |

Passing the engineering line does not establish the paper line. A feature
grouping of one flow table is not automatically a heterogeneous multimodal
method.

## Metric layers

1. Known classification: Known Macro-F1, Known Balanced Accuracy, per-class
   recall, and Benign FPR.
2. Unknown detection: AUROC-Out, AUPR-Out,
   `FPR_known@95TPR_unknown`, and Unknown-F1 at the frozen threshold.
3. Joint open set: exact OSCR, known acceptance, and unknown rejection.

Known-ECE15, Known-Brier, and Known-NLL are supplemental and require a valid
K-class probability matrix. Risk ranks are not probabilities.

## Safety gates

The engineering gate requires all six conditions:

- Alert Accuracy `>= 0.95`;
- Alert Precision `>= 0.95`;
- Attack Recall over known and unknown attacks `>= 0.95`;
- Benign FPR `< 0.05`;
- Known attack type Accuracy `>= 0.95`;
- Unknown attack alert Recall `>= 0.95`.

The paper full-open-set gate adds Unknown label Recall `>= 0.95`.
Missing metrics fail closed. Formal claims also require the one-sided
scenario-blocked confidence bounds defined in the contract.

## Execution boundary

- Formal model training and formal performance runs execute on CUDA GPUs.
- Local execution is limited to smoke tests, unit tests, aggregation, and
  document maintenance.
- While a training phase is active, sampled mean GPU utilization must be at
  least 50%, with 80% as the target. CPU-only data preparation is reported
  separately and cannot satisfy the training-resource gate.
- Outer unknown labels cannot fit preprocessing, risk formulas, thresholds,
  routing, checkpoints, or hyperparameters.

Validate the contract:

```text
python audit_project_contract.py
```

Evaluate a summarized result:

```text
python audit_project_contract.py --delivery-line engineering --metrics-json metrics.json
```
