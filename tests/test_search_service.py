# tests/test_search_service.py
"""
TDD: 高级搜索服务 - 全文检索、搜索建议、拼音搜索
"""

import pytest

from services.search_service import (
    PinyinHelper,
    SearchResult,
    SearchService,
    SearchSuggestion,
)


@pytest.fixture
def svc():
    s = SearchService()
    s.index(
        [
            {
                "id": "1",
                "type": "article",
                "title": "人工智能发展趋势",
                "content": "深度学习和大模型推动AI快速发展",
                "tags": ["AI", "科技"],
            },
            {
                "id": "2",
                "type": "article",
                "title": "新能源汽车市场分析",
                "content": "电动汽车销量持续增长，市场份额扩大",
                "tags": ["汽车", "新能源"],
            },
            {
                "id": "3",
                "type": "article",
                "title": "数字经济政策解读",
                "content": "国家出台多项政策支持数字经济发展",
                "tags": ["政策", "经济"],
            },
            {
                "id": "4",
                "type": "alert",
                "title": "负面舆情预警",
                "content": "检测到大量负面评论，情感分数骤降",
                "tags": ["预警"],
            },
            {
                "id": "5",
                "type": "article",
                "title": "绿色发展与碳中和",
                "content": "碳排放目标推动绿色能源转型",
                "tags": ["环保", "能源"],
            },
        ]
    )
    return s


# --- 全文检索 ---


def test_search_returns_results(svc):
    results = svc.search("人工智能")
    assert len(results) > 0
    assert all(isinstance(r, SearchResult) for r in results)


def test_search_matches_title(svc):
    results = svc.search("新能源")
    ids = [r.doc_id for r in results]
    assert "2" in ids


def test_search_matches_content(svc):
    results = svc.search("深度学习")
    ids = [r.doc_id for r in results]
    assert "1" in ids


def test_search_no_match_returns_empty(svc):
    results = svc.search("量子计算机芯片")
    assert results == []


def test_search_filter_by_type(svc):
    results = svc.search("发展", doc_type="article")
    assert all(r.doc_type == "article" for r in results)


def test_search_result_has_score(svc):
    results = svc.search("人工智能")
    assert all(r.score > 0 for r in results)


def test_search_results_sorted_by_score(svc):
    results = svc.search("发展")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_limit(svc):
    results = svc.search("发展", limit=2)
    assert len(results) <= 2


# --- 搜索建议 ---


def test_suggest_returns_suggestions(svc):
    suggestions = svc.suggest("人工")
    assert len(suggestions) > 0
    assert all(isinstance(s, SearchSuggestion) for s in suggestions)


def test_suggest_matches_prefix(svc):
    suggestions = svc.suggest("新能")
    texts = [s.text for s in suggestions]
    assert any("新能源" in t for t in texts)


def test_suggest_empty_query_returns_empty(svc):
    suggestions = svc.suggest("")
    assert suggestions == []


def test_suggest_limit(svc):
    suggestions = svc.suggest("发", limit=2)
    assert len(suggestions) <= 2


# --- 拼音搜索 ---


def test_pinyin_helper_to_pinyin():
    ph = PinyinHelper()
    result = ph.to_pinyin("人工智能")
    assert "rengong" in result.lower() or "ren" in result.lower()


def test_pinyin_helper_to_initials():
    ph = PinyinHelper()
    result = ph.to_initials("人工智能")
    assert result.lower() == "rgzn"


def test_search_by_pinyin(svc):
    results = svc.search("rgzn")
    ids = [r.doc_id for r in results]
    assert "1" in ids


def test_search_by_full_pinyin(svc):
    results = svc.search("rengongzhineng")
    ids = [r.doc_id for r in results]
    assert "1" in ids


# --- 索引管理 ---


def test_index_add_document(svc):
    svc.index_one(
        {
            "id": "99",
            "type": "article",
            "title": "量子计算突破",
            "content": "量子比特实现新突破",
            "tags": [],
        }
    )
    results = svc.search("量子计算")
    assert any(r.doc_id == "99" for r in results)


def test_index_remove_document(svc):
    svc.remove("1")
    results = svc.search("人工智能")
    assert not any(r.doc_id == "1" for r in results)


def test_index_count(svc):
    assert svc.count() == 5
