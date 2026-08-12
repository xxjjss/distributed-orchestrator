# Product Review — V4

**总评分：8.1/10**（四项加权平均，等权；较 V3 的 7.6 提升 +0.5）
**一句话结论：** 需打磨 → **可推进（立项材料已达产品评审可给的上限，剩余为外部依赖 / 一期主动收窄的边界 / 二期才暴露的商业验证）**。V4 是一次**近乎满分的「回应式收敛」**——我 V3 的 8 条建议（1 条 P1 单价、1 条 P1 应急退路、6 条 P2）**逐条落地，无一遗漏或以更弱替代蒙混**，且核心那条 Opus 单价（唯一「已可核准的硬数字」）精确订正为 1.67× 并去掉 hedge。产品视角的可打磨面已基本磨平；封住 8.5+ 的仍是同两类**非 writer 单方可解**的结构性天花板：商业需求本质上尚不可验证（报告诚实收窄为「愿景」，这把尺子在商用维度只能给中上分）、build-vs-embed 重复投资裁决仍待战略层署名（闸门 A）。

## 概述

V4 与 V3 一脉相承——不扩范围、不拔叙事，只把三位 reviewer（含我）V3 的 P1/P2 逐条兑现。就产品视角看，V4 最有价值的四个动作：(1) **Opus 单价订正**把 token 经济学从「方向保守但高估 3×」收敛为可核准的准确区间（Sonnet 主力 $90–450/月、Opus $150–750/月、结论「$1k/月以内」）；(2) **ECS/Fargate 应急退路 +2–4 人周入表**，把 V2 至今悬着的「matrix 延期时云端故事怎么兑现」从定性描述变成有价签的退路，并与二期 8–14 人周 Provider 化明确区分为「两笔不同触发条件的钱」；(3) **§2d Agentforce 技术桥从零推进变为收敛决策 + OQ-5**——V3 我给 SFDC 架构视角封顶的最大原因（技术桥是逐字未动的接口草图）本轮被实质推进：回调统一走 Platform Event（从「或」变结论）、Action 视为「至多一次触发 + 异步收敛」黑盒、session 内部推理不入 replay、stateFingerprint 扩校验 Prompt Builder 模板版本、Data Cloud zero-copy 集成草图；(4) **§2b 定价锚点 + 买方画像 + §2c 指标改名去 overclaim**，把商业叙事的诚实度补齐。

**本轮打分逻辑**：产品评审的尺子是「商业可行 + 客户需求 + 接受度」。V4 在**内部一期（推工具）**这条最可信价值链上已无 writer 可解的短板；四个分项全部上移。剩余扣分不再是「量化缺失 / 文档缺失 / 技术桥零推进 / 以更弱替代蒙混」这类**writer 可解**的问题，而是转为三类：(a) 外部依赖待签署（OQ-1 合规、OQ-3 编排层归属、OQ-2 matrix 身份、OQ-5 Agentforce 平台裁决）；(b) 一期主动收窄的边界（Agentforce 技术桥一期不实现、不触客户数据）；(c) 商业维度的真实验证（定价硬数字、需求侧付费、n=1 复现）本质上须待二期真实预算认领测试。这三类共同封住 8.5+ 的上沿。

### V3 → V4 改进评估（逐条对照 V3 的 8 条建议）

