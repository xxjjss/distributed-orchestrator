# Product Review — V1

**总评分：6.4/10**（四项加权平均，等权；`sfdc_architect` 视角部分不适用，见下说明后仍纳入加权）
**一句话结论：** 需打磨——作为「内部研发效率工具」立项理由扎实、诚实、有原型背书；作为「可商业化产品」尚处早期假设阶段，市场拥挤、需求未验证、商业路径与成本量化缺位。

## 概述

这是一份质量明显高于平均线的可行性报告：术语钉死、prior-art 调研到位（LangGraph/DBOS/Temporal/SFN 五候选取舍）、决策可追溯（D1–D5）、风险登记完整（R1–R7）、对 "3×" 效率信号做了极其诚实的降级（n=1 → ≥1.5× 试点判据）。这些都是加分项，且背后有可运行原型（wi-researcher/wi-worker + sticky-note），降低了从零风险。

但本轮打分标准衡量的是**商业可行性 + 客户实际需求 + 接受度**，不是文档质量。以这把尺子看：
- 一期（内部工程师效率）价值链条清晰、闭环最短，是全篇最可信的部分。
- 商业化（§2b/§2d/OQ-3）仍是「倾向内嵌 Agentforce」的战略假设，没有买方、没有定价、没有验证过的需求。
- 竞品交集（LLM-native + 本机/云端统一 + 信号驱动人机闭环 + 非专业用户编排）确实存在空位，但每一条单轴上都有强力免费开源竞品，且 Agentforce / LangGraph Platform / Temporal 正快速向"持久化可编排 agent"收敛——护城河有被时间窗口蚕食的风险。
- 成本/Token/工期量化几乎缺失（见分项 4），这是决策层立项最需要的数字。

因是 V1 首轮，无上轮遗留问题需跟进。

## 分项评审

### 1. Salesforce 架构与研发 (sfdc_architect_agent) — 6.5/10
- **视角适用性说明**：一期本质是 AWS/TCM-native 的编排基础设施（DynamoDB 单表 + SFN + SQS + MCP adaptor），**不触碰 Salesforce Platform（Apex/LWC/Flow）元数据模型**，因此 Governor Limits、AppExchange Security Review 对一期基本不适用。报告对此定位诚实。故本视角主要评估报告自称的战略落点——与 Agentforce/Platform 的耦合。
- 问题 / 风险：
  - §2d「Agentforce/Platform 编排底座」是全篇最具商业分量的主张，但**技术桥缺失**：没有说明编排器如何暴露为 Agentforce 的 Topic/Action、如何与 Prompt Builder / Flow invocable action / Data Cloud 对接、如何映射到 Platform 的多租户与 CRUD/FLS/共享模型。"互补而非竞争"目前是断言而非路径。
  - 共享云表的 per-submitter 隔离（R6）在一期用"云凭据按人隔离"最简方案可过，但一旦走向 Platform/多租户商用，这会撞上 SF 的租户隔离与数据驻留合规，属于比报告呈现更大的架构改造，建议在远期架构里显式点名。
  - `stateFingerprint` 做非确定性检测是好设计，但与 Agentforce 的 reasoning/planner 如何共存未提。
- 建议 / 替代方案（附链接）：
  - 在 §2d 增加一张「编排器 ↔ Agentforce」的接口草图（哪怕一段）：编排器作为 Agentforce Action 的长跑后端 / Flow 的 async 编排层。参考 Agentforce 能力边界：https://www.salesforce.com/agentforce/ ；Flow 编排现状：https://help.salesforce.com/s/articleView?id=sf.flow.htm
  - 若远期要进 Platform，提前评估 near-core / Hyperforce 数据驻留约束，避免 DynamoDB 单表事实源与 Platform 数据模型二次冲突。

### 2. FDE 交付与现场实施 (fde_strategy_agent) — 7.0/10
- 亮点：
  - **一期 Time-to-Value 极高**——需求方=使用方=反馈方（Dogfooding），且已有原型，这是全篇最强的可行性论据。
  - §2c 把 FDE 当"真实客户用例的桥"、用审计轨迹（append-only）当产品分析数据，思路正确且低成本。
- 问题 / 风险：
  - **可移植性悬崖（本视角最大卡点）**：一期整个运行底座——鉴权（内部 MCP adaptor）、托管（内部 matrix/falcon）、输入源（GUS）、持久化（TCM 的 DynamoDB 栈）——**在任何客户现场都不存在**。StateStore 接口抽象只解决了"存哪"，没解决鉴权层/托管层/信号层的现场落地。FDE 把它带到客户 Org 时，需要替换的远不止一个 StateStore。报告应新增一节：编排内核中"可外带的 IP"（handler 契约、event envelope、状态机语义、路由注册表）vs"内部专属、客户现场需重写"（MCP 鉴权、matrix 托管、GUS watcher）的清单。
  - FDE 客户现场通常面对客户既有 Org Customizations（自定义对象、Flow、Apex 触发器），报告未触及编排器如何与客户遗留自动化共存/不打架。
- 建议 / 替代方案（附链接）：
  - 明确「可标准化 IP 内核」边界，把鉴权/托管做成可插拔 Provider（云端一套、客户现场一套）。参考同为"背景任务 + 人机闭环"且强调可移植运行时的开源实现：Inngest（https://github.com/inngest/inngest）、Trigger.dev（https://github.com/triggerdotdev/trigger.dev），它们的 SDK/Provider 分层可借鉴。
  - FDE 试点判据里加一条"非 Salesforce-internal 环境冒烟"（哪怕在一个干净 org / 空环境跑通最小内核），提前暴露可移植性债务。

