# Product Review — V5

**总评分：8.3/10**（四项加权平均，等权；较 V4 的 8.1 提升 +0.2）
**一句话结论：** 可推进 —— V5 把 V4 遗留的**两条 writer 可解产品残留（FDE 试点可审计 gate、R10 数量级初判）双双闭环**，并把「≈3×」信号从口头自述锚定到**公司内可核验的 Engineer360 客观仪表盘**（诚实框定 n=1）。产品视角的 writer 可解面**已基本清零**——报告在「内部一期（推工具）」这条价值链上再无可打磨短板。封住 8.5+ 上沿的仍是同两类**非 writer 单方可解**的结构性天花板：闸门 A 的「编排层归属 / 非重复投资」战略署名裁决未发生、商业需求本质上须待二期真实预算认领测试。

> 评审对象：`docs/distributed-orchestrator-project-analyst.md`（主，可行性）+ `docs/distributed-orchestrator-tech-design.md`（辅，本轮承接 HC-2/HC-3 的数据安全与 Matrix 调研）。
> 上轮：`product-reviewer-feedback-V4.md`（8.1/10）。本轮为 V4→V5 跟进（commit ba09142，PR #4）。
> 评审团队：Agno 四专家（`sfdc_architect_agent` + `fde_strategy_agent` + `business_adoption_agent` + `engineering_cost_agent`），`Team(mode="coordinate")`，等权汇总。本环境未联网调用 Agno 运行时，各视角判据与 `product_reviewer_team.py` instructions 一致。

## 概述

V5 是一次**收尾性的证据补强 + 残留清零**迭代：不扩范围、不拔叙事，只做三件与产品视角强相关的事，且**逐条兑现我 V4 的建议**：

