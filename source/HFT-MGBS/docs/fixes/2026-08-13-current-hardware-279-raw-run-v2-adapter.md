# current-hardware 2.79 raw_run_v2 runner 证据适配器

## 修复目的

正式 normal/fallback 运行结束后，不再手工拼接 `raw_run_v2` 输入。新增适配器从 runner 证据目录自动发现物理机原始文件，独立复核 runner `evidence.sha256` 的每一项，再把事后落盘的 GPU、逐窗、资源、身份和质量 artifact 组成新的 binding manifest，并调用 v2 composer 输出小型 sealed receipt。

本次没有修改 runner、Rust、unified/Pareto、v2 profile 或 v2 composer 模块。

## 自动发现的 runner 文件

适配器固定发现：

- `frozen/runner.sh`
- `frozen/config.json`
- `frozen/tpacket_v3_full_pipeline`
- `pipeline_raw.json`
- `diagnostic_receipt.json`
- `pipeline_ready.json`
- `execution_events.tsv`
- `before_ens8f0_statistics.txt`
- `pre_restore_ens8f0_statistics.txt`
- `pktgen_device_*.txt`
- `evidence.sha256`

每个自动发现文件既要重新计算 SHA-256，也必须出现在 runner 原始 manifest 中。适配器忽略 `evidence.sha256.check` 的自报文本，直接重新读取和重哈希 manifest 全部条目。任一条目缺失、漂移、符号链接、路径越界或重复时，适配过程以 exit 3 中止。

## 必须事后落盘的分布式证据

下列 artifact 必须以真实文件形式预先放在同一远端 `binding_root` 内，再通过参数引用：

- `--model`
- `--runtime-manifest`
- `--service-source`
- `--engine-source`
- `--service-launcher`
- `--identity-receipt`
- `--window-observations`
- `--physical-resources`
- `--service-resources`
- `--quality-labels`
- `--quality-predictions`
- fallback 模式额外需要 `--fallback-events`

适配器不会从目录名生成 run/generator identity，不会把汇总 `mpstat` 复制成逐窗双节点资源，不会从汇总延迟分位数扩增逐窗样本，也不会从 synthetic 流量生成 label/prediction。缺项会写入 `evidence_gaps`，composer 同时给出对应严格错误，receipt 保持 `run_qualified=false`，CLI 返回 exit 2。

## 运行方式

建议在物理机的单次证据目录中建立全新的工作子目录，并先把 GPU 端的冻结 artifact 安全复制到该证据目录的 `staged/` 子目录；数据、模型和运行证据仍只留远端，不同步到本地代码目录。

```bash
python3 scripts/compose_current_hardware_279_raw_run_v2.py \
  --profile configs/current_hardware_2_79_release_profile_v2.json \
  --evidence-dir /home/wangwt/task/datasets/replay/hft_current_279_tpacket_<run> \
  --binding-root /home/wangwt/task/datasets/replay/hft_current_279_tpacket_<run> \
  --work-dir /home/wangwt/task/datasets/replay/hft_current_279_tpacket_<run>/v2_binding_normal_r1 \
  --campaign-id current-hardware-279-<campaign> \
  --candidate-id tpacket-v3-current-hardware \
  --backend tpacket_v3 \
  --mode normal \
  --repeat-index 1 \
  --model staged/a09_bundle.joblib \
  --runtime-manifest staged/runtime_manifest.json \
  --service-source staged/gpu_service.py \
  --engine-source staged/a09_numpy_inference.py \
  --service-launcher staged/start_gpu_service.sh \
  --identity-receipt staged/run_identity_receipt_v2.json \
  --window-observations staged/window_observations_v2.json \
  --physical-resources staged/physical_resources_v2.json \
  --service-resources staged/service_resources_v2.json \
  --quality-labels staged/independent_labels.json \
  --quality-predictions staged/independent_predictions.json
```

工作目录产生三个小文件：

- `raw_run_v2.binding.sha256`：重新绑定 runner 原始文件和所有 staged artifact；
- `raw_run_v2.input.json`：仅包含身份、路径和即时重算 SHA-256；
- `raw_run_v2.json`：最终派生计数、质量指标、窗口摘要、hash binding、错误/缺口，不嵌入逐样本数组或标签记录。

工作目录必须新建或为空，防止覆盖旧运行。所有引用必须位于 `binding_root` 内且不能是符号链接。

## 验证

新增 4 个 adapter 测试：完整 staged 证据可直接得到小型合格 receipt；缺失 service resource 明确 fail closed；runner manifest 后文件漂移在 composition 前中止；CLI 在缺失 GPU/逐窗/质量证据时返回 exit 2 并写出逐项 `evidence_gaps`。这些测试使用真实 composer，不通过 mock 绕过 v2 hard gates。
