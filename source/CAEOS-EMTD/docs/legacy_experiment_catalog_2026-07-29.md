# CAEOS-EMTD

Conflict-Aware Evidential Open-Set Encrypted Malicious Traffic Detection.

Local code is the source of truth and is mirrored to the GPU project after
every validated edit. Run `sync_to_gpu.cmd` from this directory; see
`SYNC_POLICY.md`. Datasets and experiment artifacts remain on the GPU and are
not included in source synchronization.

The implementation evolves a known-class traffic classifier into an open-set
detector through four auditable stages:

1. each traffic view produces non-negative class evidence;
2. Dirichlet opinions expose class belief and evidence insufficiency;
3. reliable pairwise disagreement forms an explicit conflict matrix and
   discounts conflicting evidence before fusion;
4. fused uncertainty, global conflict, class-prototype distance, and energy
   jointly form an unknown-risk score.

Unknown classes are never used to fit preprocessing, prototypes, component
normalizers, or the rejection threshold. The threshold is the selected quantile
of known validation risk.

## Local smoke test

```bash
python -m unittest discover -s tests -v
python train.py --dataset synthetic --epochs 3 --batch-size 128 --output-dir runs/synthetic
```

Compare the original weighted risk with the class-conditional diagnostic
conformal calibrator:

```bash
python train.py --dataset synthetic --calibrator weighted --output-dir runs/weighted
python train.py --dataset synthetic --calibrator conformal --output-dir runs/conformal
```

The conformal candidate fits class-conditional diagnostic distributions on
known training samples and calibrates empirical p-values on a separate known
validation split. It remains an experimental alternative until validated on
multiple held-out attack families.

## Closed-set multiclass baselines

`train_multiclass.py` runs every baseline with the same split, train-only
preprocessing, validation Macro-F1 early stopping, and reporting code.

| Name | Model |
|---|---|
| `mc0` | concatenated views with an MLP softmax classifier |
| `mc1` | independent view classifiers with averaged logits |
| `mc2` | independent Dirichlet evidence with sum fusion |
| `mc3` | evidential fusion with learned view reliability |
| `mc4` | reliability and conditional-conflict discount fusion |
| `aegis_backbone` | open-source AEGIS-Net DeepResNet under the shared protocol |

```bash
python train_multiclass.py \
  --model mc0 \
  --dataset tabular \
  --csv /path/to/NF-UNSW-NB15-v2.csv \
  --config configs/nf_unsw_nb15.json \
  --max-per-class 5000 \
  --epochs 80 \
  --patience 10 \
  --batch-size 512 \
  --output-dir runs/multiclass/mc0_seed7
```

Run the open-source AEGIS backbone without copying or modifying its source:

```bash
python train_multiclass.py \
  --model aegis_backbone \
  --aegis-root ../AEGIS-Net \
  --dataset tabular \
  --csv /path/to/NF-UNSW-NB15-v2.csv \
  --config configs/nf_unsw_nb15.json \
  --output-dir runs/multiclass/aegis_backbone_seed7
```

This adapter reuses the published DeepResNet architecture but intentionally
uses the shared preprocessing and validation loop. It is therefore an
`AEGIS-backbone` comparison, not a strict reproduction of the complete label
correction pipeline. Strict paper reproduction remains in `source/AEGIS-Net`.

Multiclass outputs include Accuracy, weighted Precision/Recall/F1, Macro/Micro
F1, Balanced Accuracy, ECE, NLL, Brier score, per-class metrics, and a confusion
matrix. Symmetric training-label noise is available through `--label-noise`.
Training also reports wall-clock time, inference throughput, and peak GPU memory.
AMP is enabled by default on CUDA; TF32, fused AdamW, persistent data workers,
and optional `torch.compile` are available for faster controlled experiments.

Run a small Mal_TLS2023 experiment:

