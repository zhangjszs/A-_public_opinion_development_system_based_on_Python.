from flask import Flask, request
import pytest

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


def test_admin_required_blocks_when_admin_config_empty(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(Config, "ADMIN_USERS", set())

    @admin_required
    def handler():
        return "ok", 200

    with app.test_request_context("/"):
        request.current_user = {"username": "anyone"}
        body, status = handler()
        assert status == 403


@pytest.fixture
def api_client_with_mock_user(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(Config, "ADMIN_USERS", {"admin"})

    from views.api.api import bp as api_bp

    @app.before_request
    def _inject_user():
        username = request.headers.get("X-Test-User")
        if username:
            request.current_user = {"username": username, "user_id": 1}

    app.register_blueprint(api_bp)
    return app.test_client()


def test_spider_search_blocks_non_admin(api_client_with_mock_user):
    response = api_client_with_mock_user.post(
        "/api/spider/search",
        json={"keyword": "测试", "page_num": 1},
        headers={"X-Test-User": "user"},
    )
    assert response.status_code == 403


def test_spider_comments_blocks_non_admin(api_client_with_mock_user):
    response = api_client_with_mock_user.post(
        "/api/spider/comments",
        json={"article_limit": 1},
        headers={"X-Test-User": "user"},
    )
    assert response.status_code == 403


def test_task_status_blocks_non_admin(api_client_with_mock_user):
    response = api_client_with_mock_user.get(
        "/api/tasks/task-123/status",
        headers={"X-Test-User": "user"},
    )
    assert response.status_code == 403


def test_spider_refresh_submits_async_task_for_admin(api_client_with_mock_user, monkeypatch):
    import views.api.spider_api as spider_api

    def _fake_dispatch(*args, **kwargs):
        return {
            'task_id': 'task-hot-001',
            'task_label': '刷新热门微博',
            'crawl_type': 'hot',
            'keyword': '',
            'page_num': 2,
            'article_limit': 50,
        }

    def _fake_register(result):
        assert result['task_id'] == 'task-hot-001'

    monkeypatch.setattr(spider_api, 'dispatch_spider_task', _fake_dispatch)
    monkeypatch.setattr(spider_api, 'register_submitted_task', _fake_register)

    response = api_client_with_mock_user.post(
        "/api/spider/refresh",
        json={"page_num": 2},
        headers={"X-Test-User": "admin"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['code'] == 200
    assert payload['data']['task_id'] == 'task-hot-001'


@pytest.fixture
def spider_client_with_mock_user(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(Config, "ADMIN_USERS", {"admin"})

    from views.api.spider_api import spider_bp

    @app.before_request
    def _inject_user():
        username = request.headers.get("X-Test-User")
        if username:
            request.current_user = {"username": username, "user_id": 1}

    app.register_blueprint(spider_bp)
    return app.test_client()


def test_spider_crawl_submits_celery_task(spider_client_with_mock_user, monkeypatch):
    import views.api.spider_api as spider_api

    def _fake_dispatch(*args, **kwargs):
        return {
            'task_id': 'task-search-001',
            'task_label': '关键词搜索: 测试',
            'crawl_type': 'search',
            'keyword': '测试',
            'page_num': 1,
            'article_limit': 50,
        }

    called = {}

    def _fake_register(result):
        called['task_id'] = result['task_id']

    monkeypatch.setattr(spider_api, 'dispatch_spider_task', _fake_dispatch)
    monkeypatch.setattr(spider_api, 'register_submitted_task', _fake_register)

    response = spider_client_with_mock_user.post(
        "/api/spider/crawl",
        json={"type": "search", "keyword": "测试", "pageNum": 1},
        headers={"X-Test-User": "admin"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['code'] == 200
    assert payload['data']['task_id'] == 'task-search-001'
    assert called['task_id'] == 'task-search-001'

