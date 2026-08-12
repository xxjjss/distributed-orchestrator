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

### 2026-08-10 — V3 评审语境补充（第二轮领导层评审）

**V3 相较 V2 的领导层可见变化（逐项对照 V2 我方 P0/P1/P2 是否闭环）**：
- **[P1 已闭环] 决策摘要卡**：§0.0 新增「30 秒决策视图」——Ask / 一期收益 / 一期成本量级 / Top-3 风险 / 决策建议 / go-no-go 门槛，一页收拢，presentation 可直接拍板。
- **[P1 已闭环] 决策建议段落**：§0.4 明写 Conditional GO + 两道闸门（闸门 A 战略裁决 + OQ-1 owner；闸门 B 四条可审计 gate）。报告从"陈述"变"建议"。
- **[P1 已闭环] 付费意愿代理指标口径化**：§2c 升级为三条**可从审计轨迹客观算出**的指标（托管深度 / 放手程度 / 决策委托范围）+ 采集方式 + 二期真实预算意向测试路径。
- **[P1 已闭环] OQ owner+deadline**：§5 补 OQ-1/2/3/4 建议 owner+deadline 表，OQ-1/OQ-3 标为闸门 A（投钱前）阻塞项，以 `[OPEN QUESTIONS]` 待管理层签署（headless 环境无法代签，处理方式正确）。
- **[P2 已闭环] 术语业务语言化**：§1 术语脚注一次性对照 affinity/CAS/lease/stateFingerprint/StateStore，降低纯业务读者摩擦。
- **[P2 已闭环] Agentforce 编排底座候选内核埋点**：§0.4「为何与战略同向」+ §2d/§3a，交付物按可被 Agentforce 复用设计——把投入在"内部工具/战略资产"两条线复用。

**V3 最大增量（回应 PR #4 两条 human review thread，直击领导层"抓人"维度）**：
- §0.2.1「一期实战一览」嵌入 **4 张真实原型截图**（sticky-note 人机界面 / 双击激活 WI-worker / job-scheduler 带登录态 / watch-pr 信号采集）+ 真实 WI `W-23433231` + **WI 端到端推进示意图**。这把"3× 个人信号"的机制从抽象论证变成**可见的、每天在跑的证据**——对领导层说服力是实打实的提升，也正对"用真实原型打动决策层"的诉求。两条 human thread 均由 writer 标记 Resolved in V3。

**V3 后仍悬空的唯一战略硬门槛（评分天花板所在）**：
- **build-vs-leverage / 编排层归属裁决（OQ-3，闸门 A 阻塞项）**——报告 §2b 已做敏感度分析（倾向内嵌基本稳健，唯"必须保独立议价权"能翻盘）+ §2d 技术桥，但这仍是**作者论证，非战略层署名裁决**。此项**按设计无法在文档内解决**（需管理层在 kickoff 签名），故报告能做的都做了；它压住评分上限的性质从"报告缺失"转为"外部依赖待管理层动作"。
- **ROI 仍是 n=1**：3× 已诚实降级为 ≥1.5× 试点判据，"团队可复现"须一期试点跑出（闸门 B），当前无法在文档层消解。

**V3 评分判断**：V2=7.2。V3 把 V2 全部 P1/P2 闭环 + 加入强说服力的真实原型证据，战略叙事的"可信度与可见度"实质提升；但两处硬伤（build-vs-leverage 未获战略层背书、ROI 未复现）按设计均须文档外动作解决，仍压住 8 分上限。给 **7.8/10**（战略 7.8 / 文档 7.7）。

---

## V4 评审沉淀（2026-08-11，distributed-orchestrator PR #4 commit 7e52e7d）

**本轮总评分 8.0/10（战略 7.9 + 文档 8.0，等权），Conditional GO 维持。**

