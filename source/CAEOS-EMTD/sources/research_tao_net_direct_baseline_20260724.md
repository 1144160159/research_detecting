# TAO-Net direct-baseline evidence refresh

Audit date: 2026-07-24 CST

## Primary sources

- Publisher record: https://doi.org/10.1016/j.neucom.2026.133170
- arXiv record: https://arxiv.org/abs/2512.15753
- Official repository: https://github.com/WaIdo/TAO-NET
- Frozen repository commit: `a1574f38741772ac79628131f9fbef8a7c78374a`
- Frozen PDF SHA-256: `9aea18ac0cecde001d38fb24eca25d46d282e126a2384609591d42ba804ef491`
- Source-file identities use SHA-256 of the canonical Git blob contents rather
  than platform-dependent CRLF/LF working-tree bytes.

## Paper facts used by the audit

- Datasets: CHNAPP, ISCXVPN, ISCXTor.
- ID/OOD class counts: 4/2, 9/4, 8/4.
- Only ID samples are in training; validation and test both contain ID/OOD at 7:3.
- The strict prompt constrains generation to the OOD candidate-label set.
- Reported hybrid parameters are alpha 0.6 and delta 0.75.
- Reported metrics are Macro Precision, Macro F1, Micro F1, and Recall.

## Released-code facts used by the audit

- The README says final configuration bundles, preprocessed-data checksum manifests,
  and deployment scripts are not yet published.
- The released Stage-1 dataset loader implements only the CHNAPP/Tinghuaall path
  and merges `processed_valid.json` into training.
- The released Stage-1 default is Youden thresholding; the runner partitions the
  test set with labels and supplies both test ID and test OOD scores to threshold
  search and final evaluation.
- Fifteen referenced processed-data, split, and pretrained-model artifacts are
  absent from the official commit.

## Scope boundary

TAO-Net is a directly relevant 2026 pressure-test baseline, but its released
snapshot and paper protocol are not equivalent to strict-v4 zero-unknown-exposure
rejection. It remains an appendix protocol-layering candidate until the missing
artifacts and exact configurations are released and a leakage-free threshold
protocol is frozen before any local effect is observed.

Native reproduction admission and strict-v4 main-table admission are separate
gates. The former may pass under TAO-Net's published task once exact release
artifacts exist; the latter additionally requires the strict-v4 task, exposure,
threshold-selection, label-visibility, and metric contract.