```bash
python train_classical.py \
  --model random_forest \
  --dataset tabular \
  --csv /path/to/Mal_TLS2023/data/malicious_TLS.csv \
  --config configs/mal_tls2023.json \
  --benign-class benign \
  --max-per-class 500

python train_multiclass.py \
  --model mc4 \
  --dataset tabular \
  --csv /path/to/Mal_TLS2023/data/malicious_TLS.csv \
  --config configs/mal_tls2023.json \
  --benign-class benign \
  --max-per-class 500 \
  --epochs 20 \
  --patience 5 \
  --batch-size 512 \
  --num-workers 4 \
  --fused-adamw
```

The four Mal_TLS views are TLS handshake fields, IP-flow statistics, payload
statistics, and the 30-position packet sequence. The `Label` column is explicit;
it is not the last CSV column.

Run the selected MC7 closed-set backbone:

```bash
python train_hybrid.py \
  --csv /path/to/Mal_TLS2023/data/malicious_TLS.csv \
  --config configs/mal_tls2023.json \
  --benign-class benign \
  --max-per-class 100000 \
  --estimators 300 \
  --global-max-features 0.5 \
  --diverse-global-seeds \
  --minimum-view-gain 0.002 \
  --seed 7 \
  --output-dir runs/mal_tls_full/mc7_stable_seed7
```

MC7 decouples a strong RF/ExtraTrees classification path from independent
view evidence and conflict. Validation selects the global convex weight and
only enables view-probability fusion when its Macro-F1 gain reaches the
configured minimum. Temperature scaling is fitted on validation NLL and does
not change predicted classes. Use `summarize_multiseed.py` to report paired
RF/MC7 results instead of selecting a favorable single seed.

Run the leave-family-out open-set evaluation:

```bash
python train_hybrid_open_set.py \
  --csv /path/to/Mal_TLS2023/data/malicious_TLS.csv \
  --config configs/mal_tls2023.json \
  --unknown-classes Caphaw.AH_None_TLS_CC,Caphaw.A_None_TLS_CC \
  --max-per-class 500 \
  --estimators 200 \
  --seed 7 \
  --output-dir runs/mal_tls_open/caphaw_seed7
```

For Mal_TLS2023 the stable fixed score remains `cauchy_evidence`: conflict and
global-tree disagreement are independently mapped to upper-tail probabilities
using an independent known validation split, then combined without
unknown-class weight tuning. Cross-dataset experiments can enable
`--risk-selection nested_conflict_gate`. The gate compares only
`support_union` (class-conditional distance plus KNN support) and
`cauchy_evidence`, using leave-one-known-attack pseudo-unknown validation and a
fixed mean/minimum robust objective. The actual outer unknown class is never
used for score selection.

Run the HIKARI-2021 fingerprint-grouped open-set experiment:

```bash
python prepare_hikari2021.py \
  --input /path/to/ALLFLOWMETER_HIKARI2021.csv \
  --output /path/to/HIKARI2021_model.csv

python train_hybrid_open_set.py \
  --csv /path/to/HIKARI2021_model.csv \
  --config configs/hikari2021.json \
  --unknown-classes Probing \
  --benign-class Benign \
  --max-per-class 2000 \
  --estimators 150 \
  --risk-selection nested_conflict_gate \
  --seed 7 \
  --output-dir runs/hikari2021/probing_seed7
```

HIKARI-2021 is a counterexample to a universal high-conflict assumption: its
unknown attacks can receive mutually consistent but unsupported known-class
opinions. The nested gate therefore selects between conflict evidence and
distribution support without tuning on the outer unknown test set.

Run the resumable three-dataset nested-gate confirmation matrix and summarize
path accuracy and oracle regret:

```bash
python run_nested_gate_matrix.py \
  --suite both \
  --seeds 7,11,19,23,29 \
  --workers 4 \
  --model-jobs 20 \
  --estimators 80 \
  --output-root runs/nested_conflict_gate_confirmation

python run_nested_gate_matrix.py \
  --suite hikari \
  --seeds 7,11,19,23,29 \
  --workers 4 \
  --model-jobs 20 \
  --estimators 150 \
  --output-root runs/nested_conflict_gate_confirmation

python summarize_nested_gate.py \
  runs/nested_conflict_gate_confirmation/doh \
  runs/nested_conflict_gate_confirmation/mal_tls \
  runs/nested_conflict_gate_confirmation/hikari \
  --output runs/nested_conflict_gate_confirmation/combined_summary.json
```

