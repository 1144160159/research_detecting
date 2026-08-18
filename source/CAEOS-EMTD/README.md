# CAEOS-EMTD

Conflict-Aware Evidential Open-Set Encrypted Malicious Traffic Detection.

This local directory is the only editable source of truth. Validated GPU code
is exposed through:

`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/current`

The machine-readable project contract is
`contracts/caeos_delivery_contract_v1.json`.

## Current delivery lines

| Line | Goal | Required gate |
|---|---|---|
| Engineering | Stable attack warning and known-family classification with the existing statistical/temporal route | `engineering_safety_95_5` |
| Paper | Heterogeneous multimodal open-set detection using the temporal/statistical backbone plus payload semantics, graph structure, or application behavior | `paper_full_open_set_95_5` plus three-layer metrics and ablations |

Engineering acceptance cannot substitute for paper multimodal evidence. The
current project status is **not formally accepted** on either line: diagnostic
or post-selected results do not count as confirmation.

## Canonical rules

- [Project contract](PROJECT_CONTRACT.md)
- [Code layout](CODE_LAYOUT.md)
- [Local/GPU synchronization policy](SYNC_POLICY.md)
- [Historical experiment catalog](docs/legacy_experiment_catalog_2026-07-29.md)

The historical catalog is retained for reproducibility only. A command listed
there is not a current entrypoint unless `CODE_LAYOUT.md` and a current
protocol both admit it.

## Validate locally

Local execution is limited to code and contract tests, result aggregation, and
document maintenance:

```text
python -m pytest -q tests/test_project_contract.py tests/test_strict_v4_open_set_metric_contract_v2.py
python audit_project_contract.py
```

Formal training and performance experiments run on the GPU server. Every
formal result must record the resolved `CAEOS-EMTD/current` release,
`SOURCE_MANIFEST.sha256`, CUDA provenance, and sampled utilization.

## Publish to the GPU

After affected local tests pass:

```text
sync_to_gpu.cmd
```

The publisher creates an immutable release under the unified workspace,
validates it remotely, and only then atomically advances `CAEOS-EMTD/current`.
Existing processes under `CAEOS-EMTD/active` are preserved as legacy active
jobs; no new experiment may start there.

## Core implementation flow

1. Each admitted modality produces non-negative known-class evidence.
2. Dirichlet opinions expose evidence insufficiency.
3. Reliability-weighted disagreement forms explicit conflict evidence.
4. Fused uncertainty, conflict, support/distance, and energy form unknown risk.
5. Alert and rejection thresholds are fitted without outer unknown labels.
6. Evaluation emits the three metric layers and the delivery-line safety gate.

The paper line must demonstrate genuinely heterogeneous information sources.
Splitting one flow-feature table into several column groups is an engineering
multi-view implementation, not sufficient evidence of paper-level
multimodality.
