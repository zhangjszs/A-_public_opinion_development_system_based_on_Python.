from flask import Flask, request

from config.settings import Config
from utils.authz import admin_required


def test_admin_required_blocks_when_not_admin(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(Config, "ADMIN_USERS", {"admin"})

    @admin_required
    def handler():
        return "ok", 200

    with app.test_request_context("/"):
        request.current_user = {"username": "user"}
        body, status = handler()
        assert status == 403


def test_admin_required_allows_admin(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(Config, "ADMIN_USERS", {"admin"})

    @admin_required
    def handler():
        return "ok", 200

    with app.test_request_context("/"):
        request.current_user = {"username": "admin"}
        body, status = handler()
        assert status == 200