The current 65-run confirmation selects `support_union` in all 20 HIKARI
runs and `cauchy_evidence` in all 45 DoH/Mal_TLS runs. Selection accuracy
against the post-hoc better of these two candidates is 100%; this is a
two-candidate cross-dataset result, not a general open-set SOTA claim.

## Neural open-set and ARPL baselines

Run same-split MSP, Energy, MaxLogit, Mahalanobis, relative Mahalanobis,
embedding KNN, OpenMax, and ViM from one MLP checkpoint:

```bash
python train_neural_open_set.py \
  --csv /path/to/HIKARI2021_model.csv \
  --config configs/hikari2021.json \
  --unknown-classes Probing \
  --benign-class Benign \
  --split-strategy fingerprint_grouped \
  --max-per-class 2000 \
  --model mlp \
  --output-dir runs/neural/hikari_probing_seed7
```

Use `--model arpl` for the official reciprocal-point and radius objective, or
`--model supcon` for the rejected supervised-contrastive embedding ablation.
Use `--model closr` for the official-method class-specific contrastive
adaptation and `--model cade` for the contrastive-autoencoder drift
adaptation. CADE reports both the shared known-validation calibration and the
fixed MAD=3.5 auxiliary threshold.
The resumable `run_neural_baseline_matrix.py` expands datasets, scenarios,
models, and seeds. `summarize_neural_comparison.py` performs paired win/loss
and Wilcoxon analysis against a nested-gate result tree. Every run saves
sample-level validation/test risks in `scores.npz`; unknown labels are never
used to fit a score or threshold.

The stable hybrid runner additionally writes a deployment-oriented
`evidence_package.npz`. It contains per-modality class evidence, probability,
uncertainty, reliability, local and pairwise conflict, fused probability,
the selected risk, its known-validation threshold, and the final reject
decision. Test labels and unknown-ground-truth flags are deliberately absent.
Validate the package independently with:

```bash
python verify_evidence_package.py \
  --input runs/hikari2021/probing_seed7/evidence_package.npz
```

Across the current 39 matched runs, the nested gate reaches mean AUROC
`0.929520`, versus `0.883127` for the strongest fixed neural score (KNN),
with 33 wins and Wilcoxon `p=3.40e-05`. ARPL reaches `0.719251`. These are
same-protocol implemented-baseline results, not a universal SOTA claim.

The external security-specific matrix uses the same 39 tasks. CAEOS v1.4.4
reaches AUROC `0.932796`, versus `0.767187` for CLOSR and `0.630395` for
CADE. CAEOS records 33/0/6 and 39/0/0 paired wins/ties/losses respectively;
the compact combined archive is under
`results/external_strong_baselines_same_split_39`.

## Hierarchical anchor/conflict gate (v1.4.3)

The current open-set default preserves the original validation-only nested
choice between `support_union` and `cauchy_evidence`. When and only when that
first stage selects support, it replaces the support score with a fixed
low-weight anchor-modality rescue:

`anchor_support = 0.85 * support_union + 0.15 * anchor_modality_knn`.

Anchor modalities are declared by feature semantics in each dataset config;
they are not selected from unknown test labels. Reproduce the final path with
`--risk-selection nested_hierarchical_anchor_gate`. Across 65 family/tool
leave-out runs, this version reaches AUROC `0.931747` versus `0.928174` for the
original gate (18 wins, 45 ties, 2 losses; Wilcoxon `p=0.005734`) while
retaining 100% path-selection accuracy and zero post-hoc oracle regret.

Run the selected MC8 modality-corruption evaluation:

```bash
python evaluate_hybrid_corruption.py \
  --csv /path/to/Mal_TLS2023/data/malicious_TLS.csv \
  --config configs/mal_tls2023.json \
  --max-per-class 500 \
  --estimators 200 \
  --seed 7 \
  --output runs/mal_tls_corruption/mc8_seed7.json
```

