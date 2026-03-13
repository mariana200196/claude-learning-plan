---
name: summarize-pr
description: Summarize a pull request. Use when the user wants to review, understand, or get an overview of PR changes. Trigger phrases: "summarize PR", "summarize this PR", "what does this PR do", "review PR".
argument-hint: "[pr-number-or-url]"
allowed-tools: Bash(gh *)
---

Summarize the pull request $ARGUMENTS.

If no PR number or URL is provided, use the PR for the current branch.

## Steps

1. Fetch PR metadata: `gh pr view $ARGUMENTS --json number,title,body,author,state,baseRefName,headRefName,additions,deletions,changedFiles,labels,reviewDecision`
2. Get changed files: `gh pr diff $ARGUMENTS --name-only`
3. Get the diff: `gh pr diff $ARGUMENTS`

## Output format

Produce a concise summary using this structure:

**PR #[number] — [title]**
**Author:** [author] | **State:** [state] | **Base:** [base branch]

**Overview**
[1-3 sentences describing what this PR does and why]

**Changes** (+[additions] / -[deletions] across [N] files)
- [filename]: [what changed and why]
- ...

**Labels / Review status**
[labels and review decision if present]

**Notable risks or concerns**
[Any breaking changes, missing tests, or things worth flagging — omit if none]

Keep the summary factual and brief. Do not repeat information that is obvious from filenames alone.
