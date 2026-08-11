# Tech Review — V4

**总评分：8.7/10**（六项等权加权平均；0–10 制。换算百分制 = 87/100，较 V3 的 8.3 提升 +0.4，累计 V1 6.7 → V2 7.6 → V3 8.3 → V4 8.7）
**一句话结论：** 明确可行、设计成熟且收敛良好 —— V4 把我在 V3 提出的**每一条**开放项逐条闭环，且核心那条（在飞计数 crash-leak）**精确采纳了我建议的最优解**：弃用独立原子计数器、改由守护层从 `GSI2(affinity+progress)` `Count` 派生背压真值（真相从记录派生 → 天然 crash-safe），并显式标注「背压=软上限、非硬保证」。技术设计文档与 `工作流模版.md` 双向同步、无漂移。剩余扣分不再是「机制真空 / 二阶未收敛 / 三阶工程缺口」，而是**四阶实现期细节**（GSI2 自身的热分区、adapter 映射态持久化）与**非 writer 可解的外部阻塞项**（OQ-1 合规引依赖、OQ-2 matrix 身份、OQ-5 Agentforce 平台裁决）。无一票否决项。评审曲线已进入边际收敛区。

## 概述

评审对象为技术设计文档（`distributed-orchestrator-tech-design.md`，主）+ `工作流模版.md`（底层状态机/持久化/幂等/恢复，纳入主设计整体打分）+ 可行性报告（`distributed-orchestrator-project-analyst.md`，辅）。

**核对一致性**：本轮核心改动（在飞计数 crash-leak → GSI Count 派生、背压软上限）在**两份文档同步落地**——技术设计 §2.1「在飞计数的 crash-leak 回收」+ `工作流模版.md §4`「背压在飞计数的 crash-leak 回收（V4 补）」措辞与决策一致（弃用独立计数器 / GSI2 Count 派生 / 保留计数器+reconcile 为备选 / 背压软上限）。未出现"技术设计改了、底层模版没跟上"的漂移。

**V3→V4 回归评估（我方 V3 的全部开放项逐条）**：

| V3 我方遗留问题 | 优先级 | V4 处理 | 结论 |
|---|---|---|---|
| 共享在飞计数的 crash-leak 回收（`+1` 后 crash → 只增不减泄漏 → 假背压永久虚高） | **P1（V3 唯一真实新增工程缺口）** | §2.1 + `工作流模版.md §4`：**弃用独立原子计数器，改由守护层 `Query GSI2 where affinity=<pool> and progress=in-progress, Select=COUNT` 按 submitter 分片求和派生真值**；crash 任务 lease 过期后被守护层按「执行超时」重新计入/回收，派生计数自动收敛；保留「计数器+lease 过期驱动周期 reconcile（GSI Count 为事实源、计数器降为缓存）」为压测退路 | **已解决**（精确采纳我 V3 建议的最优解——真相从记录派生、天然 crash-safe） |
| 背压近似性未显式标注（分片计数最终一致 → 阈值判定有窗口误差） | **P2** | §2.1「背压是软上限、非硬保证」独立小节 + `工作流模版.md §4`：明确多实例并发认领下阈值判定是最终一致读、可能瞬时略超上限后收敛；需硬上限处（per-workspace token 预算）改用**单项记录 CAS 强一致约束**，不依赖聚合计数；下游不应把背压当精确闸门 | **已解决**（定位准确） |
| sentinel 输出契约对 LLM 复述 sentinel 字符串的鲁棒性 | **P2** | §2.4：静态哨兵升级为 **per-call nonce**（`<<<ORCH_OUTPUT_BEGIN:{nonce}>>>{json}<<<ORCH_OUTPUT_END:{nonce}>>>`），adapter 只认本次注入的 nonce + **取最后一对 nonce 匹配哨兵**；`--output-format json` 提为**主路径**、nonce 哨兵仅兜底 | **已解决**（两条建议全采纳） |
| 熔断 `GUARD#<dep>` 单项在故障风暴下的连续失败计数写热点 | 残留（未解决清单） | §2.1：对 `GUARD#<dep>` 再按**时间桶+实例分片**写（`GUARD#<dep>#<epochMinute>#<instanceShard>`）、读时聚合，把单点 CAS 打散；借鉴 resilience4j 滑动窗口（并正确指出其为单 JVM 内存态、分布式须自行落盘） | **已解决** |
| （远期）多租户复合键 `(tenantId, submitter)` 与 `INFLIGHT#<submitter>#<shard>` 分片键结构交互 | 未解决清单（远期） | §4「多租户复合键与分片键的交互」：显式连一句边界——多租户下 `INFLIGHT#<tenantId>#<submitter>#<shard>`、`workid#<branchShard>`、`GUARD#<dep>` 均需纳入 tenantId 维度，是 Provider PK 前缀扩展非重写 | **已解决**（正是我 V3 §6.2 要的「连一句边界」） |
| OQ-1 合规引依赖 / OQ-2 matrix 身份 | 非 writer 可解 | project-analyst §5 owner+deadline 表，OQ-1/OQ-3 列闸门 A 阻塞项 | **跟踪中**（外部依赖，非扣分项） |

