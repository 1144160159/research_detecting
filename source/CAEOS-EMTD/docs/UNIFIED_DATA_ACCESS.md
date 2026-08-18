# Unified CAEOS Data Access

## Responsibility boundary

The supported experiment path has three layers:

1. `UnifiedDatasetLoader` resolves and verifies the frozen CSV schema, dataset
   manifest, class CSV inventory, label-admission rule, duplicate audit, and
   content-conflict policy. `iter_contract_rows()` streams rows only after the
   immutable schema and label contract has passed.
2. `OpenSetDataStrategy` applies the experiment policy. It removes rows named
   by the cross-label model-content policy, joins capture-equivalence groups,
   assigns held-out families to `unknown_test`, and partitions only the known
   groups into `train`, `known_validation`, and `known_test`.
3. `TrainOnlySampler` accepts `train` records only. It applies deterministic
   class and optional group caps without changing validation or test
   distributions.

Feature projection is contract-driven. The loader materializes payload
semantics, packet behavior, and packet-interaction graph views from the frozen
feature-view specification. Audit, identity, endpoint, port, and target columns
cannot enter these model views.

## Immutable inputs

The default registry is `configs/unified_data_access_v1.json`. Every dataset
entry binds the following artifacts:

- class-CSV dataset manifest and its embedded canonical hash;
- exact schema hash, row counts, sizes, per-file hashes, and label-status audit;
- duplicate audit and capture-equivalence edges;
- cross-label content-conflict policy and binary digest index, when required.

The default `stat` integrity mode verifies manifest hashes plus file existence
and size before data iteration. Use `sha256` for a release gate. `manifest` is a
metadata-only diagnostic and must not be used as final data acceptance.

## Commands

Validate contract metadata for all registered datasets:

```bash
python prepare_caeos_experiment_data.py validate \
  --output-root /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5 \
  --integrity stat \
  --report results/data_contract_validation.json
```

Create one replayable leave-family-out split. The operation streams all class
CSVs and therefore also executes row-level label and conflict-policy checks:

```bash
python prepare_caeos_experiment_data.py split \
  --output-root /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5 \
  --dataset ciciot2023 \
  --unknown-family DDoS \
  --seed 7 \
  --split-plan results/splits/ciciot2023_ddos_seed7.json
```

Create a bounded training index. No validation or test record can pass the
sampler boundary:

```bash
python prepare_caeos_experiment_data.py sample-index \
  --output-root /opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5 \
  --dataset ciciot2023 \
  --split-plan results/splits/ciciot2023_ddos_seed7.json \
  --seed 7 \
  --default-class-cap 200000 \
  --max-rows-per-group 20000 \
  --sample-index results/samples/ciciot2023_ddos_seed7.jsonl \
  --sampling-audit results/samples/ciciot2023_ddos_seed7.audit.json \
  --experiment-manifest results/samples/ciciot2023_ddos_seed7.manifest.json
```

## Leakage controls

- Unknown families are assigned directly to `unknown_test`; they never enter
  known training, validation, or test partitions.
- Capture-equivalent identities are unioned before partition assignment.
- A group that mixes known and unknown families fails closed by default.
- Cross-label model-content digests are excluded before grouping and splitting.
- The sampler rejects any record whose partition is not `train`.
- Split, sampling, feature-request, and experiment manifests have canonical
  hashes and bind all upstream contract hashes.
- Threshold fitting remains `known_only_validation`; unknown-test data is not
  exposed for feature, threshold, or sampler selection.

## Memory behavior

CSV rows are streamed. Without a group cap, the sampler retains at most the
sum of class caps. With `max_rows_per_group`, it first retains at most that many
records per observed `(class, group)` and then applies class caps. Split-plan
construction retains capture-level labels, counts, and assignments rather than
all flow rows. For very high-cardinality capture sets, split plans should be
generated once and reused across model runs.
