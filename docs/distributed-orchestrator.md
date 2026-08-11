# 分布式 AI Agent 编排系统 — 文档索引

> **本文档已拆分**（应 human comment / PR #4）。原单一报告拆为两份交叉引用、内容互补的文档，
> 本页仅作**索引 / 导航**，不再承载正文。

## 两份主文档

| 文档 | 面向读者 | 覆盖内容 | 链接 |
|---|---|---|---|
| **技术设计文档** | 技术审核人 | 系统结构、各部分功能的**选型与实现**、机制正确性（熔断/去重/liveness/runtime adapter）、DynamoDB 元数据、与 SF 既有编排原语的关系、可外带 IP 内核边界 | [`distributed-orchestrator-tech-design.md`](./distributed-orchestrator-tech-design.md) |
| **可行性报告** | 产品审核 / 公司领导层 | 现状与痛点（why）、分期（一期推工具/二期推环境/长期推产品）、要实现的功能、带来的益处、竞品、商业前景、成本量化（人月/云资源/LLM token）、风险与 Open Questions | [`distributed-orchestrator-project-analyst.md`](./distributed-orchestrator-project-analyst.md) |

## 配套资料

- 底层状态机 / 持久化 / 幂等 / 恢复算法：[`工作流模版.md`](./工作流模版.md)
- 设计备忘（决策 D1–D5、Open Questions 收敛）：[`design-notes.md`](./design-notes.md)
- 图表源与渲染：[`diagrams/`](./diagrams/)（`v2-*` 为当前版本）

> **给评审的提示**：`presentation` 时人类评审员**只读上面两份主文档**，不读设计思路/备忘。
> 两文交叉引用——技术设计谈「怎么做」，可行性报告谈「为什么做、做成什么、值不值得」。
