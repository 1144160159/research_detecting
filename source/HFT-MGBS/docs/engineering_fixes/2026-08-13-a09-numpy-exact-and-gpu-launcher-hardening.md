# A09 NumPy 等价推理与 GPU 启动器加固

## 范围与不变量

本次只优化冻结 A09 的运行时，不重新训练、不裁剪树、不改三成员、不改
`positive_indices`，也不改三个阈值及其中位数判定阈值。服务默认仍为
`sklearn`；只有显式设置 `INFERENCE_ENGINE=numpy_exact` 才启用新执行器。
当前 A09 仍是 CPU ExtraTrees 推理，部署在 GPU 节点不等于使用 GPU 计算。

## 等价执行器

`hft_mgbs/a09_numpy_inference.py` 在加载已经拟合的三模型后，把 600 棵树编译成
只读 NumPy 数组，以 batch×tree 同步遍历减少 sklearn 每棵树的调度开销。输入仍按
sklearn 路径转为 `float32`，每棵树、每个 forest 和三成员的加法顺序均与 sklearn
一致。编译器同时兼容旧 sklearn 的叶节点类计数和 sklearn 1.6 的归一化
`tree_.value`，并拒绝坏子节点、环、不可达节点、类别索引错误和非有限输入。

GPU 冻结 bundle 的实际验证环境为 NumPy 1.24.3、sklearn 1.6.1，模型 SHA-256 为
`fa9d29858bb7a20f9a66be2105a6182368e4b3029a59ead5fd77f6228b0eb5d2`。
实模探针包含 2,048 个随机输入和所有抽取分裂点的相邻 float32 值：概率最大绝对
误差为 0.0，字节一致为 true，阈值标签不一致数为 0。短跑 batch=8 P99 为
5.659 ms；最终发布前仍须按 500 次 batch=1/8 基准冻结正式 receipt。

## 服务和健康协议

`gpu_service.py` 新增 `--inference-engine sklearn|numpy_exact`。健康响应新增：

- `inference_engine` 与一次性 `engine_compile_us`；
- 启动加载前后重哈希一致的 `model_sha256`；
- 原有 `algorithm_device=cpu` 和冻结有效阈值保持不变。

部署前先运行 `scripts/benchmark_a09_numpy_inference.py`；它同时硬门概率字节一致、
标签一致和 batch 1/8 P99 不超过 10 ms。只有退出码 0 才允许用以下显式 opt-in：

```bash
INFERENCE_ENGINE=numpy_exact RESTART=1 bash scripts/start_gpu_service.sh
```

启动后必须通过 health 检查 `inference_engine=numpy_exact`、`model_sha256` 与冻结模型
相同，再重新生成运行身份探针和所有引用 `runtime_manifest.json` SHA 的 stage evidence。
旧清单不能沿用。

## 启动器终审与修复

终审确认的生命周期风险已经在 `start_gpu_service.sh` 收口：

- PID 信号前后绑定 `/proc/<pid>/stat` start ticks，降低 PID 重用 TOCTOU；
- dead stale PID file 对应的 `/proc/<pid>/stat` 不可读时返回空身份并继续正常
  启动，避免 `set -e` 在任何诊断前错误退出；只有仍存活 PID 才进入 ownership 门；
- 旧 conda 迁移同时要求包装命令、cwd、完整服务参数和监听子进程祖先链；
- TERM 超时后再次验证身份才 KILL，且等待退出；
- HUP/INT/TERM 以明确退出码走 EXIT cleanup，删除半成品并回收新进程；
- 模型解析为固定真实路径，拒绝加载期间 SHA 漂移；
- 原始 NUL 分隔 cmdline 直接做 SHA-256，不再以换行替换参数边界；
- runtime manifest v2 绑定进程 start ticks、launcher、服务源码、NumPy 引擎源码、
  engine、模型及运行参数；使用冻结 Python 写清单并 fsync 临时文件后原子替换；
- convenience model symlink 移到全部 ownership 拒绝门之后。

注意，manifest 与 PID 文件是两个独立原子文件，无法形成跨文件系统事务；消费者仍应
以 runtime manifest 为根，现场重验 PID/start ticks/socket/health，而不能只信 PID 文件。

## 验证

- `test_a09_numpy_inference.py`：黄金、随机、分裂边界、坏树和服务 opt-in；
- `test_gpu_service.py`：协议回归；
- `test_gpu_service_lifecycle.py`：legacy ownership、start ticks、signal/trap、原始
  cmdline hash、manifest engine/source 绑定和 mutation 顺序；
- GPU 上对脚本运行 `bash -n`，对冻结实模运行独立等价/延迟基准。
