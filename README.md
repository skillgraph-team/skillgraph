# SkillGraph

Evidence-based skills profiles for students: what you can actually do, the evidence behind it, and the internships it fits. In English, French and Arabic. Built by a team of four as a semester startup project.

- **Original project report:** [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md)
- **Spec (what we're actually building):** [docs/SPEC.md](docs/SPEC.md)
- **Plan (milestones and slices):** [docs/MILESTONES.md](docs/MILESTONES.md)
- **Decisions:** [docs/DECISIONS.md](docs/DECISIONS.md)
- **Rules for coding agents (and humans):** [CLAUDE.md](CLAUDE.md)
- **Glossary:** [docs/GLOSSARY.md](docs/GLOSSARY.md)
- **Board:** see the "SkillGraph" Project linked to this repo

## How we work

The project is split into milestones and 77 small **slices** ([docs/MILESTONES.md](docs/MILESTONES.md)). Each slice is a GitHub issue on the board that says what to build, why, what to read first, the steps, and how to know it's done. Anyone can take any slice, with whatever tool they use.

1. **Pick** an unassigned slice on the board whose `Depends on` slices are all Done.
2. **Claim** it: assign yourself and set Status to *In Progress*.
3. **Do it**, one slice per session or chat:
   - Claude Code: just say "let's do M3.5"; CLAUDE.md tells it the steps
   - Claude chatbot: [docs/CHAT_KIT.md](docs/CHAT_KIT.md)
   - Google Antigravity: [docs/CHAT_KIT_ANTIGRAVITY.md](docs/CHAT_KIT_ANTIGRAVITY.md) (English and Algerian Darija)
   - Any other coding agent: it reads `AGENTS.md`
4. **Open a pull request** that closes the issue, with the template filled in, including a plain-language review guide.
5. **Review:** Rasen reviews and merges teammates' pull requests ("review PR 12" in Claude Code). Rasen's own work goes straight to `main`, with a summary on the issue (D-016). Merging or closing moves the card to Done.

Rules:
- A claim with no commit for 3 days can be taken over after a message in the group chat.
- Slices marked `contract` (evidence model, schema, message format, API) are approved by Rasen, and later changes need the contract owner's (D-018).
- Rasen's PR review is the only approval your work needs (D-018). The summaries Rasen posts on issues for direct pushes explain how things work, if you want the details.
- A slice was unclear? Improve its text in `docs/MILESTONES.md` so the next person doesn't hit the same question.
- Never commit `.env`, API keys or real people's personal data.
- Unfamiliar term: [docs/GLOSSARY.md](docs/GLOSSARY.md).

## Getting started

Everyone runs the app locally. Install Git, Docker Desktop (or Docker Engine), [uv](https://docs.astral.sh/uv/), Node.js LTS, and either GitHub Desktop + VS Code (chatbot workflow, `docs/CHAT_KIT.md` part B) or the GitHub CLI `gh` (Claude Code workflow). The commands below can also be run from GitHub Desktop's *Repository → Open in Terminal*.

```bash
gh auth login
git clone https://github.com/skillgraph-team/skillgraph.git
cd skillgraph
cp .env.example .env
docker compose up -d db          # from M0.3
cd backend && uv sync && uv run alembic upgrade head && uv run pytest   # from M0.2/M0.3
cd ../frontend && npm install && npm run dev                            # from M0.4
```

If you use Claude Code (it updates the board for you), also run `gh auth refresh -s project` once.

_This section is completed and checked by every member in slice M0.6._
