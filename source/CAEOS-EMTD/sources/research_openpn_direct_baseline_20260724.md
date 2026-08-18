# OpenPN direct-baseline admission audit

更新时间：2026-07-24

## 结论

OpenPN 是 2026 年正式发表的直接网络开放集识别工作，但当前只能准入相关工作，不能计入 strict-v4 可执行主表。出版社页面为受限访问，OpenAlex 明确记录 `closed`、无开放 PDF、无仓储全文；按 DOI、完整标题和方法名执行的 GitHub 仓库检索均为 0，公开网页检索也未确认作者实现。这里的结论是“截至本轮未能验证作者代码”，不是“代码绝对不存在”。

出版社摘要足以确认两层框架边界：第一层 OpenPN 对已知流量分类并识别未知流量；随后专家确认未知候选，使用密度型 k-reciprocal nearest-neighbor 聚类优化，并对确认为新攻击的类别持续学习。因此，论文整体系统不是 strict-v4 的静态、零未知暴露训练协议。第一层 OpenPN 本身仍是有价值的直接基线候选，但在全文或作者代码可用前，无法审计其模型、损失、阈值、三套数据集身份、类别表、拆分、种子以及是否消费 unknown/test 进行选择。

## 官方身份

- 题名：An expert-in-the-loop framework for unknown attack detection via open-set recognition
- 作者：Xinjing Yuan、Peiran Yu、Song Liu、Zhe Sun、Yu Zhang、Jingdong Xu
- 期刊：Journal of Computer Security
- 卷期页：34(3), 193-210
- 首次在线：2026-02-10
- DOI：`10.1177/0926227X251414058`
- 出版社页面：https://journals.sagepub.com/doi/abs/10.1177/0926227X251414058
- DBLP key：`journals/jcs/YuanYLSZX26`
- OpenAlex work：`W7128482163`

## 可验证与不可验证边界

可由出版社摘要直接验证：

1. OpenPN 用于已知网络流量分类与未知流量识别。
2. 后续攻击发现过程包含专家验证。
3. 优化过程包含密度型 k-reciprocal nearest-neighbor 聚类。
4. 被专家确认为新攻击的类别进入持续学习。
5. 论文报告在三套公开数据集上的实验。

当前不可由公开证据验证：

1. OpenPN 网络结构、损失与风险公式。
2. 三套数据集名称、版本、预处理及固定类别表。
3. 训练/验证/测试划分、随机种子与 group-disjoint 约束。
4. 阈值来源及 unknown/test 是否参与选择。
5. 是否能映射到无 payload 的 strict-v4 流级表格输入。
6. strict-v4 六指标与同拆分配对复现。

## 代码检索

2026-07-24 UTC 使用 GitHub repository API 执行以下查询：

| 查询 | repository 结果数 |
|---|---:|
| `0926227X251414058` | 0 |
| 完整论文标题 | 0 |
| `OpenPN "unknown attack"` | 0 |

GitHub code search 需要认证，本轮未把未认证的 `401` 当作“代码搜索通过”。另以完整标题、DOI、OpenPN 和作者名执行公开网页检索，未定位作者仓库。负检索只支持“未验证到”，不支持存在性否定。

## strict-v4 准入

| 层次 | 决策 | 原因 |
|---|---|---|
| 论文身份 | 准入 | 出版社、DBLP、OpenAlex一致 |
| 相关工作 | 准入 | 直接网络开放集与专家闭环具有可比价值 |
| 完整 OpenPN 框架主表 | 不准入 | 专家确认未知类后持续学习，违反静态零未知暴露边界 |
| 第一层静态 OpenPN | 条件候选 | 需全文或作者代码后重新审计 |
| 原生执行 | 不准入 | 全文、代码、配置、拆分与数据身份不完整 |
| 表格低保真适配 | 不准入 | 方法公式不可核验，适配会变成自定义方法 |
| 正式方法增量 | 0 | 无模型指标，不计数、不排名 |

机器证据位于 `results/strict_v4_openpn_direct_baseline_audit/`。在获得全文或可验证作者代码前，不创建 GPU 训练任务，不占用正在运行的 Pairwise 比较链资源。

## 机器证据

- evidence canonical：`0f85e55e86f68f819c79aa6ac1122e7b66754c438c48055051d97cf9423b77fa`
- evidence file：`87efb3c71a9a8a49dcaeeca03287ce23260eb8aac7a4dec92a24142b1625946d`
- audit canonical：`a5a0248aced548c68c1b1dabf08c6cd072ea1b43ad9d4307c8502bc7203c3505`
- audit file：`9245cd2bf24f790ee75b3ab5a1bc660b942ecceb006c5598d3a253945040141a`
- auditor SHA：`a8603341f117c3934aae72bf652c89160a0ceee1e9b4688787e5baf828e3d31c`
- test SHA：`774525c95d83764c7ec99296969ff12fd831f9f3815fab9caefde01c3622b971`
- 本地/GPU定向测试：`6/6 PASS`
- `native_execution_admitted=false`
- `strict_v4_main_table_admitted=false`
- `baseline_count_increment=0`
