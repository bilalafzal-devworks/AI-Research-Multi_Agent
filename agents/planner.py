"""Agent 1 - Research Planner: breaks the topic into focused questions."""

from crewai import Agent, Task

from config import depth_cfg
from tools import web_search

NAME = "Research Planner"
ICON = "🧭"
ROLE = "Breaks the topic into sharp research questions"


def build(llm, topic: str, depth: str):
    cfg = depth_cfg(depth)
    agent = Agent(
        role="Research Planner",
        goal="Turn a broad topic into a clear, focused research plan.",
        backstory=(
            "You are a senior research strategist. You quickly scan a topic, "
            "then define the smartest questions that must be answered."
        ),
        tools=[web_search],
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )
    task = Task(
        name=NAME,
        description=(
            f"Topic: {topic}\nResearch depth: {depth}\n\n"
            "1. Run exactly ONE quick web search to understand the topic's current landscape.\n"
            f"2. Produce a research plan with exactly {cfg['questions']} specific questions "
            "and 3 suggested search keywords. Maximum 100 words in total."
        ),
        expected_output="A short numbered list of research questions and 3 keywords (max 100 words).",
        agent=agent,
    )
    return agent, task
