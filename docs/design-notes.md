# 设计备忘（design-notes）

> 追加式备忘：记录审阅要点、关键设计决策、未决问题（`[OPEN QUESTIONS]`）与其收敛结论。
> 新条目置于文末，不删改历史。writer / reviewer 均以此为共享上下文。

---

## 2026-08-09 — 交给 writer 前的设想审阅（技术专家视角）

### 术语约定（写进正式报告的术语表）
- **Worker**：被编排的**可执行单元**，实现形态无关——LLM agent / skill / command / SFN / 纯脚本 皆可，只要遵循 handler 契约。
- **handler**：状态机里那个纯函数角色 / 数据模型字段（`enter` + `route`）。概念实体叫 Worker，字段/角色叫 handler。
- 停止让 "worker" 一词在"泛可执行单元"与"状态机纯函数"之间漂移。
- 其余沿用 `工作流模版.md`：manager / branch(`branchId`) / workid / lease / substate / progress。
- 文件更名：`DESIGN.md` → `工作流模版.md`；三个 agent 定义的路径引用已同步。

### 已识别盲点（交给 writer 前应补 / 报告须显式处理）
1. **本机 worker 恢复主体未言明** → 已收敛，见下方「决策 D1」。
2. **鉴权一节几乎为空**，但一期绕不开（worker 脱机代持用户身份、token 存储合规）。待答（A2）。
3. **「信号驱动和消息传递」正文为空**，却是异步编排器的核心（事件注册/监听/去重/分发）。待答（A3）。
4. **幂等边界错配**：模版只承诺"状态转移幂等"，tool 幂等下推给 worker；但设想对用户承诺"断点续传、重入无需介入"。报告须诚实说明这是**共担责任**，勿把"全自动幂等"当无条件卖点。
5. **"效率 3×" 是 n=1 且作者自测样本**，归因脆弱。报告应写成"待验证的试点假设 + 度量方案（多人 A/B、Engineer360 口径）"，而非既成事实。待答（A5）。
6. **matrix/falcon 托管平台是外部依赖**（痛点 1 的解法）。若未落地，一期"云端 24×7 tool box"须标为**外部依赖 / 排期风险**，非自有交付。

### 太激进（建议一期降级）
- **discover agent 自主找 handler** 是开放研究问题（语义路由准确率）。一期降级为**注册表 + 显式路由 + 关键字匹配**，自主发现挪二期。
- **图形化 AI 开发界面 / 拖拽状态机** 是独立大产品，严格锁远期。
- **终端用户（Salesforce 客户）可用** 一期一字不碰，锁远期。

### 太保守（建议一期更进取）
- **持久化不应只提"DynamoDB 单表"**：抽象成 `StateStore` 接口，云端实现=DynamoDB，本机实现=SQLite/本地文件。让"本机/云端统一编排"真正成立（同一接口、两种实现），而非二选一。
- **SDK 最小内核（状态存储 skill + handler 契约，`工作流模版.md` 已设计好）提前到一期**；只把"图形化/大规模改写"留二期。否则一期做的 worker 二期返工。
- **事件层一期先定统一 event envelope 格式 + 去重键**（哪怕只接 1–2 个源），避免二期整合返工。

---

## 2026-08-09 — 决策 D1：本机 worker 的恢复与「断网」范围（A1 收敛）

**恢复主体 = 本机 daemon**，开机自动检测并断点续传。

**单一事实源 = 云端存储。** 本机与云端 worker 共用同一张云表、同一套 lease+CAS 互斥；本机 worker 启动后也写云端。云端按 `workid` + `submitter` 检索任务。

**数据模型新增字段（必须）：**
- `affinity`：运行位置亲和，`cloud | machine:<id>`。守护层按 affinity 分区认领——云端 manager 只认领 `affinity=cloud`，本机 daemon 只认领 `affinity=machine:自己`。跨界情形（`affinity=cloud` 但云端无该 handler；或 `affinity=machine:X` 但 X 离线）→ **只告警、不拉起**。这样避免云端去拉一个只存在于某台本机的 handler。
- `submitter`：既是检索键，也是**隔离边界**。共享云表须做 per-submitter 访问隔离（连回鉴权 A2）。