MC8 uses clean-validation conflict quantiles to preserve the global classifier
in the low-conflict region and continuously routes high-conflict samples to
locally discounted view evidence. The default risk objective assigns weight
`0.3` to the minimum corrupted-validation Macro-F1. The rejected dual-conflict
ablation remains reproducible with `--routing-conflict-mode probabilistic_or`
and `--robust-minimum-weight 0.7`. Aggregate seeds with
`summarize_corruption.py`.

Evaluate generalization to unseen structural corruption:

```bash
python evaluate_hybrid_structural_corruption.py \
  --csv /path/to/Mal_TLS2023/data/malicious_TLS.csv \
  --config configs/mal_tls2023.json \
  --max-per-class 500 \
  --estimators 200 \
  --seed 7 \
  --output runs/mal_tls_corruption/mc8_structural_seed7.json
```

The structural suite covers full-modality loss, random field loss,
intermittent row-level loss, and packet-sequence truncation. The optional
`--routing-conflict-mode adaptive_missingness` calibrates per-view zero-rate
anomalies from training data and only activates dual-conflict routing when a
sample exceeds that baseline. It is a safety-mode ablation; `global` remains
the selected default.

## NF-UNSW-NB15 open-set experiment

The included adapter splits NetFlow features into volume, transport, and
service/timing views. IP addresses and direct identifiers are excluded. The
configuration removes feature-identical groups carrying conflicting labels,
uses full-feature fingerprint-grouped splitting, and declares `volume` as the
semantic anchor modality.

```bash
python train.py \
  --dataset tabular \
  --csv /path/to/NF-UNSW-NB15-v2.csv \
  --config configs/nf_unsw_nb15.json \
  --unknown-classes Backdoor \
  --benign-class Benign \
  --max-per-class 5000 \
  --epochs 15 \
  --batch-size 512 \
  --num-workers 4 \
  --output-dir runs/nf_unsw_backdoor
```

Outputs include the model checkpoint, known-only calibrator, metrics, training
history, class mapping, feature groups, and train-only preprocessing state.

Reproduce the six-family leave-one-out joint-gate matrix with:

```bash
python run_nested_gate_matrix.py \
  --suite nf_unsw \
  --seeds 7,11,19,23,29,31,37,41,43 \
  --workers 3 \
  --model-jobs 4 \
  --estimators 40 \
  --nf-unsw-max-per-class 1500 \
  --risk-selection nested_hierarchical_joint_gate \
  --joint-fallback-minimum-gain 0.055 \
  --output-root runs/nf_unsw_joint_gate
```

The v1.4.4 candidate keeps the v1.4.3 support/conflict first stage. Support
still maps to `anchor_support`. On the conflict branch, `cauchy_all` replaces
`cauchy_evidence` only when its nested robust-objective gain exceeds `0.055`.
Across 54 NF-UNSW runs, AUROC increases from `0.715697` to `0.726718`
(`+0.011021`, 10 wins/43 ties/1 loss, Wilcoxon `p=0.002930`). The previous
65 HIKARI/DoH/Mal_TLS results are unchanged at this conservative margin. This
is evidence of a stable incremental mechanism, not a universal SOTA claim.

## External open-set baseline matrix

`run_neural_baseline_matrix.py` also provides same-split adapters for CLOSR,
CADE, Open-Detect, RoNeTC, FOSS, and Sieve. Open-Detect retains its Gaussian-prototype VAE
objective and prototype resets; RoNeTC retains view-wise Dirichlet evidence,
joint evidential loss, Dempster-Shafer fusion, and joint uncertainty risk.
RoNeTC and all other adapters use known-validation-only threshold calibration.
FOSS follows the TON 2024 weighted-entropy Monte Carlo isolation-tree formulas;
the official repository omits its imported `FOSS.py`, so this adapter is a
paper-faithful reimplementation rather than an official-code run.
Sieve retains the official 1D DeepResNet, neighbor-consistency selection,
confidence expansion, mixup, batch contrastive objective, and class-conditional
Mahalanobis detector. Its adapter removes author-machine paths, fits preprocessing
on training data only, selects checkpoints on known validation rather than test
accuracy, and supplies the two contrastive views expected by the published loop.

