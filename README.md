<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:E8A33D,100:2DD4BF&height=200&section=header&text=AgentPass&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Identity%20%26%20Trust%20Infrastructure%20for%20AI%20Agents&descAlignY=55&descSize=17" width="100%"/>

<br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-2A2A2A?style=for-the-badge&logo=gunicorn&logoColor=white)

<br/>

> ### 🛂 *"Give every AI agent a passport before it's let loose on the web"*
> **Scoped Identity • Delegated Trust • Live Audit Ledger**

<br/>

**RJFT 2026 · Problem Statement 2 — "AI's First Day Online"**

---

</div>

## 🎯 What Is This Project?

**AgentPass** is a working identity and trust layer for AI agents. A human **adopts** an agent and issues it a **passport** — a signed, scoped, time-limited, revocable token — instead of a blank set of credentials. The agent uses that passport to act in a mock marketplace, strictly within the limits it was granted, and every action it takes (approved or denied) is written to a public **trust ledger**.

In the 2000s every new website fought for space in the browser toolbar. Now AI agents are becoming the internet's new users — browsing, buying, negotiating, posting — without anyone building the infrastructure for them to do it safely. AgentPass is that infrastructure for one piece: **identity**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🛂 **Scoped Identity Issuance** | Every agent gets a signed JWT passport with specific granted scopes, never blanket access |
| 💰 **Delegated Spend Limits** | Agents can't spend past the budget their human set — enforced server-side, not just in the UI |
| ⏳ **Time-Limited Tokens** | Every passport expires; nothing is valid forever by default |
| 🚫 **One-Click Revocation** | A human can kill an agent's identity instantly, and every subsequent action is refused |
| 📜 **Live Trust Ledger** | Every issuance, approval, denial, and revocation is logged and publicly queryable |
| 🎫 **Visual Passport Cards** | Scopes render as stamps, spend as a live gauge, status as a badge |
| 🧪 **Provable Enforcement** | A demo script exercises the full lifecycle end-to-end — not just a UI mockup |

---

## 🏗️ Project Structure

```
agentpass/
│
├── backend/
│   ├── main.py              # FastAPI app — identity issuance, enforcement, trust ledger
│   ├── demo_agent.py         # Simulated AI agent exercising the full lifecycle
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   └── index.html            # Single-file React dashboard (no build step)
│
└── README.md
```

---

## 🎫 How a Passport Works

Every agent identity carries a small set of granted scopes drawn from a fixed vocabulary:

| Scope | Description |
|---|---|
| `browse` | Can look, cannot act |
| `purchase` | Can spend, up to its delegated limit |
| `negotiate` | Can make and log offers |
| `post` | Can publish on the agent's behalf |
| `moderate` | Can flag or act on other agents' content |

```python
# What issuing a passport looks like
POST /agents
{
  "name": "Shopping Agent",
  "owner": "surya",
  "scopes": ["browse", "purchase"],
  "spend_limit": 5000,
  "ttl_hours": 24
}
```

---

## 🤖 Identity Lifecycle

Built around a signed, verifiable token — not a session cookie, not an API key shared blindly.

### Lifecycle Pipeline:

```
Human adopts agent
    ↓
Passport issued (JWT: scopes + spend_limit + expiry, signed)
    ↓
Agent presents token on every action
    ↓
Server verifies signature + scope + remaining budget + status
    ↓
Action approved / denied  →  written to Trust Ledger
    ↓
Human can revoke instantly — all future actions refused
```

### Enforcement, not decoration:
```python
def require_agent(authorization):
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)          # signature + expiry checked
    agent = get_agent_row(payload["sub"])
    if agent["status"] != "active":
        raise HTTPException(403, "Agent identity is revoked, action refused")
    return {"payload": payload, "agent": agent}
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Identity** | PyJWT | Signed, scoped, expiring agent tokens |
| **Backend** | FastAPI, Uvicorn | REST API, request validation, CORS |
| **Persistence** | SQLite | Agents, spend state, trust ledger |
| **Frontend** | React 18 (CDN, no build step) | Passport dashboard, live ledger |
| **Styling** | Custom CSS | Passport/stamp visual system |
| **Demo Agent** | Python, requests | Proves enforcement end-to-end |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A modern browser (frontend needs no build tooling)

### Installation

```bash
# 1. Unzip / clone the project
cd agentpass/backend

