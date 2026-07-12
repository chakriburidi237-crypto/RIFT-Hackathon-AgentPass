# AgentPass — Identity & Trust Infrastructure for AI Agents

**RJFT 2026 · Problem Statement 2: "AI's First Day Online"**

> In the 2000s every new website fought for space in the browser toolbar.
> Now AI agents are becoming the internet's new users — browsing, buying,
> negotiating, posting — without anyone building the infrastructure for
> them to do it safely. AgentPass is that infrastructure for one piece:
> **identity**.

## The idea

A human "adopts" an AI agent and issues it a **passport**: a signed,
scoped, time-limited, revocable identity token. The agent uses that
passport to act in a mock marketplace — browse, purchase — strictly
within the limits it was given. Every single action, approved or denied,
is written to a public **trust ledger** so the human (or anyone) can see
exactly what the agent did and under what authority, and can revoke it
instantly if something looks wrong.

This is not "add a login system for bots." It's the missing layer between
a human's intent and an autonomous agent's actions: **delegation with
receipts.**

## What's actually built (working, not a mockup)

- **FastAPI backend** (`backend/main.py`) — issues JWT-based agent
  identities with scopes (`browse`, `purchase`, `negotiate`, `post`,
  `moderate`), a delegated spend limit, and an expiry. A mock marketplace
  endpoint enforces those scopes and limits server-side — an agent
  literally cannot spend past its budget or act outside its granted
  scopes, because the API checks the signed token on every call.
- **Trust ledger** — every identity issuance, approved action, denied
  attempt, and revocation is logged with a timestamp and queryable via
  `/trust-log`.
- **React dashboard** (`frontend/index.html`, single file, no build step)
  — adopt an agent, see its live "passport" (scopes as stamps, a spend
  gauge, one-click revoke), and watch the trust ledger update as agents
  act.
- **`demo_agent.py`** — a script that plays the part of an AI agent:
  gets issued a passport, browses the catalog, makes a purchase within
  budget, tries one that blows the budget (denied), then gets revoked by
  its owner and tries again (refused) — proving the enforcement is real,
  not decorative.

## Run it

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open `frontend/index.html` directly in a browser (it talks to
`http://localhost:8000`).

To see the enforcement logic run end-to-end from the command line:

```bash
cd backend
python demo_agent.py
```

## How this maps to the judging criteria

| Criteria | How AgentPass addresses it |
|---|---|
| **Creativity & originality** | Reframes "auth" as a delegation problem specific to autonomous agents, not humans — the passport/stamp/ledger metaphor makes the abstract concept of scoped agent identity tangible. |
| **Functionality & usability** | Every constraint is enforced server-side and demonstrably works: scope checks, budget checks, revocation, all verified live via `demo_agent.py`. |
| **Technical execution** | Real signed tokens (JWT), real persistence (SQLite), a real audit trail, clean separation between issuance, enforcement, and logging. |
| **Presentation & demo** | Dashboard visualizes the full lifecycle — issue, act, deny, revoke — with a live trust ledger so judges can watch cause and effect. |
| **AI integration (bonus)** | The AI agent is the literal end-user of this infrastructure; the whole system exists to give *it* an identity, not a human. |

## Where this goes next

- Delegation chains (agent-of-an-agent, with narrower scopes at each hop)
- Real LLM-driven agent (swap `demo_agent.py`'s fixed logic for an
  Ollama-backed agent that decides what to buy, still bound by the same
  server-enforced scopes)
- Cross-service passports — one identity, honored by multiple mock
  "sites," each seeing only the scopes relevant to them
