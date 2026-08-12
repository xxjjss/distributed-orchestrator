# Product Review — V2

**总评分：7.2/10**（四项加权平均，等权；较 V1 的 6.4 提升 +0.8）
**一句话结论：** 需打磨 → **接近可推进**。V2 把 V1 提的两个 P0 与三个 P1 **逐条落地**，一期「内部研发效率工具」的立项论据已相当扎实、可交决策层；作为「可商业化产品」仍是愿景阶段（这是报告主动收窄的定位，非缺陷），扣分集中在**未验证的商业需求 + 两项外部依赖（matrix/OQ-1）仍未收敛**。

## 概述

V2 是一次**高完成度的回归修订**。相较 V1，最显著的三点变化：

1. **文档拆分**（回应 human comment）：`project-analyst`（产品/领导层，本轮产品评审主对象）+ `tech-design`（技术审核人）交叉引用，可行性叙事与技术实现分层清晰，presentation 时人类只读可行性报告的诉求被满足（§0.1 P1–P5 痛点表作为 why）。
2. **分期主线钉死**：「一期推工具、二期推环境、长期推产品」贯穿全篇，商业化明确降级为「愿景/可能性探讨」，一期只承诺内部收益——这个诚实定位反而提升了立项可信度。
3. **V1 的 5 条关键建议全部有实质回应**（见下「V1→V2 改进评估」）。

**本轮打分逻辑**：产品评审的尺子是「商业可行 + 客户需求 + 接受度」。V2 在**内部一期**这条最可信的价值链上几乎无短板；商业化章节做到了「诚实探讨 + 埋先行信号」的上限，但真实买方/定价/需求仍空白（报告自认，列 OQ-3），且 matrix（OQ-4/R1）与 OQ-1 两个立项前置变量仍未由外部确认——这两条封住了 7.2 以上的空间。

### V1 → V2 改进评估（逐条对照 V1 的 5 条关键建议）

| V1 建议 | 优先级 | V2 落地情况 | 评价 |
|---|---|---|---|
| 补 Token/成本量化（人月+里程碑+云成本+LLM Token 预算+每-WI 上限/熔断） | **P0** | §3a 新增 M1–M4 里程碑（档位1 ≈11–17 / 档位2 ≈16–24 人周）、云资源月成本（几十至低几百美元）、**LLM Token 预算框架**（并发 15–25 × 步数 30–80 × 单步 15–40k token）、`tokenSpent` 字段 + per-workspace 硬上限 + 熔断（R8）、memoization 省 token、运维隐藏成本 0.2–0.5 人力 | **充分解决**。这是全篇进步最大处，V1 的硬缺口被填平 |
| 画出可外带 IP 内核边界，鉴权/托管做可插拔 Provider | **P0** | tech-design §4 给出「可外带 IP vs 内部专属需重写」完整清单，鉴权/托管/持久化/输入源全部收敛为可插拔 Provider；R9 新增可移植性悬崖；FDE 试点判据加「非 SF-internal 环境冒烟」 | **充分解决** |
| 给 §2d 一条真正的 Agentforce/Platform 技术桥 + 多租户/合规前瞻 | P1 | §2d 给出 4 段接口草图（编排器作 Agentforce Action 长跑后端 / Flow async 编排层 / Platform Events 双向 / 多租户前瞻）；tech-design §3 正面回答「为何不用 Flow Orchestrator」+ Einstein Trust Layer 商业化门槛 + Hyperforce | **基本解决**（仍是草图非实现，见下 sfdc 分项） |
| 商业化 OQ-3 二维打分 + 埋付费意愿代理指标 | P1 | OQ-3 升级为 4 维打分（TAM/壁垒/分发/议价权，12 vs 14 倾向内嵌）；§2c 新增付费意愿代理指标 | **基本解决**（打分为自评，敏感度未测，见 business 分项） |
| 锁定 OQ-1 时间线（立项前置阻塞项 + owner + deadline） | P1 | OQ-1 已标为「最高优先，立项前置阻塞项」，与 token 账单绑定；档位1/2 工作量分档 | **部分解决**：定性已到位，但仍**未指定 owner + deadline 的实际值**，仍是未收敛的外部变量 |

**结论**：V1 的 P0（成本量化、可移植 IP 边界）**已全部消除**；三条 P1 从「断言」升级为「路径/草图」。剩余问题从「文档缺失」性质转为「外部依赖未收敛 + 商业需求本质上尚不可验证」性质——后者非 writer 单方可解。

## 分项评审

