from fastapi.testclient import TestClient
from app.main import app

def test_read_root():
    # Use context manager to trigger lifespan events (DB setup and data loading)
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the Better Cotton Exercise API!"}

def test_get_organisations():
    with TestClient(app) as client:
        response = client.get("/organisations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "org_id" in data[0]

def test_get_transactions():
    with TestClient(app) as client:
        response = client.get("/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        
        # Test Rule 1: Unit conversion (TXN-0114 was 90 bales)
        txn_114 = next((t for t in data if t["txn_ref"] == "TXN-0114"), None)
        assert txn_114 is not None
        assert txn_114["quantity"] == 90.0 * 165.0
        assert txn_114["unit"] == "kg"
        
        # Test Rule 2: Missing buyer X-99 (TXN-0119) should be discarded
        txn_119 = next((t for t in data if t["txn_ref"] == "TXN-0119"), None)
        assert txn_119 is None
