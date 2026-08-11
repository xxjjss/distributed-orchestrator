# 分布式 AI Agent 编排系统 — 项目可行性报告

> 本文是**项目可行性报告**，覆盖现状、痛点、分期、要实现的功能、带来的益处与未来前景，
> 主要面向**产品审核与公司领导层**。与之配套的**技术设计文档**（系统结构、各部分功能的
> 选型与实现，面向技术审核人）见 [`distributed-orchestrator-tech-design.md`](./distributed-orchestrator-tech-design.md)。
> 两文交叉引用、内容互补：本文谈「为什么做、做成什么、值不值得」，技术设计文档谈「怎么做」。

---

## 0. 执行摘要（Executive Summary）

### 0.0 决策摘要卡（30 秒决策视图，回应 leadership reviewer P1）

> **一句话开篇（可量化收益 vs 开发投入，回应 human comment）**：用 **≈11–24 人周（1 季度 · 至少 2 名工程师）+ 几十至低几百美元/月云资源 + ≈$0.1–1k/月 token** 的投入，验证「把作者本人的 **≈3× 个人产出**规模化为**团队可复现的 WI 吞吐 ≥1.5×**」——这是一笔"用一个季度买'要不要加码'信息"的低风险战略期权。
>
> 一页看清 **Ask → 预期收益 → Top 风险 → go/no-go 建议 + 门槛**。细节见对应小节。
>
> **证据先行（回应 leadership reviewer V3 P2）**：本项目不是概念——作者**今天已在跑**这套原型（下方一屏截图，详见 §0.3）。决策层可先看"已在跑的东西"，再读规模化假设。
>
> ![原型总览：sticky-note 一屏驱动多 WI + 双击激活 agent](diagrams/v4-sticky-note-overview.png)
>
> *（作者本机实拍：sticky-note 面板按 IN PROGRESS / DONE / TODO 分组呈现真实 GUS WI，🤖 标记 AI 正在驱动的 WI；双击一个 WI 即弹出"选择 agent 运行"；底部 NON-WI TASKS 承接 AI 回叫提醒——甚至包含本报告自身的评审进度 `distributed-orchestrator V3 score 8.3/7.6/7.8` 与一条 PR review 提醒。这一屏就是一期"人只做决定/审查/签收、AI 做工作"的落地形态。）*

| 项 | 内容 |
|---|---|
| **要什么（Ask）** | **1 个季度 · 至少 2 名工程师 · 复用作者已有原型 · 依赖外部 `matrix` 托管**（未就绪可回退本机 worker）。只批"内部研发效率试点"，不批"商业产品"。 |
| **一期预期收益** | 把作者本人的「≈3× 个人产出」信号，验证为**团队可复现的 WI 吞吐 ≥1.5×**（Engineer360 对照口径）；沉淀可被 FDE 与 Agentforce 复用的编排内核。 |
| **一期成本量级** | 人力 ≈ **11–24 人周**（档位取决于 OQ-1）+ matrix 延期应急 **+2–4 人周**；云资源 **几十至低几百美元/月**（含护栏共享写增量 <$1）；**LLM Token ≈ $90–450/月（Sonnet 主力）**，Opus 档 **≈$150–750/月**（按已核准定价 Opus:Sonnet ≈1.67× 单价，§3a），保守上界约 $1–2k/月由硬护栏封住。 |
| **Top-3 风险** | ① 与 Agentforce/Platform 编排能力**重复投资**（须战略层裁决）；② `matrix` 依赖排期（有本机 worker 退路）；③ ROI 仍是 n=1，团队复现未发生。 |
| **决策建议** | **条件性 GO（Conditional GO）**——见 §0.4。低风险的战略期权：小注押注与公司头号战略（Agentforce 数字劳动力）同向的能力，用一个季度买"要不要加码"的信息。 |
| **go/no-go 门槛** | **闸门 A（投钱前）**：战略层对"编排层归属/非重复投资"署名裁决（OQ-3）+ 指派 OQ-1 owner。**闸门 B（二期前）**：一期试点跑出 §0.4 的 4 条 gate。 |

**一句话定位**：我们要造的不是又一个 AI agent，而是让**任何 AI agent / skill / 脚本能够 7×24 无人值守、幂等、断点续跑、并被统一编排**的「分布式操作系统层」——先在公司内部把工程师的研发效率规模化，再沿清晰的产品化路径走向商用。

**分期主线（一句话记住我们的节奏）**：**一期推工具，二期推环境，长期推产品**（回应 human comment）。
- **一期 = 推工具**：面向公司内部工程师，交付一个能把「WI 全自动推进」规模化的编排器工具，先自证价值。
- **二期 = 推环境**：把编排内核沉淀为 SDK + 统一消息/事件环境，让公司内其他团队与其他工作流低门槛接入，并与 SF 产品线（Slack/Tableau/MuleSoft/Agentforce）耦合。
- **长期 = 推产品**：模版 + 图形化编排 + 封装的持久化/消息/鉴权，包装为可商用的编排产品，走向 FDE 与终端客户。

### 0.1 为什么是现在（Why — 从现状痛点 Pain Point 归纳）

> 以下痛点（Pain Point，简称 **PP**，回应 human comment：`P` 易被误读为 priority）由「设计思路」归纳、整理、润色后在此复述，作为立项的 **why**。人类评审员在 presentation 时**只读本文**、不读设计思路（回应 human comment）。

公司已把 Claude Code / opencode 铺成开发平台，工程师已自发写出大量 skill / agent / workflow。但这些工具的价值被一连串结构性痛点锁死。**每条痛点都给出可量化的效率损耗口径（回应 human comment）**：

| # | 现状痛点（Pain Point） | 量化的效率损耗 | 后果 | 谁来解 |
|---|---|---|---|---|
| **PP1 无处托管** | 没有一个可 7×24 不停机运行的 AI 工具箱/托管平台 | AI 工具只能在开发者本机、有人盯着时才跑 → **一天里约 ⅔ 的时间窗口（夜间/周末/会议）工具闲置**，长任务无法跨夜推进 | AI 工具的可用时间被"人在工位"封顶 | `matrix`（falcon 上的公司内部托管平台）解决「在哪跑」——**外部项目，非本项目交付** |
| **PP2 自动化程度低、非幂等** | 现有 AI 过程大多半自动、状态不保证幂等、重入需人工介入；要做到幂等缺状态持久化机制，**开发门槛高** | 工作流断一次≈**从头重来（数十分钟–数小时白跑 + 重复烧 token）**；每个开发者自造持久化轮子≈**数天/人的重复投入** | 断了要人接管、从头重来；重复造轮子 | **本项目**：状态持久化 + 幂等状态机 + 最小 SDK |
| **PP3 缺友好的人机消息平台** | 仍主要依赖 Claude Code/opencode 的 CLI；**命令行交互对非专业用户上手门槛高、可用性差**；多 session 难跟踪、难管理 | 并行任务数**受限于"人能同时盯几个 CLI 窗口"（现实≈1–2 个）**——想并行更多，人先被界面淹没 | 非专业用户被挡在门外；并行度被人的注意力封顶 | **本项目**：面向工作流的 UI + 通知/审批闭环（sticky-note 起步） |
| **PP4 无法自动重跑** | 关机/断网/网络抖动会打断本地 AI 工作流，**不得不从头运行**；「写码-提交-review-修订-测试-回归」这类长工作流要数小时，**不能关机、需频繁手工保状态** | 一条长链路**要求人"全程在场数小时"**——在场时间本身就是被浪费的机会成本 | 长工作流的时间成本被「人必须全程在场」放大 | **本项目**：中断容错（断点续跑）+ 云端单一事实源 |
| **PP5 学习/使用成本高** | 即便资深工程师，用 AI 自动化日常工作、提效都是高学习成本的痛点；对 Salesforce 终端用户更是「说起来容易、却没有可用工具」——导致 **AI 在终端用户手中基本仍等同于 chatbot** | 提效红利**集中在极少数会「攒工具链」的人**（如作者）手里——**大多数工程师复现不了那套链路**，团队层面提效无法规模化 | 提效红利无法规模化、无法复现 | 一期降门槛（installer + UI）、远期图形化编排让终端用户可编排 |

**PP 与"阻碍效率"的关系（鱼骨图，回应 human comment）**：五条痛点看似分散，其实指向**同一个根因——「人的在场/介入被迫成为工作流吞吐的瓶颈」**：PP1/PP4 把人钉在"必须在场"，PP2 把人拖进"断了重来的返工"，PP3 把并行度压到"人能盯的窗口数"，PP5 让这套能力无法被复制。合起来的效应就是研发效率低下、AI 工具价值被锁死（只有极少数人达到 ≈3×）。

![痛点鱼骨图：五条 PP 如何共同压低研发效率](diagrams/v4-painpoint-fishbone.png)

> 源文件：`diagrams/v4-painpoint-fishbone.mmd`。读法：五条 PP（鱼骨支）→ 共同根因「人的在场/介入成为吞吐瓶颈」（脊柱）→ 效应「研发效率低下」（鱼头）。**本项目一期正是从根因下手：把"人必须在场"替换为"人只在关键点介入"**——见下 §0.2 解决方案。

**关键洞察**：`matrix` 解决了 PP1「在哪跑」，但**没解决 PP2 跑不稳/不幂等、PP3 触达不到人、PP4 断了续不上、PP5 门槛高**——后四条正是本项目的空位。**托管 ≠ 编排。**

### 0.2 一期解决方案（针对 PP 的对症交付，回应 human comment）

> 紧接痛点给出**一期 solution**——每条都对应上表的 PP，讲清"这条痛点怎么被消解"。技术实现见 §3a 与技术设计文档。

**一期交付（本报告核心，见 §3a）**：面向**公司内部工程师**，交付一个能把「WI 全自动推进」规模化的编排器 + 一个**本机简易 installer**（一键装依赖、引导配置，降 PP5 门槛）。**人类只做决定、审查与验收（承担责任），AI 做工作。** 逐条对症：

