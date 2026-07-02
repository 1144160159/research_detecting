# DA-FDIDS Experiment Report: CIC-ToN-IoT

**Generated**: 2026-06-05 03:15:47

**Parameters**: pretrain_epochs=10, meta_epochs=100, repetitions=10

## Results Summary

### In-Domain
| Variant | Best Alpha | F1 | NMI | vs B0 | Description |
|---------|-----------|-----|-----|-------|-------------|
| B0 | 0.7 | 0.1696 | 0.0551 | +0.0000 | DIDS-MFL baseline (must match DIDS-MFL-1) |

### Cross-Domain
| Variant | Best Alpha | F1 | NMI | vs B0 | Description |
|---------|-----------|-----|-----|-------|-------------|
| B0 | 0.7 | 0.1744 | 0.0459 | +0.0000 | DIDS-MFL baseline (must match DIDS-MFL-1) |

### Drift
| Variant | Best Alpha | F1 | NMI | vs B0 | Description |
|---------|-----------|-----|-----|-------|-------------|
| B0 | 0.7 | 0.2145 | 0.0311 | +0.0000 | DIDS-MFL baseline (must match DIDS-MFL-1) |

## Cross-Domain DA Analysis

- B0 (DIDS-MFL baseline): F1 = **0.1744**
- B3 (Cache fusion): F1 = **0.0000** (+-0.1744)

| DA Module | Variant | Best F1 | vs B3 | Effective? |
|-----------|---------|---------|-------|------------|

## Best Alpha Distribution

| Alpha | Count | Interpretation |
|-------|-------|----------------|

## Efficiency Metrics

| Protocol | Variant | LoRA Time (s) | Trainable Params |
|----------|---------|---------------|------------------|
| In-Domain | B0 | N/A | ~0 |
| Cross-Domain | B0 | N/A | ~0 |
| Drift | B0 | N/A | ~0 |