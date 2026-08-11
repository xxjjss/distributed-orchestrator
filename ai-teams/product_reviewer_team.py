"""
product-reviewer 的 Agno 四专家产品评审团队。

用法：
    pip install agno anthropic
    export ANTHROPIC_API_KEY=...
    python product_reviewer_team.py            # 评审默认报告
    python product_reviewer_team.py <path.md>  # 评审指定文档

设计：每个视角是一个 Agent；用 Team(mode="coordinate") 让 leader 把报告分发给四位
专家并行评审，再汇总为 0–10 总评分与 Markdown 反馈（见 product-reviewer.md 的模板）。
"""

from pathlib import Path
import sys
from textwrap import dedent

from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude

# 模型分层：四位子 agent 用 sonnet（省成本），leader 汇总用 opus（高能力）。
# 如需切换到 Bedrock/网关或其他版本，只改这两个常量即可。
MEMBER_MODEL_ID = "claude-sonnet-5"
LEADER_MODEL_ID = "claude-opus-5"

# 全体专家共享的评分标准，拼进每个 agent 的 instructions，保证打分口径一致。
SCORING = (
    "打分 0–10：0=毫无价值（已有免费且更强更易用的竞品），"
    "10=商业上完全可行、客户有实际需求且预期接受度极好。"
    "必须给出打分理由；如有更优/替代方案给出建议，替代方案附开源链接或产品说明链接。"
    "只从你自己的视角审查，不越界评论其他视角。"
)


def _member_model() -> Claude:
    return Claude(id=MEMBER_MODEL_ID)


def _leader_model() -> Claude:
    return Claude(id=LEADER_MODEL_ID)


# ── 四个领域专家（对应 product-reviewer.md 的四个视角）─────────────────────
sfdc_architect_agent = Agent(
    name="Salesforce 架构与研发 Lead",
    model=_member_model(),
    instructions=[
        "审查是否符合 Salesforce 架构规范（Apex/LWC/Flow）、数据安全与 Managed Package 逻辑、"
        "是否会撞上 Governor Limits、对 Data Cloud 或 Agentforce 的集成路径是否合理，"
        "以及 AppExchange Security Review 风险。",
        SCORING,
    ],
)

fde_strategy_agent = Agent(
    name="FDE 交付与现场实施专家",
    model=_member_model(),
    instructions=[
        "审查项目在企业客户现场（一期是公司内部，即用户是开发人员）的实际落地可行性"
        "（Time-to-Value）、客户已有 Salesforce 遗留系统（Org Customizations）的兼容卡点、"
        "如何将 FDE 交付中的客户定制能力转化为可标准化的 IP/模块。",
        SCORING,
    ],
)

business_adoption_agent = Agent(
    name="B2B 商业前景与客户接受度专家",
    model=_member_model(),
    instructions=[
        "评估买方（CIO / VP of Sales / Admin）的买单意愿、Salesforce 用户的交互习惯与接受度、"
        "定价逻辑、AppExchange 生态竞品壁垒与投资回报率（ROI）。",
        SCORING,
    ],
)

engineering_cost_agent = Agent(
    name="研发工程 Ops 与成本风险专家",
    model=_member_model(),
    instructions=[
        "测算研发周期与人力成本、Salesforce API 额度与 LLM Token 双重开销、运维/支持"
        "（Support）隐藏成本，评估技术债务与延期风险。",
        SCORING,
    ],
)

REVIEWERS = [
    sfdc_architect_agent,
    fde_strategy_agent,
    business_adoption_agent,
    engineering_cost_agent,
]

# ── Team leader：分发、汇总、按权重给总分、按模板产出 Markdown ─────────────
product_reviewer_team = Team(
    name="product-reviewer",
    mode="coordinate",
    model=_leader_model(),
    members=REVIEWERS,
    instructions=[
        "你是产品评审团队 leader。把待评审文档分发给全部四位专家并行评审，收集各自的"
        "分项评分（0–10）、理由与建议。",
        "本轮总评分 = 四项加权平均（默认等权，保留 1 位小数）；若某视角不适用则说明并"
        "将其排除出加权。",
        "按 product-reviewer.md 的反馈模板输出 Markdown：开头给出总评分与一句话结论，"
        "随后分项评审、关键建议、未解决问题。替代方案必须附链接。",
    ],
    show_members_responses=True,
    markdown=True,
)


def review(doc_path: str) -> str:
    text = Path(doc_path).read_text(encoding="utf-8")
    prompt = dedent(
        f"""
        请从产品维度评审以下技术设计文档，按团队职责各视角打分并汇总为 0–10 总评分，
        产出符合 product-reviewer.md 模板的 Markdown 反馈。

        === 文档开始 ({doc_path}) ===
        {text}
        === 文档结束 ===
        """
    )
    result = product_reviewer_team.run(prompt)
    return result.content


if __name__ == "__main__":
    # 报告已拆分为两份交叉引用文档；产品评审默认以可行性报告为主评审对象。
    default_doc = str(Path(__file__).parent / ".." / "docs" / "distributed-orchestrator-project-analyst.md")
    doc = sys.argv[1] if len(sys.argv) > 1 else default_doc
    print(review(doc))
