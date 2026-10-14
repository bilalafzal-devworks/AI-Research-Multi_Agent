# 🧠 AI Research Team

A multi-agent research app. You type a topic, and **four specialised AI agents** work one after another: they plan the research, search the web, fact-check the claims, and write a clean report with sources. You can watch which agent is working at every moment.

Built with **CrewAI** (agents), **Groq** (LLM) and **Streamlit** (UI).

---

## ✨ Features

- **4 agents, one file each**: easy to read, change, or extend
- **Real tools**: every agent uses tools (web search, news search, page reader, link checker)
- **Live progress**: agent cards light up (Waiting → Working now → Done), plus a live feed of tool calls and a timer
- **3 depth levels**: Quick, Standard and Deep control how much work the team does
- **Report output**: read it in the app, view the raw Markdown, or download it as a `.md` file
- **Secure by design**: the API key lives in Streamlit Secrets and is never typed into the page

---

## 🤖 The team

| # | Agent | What it does | Tools it uses |
|---|-------|--------------|---------------|
| 1 | 🧭 **Research Planner** | Turns your topic into focused research questions | `web_search` |
| 2 | 🔎 **Web Researcher** | Finds facts and collects a source link for each | `web_search`, `news_search`, `read_webpage`* |
| 3 | 🧪 **Fact-Check Analyst** | Re-checks the key claims and marks them VERIFIED / UNCERTAIN | `web_search` |
| 4 | ✍️ **Report Writer** | Checks the source links, then writes the final report | `check_links` |

\*`read_webpage` is only available in Standard and Deep.

The agents run **in order** (sequential process). Each agent only receives the notes it needs from the earlier ones, which keeps requests small and fast.

### The tools (`tools.py`)

| Tool | Purpose |
|------|---------|
| `web_search` | Searches the web with DuckDuckGo and returns the top 4 results |
| `news_search` | Searches recent news articles |
| `read_webpage` | Opens a page and returns its readable text (first 2,500 characters) |
| `check_links` | Checks up to 8 source URLs and marks each OK or DEAD |

---

## ⚙️ Research depth

The depth setting in the sidebar puts a hard limit on how much each agent may do.

| Depth | Questions | Searches | Pages opened | Claims verified | Report length |
|-------|-----------|----------|--------------|-----------------|---------------|
| **Quick** (default) | 3 | 2 | 0 | 1 | ~350 words |
| **Standard** | 4 | 3 | 1 | 2 | ~600 words |
| **Deep** | 6 | 6 | 2 | 3 | ~900 words |

You can change these numbers in `config.py` (`DEPTH_SETTINGS`).

---

## 🗂️ Project structure

Everything sits in one folder, with no sub-folders to manage.

```
├── app.py                 # Streamlit user interface
├── crew.py                # Connects the 4 agents into one crew and runs it
├── config.py              # Groq model setup and depth settings
├── tools.py               # The 4 tools the agents can call
├── agent_planner.py       # Agent 1: Research Planner
├── agent_researcher.py    # Agent 2: Web Researcher
├── agent_analyst.py       # Agent 3: Fact-Check Analyst
├── agent_writer.py        # Agent 4: Report Writer
├── requirements.txt       # Python libraries (pinned versions)
├── README.md              # This file
├── .gitignore
└── .streamlit/
    └── config.toml        # Theme colour (optional)
```

---

## 🚀 Deploy it (no installation needed)

You only need a browser and two free accounts: **GitHub** and **Streamlit Community Cloud**.

### 1. Get a Groq API key

