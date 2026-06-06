"""Tests for TurboServe API"""
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.serving.server import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_completions_basic():
    with patch("src.serving.server._generate", new=AsyncMock(return_value={
        "choices": [{"text": "Paris", "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 1}
    })):
        r = client.post("/v1/completions", json={
            "prompt": "The capital of France is",
            "max_tokens": 10,
            "stream": False
        })
    assert r.status_code == 200
    assert "choices" in r.json()

def test_queue_depth_returns_to_zero():
    from src.serving.server import QUEUE_DEPTH
    initial = QUEUE_DEPTH._value.get()
    # After request completes, queue depth should return to initial
    with patch("src.serving.server._generate", new=AsyncMock(return_value={
        "choices": [{"text": "test"}],
        "usage": {"prompt_tokens": 2, "completion_tokens": 1}
    })):
        client.post("/v1/completions", json={"prompt": "test"})
    assert QUEUE_DEPTH._value.get() == initial
