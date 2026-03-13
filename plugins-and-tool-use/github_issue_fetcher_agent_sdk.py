"""
GitHub Issue Fetcher — Agent SDK version
=========================================
Same task as github_issue_fetcher.py, but using the Claude Agent SDK instead
of the Anthropic Python SDK directly.

Key difference: we don't define tools or run the loop ourselves.
We give the agent a prompt and a tool it can use (the gh CLI via Bash),
and the SDK handles everything else.

Run:  python github_issue_fetcher_agent_sdk.py
  or: python github_issue_fetcher_agent_sdk.py "List open issues in cli/cli"
"""

import anyio
import sys

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock


async def fetch_issues(prompt: str) -> None:
    print(f"\n[PROMPT] {prompt}\n")
    print("=" * 60)

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            # Use the GitHub MCP server for authenticated GitHub access
            mcp_servers={
                "github": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                }
            },
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[thinking] {block.text}")
                else:
                    print(f"[tool] {block}")
        elif isinstance(message, ResultMessage):
            print(f"\n[result] {message.result}")

    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "List open issues in mariana200196/claude-learning-plan"

    anyio.run(fetch_issues, prompt)