**「断网」范围（刻意收缩）：**
- 断网时**只保证异地（云端 / 服务器端）worker 继续运行**。
- 本机重新联网后，本机 daemon/workflow **从云端取回上次状态，正确推进工作流**。
- **本机自身在断网期不承诺执行**（断网时本地缺 LLM API 授权与连接，worker 本就跑不动）。
- 因此**放弃"本地状态存储 + 与云端双向同步"支线**——它需要接近 CRDT 级的冲突解决，收益却是一个断网跑不动的 worker，投入产出严重失衡。
- 区分两个概念：**断网*执行*（不做）** vs **中断*容错*（关机/重启/网络抖动后自动续传，必须做）**。后者由"云端单一事实源 + daemon 重扫"完全覆盖，无需本地状态源。
- 唯一保留的本地性：worker 在长 LLM state 内部的 checkpoint 可先写本地内存/临时文件再随 `checkpoint()` 落云端——属**性能优化**（降低云端写频率），非本地事实源，归实现细节不进架构。

**由 D1 带出、待表态：**
- 本机 daemon 用什么凭据写云表：建议一期用开发者已有云凭据（AWS）直连云表，带鉴权的 API gateway 推二期。（并入 A2）
- 云端 manager 与本机 daemon 扫描竞争：靠 `affinity` 分区解决，规则须写入正式文档。

### 尚待用户回答
- **A3 消息/信号层**：事件注册/监听/去重/分发的意图（watch-pr / slack / GUS / 文档变更监听如何统一）。
- **A5 度量**：如何让"3× 效率"可信（度量口径与试点设计）。

---

## 2026-08-09 — 决策 D2：一期鉴权复用 MCP（A2 收敛）

**一期不自建鉴权体系。** worker 复用 Suite Manager（MCP adaptor）在本机维护的每连接鉴权，**以开发者本人身份**调外部系统。已支持的连接（来自 Connections 面板）：Claude Code、Claude Unleashed、GUS(OAuth，如 `x@gus.com`)、Google Workspace、Searchinator、DX Gateway(token)、Slack(可选)。

**MCP 鉴权的本质**：机器本地（machine-local）+ 交互式登录建立 + 开发者本人身份。与 D1 的"本机 daemon 用开发者已有凭据"咬合。

**由此产生的三条硬边界（报告必须显式写明，勿误导）：**
1. **给 worker 打上 `affinity=machine`**：凡依赖这些 MCP 连接的 worker，只能跑在建立了连接的那台本机。云端 24×7 tool box worker 无本机 MCP 登录态 → 一期主力全自动脱机跑的是 `affinity=machine` 本机 worker。云端 worker 的身份能力取决于 matrix 机制，见下方「决策 D3」。
2. **交互式登录 ≠ 无头长跑**：面板 Reconnect/Connect 说明连接靠人工建立/续期；OAuth 过期时无头 worker 无法自弹登录。一期"无头"的前提是**连接已认证且未过期**；过期归入"只告警、不硬跑"（类比 `error(retryable=false)`+告警），由人 Reconnect。**别把"无头"吹成"永不需要人碰鉴权"。**
3. **MCP 只解决"以谁的身份调外部系统"，不解决"谁能看云表里谁的任务"**：submitter 隔离一期风险天然低（各本机各身份），但**共享云表的 per-submitter 访问隔离仍须做**（一期最简：云凭据按人隔离，worker 只读写自己 submitter 分区）。两件事勿混。

**二期鉴权目标（报告作对比，给出进化理由）**：云端代持用户身份 24×7（server-side OAuth token 保管 + 刷新 + 最小权限），突破一期"云端 worker 拿不到用户身份"的限制。

---

## 2026-08-09 — 决策 D3：matrix 云端 worker 的身份机制（外部依赖 + OPEN QUESTION）

**背景**：用户提到 matrix（痛点 1 的云端托管平台）将实现"把 worker 搬到云端"——由 **matrix 服务账号执行**工具箱中的 worker，但**使用本机个人鉴权获得调用这些 worker 的权限**；具体身份传递机制**未知**。

