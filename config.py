"""Central configuration + the shared Groq LLM used by every agent."""

import os

from crewai import LLM

GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"  # Groq's OpenAI-compatible endpoint

# How much work each depth level is allowed to do. This is what keeps runs fast.
# Groq's FREE plan allows only ~8,000 tokens per minute for gpt-oss-120b, so every
# extra search / long answer = waiting. Small limits here = short runs.
#   questions = research questions the Planner writes
#   searches  = max web/news searches the Researcher may run
#   pages     = max web pages the Researcher may open
#   verify    = max claims the Analyst re-checks with a search
#   notes     = max words for the Researcher's and Analyst's notes
#   report    = target words for the final report
DEPTH_SETTINGS = {
    "Quick": {"questions": 3, "searches": 2, "pages": 0, "verify": 1, "notes": 150, "report": 350},
    "Standard": {"questions": 4, "searches": 3, "pages": 1, "verify": 2, "notes": 220, "report": 600},
    "Deep": {"questions": 6, "searches": 6, "pages": 2, "verify": 3, "notes": 320, "report": 900},
}


def depth_cfg(depth: str) -> dict:
    return DEPTH_SETTINGS.get(depth, DEPTH_SETTINGS["Standard"])


def get_llm(
    api_key: str | None = None,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1500,
) -> LLM:
    """Build a Groq-backed LLM. Agents share the same settings; only max_tokens differs."""
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is missing. Add it in the sidebar or in Streamlit Secrets.")
    # provider="openai" = "use the OpenAI-compatible protocol". Without it, CrewAI strips the
    # "openai/" part of the model name and Groq rejects "gpt-oss-120b" with a 404.
    return LLM(
        model=model or GROQ_MODEL,
        provider="openai",
        base_url=GROQ_BASE_URL,
        api_key=key,
        temperature=temperature,
        max_tokens=max_tokens,  # small cap = fewer tokens reserved per request
        reasoning_effort="low",  # gpt-oss "thinks" before every step; low = much faster
        timeout=120,
        max_retries=6,  # if Groq says "rate limit, wait", wait and retry instead of crashing
    )