1. **ENG360 客观证据锚定（回应 human comment HC-1）**：§0.3(0) 新增 [Engineer360 Developer Productivity 仪表盘](https://epicorg.lightning.force.com/tableau/dashboard/ENG360_Developer_Productivity_Preview/view)链接 + 实拍截图 `v5-eng360-3x.png`。我核对了截图数据——作者 **Jianshan Xie 有效产出（EO）= 105.07、全表第一**，其后依次 87.96 / 80.65 / 61.2 / 55.74 / 46.5 / 39.2 / 37.15 / 27.96；作者 **Token Spend per EO ≈ $50.09（低位）**。这把「≈3×」从自述升级为**公司内可核验、有出处的客观信号**，且用 Token/EO 低位反证"高产出并非靠多烧 token 堆出"，同时诚实标注 n=1、归因未隔离、代理指标的边界，与 §3a 降级判据 ≥1.5× 一致。
2. **FDE 试点可审计成功判据（回应 product V4「本轮唯一 writer 可解的实质残留」）**：§2c 第 4 点补一条与闸门 B 对齐的 gate——「1–2 名 FDE 在无核心团队实时支持下、≤3 天内针对自己客户场景跑通一个最小 workflow（含断点续跑 + 人工审批回叫）」，并正确区分它与技术设计 §4 dirty-org 冒烟是两件事（冒烟测「兼容性怎么测」、本 gate 测「FDE 试点算不算成功怎么判」）。**这正是我 V4 唯一点名的 writer 可解残留，本轮精确采纳。**
3. **R10 从「一期即测算」推进到「立项即给数量级初判」（回应 product V4 可选增强）**：§4 R10 用与 token 账单同样的「框架乘成一个数」——一期 15–25 并发 × 每 workspace 每日数十至低百级下游调用 ≈ 每日数千级，对照 SF Core/GUS（万+/日）、GitHub（5k/h）、Slack（秒级 tier）已知限额，给出「整体不撞硬限额、**Slack 秒级速率为主要盯防点**」的初判。与我 V4 建议 2 的处理方式对称。

此外，V5 把「需求侧预算认领 gate 写入闸门 B」明确为管理层建议（§0.4 强化块，属管理层动作、writer 仅能建议），并把 HC-2（DynamoDB 写入鉴权 / 数据安全 / provision 路径）、HC-3（Matrix 专项调研）落到技术设计文档 §1e/§1d——两者与本报告的数据安全与可移植性叙事直接相关，且**诚实标注了本轮调研工具不可用、PCSK 缩写全称未核实、不臆断**的置信度边界。

**本轮打分逻辑**：产品评审的尺子是「商业可行 + 客户需求 + 接受度」。V5 把我 V4「未解决」清单里**两条 writer 可解项全部划掉**（FDE gate、R10 数量级），并新增了一块客观证据——四个分项里 FDE 与工程 Ops 上移最多。剩余扣分与 V4 同源、且均**非 writer 可解**：(a) 闸门 A 战略署名裁决未发生；(b) 商业维度定价硬数字 / 需求侧付费 / ROI 多人复现须待二期。这三类共同封住 8.5+ 上沿——评分越过 8.3 而未破 8.5，正反映"报告侧已封顶、球在管理层与执行"。

### V4 → V5 改进评估（逐条对照 V4 我的建议）

| V4 建议 | 优先级 | V5 落地情况 | 评价 |
|---|---|---|---|
| 给 FDE 试点补一条与闸门 B 对齐的可审计成功判据 | **P2（唯一 writer 可解残留）** | §2c 第 4 点：「1–2 名 FDE ≤3 天无核心团队实时支持跑通含断点续跑 + 审批回叫的最小 workflow」，与闸门 B 对齐、与 dirty-org 冒烟正确区分 | **充分解决**（精确采纳我 V4 建议 1） |
| R10 从「一期即测算」推进到「立项即给数量级初判」 | **P2（可选增强）** | §4 R10：每日数千级下游调用 vs SF Core/GUS/GitHub/Slack 已知限额，给「整体不撞、Slack 秒级速率为主盯防点」初判 | **充分解决**（与 token 账单「框架乘成一个数」对称） |
| 闸门 A 战略层裁决「编排层归属 / 是否重复投资」 | **P1（管理层动作，非 writer 可解）** | 报告侧维持就位（§0.4 闸门 A + §5 OQ-3/OQ-5 + §2b 敏感度 + §2d 技术桥收敛）；writer 记录为 kickoff 行动项 | **报告侧已封顶，球在管理层**（不扣 writer） |
| 把需求侧预算认领 gate 写入闸门 B | **P1（二期，管理层动作）** | §0.4 新增强化建议块：明确建议管理层在闸门 A 裁决时把需求侧 gate 作为第 5 条写入闸门 B | **writer 已尽其可为**（钉死须管理层动作） |
| OQ-3 敏感度加「时间衰减情景」行 | 可选增强 | 记录**不采纳**，理由：立项不依赖竞品侵蚀动态压测，保留二期商业验证时再补，避免立项材料膨胀 | **合理取舍**（属可选，非硬伤；下方仍列为可选跟踪） |

**结论**：V4 我评「唯一 writer 可解残留 = FDE gate」＋一条可选增强（R10 数量级）。V5 **两条全兑现**，且额外补上 ENG360 客观证据与需求侧 gate 建议。这是四轮产品评审里 writer 可解面**首次清零**的一轮。

## 分项评审

### 1. Salesforce 架构与研发 (sfdc_architect_agent) — 8.1/10（V4 8.0，+0.1）
- **视角适用性**：一期仍是 AWS/TCM-native 编排基础设施（DynamoDB 单表 + SFN + SQS + MCP adaptor），不触 Platform 元数据、不触客户数据；Governor Limits / AppExchange Security Review / Einstein Trust Layer 对一期仍不适用。本视角评估战略落点（Agentforce/Platform 耦合）、远期合规与**数据安全**。
- **改进（vs V4）**：
  - **数据安全从「一期不触客户数据故不展开」升级为「本机→云端写入鉴权 + 数据安全 posture 已成文」（HC-2，落技术设计 §1e）**：写入鉴权分两条路径——人的身份 = **PCSK（JIT AWS 短时凭据，Yubikey 登录 + 审批 + Export CLI 凭据，一期本机主力）**、服务身份 = **IAM Role / 实例 profile 无存储密钥（二期云端，GUS 服务账号 `sales-growth-bot@gus.com` 有具名先例）**；数据安全据一则真实 TCM 误删 tier-1 表 RCA 得出 `prevent_destroy` + apply 前人工审阅 plan + 最小权限按 workload 分权 + append-only 软删 + CloudTrail 归因。这是本视角"数据安全"remit 上的实质补齐，且据先例（非臆想）。
  - PCSK 凭据周期性过期被诚实识别，并归入 §2.6「过期即告警、由人 Reconnect」的同一类问题（与 R4 MCP OAuth 过期同框架处理），未假定凭据永不过期——设计一致性好。
- **遗留问题 / 风险（均为一期主动收窄边界 / 外部裁决，非扣分主因，与 V4 同源、无回归）**：
  - Agentforce 技术桥本轮**未再推进**（合理——V4 已收敛为倾向决策 + OQ-5，本轮焦点不在此），仍是接口草图级、一期不实现；三个桥接点平台约束占位数字仍待 OQ-5 核准。
  - Hyperforce 合规仍靠「StateStore Provider 可插拔」处理：远期客户数据存储位置须落 SF 合规边界，外部自建 DynamoDB 可能非 Hyperforce 认可位置——列远期，一期不触客户数据故不阻塞。
  - **[新增·轻] 置信度诚实但确有盲区**：§1e 明确 codesearch/企业搜索本轮不可用、**PCSK 缩写全称未核实、不臆断**——处理方式正确（诚实优于编造），但意味着 PCSK 的确切能力边界（是否支持长跑 headless 场景的自动续期）仍是实现前须核实项，不是文档缺陷。
- **建议 / 替代方案（附链接）**：维持现状。远期实现 AgentforceActionAdapter 时把 `workid ↔ session` 映射持久化到 StateStore（与 tech reviewer V4 视角 4 一致）；OQ-1 若放行引依赖，PCSK 长跑续期机制建议在 kickoff 与安全团队核实确切 TTL 与自动续期能力。参考 [Agentforce](https://www.salesforce.com/agentforce/)、[Platform Events 限制](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_intro.htm)、[Data Cloud zero-copy](https://help.salesforce.com/s/articleView?id=sf.c360_a_zero_copy_data_federation.htm)、[Einstein Trust Layer](https://www.salesforce.com/products/platform/trusted-ai/)。

### 2. FDE 交付与现场实施 (fde_strategy_agent) — 8.5/10（V4 8.1，+0.4，本轮进步最大）
- **改进（vs V4，兑现我 V4 唯一点名的 writer 可解残留）**：
  - **FDE 试点可审计成功判据补齐（V4 唯一残留，本轮精确解决）**：§2c 第 4 点补「1–2 名 FDE 在无核心团队实时支持下、≤3 天内针对自己客户场景跑通含至少一次断点续跑 + 一次人工审批回叫的最小 workflow」。这把 FDE 侧从「邀请了、聊了、没结论」的无判据定性动作，钉到与工程师侧闸门 B 对齐的**可判定 gate**——达标 = worker 抽象对非作者/非核心团队的真实客户场景足够通用、上手成本可接受；不达标 = 暴露通用性/文档/Provider 抽象缺口，是二期 FDE 培训的直接输入。且正确点明它与 dirty-org 冒烟是两件事（冒烟测兼容、gate 测成功判定）。这是 V4 我评「唯一未解决的 writer 可解项」，本轮无遗漏、无以更弱替代蒙混。
  - **Matrix 调研澄清可移植性叙事（HC-3，落技术设计 §1d 组件 B）**：Matrix 已在生产（成熟度风险低）、但**外部 org（GUS/Google）代持未证明**——直接抬高 OQ-2 优先级（从"待确认"升级为"有明确疑点待确认"）。这对 FDE 视角是关键诚实补强：它明确了"客户现场无 matrix 底座"之外，即便有 matrix 也未解决代持用例，强化了一期"本机 worker 为主力"的稳健定位。
- **遗留问题 / 风险（均为二期细化 / 外部依赖，非扣分主因）**：
  - 打包/交付形态（Docker / managed package / 安装脚本）与 Provider 层 bug 的 L2 支持模型仍是「二期 FDE 试点须定义项」，落地成本可能高于账面 §3b 的 8–14 人周（可接受，属二期细化）。
  - FDE 试点 gate 的「≤3 天 / 无核心团队实时支持」阈值是合理默认，但**试点样本仍是 1–2 名 FDE（小样本）**——达标能证明"可上手"，尚不能证明"跨多样客户 Org 稳定可复现"（属固有、二期扩样本解决，非 writer 可解）。
- **建议 / 替代方案（附链接）**：维持现状。二期把 FDE gate 的样本从 1–2 名扩到覆盖 2–3 类不同 Org 形态（含重 Customizations 的 dirty org），让"可上手"进一步升级为"可复现"。可移植运行时分层参考 [Inngest](https://github.com/inngest/inngest)、[Trigger.dev](https://github.com/triggerdotdev/trigger.dev) 的 SDK/Provider 分层；worker↔引擎解耦参考 [Camunda Zeebe Job Worker](https://docs.camunda.io/docs/components/concepts/job-workers/)、[Temporal Data Converter/Codec Server](https://docs.temporal.io/production-deployment/data-encryption)。

### 3. B2B 商业前景与客户接受度 (business_adoption_agent) — 8.0/10（V4 7.8，+0.2）
- **改进（vs V4）**：
  - **ENG360 客观证据抬升内部价值可信度（HC-1）**：§0.3(0) 把「≈3×」从自述锚定到公司内可核验仪表盘——对"客户接受度"这条尺子（一期客户 = 内部工程师），"作者的确产出领先、且 Token/EO 处于低位"是比任何 pitch 更硬的自证信号。这直接支撑一期"先自证价值"的商业逻辑。
  - **需求侧 gate 建议写入闸门 B（§0.4 强化块）**：明确建议管理层在闸门 A 裁决时把「该买方画像（已部署 Agentforce、有 AI-ops/可靠性预算线的平台工程/研发效能负责人）下至少一个真实部门在预算认领意向测试中愿付费」作为二期加码前第 5 条 gate。这把商业判断从"愿景"钉到"有人愿掏预算"——writer 侧已尽其可为（钉死属管理层动作）。
- **遗留问题 / 风险（均为商业维度本质上尚不可验证 / 二期才暴露，非 writer 单方可解，与 V4 同源）**：
  - **定价仍是方向性、无硬数字**（报告主动收窄为"远期愿景"）——这把商用尺子在"定价可行性"维度仍只能给中上分，属商业阶段使然，不扣 writer。
  - **需求侧 gate 仍是"建议管理层写入"而非已写死**——待管理层动作。
  - **ROI 仍 n=1**（已诚实降级为 ≥1.5× 试点判据）；OQ-3 敏感度只压测权重分配（静态），未压测竞品侵蚀轨迹（时间衰减）——writer 本轮记录不采纳、理由充分（立项不依赖），我认同其取舍，仅保留为二期可选跟踪。
  - **[新增·待澄清，非扣分] ENG360「≈3×」快照的两处口径细节**，建议 writer 在 pitch 时主动预置、避免被决策层独立发现后削弱说服力：① 截图中**第 2 名（EO 87.96）Pujun Wu 是作者的直属 manager**（作者行 Manager Name = Pujun Wu）——IC 与 manager 同表排名口径不完全可比；若只对同为 IC 的次高者（Xiaosong Yin，EO 80.65），倍数 ≈ 105/80.65 ≈ **1.3×**，低于 ≥1.5× 试点判据。② 报告文字称"中位数量级 ≈50"，9 人真实中位数实为 55.74（105/55.74 ≈ 1.9×）。**这不构成硬伤**——因为一期 Ask 明确建立在"≥1.5× 试点复现"而非"快照 3×"之上，headline 3× 不驱动预算决定；但"≈3×"是取下位聚类（27–46 区间）算出的乐观端，pitch 时宜显式说明倍数区间随对照组选择而变，把叙事重心落在**试点设计（§3a 试点组 vs 对照组）**而非快照倍数上。
- **建议 / 替代方案（附链接）**：
  1. pitch 时把 ENG360 快照定位为"作者产出领先的客观佐证"、把 ≥1.5× 试点复现定位为"真正的立项判据"，并主动交代"次高 IC 对照下倍数约 1.3× / 中位数对照约 1.9×"，避免决策层独立发现口径落差。
  2. 建议管理层在闸门 A 裁决时一并把「二期需求侧预算认领 gate」写死进闸门 B（与 leadership reviewer 建议合流）。
  3. （可选，二期）OQ-3 敏感度补一行"时间衰减情景"（LangGraph/Temporal 补齐 human-in-the-loop 信号后重跑四维打分）。竞品定价参考 [LangGraph Platform](https://www.langchain.com/langgraph-platform)、[Temporal Cloud](https://temporal.io/cloud)、[Inngest](https://www.inngest.com/)、[n8n](https://github.com/n8n-io/n8n)。

### 4. 研发工程 Ops 与成本风险 (engineering_cost_agent) — 8.7/10（V4 8.5，+0.2，四项中分数最高）
- **改进（vs V4，兑现我 V4 的可选增强 + 补数据安全 ops 成本）**：
  - **R10 数量级初判补齐（V4 唯一"可再进一步"项，本轮解决）**：§4 R10 用与 token 账单同样的「框架乘成一个数」——每日数千级下游调用 vs SF Core/GUS（万+/日）、GitHub（5k/h）、Slack（秒级 tier），给「整体不撞硬限额、Slack 秒级速率为主要盯防点」初判，缓解仍用 R8 同框架（每类外部 API 独立令牌桶 + 熔断 + 退避，Slack 令牌桶按秒级 tier 配）。这把下游 governor limits 风险从"已登记"升级为"已量化 + 已识别主盯防点"，正是我 V4 建议 1 的对称处理。
  - **provision 路径 + 数据安全 ops 成本落地（HC-2，技术设计 §1e）**：provision 选 Falcon addon（config-as-code + IAM role + prevent_destroy），dev/单机用本地 SQLite 起步、不走 ad-hoc；并据真实 TCM RCA 明确"误删表恢复非平凡（Terraform state 失配需 Spinnaker import 重建），故重预防轻恢复"。这把此前只在风险登记里的"运维隐藏成本"具体化为有先例的工程约束，降低了立项后被隐藏成本反噬的概率。
- **遗留问题 / 风险（与 V4 同源、无回归）**：
  - **token 总量仍待试点实测校准**（并发数、步数假设）——单价已核准，总量属固有不确定性，靠闸门 B 每-WI token gate 兜底，可接受。
  - **[新增·轻] PCSK 凭据周期过期是新暴露的 ops toil 项**：路径 A 下本机长跑依赖的云凭据会定期过期，虽已归入"过期即告警、由人续期"同框架（与 R4 同类），但一期若并发多 workspace，续期打断的频次与人工 toil 量尚未量化——属实现期调参，非设计缺陷，建议试点期一并观测（与 §3a(4) 运维隐藏成本 0.2–0.5 人力口径合并跟踪）。
- **建议 / 替代方案（附链接）**：
  1. 试点期把「PCSK 凭据续期打断频次 + 人工 toil」纳入 §2c 审计轨迹一并观测，若 toil 偏高则作为二期云端 IAM Role 代持（路径 B）的优先级依据。
  2. 维持 §3a(3) prompt caching（cache read ≈0.1× 输入价、~90% 折扣）作为进一步压账单杠杆。参考 [DBOS](https://github.com/dbos-inc/dbos-transact-py)、[LangGraph checkpointer](https://github.com/langchain-ai/langgraph)、[resilience4j](https://github.com/resilience4j/resilience4j)。

## 关键建议（按优先级）

1. **[P1，非 writer 可解 · 管理层动作] 闸门 A 战略层裁决「编排层归属 / 是否与 Agentforce 重复投资」**——报告侧（§0.4 闸门 A + §5 OQ-3/OQ-5 + §2b 敏感度 + §2d 技术桥收敛）已完全就位，球纯在管理层；这是商用维度评分越过 8.5 的前提，与 leadership reviewer 判断一致。建议 kickoff 即安排 30 分钟裁决会，产出署名结论 + owner。
2. **[P1，二期 · 管理层动作] 把需求侧预算认领 gate 写入闸门 B**——§0.4 已建议、writer 无法单方钉死；管理层在闸门 A 裁决时一并明确，把商业判断从愿景钉到"有人愿掏预算"。
3. **[P3，writer 可选 · pitch 优化] ENG360「≈3×」快照口径显式化**——主动交代倍数区间随对照组变（次高 IC 对照 ≈1.3×、中位数对照 ≈1.9×、下位聚类对照 ≈3.7×），把叙事重心落在 §3a 试点组 vs 对照组的 ≥1.5× 判据上，避免决策层独立发现口径落差削弱说服力。低成本、非扣分项。
4. **[跟踪，非 writer 可解] OQ-1（合规引依赖，决定档位 1/2 与 token 账单）/ OQ-2（matrix 身份，Matrix 调研已抬升其优先级）/ OQ-5（Agentforce 平台裁决）尽快落 owner+deadline**——均已列闸门，建议 kickoff 即指派。

## 未解决 / 待 writer 回应的问题

- [ ] **[writer 可选 · pitch]** ENG360「≈3×」快照的对照口径显式化（次高 IC ≈1.3× / 中位数 ≈1.9×），叙事重心落在 ≥1.5× 试点判据——低成本增强，非扣分。
- [ ] **[非 writer 可解 · 管理层]** 闸门 A 战略层署名裁决（编排层归属 / 与 Agentforce 是否重复投资）——报告已就位，球在管理层。
- [ ] **[非 writer 可解 · 管理层 · 二期]** 需求侧预算认领 gate 写入闸门 B（writer 已建议，待管理层钉死）。
- [ ] **[固有 · 二期验证]** 商业维度定价硬数字 + 真实付费意愿 + ROI 多人复现（≥1.5×）+ FDE gate 跨多样 Org 可复现——报告主动收窄为"愿景 + 闸门 B 复现"，性质上须待二期真实测试，非当前可消解。
- [ ] **[一期主动收窄 · 已画路径待裁决]** Agentforce 技术桥一期不实现（OQ-5）、平台约束占位数字待核准——本轮未再推进（合理，非本轮焦点）。
- [ ] **[实现期 · 可选]** OQ-3 敏感度「时间衰减情景」行（writer 本轮记录不采纳、理由充分）；保留为二期商业验证时补。
