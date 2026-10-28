import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_catalog_retrieval():
    response = client.get("/catalog")
    assert response.status_code == 200
    catalog = response.json()
    assert isinstance(catalog, list)
    assert len(catalog) > 0

def test_agent_registration_and_token_delegation():
    payload = {
        "name": "Audit Test Agent",
        "owner": "chakradhar",
        "purpose": "Automated security test validation",
        "scopes": ["browse", "purchase"],
        "spend_limit": 3000,
        "ttl_hours": 12
    }
    response = client.post("/agents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert "token" in data
    
    agent_id = data["agent_id"]
    token = data["token"]
    
    # Verify agent inspection
    get_agent = client.get(f"/agents/{agent_id}")
    assert get_agent.status_code == 200
    agent_data = get_agent.json()
    assert agent_data["name"] == "Audit Test Agent"
    assert agent_data["status"] == "active"

def test_trust_log_audit():
    response = client.get("/trust-log")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