| V3 建议 | 优先级 | V4 落地情况 | 评价 |
|---|---|---|---|
| 订正 §3a Opus 单价倍数（5× → 1.67×），去 hedge | **P1** | §3a 单价表 + 账单表 + 结论 + 订正说明全部订正：Opus $5/$25、Sonnet $3/$15、比 1.67×，Opus 档 $150–750/月，去掉「待 claude-api 核准」，结论「大概率 $1k/月以内」 | **充分解决**（精确采纳，唯一可核准硬数字已订正） |
| M1–M4 补一期 matrix 延期的 ECS/Fargate 应急退路预算行（2–4 人周） | **P1** | §3a M1–M4 表新增「M2 应急缓冲：ECS/Fargate 自建最小托管（matrix 延期触发）」条件性行 +2–4 人周，明确与二期 8–14 人周 Provider 化区分为不同触发条件 | **充分解决**（V2 至今悬着的残留终于闭环） |
| 补外部系统 API 限额风险（SF Core/GUS/Slack/GitHub） | **P2** | §4 新增 R10，用 R8 同框架（每类 API 独立令牌桶 + 熔断 + 退避）覆盖下游 governor limits | **基本解决**（风险已登记 + 框架已给；但「一期即测算」尚是计划，未给数量级判断，见下 engineering 分项） |
| §2c 三指标改名「使用强度/信任代理」 | **P2** | §2c 改名 + 明确「付费意愿」严格保留给二期真实预算认领测试；闸门 B 第 4 条同步改名 | **充分解决**（overclaim 风险消除） |
| §2b 加定价锚点 + 假设买方画像 | **P2** | §2b 补 Temporal/LangGraph/Inngest/n8n 计费轴 + consumption 落点 + 买方画像（已部署 Agentforce、有 AI-ops/可靠性预算线的平台工程/研发效能负责人）+ 需求侧 gate 缺口提示 | **充分解决** |
| Agentforce 技术桥两未决点升级 OQ-5 + stateFingerprint 与非确定性 planner 共存 | **P2** | §2d 收敛为倾向决策（Platform Event 回调 / 黑盒 / session 不入 replay / fingerprint 扩校验 Prompt Builder）+ Data Cloud zero-copy 草图 + 平台约束占位数字 + 新增 OQ-5；tech-design §3 落 AgentforceActionAdapter 契约 | **充分解决**（V3 最大结构性缺口本轮实质推进） |
| 护栏共享写成本 / 延迟量化 | **P2** | §3a(2) 折算月增量 <$1、每步 +个位数毫秒；与 tech-design §2.1 一致 | **充分解决** |
| 「干净 org 冒烟」升级「dirty org 冒烟」+ FDE 试点可审计判据 + 打包/交付形态 + 现场支持模型 | **P2** | tech-design §4：Scratch Org + 预装含触发器/Flow 的 AppExchange 包做 dirty-org 冒烟，排入二期 FDE 培训前；打包/L2 支持模型列二期定义；§3b Provider 化成本维持 | **大部解决**（dirty-org / 打包 / 支持均已落；唯 **FDE 试点可审计成功判据**仍缺——见 FDE 分项，为本轮唯一 writer 可解的实质残留） |

**结论**：V3 的 5 条 P1/P2 中我评「4 实质 + 1 部分」；V4 把当时部分/未落的（Opus 单价、ECS 退路、技术桥、指标改名、定价锚点、护栏量化）**全部补齐**，唯一遗留的 writer 可解项是 FDE 试点缺一条与闸门 B 对齐的可审计成功判据。这是四轮里产品视角回归完成度最高的一轮。

## 分项评审