**关键岔路（决定一期云端 worker 的能力边界）：**
- **(a) 仅授权"能否调用"**：个人身份只用于准许触发云端 worker；worker 内部调 GUS/Slack 用**服务账号身份** → 操作挂在服务账号名下，权限=服务账号范围。
- **(b) 授权并传递身份（代持）**：个人身份传到云端，worker 以**用户身份**调 GUS/Slack（on-behalf-of / token 代持） → 操作挂在用户名下。这通常需要 server-side OAuth token 保管。

**`[OPEN QUESTION]`（写进报告，待用户向 matrix 团队确认）**：
> matrix 的"本机个人鉴权 → 云端 worker"是 (a) 调用门禁，还是 (b) 身份代持？这决定一期 `affinity=cloud` worker 能否以用户身份操作 GUS/Slack。

**工作假设（设计期采用）**：**假设 (b) 代持**（用户猜测/估计）。理由：按更强能力假设设计，若最终为 (a) 则降级容易，反之补代持难。报告须同时给出「若 (a)」的能力退路。

**外部依赖标注**：matrix（托管平台 + 服务账号执行 + 身份机制）非本项目交付，属**外部依赖 + 排期/机制风险**，与痛点 1 的 falcon 托管平台一并标注。

**对 `affinity` 模型的细化**：
- `affinity=cloud`（服务账号身份即可：纯计算、读公共数据）——一期 matrix 可跑。
- `affinity=cloud, identity=on-behalf-of:<user>`（需以用户身份操作外部系统）——可行性取决于上面 (a)/(b)；假设 (b) 则一期可行。
- `affinity=machine:<id>`（依赖本机 MCP 登录态）——一期主力。

## 2026-08-09 — 决策 D4：消息/信号层（A3 收敛）

**核心洞察**：`watch-pr`（`~/.local/bin/watch-pr.py`）已隐含一套完整的信号 watcher 契约，一期应将其**泛化为通用 Watcher 接口**，而非每种信号各写一套。

**从 watch-pr 提炼的 Watcher 五要素契约（一期定死）：**
| 要素 | watch-pr 体现 | 泛化概念 |
|---|---|---|
| 源+订阅 | PR url + watch-items | `source` + `event-types` |
| 轮询调度 | crons + job-scheduler（登录态长驻，故回调可跑 `claude -p`） | 统一 poll 调度 |
| **边缘触发** | 快照 diff，仅状态**跃迁**时 fire（merged 只触发一次） | **去重的本质 = edge-triggered，非 level** |
| 回调 | `callback` 命令 + `{{watched-item}}`/`{{job-id}}`/`{{pr-url}}` 替换 | 信号如何投递 |
| 生命周期 | create/watch/delete/list + expire + job-id=hash(输入) 幂等 | 注册/注销/自清理 |

**两方案不是二选一，而是同一架构的两层：**
- **方案1（预定义 watcher 工具）= 采集层**：每源一个 watcher，负责"监听某具体源 + 边缘去重"。watch-pr 为参考实现。✅ 一期做。
- **方案2（统一 SQS）= 传输层**：watcher 发事件到 SQS、worker 统一消费。⚠️ 一期不全量上：
  - watch-pr 现为 **回调 push**（fire → 直接跑 callback，同步、点对点、无中间件），本机 `affinity=machine` worker 用它已验证跑通，更简单。
  - SQS 是 **事件 pull**（解耦、可持久、可重放），**真正价值在云端**：`affinity=cloud` 的 `waiting` 任务靠 SQS "事件到达→唤醒"。
  - 结论：**一期本机走回调 push，云端 waiting 唤醒按需用 SQS；二期再统一到事件总线。**

**统一 event envelope（一期必做，独立于是否用 SQS）：**
`{ source, event-type, subject-id(如 pr-url), dedup-key, payload, timestamp, target-workid? }`。无论 push 还是 SQS，fire 出的事件都用同一 schema。

**信号 → 状态机的标准回调（接上 `工作流模版.md`）：**
- 现状 watch-pr callback 是任意 shell（常 `claude -p` 直接拉 agent）。
- 一期标准化为：**callback 调状态存储 skill 的 `signal(workid, branchId, envelope)`**，把 `waiting → new`（envelope payload 作下一步 input），由 manager 下一轮自然拉起。
- 即 **watcher 不直接拉 worker，而是"喂信号给编排器、由 manager 拉"**——更贴合分布式/云端模型。

