"""Agent 2 - Web Researcher: gathers facts and sources using search tools."""

from crewai import Agent, Task

from config import depth_cfg
from tools import news_search, read_webpage, web_search

NAME = "Web Researcher"
ICON = "🔎"
ROLE = "Searches the web and collects facts with sources"


def build(llm, topic: str, depth: str, context_tasks: list):
    cfg = depth_cfg(depth)
    searches, pages = cfg["searches"], cfg["pages"]

    tools = [web_search, news_search]
    page_rule = "Do NOT open web pages."
    if pages:
        tools.append(read_webpage)
        page_rule = f"You may open at most {pages} web page(s) with read_webpage."

    agent = Agent(
        role="Web Researcher",
        goal="Collect accurate, up-to-date facts with source links for the research questions.",
        backstory=(
            "You are a meticulous online researcher. You never guess: every fact "
            "you report comes from a search result or a web page you opened."
        ),
        tools=tools,
        llm=llm,
        allow_delegation=False,
        # hard stop: CrewAI forces a final answer when this many steps are used
        max_iter=searches + pages + 2,
        verbose=False,
    )
    task = Task(
        name=NAME,
        description=(
            f"Topic: {topic}\nResearch depth: {depth}\n\n"
            "Use the research plan to find facts. STRICT LIMITS: "
            f"at most {searches} searches in total (web_search and news_search combined). "
            f"{page_rule} Each search should cover several questions at once. "
            "When you reach the limit, STOP searching and write your findings. "
            f"Write short bullet points with a source URL each. Maximum {cfg['notes']} words."
        ),
        expected_output=f"Short bullet-point findings with a source URL each (max {cfg['notes']} words).",
        agent=agent,
        context=context_tasks,
    )
    return agent, task
