# Local/GPU synchronization policy

## Authoritative locations

- Local code source of truth: `F:\泉城实验室\二期\论文\异常检测\source\EACR-APT`
- Remote code mirror: `/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/source/EACR-APT`
- Remote datasets: `/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/datasets`
- Remote model parameters: `/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/models`
- Remote runs/results: `/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/runs` and `results`
- Remote manifests: `/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/manifests`

## Rules

1. Local stores source code, configuration, tests, documentation and small manifests only.
2. Datasets, captures, feature matrices, model weights, checkpoints, predictions, caches, logs and run directories stay on the GPU server.
3. Before every sync, run `scripts/check_local_policy.py`; any forbidden artifact blocks the transfer.
4. After every sync, remote Python syntax checks and unit tests must pass in Conda environment `py3.9` before an experiment starts.
5. Remote emergency edits must be copied back and reviewed locally before the next forward sync.
6. Only compact metrics, hashes and manifests may be copied back; never copy raw events, PCAP, feature arrays or model parameters into this folder.
7. Shared datasets are linked into the remote project; do not duplicate them merely to match a local directory shape.

The sync script is forward-only for code. It never deletes remote datasets/models and never downloads remote assets.
