# Worker Agent 示例：provision-worker

演示如何按 Agent Manager 契约写一个 worker agent。业务场景：为租户开通一个用户，需要三步。

worker 只实现两件事：`enter`（做事，非确定、有副作用）和 `route`（纯函数，决定下一步）。它**不碰 DynamoDB、不知道自己是不是重试、不管历史**——这些全由 manager 和状态存储 skill 负责。

---

## 状态定义

```
VALIDATE   校验输入（租户存在？配额够？）—— 演示 state 内部子状态推进
PROVISION  在 Pod 上创建用户 —— 演示派生另一个 agent（spawn 子分支）
NOTIFY     通知用户 + 结束 —— 演示成功结束（finish）
```

状态流转：

```
VALIDATE ──toState──> PROVISION ──spawn(audit-worker)──> (等子分支) ──> NOTIFY ──finish──> ✅
   │                      │
 内部循环              子分支跑完
 toSubstate            回写后继续
```

---

## worker 契约（伪代码）

worker 是一个纯函数式对象，manager 用 `(input, state, substate)` 调它，它返回 `(output, transition)`。

```python
class ProvisionWorker:
    handler = "provision-worker"

    # manager 喂入 input + state + substate，worker 返回 output + 下一步意图
    def run(self, input: dict, state: str, substate: dict | None) -> Transition:
        if state == "VALIDATE":
            return self.validate(input, substate)
        if state == "PROVISION":
            return self.provision(input, substate)
        if state == "NOTIFY":
            return self.notify(input, substate)
        return fail(retryable=False, reason=f"unknown state {state}")
```

`Transition` 是 route 的返回，模版提供这几种构造子：

| 构造子 | 含义 | manager 动作 |
|---|---|---|
| `to_state(next_state, next_input, output)` | 转本分支下一状态 | 原子写新记录 state=next_state, progress=new；当前标 finished |
| `to_substate(substate, output)` | 留在当前状态，更新 checkpoint | 原地更新 substate，progress 保持 in-progress，续 lease |
| `spawn(handler, child_input, output)` | 派生子分支调另一 agent | 建子分支记录；当前分支 progress=waiting |
| `finish(output)` | 本分支成功结束 | 当前标 finished，无后继 |
| `fail(retryable, reason)` | 失败 | progress=error, retryable=flag |

---

## 状态 1：VALIDATE —— 驱动自己到下一个子状态

state 内部本身是多步（先查租户，再查配额）。每完成一个内部步骤就 `to_substate` 落 checkpoint，崩溃后从最后的 substate 继续，不重跑已完成的内部步骤。

```python
def validate(self, input, substate):
    # substate 是 worker 自己定义的、能据以恢复的 checkpoint
    step = (substate or {}).get("step", "check_tenant")

    if step == "check_tenant":
        # —— 有副作用的外部调用，自带幂等键（幂等是 worker 的责任）——
        tenant = tenant_client.get(input["tenant_id"])
        if not tenant:
            return fail(retryable=False, reason="tenant not found")
        # 内部步骤完成，推进子状态。output 记录中间结果供审计
        return to_substate(
            substate={"step": "check_quota", "tenant_ok": True},
            output={"tenant": tenant["id"]},
        )

    if step == "check_quota":
        quota = tenant_client.remaining_quota(input["tenant_id"])
        if quota <= 0:
            # 业务失败但技术成功（Saga 语义）：可重试（也许配额会释放）
            return fail(retryable=True, reason="quota exhausted")
        # VALIDATE 整体完成，转到下一个 state，并把 PROVISION 需要的入参裁出来
        return to_state(
            next_state="PROVISION",
            next_input={
                "tenant_id": input["tenant_id"],
                "email": input["email"],
                "role": input["role"],
            },
            output={"validated": True, "quota_left": quota},
        )
```

**恢复演示**：worker 跑完 `check_tenant`、落了 `substate={step:check_quota}` 后进程崩溃。manager 发现 lease 过期，用**同 state=VALIDATE + substate={step:check_quota}** 重新拉起 worker。worker 读到 step 已是 `check_quota`，直接从查配额开始，**不重查租户**。这就是"已完成步骤不重跑"。

