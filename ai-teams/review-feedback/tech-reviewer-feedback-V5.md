# Tech Review — V5

**总评分：8.8/10**（六项等权加权平均；0–10 制。换算百分制 = 88/100，较 V4 的 8.7 微升 +0.1，累计 V1 6.7 → V2 7.6 → V3 8.3 → V4 8.7 → V5 8.8）
**一句话结论：** 明确可行、设计成熟、进入边际收敛区 —— V5 把我在 V4 提出的**全部 4 条 writer 可解开放项（均 P2/P3）逐条精确闭环**，并新增两块**有一手内部依据、置信度诚实标注**的实操性内容（§1e 云表写入鉴权/数据安全/provision 路径、组件 B Matrix 专项调研）。其中 §1e 把「谁授权本机写云端单一事实源、如何防误删这张表」这个**此前隐性的运维/数据安全空白**补成了以真实 TCM RCA 为依据的一等公民设计，实质抬高了 SRE 视角的天花板。剩余问题全为**实现期运维细节**（PCSK 凭据过期对本机恢复主体的 blast radius、PCSK 逐人 onboarding provision 摩擦、append-only 与 dedup 原生 TTL 的措辞澄清）与**非 writer 可解的外部阻塞项**（OQ-1 合规引依赖、OQ-2 matrix 身份代持、OQ-5 Agentforce 平台裁决）。无一票否决项，无 P0/P1。

## 概述

评审对象为技术设计文档（`distributed-orchestrator-tech-design.md`，主）+ `工作流模版.md`（底层状态机/持久化/幂等/恢复，纳入主设计整体打分）+ 可行性报告（`distributed-orchestrator-project-analyst.md`，辅）。

**核对一致性**：本轮 §1e 的数据安全/持久化约束（`prevent_destroy` / 每工作负载最小权限 / append-only 软删 / PCSK 凭据过期「告警不硬跑」）已**同步落 `工作流模版.md` 新增末节「数据安全与持久化写入约束（V5）」**，措辞与技术设计 §1e 一致（含 SQLite/DynamoDB 双后端约束：恢复/幂等不得依赖 DynamoDB 特有语义之外的东西，GSI 派生背压真值在 SQLite 侧用等价索引查询替代）。未出现「技术设计改了、底层模版没跟上」的漂移。

**V4→V5 回归评估（我方 V4 的全部开放项逐条）**：

| V4 我方遗留问题 | 优先级 | V5 处理 | 结论 |
|---|---|---|---|
| GSI2 派生背压真值查询自身的热分区（`affinity` 低基数 GSI 分区键使"cloud 在飞任务"集中在单一 GSI item collection，Count 读 + 每次 progress 转移的 GSI 写都集中，是主表 `PK=workid` 热分区的同构风险搬到 GSI 上） | **P2** | §1c 新增独立段落「GSI2 派生背压真值查询自身的热分区（V5）」：明确低基数 `affinity` 的读写双热点、与主表同构；一期步数上限同样约束 GSI2 写量、二期分片时 GSI 分区键加 `affinity#<shard>`；结论行改为"主表与 GSI2 同受此约束" | **已解决**（正是我 V4 建议的"在 §1c 连一句同构约束 + 二期加 shard 维度"） |
| 补"GSI 无强一致读 → 软上限必然性"使软/硬约束分层论证闭环 | **P2** | §2.1 新增引用块「软上限不只是「选择」，而是 GSI 机制下的「必然」（V5）」：GSI 本就不支持强一致读 → 派生 Count 天然滞后 → 背压软上限是必然非选择；反过来硬上限（token 预算）只能走单项记录 CAS | **已解决**（论证完全闭环，定位准确） |
| AgentforceActionAdapter 的 `workid↔session` 映射应落 StateStore（非 adapter 内存态）+ 跨多次触发映射更新原子性 | **P3** | §3 新增「该映射本身是须持久化的 durable 态（V5）」：映射落 StateStore、更新走单项 CAS、Action 触发 dedup-key=`workid#stepIndex#actionName` 保至多一次，与 §2.2 signal dedup 同一套幂等原语 | **已解决**（我 V4 的两条建议全采纳） |
| GSI2 Count 扫描周期纳入压测调参 | **P3** | §2.1 新增「GSI2 Count 扫描周期纳入压测调参（V5）」：`{GSI2 Count 扫描周期, lease TTL, 心跳间隔, dedup 表 TTL}` 一并列入压测调参清单，用"背压新鲜度 vs GSI 读成本"实测曲线选点 | **已解决**（与 lease TTL/心跳间隔同类调参，正确处理） |
| OQ-1 合规引依赖 / OQ-2 matrix 身份 / OQ-5 Agentforce 平台裁决 | 非 writer 可解 | project-analyst §5 owner+deadline 表；OQ-2 经 Matrix 调研从"待确认"升级为"有明确疑点待确认" | **跟踪中**（外部依赖，非扣分项；OQ-2 依据更充分了） |

