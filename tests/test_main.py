from fastapi import status
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch

client = TestClient(app)


# >>> python -m pytest tests/

def test_get():
    responce = client.get("/")

    assert responce.status_code == status.HTTP_200_OK
    assert responce.json() == {"message": "success"}