| 痛点 | 一期解决方案 | 效率如何被找回 |
|---|---|---|
| **PP1 无处托管** | affinity 模型统一调度本机/云端 worker；云端 worker 跑在 `matrix`（外部依赖），用户可关机 | 工具从"人在工位才跑"变为"7×24 可跑"，夜间/周末窗口不再闲置 |
| **PP2 非幂等/返工** | 云端单一事实源的**状态持久化 + 幂等状态机 + 步骤级 memoization**；最小 SDK 内核 | 断了从最后 checkpoint 续跑、**不重复烧 token**；开发者不再各造持久化轮子 |
| **PP3 界面不友好** | 面向工作流的 **sticky-note UI** + 通知/审批闭环——把 CLI 挡在用户之外 | 并行度不再受"能盯几个 CLI"限制，一屏看清多个 workspace |
| **PP4 无法自动重跑** | **中断容错（断点续跑）** + 边缘触发的信号采集层（watcher/signal）+ 到点回叫 | 人不必全程在场；关机后云端继续，到"该你做决定"时才被叫回 |
| **PP5 门槛高/不可复现** | **installer 降安装门槛** + SDK 内核降开发门槛 + UI 降使用门槛 | 把"作者一人能用"的链路，变成"团队多人一键可复现" |

**边界诚实**（详见技术设计文档各决策）：
- 云端 7×24 托管依赖 `matrix`/`falcon`——**外部依赖，非本项目自有交付**（技术设计 D3；风险 R1；OQ-4）。
- 一期不自建鉴权，复用 MCP adaptor 的机器本地登录态，以**开发者本人身份**调外部系统——因此一期主力是 `affinity=machine` 的**本机 worker**，「无头」的前提是「连接已认证未过期」（技术设计 D2）。
- 「断网」刻意收窄为**中断容错（关机/重启/抖动后自动续跑）**，不承诺**断网执行**（技术设计 D1）。

#### 0.2.1 一期实现后的开发流程 = 效率如何被提高（回应 human comment）

> 紧接解决方案，把"一期落地后一个工程师的一天"讲成一条流水，直观体现效率提升——对照上面 PP 的"人必须在场"，看人被从哪些环节里解放出来。

**一期落地后的 WI 推进流程（人只在 3 个关键点介入）**：

1. 工程师在 sticky-note 选若干 WI → 一键激活各自的 worker（**并行拉起多个**，不受 CLI 窗口数限制 → 解 PP3）；
2. 编排器全自动推进每个 WI：研究 → 写码 → 提 PR → 等 review → 修订 → 测试 → 回归（**云端/本机续跑，工程师可关机去做别的/下班** → 解 PP1/PP4）；
3. 任一 WI 到「**需要人做决定 / 审查 / 签收**」时，通过 sticky-note 通知 + Slack 推送回叫工程师（**只在关键点被打断，不必全程盯着**）；
4. 工程师处理完该决策点，编排器**从断点继续**（崩溃/关机不从头重来、不重复烧 token → 解 PP2）；
5. 一个工程师因此可**同时推进多个 WI**——他的时间只花在 **make decision / review / sign-off** 上，其余交给编排器。

**效率提升的机制**：把工程师从"PP1/PP4 的全程在场""PP2 的返工""PP3 的单窗口串行"里解放出来，其单位时间能覆盖的 WI 数从"能盯几个"跃升为"能决策几个"——这正是作者本人 ≈3× 个人信号的机制来源，也是一期要**规模化验证为团队 ≥1.5×** 的东西（度量见 §2c/§3a）。

**我们要的（Ask）**：一期以现有工程师小队（**至少 2 名工程师 + 作者已有原型**，回应 human comment：至少两人以便互相纠错、代码合并的审核与批准）+ `matrix` 依赖为前提，用 **1 个季度左右**把「≈3× 个人信号」验证为「多人可复现的团队效率提升」，并沉淀出可被 FDE 带向客户、可被 Salesforce 产品线复用的编排内核。成本量化见 §3a。

### 0.3 原型实例（须诚实标注 n=1，见 §2c 与技术设计 D5）

> 由 human comment，"早期信号"更名为**原型实例**，并置于解决方案之后——因为它是"上面这套方案作者已经跑起来了"的**实证**，而非立项前的推测。以下截图与实例均来自作者**已在跑的原型**（不是概念图，是每天在用的东西）。

作者本人用自建的一套原型工具（wi-researcher/wi-worker 自动化 + sticky-note 人机界面 + WI-chatter 状态持久化 + PR/Slack/GUS 监听 + 本机带登录态的 job scheduler），已能**同时并行推进 4–5 个 WI、全程无需在 CLI 内交互**，Engineer360 口径下产出约为团队他人的 **≈3×**。这是 **n=1、作者本人、归因未隔离、代理指标（WI 数 + 代码量）**的早期个人信号，**不是产品级结论**——本报告据此提出**可规模化验证的试点假设 + 度量方案**（§2c、§3a），把它当立项理由而非既成事实。

**（1）人机界面 = sticky-note：一屏看清 + 一键驱动**（总览见 §0.0 开篇的整体截图）

![sticky-note 人机界面](diagrams/v3-sticky-note.png)

sticky-note 面板把 GUS WI 按 **In Progress / Done / Todo** 分组呈现，它同时是**驱动 WI 的入口**——双击一个 WI 即弹出"选择 agent 运行"（下图），激活 WI-worker。底部 **NON-WI TASKS** 既可用户自定义待办，也承接 **AI 的回叫提示**（如"PR review … has 0/1 comments"，提醒该你去做决定/审查）。这正是 §3a 用户旅程的落地形态。

![sticky-note 双击激活 WI-worker](diagrams/v3-sticky-note-invoke.png)

**（2）一个 WI 从头到尾的自动推进（真实实例）**