- **报告侧已基本封顶**：V3 我方三条 P2（证据前置 / presentation 抽取版 / Changelog 分离）中，证据前置已彻底解决——`v4-sticky-note-overview.png` 上提到 §0.0 决策卡开篇，且该屏自含本报告评审进度（"系统在管理它自己的评审流水"，强证据）。presentation 抽取版 writer 合理 deferred（倾向独立文件），非扣分硬项。
- **加分项**：痛点鱼骨图（5 PP → 单一根因"人的在场成瓶颈"→ 研发效率低下）、§0.2.1 落地后开发流程流水、Opus 单价订正 5×→1.67×（月账单收窄 $1k 内）、ECS/Fargate 应急退路 +2–4 人周入表（matrix 依赖下行兜住）。
- **天花板不变**：闸门 A 战略层裁决（编排层归属 / 与 Agentforce 是否重复投资）仍只有作者技术论证（§2b 敏感度 + §2d 技术桥收敛 + 新增 OQ-5），无管理层署名——这是 conditional→full GO 唯一硬门槛，非 writer 可解，评分过 8.0 的前提。
- **给二期的新要点**：闸门 B 4 条 gate 全供给侧，须补一条需求侧 gate（真实部门预算认领意向测试）——V4 §2b 已诚实点名此缺口。
- **打分演进**：V2 7.2 → V3 7.8 → V4 8.0。上限由"文档外管理层动作"封住，写作侧收益递减已明显。

### 2026-08-12 — V5 战略语境采集（Slack 授权本轮可用，V2–V4 缺口补齐）

**首次拿到 Agentforce 编排 roadmap 内部实据（Slack search，直接作用于 build-vs-leverage / 闸门 A）：**
- **Agentforce Multi-Agent Orchestration 已 GA（Summer '26）**：super-agent 架构 + Atlas Reasoning Engine，primary agent 意图路由到 best-fit sub-agent，"context travels with the conversation"。**关键边界：SOMA = Single-Org Multi-Agent，是会话内/单 org 的 agent-to-agent 路由，不是跨天 durable 长跑执行层。** → 对本项目"托管≠编排、Agentforce 造 agent、本项目让 agent 7×24 可靠长跑"的互补论证是**外部产品边界背书**（互补从断言变为有据）。
- **"multi-org multi-agent orchestration efforts currently paused; third-party agent integration remains the primary strategic priority"**（FDE 技术 deep-dive，PM 口径 Pragya Anand）：本项目"编排任意 AI agent/skill/脚本"与"第三方 agent 集成为头号优先"**同向**（正向对齐信号）。
- **风险面**：内部 "orchestration" 品牌下在跑的团队极多（SOMA/Super Agents、Agentic Selling Orchestration Council、多个 DEX squad 的 MCP/Slackbot/Agentforce orchestration discovery，2026-08 多个新 channel 刚 kickoff）。landscape 拥挤 → **抬升闸门 A 署名裁决的紧迫性**：越晚裁越易被视为重复投资。
- **净判断**：Slack 语境**降低**了 build-vs-leverage 的"技术差异化"风险（SOMA≠durable 运行时），但**抬升**了其"组织资源/归属"紧迫性 → 闸门 A 须尽快做，且现在有更清晰的差异化话术支撑那次裁决。

## V5 评审沉淀（2026-08-12，distributed-orchestrator PR #4 commit ba09142）

**本轮总评分 8.1/10（战略 8.1 + 文档 8.1，等权），Conditional GO 维持。**

- **微升 +0.1 的理由（非排版打磨）**：§0.3(0) 把立项核心论据"≈3×"从口头自述**锚定到公司可核验的 ENG360 Developer Productivity 仪表盘**（作者 EO=105.07 全表第 1，第 2 名 87.96，倍数 2–3.7×，诚实标注仍 n=1）——在一个此前未使用的维度上加了客观证据，实质降低"ROI 是否真实"疑虑。叠加两条 writer 可解 P1 全部闭环（M1 埋点即验收、需求侧 gate 建议写入闸门 B），给 +0.1。
- **writer 可解项已全部闭环**：M1「埋点即验收」写死为验收项（§2c + §3a M1 行）；需求侧 gate 建议写入闸门 B（§0.4）；FDE 可审计 gate（§2c，采纳 product V4）；R10 数量级初判（§4）；3 条剩余 human comment 全部 resolve（ENG360 落主报告，DynamoDB 鉴权 + Matrix 调研落技术设计）。
- **天花板不变（~8.5）**：闸门 A 战略署名裁决（编排层归属 / 与 Agentforce/SOMA 是否重复投资）+ ROI 多人复现（闸门 B ≥1.5×），两件文档外动作。本轮 Slack 语境为"技术差异化"半边补了外部证据，但"资源/归属"半边仍须管理层动作。
- **文档侧唯一残留（非扣分硬项）**：presentation 抽取版仍 deferred；随 Changelog 四版叠加，建议从"无限期 defer"提为"kickoff 后尽快"。
- **打分演进**：V2 7.2 → V3 7.8 → V4 8.0 → V5 8.1。上限仍由文档外管理层动作封住。