**一期预定义 watcher**：PR（已有 watch-pr）、Slack message、document status、CI/CD pipeline。

**一期/二期切分：**
- 一期：event envelope schema + Watcher 契约 + 3–4 个 watcher + `signal()` 标准回调 + 本机回调 push（云端 waiting 按需 SQS）。
- 二期：全面统一 SQS/事件总线、更多源、watcher 注册中心。

---

## 2026-08-09 — 决策 D5：效率证据的度量口径（A5 收敛）

**证据**：作者个人开发效率 ≈ 他人 3×；来源 **Engineer360**（公司内部网页，可核验）；主要依据 **完成的 WI 数 + 提交的代码量**。用户将提供证据。

**报告写法（用足证据 + 堵住"过度包装"质疑）——必须诚实标注：**
1. **样本 n=1 且为作者本人** → 定位为"早期个人实测信号"，非"经统计验证的产品效果"。
2. **归因未隔离** → 3× 中工具贡献 vs 个人因素尚未区分。
3. **代理指标风险** → "WI 数 + 代码量" 是产出代理，不完全等价于价值产出（脚注一句，避免"刷量"质疑）。

**定位**：立项的**早期信号 + 待规模化验证的假设**，并给出验证路径（多人试点 / 对照，Engineer360 口径），而非既成产品级结论。

### 尚待回答（更新）
- **确认 matrix 身份机制 (a)/(b)**（D3 的唯一 OPEN QUESTION，用户将进一步确认）。

---

## 2026-08-09 — V1 报告写作完成（writer，重试成功）

上一次运行在写作阶段 API 超时；本次恢复并完成 `distributed-orchestrator.md` 首版（V1）。

**写作策略**：分段 append 落盘（骨架/§0-1a → §1b-1d → §2 → §3-5+附录），控制单次工具输出体量，避免再次超时。

**报告结构落点**（对齐产出清单）：
- §0 执行摘要 + 术语表：钉死 D1–D5 术语，防全文漂移。
- §1a 架构图（复用 `v1-architecture.png`）+ 五层组件职责表 + 交付边界。
- §1b 时序图（`v1-message-seq.png`）+ Watcher 五要素契约 + event envelope（D4）。
- §1c DynamoDB 单表元数据结构 + 结构化/非结构化划分 + D1/D2 新增字段。
- §1d 选型调研：组件 A（持久化内核：LangGraph/DBOS/Temporal/SFN/自研，5 候选）、B（matrix/ECS/GH Actions 托管）、C（MCP/OAuth 代持/SF Identity 鉴权）、D（watch-pr/SQS/EventBridge/Streams 信号）。每组给 License + 稳定性/扩展性/商用判断。
- §2 竞品对比（durable execution / LLM agent / 通用编排 / AI 托管 / 内部现状 五类）+ 四条护城河 + 商业前景 + FDE 落地闭环 + SF 产品耦合表。
- §3 一期能力交付表 + affinity 调度图（`v1-affinity-scheduling.png`）+ 度量方案（3–5 人试点、保守判据 ≥1.5×）+ 成本依赖 + 一期不做清单；二期/远期蓝图。
- §4 风险登记 R1–R7；§5 待决问题 OQ-1/2/3；附录决策追溯。

**报告内新增 OPEN QUESTIONS（写进 §5，待 reviewer/human 收敛）**：
- OQ-1：合规能否引入 MIT LangGraph/DBOS（一期成本最大变量）。
- OQ-2：matrix 身份机制 (a)/(b)（承接 D3 遗留 OPEN QUESTION）。
- OQ-3：商业化路径 独立 SaaS vs 内嵌 Agentforce/Platform（倾向后者）。

**版本**：V1。commit + PR（ghx，指向 main）。未 merge（人类决定）。

---

## V2 迭代（2026-08-10）— 模式 B 迭代修订

**触发**：PR #4 上收到大量 human review comment + 两条 issue-style reviewer 评审 + tech/product reviewer V1 反馈文件。本轮为模式 B 迭代修订，收尾一轮被墙钟超时中断的写作。

