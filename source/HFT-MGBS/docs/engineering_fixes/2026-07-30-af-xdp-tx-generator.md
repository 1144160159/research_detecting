# 修复：新增 AF_XDP TX 发生器候选

## 原因

`sendmmsg`、`PACKET_TX_RING` 和 TX coalescing 24/0 us 均未使 `bnx2x` 发送口超过约 2.8 Mpps。为避免把 AF_PACKET/Qdisc 路径的上限误判为网卡或抓包上限，新增一个受控 AF_XDP TX COPY-mode 候选。

## 实现

- 每个发送队列一个 NUMA 固定 Rust 工作线程。
- 每线程独占 AF_XDP socket、UMEM、TX ring 和 completion ring。
- 预构造 UMEM 内的 64 B Ethernet/IPv4/UDP 报文；运行时只提交描述符并回收 completion。
- 每个完成地址均进行范围、所有权和重复回收检查。
- 运行结束要求 2 秒内排空所有在途 TX descriptor，否则失败关闭。
- 输出独立记录后端、UMEM/ring 大小、逐线程 CPU、速率和 ring stall。

## 边界

当前网卡只支持 `XDP_SKB/XDP_COPY`，该候选仍不是 native zero-copy。只验证一次 5 Mpps；若无法明显越过 AF_PACKET 上限，立即淘汰并进入 native AF_XDP 网卡或经批准的 DPDK 路线。

## 验证结果

证据目录：`hft_r0_xdp_20260730T133857824025230Z`。

- 最低实发：2.778831 Mpps；平均：2.792222 Mpps。
- 发送/接收差值：0；网卡丢包：0。
- 原始 P99/P999：13/23 us。
- TX ring stall：208,374,956。
- `target_load` 硬门禁失败，候选淘汰。

该结果与 `PACKET_TX_RING` 的约 2.8 Mpps 上限一致，后续不再扩大 generic/COPY-mode 搜索空间。
