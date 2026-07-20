# HFT-MGBS

High-speed Full-Traffic Multi-Granularity feature extraction and adaptive Budget Scheduling。

本地目录是代码唯一编辑源：`F:\泉城实验室\二期\论文\异常检测\source\HFT-MGBS`。
远端工程根：`/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS`；共享数据集只从 `/opt/data/private/wangwt/ParkAttackKE/datasets` 读取。

## 已落地的最小工程闭环

- `hft_mgbs/features.py`：包/流/时间窗三级流式统计，深层载荷特征按需计算；
- `hft_mgbs/scheduler.py`：按优先级、实测成本 EMA、效用 EMA 和系统压力分配流级/深层预算；
- `hft_mgbs/optimization.py`：先执行丢包/P99/资源/关键流覆盖/回退硬约束，再计算 Pareto 前沿和 Champion；
- `hft_mgbs/pipeline.py`：基础特征全量抽取、昂贵特征渐进升级；
- `scripts/benchmark_synthetic.py`：无数据落盘的确定性合成吞吐烟测；
- `scripts/check_local_policy.py`：阻止数据、流量、特征、模型参数和运行产物进入本地目录；
- `tests/`：特征正确性、预算上界、压力反馈、管线降级与存储边界测试。

调度器支持关键流最低 tier 预留和 `allow_deep=False` 显式回退；`SchedulePlan` 会输出预算使用、越界次数、关键流覆盖和回退状态。

## 本地验证

```powershell
D:\soft\Anaconda3\python.exe scripts\check_local_policy.py
D:\soft\Anaconda3\python.exe -m unittest discover -s tests -v
$env:PYTHONPATH='.'
D:\soft\Anaconda3\python.exe scripts\benchmark_synthetic.py --packets 20000 --flows 1000
D:\soft\Anaconda3\python.exe scripts\benchmark_synthetic.py --packets 20000 --flows 1000 --disable-deep
D:\soft\Anaconda3\python.exe scripts\evaluate_pareto.py --smoke
```

真实 Pareto 评估使用 `evaluate_pareto.py --profile <约束JSON> --candidates <候选指标JSON>`。任何硬约束失败的候选不会进入 Pareto 前沿，即使其准确率更高。

远端只读 PCAP 基准入口为 `scripts/benchmark_pcap.py`；批量矩阵入口为 `scripts/run_remote_pcap_matrix.sh`。离线输出会显式标注证据范围，不把应用处理丢弃等价为 NIC 丢包，也不把批次处理 P99 等价为线上端到端 P99。

## 同步到 GPU

运行 `sync_to_gpu.cmd`。同步只包含代码、配置、测试和文档；远端随后在 Conda `py3.9` 中完成策略检查、编译、单测与合成烟测。数据/模型/特征缓存/性能剖析/运行结果不会回传本地。

当前版本是可执行的工程基线，不代表最终性能最优。后续优化必须以真实流量回放下的吞吐、P99 延迟、丢包率、特征收益和资源占用联合验收。
