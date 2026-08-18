# GPU SSH 合同统一为 25696 / 120 秒

## 问题

GPU 入口已经切换到 `10.0.5.103:25696`，且本机 SSH 配置会自动申请转发，实际连接
存在百秒级抖动。两个同步脚本虽然已经使用 25696，但仍固定 `ConnectTimeout=15`；
`tests/test_sync_contract.py` 又仍断言旧端口 25150。这会同时造成真实连接过早失败和
回归测试误报。

## 修复

- `sync_to_gpu.cmd` 与 `sync_split_deployment.cmd` 的所有 SSH/SCP 入口统一为
  `ConnectTimeout=120`；
- 保留 `BatchMode=yes`、`IdentitiesOnly=yes` 和 `ClearAllForwardings=yes`，不申请
  RemoteForward 9999，也不绑定额外本地地址；
- 回归合同统一断言 GPU 端口 25696，并拒绝残留 15 秒超时。

## 验证边界

本轮 GPU 主机的最窄 `hostname + project directory` 探测仍在 120 秒后无输出并退出
非零，因此代码没有同步到 GPU，50051 服务也没有被重启或修改。物理机与本地已完成
同步和回归；GPU 状态保持未验证，而不是把连接超时解释为服务停止。
