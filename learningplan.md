## Week 1 — Plugins & Tool Use

**What you're learning:** How LLMs use external tools; how Claude Code plugins work as a pattern.

**Primary resources:**
- Claude Code official documentation (docs.anthropic.com/claude-code)
- Anthropic Tool Use documentation — start here, not OpenAI's
- Anthropic's "Build with Claude" quickstart

**Secondary:**
- DeepLearning.AI *Functions, Tools, and Agents with LangChain* (short, practical)

**Practice:** Build a minimal tool — a GitHub issue fetcher or a weather lookup — connect it via the Anthropic API, and observe how the model decides when to invoke it. This replicates the "live demo" from Week 1 without needing the PRH hub.

---

## Week 2 — Skills, Commands, and Agents

**What you're learning:** Prompt architecture — when to use a reusable prompt vs. a triggered shortcut vs. a full reasoning loop.

| Workshop concept | Public equivalent |
|---|---|
| Skill | Reusable structured system prompt |
| Slash command | Triggered shortcut prompt |
| Agent | Multi-step tool-using reasoning loop |

**Primary resources:**
- Anthropic prompt engineering guide (docs.anthropic.com)
- Claude Code slash commands documentation
- Anthropic's agent patterns documentation

**Secondary (pick one agent framework, not all three):**
- LangGraph — most production-realistic; good for understanding stateful agent loops

**Practice:** Build a `/summarize-pr` slash command, then extend it into a small agent that fetches a file, summarizes it, and outputs a structured markdown comment. That progression from command → agent is exactly what Week 2 is teaching.

---

## Week 3 — Creating Skills (YAML + Markdown)

**What you're learning:** How to write structured, reusable prompt templates with metadata headers.

**Primary resources:**
- "Learn YAML in Y minutes" (learnxinyminutes.com/yaml) — 20 minutes, sufficient
- Markdown Guide (markdownguide.org)
- Anthropic system prompt documentation and prompt library
- Claude Code custom commands documentation

**Practice:** Design three skills relevant to your own work. Each should have a YAML header (name, description, input schema) and a clear system prompt with a strict output format. The exact domain is up to you — the skill-design discipline is the transferable thing here.

⚠️ Note: There's no detailed public documentation specifically on "Claude Code skills" as a format. You'll synthesize from the Claude Code docs + prompt engineering principles. The format is learnable by examining examples in the Claude Code docs and the public MCP ecosystem.

---

## Week 4 — MCP Servers

**What you're learning:** The standardized protocol that lets Claude interact with local and remote data sources/tools.

**Primary resources:**
- modelcontextprotocol.io — the official spec and getting-started guides have improved a lot
- Anthropic MCP documentation
- The MCP GitHub repo (github.com/modelcontextprotocol) — has growing examples

**Practice:** Build a local MCP server (Node.js or Python) that reads a folder of markdown files and exposes a search tool. Connect it to Claude Code. This is the closest public equivalent to what the PRH integration would look like, and it's genuinely buildable in an afternoon.

⚠️ Expect some rough edges — MCP tooling is moving fast. The spec is stable but tutorials vary in quality. Official examples in the GitHub repo are the most reliable.

---

## Week 5 — Advanced Integrations & Automated Workflows

**What you're learning:** Connecting Claude to real APIs; building end-to-end AI-assisted workflows.

**Primary resources:**
- GitHub REST API docs (use GitHub instead of GitLab — same concepts, better public tooling)
- Notion API / Notion SDK docs
- Slack Bolt framework docs
- Anthropic API docs for building the AI layer

**Practice path (two options):**

*Option A — Low friction:* Use n8n (self-hostable) or Make to prototype the full workflow visually first: PR opened → Claude summarizes diff → Slack message posted → Notion task updated. This lets you learn the integration pattern without getting stuck on API boilerplate.

*Option B — Build from scratch:* Write the workflow in Python or Node, using each API's official SDK. More work, more durable knowledge.

**Capstone:** Whichever path you take, the end goal is the same workflow the expert described — new PR triggers an AI summary, a style check, a Slack notification, and a Notion update. That covers ~90% of what Week 5 teaches, with fully public tools.

---