---

## 状态 2：PROVISION —— 驱动另一个 agent

在 Pod 上建用户后，需要一个独立的 `audit-worker` 做合规审计。worker 用 `spawn` 派生子分支，当前分支进入 `waiting`，等子分支跑完再继续。

```python
def provision(self, input, substate):
    step = (substate or {}).get("step", "create_user")

    if step == "create_user":
        # 幂等键 = workid+state，Pod 侧去重，重放不会建两个用户
        result = pod_client.create_user(
            tenant_id=input["tenant_id"],
            email=input["email"],
            role=input["role"],
            idempotency_key=input.get("_idem_key"),  # manager 透传的幂等键
        )
        if result.transient_error:      # POD_TIME_OUT / RATE_LIMIT 等
            return fail(retryable=True, reason=result.error)
        # 用户建好，派生 audit-worker 子分支做审计
        return spawn(
            handler="audit-worker",
            child_input={"user_id": result.user_id, "tenant_id": input["tenant_id"]},
            output={"user_id": result.user_id, "awaiting_audit": True},
        )

    # 子分支审计完成后，manager 把父分支从 waiting 改回 new 并回写子分支结果，
    # 再次拉起时 substate 里带上子分支产出
    if step == "audit_done":
        audit = substate["audit_result"]
        if not audit["passed"]:
            return fail(retryable=False, reason="audit failed: " + audit["reason"])
        return to_state(
            next_state="NOTIFY",
            next_input={"user_id": substate["user_id"], "email": input["email"]},
            output={"provisioned": True, "audit": "passed"},
        )
```

**spawn 的语义**：
- manager 收到 `spawn` → 在**新 branchId**（如 `0001`）下建子分支根记录，`handler=audit-worker`，`parentSk` 指回当前 PROVISION 步的 SK；当前父分支记录标 `progress=waiting`。
- 子分支由 manager 当作独立任务调度、跑 audit-worker，完全隔离。
- 子分支 `finish` 时，manager 顺 `parentSk` 找到父分支，把父分支 `waiting → new`，并将子分支 output 写进父分支下一步的 substate（`step=audit_done`, `audit_result=...`）。父分支被重新拉起继续。

> 父子如何互相通知，是 manager 的机制（见设计文档 §7）；worker 只需声明 `spawn` 和处理 `audit_done`。

---

## 状态 3：NOTIFY —— 成功结束

```python
def notify(self, input, substate):
    email_client.send_welcome(
        input["email"],
        idempotency_key=input["user_id"],   # 幂等：重放不会发两封
    )
    # 本分支到此成功结束，无后继状态
    return finish(output={"notified": True, "user_id": input["user_id"]})
```

manager 收到 `finish` → 当前记录标 `progress=finished`，本分支结束。若这是根分支且无未完成子分支，整棵任务树完成。

---

## 写一个新 worker 的清单

1. **定义状态枚举**：几个大阶段（本例 3 个）。
2. **实现 `run(input, state, substate)`**：按 state 分派。
3. **每个 state 内**：
   - 有内部多步 → 用 `to_substate` 落 checkpoint，保证崩溃可从中间恢复。
   - 外部调用 → **自带幂等键**（模版不替你保证 tool 幂等）。
   - 完成本阶段 → `to_state` 转下一状态，并裁出下一状态的 input。
   - 需要别的 agent → `spawn`，处理它回来的结果（约定一个 `*_done` 子状态）。
   - 成功 → `finish`；失败 → `fail(retryable=?)`，区分可重试 vs 终态。
4. **route 保持纯函数**：只读 output/substate，不做外部调用。所有副作用留在 enter/run 里。
5. **substate / input / output 用 JSON-可序列化对象**：manager 负责存取，你只管业务字段含义。

你不需要写的：DynamoDB 读写、PK/SK 拼接、lease、重试计数、超时检测、历史查询、"我是不是在重试"——全是 manager + 状态存储 skill 的事。
