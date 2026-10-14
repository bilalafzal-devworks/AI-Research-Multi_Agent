"""Agent 4 - Report Writer: checks the sources, then writes the final markdown report."""

from crewai import Agent, Task

from config import depth_cfg
from tools import check_links

NAME = "Report Writer"
ICON = "✍️"
ROLE = "Checks sources and writes the final report"


def build(llm, topic: str, depth: str, context_tasks: list):
    words = depth_cfg(depth)["report"]
    agent = Agent(
        role="Report Writer",
        goal="Write a clear, well-organised research report that a beginner can understand.",
        backstory=(
            "You are an expert technical writer. You turn verified research into "
            "polished reports with simple language and only working source links."
        ),
        tools=[check_links],
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )
    task = Task(
        name=NAME,
        description=(
            f"Topic: {topic}\n\n"
            "Step 1: call the check_links tool ONCE with the source URLs from the research notes. "
            "Do not cite any URL it marks DEAD.\n"
            f"Step 2: write the final report in Markdown, about {words} words, with these sections: "
            "# Title, ## Executive Summary, ## Key Findings, ## Analysis, "
            "## Risks & Open Questions, ## Sources (bullet list of URLs). "
            "Use only facts from the research notes. "
            "Your final answer must be the complete Markdown report."
        ),
        expected_output=f"The complete final report in Markdown (about {words} words).",
        agent=agent,
        context=context_tasks,
    )
    return agent, task
