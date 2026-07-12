"""
AgentPass — Identity & Trust Infrastructure for AI Agents
Problem Statement 2: "AI's First Day Online"

A human "adopts" an AI agent, grants it a scoped, time-limited, revocable
identity (a signed token), and the agent uses that identity to act in a
mock marketplace. Every action is written to a public trust log so the
human (or anyone) can audit exactly what the agent did, under what
authority, and revoke it instantly if something looks wrong.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Then open frontend/index.html in a browser (it points at localhost:8000).
"""

import sqlite3
import time
import uuid
import jwt
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SECRET_KEY = "agentpass-hackathon-demo-secret-do-not-use-in-prod"
ALGO = "HS256"
DB_PATH = "agentpass.db"

VALID_SCOPES = {"browse", "purchase", "negotiate", "post", "moderate"}

app = FastAPI(title="AgentPass API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner TEXT NOT NULL,
                purpose TEXT,
                scopes TEXT NOT NULL,
                spend_limit REAL NOT NULL DEFAULT 0,
                spent REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                detail TEXT,
                amount REAL DEFAULT 0,
                result TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS catalog (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)
        row = conn.execute("SELECT COUNT(*) c FROM catalog").fetchone()
        if row["c"] == 0:
            items = [
                ("USB-C Cable (2m)", 249),
                ("Mechanical Keyboard", 3499),
                ("Wireless Mouse", 899),
                ("27-inch Monitor", 15999),
                ("Noise Cancelling Headphones", 5999),
            ]
            for name, price in items:
                conn.execute(
                    "INSERT INTO catalog (id, name, price) VALUES (?, ?, ?)",
                    (str(uuid.uuid4()), name, price),
                )


init_db()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class CreateAgentRequest(BaseModel):
    name: str
    owner: str
    purpose: str = ""
    scopes: list[str] = Field(default_factory=lambda: ["browse"])
    spend_limit: float = 0
    ttl_hours: int = 24


class PurchaseRequest(BaseModel):
    item_id: str


class LogAction(BaseModel):
    action_type: str
    detail: str = ""
    amount: float = 0


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def issue_token(agent_id: str, owner: str, scopes: list[str], expires_at: datetime) -> str:
    payload = {
        "sub": agent_id,
        "owner": owner,
        "scopes": scopes,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Agent identity token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid agent identity token")


def get_agent_row(agent_id: str):
    with db() as conn:
        row = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Agent not found")
    return row


def require_agent(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing agent bearer token")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    agent = get_agent_row(payload["sub"])
    if agent["status"] != "active":
        raise HTTPException(403, f"Agent identity is {agent['status']}, action refused")
    return {"payload": payload, "agent": agent}


def log_action(agent_id: str, action_type: str, detail: str, amount: float, result: str):
    with db() as conn:
        conn.execute(
            "INSERT INTO actions (id, agent_id, action_type, detail, amount, result, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), agent_id, action_type, detail, amount, result,
             datetime.now(timezone.utc).isoformat()),
        )


# ---------------------------------------------------------------------------
# Routes — Identity issuance & lifecycle
# ---------------------------------------------------------------------------

@app.post("/agents")
def create_agent(req: CreateAgentRequest):
    bad_scopes = set(req.scopes) - VALID_SCOPES
    if bad_scopes:
        raise HTTPException(400, f"Unknown scopes: {sorted(bad_scopes)}")

    agent_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=req.ttl_hours)

    with db() as conn:
        conn.execute(
            "INSERT INTO agents (id, name, owner, purpose, scopes, spend_limit, spent, "
            "status, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, 0, 'active', ?, ?)",
            (agent_id, req.name, req.owner, req.purpose, ",".join(req.scopes),
             req.spend_limit, created_at.isoformat(), expires_at.isoformat()),
        )

    token = issue_token(agent_id, req.owner, req.scopes, expires_at)
    log_action(agent_id, "identity_issued",
               f"Adopted by {req.owner} with scopes {req.scopes}", 0, "granted")

    return {"agent_id": agent_id, "token": token, "expires_at": expires_at.isoformat()}


@app.get("/agents")
def list_agents():
    with db() as conn:
        rows = conn.execute("SELECT * FROM agents ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    agent = get_agent_row(agent_id)
    with db() as conn:
        actions = conn.execute(
            "SELECT * FROM actions WHERE agent_id = ? ORDER BY timestamp DESC", (agent_id,)
        ).fetchall()
    return {"agent": dict(agent), "actions": [dict(a) for a in actions]}


@app.post("/agents/{agent_id}/revoke")
def revoke_agent(agent_id: str):
    agent = get_agent_row(agent_id)
    with db() as conn:
        conn.execute("UPDATE agents SET status = 'revoked' WHERE id = ?", (agent_id,))
    log_action(agent_id, "identity_revoked", f"Revoked by owner {agent['owner']}", 0, "revoked")
    return {"status": "revoked"}


# ---------------------------------------------------------------------------
# Routes — Mock marketplace an agent can act in
# ---------------------------------------------------------------------------

@app.get("/catalog")
def get_catalog():
    with db() as conn:
        rows = conn.execute("SELECT * FROM catalog").fetchall()
    return [dict(r) for r in rows]


@app.post("/marketplace/purchase")
def purchase(req: PurchaseRequest, ctx: dict = Depends(require_agent)):
    agent = ctx["agent"]
    payload = ctx["payload"]

    if "purchase" not in payload["scopes"]:
        log_action(agent["id"], "purchase_attempt", req.item_id, 0, "denied_scope")
        raise HTTPException(403, "Agent identity does not carry 'purchase' scope")

    with db() as conn:
        item = conn.execute("SELECT * FROM catalog WHERE id = ?", (req.item_id,)).fetchone()
    if not item:
        raise HTTPException(404, "Item not found")

    remaining = agent["spend_limit"] - agent["spent"]
    if item["price"] > remaining:
        log_action(agent["id"], "purchase_attempt", item["name"], item["price"], "denied_limit")
        raise HTTPException(
            403,
            f"Purchase of ₹{item['price']} exceeds remaining delegated budget of ₹{remaining:.2f}",
        )

    with db() as conn:
        conn.execute("UPDATE agents SET spent = spent + ? WHERE id = ?",
                      (item["price"], agent["id"]))
    log_action(agent["id"], "purchase", item["name"], item["price"], "approved")

    return {"result": "approved", "item": item["name"], "price": item["price"]}


@app.post("/agents/{agent_id}/log")
def manual_log(agent_id: str, req: LogAction, ctx: dict = Depends(require_agent)):
    """Lets an agent log a non-purchase action (browse, negotiate, post) it took,
    provided its token carries that scope. Keeps the trust log complete."""
    if req.action_type not in ctx["payload"]["scopes"]:
        raise HTTPException(403, f"Agent identity does not carry '{req.action_type}' scope")
    log_action(agent_id, req.action_type, req.detail, req.amount, "logged")
    return {"result": "logged"}


# ---------------------------------------------------------------------------
# Global trust log
# ---------------------------------------------------------------------------

@app.get("/trust-log")
def trust_log(limit: int = 50):
    with db() as conn:
        rows = conn.execute(
            "SELECT actions.*, agents.name as agent_name, agents.owner as owner "
            "FROM actions JOIN agents ON actions.agent_id = agents.id "
            "ORDER BY actions.timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/")
def root():
    return {"service": "AgentPass API", "status": "ok"}