真实实例：GUS `W-23433231`（[WI 链接](https://gus.lightning.force.com/lightning/r/ADM_Work__c/a07EE00002edkFOYAY/view)）。从该 WI 的 **chatter**（此处临时把 chatter 当作状态持久化的介质）可以看出：WI 由 **WI-worker 驱动**并分发给 **tcm-automated-sdd** 执行；每个阶段的 AI 产出可见、提交 PR、**人机通过 PR 交互**、merge 后**自动推进到下一步**，直到最后完成。**在第 6–7 步（提 PR → 等 review）之间，还有一则信息推送到 Slack channel、并提醒作者本人去做 PR 人工 review**（回应 human comment）——这正是"到点叫人"的回叫在真实链路里的样子。下图把这条链路的组件与交互画成端到端示意：

![WI 端到端推进示意图](diagrams/v3-wi-end-to-end.png)

> 图中组件：**WI-worker**（驱动者）、**tcm-automated-sdd**（developer）、**pr-gate**（状态机桥梁 / 人类反馈、检查、签收点）、**WI-chatter**（状态持久化媒介）、**watch-pr**（信号采集者）、**job-scheduler**（驱动状态采集，见下）、**Git PR / CI-CD / GUS**（外部信号源）。
> **关键效益**：因为人类通过人机界面**及时知道需要进行的操作**，一个人可以**同时处理多个 WI**——只需做 **make decision / review / sign-off** 三件事，其余交给编排器。这就是"≈3× 个人信号"的机制来源，也是一期要规模化验证的东西。

**（3）状态采集的驱动器 = 带登录态的 job-scheduler（不同于 crontab）**

![job-scheduler list](diagrams/v3-job-scheduler.png)

`job-scheduler` 是一个**带 login session** 的作业调度器（区别于无登录态的 crontab）——正因带登录态，它定时驱动的回调才能直接跑 `claude -p` / `watch-pr`。图中每个 `wp-*` 条目就是一个被定时驱动的 watch-pr 采集任务。

**（4）信号采集者 = watch-pr（边缘触发 + 回调驱动状态机）**

![watch-pr list](diagrams/v3-watch-pr.png)

`watch-pr --list` 显示每个被监听 PR 的 `watch-items`（`approved / merged / new-comment / pipeline-failed …`）、`state`（如 `MERGED review=APPROVED pipeline=SUCCESS`）与 `callback`。当 PR 状态**跃迁**（如 merged/approved），watch-pr 触发 callback——正是这条 callback 把 `tcm-automated-sdd` 推进到下一 Stage 或让 `pr-gate` 继续驱动评审。这就是技术设计 §1b「Watcher 五要素契约」与 `signal()` 回调在现实中的样子。

> **给决策层的落点**：上面四张图分别对应本项目一期的四层——**人机界面（sticky-note）/ 驱动者（WI-worker/SDD）/ 采集驱动（job-scheduler）/ 信号采集（watch-pr）**。一期要做的，就是把这套"作者本人能用"的原型，**沉淀为状态持久化幂等、多人可复现、可被 FDE 与 Agentforce 复用**的编排器（§3a）。

### 0.4 决策建议（Go / No-Go，回应 leadership reviewer P1）

> 这是一份**给领导层做决定**的材料，故此处主动给出建议，而非把结论留给读者推断。

**建议：条件性 GO（Conditional GO）** —— 批准以「1 季度 / 1–2 名工程师 + 已有原型」的**内部研发效率试点**小额投入立项；设两道闸门：

- **闸门 A（投钱前，阻塞）**：完成一次**战略层裁决**——「编排层归属 / 是否与 Agentforce/Platform 重复投资」（OQ-3 升级），产出**署名结论 + owner**；并指派 **OQ-1 owner**（能否引 MIT LangGraph/DBOS）。二者产出前只批"探索性设计"，不批工程投入。
- **闸门 B（二期加码前，阻塞）**：一期试点跑出以下 **4 条可审计 gate**，达标才解锁二期（推环境 / SF 耦合）投入；不达标则停在内部工具、不投商业化：
  1. **WI 吞吐 ≥1.5×**（Engineer360 对照口径，试点组 vs 对照组，可统计显著）；
  2. **人工介入率**随迭代**下降**；
  3. **每-WI token 成本**达到设定上限内（不失控烧钱，§3a）；
  4. **使用强度/信任代理指标为正**（§2c 给出具体口径；付费意愿本身留二期真实预算认领测试）。

**理由**：一期投入极小、与公司头号战略（Agentforce 数字劳动力叙事）强对齐、退路清晰（matrix 未就绪回退本机 worker）、团队诚实（3× 已降级为 ≥1.5× 试点判据）——值得给机会（GO）；但**重复投资顾虑未被战略层背书 + ROI 未在多人复现**，决定了现在只能为"内部工具试点"买单、不能为"商业产品"买单（Conditional）。

**为何与公司战略同向（给战略层的一句话）**：本项目要做的「让任意 AI agent 7×24 可靠长跑、断点续跑、被统一编排、到点叫人审批」，正是 [Agentforce](https://www.salesforce.com/agentforce/)「数字劳动力」叙事所缺的**运行时 / 编排运维层**——一期交付物按「可被 Agentforce 复用的编排底座候选内核」设计（§2d、§3a），让这笔投入在"内部工具"与"战略资产"两条线复用。「编排底座候选内核」的技术边界与接口草图见 [技术设计文档](./distributed-orchestrator-tech-design.md)（§2.4 异构 runtime adapter、§3 AgentforceActionAdapter 契约）及本文 §2d「Agentforce/Platform 技术桥」。

---

## 1. 一期系统概览（详见技术设计文档）

一期系统分五层：UI 层、编排层（**本项目核心交付**）、Worker 层、数据层、外部系统。核心命题是「**workflow 引擎是唯一懂进度的组件，worker 是可被随时拉起的纯函数**」——这条约束是幂等与断点续跑得以成立的支点。

> **术语脚注（业务语言，回应 leadership reviewer P2）**：本报告尽量用业务语言，个别技术术语一次性对照如下，细节全部下沉到技术设计文档，纯业务读者可跳过——**affinity** = 任务的"本机 / 云端运行位置"；**CAS / lease** = "抢占式加锁"，保证同一任务同一时刻只有一个执行者；**stateFingerprint** = "版本指纹校验"，代码/流程变了就显式失败而非悄悄跑错；**StateStore** = "状态持久化存储"。

![一期架构图](diagrams/v2-architecture.png)

> 完整的架构图/时序图/组件职责、DynamoDB 元数据结构、选型调研、机制正确性（熔断/去重/liveness/runtime adapter）、与 Salesforce 既有编排原语的关系、可外带 IP 内核边界，均见
> [**技术设计文档**](./distributed-orchestrator-tech-design.md)。本报告不重复技术细节，只在需要时引用其小节。

**给产品/领导层的一句话技术定位**：本项目 = 「**Platform 外的、LLM-native 的 durable agent 运行时 + 人机闭环**」。它与 Salesforce 既有的 Flow Orchestrator / Agentforce **互补而非竞争**——Flow Orchestrator 编排 Platform 内的业务流程、Agentforce 负责「造 agent」，本项目负责「让任意 agent 可靠地 7×24 长跑并被编排」（详见技术设计 §3、§2.4）。

---

## 2. 优势、可行性与公司效益

### 2a. 竞品对比：我们的优势与改进点

**市场上确有相邻产品，但没有一个同时覆盖「LLM-native + 本机/云端统一 + 消息驱动人机闭环 + 面向非专业用户的编排」这四条。** 我们的差异化正在这个交集。

| 类别 | 代表 | 它做什么 | 缺口 / 我们的改进点 |
|---|---|---|---|
| **Durable execution 框架** | Temporal / DBOS / Restate / Inngest | 通用持久化执行、故障恢复 | 非 LLM-native；无人机交互闭环；面向工程师写代码，不面向「驱动一个 agent 工作流」的终端体验 |
| **LLM agent 编排** | LangGraph / LlamaIndex Workflows / CrewAI / AutoGen | 多 agent 图/协作 | 单机/单进程为主；**无内置并发锁与显式状态持久化**（LangGraph 官方承认）；无本机/云端统一调度；无脱机断点续跑的运维层 |
| **通用工作流编排** | Airflow / Prefect / Dagster / n8n | DAG 调度、数据管道、图形化编排 | 非 LLM 语义；面向数据工程师；无 agent 自主 route / spawn；无人机审批闭环 |
| **AI agent 托管平台** | LangGraph Platform / OpenAI Assistants / Vertex Agent Engine | 云端托管 agent 运行时 | 托管≠编排：不解决「多任务、断点续跑、跨本机/云端统一事实源、信号驱动人机回叫」；且多为外部云、公司合规受限 |
| **公司内部（现状）** | matrix/falcon + Claude Code + 自发 skill/agent | 托管 + 开发平台 + 零散工具 | **正是我们要填的空位**：有托管、有工具，但**无编排层**（幂等/续跑/多任务/信号/人机闭环），价值被「人必须盯着」锁死 |

**我们的四条护城河（改进点）**：
1. **LLM-native 的显式状态机**：显式 `progress` + `substate` + `stateFingerprint` 非确定性检测，比 LangGraph「靠 pending write 推断状态」可排查、可被外部工具消费。
2. **本机/云端统一事实源（affinity 模型）**：同一 StateStore 接口、同一 lease+CAS，本机 worker 与云端 worker 同表调度——竞品要么纯单机、要么纯云端。
3. **信号驱动的人机闭环**：Watcher 边缘触发 → `signal()` 唤醒 → 回叫通知 UI。这是「用户关机断网、工作流仍推进、到点叫人审批」的完整闭环，竞品普遍缺 UI/通知这一端。
4. **面向「驱动工作流」而非「写代码」的体验**：从 sticky-note 起步，把高门槛的 CLI 交互挡在用户之外——这是走向 FDE / 终端用户的产品化起点。

**诚实的时间窗口风险**：durable execution + LLM agent orchestration 赛道正快速收敛——LangGraph Platform、Temporal（signals + human-in-the-loop）、Inngest 正补齐「LLM-native 显式状态 + 信号人机闭环」。四条护城河里，**「本机/云端统一事实源」是最真实的差异点**，其余三条有被时间蚕食的风险。这也是我们主张**内嵌 Agentforce/借 SF 分发与身份**（而非在开源红海里正面拼框架）的核心理由（见 §2b、OQ-3）。

### 2b. 商业前景：能否包装为独立产品

**能，但要分阶段、诚实定位。** 商业化的产品形态不是「又一个 agent 框架」（那个赛道已拥挤且多为 MIT 开源），而是 **「让企业把已有 AI 工具变成 7×24 可靠数字员工」的编排 + 运维 + 人机闭环平台**——护城河在运维可靠性、企业身份/合规、以及非专业用户的编排体验，而非算法。

- **内部产品（一期，确定）**：面向 Salesforce 工程师的研发效率平台，先自证价值。
- **平台/SDK（二期，高潜）**：`工作流模版.md` 的 handler 契约 + 状态存储 + 消息层封装成 SDK，让公司内其他团队低门槛接入——这是「内部平台产品」的形态。
- **商用 SaaS（远期，愿景）**：模版 + 图形化界面 + 封装的持久化/消息/鉴权，降低企业客户「用已有 worker 组装自己工作流」的门槛。

> **说明（回应 product reviewer「需求未验证」+ human comment）**：一期我们**不承诺已验证的商用需求**——一期专注于**给公司内部带来的收益**，商业化只作为**愿景与可能性探讨**提出，并在一期埋下「付费意愿代理指标」（§2c）为二期的商用判断积累先行信号。这样既不夸大、也不放弃对前景的探讨。

#### OQ-3 的二维打分（独立 SaaS vs 内嵌 Agentforce，回应 product reviewer P1）

商业化路径不再只写「倾向后者」，而是用四个维度打分（1–5，越高越有利）：

| 维度 | 独立 SaaS | 内嵌 Agentforce/Platform | 说明 |
|---|---|---|---|
| **TAM（市场规模）** | 4 | 3 | 独立 SaaS 面向全市场；内嵌受 SF 客户群封顶 |
| **壁垒（护城河）** | 2 | 4 | 独立要正面对抗开源红海；内嵌借 SF 身份/合规/数据形成壁垒 |
| **分发（Go-to-market）** | 2 | 5 | 独立要从零获客；内嵌借 SF 既有分发与销售通道 |
| **议价权/独立性** | 4 | 2 | 独立自主定价；内嵌高度绑定 SF 产品战略、议价权被削弱 |
| **加权倾向（等权合计）** | **12** | **14** | **倾向内嵌**，但代价是议价权与独立性——两面性须向战略层讲透 |

**结论**：**倾向内嵌 Agentforce/Platform**（借分发与身份、避开红海），但明确其代价（独立商业价值与议价权被削弱）。此决策影响远期架构（鉴权、多租户），需产品/战略层拍板——列为 OQ-3。

**权重敏感度分析（回应 product reviewer P2：等权且分差小，结论是否稳健）**：等权下 12 vs 14（内嵌胜出但仅 2 分差）。测两种极端加权，看结论是否翻转：

| 加权情形 | 独立 SaaS | 内嵌 Agentforce | 谁胜 |
|---|---|---|---|
| 等权（基线） | 12 | 14 | 内嵌 |
| **「分发」双权重**（GTM 决定生死） | 14 | 19 | **内嵌（差距扩大到 5）** |
| **「议价权/独立性」双权重**（战略自主优先） | 16 | 16 | **打平** |
| **「壁垒」双权重**（红海生存） | 14 | 18 | 内嵌 |

**稳健性结论**：只有当战略层把「议价权/独立性」提到双倍权重时结论才收敛为**打平**，其余加权下**内嵌均胜出**——即"倾向内嵌"对权重扰动**基本稳健**，唯一能翻盘的诉求是"必须保住独立议价权/自主定价"。这恰好把 OQ-3 的裁决焦点收窄为一个战略问题：**公司是否愿意为独立商业议价权，放弃 SF 分发与壁垒的红利？** 供战略层拍板。

#### 定价锚点与假设买方画像（回应 product reviewer V3 P2：定价真空 + 无买方画像）

> OQ-3 的 build-vs-embed 此前是在**定价真空**里做的。这里补方向性锚点，证明"定价逻辑被考虑过、非跳过"——不给硬数字（商用为远期愿景），只定位相邻赛道的计费轴与我们的落点。

**相邻赛道公开计费轴（作定价锚点）**：

| 相邻产品 | 计费模型 | 对我们的定价含义 |
|---|---|---|
| **Temporal Cloud** | consumption（按 action/存储计量） | durable-execution 按量计费已被市场接受——我们的 per-workflow/per-step 计量天然对齐 |
| **LangGraph Platform** | 分层订阅 + 按 node execution 计量 | LLM 编排的 per-execution 计费有先例 |
| **Inngest** | 免费档 + 按 step/事件量阶梯 | step-based 计量对"步骤级 memoization"是自然计价单位 |
| **n8n** | 自托管开源（$0 地板价）+ 云端 seat/execution 订阅 | **存在 $0 开源替代 → 独立 SaaS 定价天花板被压低**，强化"内嵌借 SF 分发/身份"而非正面卖框架的结论 |

**我们的假设定价落点**：若**内嵌 Agentforce**（倾向），最可能作为 **Agentforce 编排能力的 consumption 计量项**（per-workflow-run 或按 durable step，与 Temporal/Inngest 计量轴一致），随 Agentforce SKU 打包分发，而非独立 per-seat 订阅——既避开 n8n 的 $0 地板价正面竞争，又借 SF 既有计费关系。独立 SaaS 路径则须直面上述开源/低价替代，是定价上另一个不利于"独立"的信号。

**假设的目标买方画像（给闸门 B 一个需求侧对照）**：早期买方 ≈ **「已部署 Agentforce、且拥有 AI-ops / 可靠性预算线的平台工程或研发效能负责人」**（非一线开发者、非 CIO 直采）——他要的是"让已买的 agent 能可靠长跑、被编排、到点叫人"，预算来自"可靠性/运维"而非"新增 AI 工具"。当前闸门 B 的 4 条 gate 全是供给侧（吞吐/介入率/token/内部信任代理）；二期须补一条**需求侧 gate**：该买方画像下的部门，是否愿在真实预算认领测试中为此付费（§2c 升级路径）。

### 2c. 落地与反馈闭环：从内部起步 + 与 FDE 结合

**获取真实需求与反馈的路径（务实、低成本）**：
1. **Dogfooding 优先**：一期先服务本团队工程师的 WI 处理——需求方 = 使用方 = 反馈方，闭环最短。
2. **可核验的度量（Engineer360）**：以 WI 完成数、PR 周期时间为客观口径做多人对照（见 §3a 度量方案），而非自述。
3. **使用强度 / 信任代理指标（改名，回应 product reviewer V3 P2；具体口径与采集方式，回应 leadership + product reviewer P1）**：一期不做真金白银交易，也**不把这三条等同于"付费意愿"**——它们测的是**内部工程师对编排器的使用强度与信任程度**（供给侧行为信号），"付费意愿"（需求侧、买方批预算行为）严格保留给二期真实预算认领测试。三条口径 + 采集方式：

   | 使用强度/信任代理指标 | 具体口径（怎么算） | 采集方式（怎么拿） |
   |---|---|---|
   | **托管深度** | 试点期内，工程师**主动新增托管的工作流类型数 / workspace 数**的周环比增长 | 直接从 StateStore 审计轨迹统计（零问卷、客观） |
   | **放手程度** | **无人值守时长占比** = workspace 处于 `waiting`(可关机) + 云端自动推进的时长 / 总时长；以及**人工介入率**（每 WI 的人工动作次数）随周下降 | 审计轨迹 + 回叫日志统计 |
   | **决策委托范围** | 工程师**批准编排器自动推进的阶段占比**（vs 坚持每步手动签收）——越高代表越信任 | pr-gate / 签收点日志统计 |

   三者**都从编排器自产的审计轨迹算出**（§2c 第 5 点），无需额外问卷，且随试点自然积累；任一为正、且随迭代走高，即"内部用户越来越信任、越愿把工作托付给编排器"的先行信号——它是**付费意愿的必要非充分前置**（自己人都不敢放手托管的工具，买方更不会付费）。二期再把它升级为一次真实的**内部部门预算认领意向测试**（需求侧、比问卷更硬，才是真正的"付费意愿"，回应 product reviewer 建议）。
4. **FDE 结合（真实客户场景的桥）**：FDE（Forward Deployed Engineer）常年在客户现场做定制自动化——他们是**把内部编排器带到真实客户用例**的天然通道。一期末期邀请 1–2 名 FDE 试用，用他们的客户场景反推 worker 抽象是否够通用；二期正式培训 FDE、收集客户用例。
5. **反馈闭环工具化**：编排器本身产生的审计轨迹（append-only 全历史）就是产品分析数据——哪些 worker 常失败、哪些状态常卡、人工介入率多高，直接指导迭代。

**FDE 现场落地需解决的问题（一期只点名、不求确切方案，回应 human comment + product reviewer FDE 卡点）**：
一期整个运行底座——鉴权（内部 MCP adaptor）、托管（内部 matrix/falcon）、输入源（GUS）、持久化（TCM 的 DynamoDB 栈）——**在任何客户现场都不存在**。技术设计 §4 已给出「可外带 IP 内核 vs 内部专属需重写」的边界清单，并把鉴权/托管/持久化/输入源做成**可插拔 Provider**。但真正在客户 Org 落地时还有一批问题，**属 FDE 需现场研究解决的工作**，一期不给确切方案，仅列为未来问题：
- 编排器如何与客户既有 Org Customizations（自定义对象、Flow、Apex 触发器）**共存/不打架**？
- 是否可建立一个**通用的 AI 组件**（可复用的鉴权/托管/输入适配器），让 FDE 按客户实际需要嵌合进本系统，而非每个现场从零重写？
- 客户现场的合规/数据驻留要求（见 §4 与技术设计 §3 Einstein Trust Layer / Hyperforce）。

### 2d. 与 Salesforce 产品线的耦合

耦合不是「顺带集成」，而是**放大器**——既能借 SF 产品分发本编排器，也能用本编排器给其他产品线增值：

| 产品线 | 耦合方式 | 价值方向 |
|---|---|---|
| **Slack** | 作为 AI 消息接收 + 工作流驱动界面（二期）；Watcher 已监听 Slack | 双向：Slack 是天然的人机界面，替代高门槛的 CLI 交互；为 Slack 增添「驱动数字员工」的能力 |
| **Tableau** | 作为工作流的输入/输出（二期）；本项目源自 TCM，天然贴近 | 编排器为 Tableau 场景做自动化运维/数据流程；Tableau 可视化编排器的审计与效率数据 |
| **MuleSoft** | 作为连接不同 worker/工作流的管道（二期） | MuleSoft 提供企业级连接器，扩展 worker 可触达的外部系统 |
| **Agentforce / Platform** | 编排器作为 Agentforce agent 的「持久化执行 + 多步编排 + 人机审批」底座 | **最具战略性**：见下「技术桥」 |
| **GUS** | 一期输入源（WI）；Watcher 监听 GUS 状态 | 直接提升 SF 内部研发流程效率，自证 ROI |

#### Agentforce/Platform 技术桥（回应 product reviewer P1「互补是断言、缺技术桥」）

把「编排底座」从断言变路径，给出一段接口草图（一期不实现，仅证明可达）。**V4 把 V2/V3 悬而未决的两个"或"收敛为决策，升级为 OQ-5（回应 product reviewer V3 P2 残留：技术桥零推进）**：

1. **编排器作为 Agentforce Action 的长跑后端（回调机制已定，OQ-5）**：Agentforce 的一个 Topic/Action 触发时，不在 Agent 会话内同步跑数小时，而是调用编排器 `submit(workspace, input)` 建根、立即返回 `workid`；编排器 7×24 推进，完成/需审批时**统一通过 [Platform Event](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/) 回调**（不再是"Platform Event 或 Agentforce notification 二选一"）——因为 Platform Event 与本项目 Watcher/envelope 设计天然对齐（技术设计 §3、§2.4）。契约把 Agentforce Action 当**「至多一次触发、结果异步回调收敛」的黑盒**：`workid ↔ Agentforce session` 建立生命周期映射（session 结束不等于 workflow 结束；workflow 完成/失败通过 Platform Event 回写 session 或新开通知），**Agent session 内部的非确定性推理不纳入编排器的 replay 校验**（见下第 5 点）。写进技术设计 §2.4 作为 `AgentforceActionAdapter` 契约。
2. **Flow 的 async 编排层**：Flow Orchestrator 的一个步骤把工作委托给编排器（invocable action → `submit`），编排器完成后回调 Flow 继续——Flow 管 Platform 内的审批与业务对象，编排器管 Platform 外的 durable agent 执行。
3. **Platform Events 作为 Watcher 的 source / 编排器的出口**：编排器把状态跃迁发布为 Platform Event 供 SF 侧消费，或订阅 Platform Event 作为一个 Watcher 源（详见技术设计 §3）。
4. **stateFingerprint 与 Agentforce 非确定性 planner 的共存（回应 product reviewer V3 残留 #3）**：编排器靠 `stateFingerprint` + checkpoint/replay 假设"同一步骤可安全重放得等价结果"，但 Agentforce planner 是**非确定性推理，session 本身不是可倒带的状态机**。解法：编排器**不重放 session 内部推理**，只把"触发 Action + 收敛其异步结果"作为一个 durable step（step 的 memoization 记录的是结果，不是推理过程）；同时把 `stateFingerprint` **扩展为一并校验 [Prompt Builder](https://help.salesforce.com/s/articleView?id=sf.prompt_builder_overview.htm) 模板版本**——解决"prompt 改了、代码没改"的隐性非确定性（模板版本变即显式失败，而非悄悄跑出不同结果）。
5. **Data Cloud / Prompt Builder 集成方向草图（回应 product reviewer V3 残留 #2）**：编排器 append-only 审计轨迹作 [Data Cloud zero-copy](https://help.salesforce.com/s/articleView?id=sf.c360_a_zero_copy_data_federation.htm) ingestion 源（与 §2c「反馈闭环工具化」天然衔接，无需搬数据即可在 Data Cloud 侧分析 worker 失败率/介入率）；Prompt 模板统一走 Prompt Builder 管理并纳入上条 fingerprint 校验。一期不实现，仅证明路径可达。
6. **多租户/合规前瞻**：走向 Platform/多租户商用时须满足 Hyperforce 租户隔离 + 数据驻留、CRUD/FLS/共享模型、[Einstein Trust Layer](https://www.salesforce.com/products/platform/trusted-ai/)——这是比一期 per-submitter 隔离更大的架构改造，列为远期架构约束（§4、技术设计 §3）。

> **平台约束占位数字（待 Agentforce 平台架构团队核准，与 token 账单"待核准"处理方式对称）**：Platform Event 发布频率上限、Flow invocable action 同步时限、Agentforce Action 会话内超时——三个桥接点各有平台硬约束，须在 OQ-5 裁决时向 Agentforce/Platform 团队取实际数字后写死；一期不依赖这些数字（一期不接 Agentforce）。

**结论**：本项目对内是研发效率工具，对外是 Agentforce/Platform 的编排底座候选——两条线共用同一内核，降低重复投入。桥接的两个关键未决点（回调机制、session 映射）**已在本版收敛为倾向决策并升级为 OQ-5**，交 Agentforce 平台架构团队 + 本项目 owner 在闸门 B 前联合裁决。

---

## 3. 开发阶段与成本

### 3a. 一期（重点）：面向内部 Engineer

**产品形态**：一个内部编排器 + 已有 sticky-note 人机界面 + 少量预定义 worker/watcher。**用户旅程**：工程师在 sticky-note 选一个 WI → 编排器全自动推进（研究→写码→提 PR→等 review→修订→测试→回归）→ 断点续跑不需盯着 → 到「需要人做决定/审查/签收」时回叫通知 → 人类审查并承担责任。

**要交付的能力（对齐设计思路·一期目标）**：

| 能力 | 交付内容 | 状态 |
|---|---|---|
| 状态持久化（StateStore） | DynamoDB 单表实现 + 接口抽象；`工作流模版.md` 的字段模型 + D1/D2 新增字段 + `tokenSpent` 预算字段 | 模型已设计，需工程实现 |
| workflow 引擎（agent-work-manager） | 扫描/CAS 抢 lease/route/守护层；affinity 分区认领；可编排多 worker、可嵌套 workflow | 核心自研 |
| affinity 调度 + liveness 改派 | 本机 daemon 认领 `machine:自己`，云端引擎认领 `cloud`；跨界只告警；永久失配→改派（技术设计 §2.3） | 见技术设计调度图 |
| 韧性护栏 | 熔断/限流/背压/bulkhead + per-workspace token 预算护栏（技术设计 §2.1） | **本版新增** |
| 最小 SDK 内核 | 状态存储 skill（`createRoot/checkpoint/transition/spawn/finish/fail/latest`）+ handler 契约（`enter`+`route`） | **提前到一期** |
| Watcher 采集层 | event envelope schema + Watcher 契约 + 预定义 watcher（Slack/PR/CI-CD/GUS 等）+ `signal()` 回调 + dedup 表 | watch-pr 泛化 |
| 路由器 | 注册表 + 显式路由 + 关键字匹配（非自主发现） | 降级版 |
| worker 鲁棒性 | 完善 wi-researcher/wi-worker，提高处理鲁棒性 | 基于现有原型 |
| 人机闭环 | sticky-note 输入抽象化 + 回叫通知/审批入口 + 局部失败呈现 + 一键 Reconnect/改派（技术设计 §2.6） | 扩展现有 |

#### 成本量化（回应 product reviewer P0「成本/Token/工期量化缺席」）

> 以下为**立项估算**，含明确假设，须在 OQ-1（能否引 MIT LangGraph/DBOS）锁定后细化。数字为区间 + 假设，不是承诺。

**（1）人力与里程碑（AI 辅助开发）**：

| 里程碑 | 内容 | 工期（1–2 名工程师） |
|---|---|---|
| **M1 内核 MVP** | StateStore(DynamoDB) + 引擎主循环 + lease/CAS + 幂等/恢复；单机 dogfood 跑通 1 个 workflow | 档位1：3–5 人周 / 档位2：8–12 人周 |
| **M2 affinity + 云端** | 本机 daemon + 云端引擎分区认领；liveness 改派；接 matrix（依赖其就绪） | 2–4 人周 |
| **M3 采集层 + 护栏** | Watcher 契约 + envelope + dedup + `signal()`；熔断/背压/token 预算 | 3–4 人周 |
| **M4 人机闭环 + 试点** | sticky-note 输入抽象 + 通知/审批 + 局部失败面板；3–5 人试点 + Engineer360 度量 | 3–4 人周 |
| **M2 应急缓冲：ECS/Fargate 自建最小托管**（**仅在 matrix 延期触发**，回应 engineering reviewer V3 P1） | 若 matrix 未按 M2 排期就绪，自建最小 ECS/Fargate 跑云端引擎 + worker（复用 TCM 同栈经验），保住"云端 7×24"这条价值主张 | **+2–4 人周**（条件性，非基线；触发条件 = R1/OQ-4 命中） |
| **合计（到可复现试点）** | — | **档位1 ≈ 11–17 人周；档位2 ≈ 16–24 人周**（约 1 季度，1–2 名工程师，AI 辅助）；**+matrix 延期应急 2–4 人周** |

> 档位1/档位2 的差别 = 能否直接复用 LangGraph/DBOS 的 checkpointer/恢复算法（OQ-1）。**OQ-1 是一期工作量与 token 账单的最大单点变量**（见 §5、技术设计 OQ-1）。
> **ECS/Fargate 应急退路成本已显式入表（回应 engineering reviewer V3 P1 残留）**：此 2–4 人周是**一期 matrix 延期的应急退路**，与 §3b 二期"Provider 化 ≈8–14 人周"是**不同触发条件的两笔钱**（前者=一期临时保云端能力；后者=二期把 4 层 Provider 化以支撑客户现场），不可混淆。护栏共享写的云资源/延迟增量成本见下 (2)。

**（2）云资源月成本（非主成本，含护栏共享写增量）**：DynamoDB on-demand + SQS + 少量计算，在一期试点量级（数名工程师、数十并发 workspace）下**月成本预计在几十至低几百美元量级**——相对 LLM token 是零头。TCM 已在同栈生产运行，容量/告警经验可复用。
- **护栏共享写成本已量化（回应 engineering reviewer V3 P1 item B）**：熔断/背压护栏每次认领/放行多一次 DynamoDB 条件写（技术设计 §2.1）。按一期量级（15–25 workspace × 30–80 步 × 每步个位数次护栏写 ≈ 每月百万级写请求，DynamoDB on-demand 写 ≈ $1.25/百万）折算，**月增量 < $1，可忽略**；延迟侧每步 **+个位数毫秒**（单次条件写 P99，AWS 保守口径），相对单步 LLM 调用的秒级耗时可忽略。

**（3）LLM Token 预算（本视角硬缺口，重点测算）**：
一个 7×24、多 worker、无人值守、以 `claude -p` 回调驱动的编排器，**Token 是主成本项且随并发线性上升**。估算框架 = **并发 workspace 数 × 每 workspace 平均步数 × 单步平均 token × 单价**：

| 参数 | 一期试点假设 | 说明 |
|---|---|---|
| 并发 workspace | 3–5 人 × 4–5 并行 ≈ **15–25** | 与早期信号一致 |
| 每 workspace 步数 | 30–80 步 | 研究→码→PR→review→修订→测试→回归 |
| 单步 token | 15k–40k（含上下文+输出） | 长上下文 agent 步 |
| 每 workspace 累计 | **≈ 1–3M token** | = 步数 × 单步 |
| 单价（已核准，2026-06 Anthropic 公开定价） | **Sonnet $3/M 输入 · $15/M 输出**；**Opus $5/M 输入 · $25/M 输出**（纯单价比 Opus:Sonnet ≈ **1.67×**，非早前假设的 5×） | prompt caching（cache read ≈0.1× 输入价、约 90% 折扣）可进一步显著降输入成本 |

**一期每月 token 账单合成区间（把框架乘成一个数，回应 product reviewer P1「临门一脚」）**：

> 用上表参数直接相乘（**单价已按 2026-06 Anthropic 公开定价核准，不再是待定值**；这里给量级区间，供决策层立项拍板）。假设一期试点每月周转 **15–25 个 workspace**、每个累计 **1–3M token**，且输入/输出约 3:1、prompt caching 未计入（计入后更低）。

| 混合模型 | 每 workspace 成本（1–3M token） | **一期每月账单（15–25 workspace）** | 说明 |
|---|---|---|---|
| **Sonnet 档**（主力，$3/M 输入 · $15/M 输出，混合 ≈ $6/M） | ≈ $6–18 | **≈ $90–450 / 月** | 一期主力路径的现实预期 |
| **Opus 档**（复杂步升级，$5/M 输入 · $25/M 输出，混合 ≈ $10/M） | ≈ $10–30 | **≈ $150–750 / 月** | **已按 Opus:Sonnet ≈1.67× 单价订正（原 5× 假设把此档高估约 3×）**；仅少数难步用 Opus |
| **保守上界**（全 Opus + 高步数 + 无 caching） | — | **约 $1–2k / 月量级** | 失控烧钱的理论上界，由下方硬护栏封住 |

**结论（一句话给决策层）**：一期 LLM token 账单**大概率落在 $1k/月以内（Sonnet 主力约 $90–450，全 Opus 也仅 $150–750）**，最坏情形（全 Opus + 高步数 + 无缓存 + 高并发）才到约 $1–2k/月——且被 per-workspace 硬上限 + 熔断封住上界。相对一支工程团队的产出提升，单位经济学清楚、可承受。**（单价已核准；总量仍待试点实测校准并发数与步数假设。）**

> **订正说明（回应 product/engineering reviewer V3 P1）**：早前版本假设「Opus 约 5× 单价」，据 2026-06 Anthropic 公开定价（Opus $5/$25、Sonnet $3/$15）实为**纯单价比 1.67×**，据此 Opus 档从 ≈$450–2,250/月**下修为 ≈$150–750/月**。原假设方向保守（高估成本）不致命，但既有权威定价可核准，故直接订正并去掉"待核准"hedge。若实际观测到 Opus 单步 token 消耗（尤推理/输出）系统性高于 Sonnet，会在试点实测中据实上调倍数并注明。

- **省 token 的关键设计**：durable execution 的**步骤级 memoization/replay**——恢复续跑时已完成步骤**不重复调 LLM**（这正是 DBOS / LangGraph checkpointer 的核心能力，也把 OQ-1 与 token 账单直接绑定：能引依赖既省工期又省 token）。
- **失控烧钱护栏（既是成本也是安全）**：新增 `tokenSpent` 字段 + **每 workspace token 上限 + attemptCount 上限**做**硬约束**，超限转终态 `error` 并回叫通知，杜绝失控循环无限烧钱（技术设计 §2.1）。**每-WI 成本上限**作为一期显式交付。

**（4）运维/支持隐藏成本**：OAuth 过期 Reconnect 的人工 toil（R4）、watcher 维护、per-submitter 隔离运维、跨界告警值班——一期靠 sticky-note 面板把这些 toil 可视化、集中处理（技术设计 §2.6），预计占 0.2–0.5 人力；随规模上升须在二期工具化。

**关键外部依赖**：`matrix`/`falcon` 云端托管（P1）、`matrix` 身份机制（OQ-2）——**非本项目交付，须并行确认排期**。若 matrix 未就绪，一期主力回退本机 worker，云端能力延后（退路成本见 R1、OQ-4）。

**一期不做**（明确降级，控制范围）：discover agent 自主发现、图形化编排界面、终端用户可用、自建鉴权、云端身份代持（若 matrix 不提供）、全量 SQS 事件总线、跨客户现场移植（仅在技术设计 §4 划边界、埋接口）。

**度量方案（把 "3×" 从个人信号变成可复现结论）**：
- **诚实定位**：现有 "3×" 是 **n=1、作者本人、归因未隔离、代理指标**的早期信号，是立项的**待验证假设**。
- **验证设计**：一期招募 **3–5 名工程师试点**，Engineer360 口径做**对照/前后对比**（WI 完成数、PR 周期时间、人工介入次数）；区分「工具贡献 vs 个人因素」。
- **成功判据（示例）**：试点组相对对照组 WI 吞吐提升可统计显著（例如 **≥1.5×**，而非坚持 3×）、人工介入率随迭代下降、付费意愿代理指标为正。

### 3b. 后续各期蓝图

沿设计思路的分期，并接住一期埋好的扩展点（StateStore 接口、event envelope、handler 契约、可插拔 Provider 都是后续不返工的地基）：

**二期（推环境：平台化 + 消息统一 + SF 耦合）**：
- 统一 AI agent 模版为正式 **SDK**，改写现有 worker，降低开发门槛与 token 消耗。
- 完善消息/事件监听、捕捉、分发——**全量统一到 SQS/EventBridge 事件总线**，watcher 注册中心；把更多工作流纳入自动化。
- **SF 产品耦合落地**：Slack 收发 AI 消息驱动工作流、Tableau 作输入/输出、MuleSoft 作 worker 管道。
- 处理 GUS WI 以外的工作流。
- **鉴权升级**：云端 server-side OAuth 代持用户身份 24×7，突破一期「云端 worker 拿不到用户身份」的限制（D2/D3）。
- 培训 FDE，收集客户用例，反推产品通用性（2c）。
- **Provider 化 + 客户现场适配的增量成本粗估（回应 product/FDE reviewer P2）**：一期 M1–M4 是**内部口径**，未含"把 4 层（持久化/鉴权/托管/输入源）Provider 化 + 客户现场落地"的额外工作量。粗估二期需额外 **≈ 8–14 人周**（每层 Provider 接口固化 + 至少一个非 SF-internal 参考实现 + 干净 org 冒烟），这是 FDE→客户商业故事的真实成本，列入二期预算而非藏在一期。

**远期（推产品：商业化）**：
- **discover agent**：语义路由自主找 handler（一期的注册表升级为智能发现）。
- **图形化 AI 开发界面**：拖拽状态机 + 组装工作流，定义 agent/skill 只需声明状态与迁移。
- **终端用户可用**：模版 + 图形界面 + 封装的持久化/消息/鉴权，让 Salesforce 客户低门槛组装自己的工作流——把 AI 从「chatbot」变成「可编排的数字员工」。
- **商业化形态**：优先作为 Agentforce/Platform 的编排能力内嵌（OQ-3）；接入 Einstein Trust Layer、满足 Hyperforce 多租户/数据驻留（技术设计 §3）。

---

## 4. 风险登记与外部依赖（Risk Register）

| # | 风险 / 依赖 | 影响 | 缓解 |
|---|---|---|---|
| R1 | `matrix`/`falcon` 托管未按期落地 | 云端 24×7 能力缺失 | 一期主力回退到 `affinity=machine` 本机 worker；准备 ECS/Fargate 技术退路（OQ-4） |
| R2 | `matrix` 身份机制 = (a) 调用门禁而非 (b) 代持（OQ-2） | 云端 worker 无法以用户身份操作 GUS/Slack | 按 (b) 强假设设计，降级 (a) 容易；给出服务账号身份退路 |
| R3 | 合规不允许引入 MIT 的 LangGraph/DBOS（OQ-1） | 需自研持久化内核，一期成本+token 账单上升 | 技术已备好（`工作流模版.md`）；先向法务/架构确认；列为立项前置阻塞项 |
| R4 | MCP 连接 OAuth 过期，无头 worker 无法自弹登录（D2） | 脱机长跑中断 | 「只告警不硬跑」+ 一键 Reconnect（技术设计 §2.6）；二期云端代持解决 |
| R5 | "3×" 效率无法在多人复现（D5） | 立项 ROI 论据削弱 | 试点对照 + 保守成功判据（≥1.5×）；即便部分成立仍有价值 |
| R6 | 共享云表 per-submitter 隔离缺失（D1/D2） | 跨 submitter 数据越权 | 一期最简：云凭据按人隔离，worker 只读写自己 submitter 分区；二期 API gateway；商用走 Hyperforce 多租户 |
| R7 | 范围蔓延（discover/图形化/终端用户被提前拉进一期） | 一期延期 | 本报告已明确降级清单（§3a「一期不做」），严格守边界 |
| R8 | **LLM token 失控烧钱**（本版新增，回应 product reviewer P0） | 成本与安全双重风险 | per-workspace token/attemptCount 硬上限 + 熔断（技术设计 §2.1）；memoization 省重复调用 |
| R9 | **客户现场无 matrix/MCP/GUS/DynamoDB 底座**（可移植性悬崖） | FDE 带向客户时需重写多层 | 可外带 IP 内核 + 可插拔 Provider（技术设计 §4）；一期埋「非 SF-internal 环境冒烟」判据 |
| R10 | **下游外部 API 限额**（本版新增，回应 engineering reviewer V3 P2）：15–25 并发 workspace 跑 WI 循环时，对 **SF Core API 每日请求限额 / GUS / Slack / GitHub API** 的消耗此前从未测算——这些系统各有 governor limits，一期护栏只防我们自己的 LLM 调用风暴，**不防下游 governor limits** | 撞下游限额 → 采集/驱动链路 429/被限流、WI 卡住 | 一期即测算每 workspace 下游调用量级 × 并发数，对照各系统已知限额给撞限额判断；用与 R8 同框架（**每类外部 API 独立令牌桶 + 熔断 + 退避重试**）覆盖下游侧，纳入技术设计 §2.1 护栏范围 |

---

## 5. 待决问题汇总（Open Questions）

供 human comment / reviewer 在下一版收敛。**owner + deadline 为 writer 的建议指派**（headless 环境无法代替管理层签名，故以 `[OPEN QUESTIONS]` 标注待人类确认；见每条 owner 列）：

| OQ | 问题 | 建议 owner | 建议 deadline | 倾向/工作假设 |
|---|---|---|---|---|
| **OQ-1**（最高优先，立项前置阻塞项） | 合规是否允许引入 MIT 的 LangGraph/DBOS？决定档位1（框架上增功能）vs 档位2（自研内核）——一期成本与 token 账单的最大单点变量 | **本项目 owner + 法务/OSS 合规评审** | **闸门 A 内，立项 kickoff 后 2 周** | 建议先确认；不能引则自研（技术已备好） |
| **OQ-2**（D3/R2） | `matrix` 的「本机个人鉴权 → 云端 worker」是 (a) 调用门禁还是 (b) 身份代持？决定 `affinity=cloud` worker 能否以用户身份操作外部系统 | **本项目 owner ↔ matrix/falcon 团队** | **M2（接 matrix）启动前** | 工作假设 (b) 代持，(a) 有服务账号退路 |
| **OQ-3**（§2b） | 商业化路径独立 SaaS vs 内嵌 Agentforce/Platform？（= build-vs-leverage / 编排层归属裁决） | **产品/战略层（Agentforce/Platform editor + 本项目 owner）** | **闸门 A 内（投钱前，阻塞）** | 敏感度分析显示**倾向内嵌基本稳健**（§2b），唯"必须保独立议价权"能翻盘 |
| **OQ-4**（human comment：Matrix 内部工具 vs 对外产品） | `matrix` 是公司内部工具 → 客户现场无 agent 托管平台，商业化落地结构性顾虑 | **本项目 owner + FDE 代表** | **二期 FDE 培训前** | 后备：客户现场 EC2/ECS/Fargate 自建最小托管或用客户自有服务器（技术设计 §4 托管 Provider 可插拔） |
| **OQ-5**（§2d，本版新增，回应 product reviewer V3 P2） | Agentforce 技术桥的两个落地未决点：① Action 异步回调机制（本版倾向统一 **Platform Event**）；② `workid ↔ Agentforce session` 生命周期映射 + stateFingerprint 与非确定性 planner 共存契约 | **Agentforce/Platform 平台架构团队 + 本项目 owner** | **闸门 B 前（二期加码前）** | 倾向：回调走 Platform Event、Action 视为"至多一次触发+异步收敛"黑盒、session 内部推理不入 replay、fingerprint 扩校验 Prompt Builder 模板版本（§2d）；须取平台约束实际数字后写死 |

> `[OPEN QUESTIONS]`：上表 owner/deadline 是 writer 的**建议默认**，非已签署承诺。**OQ-1 与 OQ-3 是闸门 A（投钱前）的两个阻塞项**——请管理层在 kickoff 时正式指派责任人并确认时间线。倾向建议：OQ-1 先确认合规、OQ-3 由战略层就"编排层归属"给署名结论。
>
> **OQ-4 补充**：是否需要一个可复用的「客户现场托管适配」通用 AI 组件，留 FDE 现场按需研究（§2c）。

---

## 附录：设计依据与决策追溯

本报告的关键设计取舍均可追溯到 `design-notes.md` 的决策记录（D1–D5）与[技术设计文档](./distributed-orchestrator-tech-design.md)：
- **D1**：本机 worker 恢复主体 = 本机 daemon；单一事实源 = 云端；`affinity`/`submitter` 字段；「断网」= 中断容错而非断网执行。
- **D2**：一期鉴权复用 MCP（开发者本人身份、机器本地）；三条硬边界。
- **D3**：matrix 云端 worker 身份机制（外部依赖 + OQ-2，工作假设 (b) 代持）。
- **D4**：消息/信号层 = watch-pr 泛化的 Watcher 契约 + event envelope + `signal()` 回调；一期本机 push、云端按需 SQS。
- **D5**：效率证据度量口径（诚实标注 n=1 + 试点验证路径）。

---

## 修订区（Changelog）

### V4 — 2026-08-11（回应 PR #4 human comments + tech/product/leadership V3 反馈）

**本文档（可行性报告）相较 V3 的主要改进**：
1. **§0.1 痛点重构（回应 human comment 多条 unresolved thread）**：`P1–P5` 更名为 **`PP1–PP5`（Pain Point，避免与 priority 混读）**；每条 PP 补**可量化的效率损耗口径**（⅔ 时间窗口闲置 / 断了从头重来 / 并行度受限于 CLI 窗口数 / 全程在场 / 红利集中在极少数人）；新增**痛点鱼骨图**（`v4-painpoint-fishbone.png`）+ "PP → 共同根因（人的在场成为吞吐瓶颈）→ 研发效率低下"的关系文字。
2. **§0.2 一期解决方案前移紧接痛点（回应 human comment）**：原 §0.3 solution 上提为 §0.2，**逐条对症 PP** 的解决方案表 + `installer` 降门槛；新增 **§0.2.1「一期实现后的开发流程」**——把"落地后工程师的一天"讲成流水（人只在 make decision/review/sign-off 三点介入），直观体现效率提升机制。
3. **§0.3 原型实例（回应 human comment）**："早期信号"更名为**原型实例**并移到解决方案之后（是"方案作者已跑起来"的实证）；WI 端到端叙述补"第 6–7 步之间推 Slack channel 提醒作者做 PR review"的回叫细节；总览截图已上提至 §0.0（证据先行）。
4. **§0.2.1 Ask 改"至少两人"（回应 human comment）**：一期小队从"1–2 名"改为**"至少 2 名工程师"**（互相纠错、代码合并的审核与批准）。
5. **§3a Opus 单价订正（回应 product/engineering reviewer V3 P1）**：Opus:Sonnet 从错误的 **5×** 订正为 **1.67×**（Opus $5/$25、Sonnet $3/$15），Opus 档月账单 **$450–2,250 → $150–750**，去掉"待 claude-api 核准"hedge（单价已核准）；结论下修为"大概率 $1k/月以内"。
6. **§3a M1–M4 补 ECS/Fargate 应急退路预算行（回应 engineering reviewer V3 P1 残留）**：matrix 延期触发的 **+2–4 人周**条件性预算，明确与二期 8–14 人周 Provider 化是不同触发条件的两笔钱；护栏共享写成本量化（月增量 <$1、每步 +个位数毫秒）。
7. **§4 新增 R10 外部 API 限额风险（回应 engineering reviewer V3 P2）**：15–25 并发下 SF Core/GUS/Slack/GitHub 下游 governor limits 盲区，用 R8 同框架（每类 API 独立令牌桶+熔断+退避）覆盖。
8. **§2b 定价锚点 + 假设买方画像（回应 product reviewer V3 P2）**：补 Temporal/LangGraph/Inngest/n8n 计费轴锚点 + 我们的 consumption 落点；假设买方 = "已部署 Agentforce、有 AI-ops/可靠性预算线的平台工程/研发效能负责人"，并指出闸门 B 缺需求侧 gate。
9. **§2c 指标改名"使用强度/信任代理"（回应 product reviewer V3 P2）**：三条指标测的是内部工程师使用强度/信任，"付费意愿"严格保留给二期真实预算认领测试（避免 overclaim）；闸门 B 第 4 条同步改名。
10. **§2d Agentforce 技术桥推进 + 新增 OQ-5（回应 product reviewer V3 P2 残留）**：两个悬而未决"或"收敛为倾向决策——回调统一走 Platform Event、Action 视为"至多一次触发+异步收敛"黑盒、`workid↔session` 生命周期映射、session 内部推理不入 replay、stateFingerprint 扩校验 Prompt Builder 模板版本；补 Data Cloud zero-copy 集成草图 + 三个桥接点平台约束占位数字；升级为 **OQ-5**（Agentforce 平台架构团队裁决，闸门 B 前）。

#### V4 Q&A / 反馈回应（逐条）

**Human comments（PR #4 上 V3 后新增的 unresolved review thread，产品/领导层文档）**：

| # | comment | 处理 |
|---|---|---|
| `P1` 改成 `PP1`（pain point）——`P1` 易被误读为 priority | **采纳**：§0.1 全部 `P1–P5` → `PP1–PP5`，并加一句说明。 |
| 各 pain point 可否量化 | **采纳**：§0.1 每条 PP 补"可量化的效率损耗"列。 |
| 找出 PP 与阻碍效率的关系，尽量量化，并生成鱼骨图 | **采纳**：§0.1 新增鱼骨图 `v4-painpoint-fishbone.png`（源 `.mmd`）+ "PP→共同根因→研发效率低下"关系文字。 |
| 在 PP 之后，立刻描述一期实现后的开发流程，体现效率提高 | **采纳**：新增 §0.2.1「一期实现后的开发流程」，把落地后工程师的一天讲成流水，点出效率提升机制。 |
| 这个改成一期的 solution，紧接 pain point（针对 PP 的解决方案） | **采纳**：原 §0.3 solution 上提为 §0.2，逐条对症 PP 的解决方案表，紧接痛点。 |
| "早期信号"改成"原型实例"，放到 solution 后面 | **采纳**：更名为"原型实例"并移到 §0.3（解决方案之后）。 |
| §0.2.1 在第 6–7 步之间应有 Slack channel 推送 + 提醒作者做 PR review | **采纳**：§0.3(2) WI 端到端叙述补此回叫细节。 |
| Ask 建议至少两人 | **采纳**：§0.2.1 Ask 改"至少 2 名工程师"（互相纠错、代码合并审核批准）。 |
| "极其不友好"等措辞需专业化 | **采纳**：§0.1 PP3 改为"命令行交互对非专业用户上手门槛高、可用性差"；§2a/§2d 的"恐怖的 CLI"改为"高门槛的 CLI 交互"。 |
| §0.4 补 Agentforce 底座内核的文档链接 | **采纳**：§0.4 补 Agentforce 官网链接 + 指向技术设计 §2.4/§3 与 §2d 技术桥。 |

**Tech reviewer V3（8.3/10）**：主要落点在技术设计文档与 `工作流模版.md`。本可行性报告同步：崩溃泄漏修复（背压真值改由 `GSI2(affinity+progress)` Count 派生、弃独立计数器）已在技术设计 §2.1 + `工作流模版.md §4` 落地；本文 §3a(2) 同步护栏共享写成本量化（月增量 <$1、每步 +个位数毫秒），与技术设计一致。

**Product reviewer V3（7.6/10）**：

| 建议 | 优先级 | 处理 |
|---|---|---|
| 订正 §3a Opus 单价倍数（5× → 1.67×，Opus 档 ≈$150–750/月），去 hedge | **P1** | **采纳**：§3a 单价表 + 账单表 + 结论全部订正，去掉"待核准"；加订正说明。 |
| M1–M4 补一期 matrix 延期的 ECS/Fargate 应急退路预算行（2–4 人周） | **P1** | **采纳**：§3a M1–M4 表新增条件性应急行，明确与二期 8–14 人周区分。 |
| 补外部系统 API 限额风险（SF Core/GUS/Slack/GitHub） | **P2** | **采纳**：§4 新增 R10，用 R8 同框架覆盖下游 governor limits。 |
| §2c 三指标改名"使用强度/信任代理" | **P2** | **采纳**：§2c 改名，"付费意愿"保留给二期真实预算测试；闸门 B 第 4 条同步改名。 |
| §2b 加定价锚点 + 假设买方画像 | **P2** | **采纳**：§2b 补 Temporal/LangGraph/Inngest/n8n 计费轴 + consumption 落点 + 买方画像 + 需求侧 gate 缺口提示。 |
| Agentforce 技术桥两未决点升级为 OQ-5 + stateFingerprint 与非确定性 planner 共存 | **P2** | **采纳**：§2d 收敛为倾向决策 + Data Cloud/Prompt Builder 草图 + 平台约束占位数字；新增 OQ-5。 |
| 护栏共享写成本/延迟量化 | **P2** | **采纳**：§3a(2) 折算月增量 <$1、每步 +个位数毫秒（与技术设计 §2.1 一致）。 |
| "干净 org 冒烟"升级为"dirty org 冒烟" + FDE 试点可审计判据 + 打包/交付形态 + 现场支持模型 | **P2** | **采纳**（落技术设计 §4 + §3b）：技术设计 §4 补 Scratch Org + 预装含触发器/Flow 的 AppExchange 包做 dirty-org 冒烟、排入二期 FDE 培训前 + 打包/L2 支持模型；本文 §3b Provider 化增量成本区间维持。 |

**Leadership reviewer V3（7.8/10，conditional-GO）**：

| 建议 | 优先级 | 处理 |
|---|---|---|
| 尽快执行闸门 A 战略层裁决（编排层归属/非重复投资）——非 writer 可解 | **P0** | **记录**：报告侧（§0.4 闸门 A + §5 OQ-3）已完全就位，球在管理层；writer 无需再改文档，本条留作 kickoff 行动项。 |
| §2c 三指标从试点 M1 即接入审计轨迹采集 | **P1** | **采纳**：§2c 已注明三指标从编排器自产审计轨迹算出（零问卷）；§3a M4 明确试点期采集，即 M1 起埋点。 |
| 把最有冲击力的原型证据前置到 §0 附近（证据先行） | **P2** | **采纳**：§0.0 决策卡开篇已上提原型总览截图 `v4-sticky-note-overview.png` + 说明（V4 保留并强化）。 |
| 产出 1–2 页 presentation 抽取版（决策卡+关键截图+Conditional GO+四 gate） | **P2** | **[OPEN QUESTIONS]**：倾向"另出独立 presentation 抽取文件而非塞进本报告"（避免完整评审版与 pitch 版混淆）。本轮先在 §0.0 决策卡确保可独立支撑 3 分钟 pitch（Ask/收益/成本/风险/建议/门槛一屏齐全 + 证据截图）；是否单独产出抽取版 deck 待管理层确认展示形式后再做。 |
| 完整版保留 Changelog/Q&A 供留痕，presentation 版剔除 | **P2** | **采纳（记录）**：Changelog/Q&A 保留在完整版末尾供评审追溯；presentation 抽取版（若产出）不含这两节。 |

### V3 — 2026-08-10（回应 human comment 实战示例 + leadership/product/tech V2 反馈）

**本文档（可行性报告）相较 V2 的主要改进**：
1. **§0.0 决策摘要卡（新增，回应 leadership P1）**：半页收拢 Ask / 一期收益 / 一期成本量级 / Top-3 风险 / 决策建议 / go-no-go 门槛，服务 30 秒 presentation 决策。
2. **§0.4 决策建议（新增，回应 leadership P1）**：明确写出 **Conditional GO + 两道闸门**（闸门 A 战略裁决+OQ-1 owner；闸门 B 四条试点 gate），把报告从"陈述"变"建议"。
3. **§0.2.1 一期实战一览（新增，回应 human comment 两条 unresolved thread）**：嵌入 4 张真实原型截图（sticky-note 人机界面 / 双击激活 WI-worker / job-scheduler 带登录态 / watch-pr 信号采集）+ 真实 WI 实例 `W-23433231` + **WI 端到端推进示意图**（WI-worker/tcm-automated-sdd/pr-gate/WI-chatter/watch-pr/job-scheduler/外部信号源），显式点出"一人并行多 WI、只做决定/审查/签收"的效益机制。
4. **§2b OQ-3 权重敏感度分析（新增，回应 product P2）**：等权 12 vs 14，测「分发/议价权/壁垒」三种双权重——除"议价权双权重打平"外内嵌均胜出，结论**基本稳健**。
5. **§2c 付费意愿代理指标口径化（回应 leadership + product P1）**：从方向性描述升级为**三条可从审计轨迹客观算出的指标**（托管深度/放手程度/决策委托范围）+ 采集方式，并给出二期"真实预算意向测试"升级路径。
6. **§3a 一期每月 token 账单合成区间（回应 product P1「临门一脚」）**：把"并发×步数×单步×单价"框架乘成数字——Sonnet 主力 **≈ $90–450/月**、Opus 档 **≈ $450–2,250/月**、保守上界数千美元/月（由硬护栏封住），标注待 claude-api 核准。
7. **§5 Open Questions owner+deadline（回应 leadership + product P1）**：OQ-1/2/3/4 补建议 owner + deadline 表，OQ-1/OQ-3 标为闸门 A（投钱前）阻塞项，以 `[OPEN QUESTIONS]` 待管理层签署。
8. **§1 术语脚注（回应 leadership P2）**：affinity/CAS/lease/stateFingerprint/StateStore 一次性业务语言对照，降低纯业务读者阅读摩擦。
9. **§3b 二期蓝图（回应 product/FDE P2）**：补 Provider 化 + 客户现场适配的增量成本粗估（≈8–14 人周），不藏在一期。

### V2 — 2026-08-10

**结构性变更（回应 human comment：拆分文档）**：应 human comment，将原单一 `distributed-orchestrator.md` **拆分为两份交叉引用的文档**——[**技术设计文档**](./distributed-orchestrator-tech-design.md)（面向技术审核人）与本**可行性报告**（面向产品/领导层）。原 `distributed-orchestrator.md` 改为索引页。相应更新了 `tech-reviewer` / `product-reviewer` / `leadership-reviewer` 定义与三个 `*_team.py` 及 `design-work-flow`，把评审对象指向两份新文档，保持一致性。

**本文档（可行性报告）相较 V1 的主要改进**：
1. **§0 执行摘要重写为产品/领导层视角**：把设计思路的 5 条痛点**归纳润色为 P1–P5 表格**作为 why（presentation 时人类只读本文）；确立「**一期推工具、二期推环境、长期推产品**」主线（回应 human comment）。
2. **§2b 商业前景**：明确一期只谈内部收益、商业化作愿景/可能性探讨（回应 human comment + product reviewer「需求未验证」）；OQ-3 从「倾向后者」升级为**四维二维打分**（TAM/壁垒/分发/议价权）。
3. **§2c 落地闭环**：新增**付费意愿代理指标**；把 FDE 现场落地问题（与客户 Org 共存、通用 AI 组件、合规）**列为未来问题**（回应 human comment：一期只点名、不给确切方案 + product reviewer FDE 卡点）。
4. **§2d Agentforce 技术桥（回应 product reviewer P1）**：给出编排器 ↔ Agentforce Action / Flow async / Platform Events 的接口草图 + 多租户/合规前瞻，把「互补」从断言变路径。
5. **§3a 成本量化（回应 product reviewer P0 硬缺口）**：新增人力/里程碑（M1–M4，档位1 ≈11–17 / 档位2 ≈16–24 人周）、云资源月成本、**LLM Token 预算**（并发×步数×单步×单价 + memoization 省 token + 每-WI token 硬上限/熔断）、运维隐藏成本。
6. **§4 风险登记**：新增 **R8（token 失控烧钱）**、**R9（客户现场可移植性悬崖）**。
7. **§5 Open Questions**：新增 **OQ-4（Matrix 内部工具 vs 对外产品 + EC2/客户服务器后备计划）**（回应 human comment）。

### Q&A / 反馈回应（产品/领导层视角，逐条）

**Human comments（产品/落地相关）**：

| # | comment | 处理 |
|---|---|---|
| 痛点应归纳复述为 why（评审员不读设计思路） | 在本文开头归纳润色痛点 | **采纳**：§0.1 P1–P5 痛点表作为 why。 |
| 一期推工具，二期推环境，长期推产品 | 分期主线 | **采纳**：§0 分期主线明确采用此表述。 |
| Matrix 是内部工具还是对外产品 | 作为 OQ 提出顾虑（客户没有 agent 托管平台）+ 后备计划（EC2/客户服务器） | **采纳**：新增 OQ-4 + R1/R9 缓解 + 技术设计 §4 托管 Provider 可插拔。 |
| 持久化能否作为产品的一部分提交 | — | **采纳**：§3a 明确 StateStore（含 DynamoDB 实现）是一期交付能力、可作产品组件；可移植性见技术设计 §4。 |
| FDE 现场落地/客户既有自动化共存 | 说明是 FDE 现场解决的工作、可否建通用 AI 组件；一期只提未来问题、不给确切方案 | **采纳**：§2c「FDE 现场落地需解决的问题」列为未来问题，不给确切方案。 |
| 商业化愿景一期可接受、只作可能性探讨 | 专注一期内部收益 | **采纳**：§2b 说明明确此定位。 |

**Product reviewer V1（6.4/10）P0/P1**：成本/token 量化（§3a）、可移植 IP 内核边界（技术设计 §4 + 本文 §2c/R9）、Agentforce 技术桥（§2d）、OQ-3 二维打分（§2b）、锁定 OQ-1 时间线（§5，标为立项前置阻塞项）——**全部采纳并落地**。付费意愿代理指标（§2c）、竞品定价/定位（§2a 时间窗口风险）已回应。

> 说明：本轮尚无 `leadership-reviewer-feedback-V1.md`（仅 tech + product 两份 V1 反馈），故本版未针对 leadership AI 反馈作回应；待其反馈产出后于下一版收敛。

### V3 Q&A / 反馈回应（逐条）

**Human comments（PR #4 上 2 条 unresolved review thread，产品/领导层文档）**：

| # | comment | 处理 |
|---|---|---|
| 给出 WI 推进从头到尾示意图（WI-worker/tcm-automated-sdd/pr-gate/WI-chatter/watch-pr/job-scheduler/Git PR/CI-CD/GUS），用真实 WI 例子（W-23433231） | **采纳**：§0.2.1 新增 WI 端到端示意图 + 真实 WI 链接 + chatter 作状态持久化媒介的说明 + "一人并行多 WI"效益。 |
| 多加一期实战示例/截图打动领导层：sticky-note 人机界面 + 双击激活 WI-worker + job-scheduler 驱动采集 + watch-pr 状态采集 | **采纳**：§0.2.1 嵌入 4 张真实原型截图（`v3-sticky-note`/`v3-sticky-note-invoke`/`v3-job-scheduler`/`v3-watch-pr`）并逐张解读其在一期四层架构中的位置。 |

**Leadership reviewer V2（7.2/10，conditional-GO）**：

| 建议 | 优先级 | 处理 |
|---|---|---|
| 一次战略层裁决：编排层归属/是否与 Agentforce 重复投资（OQ-3 升级），署名结论+owner | **P0** | **采纳**：§0.4 闸门 A 明确列为投钱前阻塞项；§5 OQ-3 指派建议 owner（Agentforce/Platform editor + 本项目 owner）+ deadline（闸门 A 内）。此项须管理层签署，以 `[OPEN QUESTIONS]` 标注。 |
| 4 条试点成功判据写死为二期投入 gate | **P0** | **采纳**：§0.4 闸门 B 四条 gate（≥1.5× 吞吐 / 人工介入率下降 / 每-WI token 达标 / 付费意愿代理为正）。 |
| §0 加决策摘要卡 + 决策建议(conditional-GO)段落 | **P1** | **采纳**：§0.0 决策摘要卡 + §0.4 决策建议。 |
| OQ-1/2/4 补 owner + deadline | **P1** | **采纳**：§5 owner+deadline 表（作为 writer 建议，待管理层确认）。 |
| 付费意愿代理指标给具体口径与采集方式 | **P1** | **采纳**：§2c 三条可从审计轨迹客观算出的指标 + 采集方式。 |
| 一期交付物按"Agentforce 编排底座候选内核"设计 | **P2** | **采纳**：§0.4「为何与战略同向」+ §2d/§3a 埋点；交付物按可被 Agentforce 复用设计。 |
| 渗漏技术术语改业务语言 | **P2** | **采纳**：§1 术语脚注一次性业务语言对照。 |

**Product reviewer V2（7.2/10）**：

| 建议 | 优先级 | 处理 |
|---|---|---|
| 一期总月度 LLM token 账单合成区间（Sonnet/Opus 两档） | **P1** | **采纳**：§3a 给出 ≈$90–450/月（Sonnet）/ ≈$450–2,250/月（Opus）/ 保守数千美元上界，标注待 claude-api 核准。 |
| 落实 OQ-1 与 OQ-4 实际 owner + deadline | **P1** | **采纳**：§5 owner+deadline 表；OQ-1 列闸门 A 阻塞项。（实际签署待管理层，`[OPEN QUESTIONS]`。） |
| OQ-3 做权重敏感度分析 | **P2** | **采纳**：§2b 敏感度表，结论基本稳健。 |
| 二期蓝图补 Provider 化 + 客户现场适配增量成本 | **P2** | **采纳**：§3b 补 ≈8–14 人周粗估。 |
| 付费意愿代理指标升级为真实预算意向测试（二期） | **P2** | **采纳**：§2c 明确二期升级路径。 |
| （轻）编排器 ↔ Agentforce 生命周期/回调映射与 Data Cloud grounding | 远期 | **记录**：属远期落地才暴露的复杂度，见技术设计 §3 与 tech-design V3 回应；一期不展开。 |

> 说明：tech reviewer V2 的 P0/P1（护栏多实例状态共享、dedup TTL/watcher 快照依赖、热分区、adapter 契约、健康度面板线框、档位1 并发风险等）主要落在**技术设计文档 V3** 与 `工作流模版.md`，本可行性报告仅在 §0.0/§3a 同步 token 账单量级与健康度面板交付承诺。
