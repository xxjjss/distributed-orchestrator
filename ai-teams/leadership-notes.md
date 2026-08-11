# Leadership Reviewer Notes

> 用途：领导层评审知识库。每轮评审前后持续追加，不覆盖历史。

## 1) 关注框架（固定）

- 公司战略匹配：是否贴合 Salesforce / Tableau 近中期战略方向。
- 资源投入回报：预算、人力、机会成本是否值得。
- 叙事吸引力：是否能在 3-5 分钟内抓住高层兴趣。
- 收益可衡量性：是否有明确业务指标（收入、效率、生态联动）。
- 执行可控性：是否可分阶段推进、先小范围验证再扩大投入。

## 2) Salesforce / Tableau 基础认知（长期维护）

### Salesforce
- 核心平台：CRM + Data Cloud + Agentforce + 行业云。
- 价值主线：统一客户数据、自动化流程、提升销售与服务效率。
- 常见领导层关注点：AI 价值落地速度、企业级可治理性、生态扩展能力。

### Tableau
- 核心定位：分析与可视化平台，强调自助分析、数据驱动决策。
- 与 Salesforce 协同：与 CRM/Data Cloud 场景联动，支持业务闭环与决策提速。
- 常见领导层关注点：跨团队采用率、洞察到行动的转化效率、平台治理成本。

## 3) 信息采集清单（每轮执行）

- 公开网页：官网产品页、投资者相关页面、官方博客/发布说明。
- Slack channel：产品策略、客户反馈、跨团队协作讨论（若有权限）。
- 公司内部搜索：roadmap、内部分享、项目复盘、经营指标相关文档（若有权限）。

## 4) 评审输出偏好（写作约束）

- 优先呈现“为什么值得投”而不是“如何实现”。
- 技术内容只保留对决策有影响的部分（风险、成本、依赖、节奏）。
- 每条建议尽量给出“可执行动作 + 预期收益 + 验证指标”。

## 5) 变更记录（追加）

- 2026-08-10：初始化 leadership reviewer 知识库模板。

### 2026-08-10 — V2 评审前的战略语境采集（首轮领导层评审）

**Agentforce = 当前 Salesforce 头号战略（公开信号，salesforce.com/agentforce）**：
- 定位「limitless digital labor force」——把 AI 从 chatbot 升级为 24/7 自主推理的「数字劳动力」。
- 明确提供 **multi-agent orchestration**（「build a collaborative AI agent team」）与 **MCP 互操作**（连接外部工具/资源）。
- 技术底座 Atlas Reasoning Engine（拆解任务、生成执行计划）；信任面 = Data 360 grounding + Einstein Trust Layer。
- 商业模式 = **消费型计费**（Flex Credits / Conversations / per-user），从 Salesforce Foundations 免费起步降低采用门槛，主打「可度量 ROI」。
- 市场证明点：18K+ 企业已上 Agentforce；Gartner 2026 会话式 AI MQ Leader；G2 #1。

**对本项目的战略含义（评审用）**：
1. **强正向对齐**：本项目「让任意 agent 7×24 可靠长跑 + 断点续跑 + 人机闭环」正是「数字劳动力」叙事缺的**运行时/编排运维层**。与公司头号战略同向，这是最大加分项。
2. **build-vs-leverage 风险（最尖锐的领导层问题）**：Agentforce 自身**已宣称 multi-agent orchestration + MCP**。本项目主张「互补而非竞争」（做 Platform 外 durable 运行时），但领导层会问：**这是否与 Agentforce/Platform 团队正在自建的编排能力重叠/重复投资？** 报告 §2d 给了技术桥，但「不重复投入」需战略层背书（呼应 OQ-3）。
3. **消费型计费 = token 成本敏感**：公司战略已把 LLM 成本/ROI 摆上台面，本项目 §3a 的 token 预算护栏与「每-WI 成本上限」正对领导层胃口——继续强化「可度量单位经济学」。
4. **Trust Layer / Hyperforce 是商用硬门槛**：任何触客户数据的商用化都要过 Einstein Trust Layer + Hyperforce 多租户——报告已列为远期前置门槛，方向正确。

**Slack channel 内部讨论**：本轮 Slack MCP 未授权，内部方向信号未采集；下一轮若授权应核对 Agentforce 编排 roadmap 与本项目是否 owner 重叠（build-vs-leverage 的关键实据）。