**结论**：这是**连续第三次扎实迭代**，且是四轮里回归完成度最高的一轮——我 V3 列出的 6 条开放项中，5 条 writer 可解的**全部闭环**（含唯一 P1），且核心那条精确采纳建议解、而非"另找一个凑合方案"。V1 扣分是「机制真空」、V2 是「二阶正确性待收敛」、V3 是「三阶工程缺口」，V4 剩余的是「四阶实现期细节 + 外部阻塞」——评审曲线健康收敛，边际问题越来越薄。

> 说明：六视角由 team leader 按 `tech_reviewer_team.py` 定义统一应用与汇总（本环境未联网调用 Agno 运行时；各视角判据与该文件 instructions 一致）。分布式系统架构、SRE 两视角已把 `工作流模版.md §2/§4` 的状态机/持久化/护栏共享/dedup 时序/crash-leak 回收设计计入分项评分。

## 分项评审

### 1. 开源架构 — 8.5/10（V3: 8.5，持平）
- **判断**：本轮组件选型层无实质变化（合理——V3 已把档位 1/2、LangGraph 并发语义风险、License 结论说清）。§2.1 补的 resilience4j 滑动窗口借鉴 + 正确指出"其为单 JVM 内存态、分布式共享须自行落盘"是选型诚实度的延续。
- **残留问题 / 风险**：
  1. 组件 A 最终选型仍悬于 **OQ-1**（合规能否引 MIT LangGraph/DBOS）——外部阻塞项、非 writer 可解，已列闸门 A，是本视角封顶的唯一原因。
  2. 若档位 1 最终走"借鉴 subgraph 命名空间 + 自研 CAS lease"，与档位 2 边界会模糊，人周估计需在 OQ-1 落定后再收敛一次——属立项后细化，不在设计文档扣分。