### 1. Salesforce 架构与研发 (sfdc_architect_agent) — 7.0/10（V1 6.5）
- **视角适用性**：一期仍是 AWS/TCM-native 编排基础设施（DynamoDB 单表 + SFN + SQS + MCP adaptor），不触碰 Platform（Apex/LWC/Flow）元数据，Governor Limits / AppExchange Security Review 对一期不适用——报告定位诚实。本视角评估战略落点（Agentforce/Platform 耦合）。
- **改进**：V1 最大痛点「§2d 是断言、缺技术桥」已解决——§2d 4 段接口草图把「互补」从口号变为可达路径；tech-design §3 正面回答了「为何不在 Flow Orchestrator 上建」（Flow 无 lease/affinity/token 预算/脱机续跑语义）；Einstein Trust Layer 列为商业化前置门槛、Hyperforce 多租户/数据驻留列远期架构约束；per-submitter 隔离 → Hyperforce 租户隔离的鸿沟已被点名（回应 V1）。
- **遗留问题 / 风险**：
  - 技术桥仍是**接口草图、一期不实现**——可接受（一期不碰客户数据），但「编排器 ↔ Agentforce」的关键未知（Action 超时/异步回调用 Platform Event 还是 Agentforce notification、`workid` 与 Agent session 的生命周期映射）留到落地才会暴露真实复杂度。
  - **Data Cloud / Prompt Builder 集成路径**仍未展开（V1 也提过）——若远期定位为 Agentforce 底座，Data Cloud 作为 grounding/数据面是绕不开的一环。
  - `stateFingerprint` 非确定性检测与 Agentforce 自身 reasoning/planner 的共存关系仍未提。
- **建议 / 替代方案**：远期进 Platform 前，评估编排器状态跃迁经 Platform Event 上 Data Cloud 的可行性（避免 DynamoDB 事实源与 Platform 数据模型二次冲突）。参考 Agentforce 能力边界 https://www.salesforce.com/agentforce/ 、Flow Orchestrator https://help.salesforce.com/s/articleView?id=sf.flow_concepts_orchestrator.htm 、Einstein Trust Layer https://www.salesforce.com/products/platform/trusted-ai/ 。

### 2. FDE 交付与现场实施 (fde_strategy_agent) — 7.5/10（V1 7.0）
- **改进**：V1 的最大卡点「可移植性悬崖」已被**正面处理**——tech-design §4 的「可外带 IP vs 内部专属需重写」清单精确划出边界（状态机语义/事件契约/路由/韧性框架可外带；DynamoDB/MCP/matrix/GUS 实现现场换 Provider），鉴权/托管/持久化/输入源全部做成可插拔 Provider；R9 显式登记可移植性悬崖；FDE 试点判据加「非 SF-internal 环境冒烟」（干净 org 跑通最小内核）——这正是 V1 建议的「提前暴露可移植性债务」。§2c 把 FDE 现场落地问题（与客户 Org Customizations 共存、通用 AI 组件、合规/数据驻留）作为未来问题点名，符合 human comment「一期只点名、不给确切方案」的定位。
- **遗留问题 / 风险**：
  - 「客户既有 Org Customizations（自定义对象/Flow/Apex 触发器）共存」仍**只点名未设计**——这是 human comment 明确批准一期不展开的，可接受；但需在二期 FDE 培训前给出至少一个真实客户 Org 的冒烟结论，否则 Provider 抽象是否够用仍是纸面假设。
  - **Provider 化的增量成本未单独计价**：§3a 的 M1–M4 是内部一期口径，未含「把 4 层 Provider 化 + 客户现场适配」的额外人力——FDE→客户的商业故事里这是真实工作量，建议二期蓝图补一个粗估。
- **建议 / 替代方案**：一期末邀 1–2 名 FDE 用真实客户场景反推 worker 抽象通用性（报告已列，good）。可移植运行时分层参考 Inngest https://github.com/inngest/inngest 、Trigger.dev https://github.com/triggerdotdev/trigger.dev 的 SDK/Provider 分层。

### 3. B2B 商业前景与客户接受度 (business_adoption_agent) — 6.8/10（V1 6.0）
- **改进**：OQ-3 从「倾向后者」升级为 **4 维打分**（TAM 4/3、壁垒 2/4、分发 2/5、议价权 4/2，合计 12 vs 14 倾向内嵌 Agentforce），并**诚实写出内嵌的代价**（议价权与独立商业价值被削弱）——V1 批评「只写正面」已修正；§2c 埋「付费意愿代理指标」（愿否托管更多工作流/愿放弃盯屏多久/愿交多大决定权）作为二期需求先行信号；§2a 明确「四条护城河里只有『本机/云端统一事实源』最真实，其余三条有被时间窗口蚕食风险」——竞品定位诚实。
- **遗留问题 / 风险**：
  - **需求仍未验证**：一期无外部买方，商用买方（CIO/VP/Admin）意愿仍是推断，无定价、无目标客户画像。报告主动把这收窄为「愿景探讨」，定位正确；但这也意味着「商业可行性」这把尺子在商用维度只能给中位分。
  - **4 维打分是自评且分差小**（12 vs 14）：权重等权、分值主观，敏感度未测——换一组权重结论可能翻转。作为战略讨论足够，作为拍板依据偏薄。
  - **时间窗口风险是真实的**：LangGraph Platform / Temporal（signals + human-in-the-loop）/ Inngest 正快速补齐「LLM-native 显式状态 + 信号人机闭环」；「本机/云端统一事实源」这条差异点客户是否愿付费仍存疑。ROI 论据仍依赖 n=1 的 3×（已诚实降级为 ≥1.5× 试点判据）。
