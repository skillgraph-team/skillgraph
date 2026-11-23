"""Tell a Claude Code session when teammates have pushed new work.

Run by the UserPromptSubmit hook in `.claude/settings.json` each time a prompt is sent.
At most once every 30 minutes it runs `git fetch` and compares with what the last check
saw: new commits on origin/main by someone else, new or updated open PRs, and new
unmerged branches. If something changed, it prints a short note that Claude Code adds
to the conversation. Otherwise it prints nothing.

Its memory lives in `.git/claude-session-check.json` (one per clone, never committed).
The first run only records a baseline, because CLAUDE.md's "Every session, before any
work" step already gives the full summary when a session starts.
It never fails the prompt: any error (offline, no `gh`) means "say nothing".
Manual test: `python scripts/session_check.py --force`.
"""

from __future__ import annotations

import contextlib
import json
import subprocess
import sys
import time
from pathlib import Path

INTERVAL_SECONDS = 30 * 60
ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / ".git" / "claude-session-check.json"


def run(*args: str, timeout: int = 20) -> str:
    """Run a command in the repo root and return its stdout ('' on any failure)."""
    try:
        result = subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def current_state() -> dict[str, object]:
    """What the remote looks like right now (after a fetch)."""
    run("git", "fetch", "--prune", "--quiet", timeout=30)
    prs_raw = run(
        "gh",
        "pr",
        "list",
        "--state",
        "open",
        "--json",
        "number,title,author,updatedAt,headRefName",
    )
    try:
        prs = {
            str(p["number"]): {
                "title": p["title"],
                "author": p["author"]["login"],
                "updatedAt": p["updatedAt"],
                "branch": p["headRefName"],
            }
            for p in json.loads(prs_raw or "[]")
        }
    except (ValueError, KeyError, TypeError):
        prs = {}
    branches = [
        b.strip()
        for b in run("git", "branch", "-r", "--no-merged", "origin/main").splitlines()
        if b.strip() and "HEAD" not in b
    ]
    return {
        "main": run("git", "rev-parse", "origin/main"),
        "prs": prs,
        "branches": sorted(branches),
    }


def describe_changes(old: dict, new: dict) -> list[str]:
    """Plain-language lines for everything that changed since the last check."""
    lines: list[str] = []
    me = run("git", "config", "user.name")
    if old.get("main") and new["main"] and old["main"] != new["main"]:
        log = run("git", "log", "--format=%h %an: %s", f"{old['main']}..{new['main']}")
        others = [line for line in log.splitlines() if me and f" {me}: " not in line]
        if others:
            lines.append(f"New commits on origin/main by teammates ({len(others)}):")
            lines += [f"  - {line}" for line in others[:10]]
    old_prs, new_prs = old.get("prs", {}), new["prs"]
    for number, pr in new_prs.items():
        if number not in old_prs:
            lines.append(f"New PR #{number} by {pr['author']}: {pr['title']} (waiting for review)")
        elif old_prs[number]["updatedAt"] != pr["updatedAt"]:
            lines.append(f"PR #{number} by {pr['author']} was updated: {pr['title']}")
    pr_branches = {f"origin/{pr['branch']}" for pr in new_prs.values()}
    for branch in new["branches"]:
        if branch not in old.get("branches", []) and branch not in pr_branches:
            lines.append(f"New branch without a PR yet: {branch}")
    behind = run("git", "rev-list", "--count", "HEAD..origin/main")
    if lines and behind not in ("", "0"):
        lines.append(f"Your local branch is {behind} commit(s) behind origin/main: pull first.")
    return lines


def main() -> None:
    force = "--force" in sys.argv
    try:
        old = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    if not force and time.time() - float(old.get("checked_at", 0)) < INTERVAL_SECONDS:
        return
    new = current_state()
    if not new["main"]:
        return  # fetch or git failed (offline?): say nothing, try again next prompt
    lines = describe_changes(old, new) if old else []
    STATE_FILE.write_text(json.dumps({**new, "checked_at": time.time()}), encoding="utf-8")
    if not lines:
        return
    note = "Teammate activity since the last check (scripts/session_check.py):\n" + "\n".join(lines)
    print(
        json.dumps(
            {
                "systemMessage": note,
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": note
                    + "\nMention this to the user before continuing, and pull/re-read"
                    " anything it affects.",
                },
            }
        )
    )


if __name__ == "__main__":
    # A hook must never block the user's prompt, so any unexpected error means "say nothing".
    with contextlib.suppress(Exception):
        main()