- **建议 / 替代方案（附链接）**：维持现状。若 OQ-1 放行引依赖，仍建议优先评估 [Inngest](https://github.com/inngest/inngest)（step-level memoization + 事件驱动，SDK Apache-2）作"信号唤醒"模型的最贴近参考，其事件驱动 + step 记忆与本项目 signal/waiting 天然同构，可能比在 [LangGraph](https://langchain-ai.github.io/langgraph/concepts/persistence/) 上驯服 last-write-wins 并发模型代价更低。参考 [dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py)。

### 2. 分布式系统架构 — 9.0/10（V3: 8.5，+0.5）
- **改进**：V3 唯一真实新增工程缺口（在飞计数 crash-leak）已用**正确的分布式原语**闭环——把"独立可漂移的旁路计数器"回归为"记录的投影"（GSI2 Count 派生），这是 durable-execution 里"真相只有一个、其余皆派生"的正解。且**主动标注背压为软上限**、把硬约束（token 预算）留给单项 CAS 强一致——这条"软/硬约束分层"是分布式背压设计的教科书式正确。CAP 仍是干净的 CP（DynamoDB 条件写强一致），幂等/去重键三层齐备（workid 提交幂等 + dedup-key + 子分支确定性派生）。
- **残留问题 / 风险（均为四阶、一期可接受）**：
  1. **GSI2 自身的热分区（新暴露的四阶点）**：派生背压真值靠 `Query GSI2 where affinity=<pool> and progress=in-progress`——但 `affinity` 是**低基数** GSI 分区键（`cloud` / 少数 `machine:<id>`），意味着"所有 cloud 在飞任务"共享同一 GSI item collection：既是 Count 读的集中点，也是**每次 progress 状态转移都要维护 GSI 写**的集中点。这与 §1c 主表 `PK=workid` 热分区是**同构风险、只是搬到了 GSI 上**。文档提的"按 submitter 分片 Query"只降**读**量，不解 GSI 的**写**热点。一期步数/子分支上限可兜底（与 §1c 同源），但值得在 §1c 热分区小节里连一句"GSI2 同受此约束"。
  2. **GSI 读的最终一致性放大了软上限的必然性（正向印证，非缺陷）**：DynamoDB GSI **不支持强一致读**，故派生 Count 天然滞后（GSI 传播延迟 + 周期扫描）——这恰恰说明"背压必须是软上限"不只是一个选择、而是 GSI 机制下的**必然**。文档已正确标注软上限，若能补一句"GSI Count 本就无法强一致、故硬上限只能走单项 CAS"会让论证更闭环。
- **建议 / 替代方案（附链接）**：V5（或实现阶段）在 §1c 热分区表里把 GSI2 一并纳入"低基数分区键的读写热点"注记；若二期上分支级 PK 分片，GSI2 的分区键也应考虑加 submitter/shard 维度（`affinity#<shard>`）以分散写。参考 [DynamoDB GSI 最佳实践](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-indexes-general.html)（GSI 只支持最终一致读）、[write sharding](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-sharding.html)、[atomic counters 局限](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html#WorkingWithItems.AtomicCounters)。

### 3. SRE 容错 — 9.0/10（V3: 8.5，+0.5）
- **改进**：这个系统的**存在理由就是容忍 crash/关机**，而 V3 的背压计数器恰恰在 crash 下泄漏——V4 把这个"自相矛盾"的缺口彻底堵上：派生真值下，crash 的任务 lease 过期 → 守护层按「执行超时」重新计入/回收 → 派生计数**自动收敛**，无需额外对账进程。这是从"需要加一个 reconcile 兜底"升级为"根本不会漂移"。`GUARD#<dep>` 故障风暴写热点（我 V3 未解决清单第 4 条）也用时间桶+实例分片打散。half-open 挂守护层重扫周期、每周期只放行一个探测任务延续 V3。SPOF 分析清楚（引擎多实例无主非 SPOF，本机 daemon 单点由 liveness 改派兜底）。
- **残留问题 / 风险**：
  1. **GSI2 Count 的周期性扫描频率 vs 派生真值新鲜度的权衡**（四阶）：派生真值靠守护层"周期性 Count"，扫描间隔越长、背压反应越滞后（可能瞬时超上限更多）；越短、GSI 读成本越高。文档给了 reconcile 退路但未给扫描频率建议——属实现期调参（与 lease TTL/心跳间隔同类），不扣设计分，仅提示实现阶段需压测定频。
  2. 本机 daemon SPOF 已诚实标注、靠 liveness 改派兜底，可接受。
- **建议 / 替代方案（附链接）**：维持现状。实现阶段把"GSI2 Count 扫描周期"与"lease TTL / 心跳间隔"一起纳入压测调参清单；故障态短暂（cooldown 内转 half-open）使 GUARD 热点可接受。熔断计数窗口范式参考 [resilience4j](https://github.com/resilience4j/resilience4j)（分布式共享须自行落盘，文档已正确认识）。

### 4. 异构通信协议 — 9.0/10（V3: 8.5，+0.5）
- **改进**：两处显著进步。(a) **sentinel 契约防 LLM 复述**——我 V3 的 P2 建议（nonce + 取最后一对）被**完整采纳**：per-call nonce `<<<ORCH_OUTPUT_BEGIN:{nonce}>>>` + adapter 只认本次 nonce + 取最后一对匹配哨兵 + `--output-format json` 提为主路径。这把 `claude -p` stdout 解析的对抗性长尾（worker 在思考文本里复述哨兵）降到可忽略。(b) **AgentforceActionAdapter 契约 + 与非确定性 planner 共存**（§3，收敛为 OQ-5）——这是本轮**最有深度的架构洞察**：正面回答了"编排器靠 stateFingerprint+replay 假设『同一步骤可安全重放得等价结果』，但 Agentforce planner 是非确定性推理、session 不是可倒带状态机"这个真实的正确性冲突，解法是把 Action 当「至多一次触发 + 异步回调收敛」的**黑盒**、session 内部推理**不纳入 replay 校验**、两套状态模型在边界解耦。这是异构 agent 编排里少见的、把"两套并发/状态模型如何共存"讲透的设计。
- **残留问题 / 风险**：
  1. **`workid ↔ Agentforce session` 映射本身是须持久化的 durable 态**：契约说映射在 adapter 层维护为「workid → 最近一次触发的 session/execution id」——但这份映射本身就是状态，若 adapter 层重启丢失、或一个 workid 跨多次 Action 触发时映射更新的原子性，未展开。属契约草图级（一期不实现 Agentforce），可接受；实现阶段应把该映射落 StateStore 而非 adapter 内存态，并复用触发用的 dedup-key 保证至多一次。
  2. 云端 on-behalf-of 鉴权仍卡 **OQ-2**（外部依赖，非 writer 可解，但决定 A2AAdapter/云 adapter 能力边界），已跟踪。
- **建议 / 替代方案（附链接）**：维持现状；实现 AgentforceActionAdapter 时把 `workid↔session` 映射持久化到 StateStore、触发复用 dedup-key。参考 [Claude Code output formats](https://docs.claude.com/en/docs/claude-code)（结构化输出主路径）、[MCP 规范](https://modelcontextprotocol.io)、[A2A](https://github.com/google/A2A)、[Salesforce Platform Events](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/)。

### 5. 分布式 UX — 8.0/10（V3: 8.0，持平）
- **判断**：本轮 UX 层无新增设计工作（V3 的 `v3-health-panel` 两级钻取线框已达设计文档阶段要求），也无回归。progress→UI 映射表、两类最高频部分失败（关机停摆 / MCP 过期）的一键 Reconnect/改派闭环、非绿优先展开的信息密度策略均延续。此项持平是合理的——V4 的改动集中在分布式/SRE/异构/SF 四个视角，UX 不是本轮焦点。
- **残留问题 / 风险**：
  1. "20 个 workspace × 每树数十分支"的二级视图在极端 fan-out 下的**滚动/折叠/搜索/定位**交互仍未展开（如何一屏内定位到那个红色分支）——属实现细节，不扣设计分。
  2. sticky-note 仅 macOS 桌面（已诚实标注，商业化跨端留后续，可接受）。
- **建议 / 替代方案（附链接）**：维持现状。二级树视图的大规模 fan-out 呈现实现阶段可借鉴 [Temporal Web UI](https://docs.temporal.io/web-ui) 对 workflow/child-workflow 树形状态的"父折叠、异常子高亮上浮"信息密度范式。

### 6. Salesforce 产品 — 8.5/10（V3: 8.0，+0.5）
- **改进**：我 V3 的两条 SF 残留全部闭环，且加了实质设计：(a) **多租户复合键 × 分片键交互**（§4）——正是我 V3 §6.2 要的"连一句边界"，明确 `(tenantId, submitter)` 下 `INFLIGHT`/`workid#branchShard`/`GUARD` 分片键均纳入 tenantId 维度、是 Provider PK 前缀扩展非重写；(b) **AgentforceActionAdapter 非确定性 planner 共存契约**（§3，见视角 4）把"编排底座候选内核"从断言推进为可裁决的技术契约；(c) 新增 **Data Cloud zero-copy / Prompt Builder 集成方向草图** + stateFingerprint 扩校验 Prompt 模板版本（解"prompt 改了、code 没改"的隐性非确定性）；(d) §4 **dirty org 冒烟**（Scratch Org + 预装含触发器/Flow 的 AppExchange 包）升级、排入二期 FDE 培训前——比 V3 的"干净 org 冒烟"更能暴露与客户既有自动化的冲突面。Flow Orchestrator 互补+桥接、Einstein Trust Layer 商业化前置门槛、Hyperforce 前瞻定位诚实。
- **残留问题 / 风险**：
  1. Agentforce/Flow 技术桥仍是**接口草图级**（一期不实现，合理，已升级为 OQ-5 交平台架构团队裁决）；Platform Event 回调本编排器时会撞 CRUD/FLS/共享模型——V2/V3 已点名、V4 仍留远期，一期不触客户数据不进 Platform，可接受。
  2. 三个桥接点的平台约束（Platform Event 发布频率上限、Flow invocable 同步时限、Agentforce Action 会话超时）为**占位待核准**——正确处理（与 token 账单"待核准"对称），但意味着 OQ-5 裁决前技术桥的可行性仍有平台侧未知数。
- **建议 / 替代方案（附链接）**：保持现有诚实定位。参考 [Flow Orchestrator 文档](https://help.salesforce.com/s/articleView?id=sf.flow_concepts_orchestrator.htm)、[Platform Events 限制](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_intro.htm)、[Einstein Trust Layer](https://www.salesforce.com/products/platform/trusted-ai/)、[Data Cloud zero-copy](https://help.salesforce.com/s/articleView?id=sf.c360_a_zero_copy_data_federation.htm)。

## 关键建议（按优先级）
1. **[P2，视角 2] GSI2 派生背压的自身热分区**——派生真值靠 `affinity`（低基数）GSI 分区键的 item-collection Query，"所有 cloud 在飞任务"集中在单一 GSI 分区，是 §1c 主表热分区的同构风险搬到 GSI 上；submitter 分片只降读、不解 GSI 写热点。建议在 §1c 热分区小节连一句"GSI2 同受步数/子分支上限约束"，二期分片时 GSI 分区键考虑加 `affinity#<shard>` 维度。
2. **[P2，视角 2] 补一句 GSI 无强一致读 → 软上限的必然性**——当前软上限是"选择"的论证，可加"GSI Count 本就无法强一致，故硬上限只能走单项 CAS"，让软/硬约束分层的论证完全闭环。
3. **[P3，视角 4] AgentforceActionAdapter 的 `workid↔session` 映射落 StateStore**——实现阶段该映射应持久化（非 adapter 内存态）、触发复用 dedup-key 保证至多一次；契约草图阶段可先连一句。
4. **[P3，视角 3] GSI2 Count 扫描周期纳入压测调参**——扫描间隔 vs 背压新鲜度/GSI 读成本的权衡，与 lease TTL/心跳间隔同类，实现阶段定频。
5. **[跟踪，非 writer 可解] OQ-1 / OQ-2 / OQ-5 尽快落 owner+deadline**——OQ-1（合规引依赖）决定档位 1/2 与 token 账单、封顶开源架构视角；OQ-2（matrix 身份 a/b）决定云 adapter 能力边界；OQ-5（Agentforce 平台裁决）决定"编排底座候选内核"战略卖点的技术可行性。均已列闸门，建议 kickoff 即指派。

## 未解决 / 待 writer 回应的问题
- [ ] （四阶）GSI2 派生背压真值查询自身的热分区：低基数 `affinity` 分区键使"cloud 在飞任务"集中在单一 GSI item collection，Count 读 + 每次 progress 转移的 GSI 写都集中；建议在 §1c 连一句同构约束。
- [ ] （论证完整性）显式补"GSI 只支持最终一致读 → 背压硬上限只能靠单项 CAS"，把软/硬约束分层论证闭环。
- [ ] （实现期）AgentforceActionAdapter 的 `workid↔session` 映射应落 StateStore 而非 adapter 内存态，跨多次触发的映射更新原子性。
- [ ] （实现期）GSI2 Count 扫描周期 vs 背压新鲜度/成本的调参，纳入压测清单。
- [ ] （非 writer 可解，跟踪）OQ-1 合规引依赖、OQ-2 matrix 身份 (a)/(b)、OQ-5 Agentforce 平台裁决——决定档位、云 adapter 能力边界与战略卖点可行性，建议尽快指定 owner+deadline。
