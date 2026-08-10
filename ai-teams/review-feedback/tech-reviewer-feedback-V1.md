# Tech Review — V1

**总评分：6.7/10**（六项等权加权平均；0–10 制。换算百分制 = 67/100）
**一句话结论：** 需改进但明确可行 —— 作为「立项可行性报告」诚实、边界清晰、选型调研扎实；扣分集中在**熔断/背压缺失、异构 runtime 调用机制与 agent 互操作标准（MCP/A2A）欠展开、局部失败的 UX 未设计、以及未回应 Salesforce 既有编排原语（Flow Orchestrator）**。无一票否决项。

## 概述
V1 是首轮评审，无 human comment、无其他 reviewer 反馈、无我方上一轮记录，故本轮为基线打分、不涉及回归跟进。

整体判断：这是一份**质量高于平均线的可行性报告**。突出优点：
- **诚实**：3× 效率被明确降级为 n=1、归因未隔离的早期信号（D5）；「断网执行」收窄为「中断容错」（D1）；「无头」明确以「连接未过期」为前提（D2）；外部依赖（matrix/falcon、身份机制）与自研成本变量（OQ-1）都摆到台面。这在立项报告里罕见且加分。
- **选型调研达标**：§1d 四组件每组给了候选 + License + 稳定性/商用判断，符合「先调研再自研」的纪律。
- **抽象方向正确**：StateStore 接口 + handler 契约 + event envelope 提前到一期，与业界（Temporal/DBOS/LangGraph）收敛方向一致。

主要问题是：报告在「机制正确性」层面尚有真空——**熔断/背压、异构 worker 的实际拉起机制、局部失败的 UI 呈现、以及与 Salesforce 既有编排能力的关系**。这些不是致命缺陷，但应在 V2 收敛。

> 说明：六视角评审由 team leader 按 `tech_reviewer_team.py` 定义的六个专家视角统一应用与汇总（本环境未联网调用 Agno 运行时；各视角判据与该文件 instructions 一致）。

## 分项评审

### 1. 开源架构 — 7.5/10
- **优点**：§1d 的候选/License/取舍表是全文最扎实的部分；自研理由（合规不能引三方依赖 + 贴合 DynamoDB/SFN/outbox 既有栈）站得住；OQ-1 把「能否引 MIT 的 LangGraph/DBOS」标为一期最大成本变量，判断准确。
- **问题 / 风险**：
  1. **低估自研 durable-core 的工程风险**。即使合规禁止打包三方依赖，"正确"地自研持久化执行（幂等、恢复、非确定性重放、lease 竞态）是 Temporal/DBOS 花数年打磨的领域；报告把它当"技术已备好"，对 correctness 的长尾成本过于乐观。
  2. **候选集不全**。durable execution 漏了 Restate（https://github.com/restatedev/restate，注意 BSL 授权，商用需评估）、Inngest（https://github.com/inngest/inngest，durable functions）、Windmill（https://github.com/windmill-labs/windmill，AGPL，商用授权风险须显式标注）。
  3. **Watcher = watch-pr 泛化 = 重造轮子的隐忧**：轮询式 watcher 在"已有 webhook"的源（GitHub/Slack）上是倒退。应优先 webhook/事件推送，或复用连接器框架（Benthos / Redpanda Connect https://github.com/redpanda-data/connect），仅在无 webhook 的源退回轮询。
- **建议**：V2 给「自研 vs LangGraph（MIT，https://github.com/langchain-ai/langgraph）/ DBOS（MIT，https://github.com/dbos-inc/dbos-transact-py）」一个量化的工时/风险对照，并把 Restate/Inngest/Windmill 补进候选表与 License 结论。