1. Go to [console.groq.com](https://console.groq.com) and sign in.
2. Open **API Keys** and click **Create API Key**.
3. Copy the key (it starts with `gsk_`). It is shown only once.

### 2. Upload the project to GitHub

1. On GitHub click **+ → New repository**, name it, choose **Public**, and create it.
2. Click **uploading an existing file**.
3. Drag in **all the files** from this project (the 9 `.py` / `.txt` files, plus `.streamlit/config.toml` if you want the theme).
4. Click **Commit changes**.
5. Check that the repo's main page lists `app.py`, `crew.py`, `config.py`, `tools.py`, `requirements.txt` and the four `agent_*.py` files.

### 3. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **Create app → Deploy a public app from GitHub**.
3. Choose your repository, branch `main`, and main file path `app.py`.
4. Click **Advanced settings**:
   - **Python version**: `3.12`
   - **Secrets**: paste this with your real key
     ```toml
     GROQ_API_KEY = "gsk_your_key_here"
     ```
5. Click **Deploy**. The first build takes a few minutes.

> **Never write your API key inside any file in the repo.** Public repos are scanned by bots within minutes. Keep it only in Streamlit Secrets.

To change the key later: **Manage app → Settings → Secrets**, save, then **Reboot app**.

---

## 🧪 Run it on your own computer (optional)

```bash
pip install -r requirements.txt
export GROQ_API_KEY="gsk_your_key_here"     # Windows PowerShell: $env:GROQ_API_KEY="gsk_..."
streamlit run app.py
```

CrewAI needs Python **3.10 to 3.13**.

---

## 🧰 Tech stack

| Library | Version | Used for |
|---------|---------|----------|
| [CrewAI](https://github.com/crewAIInc/crewAI) | 1.15.28 | Agents, tasks, crew |
| [Streamlit](https://streamlit.io) | 1.65.0 | Web interface |
| [ddgs](https://pypi.org/project/ddgs/) | 9.16.0 | DuckDuckGo web and news search |
| beautifulsoup4 | 4.15.0 | Reading web pages |
| httpx | 0.28.1 | Fetching pages and checking links |

**LLM:** `openai/gpt-oss-120b` on [Groq](https://groq.com), connected through Groq's OpenAI-compatible endpoint (`https://api.groq.com/openai/v1`).

---

## ⏱️ About speed and limits

Groq's **free plan** limits how many tokens per minute you can use. For `gpt-oss-120b` that is **8,000 tokens per minute** and **200,000 per day** (check yours at [console.groq.com/settings/limits](https://console.groq.com/settings/limits)). When the limit is reached, the app simply waits for the next minute, and a message appears in the UI.

What this means for you:

- Expect a **Quick** run to take a few minutes on the free plan.
- Use **Quick** or **Standard** for most topics. **Deep** will wait more often.
- A paid Groq plan has much higher limits and makes runs much faster.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| Red box: *"A project file is missing…"* | A file was not uploaded. Compare your repo's main page with the file list above. |
| *"The Groq API key is not set"* | Add `GROQ_API_KEY` in **Manage app → Settings → Secrets**, save, and reboot. |
| `Model gpt-oss-120b not found` (404) | Keep `provider="openai"` in `config.py`. Without it, CrewAI shortens the model name and Groq rejects it. |
| Build error mentioning Python | Redeploy with Python **3.12** selected in Advanced settings. |
| Very slow run | Use **Quick** depth. The free plan token limit is the most likely cause (see above). |
| `Search failed` in a tool result | DuckDuckGo sometimes throttles shared servers. The agents continue, and retrying usually works. |
| Changes on GitHub not showing | Open **Manage app → Reboot app**. |

---

## ➕ Add your own agent

1. Copy `agent_analyst.py` to `agent_yourname.py`. Change `NAME`, `ICON`, `ROLE`, and the `Agent` and `Task` text inside `build()`.
2. In `crew.py`, import it, add it to the `TEAM` list, and build it in `run_crew()` with the notes it should receive.
3. The UI cards and the live feed pick it up automatically. The card grid is 4 columns wide, so a fifth agent wraps onto a second row.

Add new tools in `tools.py` with the `@tool("name")` decorator, then pass them in an agent's `tools=[...]` list.

---

## 🔒 Security notes

- The API key is read only from Streamlit Secrets (or the `GROQ_API_KEY` environment variable). There is no key box on the page.
- Anyone who can open your deployed app can run research on **your** Groq quota. To limit that, restrict who can view the app in the app's **Share** settings.
- If a key is ever exposed (pasted in a screenshot, chat, or file), create a new one in the Groq console and delete the old one.

---

## 👤 Author

Built by **M. Bilal**, [github.com/bilalafzal-devworks](https://github.com/bilalafzal-devworks)
