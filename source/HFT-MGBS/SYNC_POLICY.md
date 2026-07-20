# Local/GPU synchronization policy

## Authoritative locations

- Local code source of truth: `F:\泉城实验室\二期\论文\异常检测\source\HFT-MGBS`
- Remote code mirror: `/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS`
- Shared remote datasets: `/opt/data/private/wangwt/ParkAttackKE/datasets`
- Remote feature caches/models/runs/results/profiles: `/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/{features,models,runs,results,profiles}`
- Remote manifests: `/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/manifests`

## Rules

1. Local stores source code, configuration, tests and documentation only.
2. PCAP/PCAPNG、原始流量、特征矩阵、模型权重、检查点、性能剖析和运行结果只保存在 GPU 服务器。
3. 每次同步前运行 `scripts/check_local_policy.py`；发现禁入文件即停止传输。
4. 每次同步后在远端 Conda `py3.9` 中执行语法检查、单元测试和合成烟测。
5. 同步为代码单向前推，不删除远端数据/模型，不把远端资产回传本地。
6. 只允许把小型指标摘要、哈希和 manifest 写入方向分析文档；不得复制原始数据和参数。
7. 共用数据集直接引用 `/opt/data/private/wangwt/ParkAttackKE/datasets`，不为目录外观重复复制。

远端 PCAP 矩阵使用 `scripts/run_remote_pcap_matrix.sh`。它只读取服务器数据集，结果写入远端 `runs/`、`results/` 和 `manifests/`，不会回传 PCAP 或大型产物。