**结论**：这是**连续第四次扎实迭代**。V4 剩余的全是「四阶实现期细节 + 外部阻塞」，V5 把其中 4 条 writer 可解的**全部闭环**，并把两条最重要的 human comment（DynamoDB 写入鉴权/数据安全、Matrix 成熟度调研）落成有一手依据、置信度诚实标注的设计。评审曲线继续健康收敛——本轮我能新提的问题已薄到「运维 provision 摩擦」与「措辞澄清」层级，且核心亮点（§1e 数据安全）反而是**主动补齐了一个我此前未点名、但一个真要 ship 的系统绕不开的空白**。

> 说明：六视角由 team leader 按 `tech_reviewer_team.py` 定义统一应用与汇总（本环境未联网调用 Agno 运行时；各视角判据与该文件 instructions 一致）。分布式系统架构、SRE 两视角已把 `工作流模版.md §2/§4/末节` 的状态机/持久化/护栏共享/dedup 时序/crash-leak 回收/数据安全约束计入分项评分。

## 分项评审

### 1. 开源架构 — 8.5/10（V4: 8.5，持平）
- **判断**：组件 A（持久化内核）选型层无实质变化，合理。本轮亮点在组件 B 的 **Matrix build-vs-reuse 尽职调研**——文档正面评估了「是否复用 Matrix 的 Temporal 持久化层」，并诚实得出「不假定 Matrix 提供通用云端存储、一期仍以自有 DynamoDB 单表为单一事实源」的结论，这是对"重复造轮子 vs 复用平台"的健康克制（不盲目自建、也不盲目依赖未证明的平台能力）。§1e 引入的 PCSK / Falcon addon 均为公司内部机制，与 §4「内部专属需换 Provider」的边界一致，不污染可外带 IP 内核。
- **残留问题 / 风险**：
  1. 组件 A 最终选型仍悬于 **OQ-1**（合规能否引 MIT LangGraph/DBOS）——外部阻塞项、非 writer 可解，已列闸门 A，是本视角封顶的唯一原因。
  2. Matrix 调研为**二手（作者源码级审阅、本轮未重核）**，仓库/wiki 在 SAML 墙后不可达——文档已显式标注置信度，实施前须由 Matrix 团队一手确认，非扣分项但需 kickoff 跟进。