```bash
python run_neural_baseline_matrix.py \
  --suite all \
  --models opendetect,ronetc,foss,sieve \
  --seeds 7,11,19 \
  --workers 4 \
  --epochs 100 \
  --patience 10 \
  --output-root runs/direct_external_baselines_39
```

Across the shared 39 tasks, CAEOS v1.4.4 reaches mean AUROC `0.932796`,
compared with `0.792297` for Open-Detect, `0.656010` for RoNeTC, and
`0.675517` for the FOSS reimplementation. Against FOSS, CAEOS records 34 wins and 5 losses,
with Wilcoxon `p=1.29e-07`. FOSS wins all three HIKARI/XMRIGCC seeds, which
motivated known-only random-partition representation ablations. Neither the
nested FOSS expert gate nor 61-dimensional and 8-dimensional structural views
improved both AUROC and OSCR across the 12 HIKARI confirmation tasks, so v1.4.4
remains the stable default. Reproduce the compact structural view with
`--foss-structural-view --foss-structural-view-mode aggregate`.
Use `--foss-structural-view-scope evidence` to exclude it from the global
classifier and all support geometry, or `--foss-structural-view-scope support`
to keep classification/evidence unchanged and augment only distance, KNN, and
LOF support. The evidence-only seed-7 pilot exactly reproduces v1.4.4. The
support-only 12-run confirmation improves AUROC by `0.006262` but reduces OSCR
by `0.009889`; both remain ablations rather than stable defaults.
The validation-only `nested_structural_support_gate` also evaluates support
weights `0,0.1,0.25,0.5,1.0`, with weight zero as an exact raw-feature
fallback and a joint robust AUROC/OSCR objective. In the 12-run confirmation it
selects zero eight times, but the four nonzero triggers reduce mean AUROC by
`0.006056` and OSCR by `0.005274` overall. All four triggers had positive inner
AUROC and OSCR gains, so an additional Pareto-positive check cannot repair the
transfer failure without tuning on outer unknown labels. This path remains an
ablation and v1.4.4 remains the stable default.

The Sieve same-split 39-run adapter reaches AUROC `0.766057`, versus
`0.932796` for CAEOS (37 wins, 2 losses; Wilcoxon `p=9.09e-11`). Sieve wins
HIKARI/Bruteforce-XML seed 7 and Brutefoce seed 11, but its mean OSCR is
`0.659123` versus `0.907870`. Four validation-calibrated fixed risk fusions all
regress; the best, `rank_max`, reaches `0.909584`. These results use complete
unknown-class holdout and are separate from Sieve's original mixed closed/open
label-noise protocol, which requires authorized CipherSpectrum access.

The validation-only Open-Detect expert gate and four fixed empirical-rank fusions
were also evaluated and rejected because they did not improve the complete
matrix. Reproduce the fixed-fusion diagnostic with:

```bash
python analyze_caeos_closr_fusion.py \
  --gate-root runs/nested_anchor_gate_confirmation \
  --expert-root runs/opendetect_official_same_split_39 \
  --expert-name opendetect \
  --output runs/caeos_opendetect_fixed_fusion/analysis.json
```

## Strict-v2 extended-dataset SOTA protocol

The current formal protocol covers 38 leave-one-attack-out scenarios from
Edge-IIoTset (14), NF-CSE-CIC-IDS2018-v2 (14), and USTC-TFC2016 (10), with
seeds `7,11,19,23,37`. Seed-specific caches freeze the exact sampled rows and
all methods must match train/validation/test split fingerprints. Unknown rows
are isolated before cross-label fingerprint cleaning, and no unknown test
label may participate in preprocessing, checkpoint selection, score fitting,
threshold fitting, or hyperparameter selection.

The baseline coverage is deliberately split by computational ownership:

