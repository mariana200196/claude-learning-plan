"""
GitHub Issue Fetcher — Week 1 Practice
=======================================
Demonstrates the Anthropic tool use loop:
  1. We define tools (get_issue, list_issues) and send them to Claude with a prompt
  2. Claude replies with a tool_use block (tool name + arguments)
  3. We execute the tool ourselves (call the GitHub API)
  4. We send the result back to Claude as a tool_result message
  5. Claude gives a final natural-language response

Run:  python github_issue_fetcher.py
"""

import json
import os
import sys

import anthropic
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
MAGENTA = "\033[95m"
RED    = "\033[91m"
DIM    = "\033[2m"


def log(label: str, color: str, message: str) -> None:
    print(f"\n{color}{BOLD}[{label}]{RESET} {message}")


def log_json(label: str, color: str, data: object) -> None:
    formatted = json.dumps(data, indent=2)
    print(f"\n{color}{BOLD}[{label}]{RESET}")
    print(f"{DIM}{formatted}{RESET}")


# ---------------------------------------------------------------------------
# Tool implementations — these call the real GitHub API
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT = 10
MODEL = "claude-haiku-4-5"


def _github_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _check_github_errors(response: requests.Response, not_found_msg: str) -> dict | None:
    """Return an error dict for known GitHub error codes, or None if the response is OK."""
    if response.status_code == 404:
        return {"error": not_found_msg}
    if response.status_code == 403:
        return {"error": "GitHub rate limit exceeded. Set GITHUB_TOKEN in .env to increase the limit."}
    return None


def _format_issue(i: dict) -> dict:
    """Extract the common fields from a GitHub issue object."""
    return {
        "number": i["number"],
        "title": i["title"],
        "state": i["state"],
        "author": i["user"]["login"],
        "labels": [l["name"] for l in i.get("labels", [])],
        "comments": i["comments"],
        "created_at": i["created_at"],
        "url": i["html_url"],
    }


