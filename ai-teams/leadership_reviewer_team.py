"""
leadership-reviewer 的 Agno 双 reviewer 领导层评审团队。

用法：
    pip install agno anthropic
    export ANTHROPIC_API_KEY=...
    python leadership_reviewer_team.py            # 评审默认报告
    python leadership_reviewer_team.py <path.md>  # 评审指定文档

设计：每个视角是一个 Agent；用 Team(mode="coordinate") 让 leader 把报告分发给两位
reviewer 并行评审，再汇总为 0–10 总评分与 Markdown 反馈（见 leadership-reviewer.md 模板）。
"""

from pathlib import Path
import sys
from textwrap import dedent

from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude

# 模型分层：子 reviewer 用 sonnet（省成本），leader 汇总用 opus（高能力）。
MEMBER_MODEL_ID = "claude-sonnet-5"
LEADER_MODEL_ID = "claude-opus-5"

SCORING = (
    "打分 0–10：0=与公司战略明显不匹配且投入产出比差，"
    "10=与战略高度一致、价值主张清晰且值得优先投入资源。"
    "必须给出打分理由与可执行建议。"
    "只从你自己的视角审查，不越界评论其他视角。"
)


def _member_model() -> Claude:
    return Claude(id=MEMBER_MODEL_ID)


def _leader_model() -> Claude:
    return Claude(id=LEADER_MODEL_ID)


leadership_strategy_agent = Agent(
    name="公司领导战略 reviewer",
    model=_member_model(),
    instructions=[
        "审查产品是否贴合 Salesforce 与 Tableau 的公司战略方向，"
        "是否值得投入资源推进；评估其商业叙事是否能吸引领导层，"
        "以及能否带来明确收益（收入增长、效率提升、生态协同）。",
        "避免陷入底层技术实现细节，重点看战略匹配与资源优先级。",
        SCORING,
    ],
)

leadership_secretary_agent = Agent(
    name="领导秘书 reviewer",
    model=_member_model(),
    instructions=[
        "审查文档结构与表达：内容取舍是否合理、重点是否突出、是否有冗余、"
        "排版是否便于领导快速理解与决策。",
        "重点检查技术设计和产品价值介绍是否分割合理；"
        "从领导阅读习惯出发，强调收益导向表达，弱化过深技术细节。",
        SCORING,
    ],
)

REVIEWERS = [leadership_strategy_agent, leadership_secretary_agent]

leadership_reviewer_team = Team(
    name="leadership-reviewer",
    mode="coordinate",
    model=_leader_model(),
    members=REVIEWERS,
    instructions=[
        "你是领导层评审团队 leader。把待评审文档分发给两位 reviewer 并行评审，"
        "收集各自分项评分（0–10）、理由与建议。",
        "本轮总评分 = 两项加权平均（默认等权，保留 1 位小数）。",
        "按 leadership-reviewer.md 的模板输出 Markdown：开头给出总评分与一句话结论，"
        "随后分项评审、关键建议、待回应问题。",
    ],
    show_members_responses=True,
    markdown=True,
)


def review(doc_path: str) -> str:
    text = Path(doc_path).read_text(encoding="utf-8")
    prompt = dedent(
        f"""
        请从公司领导层视角评审以下设计文档，按团队职责分别打分并汇总为 0–10 总评分，
        产出符合 leadership-reviewer.md 模板的 Markdown 反馈。

        === 文档开始 ({doc_path}) ===
        {text}
        === 文档结束 ===
        """
    )
    result = leadership_reviewer_team.run(prompt)
    return result.content


if __name__ == "__main__":
    # 报告已拆分为两份交叉引用文档；领导层评审默认以可行性报告为主评审对象。
    default_doc = str(Path(__file__).parent / ".." / "docs" / "distributed-orchestrator-project-analyst.md")
    doc = sys.argv[1] if len(sys.argv) > 1 else default_doc
    print(review(doc))
