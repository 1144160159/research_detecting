# GPU 服务真实 PID 与运行清单绑定修复

## 问题

GPU 节点的旧启动器用 `setsid conda run ... python` 启动服务。PID 文件与
`runtime_manifest.json` 记录的是 `conda` 包装进程 `1857`，而 50051 的实际监听者是
Python 子进程 `1888`。因此即使健康接口可用，也不能把清单、进程和监听 socket
组成同一身份链，停止逻辑还可能只处理包装进程。

## 修复

`scripts/start_gpu_service.sh` 现在直接执行冻结环境中的 Python 解释器，不再经过
`conda run`。启动器在发布 PID 文件和运行清单前同时验证：

- `/proc/<pid>/exe` 是冻结的 Python；
- cwd 是 HFT-MGBS Python 代码目录；
- 命令行精确包含模块、bind、connect 和模型参数；
- 50051 的 socket owner 与新进程 PID 完全一致；
- ready 标记已经出现。

PID 文件和运行清单均用临时文件加原子 `mv` 发布。清单额外绑定 Python、cwd、
命令行摘要、模型摘要及服务源码摘要。重启只允许停止通过上述身份检查的监听进程；
旧 `conda` PID 只有在证明是该监听进程的祖先时才允许清理，其他存活 PID 一律拒绝。

## 边界

本修复只解决服务生命周期和身份证据，不改变 A09 模型、阈值或算法。当前 A09 是
CPU ExtraTrees；运行时延仍必须独立实测，不能因 PID 修复而视为 2.79 Mpps
全流水线合格。
