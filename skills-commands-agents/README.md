Test the summarize-pr skill by prompting Claude Code with: "Review the PR from https://github.com/explosion/spaCy/pull/13922"

Test the pr-summarizer agent by prompting Claude Code with: "Agentically review the PR from https://github.com/explosion/spaCy/pull/13922"


# Overview of the frontmatter of a Skill

Skill.md files should be up to 500 lines. Use Progressive Disclosure to provide additional references, assets, and runnable scripts.

## `name`

The slash command name used to invoke the skill. Must be lowercase with hyphens — no spaces or special characters.

```yaml
name: summarize-pr
```

Invoked as `/summarize-pr`.

---

## `description`

Tells Claude when to automatically invoke the Skill. Write it as a sentence describing what the skill does and include trigger phrases — Claude matches these against user messages.

That means, all names and descriptions of Skills are loaded into the context window, but not the full Skill, unless it matches the prompt intent and the user approves the use of the Skill.

```yaml
description: Summarize a pull request. Use when the user wants to review or understand PR changes. Trigger phrases: "summarize PR", "what does this PR do".
```

The richer and more specific this is, the better Claude is at knowing when to use the skill automatically. **A good description answers: What does this Skill do and when should Claude us it?**

---

## `argument-hint`

**Display only** — has zero effect on behavior. It's the hint shown in the autocomplete UI when a user types `/skill-name`, indicating what arguments to pass.

```yaml
argument-hint: "[pr-number-or-url]"       # single arg
argument-hint: "[filename] [format]"      # multiple args
```

Any free-form string is accepted. Convention is square or angle brackets around arg names, but nothing enforces this.

---

## `allowed-tools`

Controls which tools Claude can use **without prompting for permission** while the skill runs. Values must be exact tool names — no natural language.

**Simple list:**
```yaml
allowed-tools: Read, Grep, Glob, WebFetch
```

**Scoped Bash commands** — restrict to specific shell patterns:
```yaml
allowed-tools: Bash(gh *)           # only gh commands
allowed-tools: Bash(git *)          # only git commands
allowed-tools: Bash(gh *), Read     # gh commands + unrestricted Read
```

The `Bash(pattern)` syntax is specific to the `Bash` tool. Other tools can't be scoped this way — they're either fully allowed or not listed.

