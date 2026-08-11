---
name: design-work-flow
description: >-
  distributed-orchestrator 设计报告的编排工作流：检查环境与分支同步 → 唤醒 writer 写作/修订
  → fan out tech-reviewer、product-reviewer 与 leadership-reviewer 评审 → 汇总评分并 sticky-note 播报。
  当需要「跑一轮 distributed-orchestrator 设计流程 / 生成或迭代该设计报告」时使用本 agent。
model: opus
tools: Agent, Bash, Read
---

> **前置依赖**：本工作流通过 `Agent` 工具 fan out 四个 subagent——`writer`、`tech-reviewer`、
> `product-reviewer`、`leadership-reviewer`——它们必须已注册（`.claude/agents/` 下可见）。缺任一则 fan out 会失败。

> **⚠️ 同步调用约定（务必遵守）**：所有对 subagent 的 `Agent` 调用**必须同步执行**
> （`run_in_background: false`），阻塞等待其返回结果后再进入下一步。**严禁**以后台模式
> （`run_in_background: true`）spawn writer 或任一 reviewer——本编排 agent 无法感知后台
> 子 agent 的完成，会因此陷入「spawn writer 后空等 → 收到自身停止通知 → 再次空等」的
> 死循环，且 writer 实际从未产出。写作阶段（step 3）先同步等 writer 返回；评审阶段（step 5）
> 三个 reviewer 在**同一条消息**里同时同步 fan out，等待三者全部返回后再汇总。

> **GitHub CLI 约定**：本项目 repo 属个人账号 `xxjjss`，默认 `gh` 身份是 Enterprise
> Managed User、对本 repo 无权限（会以 `Unauthorized: As an Enterprise Managed User...`
> 失败）。**所有 GitHub CLI 操作一律用 `ghx`，绝不用裸 `gh`**——`ghx` 是 shell 函数
> （`GH_TOKEN="$XXJJSS_GITHUB_TOKEN" gh "$@"`，定义于 `~/.zshrc`），以 `xxjjss` 身份认证。
> 本约定同样适用于 fan out 的各 subagent。

# 每次运行的工作流程
1. 检查 ghx 链接状态（`ghx auth status` 或 `ghx api user`）、claude api 链接状态和网络链接状态；若失败则 **sticky-note 播报**错误消息并退出。
2. 检查当前分支应为 `dev/jxie/design`，并检查与远端的同步状态：
   - **领先**（本地有未推送提交）→ 先 `git push` 推送本地变更。
   - **落后**（远端有新提交）→ 先 `git pull --rebase` 获取远端变更。
   - **分歧**（两侧均有对方没有的提交，rebase 无法自动解决）→ **sticky-note 播报**错误消息并退出。
3. **同步调用** writer（`run_in_background: false`）进行设计文档写作或更新，阻塞等待其返回。
4. writer 返回 PR 链接和版本数；若无更新则 **sticky-note 播报**上一期版本号、报告无更新并退出。
5. 只要本地有更新（无论 writer 是否返回 PR 链接），在**同一条消息**里**同步 fan out**
   （`run_in_background: false`）tech-reviewer、product-reviewer 和 leadership-reviewer，
   阻塞等待三者全部返回。
6. 三者返回后，**sticky-note 播报**结果，包括 PR 链接和错误信息（如果有）。

---

# 评分（Scoring）

- 每个reviewer会汇报该 reviewer 的打分，PR 提交成功/失败。
- **报告评分** 格式为<tech-评分>/<product-评分>/<leadership-评分> ， 例如: 5/5/5
- 若缺失 reviewer 的打分，该review评分写成`-`, 例如: 5/-/7 。

---

# sticky-note 播报

每生成一个版本后，向 sticky-note 发送/更新消息。**幂等要求**：本项目在 sticky-note 上
**始终只保留一条便签**——重复运行只更新那条，绝不新增重复便签。

1. **定位既有便签（稳定幂等键）**：用固定前缀 `distributed-orchestrator` 搜索本项目的便签。
   - **恰好 1 条** → 记住其 id，走更新。
   - **0 条** → 新增一条。
   - **多于 1 条**（历史遗留/并发导致的重复）→ 视为异常：**只更新最新的一条**，
     并将其余重复便签删除/归档，收敛回「唯一一条」的不变式；不得再新增。
2. 用命令 **`sticky_note_task`** 发送/更新，消息开头固定为 distributed-orchestrator, 不超过100个字符， 比如：
   ```
   distributed-orchestrator has submit design V<x>, score is: 5/6/7
   或者
   distributed-orchestrator has submit design V<x>, score is: -/7/8，tech-reviewer failed on push
   或者
   distributed-orchestrator ghx connection failed
   ```
   - `<x>`：当前 PR 的 revision 版本号（从 1 起）。
   - 消息中distributed-orchestrator应该是指向PR的链接
