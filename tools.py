"""Tools that the agents can call. All of them work online only (no local installs)."""

import re
from concurrent.futures import ThreadPoolExecutor

import httpx
from bs4 import BeautifulSoup
from crewai.tools import tool
from ddgs import DDGS


@tool("web_search")
def web_search(query: str) -> str:
    """Search the web for a query and return the top results (title, link, snippet)."""
    try:
        results = DDGS(timeout=10).text(query, max_results=4)  # short timeout = no long hangs
    except Exception as exc:  # network / rate-limit errors should not crash the crew
        return f"Search failed: {exc}. Try a shorter or different query."
    if not results:
        return "No results found. Try different keywords."
    lines = []
    for i, r in enumerate(results, 1):
        snippet = (r.get("body", "") or "")[:300]  # short snippets keep every LLM step fast
        lines.append(f"{i}. {r.get('title', '')}\n   URL: {r.get('href', '')}\n   {snippet}")
    return "\n\n".join(lines)


@tool("news_search")
def news_search(query: str) -> str:
    """Search recent news articles for a query and return title, source, date, link and snippet."""
    try:
        results = DDGS(timeout=10).news(query, max_results=4)
    except Exception as exc:
        return f"News search failed: {exc}."
    if not results:
        return "No recent news found."
    lines = []
    for i, r in enumerate(results, 1):
        snippet = (r.get("body", "") or "")[:300]
        lines.append(
            f"{i}. {r.get('title', '')} ({r.get('source', 'unknown')}, {r.get('date', '')})\n"
            f"   URL: {r.get('url', '')}\n   {snippet}"
        )
    return "\n\n".join(lines)


@tool("read_webpage")
def read_webpage(url: str) -> str:
    """Download a web page and return its main readable text (first ~2500 characters)."""
    try:
        resp = httpx.get(
            url,
            timeout=10,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (ResearchTeamBot)"},
        )
        resp.raise_for_status()
    except Exception as exc:
        return f"Could not open {url}: {exc}"
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return text[:2500] if text else "The page had no readable text."


def _check_one(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (ResearchTeamBot)"}
    try:
        resp = httpx.head(url, timeout=6, follow_redirects=True, headers=headers)
        if resp.status_code in (403, 405, 501):  # many sites refuse HEAD or bots; try a normal GET
            resp = httpx.get(url, timeout=6, follow_redirects=True, headers=headers)
        if resp.status_code < 400:
            return f"OK   {url}"
        if resp.status_code in (401, 403, 429):
            return f"OK   {url} (site blocks bots but the page exists)"
        return f"DEAD {url} (HTTP {resp.status_code})"
    except Exception:
        return f"DEAD {url} (could not connect)"


@tool("check_links")
def check_links(urls: str) -> str:
    """Check which source URLs really work. Pass the URLs you plan to cite, separated by spaces or new lines."""
    raw = re.findall(r"https?://[^\s<>\")\]]+", urls)
    found = list(dict.fromkeys(u.rstrip(".,;:!?'") for u in raw))[:8]  # drop trailing punctuation
    if not found:
        return "No URLs found in the input."
    with ThreadPoolExecutor(max_workers=8) as pool:
        return "\n".join(pool.map(_check_one, found))