def get_github_issue(owner: str, repo: str, issue_number: int) -> dict:
    """Fetch a single GitHub issue by number."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    log("TOOL RUN", GREEN, f"GET {url}")

    response = requests.get(url, headers=_github_headers(), timeout=REQUEST_TIMEOUT)

    err = _check_github_errors(response, f"Issue #{issue_number} not found in {owner}/{repo}")
    if err:
        return err
    response.raise_for_status()

    data = response.json()
    # Return only the fields Claude needs — keeps the context window small
    return {
        **_format_issue(data),
        "updated_at": data["updated_at"],
        "body": (data["body"] or "")[:1000],  # truncate long bodies
    }


def list_github_issues(owner: str, repo: str, state: str = "open", limit: int = 5) -> dict:
    """List recent issues in a GitHub repo."""
    limit = min(limit, 10)  # cap at 10 to keep responses manageable
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"state": state, "per_page": limit, "page": 1}
    log("TOOL RUN", GREEN, f"GET {url} (state={state}, limit={limit})")

    response = requests.get(url, headers=_github_headers(), params=params, timeout=REQUEST_TIMEOUT)

    err = _check_github_errors(response, f"Repository {owner}/{repo} not found")
    if err:
        return err
    response.raise_for_status()

    # Filter out pull requests (GitHub's /issues endpoint includes PRs)
    issues = [i for i in response.json() if "pull_request" not in i][:limit]

    return {
        "repository": f"{owner}/{repo}",
        "state": state,
        "count": len(issues),
        "issues": [_format_issue(i) for i in issues],
    }


# ---------------------------------------------------------------------------
# Tool registry — maps tool names to Python functions
# ---------------------------------------------------------------------------

TOOL_FUNCTIONS = {
    "get_github_issue": lambda args: get_github_issue(**args),
    "list_github_issues": lambda args: list_github_issues(**args),
}

# ---------------------------------------------------------------------------
# Tool schemas — sent to Claude so it knows what tools exist
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "get_github_issue",
        "description": (
            "Fetch a single GitHub issue by its number. "
            "Returns the issue title, body, state, labels, and metadata."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "The GitHub repository owner (user or organisation), e.g. 'anthropics'",
                },
                "repo": {
                    "type": "string",
                    "description": "The repository name, e.g. 'anthropic-sdk-python'",
                },
                "issue_number": {
                    "type": "integer",
                    "description": "The issue number to fetch",
                },
            },
            "required": ["owner", "repo", "issue_number"],
        },
    },
    {
        "name": "list_github_issues",
        "description": (
            "List recent issues in a GitHub repository. "
            "Can filter by state (open/closed/all). Returns up to 10 issues."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "The GitHub repository owner",
                },
                "repo": {
                    "type": "string",
                    "description": "The repository name",
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "description": "Filter issues by state. Defaults to 'open'.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of issues to return (1–10). Defaults to 5.",
                },
            },
            "required": ["owner", "repo"],
        },
    },
]

TOOLS_SUMMARY = [{"name": t["name"], "description": t["description"]} for t in TOOLS]

# ---------------------------------------------------------------------------
# Agentic loop — the core of the Week 1 exercise
# ---------------------------------------------------------------------------

def run(prompt: str) -> None:
    """
    Send a prompt to Claude with tool definitions and run the tool use loop
    until Claude has a final answer.
    """
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": prompt}]

    log("USER PROMPT", CYAN, prompt)
    log_json("TOOLS SENT TO CLAUDE", CYAN, TOOLS_SUMMARY)

    iteration = 0

    while True:
        iteration += 1
        log("API CALL", MAGENTA, f"Sending {len(messages)} message(s) to Claude (iteration {iteration})")

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        log("CLAUDE RESPONSE", MAGENTA,
            f"stop_reason={response.stop_reason!r}  |  "
            f"{len(response.content)} content block(s)")

        # Collect any tool-use blocks from this response
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]

        for block in text_blocks:
            if block.text.strip():
                log("CLAUDE TEXT", MAGENTA, block.text)

        # If Claude is done (no more tool calls), print final answer and exit
        if response.stop_reason == "end_turn":
            log("DONE", GREEN, "Claude finished. No more tool calls.")
            break

        # Claude wants to call one or more tools
        if response.stop_reason == "tool_use":
            # Append the assistant's response to the conversation history
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_block in tool_use_blocks:
                log("CLAUDE TOOL CALL", YELLOW,
                    f"Tool: {tool_block.name!r}  |  "
                    f"ID: {tool_block.id}  |  "
                    f"Args: {json.dumps(tool_block.input)}")

                # Execute the actual tool
                fn = TOOL_FUNCTIONS.get(tool_block.name)
                if fn is None:
                    result = {"error": f"Unknown tool: {tool_block.name}"}
                    is_error = True
                else:
                    try:
                        result = fn(tool_block.input)
                        is_error = "error" in result
                    except Exception as exc:
                        result = {"error": str(exc)}
                        is_error = True

                log("TOOL RESULT", GREEN,
                    f"{'ERROR' if is_error else 'OK'}  →  "
                    + json.dumps(result, indent=2)[:400])  # truncate for readability

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": json.dumps(result),
                    "is_error": is_error,
                })

            # Send all tool results back as a user message
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason
            log("WARN", RED, f"Unexpected stop_reason: {response.stop_reason!r}")
            break

    # Print the final text answer clearly
    final_text = next(
        (b.text for b in response.content if b.type == "text"),
        "(no text in final response)"
    )
    print(f"\n{'='*60}")
    print(f"{BOLD}FINAL ANSWER:{RESET}")
    print(f"{'='*60}")
    print(final_text)
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

DEFAULT_PROMPTS = [
    "List the 3 most recent open issues in the anthropics/anthropic-sdk-python repo.",
    "Fetch issue #1 from the anthropics/anthropic-sdk-python repo and summarise it for me.",
]

if __name__ == "__main__":
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(f"{RED}Error: ANTHROPIC_API_KEY not set.{RESET}")
        print("Copy .env.example to .env and add your key.")
        sys.exit(1)

    # Allow passing a custom prompt as a command-line argument
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        print("No prompt given — using default.\n")
        print("You can run with a custom prompt:")
        print('  python github_issue_fetcher.py "List open issues in cli/cli"\n')
        prompt = DEFAULT_PROMPTS[0]

    run(prompt)
