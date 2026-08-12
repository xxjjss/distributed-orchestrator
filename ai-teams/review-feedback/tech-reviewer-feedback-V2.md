# Tech Review — V2

**总评分：7.6/10**（六项等权加权平均；0–10 制。换算百分制 = 76/100，较 V1 的 6.7 提升 +0.9）
**一句话结论：** 明确可行、显著改进 —— V2 把 V1 指出的四处「机制真空」（熔断/背压、signal 去重与 fan-out 防护、affinity liveness、异构 runtime adapter+MCP/A2A 定位）与两处产品面欠账（Flow Orchestrator 关系、局部失败 UX）**全部从「断言」补成了「设计」**，且拆分为技术设计 + 可行性两份文档、交叉引用干净。扣分集中在**新暴露的分布式二阶问题**（多实例引擎下熔断/背压/在飞计数的状态共享、热分区）、**adapter 契约仍停在清单级、缺跨大模型归一**、以及 **UX 仍无线框**。无一票否决项。

## 概述

评审对象为拆分后的两份文档，以**技术设计文档**（`distributed-orchestrator-tech-design.md`）为主、**可行性报告**（`distributed-orchestrator-project-analyst.md`）为辅。文档拆分本身是对 human comment 的正确回应，且未牺牲一致性（术语表、决策 D1–D5、图表 v2 全部同步）。

**V1→V2 回归评估（我方 V1 六个 P0/P1 + 遗留清单逐条）**：

| V1 遗留问题 | V2 处理 | 结论 |
|---|---|---|
| P0 熔断/限流/背压/bulkhead 缺失 | §2.1 全节新增（circuit breaker per-dependency、令牌桶限流+指数退避、URS 200 式背压、按 submitter/依赖分池 bulkhead、per-workspace `tokenSpent` 预算硬上限） | **已解决**（但引入新二阶问题，见分项 3） |
| P0 signal 去重键落地 + fan-out 双重 spawn | §2.2：`dedup-key` = `source#event-type#subject-id#跃迁标识` 做 `attribute_not_exists` 条件写；fan-out 子分支由父 SK+确定性序号派生 | **已解决**（残留：dedup 表 TTL/清理、跃迁标识跨重启确定性未展开） |
| P0 affinity 永久失配的改派 (liveness) | §2.3 + v2-affinity-scheduling 图：`stall > reassignThreshold` → 改派分支，一期人工确认 | **基本解决**（残留：改派到 cloud 时 handler 是否存在于目标） |
| P1 异构 runtime adapter + MCP/A2A 定位 | §2.4 + v2-runtime-adapter 图：五 adapter 表 + MCP(消费方)/A2A(编排上层)定位 + MCP 未覆盖鉴权的直连凭据退路 | **已解决**（残留：契约停在清单级、缺跨大模型归一） |
| P1 Flow Orchestrator/Platform Events/Trust Layer/Hyperforce | §3 关系表 + project-analyst §2d 技术桥草图；Trust Layer 列商业化前置门槛；Hyperforce 前瞻 | **已解决** |
| P1 局部失败/高延迟 UI 呈现 | §2.6 progress→UI 映射表 + 健康度/Reconnect 面板 + 两类最高频部分失败闭环 | **基本解决**（残留：仍无线框、无 fan-out 多分支树的部分态可视化） |
| 遗留 · 候选集补全 (Restate/Inngest/Windmill) | §1d 已补三者 + License 结论；组件 D 补 Benthos/Redpanda Connect + webhook 优先 | **已解决** |
| 遗留 · 「自研」量化对照 | §1d 分档位 1（6–10 人周）/档位 2（14–22 人周），AI 辅助口径 + 诚实标注长尾风险 | **已解决** |
| 遗留 · 引擎多实例非 SPOF | §2.5：多实例无主 + CAS 抢 lease 去重 | **已解决**（但见分项 3 的状态共享二阶问题） |
| 遗留 · 7×24 vs 本机 worker 封顶的张力 | project-analyst §0.3「边界诚实」+ 执行摘要显式收窄 | **已解决**（诚实前置） |
| 遗留 · 热分区 (单 PK 全树 Query 写放大) | §1c 谈 item collection，但**未回应吞吐热点** | **未解决**（见分项 2） |

整体判断：这是一次**扎实的迭代**——writer 没有用「已采纳」搪塞，而是每条都落到具体字段（`tokenSpent`）、具体条件写（`attribute_not_exists`）、具体图（liveness/adapter）与具体接口草图（Agentforce Action/Flow async）。剩余扣分不再是「真空」，而是「设计已到位、二阶正确性待收敛」——评审阶段的健康状态。

