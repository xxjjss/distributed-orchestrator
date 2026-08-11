# Tech Review — V3

**总评分：8.3/10**（六项等权加权平均；0–10 制。换算百分制 = 83/100，较 V2 的 7.6 提升 +0.7，较 V1 的 6.7 累计 +1.6）
**一句话结论：** 明确可行、设计已成熟 —— V3 把 V2 指出的**分布式二阶正确性**问题（多实例护栏状态共享、dedup TTL vs 重放窗口、watcher 快照依赖链、热分区、adapter 契约、健康度面板线框、档位 1 并发语义风险）**逐条从「断言/清单」补成了「机制/契约/线框」**，且技术设计文档与 `工作流模版.md` 双向同步落地。剩余扣分不再是「机制真空」或「二阶未收敛」，而是**更细的三阶工程细节**（共享在飞计数的 crash-leak 回收、近似背压的最终一致性）与**非 writer 可解的外部阻塞项**（OQ-1 合规引依赖、OQ-2 matrix 身份）。无一票否决项。

## 概述

评审对象为技术设计文档（`distributed-orchestrator-tech-design.md`，主）+ `工作流模版.md`（底层状态机/持久化/幂等/恢复，纳入主设计整体打分）+ 可行性报告（`distributed-orchestrator-project-analyst.md`，辅）。`工作流模版.md` §4 已同步落地护栏共享与 dedup 时序约束、§2 已同步热分区约束——两文一致，未出现"技术设计改了、底层模版没跟上"的漂移。

**V2→V3 回归评估（我方 V2 的 P0/P1 + 未解决清单逐条）**：

| V2 遗留问题 | 优先级 | V3 处理 | 结论 |
|---|---|---|---|
| 多实例引擎下熔断/背压/令牌桶状态共享（护栏被实例数放大失效） | **P0** | §2.1 新增护栏共享落盘表：熔断状态项（`PK=GUARD#<dep>` + CAS）、在飞计数（`PK=INFLIGHT#<submitter>#<shard>` + 原子 ADD）、令牌桶（per-dep）；本地配额退路；同步落 `工作流模版.md §4` | **已解决**（残留：在飞计数的 crash-leak 回收未言明，见分项 3） |
| dedup 表 TTL vs 事件重放窗口时序约束 | **P0/P1** | §2.2 给出硬约束 `dedup_TTL > max_replay_window`（含 watcher 恢复 + SQS 重投 + 时钟余量），一期取 7d，原生 TTL 清理；SQS 保留调大须同步调大 dedup_TTL | **已解决** |
| watcher 快照持久化与 dedup-key 确定性依赖链 | **P0/P1** | §2.2 显式画出依赖链：快照持久化（本机 SQLite + 云端备份）+ 跃迁标识优先取事件自带稳定标识（PR `merge_commit_sha`、GUS `LastModifiedDate`+状态值） | **已解决**（跃迁标识优先无状态可重建的思路正确，是最优解） |
| 单 `PK=workid` 全树吞吐热分区（V1 遗留） | **P0/P1** | §1c 一期步数/子分支上限规避（与 token 预算护栏同源）+ 二期分支级 PK 分片 `workid#<branchShard>` + CloudWatch 分区级热点监控；同步落 `工作流模版.md §2` | **已解决** |
| 改派 `machine:X → cloud` 目标端是否具备 handler | 残留 | §2.3 改派前校验目标端 handler 注册表 + 鉴权可达性，候选只列"确实能跑"的位置，缺则置灰说明原因 | **已解决** |
| adapter 契约停在清单级 | **P1** | §2.4 ClaudeCodeAdapter sentinel 包裹契约（`<<<ORCH_OUTPUT_BEGIN>>>…`）+ 优先 `--output-format json` + 解析失败=显式 `error(retryable)` + 进度回传 `<<<ORCH_PROGRESS>>>`；StepFunctionsAdapter SFN 执行态→progress 映射表（含 retryable 由错误类型判定） | **已解决**（从"能列出"升级到"能定契约"，达标） |
| 跨大模型（Claude/GPT/Gemini）调用转换与归一 | **P1** | §2.4 明确标注为**二期已知边界**，一期只覆盖 Claude Code/opencode 同族语义 | **已解决**（标注边界即达标要求） |
| 熔断 open 任务的 half-open 重探测挂守护层重扫周期 | 残留 | §2.1 明确挂重扫周期，到 cooldown 置 half-open **只放行一个探测任务**，成功→closed、失败→回 open 重新计时 | **已解决** |
| UX：健康度面板线框 + fan-out 树形部分态 | **P1** | §2.6 新增 `v3-health-panel` 两级钻取线框（一级健康度汇总条+非绿优先展开；二级钻取单树分支部分态） | **已解决** |
| 档位 1 LangGraph last-write-wins 上叠加 CAS lease 的并发语义风险 | **P1** | §1d 注记：LangGraph 官方承认"最后写赢/无锁/副作用不去重"，与 CAS lease 是两套并发模型可能打架，6–10 人周偏乐观，更可能落"借鉴 subgraph 命名空间+自研 CAS lease"；DBOS 的 Postgres 栈冲突 | **已解决**（风险坦白，扣分转正） |
| StateStore 多租户返工面 + Platform Event→signal 租户上下文 | **P2** | §3 补：per-submitter→per-tenant 是 Provider 扩展非重写（返工集中在实现层）；envelope 预留 tenantId，signal 落库按 `(tenantId, submitter)` 复合键分区 | **已解决** |
| OQ-1 合规引依赖 / OQ-2 matrix 身份 | 非 writer 可解 | project-analyst §5 owner+deadline 表，OQ-1 列闸门 A 阻塞项 | **跟踪中**（外部依赖，非扣分项） |

