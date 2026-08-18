# Fastpath 首次定向同步路径修正留存

## 问题现象

首次把 `xdp_capture.rs` 与新二进制 `xdp_fastpath_probe.rs` 同一条 SCP 命令
发送到物理机时，公共目标误设为 `src/bin/`，因此远端短暂出现非预期文件：

`/home/wangwt/phase_2/code/HFT-MGBS/rust/hft-capture/src/bin/xdp_capture.rs`

## 根因

两个本地文件实际目标目录不同，但一次 SCP 只能使用同一个远端目标目录。
同步命令没有按目录拆分。

## 修正范围与验证

- 只删除上述精确的 HFT-MGBS 非预期文件，没有递归删除或触碰上游目录。
- 将 `src/xdp_capture.rs` 和 `src/bin/xdp_fastpath_probe.rs` 分两条命令同步到
  各自目录。
- 删除后执行 `test ! -e` 验证非预期文件不存在。
- 随后的 `cargo test` 全部 8 项通过，`cargo build --release` 通过，并成功
  构建 `xdp_fastpath_probe`。
- 只读上游 `traffic-analysis-platform/rust` 未修改。

## 防复发与遗留风险

以后跨目录文件禁止合并为一条 SCP；全量同步仍由目录感知且 fail-closed 的
`sync_split_deployment.cmd` 完成。该错误在编译和实验前被发现，没有产生
运行证据或配置漂移，遗留风险为无。
