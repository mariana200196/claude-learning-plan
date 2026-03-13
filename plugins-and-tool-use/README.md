Fetch GitHub issues from using

1. Native MCP on Claude Code CLI: 
`github - list_issues (MCP)(owner: "mariana200196", repo: "claude-learning-plan")`
2. From-scratch script implementation from scratch:
`python plugins-and-tool-use/github_issue_fetcher.py "List open issues in mariana200196/claude-learning-plan"`
3. Script using claude agent SDK: `python plugins-and-tool-use/github_issue_fetcher.py "List open issues in mariana200196/claude-learning-plan. Use GitHub MCP."`





## Ways to Fetch GitHub Issues with Claude

1. **From-scratch implementation (`github_issue_fetcher.py`)**

Uses the *Anthropic Python SDK* directly.

You write everything yourself:

- Tool schemas (what tools exist and their parameters)
- Tool implementations (the actual GitHub REST API calls via `requests`)
- The agentic loop (sending tool results back to Claude, checking `stop_reason`, looping until `end_turn`)

**Communication flow:**

`Your script  ──HTTPS──▶  Anthropic API (Claude decides which tool to call)`
`Your script  ──HTTPS──▶  GitHub REST API (you execute the tool call)`

Claude never touches GitHub directly — your code does, and feeds the result back to Claude.

2. **Claude Code CLI + GitHub MCP (`claude` in terminal)**

You just type a prompt in the terminal. Claude Code handles everything.

The GitHub MCP server is configured in ~/.claude.json. When Claude Code needs GitHub tools, it:

1. Spawns the MCP server on-the-fly as a **local process** via `npx -y @modelcontextprotocol/server-github`
2. Communicates with it over stdin/stdout using JSON-RPC (MCP protocol) via the complementary MCP client that is inbuilt in the claude CLI.
3. The server calls the GitHub REST API over HTTPS using your GITHUB_PERSONAL_ACCESS_TOKEN

**Communication flow:**

```
You (terminal prompt)
      │
      ▼
Claude Code CLI  ──HTTPS──▶  Anthropic API (Claude decides to call list_issues)
      │
      │ stdin/stdout (JSON-RPC)
      ▼
GitHub MCP Server (local npx process)  ──HTTPS──▶  GitHub API
```

The Anthropic API call send the prompt to the LLM which:
1. Decides whether to call a tool or respond directly
2. Picks which tool and with what arguments (e.g. list_issues with owner="mariana200196", repo="claude-learning-plan")
3. Receives the tool result back and decides if it needs more tool calls
4. Synthesises the final natural language response ("Here are the open issues: ...")

The MCP server is not a remote service — it's an npm package created by GitHub software developers that runs locally on your machine. The "server" label just means it serves tools over the MCP protocol.

3. **Claude Agent SDK (`github_issue_fetcher_agent_sdk.py`)**

Uses the **Claude Agent SDK** from Python code, with the GitHub MCP server configured inline.

You write almost nothing — just a prompt and MCP server config. The SDK:

1. Launches your local claude CLI as a subprocess
2. Passes the MCP server config to it
3. Claude Code spawns the GitHub MCP server (same as case 2 above)
4. Returns the final result to your Python script

**Communication flow:**

```
Your script
      │
      │ subprocess
      ▼
Claude Agent SDK  ──launches──▶  Claude Code CLI  ──HTTPS──▶  Anthropic API
                                       │
                                       │ stdin/stdout (JSON-RPC)
                                       ▼
                                 GitHub MCP Server (local npx process)  ──HTTPS──▶  GitHub API
```

Cases 2 and 3 are nearly identical under the hood — the only difference is who drives Claude Code: you manually (terminal) vs. your Python script (Agent SDK).

### Summary

| | Anthropic SDK | Claude Code CLI | Agent SDK |
|---|---|---|---|
| You write | tools + loop | nothing | just a prompt |
| Tools | custom Python functions | GitHub MCP | GitHub MCP |
| GitHub API caller | your code | MCP server (local) | MCP server (local) |
| MCP involved | no | yes | yes |
| Claude Code required | no | yes | yes |
| Best for | learning / production apps | quick queries | automating tasks from Python |
