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
