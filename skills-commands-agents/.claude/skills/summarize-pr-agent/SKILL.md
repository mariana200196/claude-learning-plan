---
name: summarize-pr-agent
description: Summarize a pull request using a dedicated subagent. Same as summarize-pr but delegates to the pr-summarizer agent running in a forked context. Use when you want the summary to run in isolation without polluting the main conversation context.
argument-hint: "[pr-number-or-url]"
context: fork
agent: pr-summarizer
allowed-tools: Bash(gh *)
---

Summarize the pull request $ARGUMENTS.

If no PR number or URL is provided, use the PR for the current branch.
