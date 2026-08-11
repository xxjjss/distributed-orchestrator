# Product Review — V3

**总评分：7.6/10**（四项加权平均，等权；较 V2 的 7.2 提升 +0.4）
**一句话结论：** 需打磨 → **可推进（Conditional GO 论据已足够扎实）**。V3 把我 V2 的 P1「临门一脚」逐条兑现——token 月账单合成区间、OQ owner+deadline 表、OQ-3 权重敏感度、Provider 化增量成本、付费意愿代理指标口径化——立项材料对决策层已足够完整、可拍板。剩余扣分集中在**四项结构性未收敛项**：商业需求仍未验证（无买方/无定价锚点）、matrix/OQ-4 一期应急退路成本仍未进 M1–M4、Agentforce 技术桥仍是零推进的接口草图、客户 Org 真实兼容性被「干净 org 冒烟」这个更弱替代悄悄置换——这些多为**外部依赖未收敛或一期主动收窄的边界**，非 writer 单方可解。

## 概述

V3 是一次**精准的「回应式收敛」修订**：不再有 V1/V2 那种整章补写，而是把三位 AI reviewer（含我）V2 的 P1/P2 逐条落地。就我这个产品视角看，V3 最有价值的动作是把 §3a 的 token 框架**乘成了具体金额区间**（Sonnet ≈$90–450/月、Opus ≈$450–2,250/月、结论「大概率 $1.5k/月以内」）——这正是我 V2 反馈里点名的「决策层立项最后要看的一个数」。加上 §5 的 owner+deadline 表、§2b 的 OQ-3 敏感度分析、§3b 的 Provider 化 8–14 人周，我 V2 的五条关键建议 **4 条实质落地、1 条部分落地**。

**本轮打分逻辑**：产品评审的尺子是「商业可行 + 客户需求 + 接受度」。V3 在**内部一期（推工具）**这条最可信的价值链上已几乎无短板，且 §0.0 决策摘要卡 + §0.4 Conditional GO 使报告从「陈述」彻底变成「可决策材料」。封住 7.6 以上空间的仍是同两类问题：(1) 商业维度真实买方/定价始终空白（报告主动收窄为「愿景探讨」，定位诚实但也意味着这把尺子在商用维度只能给中位分）；(2) matrix（OQ-4/R1）与 OQ-1 两个立项前置变量仍待管理层签署，且一期 matrix 延期的 ECS 应急退路成本仍未量化进里程碑。

### V2 → V3 改进评估（逐条对照 V2 的 5 条关键建议）

| V2 建议 | 优先级 | V3 落地情况 | 评价 |
|---|---|---|---|
| 给出一期总月度 LLM token 账单的合成区间（Sonnet/Opus 两档） | **P1** | §3a 给出 Sonnet ≈$90–450/月、Opus ≈$450–2,250/月、保守上界数千美元/月（硬护栏封住）、结论「大概率 $1.5k/月以内」 | **充分解决**（但 Opus 倍数假设偏高约 3×，见下 engineering 分项，方向保守不致命） |
| 落实 OQ-1 与 OQ-4 的实际 owner + deadline | **P1** | §5 补 OQ-1/2/3/4 建议 owner + deadline 表，OQ-1/OQ-3 标为闸门 A（投钱前）阻塞项 | **部分解决**：从「无主」升级为「有建议主人+时间线」，但显式标注 `[OPEN QUESTIONS]` 待管理层签署——headless 环境无法代签，可接受，但仍是未收敛外部变量 |
| OQ-3 做权重敏感度分析 | **P2** | §2b 测「分发/议价权/壁垒」三种双权重，结论「倾向内嵌基本稳健，唯保独立议价权双权重时打平」 | **充分解决** |
| 二期蓝图补 Provider 化 + 客户现场适配的增量成本粗估 | **P2** | §3b 补 ≈8–14 人周（Provider 接口固化 + 非 SF-internal 参考实现 + 干净 org 冒烟） | **充分解决**（但这是二期通用适配成本，≠ 一期 matrix 延期的 ECS 应急退路成本，后者仍缺） |
| 把付费意愿代理指标升级为一次真实预算意向测试 | **P2** | §2c 三条可从审计轨迹客观算出的指标（托管深度/放手程度/决策委托范围）+ 采集方式 + 二期「真实预算认领意向测试」升级路径 | **基本解决**（但三指标测的是内部工程师参与深度，非买方付费意愿，命名有 overclaim 风险，见 business 分项） |

