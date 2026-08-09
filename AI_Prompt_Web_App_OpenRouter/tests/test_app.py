import os
import tempfile
from pathlib import Path

import pytest

os.environ["AI_PROVIDER"] = "mock"

import app as app_module


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    app_module.init_db()

    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"AI Prompt Web App" in response.data


def test_empty_prompt(client):
    response = client.post(
        "/api/prompt",
        json={"prompt": "", "template": "general"},
    )
    assert response.status_code == 400
    assert response.get_json()["ok"] is False


def test_mock_prompt(client):
    response = client.post(
        "/api/prompt",
        json={"prompt": "Explain Flask", "template": "explain"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["ok"] is True
    assert data["provider_mode"] == "mock"
    assert "Explain Flask" in data["response"]


def test_oversized_prompt(client, monkeypatch):
    monkeypatch.setattr(app_module, "MAX_PROMPT_LENGTH", 10)
    response = client.post(
        "/api/prompt",
        json={"prompt": "12345678901", "template": "general"},
    )
    assert response.status_code == 413


def test_history_search(client):
    client.post(
        "/api/prompt",
        json={"prompt": "Python decorators", "template": "general"},
    )

    response = client.get("/history?q=decorators")
    assert response.status_code == 200
    assert b"Python decorators" in response.data


def test_openrouter_mode_without_key(client, monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openrouter")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    response = client.post(
        "/api/prompt",
        json={"prompt": "Hello OpenRouter", "template": "general"},
    )

    assert response.status_code == 502
    assert response.get_json()["status"] == "provider_error"
