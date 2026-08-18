# DPDK perf 证据路径与进程匹配纠正

## 问题

首次 5 Mpps perf 诊断在新运行目录创建前读取了 `ls -dt`，同时用会匹配
控制命令自身的 `pgrep -f` 表达式选取 PID。结果为：

- perf 附加到了错误进程，没有采到样本；
- `perf.data`、`perf-report.txt`、`perf-evidence-sha256.txt` 被写入上一轮
  已完成证据目录
  `hft_r0_dpdk_20260731T014313443709656Z`。

原 `result.json`、`manifest.txt` 和 `evidence_sha256.txt` 未被覆盖。

## 纠正

- 在远端同一 shell 中只删除上述 3 个明确命名、由本次误操作新增的文件。
- 重跑前保存旧的最新目录，轮询直到出现不同的新 `hft_r0_dpdk_*` 目录。
- 用 `[h]ft-dpdk.bin --capture-pci` 模式避免进程选择表达式匹配自身。
- 只有确认新目录和真实 DPDK PID 后才启动 perf。
- perf 轮为诊断证据，不进入吞吐或 Pareto 结果。

## 验证

- 纠正后旧证据目录不包含 3 个误投文件。
- 旧 `result.json` 和 `manifest.txt` 的 SHA-256 保持：
  - `a08eb6edf32b629c04a14043db9f687cb865655283d592ef821292b8624c84ce`
  - `45ea1c58cdd492b1ddca100f054038d312a9caee4ce876aa963837f303cb2dd6`
- 新 perf 报告必须包含非零 samples，否则继续判为无效诊断。