### 结构性决策（最大变更）
- **拆文档**（human comment 最高优先）：原单一 `distributed-orchestrator.md` 拆为两份交叉引用文档：
  - `distributed-orchestrator-tech-design.md`：面向技术审核人，系统结构/选型/实现/机制正确性。
  - `distributed-orchestrator-project-analyst.md`：面向产品与领导层，现状/痛点/分期/益处/成本/前景。
  - 原 `distributed-orchestrator.md` 降级为索引/导航页。
- **一致性联动**（human comment 明确要求）：拆分后同步更新三个 reviewer 定义（`tech-reviewer.md`/`product-reviewer.md`/`leadership-reviewer.md`）的「报告」路径行、三个 `*_team.py` 的 `default_doc`（tech→tech-design，product/leadership→project-analyst）、以及 `design-work-flow.md`，使评审对象与拆分后的文档结构保持一致。

### 术语与命名（human comment）
- 新增术语：**CAS**（Compare-And-Swap）、**workspace**（workid/branchId 的对外泛化）、**envelope**。
- `agent-work-manager` 正式定位为 **workflow 引擎**（可编排多 worker、可嵌套 workflow）。
- 回叫措辞由「该你做决定了」改为「该你做动作了（决定/审查/签收，承担责任）」。
- Watcher 例子去掉「3–4 个」具体数字，改为「Slack/PR/CI-CD/GUS 状态等」。
- 「富交互留后续」明确为「图形化拖拽编辑、多面板联动、可视化审计钻取」。
- SFN 措辞去掉「大量」→「公司已在 TCM 使用」。

### 分期主线（human comment）
- 确立「**一期推工具、二期推环境、长期推产品**」主线，贯穿执行摘要与蓝图。
- 设计思路的痛点归纳润色为 P1–P5 表格，作为 presentation 的 why（人类评审只读成品文档）。

### 图表（v2 重画）
- `v2-architecture`：Watcher 加监听 GUS 连线；workflow 引擎标注可组合；新增韧性护栏节点；云端 worker 标注「云端跑时用户可关机」。
- `v2-message-seq`：加 note「worker=affinity:cloud 时用户即可关机断网」；signal 标注 dedup 条件写。
- `v2-affinity-scheduling`：新增 `machine:X` 永久离线 → stall 超阈值 → 改派分支（liveness）。
- `v2-runtime-adapter`：新增，异构 runtime adapter（ClaudeCode/Script/StepFunctions/A2A/MCPTool）。

### 机制正确性（tech reviewer P0/P1，落到 tech-design §2）
- §2.1 熔断/限流/背压/bulkhead + per-workspace token 预算护栏（新增 `tokenSpent` 字段）。
- §2.2 signal 幂等/去重：dedup-key 条件写 `attribute_not_exists`；fan-out 子分支确定性派生防双重 spawn。
- §2.3 affinity 永久失配的改派（liveness 兜底，一期默认人工确认）。
- §2.4 Worker Runtime Adapter + MCP（消费方）/A2A（编排上层）定位。
- §2.5 引擎多实例无主 HA（CAS 抢 lease 去重，非 SPOF）。
- §2.6 局部失败 progress→UI 映射 + MCP 过期一键 Reconnect + machine 离线一键改派闭环。

### DynamoDB 选型理由（human comment，tech-design §1c）
- 结合主要用例（高频点写+CAS 抢锁+按树读+幂等提交）论证 NoSQL 强项；诚实标注复合查询缺失，用 GSI（submitter / affinity+progress）+ 分析侧导出规避。

### 自研含义与工作量（human comment，tech-design §1d）
- 「自研」分两档：档位1（可引 MIT 依赖，在 LangGraph/DBOS 上增功能，6–10 人周）/档位2（合规禁止，全自研内核，14–22 人周），AI 辅助估计；差别由 OQ-1 决定。

### 成本量化（product reviewer P0，project-analyst §3a）
- 人力/里程碑 M1–M4（档位1 ≈11–17 / 档位2 ≈16–24 人周，约 1 季度，1–2 工程师）；云资源月成本（几十至低几百美元）；LLM Token 预算（并发×步数×单步×单价 + memoization 省 token + 每-workspace token/attemptCount 硬上限熔断）。