整体判断：这是**连续第二次扎实迭代**——writer 没有用"已采纳"搪塞，每条都落到具体机制（共享护栏表的 PK 结构 + CAS/ADD 语义）、具体约束（`dedup_TTL > max_replay_window` 不等式）、具体契约（sentinel 包裹 + SFN 状态映射表）、具体线框（`v3-health-panel` 两级钻取）。V1 的扣分是"机制真空"，V2 是"二阶正确性待收敛"，V3 剩余的是"三阶工程细节 + 外部阻塞"——评审曲线在健康收敛。

> 说明：六视角由 team leader 按 `tech_reviewer_team.py` 定义统一应用与汇总（本环境未联网调用 Agno 运行时；各视角判据与该文件 instructions 一致）。分布式系统架构、SRE 两视角已把 `工作流模版.md §2/§4` 的状态机/持久化/护栏共享/dedup 时序设计计入分项评分。

## 分项评审

### 1. 开源架构 — 8.5/10（V2: 8.0，+0.5）
- **改进**：§1d 补上了我 V2 要的**档位 1 隐藏集成风险注记**——LangGraph 官方承认其 checkpointer 是"最后写赢、无并发锁、副作用不去重"，与我们要叠加的 lease+CAS「恰好一个 runner」是**两套并发模型**，直接坦白"6–10 人周若含驯服 LangGraph 并发模型则偏乐观，更可能落在借鉴 subgraph 命名空间 + 自研 CAS lease 层"，并点名 DBOS 的 Postgres 栈与公司 DynamoDB 栈冲突。这是把风险从"隐藏"变"显式"，正是选型诚实度的加分项。候选表 License 结论（LangGraph/DBOS MIT 可商用、Restate BSL、Windmill AGPL 须法务）清晰。
- **残留问题 / 风险**：
  1. 组件 A 的最终选型仍**悬于 OQ-1**（合规能否引 MIT 依赖），这是外部阻塞项、非 writer 可解，已列闸门 A，可接受。
  2. 档位 1 若最终走"借鉴 subgraph 命名空间 + 自研 CAS lease"，则它与档位 2（全自研内核）的边界会模糊——两档的人周估计可能需要在 OQ-1 落定后再收敛一次，但这属立项后细化，不在设计文档扣分。
