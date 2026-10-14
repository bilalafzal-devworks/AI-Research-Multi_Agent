"""Agent 3 - Fact-Check Analyst: verifies claims and extracts insights."""

from crewai import Agent, Task

from config import depth_cfg
from tools import web_search

NAME = "Fact-Check Analyst"
ICON = "🧪"
ROLE = "Verifies key claims and extracts insights"


def build(llm, topic: str, depth: str, context_tasks: list):
    cfg = depth_cfg(depth)
    n = cfg["verify"]
    agent = Agent(
        role="Fact-Check Analyst",
        goal="Verify the most important claims and turn raw findings into insights.",
        backstory=(
            "You are a skeptical analyst. You cross-check important claims with a "
            "second source, flag anything doubtful, and look for patterns and trade-offs."
        ),
        tools=[web_search],
        llm=llm,
        allow_delegation=False,
        max_iter=n + 2,
        verbose=False,
    )
    task = Task(
        name=NAME,
        description=(
            f"Topic: {topic}\n\n"
            "Review the researcher's findings. "
            f"Pick the {n} most important claim(s) and verify each with ONE web_search "
            f"(at most {n} searches in total). Then write: key insights, "
            "risks or trade-offs, and the claims marked VERIFIED / UNCERTAIN. "
            f"Maximum {cfg['notes']} words."
        ),
        expected_output=f"Insights, risks, and a VERIFIED/UNCERTAIN claim list (max {cfg['notes']} words).",
        agent=agent,
        context=context_tasks,
    )
    return agent, task