# 2. Install dependencies
pip install -r requirements.txt
```

**requirements.txt:**
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pyjwt==2.8.0
pydantic==2.7.4
```

---

## ▶️ Running the Application

### Option 1 — Full Stack (Recommended)

```bash
# Terminal 1: Start Backend (from backend/ folder)
uvicorn main:app --reload --port 8000
# API starts at http://127.0.0.1:8000

# Then just open frontend/index.html in your browser directly
# (no dev server or build step needed)
```

### Option 2 — Enforcement Demo Only (Command Line)

```bash
# With the backend running, in another terminal:
python demo_agent.py

# Output:
# == 1. Human adopts an agent and delegates identity ==
# == 3. Agent purchases within budget: USB-C Cable (2m) ==
# == 4. Agent attempts a purchase beyond remaining budget → denied ==
# == 5. Human revokes the agent's identity ==
# == 6. Agent tries to act again → refused ==
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/agents` | Issue a new agent passport (returns token) |
| `GET` | `/agents` | List all adopted agents |
| `GET` | `/agents/<id>` | Get one agent's profile + its action history |
| `POST` | `/agents/<id>/revoke` | Revoke an agent's identity instantly |
| `GET` | `/catalog` | Mock marketplace items an agent can browse |
| `POST` | `/marketplace/purchase` | Agent attempts a purchase (requires Bearer token) |
| `POST` | `/agents/<id>/log` | Agent logs a scoped, non-purchase action |
| `GET` | `/trust-log` | Global, chronological trust ledger |

### Example — issuing a passport:

```bash
POST /agents
```

```json
{
  "agent_id": "db120254-d2bd-4b08-97ad-746ab94e50a2",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-07-12T11:54:04.078054+00:00"
}
```

---

## 🎨 Frontend — How It Works

```
Human fills out "Adopt an agent" form
        ↓
React POSTs to /agents, stores returned token for this session
        ↓
Passport card renders: scope stamps, spend gauge, status badge
        ↓
Human clicks "Act as agent: buy"
        ↓
React sends the agent's own token to /marketplace/purchase
        ↓
Approval or denial appears instantly, ledger updates within 4s
```

---

## 📈 What The Demo Proves

| Check | Result |
|---|---|
| **Purchase within budget** | ✅ Approved, spend gauge updates |
| **Purchase beyond remaining budget** | ❌ Denied — `403`, exact remaining budget returned |
| **Action after revocation** | ❌ Refused — `403`, "Agent identity is revoked" |
| **Every step above** | 📜 Written to the trust ledger with a timestamp |

---

## 🔮 Future Improvements

- [ ] 🔗 Delegation chains — agent-of-an-agent, with narrower scopes at each hop
- [ ] 🧠 Swap `demo_agent.py`'s fixed logic for a real Ollama-backed agent that decides what to buy, still bound by server-enforced scopes
- [ ] 🌐 Cross-service passports — one identity honored by multiple mock "sites," each seeing only the scopes relevant to them
- [ ] 🔐 Real owner authentication (currently single-owner demo scope)
- [ ] 📊 Add a ledger analytics view (denials over time, spend by agent)
- [ ] 🐳 Dockerize backend + frontend for one-command demo spin-up

---

## 👨‍💻 Developer

<div align="center">

**Surya Chakradhar Buridi**

*AI/ML Engineer | B.E. Artificial Intelligence & Machine Learning @ KIET*
*Ex-Industrial Trainee @ Schneider Electric, Bengaluru*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/surya-chakradhar-buridi-767548355)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/chakriburidi237-crypto)

</div>

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2DD4BF,100:E8A33D&height=100&section=footer" width="100%"/>

**⭐ Built for RJFT 2026 — Problem Statement 2: "AI's First Day Online"**

*Built with 🛂 by Surya Chakradhar Buridi*
*Associated with Kakinada Institute of Engineering and Technology (KIET)*

</div>
