# NF-UNSW v1.4.4 full-scale confirmation

This directory contains the compact, local evidence archive for the fixed-gate confirmation experiment. Per-sample predictions and sampled CSV files remain on the GPU server.

## Protocol

- Dataset: NF-UNSW-NB15-v2.
- Unknown families: Analysis, Backdoor, DoS, Exploits, Generic, and Reconnaissance.
- Seeds: 47, 53, and 59; these seeds were not used by the 54-run development matrix.
- Scale: at most 5000 rows per class and 150 trees.
- Split: cross-label fingerprints removed before fingerprint-grouped train/validation/test splitting.
- Risk rule: fixed `nested_hierarchical_joint_gate` with joint-branch minimum inner robust gain `0.055`.

## Result

The v1.4.4 mean unknown AUROC is `0.760056`, compared with `0.744254` for its v1.4.3 hierarchical parent. The paired outcome is 3 wins, 15 ties, and 0 losses; the exact two-sided Wilcoxon p-value after removing zero differences is `0.25`. The experiment confirms positive transfer without observed regression, but is not independently statistically significant because the safety gate activated only three times.

## Files

- `manifest.json`: exact commands, runtime parameters, completion state, and elapsed time for all 18 runs.
- `summary.json` and `summary.md`: direct runtime result compared with the v1.4.3 parent gate.
- `replay_gain_0055.json`: offline replay of the fixed `0.055` safety gate.
- `cache_seed*.json`: source, class counts, column list, sample seed, and SHA-256 of each remote deterministic cache.