### 2. 分布式系统架构 — 7.5/10
- **优点**：单一事实源 = 云端 DynamoDB + lease/CAS 乐观锁、workid 兼幂等键（exactly-once 提交）、SK=`{branchId}#{stepIndex}` + `Query(PK)` 拉全树——访问模式清晰，且已在 TCM/URS 生产验证。把本机 SQLite 明确降级为「非事实源的性能 checkpoint」、放弃本地双向同步（避免 CRDT）是正确的 CAP 取舍（隐式选 CP），且诚实。
- **问题 / 风险**：
  1. **去重键机制未落地**。envelope 有 `dedup-key`，但没有说明**在哪里、用什么条件写来保证 signal 的幂等投递**。crash 发生在 watcher fire 与 callback 之间时，事件可能重放；fan-out 类事件重放会**重复 spawn 子分支**。需要一张 dedup 表 / 基于 dedup-key 的条件写。
  2. **liveness 缺口**：`affinity=machine:X` 而 X 永久离线 → 任务"只告警不拉起"会**永久卡死**，无重分配/迁移机制。应设计人工/自动改派 affinity 的路径。
  3. **热分区**：超大任务树共享单一 PK，`Query(PK)` 与写放大有热分区风险（DynamoDB 单 item-collection 10GB 上限一般够，但吞吐热点需评估）。
- **建议**：V2 补「signal 幂等/去重」的具体写路径与 dedup 存储，并补 affinity 永久失配的改派策略。参考 DBOS check-then-execute（https://github.com/dbos-inc/dbos-transact-py）。

### 3. SRE 容错 — 6.5/10
- **优点**：断点续跑（daemon 重扫 + 云端事实源）是全篇最强的容错论证链；attemptCount 阈值转终态、retryable(Saga) 语义、lease 过期回收都到位。SPOF（本机 daemon、MCP 过期）被诚实标注（R1/R4）。
- **问题 / 风险**：
  1. **无熔断/背压/隔离**。编排器会 fan-out 昂贵的 LLM 调用；当某外部系统（GUS/Slack/Pod/LLM API）故障时，没有 circuit breaker / bulkhead / 限流退避，会**烧 token 空转并放大故障**。TCM 自身「一个 Pod 故障拖垮所有 Pod（noisy neighbor）」的教训直接适用，报告未吸收。
  2. **"7×24 无人值守"与"一期主力 = affinity=machine 本机 worker"存在标题级张力**：核心卖点的可用性被"某台笔记本是否开机"封顶。报告在正文分散承认，但应在执行摘要就把这条张力讲透。
  3. **manager 自身 HA 未言明**：云端 manager 是否多实例？轮询模型允许任意实例扫描（利好），但需明确"manager 非 SPOF"。
- **建议**：V2 增设「熔断/限流/退避」小节（可复用 TCM 的 200 任务背压 + Lock TTL 模式），并明确 manager 多实例 + affinity 分区下的扫描竞争规则。参考 resilience4j（https://github.com/resilience4j/resilience4j）。

### 4. 异构通信协议 — 6.0/10
- **优点**：handler 契约（enter+route）+ 统一 envelope 是合理的互操作层；worker 形态无关（agent/skill/SFN/脚本）抽象方向对；OQ-2（matrix 身份 a/b）作为关键鉴权岔路被清晰标注。
- **问题 / 风险**：
  1. **异构 runtime 的"实际拉起机制"缺失**。这是"异构编排"的核心：云端 manager 如何**统一地**拉起一个 Claude Code agent vs 一个纯脚本 vs 一个 Step Functions？报告只说了 enter/route 契约，没说 invocation/adapter 机制——这是最该展开却最薄的一环。
  2. **未定位 agent 互操作标准**。一份自称"分布式 AI agent 编排 OS 层"的报告，全篇未提 **MCP（工具互操作，已成事实标准）与 A2A（Agent2Agent，https://github.com/google/A2A）**。应说明本编排器与这两条标准的关系（是消费方？是 A2A 的编排上层？）。
  3. **MCP adaptor 是鉴权单一通道的瓶颈**：MCP 未覆盖的鉴权类型（某些 service account / 自定义 token）如何接？未讨论。
- **建议**：V2 增「worker runtime adapter」小节（不同形态如何被统一 enter/route 拉起），并显式定位 MCP（https://modelcontextprotocol.io）+ A2A 与本编排器的边界。

### 5. 分布式 UX — 6.0/10
- **优点**：sticky-note + 通知/审批入口的人机闭环方向正确；"把恐怖 CLI 挡在用户之外"抓住了终端体验的要害；append-only 审计轨迹作为产品分析数据的洞察很好。
- **问题 / 风险**：
  1. **局部失败/高延迟的 UI 呈现——分布式 UX 最难的问题——只被断言未被设计**。data model 有 `progress` 枚举，但"N 个任务中 2 个 waiting、1 个 error(retryable)、1 个 MCP 过期需 Reconnect"如何被可理解地呈现，没有交互模型/线框。
  2. **最可能发生的两个状态（笔记本关机导致 machine worker 停摆、MCP OAuth 过期）如何通知用户并引导 Reconnect**，恰恰没设计——而这是一期实际运行中最高频的"部分失败"。
  3. sticky-note 目前仅 macOS 桌面（限触达，一期内部可接受，但商业化需说明）。
