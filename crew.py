"""Assembles the 4 agents into one sequential crew and runs it."""

from crewai import Crew, Process
from crewai.events import crewai_event_bus
from crewai.events.types.tool_usage_events import ToolUsageStartedEvent

from agents import analyst, planner, researcher, writer
from config import get_llm

# Order matters: this is the order the agents work in (and shown in the UI).
TEAM = [planner, researcher, analyst, writer]


def run_crew(topic: str, depth: str, api_key: str, on_event, model: str | None = None):
    """Run the research crew.

    on_event(kind, payload) is called with:
      ("agent_start", index)       -> agent number `index` begins working
      ("tool", (index, tool_name)) -> that agent called a tool
      ("agent_done", index)        -> agent number `index` finished
    Returns the final report text.
    """
    # The writer needs room for the full report; everyone else only writes short notes.
    llm_notes = get_llm(api_key, model, max_tokens=1500)
    llm_report = get_llm(api_key, model, max_tokens=3000)

    # Each agent only receives the notes it really needs. Sending everything to everyone
    # makes every request bigger, and Groq's free plan limits tokens per minute.
    plan_agent, plan_task = planner.build(llm_notes, topic, depth)
    res_agent, res_task = researcher.build(llm_notes, topic, depth, [plan_task])
    ana_agent, ana_task = analyst.build(llm_notes, topic, depth, [res_task])
    wri_agent, wri_task = writer.build(llm_report, topic, depth, [res_task, ana_task])

    agents = [plan_agent, res_agent, ana_agent, wri_agent]
    tasks = [plan_task, res_task, ana_task, wri_task]

    # Tool events are matched to the right agent by task name (works even if an event arrives late)
    name_to_index = {m.NAME: i for i, m in enumerate(TEAM)}
    role_to_index = {a.role: i for i, a in enumerate(agents)}
    state = {"current": 0}

    def task_cb(_output):
        on_event("agent_done", state["current"])
        state["current"] += 1
        if state["current"] < len(TEAM):
            on_event("agent_start", state["current"])

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        task_callback=task_cb,
        verbose=False,
        tracing=False,
    )

    # scoped_handlers() removes our listener when the run ends (no duplicates on Streamlit reruns)
    with crewai_event_bus.scoped_handlers():

        @crewai_event_bus.on(ToolUsageStartedEvent)
        def _on_tool(source, event):
            idx = name_to_index.get(getattr(event, "task_name", None))
            if idx is None:
                idx = role_to_index.get(getattr(event, "agent_role", None), state["current"])
            on_event("tool", (idx, str(event.tool_name)))

        on_event("agent_start", 0)
        result = crew.kickoff()
        crewai_event_bus.flush()  # make sure every tool event is delivered

    return getattr(result, "raw", None) or str(result)