### 商业化与 FDE（product reviewer P1 + human comment）
- 一期只谈内部收益，商业化作愿景/可能性探讨；OQ-3 升级为四维打分（TAM/壁垒/分发/议价权，倾向内嵌 Agentforce）。
- §2d Agentforce 技术桥：编排器作 Agentforce Action 长跑后端 / Flow async 编排层 / Platform Events 桥。
- FDE 现场落地问题（与客户 Org 共存、通用 AI 组件、合规）列为未来问题，一期只点名不给方案。
- tech-design §4 可外带 IP 内核边界：鉴权/托管/持久化/输入源做可插拔 Provider。

### 与 SF 既有编排原语（tech P1 + product P1，tech-design §3）
- 正面回答「为何不用 Flow Orchestrator/Platform Events」（互补+桥接，非替代）；Einstein Trust Layer 商业化前置门槛；Hyperforce 多租户前瞻。

### 风险与 OQ 新增
- R8（token 失控烧钱）、R9（客户现场可移植性悬崖）；OQ-4（Matrix 内部工具 vs 对外产品 + EC2/客户服务器后备计划）。

### 反馈处理与标记
- PR #4 的 24 条 review thread 逐条对照 V2 文档，处理后用 GraphQL `resolveReviewThread` resolve。
- 2 条 issue-style reviewer 评审回复「Resolved in V2」并加 👍。
- 备注：本轮尚无 `leadership-reviewer-feedback-V1.md`（仅 tech + product 两份），故未针对 leadership AI 反馈作回应，待其产出后下一版收敛。

**版本**：V2。commit + push 到已存在的 PR #4（复用，绝不重复 create）。未 merge（人类决定）。

---

## V3 迭代（2026-08-10）— 模式 B 迭代修订

**触发**：PR #4 上 2 条 unresolved human review thread（要求补真实原型实战示例/截图 + WI 端到端示意图）+ 三份 V2 reviewer 反馈（leadership 7.2 conditional-GO、product 7.2、tech 7.6）。V1 comment 与 issue-style comment 上一轮已 Resolved in V2。

### Human comment（2 条 unresolved thread，均在 project-analyst.md）
- **WI 端到端示意图 + 真实 WI 例子（W-23433231）**：新增 §0.2.1 + `v3-wi-end-to-end.mmd/png` 序列图，画上 WI-worker/tcm-automated-sdd/pr-gate/WI-chatter/watch-pr/job-scheduler/外部信号源；点明"一人并行多 WI、只做 decide/review/sign-off"的效益机制（chatter 临时作状态持久化媒介）。
- **一期实战截图打动领导层**：嵌入 4 张真实原型截图到 §0.2.1——`v3-sticky-note`（人机界面 in-progress/done/todo=GUS item + NON-WI TASKS 承接 AI 回叫）、`v3-sticky-note-invoke`（双击激活 WI-worker）、`v3-job-scheduler`（带 login session 的调度器，区别于 crontab）、`v3-watch-pr`（watch-pr --list 的 watch-items/state/callback）。截图从 ~/Desktop 复制（文件名含 narrow no-break space  ，用 python glob 处理）。

### Leadership reviewer V2（7.2，conditional-GO）落地
- §0.0 决策摘要卡（Ask/收益/成本量级/Top-3 风险/建议/门槛，半页）。
- §0.4 决策建议：Conditional GO + 闸门 A（投钱前：OQ-3 战略裁决 + OQ-1 owner）+ 闸门 B（二期前：4 条试点 gate）。
- §2c 付费意愿代理指标口径化（三条可从审计轨迹客观算出的指标 + 采集方式）。
- §5 OQ owner+deadline 表（OQ-1/OQ-3 = 闸门 A 阻塞项；owner/deadline 为 writer 建议，管理层签署以 [OPEN QUESTIONS] 标注——headless 不代签）。
- §1 术语脚注（affinity/CAS/lease/stateFingerprint/StateStore 业务语言对照）。
- 战略埋点：一期交付物按"Agentforce 编排底座候选内核"设计（§0.4/§2d/§3a）。

### Product reviewer V2（7.2）落地
- §3a 一期每月 token 账单合成区间：Sonnet ≈$90–450/月、Opus ≈$450–2,250/月、保守数千/月（护栏封顶），待 claude-api 核准。
- §2b OQ-3 权重敏感度分析（等权 12v14；分发/壁垒双权重内嵌胜出；仅议价权双权重打平 → 结论基本稳健）。
- §3b Provider 化 + 客户现场适配增量成本粗估（≈8–14 人周）。
- OQ-1/OQ-4 owner+deadline（§5 表）。