### 3. B2B 商业前景与客户接受度 (business_adoption_agent) — 6.0/10
- 问题 / 风险：
  - **需求未验证**：一期无买方（内部），商用买方（CIO/VP/Admin）意愿完全是推断，报告自己也把它列为 OQ-3。没有定价逻辑、没有 willingness-to-pay 信号、没有目标客户画像。
  - **红海 + 时间窗口**：durable execution 与 LLM agent orchestration 赛道已由 MIT 开源主导（Temporal/LangGraph/DBOS/Restate/Prefect/CrewAI）。四条护城河里，"LLM-native 显式状态机"和"信号驱动人机闭环"正被 LangGraph Platform、Temporal（signals + human-in-the-loop）、Inngest 快速补齐；"本机/云端统一事实源"是较真的差异点，但客户是否为之付费存疑。ROI 仅靠 n=1 的 3×（已诚实降级），不足以支撑商用定价论证。
  - "内嵌 Agentforce"是聪明的 go-to-market（避开开源红海、借 SF 分发与身份），但也意味着商业成败高度绑定 SF 产品战略，本项目自身的议价权与独立商业价值被削弱——这一取舍的两面性报告只写了正面。
- 建议 / 替代方案（附链接）：
  - 一期就埋一个"付费意愿代理指标"：内部试点里记录工程师"愿不愿意让它托管更多工作流""愿意放弃盯屏多久"，作为 demand 的先行信号。
  - 做一页竞品定价/定位对照，明确"我们不与框架竞争、只在可靠运维+企业身份+非专家 UX 上取胜"。参考竞品：LangGraph Platform（https://www.langchain.com/langgraph-platform）、Temporal Cloud（https://temporal.io/cloud）、Inngest（https://www.inngest.com/）、n8n（远期图形化编排的强免费对手，https://github.com/n8n-io/n8n）。
  - 商业路径 OQ-3 建议在 V2 给出"独立 SaaS vs 内嵌 Agentforce"的二维打分（TAM、壁垒、分发、议价权），而非仅"倾向后者"。

### 4. 研发工程 Ops 与成本风险 (engineering_cost_agent) — 6.0/10
- 亮点：风险登记 R1–R7 诚实且可执行；最大成本单点变量（OQ-1：能否引 MIT LangGraph/DBOS 省掉自研持久化内核）识别精准；范围蔓延用"一期不做"清单守住（R7）。
- 问题 / 风险：
  - **成本量化基本缺席**：§3a 只有"以现有工程师小队为主"，无 headcount、无里程碑工期、无 DynamoDB/SQS 云成本估算。决策层立项最需要的数字恰恰没有。
  - **LLM Token 双重开销未测算（本视角硬缺口）**：一个 7×24、多 worker、无人值守、以 `claude -p` 回调驱动的编排器，Token 消耗可能是主成本项且随并发线性上升。报告通篇未给 Token 预算、无每-WI 成本上限、无熔断/预算护栏。这既是成本风险也是安全风险（失控循环烧钱）。
  - **运维/支持隐藏成本**：OAuth 过期 Reconnect 的人工 toil（R4）、watcher 维护、per-submitter 隔离运维、跨界告警的值班处理——只部分点到，未估人力。
  - matrix/falcon 是外部依赖且排期未定（R1/R2），把一期关键路径押在不受控的外部平台上，是最大交付风险，建议给出"matrix 不到位"的量化退路成本（自建 ECS/Fargate 的增量人力）。
- 建议 / 替代方案（附链接）：
  - V2 增加一张成本表：一期人月、里程碑、云资源月成本、**LLM Token 预算（按并发 worker 数 × 平均步数 × 单步 token 估算）**、每-WI 成本上限与熔断阈值。
  - Token 成本可借鉴 durable-execution 的"步骤级 memoization/replay"避免重复 LLM 调用——DBOS（https://github.com/dbos-inc/dbos-transact-py）与 LangGraph checkpointer（https://github.com/langchain-ai/langgraph）的 memoization 正是省 token 的关键，OQ-1 结论直接影响 Token 账单，建议把二者绑定评估。
  - 引入预算/护栏参考：把每 workid 的 attemptCount/token 上限做成硬约束（呼应现有 `attemptCount` 字段）。

## 关键建议（按优先级）
1. **补 Token/成本量化（P0，成本视角硬缺口）**：一期人月 + 里程碑 + 云成本 + LLM Token 预算 + 每-WI 成本上限/熔断。这是立项决策的核心数字，当前为空。
2. **画出可移植 IP 内核边界（P0，FDE 视角卡点）**：明确"可外带内核"vs"内部专属需重写"清单，鉴权/托管做成可插拔 Provider，否则 FDE→客户的商业故事落不了地。
3. **给 §2d 一条真正的 Agentforce/Platform 技术桥（P1）**：接口草图 + 多租户/合规前瞻，把"编排底座"从断言变路径。
4. **商业化 OQ-3 做二维打分（P1）**：独立 SaaS vs 内嵌 Agentforce 用 TAM/壁垒/分发/议价权量化，并在一期埋"付费意愿代理指标"。
5. **锁定 OQ-1 时间线（P1）**：能否引 LangGraph/DBOS 同时决定一期工作量与 Token 账单，建议标为立项前置阻塞项、给出向法务/架构确认的 owner 与 deadline。

## 未解决 / 待 writer 回应的问题
- [ ] 一期 LLM Token / 云成本 / 人月 / 工期的量化估算（决策层立项必需）。
- [ ] 编排内核"可外带 IP"vs"内部专属重写"的边界清单（FDE 可移植性）。
- [ ] 编排器 ↔ Agentforce/Platform 的具体技术接口与多租户/合规前瞻（§2d）。
- [ ] 商业化路径 OQ-3 的量化对照与目标客户/定价假设。
- [ ] 失控循环的 Token/成本护栏（每-workid 预算上限 + 熔断）设计。