- **建议 / 替代方案（附链接）**：维持现状。若 OQ-1 放行引依赖，仍建议优先评估 [Inngest](https://github.com/inngest/inngest)（step-level memoization + 事件驱动、SDK Apache-2）作"信号唤醒"模型最贴近参考，其事件驱动 + step 记忆与本项目 signal/waiting 天然同构。参考 [LangGraph persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)、[dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py)。

### 2. 分布式系统架构 — 9.1/10（V4: 9.0，+0.1）
- **改进**：我 V4 的两条 P2 全部精确闭环——(a) GSI2 派生背压的**自身热分区**在 §1c 连成同构约束（低基数 `affinity` 的读写双热点 = 主表 `PK=workid` 热分区搬到 GSI 上），二期分片方案加 `affinity#<shard>` 维度；(b) **软上限的必然性论证闭环**——从「GSI 不支持强一致读」推出「背压软上限是机制必然、非主观选择」，并反向锁定「硬上限只能走单项记录 CAS」。软/硬约束分层至此论证完整。此外 `工作流模版.md` 末节新增的 **SQLite/DynamoDB 双后端约束**（恢复/幂等不得依赖 DynamoDB 特有语义之外的东西、GSI 派生背压在 SQLite 侧用等价索引查询替代）是一条正确的抽象层不变式——它保证 StateStore 接口的两种实现语义一致，是"本机/云端统一编排"成立的隐性前提，此前未显式写出。CAP 仍是干净的 CP，幂等/去重键三层齐备。
- **残留问题 / 风险（均为实现期运维、一期可接受）**：
  1. **PCSK 时间盒凭据过期对本机恢复主体的 blast radius（新暴露）**：D1 把**本机 daemon 定为恢复主体**，它写云端 StateStore 依赖 §1e 路径 A 的 PCSK 短时凭据；PCSK 是时间盒的（旁证「31 天」+ 周期重新申报）。文档正确地把其过期归入「告警不硬跑、人续期」，与 MCP OAuth 过期同一原则——但两者**爆炸半径不同**：单个 MCP OAuth 过期只让**一类 worker** 停摆，而 PCSK 云表写凭据过期会让该机**所有 workspace 的 checkpoint/推进全部停摆**（无法写单一事实源）。建议在 §1e 或 §2.6 连一句区分这两级过期的影响面（"连接级过期 = 单 worker 停" vs "云写凭据级过期 = 该机全线停"），并把云写凭据过期纳入 §2.6 健康度面板的"需 Reconnect/续期"高亮类目。
  2. **append-only 软删 vs dedup 原生 TTL 的措辞张力（澄清级）**：§1e / `工作流模版.md` 强调"append-only、人类不得直接 delete、物理删除权限收归运维"，而 §2.2 的 dedup 存储明确靠 **DynamoDB 原生 TTL 物理清理**。二者不冲突（TTL 是系统驱动、非人为，且 dedup 项本就是瞬态），但两处措辞相邻易被误读为矛盾——建议加一句"瞬态项（dedup/lease 旁路）的系统 TTL 过期 ≠ 被禁止的人为删除 append-only 状态历史"，消除表面张力。
- **建议 / 替代方案（附链接）**：维持现状。参考 [DynamoDB GSI 最佳实践](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-indexes-general.html)（GSI 只支持最终一致读）、[write sharding](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-sharding.html)、[TTL 语义](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)。

### 3. SRE 容错 — 9.2/10（V4: 9.0，+0.2）
- **改进**：本轮 SRE 视角实质受益最大。§1e **数据安全**把一个此前隐性的空白补成一等公民设计——「本机单一事实源这张表被误删 = 全量停摆」这个 SPOF/数据丢失风险，V5 用**真实 TCM RCA**（`falcon addons tidy --all` 误删 tier-1 表 `userManagementWorkArea` → dev/perf/test/stage 全线故障）为依据，给出 `prevent_destroy` + apply 前人工审阅 plan + 每工作负载最小权限（worker IAM 只授自己 submitter 分区、无 `DeleteTable`/全表 `DeleteItem`）+ append-only 软删 + CloudTrail 归因 + **恢复代价已知**（手动恢复致 Terraform state 失配 `ResourceInUseException`、需 Spinnaker import pipeline 重 import）的完整"重预防轻恢复"闭环。这正是教科书式的 SRE/灾备思维（以真实事故为依据、量化恢复代价、把破坏性权限从数据面剥离）。同时我 V4 的 GSI2 Count 扫描周期调参（P3）已纳入压测清单。SPOF 分析仍清楚（引擎多实例无主非 SPOF、本机 daemon 单点由 liveness 改派兜底）。
- **残留问题 / 风险**：
  1. **PCSK 逐人 onboarding provision 摩擦（新，运维成本）**：3–5 人试点每人都需向共享编排 AWS 账户申请 PCSK 访问 + 审批 + per-submitter IAM 分区授权 + 周期重新申报——这是一笔真实（虽小）的 onboarding/运维 toil，当前未计入 project-analyst §3a(4) 的运维隐藏成本（0.2–0.5 人力）或 M1–M4。建议在运维成本处连一句"PCSK 逐人申报/续期 toil"，避免试点扩人时被 provision 摩擦拖慢。
  2. PCSK 云写凭据过期是**新的一类停摆故障**（见视角 2 残留 1），须纳入健康度面板与值班 runbook——属实现期。
  3. 本机 daemon SPOF 已诚实标注、靠 liveness 改派兜底，可接受。
- **建议 / 替代方案（附链接）**：维持现状。实现阶段把 PCSK 续期 toil + 云写凭据过期告警纳入 §2.6 面板与运维 runbook；`prevent_destroy` 范式参考 [Terraform lifecycle](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)、DynamoDB 灾备参考 [point-in-time recovery](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery.html)（可作为 append-only 软删之外的第二层兜底，值得在 §1e 提一句 PITR 是否开启）。

### 4. 异构通信协议 — 9.0/10（V4: 9.0，持平）
- **改进**：两处受益。(a) 我 V4 的 P3（AgentforceActionAdapter 的 `workid↔session` 映射落 StateStore）已闭环——映射持久化到 StateStore、CAS 更新、触发 dedup-key=`workid#stepIndex#actionName` 复用 §2.2 幂等原语，把"两套状态模型边界解耦"的契约补完整。(b) **Matrix 鉴权专项调研**直接强化本视角——澄清了 Matrix 的强身份是 **MAS 签发短时 ES256 JWT + SPIFFE 证书授权签名（私钥不出 Falcon KMS、`jti` 防重放）**、`mas:caller` 三模式（u2s/s2s/internal），但**外部 org（GUS/Google）代持是公开缺口**（委托 MCP Gateway、未证明）→ 直接把 OQ-2 从"待确认"升级为"有明确疑点待确认"。这是异构鉴权边界的诚实澄清：Matrix 强在内部 s2s，我们要的"云端 worker 以开发者身份操作外部 SF org"未被证明，不再是模糊假设。
- **残留问题 / 风险**：
  1. 云端 on-behalf-of 鉴权仍卡 **OQ-2**（外部依赖、非 writer 可解，决定 A2AAdapter/云 adapter 能力边界）——但本轮调研已把它从"盲目工作假设 (b)"收窄为"有具体疑点的待确认项"，是进步。已跟踪。
  2. Matrix 15 分钟心跳调度粒度与常驻 watcher 模型的适配（"常驻监听留本机 / worker 执行 offload 到 Matrix"）已给方向，实施期需验证该适配层不会引入亚 15 分钟节拍类 watcher 的漏触发——属实现期。
- **建议 / 替代方案（附链接）**：维持现状。实现 AgentforceActionAdapter 时按契约落 StateStore + dedup-key。参考 [Claude Code output formats](https://docs.claude.com/en/docs/claude-code)、[MCP 规范](https://modelcontextprotocol.io)、[A2A](https://github.com/google/A2A)、[SPIFFE](https://spiffe.io/)、[Salesforce Platform Events](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/)。

### 5. 分布式 UX — 8.0/10（V4: 8.0，持平）
- **判断**：本轮 UX 层无新增设计工作（合理——V5 焦点在鉴权/数据安全/持久化四视角），也无回归。V3 的 `v3-health-panel` 两级钻取线框、progress→UI 映射、两类最高频部分失败（关机停摆 / MCP 过期）的一键 Reconnect/改派闭环、非绿优先展开的信息密度策略均延续。
- **残留问题 / 风险**：
  1. §1e 新引入的 **PCSK 云写凭据过期**是一类新的"需人续期"高频情形（见视角 2/3），但**尚未反映到 §2.6 的 progress→UI 映射表**（当前表只有"MCP OAuth 过期"一行）。建议 V6 在映射表加一行"云写凭据过期 → 该机全线停、需续期"，与 MCP 过期区分影响面——这是 UX 侧一处可直接补齐的小缺口。
  2. "20 workspace × 每树数十分支"的二级视图在极端 fan-out 下的滚动/折叠/搜索/定位交互仍未展开；sticky-note 仅 macOS（均已诚实标注，可接受）。
- **建议 / 替代方案（附链接）**：V6 把"云写凭据过期"补进 §2.6 映射表。大规模 fan-out 树呈现实现阶段可借鉴 [Temporal Web UI](https://docs.temporal.io/web-ui) 的"父折叠、异常子高亮上浮"信息密度范式。

### 6. Salesforce 产品 — 8.5/10（V4: 8.5，持平）
- **判断**：本轮无新增 SF 产品耦合设计（§1e 是基础设施层、Matrix 是托管依赖调研），V4 的成果（多租户复合键×分片键交互、AgentforceActionAdapter 非确定性 planner 共存契约、Data Cloud zero-copy / Prompt Builder 方向、dirty org 冒烟）均延续、无回归。§1e 的服务身份路径 B 具名先例（`sales-growth-bot@gus.com` 在 Falcon 走 JWT Bearer + Vault）间接印证了"云端 worker 以服务账号身份操作 SF 内部系统"的现实可行，与 OQ-2 假设 (a) 退路咬合。
- **残留问题 / 风险**：
  1. Agentforce/Flow 技术桥仍是**接口草图级**（一期不实现，已升级 OQ-5 交平台架构团队裁决）；三个桥接点平台约束（Platform Event 发布频率、Flow invocable 同步时限、Agentforce Action 会话超时）为占位待核准——正确处理，但 OQ-5 裁决前技术桥可行性仍有平台侧未知数。
  2. 一期不触客户数据、不进 Platform，Einstein Trust Layer / Hyperforce 多租户为商业化前置门槛——诚实定位，可接受。
- **建议 / 替代方案（附链接）**：保持现有诚实定位。参考 [Flow Orchestrator 文档](https://help.salesforce.com/s/articleView?id=sf.flow_concepts_orchestrator.htm)、[Platform Events 限制](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_intro.htm)、[Einstein Trust Layer](https://www.salesforce.com/products/platform/trusted-ai/)、[Data Cloud zero-copy](https://help.salesforce.com/s/articleView?id=sf.c360_a_zero_copy_data_federation.htm)。

## 关键建议（按优先级）
1. **[P3，视角 2/3] 区分两级凭据过期的影响面**——PCSK 云表写凭据过期会让该机**全线**停摆（无法写单一事实源），比单个 MCP OAuth 过期（单 worker 停）blast radius 大。建议在 §1e/§2.6 连一句区分，并把"云写凭据过期"补进 §2.6 progress→UI 映射表（新增一行、与 MCP 过期区分）。
2. **[P3，视角 3] PCSK 逐人 onboarding provision 摩擦入运维成本**——试点每人需 PCSK 账户访问申报 + per-submitter IAM 授权 + 周期续报，当前未计入 project-analyst §3a(4) 运维隐藏成本；连一句避免扩人时被 provision 摩擦拖慢。
3. **[P3，视角 2] append-only 软删 vs dedup 原生 TTL 措辞澄清**——加一句"瞬态项系统 TTL 过期 ≠ 被禁止的人为删除 append-only 历史"，消除 §1e 与 §2.2 相邻措辞的表面张力。
4. **[P4，视角 3，增强] §1e 提一句 DynamoDB PITR 是否开启**——作为 `prevent_destroy` + append-only 软删之外的第二层灾备兜底（point-in-time recovery），让"单一事实源误损"的恢复故事更完整。
5. **[跟踪，非 writer 可解] OQ-1 / OQ-2 / OQ-5 尽快落 owner+deadline**——OQ-1 决定档位 1/2 与 token 账单、封顶开源架构视角；OQ-2（经 Matrix 调研已升级为"有明确疑点"）决定云 adapter 能力边界；OQ-5 决定"编排底座候选内核"战略卖点可行性。均已列闸门，建议 kickoff 即指派。

## 未解决 / 待 writer 回应的问题
- [ ] （实现期，视角 2/3）区分 PCSK 云写凭据过期（该机全线停）vs MCP OAuth 过期（单 worker 停）的 blast radius，并把前者补进 §2.6 progress→UI 映射表。
- [ ] （运维成本，视角 3）PCSK 逐人 onboarding/续期 provision 摩擦纳入 project-analyst §3a(4) 运维隐藏成本。
- [ ] （措辞澄清，视角 2）§1e append-only「人类不得直接 delete」与 §2.2 dedup 原生 TTL 物理清理的表面张力，加一句系统 TTL ≠ 人为删除。
- [ ] （增强，视角 3）§1e 补一句 DynamoDB PITR 是否作为第二层灾备。
- [ ] （非 writer 可解，跟踪）OQ-1 合规引依赖、OQ-2 matrix 身份代持（已升级为"有明确疑点待确认"）、OQ-5 Agentforce 平台裁决——决定档位、云 adapter 能力边界与战略卖点可行性，建议尽快指定 owner+deadline。