### Tech reviewer V2（7.6）落地 — 分布式二阶正确性（tech-design §，同步 工作流模版.md）
- **[P0] 护栏多实例状态共享**（§2.1）：熔断/在飞计数/令牌桶落 DynamoDB 共享项+条件写，按 submitter/dependency 分片；本地配额退路；half-open 挂守护层重扫周期。→ 同步 工作流模版.md §4。
- **[P0/P1] dedup TTL vs 重放窗口 + watcher 快照依赖链**（§2.2）：dedup_TTL > max_replay_window + 原生 TTL；跃迁标识优先事件稳定标识（merge_commit_sha）+ 快照持久化兜底。→ 同步 工作流模版.md §4。
- **[P0/P1] 热分区**（§1c）：一期步数/子分支上限规避；二期分支级 PK 分片 workid#branchShard。→ 同步 工作流模版.md §2。
- **[P1] adapter 契约**（§2.4）：ClaudeCodeAdapter sentinel 包裹 + 解析失败显式失败 + 进度回传；StepFunctionsAdapter 执行态映射；跨大模型归一=二期边界。
- **[P1] 健康度面板线框**（§2.6）：`v3-health-panel` 两级钻取（多 workspace 汇总条 → 单树分支部分态）。
- **[P1] 档位1 LangGraph 并发语义风险**（§1d）：CAS lease 叠加 last-write-wins checkpointer 集成成本 + DBOS Postgres 栈冲突注记。
- **[残留] 改派前校验目标端 handler/鉴权**（§2.3）。
- **[P2] StateStore 多租户返工面 + Platform Event→signal 租户上下文**（§3）：Provider 扩展非重写；envelope 预留 tenantId。

### 底层设计文档改动（工作流模版.md）
- §2 加热分区约束（步数上限/二期 PK 分片），与 tech-design §1c 一致。
- §4 加多实例护栏共享落盘约束 + dedup 时序约束，与 tech-design §2.1/§2.2 一致。
- 理由：tech reviewer P0 指出的护栏/dedup/热分区是底层状态机/持久化/幂等正确性问题，须落到 工作流模版.md 保持主设计与底层一致。

### 反馈处理与标记
- PR #4 的 2 条 unresolved review thread → 处理后用 GraphQL resolveReviewThread resolve。
- 三份 V2 reviewer 反馈（各只读最新轮次）逐条在 V3 Q&A 回应。
- 无新增 issue-style human comment 待处理（V1 两条上轮已 Resolved in V2）。

**版本**：V3。commit + push 到已存在的 PR #4（复用，绝不重复 create）。未 merge（人类决定）。

---

## V4 修订要点（2026-08-11，回应 PR #4 human comments + tech/product/leadership V3 反馈）

