# 当前硬件 2.79 Mpps：A09 精确推理服务切换为 inline

## 问题

2026-08-13 的首轮 `TPACKET_V3` 全流水线诊断中，A09 仍使用
`numpy_exact`，但服务运行模式为 `prediction_execution=thread`。该轮只有
59 个小批次，Rust 侧 GPU/推理往返 P99 为 59.033 ms，无法用来证明
2.79 Mpps 闭环的 10 ms 尾延迟门。

## 单变量验证

在 10.0.5.103 上加载同一个冻结模型，固定 `MODEL_N_JOBS=1`、BLAS 线程数为
1、batch=8，各预热 30 次并执行 500 次：

| 模式 | 服务 P50 | 服务 P99 | 服务最大值 |
|---|---:|---:|---:|
| `thread` | 5.504 ms | 6.833 ms | 15.057 ms |
| `inline` | 4.781 ms | 5.222 ms | 6.418 ms |

`inline` 不更改模型、阈值、特征顺序或 `numpy_exact` 数值语义，只删除
`asyncio.to_thread` 的线程池调度开销。该服务同时只有一个反向推理流，故
在当前部署范围内采用 `inline`。

共享 CPU 集上的实际 500 次 batch=8 检查曾出现服务 P99 10.762 ms、往返
P99 12.006 ms。随后在同一主机只读扫描 CPU 利用率，CPU 6 的 5 个 1 秒样本
峰值为 1.98%；用 `taskset -c 6` 启动相同服务并重复 500 次，得到服务 P50/P99
为 4.904/5.182 ms、往返 P50/P99 为 5.703/6.021 ms。临时 55054 服务已按
PID、启动时钟和完整命令身份核验后清理。因此启动器只新增
`inline:6 -> inline_cpu6` 这一单 CPU 候选；每次正式运行仍须重新验证进程
亲和性、运行时身份和实测尾延迟，不能把本次空闲采样当作永久预留。

## 部署与身份

使用已有受控启动器执行：

```bash
INFERENCE_ENGINE=numpy_exact \
PREDICTION_EXECUTION=inline \
CPU_SET=6 \
RESTART=1 bash scripts/start_gpu_service.sh
```

加入 CPU 6 固定候选后，正式 50051 服务已重新部署并现场核验：

- PID：`1939474`
- `process_start_ticks=3258220341`
- 监听：`0.0.0.0:50051`
- CPU 亲和性：`6`
- runtime candidate：`inline_cpu6`
- health：`ok=true`、`failures=0`
- 模型 SHA-256：`fa9d29858bb7a20f9a66be2105a6182368e4b3029a59ead5fd77f6228b0eb5d2`
- runtime manifest SHA-256：`bdd5b251381037f41f53e1185ed34eadd7533e3917bb46a3682ca2f828e48b35`
- NUL 边界命令 SHA-256：`cca0134127beb170cbc74fb012436f49088468cb9a4ff0a27d1fbc7fd3ef948d`
- 启动器 SHA-256：`09f1acde695b2867416bbd6af09215ba898b19af08afbf9d4710515b58c7aab2`

按监听端真实“一连接一请求”协议重复 batch=8 共 500 次，服务内部 P50/P99 为
6.471/8.785 ms，最大值 9.747 ms；包含本机 TCP 建连和 JSON 往返后的 P50/P99
为 10.829/13.272 ms。正式 Rust 反向通道使用持久连接，因此闭环应以后续 Rust
原始 `gpu_roundtrip` 直方图为准，不能用本机逐请求建连时间替代。

上述数据只是运行时身份和单组件延迟证据。只有新的 2.79 Mpps 多流全流水线
实跑同时通过连续窗口、零 NIC/socket/internal drop、关键流守恒、资源和恢复门，
才能形成候选闭环回执。
