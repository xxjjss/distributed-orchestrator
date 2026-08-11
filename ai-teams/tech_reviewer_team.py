"""
tech-reviewer 的 Agno 六专家评审团队。

用法：
    pip install agno anthropic
    export ANTHROPIC_API_KEY=...
    python tech_reviewer_team.py            # 评审默认报告
    python tech_reviewer_team.py <path.md>  # 评审指定文档

设计：每个视角是一个 Agent；用 Team(mode="coordinate") 让 leader 把报告分发给六位
专家并行评审，再汇总为 0–10 总评分与 Markdown 反馈（见 tech-reviewer.md 的模板）。
"""

from pathlib import Path
import sys
from textwrap import dedent

from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude

# 模型分层：六位子 agent 用 sonnet（省成本），leader 汇总用 opus（高能力）。
# 如需切换到 Bedrock/网关或其他版本，只改这两个常量即可。
MEMBER_MODEL_ID = "claude-sonnet-5"
LEADER_MODEL_ID = "claude-opus-5"

# 全体专家共享的评分标准，拼进每个 agent 的 instructions，保证打分口径一致。
SCORING = (
    "打分 0–10：0=毫无价值，10=技术上完全可行且暂无更好方案。"
    "必须给出打分理由；如有更优/替代方案给出建议，替代方案若为开源则附链接。"
    "只从你自己的视角审查，不越界评论其他视角。"
)


def _member_model() -> Claude:
    return Claude(id=MEMBER_MODEL_ID)


def _leader_model() -> Claude:
    return Claude(id=LEADER_MODEL_ID)


# ── 六个领域专家（对应 tech-reviewer.md 的六个视角）─────────────────────────
open_source_expert = Agent(
    name="开源架构专家",
    model=_member_model(),
    instructions=[
        "审查各部分功能实现的方法：所用开源系统在功能、安全、授权（License）上是否有顾虑；"
        "自研部分是否有重复开发的嫌疑，是否有更好更经济的替代方案。",
        SCORING,
    ],
)

distributed_expert = Agent(
    name="分布式系统架构专家",
    model=_member_model(),
    instructions=[
        "审查 CAP 权衡、幂等性、去重键，以及状态落盘（SQLite/DynamoDB/Redis 等）机制。",
        SCORING,
    ],
)

sre_expert = Agent(
    name="SRE 容错专家",
    model=_member_model(),
    instructions=[
        "审查断点续传（Crash-Recovery）、熔断、重试与 SPOF（单点故障）风险。",
        SCORING,
    ],
)

protocol_expert = Agent(
    name="异构通信协议专家",
    model=_member_model(),
    instructions=[
        "审查异构系统、多 runtime、不同大模型下 agent 之间的调用转换及安全鉴权。",
        SCORING,
    ],
)

ux_expert = Agent(
    name="分布式 UX 专家",
    model=_member_model(),
    instructions=[
        "审查高延迟与部分失败状态如何抽象并呈现在 UI 上，以及 UI 的简洁易用与低学习成本。",
        SCORING,
    ],
)

salesforce_expert = Agent(
    name="Salesforce 产品专家",
    model=_member_model(),
    instructions=[
        "审查与 Salesforce 现有产品的耦合程度，是否能方便支持并扩展到其他 Salesforce 产品。",
        SCORING,
    ],
)

REVIEWERS = [
    open_source_expert,
    distributed_expert,
    sre_expert,
    protocol_expert,
    ux_expert,
    salesforce_expert,
]

# ── Team leader：分发、汇总、按权重给总分、按模板产出 Markdown ─────────────
tech_reviewer_team = Team(
    name="tech-reviewer",
    mode="coordinate",
    model=_leader_model(),
    members=REVIEWERS,
    instructions=[
        "你是技术评审团队 leader。把待评审文档分发给全部六位专家并行评审，收集各自的"
        "分项评分（0–10）、理由与建议。",
        "本轮总评分 = 六项加权平均（默认等权，保留 1 位小数）；若某视角不适用则说明并"
        "将其排除出加权。",
        "按 tech-reviewer.md 的反馈模板输出 Markdown：开头给出总评分与一句话结论，"
        "随后分项评审、关键建议、未解决问题。开源替代方案必须附链接。",
    ],
    show_members_responses=True,
    markdown=True,
)


def review(doc_path: str) -> str:
    text = Path(doc_path).read_text(encoding="utf-8")
    prompt = dedent(
        f"""
        请评审以下技术设计文档，按团队职责各视角打分并汇总为 0–10 总评分，
        产出符合 tech-reviewer.md 模板的 Markdown 反馈。

        === 文档开始 ({doc_path}) ===
        {text}
        === 文档结束 ===
        """
    )
    result = tech_reviewer_team.run(prompt)
    return result.content


if __name__ == "__main__":
    # 报告已拆分为两份交叉引用文档；技术评审默认以技术设计文档为主评审对象。
    default_doc = str(Path(__file__).parent / ".." / "docs" / "distributed-orchestrator-tech-design.md")
    doc = sys.argv[1] if len(sys.argv) > 1 else default_doc
    print(review(doc))
