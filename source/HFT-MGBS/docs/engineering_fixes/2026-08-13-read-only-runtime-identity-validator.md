# 双机运行时身份链只读校验器

## 问题

GPU 本机的 50051 health 成功只能证明端口上存在可响应服务，不能证明该 listener
就是 runtime manifest 声明的进程，也不能证明物理机 50052 反向链路已经形成。旧清单
PID、当前 listener PID、进程命令行和双机 socket 若未绑定，容易把孤立服务误报为生产链。

## 修复

新增 `hft_mgbs/runtime_identity.py`，对只读事实 receipt 重新计算结果，不接受人工
`verified=true` 覆盖。校验同时要求：manifest 期望/实测 SHA 一致；manifest PID、活进程
PID 和 50051 owner PID 一致；命令行、可执行文件和 cwd 完整；localhost health 成功且
无失败；物理机可达 50051；物理机 50052 同时存在 listener 和 ESTABLISHED 连接。
JSON 重复键、布尔值冒充 PID、缺失字段和任何不一致均失败关闭。

该模块只读取调用方提供的事实，不连接远端、不修改服务、不改 runtime manifest，也未
接入统一发布审计。`current_runtime_identity_v1.json` 固化本轮已观察事实：manifest SHA
漂移、PID 1857/1888 不一致、进程 cmd/exe/cwd 尚未绑定、物理机到 50051 被拒绝、50052
无 listener/ESTABLISHED，因此 `verified=false`。

## 验证

执行：

```text
python -m unittest tests.test_runtime_identity -v
```

测试覆盖完整正例、当前失败事实、listener owner 错配、缺少进程身份、health failure、
伪造 verified 声明和重复 JSON 键。
