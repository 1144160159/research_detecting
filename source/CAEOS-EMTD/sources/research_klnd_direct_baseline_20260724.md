# k-LND direct-baseline evidence record

Audit date: 2026-07-24 CST

## Primary sources

- Paper DOI: https://doi.org/10.1016/j.comnet.2023.109991
- Open paper copy:
  https://opus.lib.uts.edu.au/bitstream/10453/179247/2/Robust%20open-set%20classification%20for%20encrypted%20traffic%20fingerprinting.pdf
- Official repository:
  https://github.com/ThiliniDahanayaka/Open-Set-Traffic-Classification
- Frozen repository commit:
  `673320b86dcaf72dcdeae5159b3b8ce91ac5e19c`
- Repository bundle SHA-256:
  `3cac6a8dbedc364d1514c3e0cf517410319e8dc99165326f4352654c5549ed9e`
- Paper PDF SHA-256:
  `dd64018fd7875ca862ed50ab41b935a414bd1631fa5d3841c504f0806b38e52a`

## Method contract

- Class centers are mean logit vectors from correctly classified known
  training samples.
- Native per-class thresholds use correctly classified known validation
  samples.
- k-LND1 uses the distance to the predicted-class center.
- k-LND2 compares the predicted-class distance with the sum of distances to
  all other known-class centers.
- k-LND3 divides the predicted-class distance by the sum of distances to the
  other known-class centers.
- The strict-v4 adapter orients all scores so higher means more unknown. Its
  k-LND2 risk is therefore negative D2; a 90th risk percentile is equivalent
  to the official large-class notebooks' 10th-percentile lower-tail D2 rule.

## Released-code audit boundary

- The frozen repository has 219 tracked files and a clean worktree.
- Source identities use canonical Git blob contents so CRLF/LF differences do
  not change the protocol.
- The official experiments cover AWF, DF, DC, SETA, and IoT rather than the
  strict-v4 seven-suite leave-one-family-out matrix.
- Official notebooks are research artifacts, not a uniform package. The DC
  notebook uses a 0.9 index for all three distance variants, while the
  large-class AWF/DF path uses the lower-tail D2 convention. The adapter
  follows the paper's equations and records the risk orientation explicitly
  instead of copying notebook-specific inconsistencies.

## Strict-v4 adaptation

- The already trained strict MLP is frozen. k-LND is fitted only to its known
  training and known validation logits; no model retraining or unknown-label
  fitting is allowed.
- All other known classes are neighbors. No value of k is tuned on OOD or test
  data.
- The 14-scenario development pilot is chosen from the frozen coverage SHA and
  official commit, two scenarios per suite, independently of metric values.
- k-LND1, k-LND2, and k-LND3 are evaluated together. Variant selection uses
  the lowest four-unknown-metric mean rank with a lexical exact-tie rule.
- The pilot may spend test labels only on the explicitly development-only
  expansion decision. A separate known-validation 95% acceptance threshold is
  used for strict deployment reporting.
- Full 102-scenario execution is not automatic. It requires all frozen
  completeness, leakage, score, rank, metric-breadth, known-F1, suite, and
  overall-gain gates to pass.

## Frozen identities and current state

- Protocol canonical/file SHA-256:
  `a3f0572b316f758e0f5e518ba21dd9c4384f9270e48659f1864c5e372a24611e` /
  `b36099b263bcbf971c38f35e30fe2fc96671d0a30152fdc3b5f424664f83e631`
- Expansion-gate canonical/file SHA-256:
  `a6b73331a77c279baa86bf0b81856a6e4a7f32ab915d55e9e5da20c68e12a5a2` /
  `0933aeb7e0e1efcb9ede4f2becbdee1ff2f108e853667db1c78a8b1b876e39b6`
- Scorer/evaluator/runner SHA-256:
  `78a57d674be63cc2c24a91859b855ff6888ce899aec52ad4de4e04bf23e2d295` /
  `6f34646d346cbea45021365fd00fc214eedc2ecaf04ece194060fb57a73e25f1` /
  `ccf8c7c7ee813ab6eed14781cfa88507140704916191b470255d061b1e79933d`
- Watcher SHA-256:
  `16adc13092860e208a12382493852407672d001d16b95fa2f484300bbe09220c`
- Local and GPU regression result: 12/12 passed.
- At freeze: 0/14 pilot runs and zero model reports. k-LND does not increment
  the formal baseline count until complete results pass the frozen gate.