- **建议**：V2 给出 progress 枚举 → UI 状态的映射表 + 一张"多任务健康度/待办/需 Reconnect"面板线框；把"stall/过期→通知→一键 Reconnect"作为一期显式 UX 交付。

### 6. Salesforce 产品 — 6.5/10
- **优点**：§2d 耦合表有想法；**Agentforce-as-底座**定位（Agentforce 造 agent，本项目让 agent 可靠长跑并被编排——互补非竞争）战略上准确且有说服力；一期耦合刻意松（GUS 输入 + MCP 访问），锁定风险低，适合可行性阶段；扩展点（StateStore/handler/envelope）提前到一期，利好后续 SF 复用。
- **问题 / 风险**：
  1. **回避了 Salesforce 既有编排原语**。SF 已有 **Flow Orchestrator**（平台级工作流编排 + 人工审批步骤）、**Platform Events**、以及 Agentforce 自身的 orchestration。报告应正面回答"为何不在 Flow Orchestrator / Platform Events 上构建，而另起一个 DynamoDB 引擎"——这是最大的 SF 产品契合度问题，却未触及。
  2. **Trust / 合规缺位**：LLM worker 操作客户数据必过 **Einstein Trust Layer**（脱敏/审计/零留存）；商业化章节完全未提，这在 SF 是硬门槛。
  3. **多租户/数据驻留**：共享云表在 Hyperforce 下的租户隔离与数据驻留仅由 submitter 隔离粗略覆盖，未达 SF 产品级。
- **建议**：V2 增「与 Flow Orchestrator / Platform Events 的关系（互补/替代/桥接）」+「Einstein Trust Layer 接入」+「Hyperforce 多租户」三段。参考 SF Flow Orchestrator 文档（https://help.salesforce.com/s/articleView?id=sf.flow_concepts_orchestrator.htm）。

## 关键建议（按优先级）
1. **补齐容错的机制真空（P0，视角 3）**：熔断 / 限流 / 背压 / bulkhead——否则 fan-out LLM 调用在下游故障时会烧钱放大故障。复用 TCM 200 任务背压 + Lock TTL 经验。
2. **落地 signal 幂等/去重与 affinity 永久失配的改派（P0，视角 2）**：给出 dedup-key 的具体写路径 + 卡死任务的改派机制，堵住 exactly-once 与 liveness 两个洞。
3. **展开异构 runtime 的 adapter 机制并定位 MCP/A2A（P1，视角 4）**：这是"编排 OS 层"命题成立的关键，也是与业界标准对齐的必答题。
4. **正面回应 Salesforce 既有编排原语（P1，视角 6）**：为何不用 Flow Orchestrator + 补 Einstein Trust Layer，决定 SF 产品化叙事是否成立。
5. **设计局部失败/高延迟的 UI 呈现（P1，视角 5）**：progress→UI 映射 + stall/过期→通知→Reconnect 闭环，把一期 UX 从"断言"变"设计"。

## 未解决 / 待 writer 回应的问题
- [ ] OQ-1（合规能否引 MIT LangGraph/DBOS）—— 一期成本最大变量，建议报告给出量化对照而非仅标注。
- [ ] 熔断/限流/背压方案缺失（P0）。
- [ ] signal 去重键的具体机制、fan-out 事件重放的双重 spawn 防护（P0）。
- [ ] `affinity=machine:X` 永久离线任务的改派/迁移路径（liveness）。
- [ ] 异构 worker runtime 的统一拉起（adapter）机制；与 MCP / A2A 标准的定位。
- [ ] 与 Salesforce Flow Orchestrator / Platform Events 的关系；Einstein Trust Layer；Hyperforce 多租户。
- [ ] 局部失败/高延迟的 UI 交互模型（含 MCP 过期 → 引导 Reconnect）。
- [ ] "7×24 无人值守" 与 "一期主力 = 本机 worker（受笔记本开机封顶）" 的张力，建议在执行摘要显式讲透。