> 说明：六视角由 team leader 按 `tech_reviewer_team.py` 定义统一应用与汇总（本环境未联网调用 Agno 运行时；各视角判据与该文件 instructions 一致）。

## 分项评审

### 1. 开源架构 — 8.0/10（V1: 7.5，+0.5）
- **改进**：候选表补齐 Restate(BSL，商用须评估)/Inngest(SDK Apache-2)/Windmill(AGPL，硬约束)，License 结论清楚；「自研」歧义被拆成档位 1（在 LangGraph/DBOS 上增功能，只写 DynamoDB StateStore 适配+affinity 调度+采集层+护栏，6–10 人周）vs 档位 2（全自研内核 14–22 人周），并诚实标注 durable-execution correctness 长尾主要成本在测试/边界加固——这正是我 V1 要的量化对照与风险坦白。组件 D 的 webhook 优先 + Benthos/Redpanda Connect 也吸收了 V1 的「轮询是倒退」意见。
- **残留问题 / 风险**：
  1. **档位 1 的隐藏集成风险未点破**：LangGraph 官方承认其 checkpointer 是「最后写赢、无并发锁、无副作用去重」；我们要在其上叠加 lease+CAS 恰好一个 runner 的语义，**这不是"复用 checkpointer"那么轻——两套并发模型（LangGraph 的 pending-write vs 我们的 CAS lease）可能语义打架**。档位 1 的 6–10 人周若含"驯服 LangGraph 并发模型"，估计偏乐观。
  2. DBOS 走 Postgres 背书，与"公司既有栈=DynamoDB"存在栈冲突；档位 1 若选 DBOS 需评估引入 Postgres 的运维代价（文档未展开）。
