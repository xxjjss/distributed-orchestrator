---
name: design-work-flow
description: >-
  distributed-orchestrator 设计报告的编排工作流：检查环境与分支同步 → 唤醒 writer 写作/修订
  → fan out tech-reviewer 与 product-reviewer 评审 → 汇总评分并 sticky-note 播报。
---

# 每次运行的工作流程
1. 检查 ghx 链接状态、claude api 链接状态和网络链接状态；若失败则 **sticky-note 播报**错误消息并退出。
2. 检查当前分支应为 `dev/jxie/design`，并检查与远端的同步状态：
   - **领先**（本地有未推送提交）→ 先 `git push` 推送本地变更。
   - **落后**（远端有新提交）→ 先 `git pull --rebase` 获取远端变更。
   - **分歧**（两侧均有对方没有的提交，rebase 无法自动解决）→ **sticky-note 播报**错误消息并退出。
3. 唤醒 writer 进行设计文档写作或更新。
4. writer 返回 PR 链接和版本数；若无更新则 **sticky-note 播报**上一期版本号、报告无更新并退出。
5. 只要本地有更新（无论 writer 是否返回 PR 链接），同时 fan out tech-reviewer 和 product-reviewer，等待两者返回。
6. 两者返回后，**sticky-note 播报**结果，包括 PR 链接和错误信息（如果有）。

---

# 评分（Scoring）

- 每个reviewer会汇报该 reviewer 的打分，PR 提交成功/失败。
- **报告总分 = 最新一轮各 reviewer 打分之乘积**（每个 reviewer 只取其最新轮次分数，两个reviewer满分为100， 任何一者给出零分则总分为零）。
- 首版若无任何 reviewer 打分，总分记 `0`（或 `pending`）。

---

# sticky-note 播报

每生成一个版本后，向 sticky-note 发送/更新消息：

1. 用关键字 `distributed-orchestrator` 搜索是否已有消息。
2. **无** → 新增一条；**有** → 更新该条。
3. 用命令 **`sticky_note_task`** 发送，消息开头固定为 distributed-orchestrator, 不超过100个字符， 比如：
   ```
   distributed-orchestrator has submit design V<x>, total score: <yyy>
   或者
   distributed-orchestrator has submit design V<x>, total score: <yyy>，tech-reviewer failed on push
   或者
   distributed-orchestrator ghx connection failed
   ```
   - `<x>`：当前 PR 的 revision 版本号（从 1 起）。
   - `<yyy>`：上文「评分」算出的总分。
   - 消息中distributed-orchestrator应该是指向PR的链接
