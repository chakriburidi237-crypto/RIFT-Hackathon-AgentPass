"""
Demo: simulates an AI agent that has been handed a scoped AgentPass identity
and uses it to browse + purchase in the mock marketplace — then shows what
happens when it oversteps its budget, and after its human revokes it.

Run the API first: uvicorn main:app --reload --port 8000
Then:              python demo_agent.py
"""

import requests


BASE = "http://localhost:8000"


def main():
    print("== 1. Human adopts an agent and delegates identity ==")
    resp = requests.post(f"{BASE}/agents", json={
        "name": "Surya's Shopping Agent",
        "owner": "surya",
        "purpose": "Buy peripherals under a fixed budget",
        "scopes": ["browse", "purchase"],
        "spend_limit": 5000,
        "ttl_hours": 24,
    })
    resp.raise_for_status()
    data = resp.json()
    agent_id, token = data["agent_id"], data["token"]
    print(f"Agent ID: {agent_id}")
    print(f"Token (truncated): {token[:40]}...")
    headers = {"Authorization": f"Bearer {token}"}

    print("\n== 2. Agent browses the catalog ==")
    catalog = requests.get(f"{BASE}/catalog").json()
    for item in catalog:
        print(f" - {item['name']}: Rs.{item['price']}")

    cheap_item = min(catalog, key=lambda i: i["price"])
    expensive_item = max(catalog, key=lambda i: i["price"])

    print(f"\n== 3. Agent purchases within budget: {cheap_item['name']} ==")
    r = requests.post(f"{BASE}/marketplace/purchase", json={"item_id": cheap_item["id"]},
                       headers=headers)
    print(r.status_code, r.json())

    print(f"\n== 4. Agent attempts a purchase beyond remaining budget: {expensive_item['name']} ==")
    r = requests.post(f"{BASE}/marketplace/purchase", json={"item_id": expensive_item["id"]},
                       headers=headers)
    print(r.status_code, r.json())

    print("\n== 5. Human revokes the agent's identity ==")
    requests.post(f"{BASE}/agents/{agent_id}/revoke")

    print("\n== 6. Agent tries to purchase again after revocation ==")
    r = requests.post(f"{BASE}/marketplace/purchase", json={"item_id": cheap_item["id"]},
                       headers=headers)
    print(r.status_code, r.json())

    print("\n== 7. Trust log for this agent ==")
    log = requests.get(f"{BASE}/agents/{agent_id}").json()["actions"]
    for entry in log:
        print(f" [{entry['timestamp']}] {entry['action_type']} -> {entry['result']} "
              f"({entry['detail']})")


if __name__ == "__main__":
    main()
