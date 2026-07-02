# DA-FDIDS Experiment Report: CIC-ToN-IoT

**Generated**: 2026-06-22 07:50:27

**Parameters**: pretrain_epochs=10, meta_epochs=100, repetitions=10

## Results Summary

### In-Domain
| Variant | Best Alpha | F1 | NMI | vs B0 | Description |
|---------|-----------|-----|-----|-------|-------------|
| B1 | 0.7 | 0.9987 | 0.9969 | +0.9987 | +Foundation Encoder (TrafficEncoder) |

### Cross-Domain
| Variant | Best Alpha | F1 | NMI | vs B0 | Description |
|---------|-----------|-----|-----|-------|-------------|

## Cross-Domain DA Analysis

- B0 (DIDS-MFL baseline): F1 = **0.0000**
- B3 (Cache fusion): F1 = **0.0000** (+0.0000)

| DA Module | Variant | Best F1 | vs B3 | Effective? |
|-----------|---------|---------|-------|------------|

## Best Alpha Distribution

| Alpha | Count | Interpretation |
|-------|-------|----------------|

## Efficiency Metrics

| Protocol | Variant | LoRA Time (s) | Trainable Params |
|----------|---------|---------------|------------------|