**结论**：V2 的 P1「临门一脚」（token 合成金额）**已消除**；四条 P2 全部有实质回应。剩余问题从「文档缺失/量化缺失」性质转为「外部依赖待签署 + 商业需求本质上尚不可验证 + 一期主动收窄的边界」性质——后两类非 writer 单方可解。

## 分项评审

### 1. Salesforce 架构与研发 (sfdc_architect_agent) — 7.3/10（V2 7.0）
- **视角适用性**：一期仍是 AWS/TCM-native 编排基础设施（DynamoDB 单表 + SFN + SQS + MCP adaptor），不触碰 Platform（Apex/LWC/Flow）元数据，Governor Limits / AppExchange Security Review 对一期不适用——报告定位诚实。本视角评估战略落点（Agentforce/Platform 耦合）与远期合规。
- **改进（vs V2）**：
  - StateStore 多租户返工面讲清楚了（tech-design §3）——per-submitter → per-tenant 是 **StateStore Provider 层扩展、非抽象层重写**（`tenantId` 前缀/独立表/驻留路由），是正确的防返工架构判断。
  - Platform Event → signal 的租户上下文映射新增（envelope 预留 `tenantId`、复合隔离键 `(tenantId, submitter)`）——为将来订阅 Platform Event 作 Watcher 源打了地基。
  - OQ-3 权重敏感度分析把「build vs leverage Platform」这个架构归属问题从主观倾向变成可审计的决策依据，直接回应了架构 Lead 最关心的「不要重复造 Platform 编排能力」顾虑。
  - 一期仍明确「不触客户数据、不接 Einstein Trust Layer」，Hyperforce 列远期——克制得当。
- **遗留问题 / 风险**：
  - **Agentforce 技术桥仍是零推进的接口草图（V2 残留 #1，V3 未推进）**：§2d 四点与 V2 逐字相同——Action 超时/异步回调走 Platform Event 还是 Agentforce notification 仍是「或」而非决策；`workid` ↔ Agentforce session 生命周期映射仍未定义。而 §0.4 已把「一期交付物按 Agentforce 编排底座候选内核设计」写成既定叙事——**结论跑在技术验证前面**。
  - **stateFingerprint 与 Agentforce reasoning/planner 的共存关系仍未回应（V2 残留 #3）**：编排器靠 stateFingerprint + checkpoint/replay 假设「同一步骤可安全重放得等价结果」，但 Agentforce planner 是非确定性推理，Agent session 本身不是可倒带的状态机。tech-design §1d 对 LangGraph 那侧做了详细并发风险注记，对 Agentforce 这侧完全没有对应分析——削弱「可被 Agentforce 复用的编排底座」这个战略卖点的可信度。
  - **Data Cloud / Prompt Builder 集成路径仍完全空白（V2 残留 #2）**：两份文档搜不到任何字样，比其他 OQ 的处理（至少给倾向/工作假设）更弱。
  - Hyperforce 合规被「接口可插拔」轻描淡写：客户数据存储位置本身须落在 SF 合规存储边界内，外部自建 DynamoDB 可能就不是 Hyperforce 认可的存储位置——比「换个 Provider」重得多。
