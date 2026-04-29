---
name: git-commit-push
description: "Create Git commits and push to GitHub with Conventional Commits and a detailed body. Trigger on 'commit', 'git commit', 'push', 'commit and push', 'save to git', or 'push to main'. Builds a message from diffs and optional plan.md, and respects safety hooks."
allowed-tools: Bash, Read
model: claude-sonnet-4-5
---

# Git commit and push (Conventional Commits)

## When to use

- User asks to commit or push work
- End of a milestone or session

## Goal

Produce a Conventional Commit message (subject + structured body) and push to the correct branch, respecting `prevent-git-commit-push` hooks.

## Step 1: Gather context

```bash
git status
git diff --cached --stat
git diff --stat
git diff --cached
git diff
git branch --show-current
git remote -v
cat plan.md 2>/dev/null || echo "[plan.md not found]"
git log --oneline -5
```

## Step 2: Build the commit message

Use the message rules and body template in [references/commit-message.md](references/commit-message.md).

## Step 3: Stage and branch safety

- If user specified files, stage only those; otherwise `git add -A`.
- Show `git diff --cached --stat` before committing.
- If target branch differs from current, ask for confirmation before switching.
- If target is `main` or `master`, warn explicitly.

## Step 4: Execute

```bash
git add <target>
git commit -m "<subject>" -m "<body>"
git push origin <branch>
```

## Step 5: Post-push confirmation

Summarize branch, remote, commit hash, and key changes.

## Special cases

- Commit only (no push)
- Push only (no new commits)
- Repo not initialized
- Clean working tree
- Push rejected or conflicts (no force push)