### 1. Salesforce 架构与研发 (sfdc_architect_agent) — 8.0/10（V3 7.3，+0.7，本视角进步最大）
- **视角适用性**：一期仍是 AWS/TCM-native 编排基础设施（DynamoDB 单表 + SFN + SQS + MCP adaptor），不触 Platform 元数据、不触客户数据，Governor Limits / AppExchange Security Review / Einstein Trust Layer 对一期仍不适用——定位诚实。本视角评估战略落点（Agentforce/Platform 耦合）与远期合规。
- **改进（vs V3，本轮兑现我 V3 全部三条 SFDC 残留）**：
  - **Agentforce 技术桥从零推进 → 收敛决策（V3 残留 #1，本轮实质推进）**：§2d + tech-design §3 把 V3 逐字未动的「Action 回调走 Platform Event 还是 notification」的「或」收敛为**建议结论**（统一走 Platform Event，与 Watcher/envelope 天然对齐）；`workid ↔ Agentforce session` 生命周期映射定义为「一对多、adapter 层维护」；升级为 OQ-5 交平台架构团队裁决。「结论跑在技术验证前面」的 V3 批评本轮被正确处理——现在是「可裁决的技术契约」而非「既定叙事」。
  - **stateFingerprint 与非确定性 planner 共存（V3 残留 #3，本轮解决）**：§2d 第 4 点 + tech-design §3 给出正解——把 Agentforce Action 当「至多一次触发 + 异步收敛」黑盒，**session 内部非确定性推理不纳入 replay 校验**，两套状态模型（可倒带 checkpoint vs 不可倒带 session）在边界解耦；fingerprint 扩展校验 Prompt Builder 模板版本解「prompt 改了、code 没改」的隐性非确定性。这是异构 agent 编排里少见的把「两套状态模型如何共存」讲透的设计。
  - **Data Cloud / Prompt Builder 集成路径（V3 残留 #2，本轮补齐）**：§2d 第 5 点 + tech-design §3 补方向性草图——审计轨迹作 Data Cloud zero-copy ingestion 源（与 §2c 反馈闭环工具化天然衔接）、Prompt 走 Prompt Builder 并纳入 fingerprint。从「完全空白」升级为「有方向草图」，与其它 OQ 处理方式对称。
  - 三个桥接点补平台约束占位数字（Platform Event 发布频率上限 / Flow invocable 同步时限 / Agentforce Action 会话超时），待核准，与 token 账单「待核准」处理方式对称——文档严谨度对称性达成。
- **遗留问题 / 风险（均为一期主动收窄边界 / 外部裁决，非扣分主因）**：
  - Agentforce 技术桥仍是**接口草图级、一期不实现**（合理，已升级 OQ-5 交平台架构团队裁决）；桥接可行性仍有平台侧未知数（占位数字待核准）——这是「编排底座候选内核」战略卖点的剩余不确定性，但已从「零推进」变为「路径已画、待裁决」，性质大不同。
  - Hyperforce 合规仍靠「StateStore Provider 可插拔」处理：客户数据存储位置须落 SF 合规存储边界，外部自建 DynamoDB 可能非 Hyperforce 认可位置——比换 Provider 重，列远期，一期不触客户数据故不阻塞。