- **建议**：V3 给档位 1 补一句"在 LangGraph checkpointer 上叠加 CAS lease 的并发语义边界"的风险注记；参考 [LangGraph persistence 文档](https://langchain-ai.github.io/langgraph/concepts/persistence/) 明确其 last-write-wins 语义，以及 [DBOS transact-py](https://github.com/dbos-inc/dbos-transact-py) 的 Postgres 依赖。

### 2. 分布式系统架构 — 8.0/10（V1: 7.5，+0.5）
- **改进**：两个 V1 P0 洞都堵上了——§2.2 把 exactly-once 落到一次 `attribute_not_exists` 条件写（dedup-key 由事件内容确定，重放同 key 幂等吸收）；fan-out 子分支由父 SK+确定性序号派生，`spawn` 条件写防双重 spawn，机制正确。§1c 对 DynamoDB 选型结合主要用例（高频点写+CAS+按树读+幂等提交）论证 NoSQL 强项、诚实标注复合查询缺失用 GSI(submitter / affinity+progress)+分析侧导出规避——权衡讲透。CAP 仍是干净的 CP。
- **残留问题 / 风险**：
  1. **热分区未回应（V1 遗留）**：超大任务树共享单一 `PK=workid`，`Query(PK)` 拉全树 + 主循环高频点写在单 item-collection 上有吞吐热点风险（DynamoDB 单分区 ~1000 WCU/3000 RCU 上限）。大扇出 workspace 可能撞分区吞吐上限。建议评估"分支级 PK 分片"或标注 workspace 步数上限。
  2. **dedup 存储生命周期未定**：dedup 表只增不删会无限增长；需 TTL 策略，且 TTL 早于事件可能重放的最长窗口会破坏幂等——两者的时序约束未言明。
  3. **「跃迁标识」的确定性依赖 watcher 快照**：edge-triggered 去重要求"同一跃迁产生同一 dedup-key"，但若 watcher 自身崩溃丢失上次快照，重建快照后可能对同一 merged 事件生成不同跃迁标识→重复 fire。dedup 的正确性其实**串联依赖 watcher 快照的持久化**，这条依赖链未画出。
- **建议**：V3 补 dedup 表 TTL vs 重放窗口的时序约束、watcher 快照持久化与 dedup 的依赖关系；热分区给出分片或上限。参考 [DynamoDB 单表设计的 write sharding](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-sharding.html)。

### 3. SRE 容错 — 7.5/10（V1: 6.5，+1.0，本轮进步最大）
- **改进**：§2.1 一次补齐熔断（per-dependency closed/open/half-open）、限流退避、URS 200 式背压、bulkhead 分池、per-workspace `tokenSpent`+attemptCount 硬上限——直接吸收 TCM noisy-neighbor 教训，这是 V1 最大扣分项的正解。§2.5 引擎多实例无主 + CAS 去重把 manager 从"未言明"变"显式非 SPOF"。§2.3 liveness 兜底 + project-analyst 边界诚实把 7×24 张力前置。
- **残留问题 / 风险**：
  1. **多实例引擎下护栏状态的共享未定（§2.1 与 §2.5 的交互二阶问题）**：熔断器状态（open/half-open）、背压"在飞 in-progress 计数"、令牌桶配额——**若各引擎实例本地持有，则 N 个实例各自学习故障、各自放行 N 倍在飞任务，背压与熔断会被实例数放大失效**；若共享，则需一个分布式计数器/熔断状态表（又是一次高频写）。文档把护栏当单机语义写，与 §2.5 多实例模型未打通。这是 V2 新引入、最应在 V3 收敛的正确性问题。
  2. **本机 daemon 仍是 machine:X 任务的 SPOF**（已诚实标注，靠 liveness 改派兜底，可接受）。
  3. 熔断 open 时把任务转 `error(retryable)` 挂起——但若下游长期故障，这些任务靠什么重新探测 half-open？重扫周期与 half-open 探测的关系未言明。
- **建议**：V3 明确护栏状态存放层（建议：熔断状态/在飞计数放 DynamoDB 共享项，用条件写维护，接受额外写成本，或按 submitter 分片降低竞争），并把 half-open 探测挂到守护层重扫周期。参考 [resilience4j](https://github.com/resilience4j/resilience4j) 的熔断状态机（注意其为单 JVM 内存态，分布式需自行落盘共享）。

### 4. 异构通信协议 — 7.5/10（V1: 6.0，+1.5，并列进步最大）
- **改进**：§2.4 直接命中 V1 最薄一环——Worker Runtime Adapter 层（ClaudeCode/Script/StepFunctions/A2A/MCPTool 五 adapter）把"引擎只认 handler 契约、怎么拉起交给 adapter"讲清；MCP 定位为消费方（不重造工具协议）、A2A 定位为编排上层（把远程 agent 当一种 runtime），并给 MCP 未覆盖鉴权留了"直连凭据"退路——V1 的三个子问题全部回应。
- **残留问题 / 风险**：
  1. **adapter 契约停在清单级**：`StepFunctionsAdapter` 如何把 SFN 执行态映射到 `waiting`/`finish`、`ClaudeCodeAdapter` 如何从 `claude -p` 子进程**可靠地**解析结构化 output（子进程 stdout 混入日志/非结构化文本是现实难题），均未给契约。这是一期主力路径，值得从"能列出"升级到"能定契约"。
  2. **缺跨大模型归一（本视角明确职责）**：文档只覆盖 Claude Code / opencode，未讨论"同一 handler 在不同大模型（Claude/GPT/Gemini）下的调用转换与 prompt/tool-schema 归一"。若二期要接异构模型 worker，这是必答项，一期至少应标注为已知边界。
  3. 云端 on-behalf-of 鉴权仍卡在 OQ-2（外部依赖，非 writer 可解，但决定 A2A/云 adapter 的能力边界）。
- **建议**：V3 给 ClaudeCodeAdapter 的 output 解析契约（如约定 JSON 分隔符/结构化 sentinel）与 StepFunctionsAdapter 的状态映射；标注"跨大模型归一"为二期边界。参考 [MCP 规范](https://modelcontextprotocol.io) 与 [A2A](https://github.com/google/A2A)。

### 5. 分布式 UX — 7.0/10（V1: 6.0，+1.0）
- **改进**：§2.6 progress→UI 映射表把六种 progress + MCP 过期 + machine 离线映射到具体 UI 呈现与用户动作；显式交付"多任务健康度/待办/需 Reconnect"面板，把两类最高频部分失败（笔记本关机、MCP OAuth 过期）做成"通知→一键 Reconnect/改派"闭环——V1 的核心诉求（从断言变设计）达成。高延迟态给了"当前步名+已耗时+已花 token"。
- **残留问题 / 风险**：
  1. **仍无线框（wireframe）**：映射表对设计文档而言可接受，但 V1 明确要"一张面板线框"。多任务健康度面板的信息层级（如何一屏区分 20 个 workspace 的红/黄/绿而不淹没用户）只有文字描述，无布局。
  2. **fan-out 多分支树的部分态可视化缺位**：一个 workspace = 一棵任务树（根+若干子分支），"某树里 2 分支 waiting、1 分支 error"如何在面板呈现树形部分态，没设计——而这恰是分布式 UX 最难的层级。当前面板停在 workspace 级聚合。
  3. sticky-note 仅 macOS（已诚实标注，商业化跨端留后续，可接受）。
- **建议**：V3 补一张健康度面板线框（含 workspace 列表→展开看分支树部分态的两级钻取），把"20 个并发 workspace 不淹没用户"的信息密度问题落到布局。参考 [Temporal Web UI](https://docs.temporal.io/web-ui) 对 workflow/child-workflow 树形状态的呈现范式。

### 6. Salesforce 产品 — 7.5/10（V1: 6.5，+1.0）
- **改进**：§3 正面回答了 V1 最大的 SF 契合度问题——"为何不在 Flow Orchestrator 上建"：关系表把 Flow Orchestrator（Platform 内声明式+审批，无 lease/affinity/token 预算/脱机续跑运行时语义）、Platform Events（桥接候选）、Agentforce orchestration（互补）讲清，且给了桥接方式（workspace 暴露为 Flow 可调 async 动作）。Einstein Trust Layer 列为商业化前置门槛（一期只碰内部研发数据故不接，定位诚实）；Hyperforce 多租户前瞻点名。project-analyst §2d 的 Agentforce Action 长跑后端 / Flow async 编排层接口草图把"互补"从断言变路径。
- **残留问题 / 风险**：
  1. Agentforce/Flow 技术桥仍是**接口草图级**（一期不实现，合理），但 Platform Event 回调本编排器的鉴权/多租户映射未展开——真正桥接时会撞上 CRUD/FLS/共享模型（V1 已提，V2 点名未深入，可接受留远期）。
  2. Hyperforce 多租户从 per-submitter 隔离升级到 per-tenant 表/账户+驻留路由，是比文档呈现更大的架构改造——已诚实点名为远期，但未估其对 StateStore 抽象的返工面。
- **建议**：保持现有诚实定位即可；V3 可选补一句"Platform Event → signal 的租户上下文如何映射到 submitter/tenant 键"。参考 [Flow Orchestrator 文档](https://help.salesforce.com/s/articleView?id=sf.flow_concepts_orchestrator.htm)、[Platform Events](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_intro.htm)。

## 关键建议（按优先级）
1. **打通护栏与多实例引擎的状态共享（P0，视角 3，V2 新引入）**：§2.1 的熔断/背压/令牌桶是单机语义，与 §2.5 多实例无主模型冲突——多实例各自本地持有会把在飞上限与熔断放大 N 倍失效。V3 须定义护栏状态的共享落盘（DynamoDB 共享项+条件写，或按 submitter 分片）。
2. **收敛 dedup 与热分区的分布式正确性（P0/P1，视角 2）**：dedup 表 TTL vs 重放窗口的时序约束、watcher 快照持久化与 dedup 的依赖链、单 PK 全树的吞吐热分区——三者是 §2.2 幂等设计能否在生产成立的边界。
3. **把 adapter 从清单升级为契约（P1，视角 4）**：ClaudeCodeAdapter 的 output 解析契约、StepFunctionsAdapter 的状态映射，是一期主力路径的落地细节；并标注"跨大模型归一"为二期已知边界。
4. **补健康度面板线框 + fan-out 树形部分态（P1，视角 5）**：把"20 并发 workspace 不淹没用户"与"树内分支部分失败"从文字升级为两级钻取布局。
5. **档位 1 的 LangGraph 并发语义风险注记（P1，视角 1）**：在 last-write-wins checkpointer 上叠加 CAS lease 的集成成本，可能使 6–10 人周偏乐观。

## 未解决 / 待 writer 回应的问题
- [ ] 多实例引擎下熔断/背压/令牌桶的状态共享机制（护栏在分布式下如何不被实例数放大失效）——**V2 新引入的最高优先正确性问题**。
- [ ] dedup 表 TTL 与事件重放窗口的时序约束；watcher 快照持久化与 dedup-key 确定性的依赖链。
- [ ] 单 `PK=workid` 全树的吞吐热分区（V1 遗留，V2 未回应）——分片或 workspace 步数上限。
- [ ] 改派 `machine:X → cloud` 时目标端是否具备该 handler（否则改派后仍拉不起）。
- [ ] adapter 契约级细节：`claude -p` 子进程结构化 output 解析、SFN 执行态→waiting/finish 映射。
- [ ] 跨大模型（Claude/GPT/Gemini）的调用转换与归一——一期至少标注为已知边界。
- [ ] 熔断 open 任务的 half-open 重探测如何挂到守护层重扫周期。
- [ ] UX：健康度面板线框 + fan-out 多分支树的部分态可视化。
- [ ] （非 writer 可解，跟踪）OQ-1 合规引依赖结论、OQ-2 matrix 身份 (a)/(b)——决定档位与云 adapter 能力边界，建议尽快指定 owner+deadline 落地。