| Family | Methods emitted |
|---|---|
| shared MLP checkpoint | MSP, Energy, MaxLogit, Mahalanobis, relative Mahalanobis, KNN, ViM, OpenMax, NCI, Energy+CEA, NCI+CEA, SCALE |
| independent neural training | ARPL, CLOSR, CADE, Open-Detect, RoNeTC, Sieve, PALM |
| non-neural open-set detector | FOSS |
| CAEOS | frozen suite-conditional density policy described below |

This gives 20 paired baseline methods per scenario. Supervised contrastive
learning remains a documented ablation rather than a promoted baseline because
it was rejected during earlier development and is not a distinct published
open-set detector in this protocol.

PALM retains its official balanced Sinkhorn assignments, frozen pre-EMA top-k
prototype selection, EMA mixture prototypes, MLE and prototype-contrastive
losses, ICLR 2024 runner budget (`500` epochs, batch `512`, learning rate
`0.5`, weight decay `1e-6`), and SSD+ detector. Its ResNet and image crops are
necessarily adapted to the shared tabular MLP and stochastic tabular encoder
passes. SCALE retains the official activation scaling and Energy score; the
only model-specific adaptation is ReLU clamping of GELU penultimate features.
NCI and CEA use their official fixed score parameters without auxiliary OOD
selection.

Development seed 7 selected density blend weight `0.30` under the predeclared
AUROC objective with AUPR/OSCR non-regression and absolute FPR95-regression
limit `0.01`. Only Edge-IIoTset had at least three development triggers, so the
frozen policy enables the density gate there and uses
`nested_hierarchical_joint_gate` on NF-CSE and USTC. Four confirmation seeds
showed positive mean deltas on AUROC, AUPR, FPR95, and OSCR, but none was
statistically significant after scenario-blocked inference and Holm
correction. The frozen evidence is stored under
`results/strict_v2_density_policy`; it supports a guarded candidate, not a
universal density-gate claim.

Run the final CAEOS policy matrix:

```bash
python run_nested_gate_matrix.py \
  --suite extended \
  --scenarios all \
  --seeds 7,11,19,23,37 \
  --workers 4 \
  --model-jobs 10 \
  --estimators 80 \
  --risk-selection nested_density_reliability_gate \
  --density-gate-supported-suites edge_iiot \
  --density-gate-fallback-risk-selection nested_hierarchical_joint_gate \
  --density-gate-minimum-gain 0.02 \
  --density-gate-minimum-known-classes 8 \
  --density-gate-blend-weight 0.30 \
  --edge-iiot-cache-dir caches/strict_v2/edge_iiot \
  --nf-cse-cache-dir caches/strict_v2/nf_cse \
  --ustc-cache-dir caches/strict_v2/ustc_tfc2016 \
  --output-root runs/strict_v2_caeos_frozen_policy_5seed
```

Run the modern neural matrix. `--epochs 0` selects each method's frozen
paper-aligned budget, including the 500-epoch PALM setting:

```bash
python run_neural_baseline_matrix.py \
  --suite extended \
  --scenarios all \
  --models mlp,palm \
  --seeds 7,11,19,23,37 \
  --workers 4 \
  --epochs 0 \
  --patience 10 \
  --edge-iiot-cache-dir caches/strict_v2/edge_iiot \
  --nf-cse-cache-dir caches/strict_v2/nf_cse \
  --ustc-cache-dir caches/strict_v2/ustc_tfc2016 \
  --output-root runs/strict_v2_modern_baselines_5seed
```

Run the official-method external baselines and the remaining independent
baseline families as separate resumable matrices:

```bash
python run_neural_baseline_matrix.py \
  --suite extended \
  --scenarios all \
  --models opendetect,sieve \
  --seeds 7,11,19,23,37 \
  --workers 2 \
  --epochs 0 \
  --patience 10 \
  --edge-iiot-cache-dir caches/strict_v2/edge_iiot \
  --nf-cse-cache-dir caches/strict_v2/nf_cse \
  --ustc-cache-dir caches/strict_v2/ustc_tfc2016 \
  --output-root runs/strict_v2_strong_baselines_5seed

python run_neural_baseline_matrix.py \
  --suite extended \
  --scenarios all \
  --models arpl,closr,cade,ronetc,foss \
  --seeds 7,11,19,23,37 \
  --workers 2 \
  --epochs 0 \
  --patience 10 \
  --edge-iiot-cache-dir caches/strict_v2/edge_iiot \
  --nf-cse-cache-dir caches/strict_v2/nf_cse \
  --ustc-cache-dir caches/strict_v2/ustc_tfc2016 \
  --output-root runs/strict_v2_legacy_baselines_5seed
```