- **建议 / 替代方案**：
  - 二期正式商用判断前，把付费意愿代理指标转化为一次真实的「内部部门付费/预算认领」意向测试（比问卷更硬）。
  - OQ-3 建议做一次权重敏感度分析（例如给「分发」双倍权重 vs 给「议价权」双倍权重），让战略层看到结论的稳健性。
  - 竞品定价对照参考：LangGraph Platform https://www.langchain.com/langgraph-platform 、Temporal Cloud https://temporal.io/cloud 、Inngest https://www.inngest.com/ 、n8n（远期图形化编排的强免费对手）https://github.com/n8n-io/n8n 。

### 4. 研发工程 Ops 与成本风险 (engineering_cost_agent) — 7.3/10（V1 6.0）
- **改进（本视角进步最大）**：V1 的 P0 硬缺口「成本/Token/工期量化缺席」被**系统性填平**——§3a 给出 M1–M4 里程碑与人周区间（档位1 ≈11–17 / 档位2 ≈16–24，约 1 季度）、云资源月成本量级、**LLM Token 预算的可算框架**（并发 workspace × 每 workspace 步数 × 单步 token × 单价，每 workspace ≈1–3M token）、运维隐藏成本估 0.2–0.5 人力。失控烧钱被 R8 + `tokenSpent` 字段 + per-workspace token/attemptCount 硬上限 + 熔断（tech-design §2.1）+ memoization 省重复调用治理——既是成本护栏也是安全护栏。OQ-1 与 token 账单显式绑定（能引 MIT 依赖既省工期又省 token）。matrix 未就绪的退路（ECS/Fargate，R1/OQ-4）已给。
- **遗留问题 / 风险**：
  - **未给出「一期试点总月度 token 账单」的合成估算**：框架齐全（15–25 并发 × 1–3M token/workspace），但没乘出一个「一期每月约 $X」的区间——决策层最想看的正是这个总数。单价还标「须以 claude-api 实际定价核准」，未定稿。（按报告参数粗算：若 15–25 workspace/月周转、每个 1–3M token、Sonnet 混合价，量级约数百至数千美元/月，Opus 则数倍——建议报告直接给出这个量级区间，即便标注为待核准。）
  - **OQ-1 仍未收敛**：档位1 vs 档位2 的工期差（≈5–7 人周）与 token 差（memoization 能否复用）都押在 OQ-1 上，而 OQ-1 仍无 owner+deadline 实际值——一期最大单点变量仍悬空。
  - **matrix/OQ-4 是最大交付风险**：一期关键路径押在不受控的外部平台排期上；退路（ECS/Fargate 自建）的增量人力仍未计入 M1–M4。
- **建议 / 替代方案**：
  - §3a 补一行「一期每月 token 账单合成区间（Sonnet / Opus 两档）」，哪怕标注待 claude-api 核准——这是立项数字的临门一脚。
  - 给 OQ-1 / OQ-4 落实际 owner + deadline（法务/架构、matrix 团队），否则成本区间的上下界无法收窄。
  - memoization 省 token 参考 DBOS https://github.com/dbos-inc/dbos-transact-py 、LangGraph checkpointer https://github.com/langchain-ai/langgraph ；熔断参考 resilience4j https://github.com/resilience4j/resilience4j 。

## 关键建议（按优先级）

1. **[P1] 给出一期总月度 LLM token 账单的合成区间**（成本视角，临门一脚）：把已有的「并发 × 步数 × 单步 × 单价」框架乘成一个「约 $X–$Y/月（Sonnet / Opus 两档）」的数字，即便标注待 claude-api 核准。这是决策层立项最后要看的一个数。
2. **[P1] 落实 OQ-1 与 OQ-4 的实际 owner + deadline**：两者分别封住成本区间上界（自研 vs 引依赖）与交付关键路径（matrix 排期）。当前定性已到位，缺的是「谁、何时确认」的硬承诺。
3. **[P2] OQ-3 做权重敏感度分析**：4 维打分 12 vs 14 分差小且等权主观，给战略层看结论稳健性，避免拍板依据偏薄。
4. **[P2] 二期蓝图补 Provider 化 + 客户现场适配的增量成本粗估**：FDE→客户商业故事的真实工作量，当前 M1–M4 未覆盖。
5. **[P2] 把付费意愿代理指标升级为一次真实预算意向测试**（二期）：比问卷更硬的 demand 先行信号。

## 未解决 / 待 writer 回应的问题

- [ ] 一期每月 LLM token 账单的**合成金额区间**（框架已备，缺最终乘积数字 + Sonnet/Opus 两档）。
- [ ] OQ-1（能否引 MIT LangGraph/DBOS）与 OQ-4（matrix 定位/排期）的**实际 owner + deadline**——一期成本与交付的两个未收敛外部变量。
- [ ] 商业化真实需求信号：付费意愿代理指标 → 真实预算意向测试的转化路径（二期）。
- [ ] Provider 化 + 客户现场适配的增量人力（FDE→客户可移植性的成本面）。
- [ ] OQ-3 4 维打分的权重敏感度（结论稳健性）。
- [ ] （轻）编排器 ↔ Agentforce 的生命周期/回调映射与 Data Cloud grounding 路径（远期，落地才会暴露复杂度）。
