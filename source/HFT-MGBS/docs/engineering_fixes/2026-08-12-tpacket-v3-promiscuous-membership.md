# TPACKET_V3 入口过滤修复

## 现象

首次非破坏性冒烟在 ens8f1 实发 303,104 个 64 B 测试帧，但 ens8f0 的四个
packet socket 统计总计只看到 60 个背景包，用户态只处理 10 包；ring drop 为 0。
测试帧目的 MAC 固定为 `02:00:00:00:00:01`，与 ens8f0 的 MAC 不同，而探针创建
AF_PACKET socket 时未申请混杂接收。

## 根因

XDP 入口探针在以太网目的地址过滤之前观察数据；AF_PACKET/TPACKET 依赖网卡与内核
入口接收策略。未启用混杂成员关系时，非本机 MAC 的回放帧不会进入 packet socket。
因此“只看到背景包且 drop=0”不能解释为 TPACKET 性能不足。

## 修复

- 在每个 HFT 自有 fanout socket 上使用 `PACKET_ADD_MEMBERSHIP` 申请
  `PACKET_MR_PROMISC`，不修改接口持久配置。
- socket 关闭时由内核引用计数自动撤销 membership；每次实验仍需独立检查
  `ip -details link` 中 `promiscuity 0`，否则不得判定恢复完成。
- 原始报告新增 `promiscuous_membership=true`，避免证据遗漏抓包语义。

## 资格边界

本修复仅解决测试帧入口可见性。首次失败冒烟保留在
`/home/wangwt/task/datasets/replay/hft_tpacket_v3_smoke_20260812T083000Z`，不删除、
不计为吞吐候选结果；修复后的运行仍须重新验证实发/接收、fanout 覆盖、drop、P99 和
退出后的混杂状态。