`summarize_neural_comparison_strict_v2.py` rejects incomplete method coverage,
protocol mismatches, invalid split fingerprints, and inconsistent frozen
policies. It averages seed repeats within each scenario, uses scenarios as the
inference units, reports scenario-block bootstrap 95% confidence intervals,
paired Cohen's dz, matched-pairs rank-biserial correlation, two-sided Wilcoxon
tests, and Holm-adjusted p-values. Missing runtime or GPU-memory fields remain
explicitly missing and are never imputed.

Seed `7` selected the frozen density weight, so it is development evidence and
must not enter confirmatory inference. Pass `--inference-seeds 11,19,23,37`
when generating the final comparison. The comparator first validates complete
coverage, protocol identity, and split fingerprints for all five seeds, then
excludes seed `7` only from the statistical summaries.

After all four matrices are complete, generate the final paired report with
every method root supplied separately for every suite:

```bash
python summarize_neural_comparison_strict_v2.py \
  --gate-root runs/strict_v2_caeos_frozen_policy_5seed \
  --neural-root edge_iiot=runs/strict_v2_strong_baselines_5seed/edge_iiot \
  --neural-root edge_iiot=runs/strict_v2_modern_baselines_5seed/edge_iiot \
  --neural-root edge_iiot=runs/strict_v2_legacy_baselines_5seed/edge_iiot \
  --neural-root nf_cse=runs/strict_v2_strong_baselines_5seed/nf_cse \
  --neural-root nf_cse=runs/strict_v2_modern_baselines_5seed/nf_cse \
  --neural-root nf_cse=runs/strict_v2_legacy_baselines_5seed/nf_cse \
  --neural-root ustc_tfc2016=runs/strict_v2_strong_baselines_5seed/ustc_tfc2016 \
  --neural-root ustc_tfc2016=runs/strict_v2_modern_baselines_5seed/ustc_tfc2016 \
  --neural-root ustc_tfc2016=runs/strict_v2_legacy_baselines_5seed/ustc_tfc2016 \
  --inference-seeds 11,19,23,37 \
  --bootstrap-repetitions 10000 \
  --output-dir results/strict_v2_sota_confirmation_4seed
```

## Decisions

- non-negative class index: accepted known class;
- `-1`: unknown malicious candidate;
- `-2`: unknown benign traffic or environment drift.

The initial tabular adapter is intended for algorithm validation. Packet
sequence, visible protocol fields, and communication-graph encoders can replace
the three view encoders without changing the evidence, conflict, fusion, or
open-set calibration interfaces.

## Strict-v4 VOS pilot

The strict-v4 baseline screen includes a VOS adaptation that is intentionally
separate from NPOS. `caeos/vos.py` implements per-class feature queues, class
means, tied covariance, low-likelihood Gaussian virtual outliers, and the
weighted-energy regularizer. `train_vos_open_set.py` uses plain negative
log-sum-exp energy as the primary OOD score and known-only validation for the
deployment threshold.

`create_strict_v4_vos_pilot_protocol.py` freezes 14 seed-7 scenarios before any
VOS result, `run_strict_v4_vos_matrix.py` enforces implementation/source SHA
bindings, and `summarize_strict_v4_vos_pilot.py` applies the prefrozen expansion
gate. The remote zero-result protocol SHA is
`9669965f282d5832b9dcaf460ed85b2882e14dbe4b1060376bd8498174f05903`.
`scripts/wait_and_run_strict_v4_vos_pilot.sh` waits for the DoH temporal screen
and an idle GPU; a gate failure retains VOS as negative baseline evidence and
does not trigger full102 work.
