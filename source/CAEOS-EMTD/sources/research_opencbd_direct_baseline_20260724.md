# OpenCBD direct-baseline evidence record

Audit date: 2026-07-24 CST

## Primary source identity

- Title: OpenCBD: A Network-Encrypted Unknown Traffic Identification Scheme
  Based on Open-Set Recognition
- Publisher full text:
  https://onlinelibrary.wiley.com/doi/10.1155/2022/1746373
- DOI: https://doi.org/10.1155/2022/1746373
- Authors: Xinyi Hu, Chunxiang Gu, Yihang Chen, Xi Chen, and Fushan Wei
- Publication: Wireless Communications and Mobile Computing, 2022, article
  1746373, 18 pages
- License reported by the publisher and Semantic Scholar: CC BY
- The publisher HTML was readable during the audit. Direct PDF retrieval from
  the current environment returned HTTP 403, so no local PDF hash is claimed.

## Paper contract

- Dataset: ISCXVPN2016.
- Eight traffic classes are known and five disjoint classes are unknown.
- The experiment samples 1,000 examples per class.
- One example is built from ten consecutive packets.
- Packet payload is truncated or padded to a fixed byte vector, and a virtual
  packet represents inter-packet gaps greater than one second.
- The CBD encoder combines a CNN module, a Transformer/BERT encoder, and dense
  layers.
- Training has an unlabeled self-supervised pretraining stage, an individual
  known-class training stage, and an ensemble known-class training stage.
- The paper evaluates 4, 8, and 12 individual encoders; the open-set ensemble
  has eight known outputs plus one unknown decision.
- The loss combines cross entropy and II-loss.
- The rejection threshold is the known-training outlier-distance boundary:
  distances are sorted and the largest one percent are treated as outliers.
  Unknown/test samples are not described as threshold-fitting inputs.
- Reported evaluation is known/unknown binary and known-class multiclass
  accuracy, precision, recall, and F1 rather than the strict-v4 five-metric
  contract.

## Reproducibility and admission boundary

- Exact searches by title, acronym, DOI, and architecture terms found no
  author-identified public implementation on 2026-07-24.
- The paper does not publish a code commit, dependency lock, deterministic
  seed, exact eight-known/five-unknown class-name table in machine-readable
  form, archive checksum manifest, or model configuration artifact.
- The payload-sequence input is not equivalent to the strict-v4
  payload-free flow-statistics table. A tabular adapter would not be an
  OpenCBD reproduction.
- The random selection of consecutive packets requires a capture/session
  group mapping to prevent source-PCAP leakage. That mapping is not supplied
  as a reusable artifact.
- Therefore the paper contract is admitted for related work and a
  protocol-layering appendix, while native execution and strict-v4 main-table
  admission remain false.

## GPU data evidence

Candidate raw archives exist at:

`/opt/data/private/wangwt/ParkAttackKE/datasets/cic/iscx_vpn_nonvpn_2016/raw/PCAPs`

The five archives total 26,217,052,748 bytes:

- `NonVPN-PCAPs-01.zip`: 839,164,750 bytes
- `NonVPN-PCAPs-02.zip`: 12,698,509,108 bytes
- `NonVPN-PCAPs-03.zip`: 10,342,707,183 bytes
- `VPN-PCAPS-01.zip`: 670,550,834 bytes
- `VPN-PCAPs-02.zip`: 1,666,120,873 bytes

This proves dataset-candidate presence only. It does not prove the paper's
13-class sample construction, preprocessing, splits, or model artifacts are
reproducible.

## Current decision

- `paper_contract_admitted=true`
- `gpu_raw_dataset_candidate_present=true`
- `official_source_snapshot_admitted=false`
- `native_execution_admitted=false`
- `strict_v4_main_table_admitted=false`
- `appendix_protocol_candidate=true`
- `model_metrics_generated=false`
- `formal_baseline_count_increment=0`