- **建议 / 替代方案**：
  - 把 Agentforce 技术桥两个悬而未决点升级为新 OQ（OQ-5），交 Agentforce 平台架构团队 + 本项目 owner 联合裁决，deadline 放闸门 B 前；建议结论：Action 异步回调统一走 **Platform Event**（与 Watcher/envelope 设计天然对齐），编排器只把 Agentforce Action 当「至多一次触发、结果异步回调收敛」的黑盒，Agent session 内部推理不纳入 replay 校验——写进 tech-design §2.4 作为 AgentforceActionAdapter 契约。
  - Data Cloud / Prompt Builder 至少补一段方向性草图：审计轨迹作 Data Cloud zero-copy ingestion 源（与 §2c「反馈闭环工具化」天然衔接）；stateFingerprint 扩展为同时校验 Prompt Builder 模板版本（解决「prompt 改了 code 没改」的隐性非确定性）。参考 [Data Cloud zero-copy](https://help.salesforce.com/s/articleView?id=sf.c360_a_zero_copy_data_federation.htm)、[Prompt Builder](https://help.salesforce.com/s/articleView?id=sf.prompt_builder_overview.htm)、[Agentforce](https://www.salesforce.com/agentforce/)、[Einstein Trust Layer](https://www.salesforce.com/products/platform/trusted-ai/)。
  - 给三个桥接点各补一行平台约束占位数字（Platform Event 发布频率上限 / Flow invocable action 同步时限 / Agentforce Action 会话内超时）——与 token 账单「待核准」处理方式一致，保持文档严谨度对称。

### 2. FDE 交付与现场实施 (fde_strategy_agent) — 7.8/10（V2 7.5）
- **改进（vs V2）**：
  - **Provider 化增量成本量价化（§3b，直接回应 V2 残留 #2）**：粗估二期 ≈8–14 人周，明确覆盖「持久化/鉴权/托管/输入源」4 层 Provider 接口固化 + 至少一个非 SF-internal 参考实现 + 干净 org 冒烟——把此前「藏在一期」的真实工作量摆上桌，是本轮 FDE 视角最认可的改动。
  - 可外带 IP 边界表保持稳定（tech-design §4），继续支撑「不是每个现场从零重写」的叙事。
  - §0.2.1 的真实原型证据（4 张截图 + 真实 WI W-23433231 + 端到端时序图）间接提升「这套东西真能跑、值得让 FDE 带出去试」的信心，对二期 FDE 试点立项有正向溢出。
- **遗留问题 / 风险**：
  - **「干净 org 冒烟」≠「真实客户 Org 兼容性验证」——V2 残留 #1 本质未解决**：我 V2 要的是「二期 FDE 培训前至少一个真实客户 Org 的冒烟结论」，V3 给的是「干净/空 org 冒烟」。空 org 天然不含客户既有 Apex 触发器/Flow/自定义对象，恰恰测不出编排器与之**是否打架**——这是一个「看起来响应了、实际测的是另一件事」的更弱替代，风险敞口未实质收窄。
  - **时间线脱节**：Org-共存挂「未来问题」、干净 org 冒烟挂二期 8–14 人周预算，但没有一条明确写「二期 FDE 培训前完成」；OQ-4 的 deadline 针对的是 matrix 定位战略裁决，不是 Org-共存验证本身——两件事容易被误读为已有 deadline 覆盖。
  - **FDE 试点缺可审计成功判据**：工程师侧有清晰的闸门 B 四条 gate，FDE 侧「一期末 1–2 名 FDE 试用」却没有对应判据，容易变成「邀请了、聊了、没结论」。
  - **打包/交付形态空白**：可插拔 Provider 解决「接口在哪切换」，但没回答「FDE 在客户现场怎么实际部署这一整套栈」（Docker/managed package/安装脚本？），落地成本会远高于账面 8–14 人周。
  - **现场支持模型未定义**：FDE 现场遇 Provider 层 bug（如客户 KV 不支持条件写，CAS 语义打折）谁兜底？一二期文档均无 L2 支持/escalation 路径。
- **建议 / 替代方案**：
  - 把「干净 org 冒烟」升级为「近似真实的 dirty org 冒烟」：用 Scratch Org + 预装一个含自定义对象/Flow/Apex 触发器的常见 AppExchange 包做近似（成本远低于找真实客户，但能测出触发器递归、Flow 与 Watcher 事件顺序竞态等冲突面），并明确排入「二期 FDE 培训前」deadline。
  - 给 FDE 试点补一条可审计 gate，与闸门 B 对齐，如「1–2 名 FDE 能否在无核心团队实时支持下、≤3 天内针对自己客户场景跑通一个最小 workflow」。
  - 补一条打包/交付形态决策 + 现场支持模型（哪怕「二期随试点补充」）。可移植运行时分层参考 [Inngest](https://github.com/inngest/inngest)、[Trigger.dev](https://github.com/triggerdotdev/trigger.dev) 的 SDK/Provider 分层；worker↔引擎解耦参考 [Temporal Data Converter/Codec Server](https://docs.temporal.io/production-deployment/data-encryption)、[Camunda Zeebe Job Worker](https://docs.camunda.io/docs/components/concepts/job-workers/) 模式。
  - 决策摘要卡里加一句「FDE 现场可落地性仍是二期待验证项、非一期已解决项」，避免领导层读完 §0.2.1 实战截图后误以为可移植性已验证。

### 3. B2B 商业前景与客户接受度 (business_adoption_agent) — 7.2/10（V2 6.8）
- **改进（vs V2）**：
  - **OQ-3 权重敏感度分析（§2b）**是本轮最强的新分析工作——测三种双权重后「内嵌」基本稳健（唯独议价权双权重打平），把决策收窄为一个可证伪的单变量问题（「独立议价权是否值得放弃 SF 分发+壁垒红利」），远优于 V2 的主观倾向。
  - **付费意愿代理指标口径化（§2c）**从占位升级为三条零问卷、可从审计轨迹客观算出的指标，测「信任/采纳行为」而非「陈述意向」，方向正确；二期「真实预算认领意向测试」升级路径可信。
  - **§0.4 Conditional GO + 两道闸门**给买方清晰的决策结构；自评分小margin（12 vs 14）主动surface而非隐藏，calibration 诚实。
- **遗留问题 / 风险**：
  - **仍零定价锚点（V2 残留，V3 未触）**：LangGraph Platform / Temporal Cloud / Inngest / n8n 都有公开定价，报告从未问「若商业化收什么费、相对买方已付 Temporal/LangGraph 的相邻能力怎么定位」。OQ-3 的 build-vs-embed 是在**定价真空**里做的——这是商用视角最大的剩余缺口，应作为一个具体的、有 deadline 的 open question 显式列出，而非静默缺席。
  - **付费意愿代理指标测的是内部工程师行为、非买方行为**：托管深度/放手程度/决策委托范围是「免费内部工具用户是否越来越信任」的好信号，但 CIO/VP 批预算是另一种心理行为。文档把「内部参与深度」与「付费意愿」混为一谈——建议明确改名为**「使用强度/信任代理」**，「付费意愿」严格保留给二期真实预算测试。
  - **全篇无目标买方画像**：即便「愿景探讨」，一句假设（「早期买方 = 已跑 Agentforce 的企业内、拥有 AI-ops/可靠性预算线的平台工程负责人」）就能让领导层核对闸门 B 四条 gate 是否是**那个买方**的批准标准。目前四条 gate 全是供给侧（吞吐/介入率/token/内部 WTP 代理），无需求侧检查。
  - **时间窗口/竞品侵蚀风险已承认但未再评分**：§2a 承认四条护城河里三条有侵蚀风险，但 OQ-3 敏感度分析只压测权重分配（静态维度），未压测侵蚀轨迹。ROI 仍是 n=1（已诚实降级为 ≥1.5× 试点判据）。
- **建议 / 替代方案**：
  - §2b 加一段定价锚点（哪怕方向性）：拉取 [LangGraph Platform](https://www.langchain.com/langgraph-platform)、[Temporal Cloud](https://temporal.io/cloud)、[Inngest](https://www.inngest.com/) 公开定价（[n8n](https://github.com/n8n-io/n8n) 自托管开源、实为 $0 地板价的工作流竞品），说明假设的内嵌-Agentforce SKU 或独立 SaaS SKU 相对它们落在哪（per-execution vs per-seat vs consumption）——不需硬数字，需展示「定价逻辑被考虑过、非跳过」。
  - §2c 三指标改名为「使用强度/信任代理」，「付费意愿」保留给二期真实预算测试。
  - §0.0 或 §2b 加一句假设买方画像，让闸门 B 可对照该买方实际批准门槛。
  - OQ-3 敏感度表加一行「时间衰减情景」：假设 LangGraph/Temporal 试点末补齐 human-in-the-loop 信号，重跑四维打分看「内嵌胜出」是否仍稳健。
  - §0.0 决策卡把 n=1 caveat 更前置（如「3× 是一人、n=1 未验证；闸门 B 要求 ≥1.5× 复现才进一步投入」），与报告其余处的诚实一致，预先化解领导层 pushback。

### 4. 研发工程 Ops 与成本风险 (engineering_cost_agent) — 8.0/10（V2 7.3，本视角进步最大且分数最高）
- **改进（vs V2，均已核对行号）**：
  - **§3a token 月账单合成**（analyst 288–298）：把框架乘成具体区间——Sonnet 主力 ≈$90–450/月、Opus 档 ≈$450–2,250/月、保守上界「数千美元/月」、结论「大概率 $1.5k/月以内」。这正是 V2 P1「临门一脚」的直接回应，**已解决**。
  - **§5 OQ owner+deadline 表**（analyst 355–364）：OQ-1~4 均补建议 owner + deadline + 工作假设，诚实标注 `[OPEN QUESTIONS]`。相比 V2「提了问题没主人」是实质进展。
  - **§3b Provider 化增量成本**（analyst 325）：新增二期 ≈8–14 人周，明确「列入二期预算而非藏在一期」。
  - **tech-design §1d 档位1 风险注记**（147–152）：新增「6–10 人周若含驯服 LangGraph 并发模型估计偏乐观」+ DBOS 走 Postgres 与公司 DynamoDB 栈冲突——技术债务视角最想看到的诚实修正，已采纳。
  - **tech-design §2.1 护栏多实例共享写设计**（208–219）：从 V2「未提」变成有具体机制（DynamoDB 共享护栏项 + 条件写 + 按 dependency 分片）。
- **遗留问题 / 风险**：
  - **A. ECS/Fargate 一期应急退路成本仍未纳入 M1–M4（V2 残留 #3 未解决）**：ECS/Fargate 全文档 4 处均为定性描述（R1、OQ-4、tech-design §组件B/§4），M1–M4 里程碑表无应急预算行或缓冲。§3b 的 8–14 人周是**二期通用适配**成本，≠ **一期 matrix 延期时的 ECS 应急退路**成本（不同触发条件），后者被排除在任何数字之外。**确认 V2 第三条残留在 V3 仍未解决。**
  - **B. 护栏共享写成本未反映进 token/延迟/云资源预算（新发现，恰命中本视角检查项）**：tech-design 217 只有一句定性「每次认领/放行多一次条件写……分片分散」，从未折算进 §3a 云资源月成本（DynamoDB 额外写请求量），也未折算进任何延迟预算（哪怕「+个位数毫秒、可忽略」的一句话结论都无）。**评审方检查问题成立，真实缺口。**
  - **C. §3a Opus 单价倍数存在可核实偏差（新发现，方向保守、非致命）**：文档假设「Opus 约 5× 单价」（analyst 295），但当前 Anthropic 公开定价 Sonnet $3/$15、Opus $5/$25，纯单价比 = **1.67×，非 5×**。若按 1.67× 折算，Opus 档月账单应落 ≈$150–750/月而非 $450–2,250/月——**文档把 Opus 档高估约 3×**。不致命：(a) 高估方向对决策层保守有利；(b) 5× 可能隐含「Opus 单步 token 消耗（尤推理/输出）更高」这一现实，但文档没明说；(c) 核心结论「$1.5k/月以内」用 Sonnet 档，不依赖 Opus 数字。既然已有权威定价可核准，建议直接订正。
  - **D. Salesforce/GUS/Slack/GitHub 外部 API 限额风险 = 全新盲区**：全文档「限流/rate limit」只命中我们自己 LLM 调用的令牌桶护栏，从未讨论 15–25 并发 workspace 规模下对 SF Core API 每日请求限额、GUS/Slack/GitHub API 的消耗测算——这些下游系统本身有 governor limits，一旦并发跑 WI 循环，调用量级从未被估算。
- **建议 / 替代方案**：
  1. M1–M4 表新增一行「M2 应急缓冲：ECS/Fargate 自建最小托管（matrix 延期触发）」+ 触发条件 + 2–4 人周量级估算，而非留白。
  2. tech-design §2.1 补护栏共享写成本量化：DynamoDB 条件写单价 × 预估每步认领/放行次数 → 折算进云资源月成本；延迟侧给「+X ms per-step」量级（个位数毫秒，可参考 AWS 官方给保守上界）。
  3. **Opus 定价订正**：analyst 295「约 5× 单价」改为基于当前定价（Opus $5/$25、Sonnet $3/$15，比 ≈1.67×）重算 Opus 档 ≈$150–750/月，并可去掉「待 claude-api 核准」的 hedge（现已可核准）；若仍想保守，明写「因 Opus 单步 token 消耗通常高于 Sonnet，实际倍数取 X」。可提 prompt caching（cache read ≈0.1× 基础输入价、~90% 折扣）作为进一步压账单杠杆。参考 [DBOS](https://github.com/dbos-inc/dbos-transact-py)、[LangGraph checkpointer](https://github.com/langchain-ai/langgraph)、[resilience4j](https://github.com/resilience4j/resilience4j)。
  4. R 风险表新增一行外部 API 限额：15–25 并发 workspace × 每 workspace 下游 API 调用估算，对照 SF Core API / GUS / Slack / GitHub 已知限额，给初步撞限额判断，用与 R8 同样的「硬上限 + 熔断」框架覆盖外部 API 侧。

## 关键建议（按优先级）

1. **[P1] 订正 §3a Opus 单价倍数**（成本视角，唯一「已可核准」的硬数字）：现假设 5× 实为 1.67×（Opus $5/$25 vs Sonnet $3/$15），Opus 档月账单被高估约 3×（应 ≈$150–750/月）。方向保守不致命，但既有权威定价即可核准，建议直接订正并去掉「待 claude-api 核准」hedge；若保留保守估算须明写「Opus 单步 token 消耗更高」的假设。
2. **[P1] M1–M4 补一期 matrix 延期的 ECS/Fargate 应急退路预算行**（2–4 人周量级）：这是 V2 至今未解决的残留，与二期 8–14 人周 Provider 化是不同触发条件的两笔钱，不能混淆。
3. **[P2] 补外部系统 API 限额风险分析**（SF Core/GUS/Slack/GitHub）：15–25 并发 workspace 对下游 API 的消耗测算 + 撞限额判断，纳入 R 风险表。当前护栏只防我们自己的 LLM 调用风暴，不防下游 governor limits——新盲区。
4. **[P2] §2c 三指标改名「使用强度/信任代理」**，「付费意愿」严格保留给二期真实预算认领测试——避免把内部工程师参与深度 overclaim 为买方付费意愿。
5. **[P2] §2b 加定价锚点 + 假设买方画像**：即便方向性，展示定价逻辑被考虑过；给闸门 B 四条 gate 一个需求侧对照。竞品定价参考 LangGraph Platform / Temporal Cloud / Inngest / n8n。
6. **[P2] Agentforce 技术桥两个悬而未决点升级为 OQ-5**（Action 回调走 Platform Event 的决策 + workid↔session 生命周期 = 黑盒契约），并补 stateFingerprint 与 Agentforce 非确定性 planner 的共存分析——支撑「Agentforce 编排底座候选内核」这一战略卖点的可信度。
7. **[P2] 「干净 org 冒烟」升级为「dirty org 冒烟」**（Scratch Org + 预装含触发器/Flow 的 AppExchange 包），并明确排入「二期 FDE 培训前」deadline；FDE 试点补一条可审计成功判据。

## 未解决 / 待 writer 回应的问题

- [ ] §3a Opus 单价倍数订正（5× → 1.67×，Opus 档 ≈$150–750/月），去掉「待核准」hedge 或明写更高 token 消耗假设。
- [ ] 一期 matrix 延期的 ECS/Fargate 应急退路成本（2–4 人周量级）纳入 M1–M4——V2 至今未解决。
- [ ] 护栏共享条件写的成本（云资源月成本增量）与延迟（+X ms per-step）量化——tech-design §2.1 仅定性一句。
- [ ] 外部系统 API 限额风险（SF Core/GUS/Slack/GitHub）在 15–25 并发下的消耗测算——全新盲区。
- [ ] 商业维度：定价锚点（相对 Temporal/LangGraph/Inngest/n8n）+ 假设买方画像——V2 至今未触，报告主动收窄为「愿景」，但应作为有 deadline 的显式 open question。
- [ ] §2c 付费意愿代理指标改名为「使用强度/信任代理」，避免 overclaim。
- [ ] Agentforce 技术桥落地未知（Action 回调机制决策、workid↔session 生命周期、stateFingerprint 与非确定性 planner 共存）+ Data Cloud / Prompt Builder 集成路径——V2 残留，V3 未推进（远期，落地才暴露复杂度，但战略结论已先行）。
- [ ] 客户 Org 真实兼容性验证（干净 org → dirty org 冒烟）+ FDE 试点可审计判据 + 打包/交付形态 + 现场支持模型。
