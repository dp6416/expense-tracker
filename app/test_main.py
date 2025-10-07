#test/test_main.py
from fastapi.testclient import TestClient
from app.main import app
from app import database, models

client = TestClient(app)

def test_health():
    response = client.get("/health")
    