Valid tool names: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebFetch`, `WebSearch`, `Agent`, `NotebookEdit`

Unlike `argument-hint`, this has real security implications — it bypasses normal permission prompts for the listed tools while the skill is active.

---

## `disable-model-invocation`

Prevents Claude from automatically invoking the skill based on conversation context. When `true`, the skill only runs when explicitly triggered with `/skill-name`.

```yaml
disable-model-invocation: true
```

Useful for skills that are destructive, slow, or expensive — ones you never want firing automatically.

---

## `user-invocable`

Controls whether the skill appears in the `/` autocomplete menu. Default is `true`.

```yaml
user-invocable: false
```

Set to `false` for internal or background skills that users shouldn't trigger directly — for example, a helper skill invoked by another skill via the `Agent` tool.

---

## `model`

Overrides the Claude model used when this skill runs. Accepts any valid model ID.

```yaml
model: claude-haiku-4-5-20251001
```

Useful for routing cheap/fast tasks to a smaller model (e.g. Haiku) and reserving the default model for heavier work.

---

## `context`

Set to `fork` to run the skill in an isolated subagent session, separate from the main conversation context.

```yaml
context: fork
```

The forked session doesn't share conversation history with the parent. Good for long-running or exploratory tasks where you don't want intermediate results polluting the main context.

---

## `agent`

Specifies which subagent type to use when `context: fork` is set. Has no effect without `context: fork`.

```yaml
context: fork
agent: Explore
```

Built-in types: `Explore` (fast codebase search), `Plan` (architecture and planning), `general-purpose` (full tool access). You can also pass the name of any custom agent you've defined in `.claude/agents/<name>/AGENT.md` or `~/.claude/agents/<name>/AGENT.md`. If omitted, defaults to `general-purpose`.

Example of when to use `agent` in the front matter:

---
name: review-pr
description: Do a thorough code review of the current PR
context: fork
agent: Explore
allowed-tools: Bash(gh *), Read, Grep, Glob
---

Review the PR for the current branch.

1. Fetch the diff: `gh pr diff`
2. Fetch changed files: `gh pr diff --name-only`
3. Read each changed file in full
4. Search for related tests and check coverage
5. Report: bugs, security issues, missing tests, style violations

**Why `context: fork` + `agent: Explore` makes sense here:**

- The review involves reading many files and running several `gh` commands — it produces a lot of intermediate output you don't want filling your main conversation history
- `Explore` is optimized for searching and reading codebases — exactly what a reviewer needs
- Running in a forked context means when it's done, only the final summary comes back to you, not every `Read` and `Grep` call it made along the way
- You can start the review and continue other work in the main conversation while it runs

**Contrast with when you wouldn't use `context: fork`:** a simple skill like `/summarize-pr` that just runs a couple of `gh` commands and formats the output — that's fast and lightweight, no reason to fork a subagent for it.

The general rule: use `context: fork` + `agent` when the skill needs to do deep, multi-step exploration that would pollute the main context with noise.

---

## `hooks`

Defines shell commands that run at specific points in the skill's lifecycle, scoped only to this skill. Same format as global hooks in settings.

```yaml
hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "prettier --write ."
```

Useful for automating side effects like formatting, linting, or logging that should only trigger when this specific skill is active.

## Progressive Disclosure

Example: `C:/Users/maria/.claude/plugins/marketplaces/claude-plugins-official/plugins/claude-code-setup/skills`

Example "Release Management Skill": 

The release process has multiple distinct phases (pre-flight checks, versioning, changelog, deployment, post-deploy verification), each with detailed steps. Putting it all in one SKILL.md would push past 500 lines and load a wall of instructions Claude mostly won't need.

Structure:
```
.claude/skills/release/
├── SKILL.md                        # orchestrator — stays short
├── scripts/
│   ├── preflight-checks.sh         # runs automated checks before release
│   └── post-deploy-verify.sh       # pings endpoints, checks error rates
└── templates/
    ├── changelog-entry.md           # format for CHANGELOG.md entries
    └── release-notes.md             # format for GitHub release body
```

SLILL-md stays concise:
```
---
name: release
description: Cut a release. Trigger: "release", "ship", "deploy to prod"
disable-model-invocation: true
allowed-tools: Bash(gh *), Bash(git *), Read, Edit
---

Cut a release for $ARGUMENTS (patch | minor | major).

## Phase 1 — Pre-flight
Run: `bash ${CLAUDE_SKILL_DIR}/scripts/preflight-checks.sh`
Fix any failures before proceeding.

## Phase 2 — Version & Changelog
Bump the version in package.json.
Add a changelog entry using the format in ${CLAUDE_SKILL_DIR}/templates/changelog-entry.md.

## Phase 3 — Tag & Push
`git tag v<version> && git push --tags`
Create a GitHub release using the template at ${CLAUDE_SKILL_DIR}/templates/release-notes.md.

## Phase 4 — Post-deploy verification
Run: `bash ${CLAUDE_SKILL_DIR}/scripts/post-deploy-verify.sh`
Report results.
```

**Why progressive disclosure makes sense here:**

- The shell scripts contain the real detail (which endpoints to ping, which checks to run) — they only execute when that phase is reached, not upfront
- The templates are only read when Claude needs to write the changelog or release notes — not loaded into context for every phase
- SKILL.md stays under 30 lines and reads as a clear orchestration plan
- You can update `preflight-checks.sh` independently without touching the skill logic

The rule of thumb: use it when your skill has phases with their own detailed content, or reusable assets (templates, scripts) that shouldn't bloat the main instruction file.


## A Note on Subganets + Skills:

Built-in agents (Explore, Plan, general-purpose) cannot access skills when running as a forked subagent. BUT when a skill uses `context: fork`, the forked agent receives the skill's own SKILL.md content and CLAUDE.md — no other context or skills are available to it. This keeps the context window minimal and only returns the subagent result to the main conversation, again for context efficiency.

Custom subagents can preload Skills via a skills field in their AGENT.md frontmatter:

```
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---
```


## Sharing Skills and their Prioritization

1. Enterprise — managed settings (~/.claude/settings.json), highest priority
2. Personal — your home directory (~/.claude/skills)
3. Project — the .claude/skills directory inside a repository
4. Plugins — installed plugins, lowest priority