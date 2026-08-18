# A09 独立质量证据导出 v2 修复记录

日期：2026-08-13  
范围：仅代码、测试和文档；未训练模型、未启动服务、未运行远端 PCAP 或网卡流量。

## 问题与根因

旧的候选导出脚本不是可用于 current-hardware 2.79 v2 的正式质量证据链：

1. `max_packets/max_flows/tolerance` 等评价参数暴露为 CLI，允许在看过 outer-unknown 指标后重跑挑参。
2. 任意运行清单只要自称 A09 并绑定某模型就可作为身份根，不能证明这是本轮冻结服务。
3. 模型、运行清单、PCAP、GT、输入哈希清单在校验与读取之间可漂移；实际 Python import 也可能被 `PYTHONPATH` 替换。
4. labels 以 GPU 绝对路径引用来源，复制到物理节点后引用失效。
5. 旧 `event_id` 将一条 flow 匹配的多个 GT 行合并，而且只把已抽中、已匹配事件放入分母，漏掉未匹配 eligible 官方事件，导致 event recall 结构性偏高。
6. 多文件逐个写入最终目录，失败时可能留下 labels-only 或 labels+predictions 的半成品。

## 修复内容

- 导出 CLI 只接受数据/受信根位置：必须同时提供 `trusted prepare receipt SHA-256`、`trusted campaign contract SHA-256` 和当前 exporter 源码 SHA-256。模型与 runtime 路径只能从 prepare receipt 的冻结副本解析。
- 抽取策略固定为合同值：batch 512、budget 5000us、safety 0.50、max packet 50000、max flow 5000、deep on、key ratio 0.10、payload 256、alignment tolerance 0。不存在对应调参 CLI。
- 深校验 A09 candidate、三 seed、每 seed 200 棵树、positive class index、阈值有限且位于 `[0,1]`、holdout/training/input-manifest SHA、所有实际 import 模块路径与 campaign-bound SHA。
- 开始/结束重算 exporter、prepare 全部冻结工件、合同/依赖源、input manifest、holdout、GT 与三份 fresh PCAP；任一漂移即失败。
- `sample_id` 使用规范化双向五元组、group 和起止时间；反向流同 ID，不同会话时间不同 ID；NaN/Inf、反转时间和重复 ID 均拒绝。
- labels/predictions 升级为 schema v2。新增完整 `eligible_events`（按每份冻结 PCAP 的实际 packet span 从官方 GT 行得到）以及多对多 `sample_event_relations`。consumer 使用完整 eligible inventory 作为 event recall 分母，未匹配事件成为真实 FN。
- 输出内含可搬运 `official_quality_source.json`，嵌入冻结 input-hash manifest、官方输入 hashes/sizes、eligible inventory 和 relations。collector 在 finalize 时复制并重验它；adapter 将其加入 binding manifest。
- sibling staging 目录内生成 source、labels、predictions、receipt、manifest、COMPLETE；全部完成并 fsync 后才原子 rename。异常清理 staging，最终目录不存在。
- exporter 的 `quality_qualified` 固定为 `false`。导出只产生独立逐样本证据，是否过门由 current-hardware consumer 重新计算；禁止从历史 summary 反推，也不调用 `.fit`/`.fit_transform`。

## v1/v2 兼容边界

- consumer 保留 legacy profile（未声明 `artifact_schema_version`）对 schema v1 fixture 的原语义。
- 正式 `current_hardware_2_79_release_profile_v2.json` 显式要求 `artifact_schema_version: 2`，因此旧 schema v1 不能在正式 v2 profile 中误过。
- collector 可校验/搬运 v1 历史输入，但 schema v2 启用 portable source、eligible inventory、relation 守恒与重复拒绝。

## 正式 GPU 执行命令

先在 GPU 节点完成本轮只读 `prepare`，由控制端独立记录 receipt SHA；再运行：

```bash
cd /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS
/opt/data/private/wangwt/anaconda3/bin/conda run -n py3.9 python \
  scripts/export_a09_current_279_quality_evidence.py \
  --output-dir /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/results/current279-quality-v2 \
  --contract configs/algorithm_qualification_campaign_v1.json \
  --trusted-contract-sha256 2ea166044b6b7050c0c345ef6f7f537671d40169cfc02021dade6a2f38186941 \
  --trusted-exporter-sha256 ae21a18fdb324fe3b134f0bb481566826f099a6ea37d866636a3f376fc17d036 \
  --prepare-receipt /ABSOLUTE/PREPARE/prepare_receipt.json \
  --trusted-prepare-receipt-sha256 PREPARE_RECEIPT_SHA256_FROM_CONTROL_PLANE \
  --input-hash-manifest /ABSOLUTE/FROZEN/input_sha256.json
```

`PREPARE_RECEIPT_SHA256_FROM_CONTROL_PLANE` 不允许由同一 exporter 运行临时自算后自签，必须来自已冻结的 prepare 阶段/控制面记录。input manifest SHA 必须等于 A09 frozen search contract 中的 `4b0ac8b...1665`，否则导出 fail-closed。

## 成本与剩余边界

- 无训练成本。主要成本为三份 fresh PCAP 各读取前 50000 包、最多各 5000 flow 的特征抽取，以及约最多 15000 flow 的三模型 CPU inference。
- 预期单进程运行通常为分钟级；实际时间/峰值内存必须由正式 GPU 节点实测，本轮没有运行数据，不能给出已验证耗时。
- 该证据只证明冻结 A09 在独立 UNSW holdout 上的逐样本离线质量；不证明实时 GPU 加速、2.79 Mpps、fallback 质量等价或生产发布。

## 本地验证

使用本地 Python 3.7.6 做语法兼容和单元回归；项目正式目标仍为远端 Conda `py3.9`。

- `tests/test_a09_current_279_quality_export.py`: 9/9
- `tests/test_current_hardware_279_v2.py`: 10/10
- `tests/test_current_hardware_279_evidence_collector.py`: 12/12
- `tests/test_current_hardware_279_raw_run_adapter.py`: 4/4

没有执行正式远端数据导出，因此不存在 labels/predictions 正式结果；当前状态是“代码/TDD 完成，GPU 正式运行待执行”。