### 关键决策与调研
- **Opus 定价订正（已核准，非待定）**：据 claude-api skill 缓存的 2026-06 Anthropic 公开定价（Sonnet $3/$15、Opus $5/$25），Opus:Sonnet **纯单价比 = 1.67×**，而非 V3 假设的 5×。据此把 Opus 档月账单从 ≈$450–2,250 下修为 **≈$150–750/月**，去掉"待 claude-api 核准"hedge。product + engineering reviewer V3 P1 均点名此项，确认订正方向。保守上界从"数千/月"收窄为"约 $1–2k/月"。
- **ECS/Fargate 应急退路成本入表**：engineering reviewer V3 反复指出的 V2 残留——matrix 延期的一期应急退路成本从未进 M1–M4。V4 在里程碑表加**条件性行 +2–4 人周**，明确与二期 Provider 化 8–14 人周是**不同触发条件的两笔钱**（一期临时保云端能力 vs 二期客户现场适配）。
- **痛点重构（PP + 鱼骨图）**：human comment 指出 `P1` 易被误读为 priority → 全改 `PP1–PP5`（Pain Point）。每条 PP 补可量化效率损耗口径。新增鱼骨图 `v4-painpoint-fishbone`（源+PNG，mermaid.ink pako 渲染）：五 PP → 共同根因「人的在场/介入被迫成为工作流吞吐瓶颈」→ 效应「研发效率低下」。这是把分散痛点收敛到单一根因的关键叙事。
- **§0 结构重排（痛点→解决方案→原型实例）**：human comment 要求 solution 紧接 pain point、"早期信号"更名"原型实例"并移到 solution 之后、并在 PP 后立刻描述一期落地后的开发流程体现效率。据此：原 §0.3 solution 上提为 §0.2 + 新增 §0.2.1「落地后开发流程」流水；原 §0.2 早期信号降为 §0.3「原型实例」（实证而非推测）。
- **§2c 指标改名"使用强度/信任代理"**：product reviewer V3 P2 指出三指标测的是内部工程师行为，非买方付费意愿，命名 overclaim。改名后"付费意愿"严格保留给二期真实预算认领测试。闸门 B 第 4 条同步改名。
- **§2b 定价锚点 + 买方画像**：补 Temporal Cloud/LangGraph Platform/Inngest/n8n 计费轴锚点，我们倾向 consumption 计量（per-workflow-run/per-step）随 Agentforce SKU 打包（避开 n8n $0 开源地板价）。假设买方 = 已部署 Agentforce、有 AI-ops/可靠性预算线的平台工程/研发效能负责人；指出闸门 B 全供给侧、缺需求侧 gate。
- **Agentforce 技术桥收敛 + OQ-5**：product reviewer V3 P2 指出技术桥零推进、结论跑在验证前。V4 把两个"或"收敛为倾向决策：回调统一走 Platform Event；Action 视为"至多一次触发+异步收敛"黑盒；`workid↔session` 生命周期映射；session 内部非确定性推理**不纳入 replay 校验**（解决 stateFingerprint 与非确定性 planner 的共存正确性问题）；stateFingerprint 扩校验 Prompt Builder 模板版本；补 Data Cloud zero-copy 集成草图 + 三桥接点平台约束占位数字。升级为 **OQ-5**（Agentforce 平台架构团队裁决，闸门 B 前）。
- **R10 外部 API 限额风险**：engineering reviewer V3 P2 新盲区——15–25 并发下 SF Core/GUS/Slack/GitHub 下游 governor limits 从未测算，一期护栏只防自己的 LLM 调用。新增 R10，用 R8 同框架（每类 API 独立令牌桶+熔断+退避）覆盖。

### 底层设计文档改动（工作流模版.md）
- **§4 加背压在飞计数的 crash-leak 回收（V4）**：tech reviewer V3 P1 指出 V3 的"独立在飞计数器 +1/-1"在 worker crash（+1 后、-1 前）时**只增不减泄漏 → 假背压永久虚高**。决策：**弃用独立计数器，改由守护层从 `GSI2(affinity+progress)` Count 派生背压真值**（真相从记录派生 → crash-safe，crash 任务 lease 过期后被守护层重新计入/回收，计数自动收敛）；保留计数器+reconcile 为备选（计数器降级为缓存、GSI Count 为事实源）。显式标注**背压=软上限**（最终一致读、有窗口误差），硬上限（token 预算）用单项 CAS 强一致约束。与 tech-design §2.1 一致。
- 理由：这是底层状态机/持久化正确性缺口（独立旁路状态漂移 vs 从记录派生的真相），必须落到 工作流模版.md 保持主设计与底层一致。

### 反馈处理与标记
- PR #4 上 V3 后新增的 unresolved review thread（PP 命名/量化/鱼骨图/solution 前移/原型实例更名/Slack 回叫/至少两人/措辞专业化/Agentforce 文档链接等）→ 逐条在 V4 落地，处理后用 GraphQL resolveReviewThread resolve。
- 三份 V3 reviewer 反馈（tech 8.3 / product 7.6 / leadership 7.8，各只读最新轮次）逐条在 V4 Q&A 回应。
- leadership 的两个 P0（闸门 A 战略裁决、非 writer 可解）报告侧已就位，留作 kickoff 行动项，不改文档。
- presentation 抽取版：标为 [OPEN QUESTIONS]，倾向另出独立文件而非塞进报告；本轮先确保 §0.0 决策卡可独立支撑 3 分钟 pitch。

**版本**：V4。commit + push 到已存在的 PR #4（复用，绝不重复 create）。未 merge（人类决定）。