- **建议 / 替代方案（附链接）**：维持现状即可。若 OQ-1 放行引依赖，评估 [Inngest](https://github.com/inngest/inngest)（step-level memoization + 事件驱动，SDK Apache-2）作为"信号唤醒"模型的最贴近参考，其事件驱动 + step 记忆与本项目 signal/waiting 模型天然同构，可能比在 LangGraph 上驯服并发模型代价更低。参考 [LangGraph persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)、[dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py)。

### 2. 分布式系统架构 — 8.5/10（V2: 8.0，+0.5）
- **改进**：我 V2 的三个 P0/P1 残留全部收敛且机制正确——(a) **dedup TTL 时序约束**落成硬不等式 `dedup_TTL > max_replay_window`（= watcher 恢复 + 传输重投 + 时钟余量），一期 7d 覆盖 SQS 默认 4d 保留，且明确"SQS 保留调 14d 须同步调 dedup_TTL"，DynamoDB 原生 TTL 清理零运维；(b) **watcher 快照依赖链**显式画出，且**跃迁标识优先取事件自带稳定标识**（`merge_commit_sha`/`LastModifiedDate`+状态值）而非 watcher 内部快照序号——这是最优解，把对可变快照的依赖降到最低，快照持久化仅作兜底；(c) **热分区**一期步数/子分支上限规避 + 二期分支级 PK 分片。CAP 仍是干净的 CP（DynamoDB 条件写强一致），幂等/去重键（workid 提交幂等 + dedup-key + 子分支确定性派生）三层齐备。
- **残留问题 / 风险**：
  1. **共享在飞计数的 crash-leak（新暴露的三阶问题）**：§2.1 说"认领时原子 `ADD +1`、完成/失败时 `ADD -1`"——但若 worker 在 `+1` 之后、`-1` 之前 **crash**（正是本系统要容错的核心场景），该 shard 的在飞计数会**只增不减泄漏**，多次 crash 后背压阈值会被虚高的计数永久触发（假背压）。需要一个对账机制（如守护层按 lease 过期扫描活跃 in-progress 记录、周期性重算 shard 真值），文档未言明。CAS lease 的正确性靠"记录存在性"这个真相支撑、天然 crash-safe；但**共享计数器不是从记录派生的真相，而是独立可漂移的旁路状态**——这是它与 lease 的本质区别。
  2. **背压的最终一致性近似**：分片在飞计数"读聚合分片求和判阈值"是**最终一致**读，多实例并发认领时阈值判定有窗口误差（可能瞬时略超上限）。对内部试点可接受，但应显式标注"背压是软上限、非硬保证"。
- **建议 / 替代方案（附链接）**：V4 给共享在飞计数补一句 crash-leak 回收策略——推荐**不维护独立计数器，改由守护层从 `GSI2(affinity+progress)` 直接 `Count` 活跃 in-progress 记录**（真相从记录派生、天然 crash-safe，代价是一次 GSI Count 查询），把计数器从"旁路可漂移状态"回归为"记录的投影"；或保留计数器但加 lease 过期驱动的周期性 reconcile。参考 [DynamoDB atomic counters 的已知局限](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html#WorkingWithItems.AtomicCounters)（非幂等、crash 下不可回滚）与 [write sharding 最佳实践](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-sharding.html)。

### 3. SRE 容错 — 8.5/10（V2: 7.5，+1.0，本轮进步最大）
- **改进**：V2 我标为"最应在 V3 收敛的正确性问题"——多实例护栏状态共享——已正解落地。§2.1 明确熔断状态/在飞计数/令牌桶落 **DynamoDB 共享项**、用 CAS/原子 ADD 维护、按 submitter/dependency 分片降热点，并给"每实例本地配额=全局/实例数"作为压测退路；**half-open 重探测挂守护层重扫周期、每周期只放行一个探测任务**（残留问题的正解）；同步落 `工作流模版.md §4`。这把 V2 "护栏是单机语义、与多实例模型冲突"的 P0 二阶洞彻底堵上。§2.3 改派前校验目标端 handler+鉴权也堵上了"改派后仍拉不起"的空转。SPOF 分析清楚（引擎多实例无主非 SPOF，本机 daemon 单点由 liveness 改派兜底）。
- **残留问题 / 风险**：
  1. **共享在飞计数的 crash-leak 回收未言明**（与分项 2.1 同源，从 SRE 视角更严重）：这个系统的存在理由就是容忍 crash/关机，而背压计数器恰恰在 crash 下会泄漏——若不设对账，长期运行后背压会因幽灵计数误触发、拒绝认领健康任务。这是本轮唯一的**真实新增工程缺口**（P1），应在 V4 或实现阶段闭环。
  2. **熔断/令牌桶共享项的写放大**：每次认领/放行多一次条件写，虽有分片缓解、且与主循环高频点写同源，但在故障风暴（大量任务同时撞熔断）时，`GUARD#<dep>` 单项的连续失败计数 CAS 会成为写热点（同一 dependency 只有一个 PK）。文档提了"按 dependency 分项天然分散"，但**同一 dependency 的高频故障计数仍集中在单项**。可接受（故障态短暂），但值得注记。
  3. 本机 daemon SPOF 已诚实标注、靠 liveness 改派兜底，可接受。
- **建议 / 替代方案（附链接）**：V4 给在飞计数补 crash-leak reconcile（见分项 2 建议，推荐用 GSI Count 派生真值替代独立计数器）；熔断计数热点可借鉴 [resilience4j](https://github.com/resilience4j/resilience4j) 的滑动窗口 + 对 `GUARD#<dep>` 再按时间桶/实例分片写、读时聚合。注意 resilience4j 本身是单 JVM 内存态，分布式共享须自行落盘（文档已正确认识到这点）。

### 4. 异构通信协议 — 8.5/10（V2: 7.5，+1.0，并列进步最大）
- **改进**：V2 我标"adapter 契约停在清单级"，V3 已升级到**能定契约**——ClaudeCodeAdapter 给出 sentinel 包裹（`<<<ORCH_OUTPUT_BEGIN>>>{json}<<<ORCH_OUTPUT_END>>>`）+ 优先 `--output-format json` + **解析失败=显式 `error(retryable)` 而非把半解析结果当成功**（这条最关键，杜绝"悄悄跑错"）+ 进度回传 `<<<ORCH_PROGRESS>>>` 转 `checkpoint()` 续 lease；StepFunctionsAdapter 给出 SFN 执行态→progress 完整映射表（`RUNNING→in-progress`、`SUCCEEDED→finished`、`FAILED/TIMED_OUT→error`，retryable 由 `States.Timeout` vs 业务错误判定）。**跨大模型归一明确标注二期已知边界**（我 V2 要的即"一期至少标注边界"）。MCP(消费方)/A2A(编排上层) 定位不变、清晰。
- **残留问题 / 风险**：
  1. **sentinel 契约的对抗性鲁棒性**：worker 是 LLM，可能在思考文本里**吐出 sentinel 字符串本身**（如复述 prompt、生成示例），导致 adapter 误取。契约应补一条"取**最后一对**完整 sentinel"或"sentinel 带随机 nonce（每次调用注入）"以防 LLM 复述污染。这是 `claude -p` 解析的现实长尾。
  2. 云端 on-behalf-of 鉴权仍卡 **OQ-2**（外部依赖，非 writer 可解，但决定 A2AAdapter/云 adapter 能力边界），已跟踪。
- **建议 / 替代方案（附链接）**：V4 给 sentinel 契约补 nonce 防复述（`<<<ORCH_OUTPUT_BEGIN:{nonce}>>>`，adapter 只认本次注入的 nonce）；优先推动 `--output-format json` 成为主路径、sentinel 仅兜底。参考 [Claude Code output formats](https://docs.claude.com/en/docs/claude-code)（结构化输出）、[MCP 规范](https://modelcontextprotocol.io)、[A2A](https://github.com/google/A2A)。

### 5. 分布式 UX — 8.0/10（V2: 7.0，+1.0）
- **改进**：V2 我明确要"一张面板线框 + fan-out 多分支树部分态"，V3 `v3-health-panel` 两级钻取线框已交付——一级**健康度汇总条**（🟢运行/等待 · 🟡需 Reconnect/改派 · 🔴失败需人工）+ 每行一个 workspace + 就地动作按钮，**默认只展开非绿、绿色折叠计数**（正面解决"20 并发不淹没用户"的信息密度问题）；二级钻取**单树分支部分态**（根+fan-out 子分支各自 progress），正是"一棵树里 2 分支 waiting、1 分支 error"如何呈现——分布式 UX 最难的层级被补齐。progress→UI 映射表 + 两类最高频部分失败（关机停摆 / MCP 过期）的一键 Reconnect/改派闭环延续 V2。
- **残留问题 / 风险**：
  1. 线框为**设计基线**、视觉细节留实现——对设计文档阶段完全可接受，但"20 个 workspace × 每树数十分支"的二级视图在极端 fan-out 下的**滚动/折叠/搜索**交互未展开（如何在一屏内定位到那个红色分支）。属实现细节，不扣设计分，仅提示。
  2. sticky-note 仅 macOS 桌面（已诚实标注，商业化跨端留后续，可接受）。
- **建议 / 替代方案（附链接）**：维持现状。二级树视图的大规模 fan-out 呈现可参考 [Temporal Web UI](https://docs.temporal.io/web-ui) 对 workflow/child-workflow 树形状态的折叠+着色范式，实现阶段直接借鉴其"父折叠、异常子高亮上浮"的信息密度策略。

### 6. Salesforce 产品 — 8.0/10（V2: 7.5，+0.5）
- **改进**：我 V2 的 P2 残留已补——§3 明确 **per-submitter→per-tenant 是 StateStore Provider 的扩展而非重写**（因一期已把持久化收敛为接口，返工集中在 Provider 实现层，抽象层可复用），并给出 **Platform Event → signal 的租户上下文映射**（一期 `submitter` 在多租户升级为 `(tenantId, submitter)` 复合键，envelope 增 `tenantId` 透传，signal 按复合键分区）。§3 与 SF 既有编排原语关系（Flow Orchestrator 互补+桥接、Platform Events 桥接候选、Agentforce 互补）延续 V2、清晰；Einstein Trust Layer 列商业化前置门槛、Hyperforce 多租户前瞻，定位诚实。
- **残留问题 / 风险**：
  1. Agentforce/Flow 技术桥仍是**接口草图级**（一期不实现，合理），Platform Event 回调本编排器时会撞上 CRUD/FLS/共享模型——V2 已点名、V3 仍留远期，可接受（一期不触客户数据、不进 Platform）。
  2. 复合键 `(tenantId, submitter)` 落到 DynamoDB PK 前缀时，会与 §1c 的热分区/§2.1 的 `INFLIGHT#<submitter>#<shard>` 分片键结构产生**交互**（多租户下分片键需再纳入 tenantId 维度）——远期改造，一期不必展开，但值得在 §4 返工面里连一句。
- **建议 / 替代方案（附链接）**：保持现有诚实定位即可。参考 [Flow Orchestrator 文档](https://help.salesforce.com/s/articleView?id=sf.flow_concepts_orchestrator.htm)、[Platform Events](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_intro.htm)、[Einstein Trust Layer](https://www.salesforce.com/products/platform/trusted-ai/)。

## 关键建议（按优先级）
1. **[P1，视角 2/3] 共享在飞计数的 crash-leak 回收**——这是 V3 唯一的真实新增工程缺口：`ADD +1` 后 crash（本系统的核心容错场景）会让背压计数只增不减、长期误触发假背压。推荐**弃用独立计数器，改由守护层从 `GSI2(affinity+progress)` `Count` 活跃 in-progress 记录派生真值**（真相从记录派生、天然 crash-safe），或给计数器加 lease 过期驱动的周期性 reconcile。
2. **[P2，视角 4] sentinel 契约防 LLM 复述**——`claude -p` 的 worker 可能在文本里吐出 sentinel 本身；给 sentinel 注入 per-call nonce（`<<<ORCH_OUTPUT_BEGIN:{nonce}>>>`）或"取最后一对完整 sentinel"，并优先把 `--output-format json` 作主路径。
3. **[P2，视角 2/3] 显式标注背压为软上限**——分片在飞计数是最终一致读，多实例并发下阈值判定有窗口误差；对内部试点可接受，但应写明"背压是软上限、非硬保证"，避免下游误以为是精确闸门。
4. **[跟踪，非 writer 可解] OQ-1 / OQ-2 尽快落 owner+deadline**——OQ-1（合规引依赖）决定档位 1/2 与 token 账单，OQ-2（matrix 身份 a/b）决定云 adapter 能力边界；已列闸门 A，建议 kickoff 即指派。

## 未解决 / 待 writer 回应的问题
- [ ] 共享在飞计数的 crash-leak 回收策略（`+1` 后 crash 导致背压计数泄漏、假背压）——**V3 唯一新增的真实工程缺口**。
- [ ] sentinel 输出契约对 LLM 复述 sentinel 字符串的鲁棒性（nonce / 取最后一对）。
- [ ] 背压近似性的显式标注（分片计数最终一致 → 软上限而非硬保证）。
- [ ] 熔断 `GUARD#<dep>` 单项在故障风暴下的连续失败计数写热点（同一 dependency 集中单 PK）。
- [ ] （远期）多租户复合键 `(tenantId, submitter)` 与 `INFLIGHT#<submitter>#<shard>` 分片键结构的交互（分片键需纳入 tenantId 维度）。
- [ ] （非 writer 可解，跟踪）OQ-1 合规引依赖结论、OQ-2 matrix 身份 (a)/(b)——决定档位与云 adapter 能力边界，建议尽快指定 owner+deadline 落地。
