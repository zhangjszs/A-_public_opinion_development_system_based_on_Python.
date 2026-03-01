#!/usr/bin/env python3
"""
报告数据 API 测试
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.jwt_handler import create_token


@pytest.fixture
def app():
    from app import app

    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def _auth_headers():
    token = create_token(1, "report_tester")
    return {"Authorization": f"Bearer {token}"}


def test_report_data_returns_core_fields(client):
    response = client.get("/api/report/data", headers=_auth_headers())

    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body.get("code") == 200

    payload = body.get("data", {})
    for key in [
        "summary",
        "hot_topics",
        "alerts",
        "trend",
        "demo_mode",
        "data_source",
    ]:
        assert key in payload


def test_report_data_demo_mode_explicit(client):
    response = client.get("/api/report/data?demo=true", headers=_auth_headers())

    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body.get("code") == 200

    payload = body.get("data", {})
    assert payload.get("demo_mode") is True
    assert payload.get("data_source") == "demo"
    assert payload.get("summary", {}).get("total_articles", 0) > 0