- **建议 / 替代方案（附链接）**：维持现状。远期实现 AgentforceActionAdapter 时，把 `workid ↔ session` 映射持久化到 StateStore（非 adapter 内存态）、触发复用 dedup-key 保证至多一次（与 tech reviewer V4 视角 4 一致）。参考 [Agentforce](https://www.salesforce.com/agentforce/)、[Platform Events 限制](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_intro.htm)、[Data Cloud zero-copy](https://help.salesforce.com/s/articleView?id=sf.c360_a_zero_copy_data_federation.htm)、[Prompt Builder](https://help.salesforce.com/s/articleView?id=sf.prompt_builder_overview.htm)、[Einstein Trust Layer](https://www.salesforce.com/products/platform/trusted-ai/)。

### 2. FDE 交付与现场实施 (fde_strategy_agent) — 8.1/10（V3 7.8，+0.3）
- **改进（vs V3）**：
  - **「干净 org 冒烟」→「dirty org 冒烟」升级（V3 残留 #1，本轮解决）**：tech-design §4 明确用 Scratch Org + 预装含自定义对象/Flow/Apex 触发器的常见 AppExchange 包做近似真实环境，暴露触发器递归、Flow 与 Watcher 事件顺序竞态、命名冲突等冲突面——恰恰是空 org 测不出的。这解决了我 V3 批评的「看起来响应了、实际测的是另一件事」的更弱替代问题。
  - **明确排入「二期 FDE 培训前」deadline**（V3 残留 #2 时间线脱节）：不再挂「未来问题」含糊处理，成本并入 §3b 二期 Provider 化预算。
  - **打包/交付形态 + 现场支持模型（V3 残留 #4/#5）**：tech-design §4 补——一期 installer 面向本机开发者，FDE 现场部署整套栈（Docker / managed package / 安装脚本）与 Provider 层 bug 的 L2 支持/escalation 列「二期 FDE 试点须定义项」。虽是「二期定义」而非「现在给方案」，但已从空白变为已登记待办，对一期立项可接受。
- **遗留问题 / 风险**：
  - **FDE 试点仍缺可审计成功判据（V3 残留 #3，本轮唯一未解决的 writer 可解项）**：§2c 仍是「一期末期邀请 1–2 名 FDE 试用」，工程师侧有清晰的闸门 B 四条 gate，FDE 侧却没有对应可审计判据，容易变成「邀请了、聊了、没结论」。dirty-org 冒烟解决了「兼容性怎么测」，但没解决「FDE 试点算不算成功怎么判」——这是两件事。
  - 打包/L2 支持虽登记但仍是「二期定义」，落地成本可能高于账面 8–14 人周（可接受，属二期细化）。
- **建议 / 替代方案（附链接）**：
  - 给 FDE 试点补一条与闸门 B 对齐的可审计 gate，如「1–2 名 FDE 能否在无核心团队实时支持下、≤3 天内针对自己客户场景跑通一个最小 workflow」——这是本轮唯一低成本、writer 可直接补的实质残留。
  - 可移植运行时分层参考 [Inngest](https://github.com/inngest/inngest)、[Trigger.dev](https://github.com/triggerdotdev/trigger.dev) 的 SDK/Provider 分层；worker↔引擎解耦参考 [Camunda Zeebe Job Worker](https://docs.camunda.io/docs/components/concepts/job-workers/)、[Temporal Data Converter/Codec Server](https://docs.temporal.io/production-deployment/data-encryption)。

### 3. B2B 商业前景与客户接受度 (business_adoption_agent) — 7.8/10（V3 7.2，+0.6）
- **改进（vs V3，本轮兑现我 V3 全部三条商业残留）**：
  - **定价锚点补齐（V3 残留 #1「零定价锚点」，本轮解决）**：§2b 拉出 Temporal Cloud（consumption）、LangGraph Platform（分层订阅 + per-node 计量）、Inngest（免费档 + step 阶梯）、n8n（自托管开源 $0 地板价）四条公开计费轴，并给出我们的落点——若内嵌 Agentforce 作 consumption 计量项（per-workflow-run / per-durable-step），避开 n8n $0 地板价正面竞争、借 SF 计费关系。这正是我 V3 要的「展示定价逻辑被考虑过、非跳过」；n8n $0 地板价这条还反向强化了「独立 SaaS 定价天花板被压低 → 倾向内嵌」的 OQ-3 结论。
  - **假设买方画像补齐（V3 残留 #3「全篇无买方画像」，本轮解决）**：§2b 收窄买方为「已部署 Agentforce、且拥有 AI-ops/可靠性预算线的平台工程/研发效能负责人」（非一线开发者、非 CIO 直采），预算来自「可靠性/运维」而非「新增 AI 工具」——给闸门 B 一个需求侧对照，并诚实点出「当前闸门 B 4 条全是供给侧、二期须补需求侧 gate」。
  - **指标改名去 overclaim（V3 残留 #2，本轮解决）**：§2c 三指标改名「使用强度/信任代理」，明确测的是内部工程师供给侧行为信号，「付费意愿」（买方批预算行为）严格保留给二期真实预算认领测试——把「内部参与深度」与「付费意愿」的混淆消除，是本轮商业叙事诚实度的关键补齐。
- **遗留问题 / 风险（均为商业维度本质上尚不可验证 / 二期才暴露，非 writer 单方可解）**：
  - **定价仍是方向性、无硬数字**：报告主动收窄为「远期愿景，不给硬数字」——定位诚实，但意味着这把商用尺子在「定价可行性」维度仍只能给中上分（不是扣 writer，是商业阶段使然）。
  - **需求侧 gate 仍是「二期须补」而非已写入闸门 B**：§2b 已诚实点出缺口、leadership reviewer V4 亦建议管理层在闸门 A 一并明确二期加一条真实预算认领 gate——这是待管理层动作，非 writer 可单方钉死。
  - **ROI 仍 n=1**（已诚实降级为 ≥1.5× 试点判据，靠闸门 B 复现）；**时间窗口/竞品侵蚀**已承认（§2a 四条护城河三条有侵蚀风险）但 OQ-3 敏感度分析只压测权重分配（静态维度），未压测侵蚀轨迹——这条我 V3 提过，属可选增强，非硬伤。
- **建议 / 替代方案（附链接）**：
  - 建议管理层在闸门 A 裁决时一并把「二期需求侧预算认领 gate」写入闸门 B（与 leadership reviewer V4 建议 3 合流），把商业判断从「愿景」钉到「有人愿掏预算」。
  - （可选）OQ-3 敏感度表加一行「时间衰减情景」：假设 LangGraph/Temporal 在试点末补齐 human-in-the-loop 信号，重跑四维打分看「内嵌胜出」是否仍稳健。竞品定价参考 [LangGraph Platform](https://www.langchain.com/langgraph-platform)、[Temporal Cloud](https://temporal.io/cloud)、[Inngest](https://www.inngest.com/)、[n8n](https://github.com/n8n-io/n8n)。

### 4. 研发工程 Ops 与成本风险 (engineering_cost_agent) — 8.5/10（V3 8.0，+0.5，四项中分数最高）
- **改进（vs V3，本轮兑现我 V3 全部四条成本残留）**：
  - **Opus 单价订正（V3 P1，唯一可核准硬数字，本轮精确解决）**：§3a 单价表订正为 Opus $5/$25、Sonnet $3/$15、比 1.67×，Opus 档月账单从 $450–2,250 下修为 $150–750/月，去掉「待 claude-api 核准」hedge，并加订正说明（承认原 5× 高估约 3×、方向保守不致命、若实测 Opus 单步 token 更高会据实上调）。这正是我 V3 P1 的精确回应。
  - **ECS/Fargate 一期应急退路入 M1–M4（V3 P1，V2 至今残留，本轮解决）**：§3a M1–M4 表新增条件性行 +2–4 人周（触发条件 = R1/OQ-4 命中），并明确与二期 8–14 人周 Provider 化是「不同触发条件的两笔钱」——彻底消除我从 V2 就跟的混淆风险。
  - **护栏共享写成本量化（V3 残留 item B，本轮解决）**：§3a(2) 折算月增量 <$1（百万级写 × $1.25/百万）、每步 +个位数毫秒（单次条件写 P99），并入云资源月成本（标注「含护栏共享写」），与 tech-design §2.1 一致。
  - **外部 API 限额风险登记（V3 残留 item D，本轮基本解决）**：§4 新增 R10，覆盖 SF Core/GUS/Slack/GitHub 下游 governor limits，用 R8 同框架（每类 API 独立令牌桶 + 熔断 + 退避）——V3 我点名的「护栏只防自己的 LLM 调用、不防下游」盲区已登记。
- **遗留问题 / 风险**：
  - **R10 尚停在「一期即测算」的计划、未给数量级判断（本轮唯一可再进一步项）**：R10 缓解写「一期即测算每 workspace 下游调用量级 × 并发数，对照各系统已知限额」——这是**计划**而非**已算**。对比 token 账单本轮已从框架「乘成一个数」，R10 完全可以同样临门一脚：15–25 并发 × 每 workspace 下游 API 调用估算，对照 SF Core API 已知每日限额（如 org 级 ~15k/日量级）给一个「大概率不撞/可能撞」的初判。属立项估算级、可选增强，非硬伤（一期主力本机 worker、并发受控，且有护栏框架兜底）。
  - **token 总量仍待试点实测校准**（并发数、步数假设）——单价已核准，总量属固有不确定性，靠闸门 B 每-WI token gate 兜底，可接受。
- **建议 / 替代方案（附链接）**：
  1. （可选）R10 从「一期即测算」推进到「立项即给数量级初判」，与 token 账单本轮的处理方式对称——给一个 15–25 并发下 SF Core/GUS/Slack/GitHub 各自撞限额与否的粗判，让下游限额风险从「已登记」升级为「已量化」。
  2. 维持 §3a(3) 的 prompt caching（cache read ≈0.1× 输入价、~90% 折扣）作为进一步压账单杠杆的提示。参考 [DBOS](https://github.com/dbos-inc/dbos-transact-py)、[LangGraph checkpointer](https://github.com/langchain-ai/langgraph)、[resilience4j](https://github.com/resilience4j/resilience4j)。

## 关键建议（按优先级）

1. **[P2，唯一 writer 可解的实质残留] 给 FDE 试点补一条与闸门 B 对齐的可审计成功判据**（如「1–2 名 FDE 在无核心团队实时支持下、≤3 天内针对自己客户场景跑通一个最小 workflow」）——dirty-org 冒烟解决了「兼容性怎么测」，但 FDE 试点仍缺「算不算成功怎么判」，是两件事。低成本、可直接补。
2. **[P2，可选增强] R10 外部 API 限额从「一期即测算」推进到「立项即给数量级初判」**——与 token 账单本轮「框架乘成一个数」的处理方式对称；15–25 并发 × 下游调用估算 vs SF Core/GUS/Slack/GitHub 已知限额，给撞/不撞粗判。
3. **[P1，非 writer 可解 · 管理层动作] 闸门 A 战略层裁决「编排层归属 / 是否与 Agentforce 重复投资」**——报告侧（§0.4 闸门 A + §5 OQ-3 + §2b 敏感度 + §2d 技术桥收敛 + OQ-5）已完全就位，球纯在管理层；这是商用维度评分越过 8.5 的前提，与 leadership reviewer V4 判断一致。
4. **[P1，二期 · 管理层动作] 把需求侧预算认领 gate 写入闸门 B**——§2b 已诚实点出闸门 B 4 条全供给侧，二期须补一条真实部门预算认领意向测试，把商业判断从愿景钉到「有人愿掏预算」。
5. **[跟踪，非 writer 可解] OQ-1（合规引依赖，决定档位 1/2 与 token 账单）/ OQ-2（matrix 身份）/ OQ-5（Agentforce 平台裁决）尽快落 owner+deadline**——均已列闸门，建议 kickoff 即指派。

## 未解决 / 待 writer 回应的问题

- [ ] **[writer 可解]** FDE 试点缺一条与闸门 B 对齐的可审计成功判据（dirty-org 冒烟已解决兼容性验证，但试点成功判据未定）。
- [ ] **[writer 可选增强]** R10 外部 API 限额从「计划测算」推进到「立项即给数量级初判」（对照 SF Core/GUS/Slack/GitHub 已知限额）。
- [ ] **[非 writer 可解 · 管理层]** 闸门 A 战略层署名裁决（编排层归属 / 与 Agentforce 是否重复投资）——报告已就位，球在管理层。
- [ ] **[非 writer 可解 · 管理层 · 二期]** 需求侧预算认领 gate 写入闸门 B。
- [ ] **[固有 · 二期验证]** 商业维度定价硬数字 + 真实付费意愿 + ROI 多人复现（≥1.5×）——报告主动收窄为「愿景 + 闸门 B 复现」，性质上须待二期真实预算测试，非当前可消解。
- [ ] **[一期主动收窄 · 已画路径待裁决]** Agentforce 技术桥一期不实现（OQ-5）、平台约束占位数字待核准——已从 V3 的「零推进」变为「路径已画、待平台架构团队裁决」。
