#!/usr/bin/env python3
"""Set up and maintain SkillGraph's GitHub repo, Project board and issues.

Reads docs/MILESTONES.md and turns it into GitHub labels, milestones, a Project
board with custom fields, and one issue per slice. Safe to re-run: anything
that already exists is skipped, so after adding a slice to MILESTONES.md you
can run `setup` again to create just the new issue.

Requires the GitHub CLI (`gh`) logged in with the `project` scope:
    gh auth login
    gh auth refresh -s project

Commands:
    python scripts/github_setup.py parse
        Print what would be created (no GitHub calls).
    python scripts/github_setup.py setup --owner OWNER --repo OWNER/NAME [--start-date YYYY-MM-DD] [--dry-run]
        Create labels, milestones, the Project board, its fields and the issues.
        --start-date sets milestone due dates from the week ranges in MILESTONES.md.
    python scripts/github_setup.py invite USER [USER ...]
        Add teammates to the repo with write access.
    python scripts/github_setup.py protect
        Require a PR with 1 approval on main, block force-pushes and deletion.
        Org admins (Rasen) bypass the rule and can push to main directly (D-016).
        Add --check NAME (repeatable) to also require CI jobs to pass.
    python scripts/github_setup.py status M3.5 "In Progress"
        Set a slice's Status on the board (Todo / In Progress / Done).

Only the Python standard library is used, so it runs before the backend exists.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MILESTONES_FILE = ROOT / "docs" / "MILESTONES.md"
CONFIG_FILE = ROOT / "scripts" / "github_project.json"
PROJECT_TITLE = "SkillGraph"

SECTIONS = ("**Goal:**", "**Why:**", "**Read first:**", "**Tasks**", "**Done when**")
SIZES = ["S", "M", "L"]

AREA_COLORS = {
    "infra": "5319e7",
    "backend": "1d76db",
    "frontend": "0e8a16",
    "agents": "b60205",
    "ai": "d93f0b",
    "data": "fbca04",
    "eval": "c5def5",
    "research": "bfd4f2",
    "docs": "d4c5f9",
}
EXTRA_LABELS = {
    "contract": ("000000", "Defines something everyone builds on; needs whole-team approval"),
    "blocked": ("e11d21", "Waiting on another slice or a decision"),
    "bug": ("d73a4a", "Something is broken"),
    "decision": ("0052cc", "A hard-to-reverse choice that needs a decision"),
}

MILESTONE_RE = re.compile(r"^## (M\d+) · (.+?)\s*$")
WEEKS_RE = re.compile(r"<!--\s*weeks:\s*(\d+)\s*-\s*(\d+)\s*-->")
SLICE_RE = re.compile(r"^### (M\d+\.\d+) · (.+?)\s*$")
TAG_RE = re.compile(r"`(\w+):([^`]*)`")


# --------------------------------------------------------------------------- parsing


@dataclass
class Slice:
    id: str
    title: str
    tags: dict[str, str]
    body_lines: list[str] = field(default_factory=list)

    @property
    def full_title(self) -> str:
        return f"{self.id} · {self.title}"

    @property
    def area(self) -> str:
        return self.tags.get("area", "").strip()

    @property
    def size(self) -> str:
        return self.tags.get("size", "").strip()

    @property
    def depends(self) -> list[str]:
        raw = self.tags.get("depends", "").strip()
        return [d.strip() for d in raw.split(",") if re.fullmatch(r"M\d+\.\d+", d.strip())]

    @property
    def is_contract(self) -> bool:
        return self.tags.get("contract", "").strip().lower() == "yes"

    def issue_body(self) -> str:
        body = "\n".join(self.body_lines).strip()
        meta = [
            f"**Area:** {self.area or '—'} · **Size:** {self.size or '—'}",
            f"**Depends on:** {', '.join(self.depends) if self.depends else 'nothing'}",
        ]
        if self.is_contract:
            meta.append("**Contract:** yes. The whole team approves the PR; name the contract "
                        "owner in a comment before starting.")
        footer = (
            "---\n"
            f"Branch: `{self.id.lower()}-<short-name>` · "
            f"Claude Code: say \"let's do {self.id}\" · Chatbot: `docs/CHAT_KIT.md` · "
            "Terms: `docs/GLOSSARY.md` · Source of truth: `docs/MILESTONES.md`"
        )
        return "\n".join(meta) + "\n\n" + body + "\n\n" + footer + "\n"


@dataclass
class Milestone:
    id: str
    title: str
    weeks: tuple[int, int] | None = None
    description_lines: list[str] = field(default_factory=list)
    slices: list[Slice] = field(default_factory=list)

    @property
    def full_title(self) -> str:
        return f"{self.id} · {self.title}"

    @property
    def description(self) -> str:
        text = " ".join(line.strip() for line in self.description_lines if line.strip())
        if self.weeks:
            text = f"Weeks {self.weeks[0]}–{self.weeks[1]}. {text}"
        return text


def parse_milestones(path: Path = MILESTONES_FILE) -> list[Milestone]:
    milestones: list[Milestone] = []
    current_m: Milestone | None = None
    current_s: Slice | None = None
    seen: set[str] = set()

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = MILESTONE_RE.match(line)
        if m:
            current_m = Milestone(id=m.group(1), title=m.group(2))
            milestones.append(current_m)
            current_s = None
            continue
        s = SLICE_RE.match(line)
        if s:
            if current_m is None:
                raise ValueError(f"Slice {s.group(1)} appears before any milestone heading")
            if not s.group(1).startswith(current_m.id + "."):
                raise ValueError(f"Slice {s.group(1)} is under milestone {current_m.id}")
            if s.group(1) in seen:
                raise ValueError(f"Duplicate slice id {s.group(1)}")
            seen.add(s.group(1))
            current_s = Slice(id=s.group(1), title=s.group(2), tags={})
            current_m.slices.append(current_s)
            continue
        if line.startswith("## ") or line.strip() == "---":
            # any other level-2 heading or a rule ends the current block
            if line.startswith("## "):
                current_m = None
            current_s = None
            continue
        if current_s is not None:
            if not current_s.tags and TAG_RE.search(line):
                current_s.tags = {k: v for k, v in TAG_RE.findall(line)}
            else:
                current_s.body_lines.append(line)
        elif current_m is not None:
            w = WEEKS_RE.search(line)
            if w:
                current_m.weeks = (int(w.group(1)), int(w.group(2)))
            else:
                current_m.description_lines.append(line)

    validate(milestones)
    return milestones


def validate(milestones: list[Milestone]) -> None:
    ids = {s.id for m in milestones for s in m.slices}
    problems = []
    for m in milestones:
        for s in m.slices:
            if s.area not in AREA_COLORS:
                problems.append(f"{s.id}: unknown area '{s.area}'")
            if s.size not in SIZES:
                problems.append(f"{s.id}: size must be one of {SIZES}")
            for d in s.depends:
                if d not in ids:
                    problems.append(f"{s.id}: depends on unknown slice {d}")
            body = "\n".join(s.body_lines)
            for section in SECTIONS:
                if section not in body:
                    problems.append(f"{s.id}: missing {section}")
    if problems:
        raise ValueError("MILESTONES.md problems:\n  " + "\n  ".join(problems))


# --------------------------------------------------------------------------- gh wrapper


class GH:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        if not dry_run and shutil.which("gh") is None:
            sys.exit("The GitHub CLI 'gh' is not installed. See https://cli.github.com")

    def run(self, *args: str, read: bool = False, check: bool = True) -> str:
        if self.dry_run and not read:
            print("  [dry-run] gh " + " ".join(_quote(a) for a in args))
            return ""
        if self.dry_run and read:
            return ""
        # gh always prints UTF-8; without an explicit encoding Windows decodes it
        # as cp1252, which garbles "·" in titles and breaks the "already exists" checks.
        proc = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
        if proc.returncode != 0 and check:
            raise RuntimeError(f"gh {' '.join(args)} failed:\n{proc.stderr.strip()}")
        return proc.stdout

    def json(self, *args: str) -> object:
        out = self.run(*args, read=True)
        return json.loads(out) if out.strip() else None


def _quote(a: str) -> str:
    return a if re.fullmatch(r"[\w@./:=,-]+", a) else repr(a)


# --------------------------------------------------------------------------- setup steps


def resolve_owner(gh: GH, owner: str) -> str:
    if owner != "@me":
        return owner
    if gh.dry_run:
        return "@me"
    return gh.run("api", "user", "--jq", ".login", read=True).strip()


def ensure_labels(gh: GH, repo: str) -> None:
    print("Labels")
    for area, color in AREA_COLORS.items():
        gh.run("label", "create", f"area:{area}", "--repo", repo, "--color", color,
               "--description", f"{area} work", "--force")
    for name, (color, desc) in EXTRA_LABELS.items():
        gh.run("label", "create", name, "--repo", repo, "--color", color,
               "--description", desc, "--force")


def ensure_milestones(gh: GH, repo: str, milestones: list[Milestone], start: dt.date | None) -> None:
    print("Milestones")
    existing = gh.json("api", f"repos/{repo}/milestones?state=all&per_page=100") or []
    titles = {m["title"] for m in existing}  # type: ignore[index]
    for m in milestones:
        if m.full_title in titles:
            print(f"  exists: {m.full_title}")
            continue
        args = ["api", f"repos/{repo}/milestones", "-f", f"title={m.full_title}",
                "-f", f"description={m.description}"]
        if start and m.weeks:
            due = start + dt.timedelta(weeks=m.weeks[1]) - dt.timedelta(days=1)
            args += ["-f", f"due_on={due.isoformat()}T23:59:59Z"]
        gh.run(*args)
        print(f"  {'would create' if gh.dry_run else 'created'}: {m.full_title}")


def ensure_project(gh: GH, owner: str, repo: str) -> dict:
    print("Project board")
    projects = gh.json("project", "list", "--owner", owner, "--format", "json", "--limit", "100")
    for p in (projects or {}).get("projects", []):  # type: ignore[union-attr]
        if p["title"] == PROJECT_TITLE:
            print(f"  exists: #{p['number']}")
            info = {"number": p["number"], "id": p["id"], "url": p.get("url", "")}
            break
    else:
        if gh.dry_run:
            gh.run("project", "create", "--owner", owner, "--title", PROJECT_TITLE, "--format", "json")
            info = {"number": 0, "id": "DRY_RUN", "url": ""}
        else:
            created = json.loads(gh.run("project", "create", "--owner", owner,
                                        "--title", PROJECT_TITLE, "--format", "json"))
            info = {"number": created["number"], "id": created["id"], "url": created.get("url", "")}
            print(f"  created: #{info['number']} {info['url']}")
    gh.run("project", "link", str(info["number"]), "--owner", owner, "--repo", repo, check=False)
    return info


def ensure_fields(gh: GH, owner: str, number: int, areas: list[str]) -> dict:
    print("Project fields")
    wanted = {"Area": areas, "Size": SIZES}
    fields = _field_map(gh, owner, number)
    for name, options in wanted.items():
        if name in fields:
            print(f"  exists: {name}")
            continue
        gh.run("project", "field-create", str(number), "--owner", owner, "--name", name,
               "--data-type", "SINGLE_SELECT", "--single-select-options", ",".join(options))
        print(f"  {'would create' if gh.dry_run else 'created'}: {name}")
    return _field_map(gh, owner, number)


def _field_map(gh: GH, owner: str, number: int) -> dict:
    data = gh.json("project", "field-list", str(number), "--owner", owner, "--format", "json",
                   "--limit", "50")
    result = {}
    for f in (data or {}).get("fields", []):  # type: ignore[union-attr]
        result[f["name"]] = {
            "id": f["id"],
            "options": {o["name"].lower(): o["id"] for o in f.get("options", [])},
        }
    return result


def ensure_issues(gh: GH, owner: str, repo: str, project: dict, fields: dict,
                  milestones: list[Milestone]) -> None:
    print("Issues")
    existing = gh.json("issue", "list", "--repo", repo, "--state", "all", "--limit", "1000",
                       "--json", "number,title,url") or []
    by_id = {}
    for issue in existing:  # type: ignore[union-attr]
        sid = issue["title"].split(" ", 1)[0]
        by_id[sid] = issue
    for m in milestones:
        for s in m.slices:
            if s.id in by_id:
                print(f"  exists: {s.full_title}")
                continue
            labels = [f"area:{s.area}"] + (["contract"] if s.is_contract else [])
            with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
                fh.write(s.issue_body())
                body_path = fh.name
            args = ["issue", "create", "--repo", repo, "--title", s.full_title,
                    "--body-file", body_path, "--milestone", m.full_title]
            for label in labels:
                args += ["--label", label]
            url = gh.run(*args).strip()
            Path(body_path).unlink(missing_ok=True)
            print(f"  {'would create' if gh.dry_run else 'created'}: {s.full_title}")
            if gh.dry_run:
                continue
            add_to_project(gh, owner, project, fields, url, s)
            time.sleep(1)  # stay well under GitHub's content-creation rate limits


def add_to_project(gh: GH, owner: str, project: dict, fields: dict, url: str, s: Slice) -> None:
    item = json.loads(gh.run("project", "item-add", str(project["number"]), "--owner", owner,
                             "--url", url, "--format", "json"))
    for field_name, value in (("Area", s.area), ("Size", s.size), ("Status", "Todo")):
        f = fields.get(field_name)
        if not f or value.lower() not in f["options"]:
            continue
        gh.run("project", "item-edit", "--id", item["id"], "--project-id", project["id"],
               "--field-id", f["id"], "--single-select-option-id", f["options"][value.lower()])


# --------------------------------------------------------------------------- commands


def cmd_parse(_: argparse.Namespace) -> None:
    milestones = parse_milestones()
    total = 0
    for m in milestones:
        weeks = f"weeks {m.weeks[0]}-{m.weeks[1]}" if m.weeks else "no weeks"
        print(f"{m.full_title}  ({weeks}, {len(m.slices)} slices)")
        for s in m.slices:
            flag = " [contract]" if s.is_contract else ""
            dep = ", ".join(s.depends) or "—"
            print(f"   {s.full_title:<60} {s.area:<9} {s.size}  depends: {dep}{flag}")
        total += len(m.slices)
    tasks = sum(
        sum(1 for line in s.body_lines if line.strip().startswith("- [ ]"))
        for m in milestones for s in m.slices
    )
    print(f"\n{len(milestones)} milestones, {total} slices, {tasks} checklist items")


def cmd_setup(args: argparse.Namespace) -> None:
    milestones = parse_milestones()
    gh = GH(dry_run=args.dry_run)
    owner = resolve_owner(gh, args.owner)
    start = dt.date.fromisoformat(args.start_date) if args.start_date else None
    ensure_labels(gh, args.repo)
    ensure_milestones(gh, args.repo, milestones, start)
    project = ensure_project(gh, owner, args.repo)
    areas = sorted({s.area for m in milestones for s in m.slices})
    fields = ensure_fields(gh, owner, project["number"], areas)
    ensure_issues(gh, owner, args.repo, project, fields, milestones)
    if not args.dry_run:
        CONFIG_FILE.write_text(json.dumps(
            {"owner": owner, "repo": args.repo, "project_number": project["number"],
             "project_id": project["id"], "project_url": project["url"]}, indent=2) + "\n")
        print(f"\nSaved {CONFIG_FILE.relative_to(ROOT)} (commit it).")
        print("Next: turn on the board's built-in workflows (Item closed → Done, "
              "Pull request merged → Done) and share the board with the team.")


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        sys.exit("scripts/github_project.json not found. Run `setup` first.")
    return json.loads(CONFIG_FILE.read_text())


def cmd_invite(args: argparse.Namespace) -> None:
    cfg = load_config()
    gh = GH()
    for user in args.users:
        gh.run("api", "-X", "PUT", f"repos/{cfg['repo']}/collaborators/{user}",
               "-f", "permission=push")
        print(f"Invited {user} (they must accept the email/GitHub invitation)")
    print("If the board belongs to a personal account, also add them in the Project's "
          "Settings → Manage access. Organization members get access through the org.")


def cmd_protect(args: argparse.Namespace) -> None:
    cfg = load_config()
    gh = GH()
    rules: list[dict] = [
        {"type": "pull_request", "parameters": {
            "required_approving_review_count": 1,
            "dismiss_stale_reviews_on_push": True,
            "require_code_owner_review": False,
            "require_last_push_approval": False,
            "required_review_thread_resolution": False,
        }},
        {"type": "non_fast_forward"},
        {"type": "deletion"},
    ]
    if args.check:
        rules.append({"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": False,
            "required_status_checks": [{"context": c} for c in args.check],
        }})
    ruleset = {
        "name": "protect-main",
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        # D-016: org admins push straight to main; everyone else goes through a reviewed PR.
        # For OrganizationAdmin, GitHub expects actor_id 1.
        "bypass_actors": [{"actor_id": 1, "actor_type": "OrganizationAdmin", "bypass_mode": "always"}],
        "rules": rules,
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(ruleset, fh)
        path = fh.name
    try:
        gh.run("api", "-X", "POST", f"repos/{cfg['repo']}/rulesets", "--input", path)
        print("main is protected: PR + 1 approval" + (", CI checks" if args.check else "")
              + ", no force-push, no deletion. Org admins can bypass.")
    except RuntimeError as err:
        print("Could not create the ruleset. On GitHub Free, rulesets only work on public "
              "repos (see D-002). Keep the 'PR + review' rule by convention.\n" + str(err))
    finally:
        Path(path).unlink(missing_ok=True)


def cmd_status(args: argparse.Namespace) -> None:
    cfg = load_config()
    gh = GH()
    owner, number = cfg["owner"], cfg["project_number"]
    fields = _field_map(gh, owner, number)
    status = fields.get("Status")
    if not status:
        sys.exit("The board has no Status field.")
    option = status["options"].get(args.value.lower())
    if not option:
        sys.exit(f"Unknown status '{args.value}'. Options: {', '.join(status['options'])}")
    items = gh.json("project", "item-list", str(number), "--owner", owner, "--format", "json",
                    "--limit", "1000") or {}
    for item in items.get("items", []):  # type: ignore[union-attr]
        title = (item.get("content") or {}).get("title", "")
        if title.split(" ", 1)[0] == args.slice:
            gh.run("project", "item-edit", "--id", item["id"], "--project-id", cfg["project_id"],
                   "--field-id", status["id"], "--single-select-option-id", option)
            print(f"{args.slice} → {args.value}")
            return
    sys.exit(f"No board item found for {args.slice}.")


def main() -> None:
    # Output contains "→" and "·". A Windows console defaults to cp1252, which has no "→",
    # so print() crashed (after the work was already done). Always write UTF-8 instead.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("parse", help="print the parsed plan").set_defaults(func=cmd_parse)

    p = sub.add_parser("setup", help="create labels, milestones, board, fields and issues")
    p.add_argument("--owner", required=True, help="user or organization login, or @me")
    p.add_argument("--repo", required=True, help="OWNER/NAME")
    p.add_argument("--start-date", help="semester week 1 Monday, YYYY-MM-DD (sets due dates)")
    p.add_argument("--dry-run", action="store_true", help="print the gh commands without running")
    p.set_defaults(func=cmd_setup)

    p = sub.add_parser("invite", help="give teammates write access")
    p.add_argument("users", nargs="+")
    p.set_defaults(func=cmd_invite)

    p = sub.add_parser("protect", help="protect main with a ruleset")
    p.add_argument("--check", action="append", help="CI job name to require (repeatable)")
    p.set_defaults(func=cmd_protect)

    p = sub.add_parser("status", help="set a slice's Status on the board")
    p.add_argument("slice", help="e.g. M3.5")
    p.add_argument("value", help="Todo, In Progress or Done")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, RuntimeError) as err:
        sys.exit(str(err))


if __name__ == "__main__":
    main()
