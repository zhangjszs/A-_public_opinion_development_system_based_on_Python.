# tests/test_report_template.py
"""
TDD: 报告模板系统
"""
import os
import tempfile
import pytest
from utils.report_generator import (
    ReportTemplate, TemplateRegistry,
    PDFReportGenerator, PPTReportGenerator, ReportConfig,
)


# --- TemplateRegistry ---

def test_registry_has_default_templates():
    reg = TemplateRegistry()
    names = reg.list_templates()
    assert 'default' in names
    assert 'minimal' in names
    assert 'detailed' in names


def test_registry_get_template_returns_template():
    reg = TemplateRegistry()
    t = reg.get('default')
    assert isinstance(t, ReportTemplate)


def test_registry_get_unknown_raises():
    reg = TemplateRegistry()
    with pytest.raises(KeyError):
        reg.get('nonexistent_template_xyz')


def test_registry_register_custom_template():
    reg = TemplateRegistry()
    custom = ReportTemplate(
        name='custom',
        title='自定义报告',
        include_charts=False,
        include_tables=True,
        sections=['summary'],
    )
    reg.register(custom)
    assert 'custom' in reg.list_templates()
    assert reg.get('custom') is custom


# --- ReportTemplate ---

def test_template_to_config_returns_report_config():
    t = ReportTemplate(
        name='test',
        title='测试报告',
        include_charts=True,
        include_tables=True,
        sections=['summary', 'hot_topics'],
    )
    config = t.to_config()
    assert isinstance(config, ReportConfig)
    assert config.title == '测试报告'
    assert config.include_charts is True


def test_minimal_template_has_no_charts():
    reg = TemplateRegistry()
    t = reg.get('minimal')
    config = t.to_config()
    assert config.include_charts is False


def test_detailed_template_has_charts():
    reg = TemplateRegistry()
    t = reg.get('detailed')
    config = t.to_config()
    assert config.include_charts is True


def test_template_sections_filter_data():
    t = ReportTemplate(
        name='summary_only',
        title='摘要报告',
        include_charts=False,
        include_tables=True,
        sections=['summary'],
    )
    full_data = {
        'summary': {'positive_count': 10, 'neutral_count': 5, 'negative_count': 2,
                    'total_articles': 17, 'total_comments': 30},
        'hot_topics': [{'name': '话题1', 'heat': 100}],
        'alerts': [{'level': 'info', 'title': 'test', 'message': 'msg'}],
    }
    filtered = t.filter_data(full_data)
    assert 'summary' in filtered
    assert 'hot_topics' not in filtered
    assert 'alerts' not in filtered


# --- PDF with template ---

def test_pdf_generate_with_minimal_template(sample_data):
    reg = TemplateRegistry()
    gen = PDFReportGenerator()
    config = reg.get('minimal').to_config()
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        out = f.name
    try:
        result = gen.generate(sample_data, output_path=out, config=config)
        assert result == out
        assert os.path.getsize(out) > 0
    finally:
        if os.path.exists(out):
            os.unlink(out)


def test_pdf_generate_with_detailed_template(sample_data):
    reg = TemplateRegistry()
    gen = PDFReportGenerator()
    config = reg.get('detailed').to_config()
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        out = f.name
    try:
        result = gen.generate(sample_data, output_path=out, config=config)
        assert result == out
        assert os.path.getsize(out) > 0
    finally:
        if os.path.exists(out):
            os.unlink(out)


# --- PPT with template ---

def test_ppt_generate_with_minimal_template(sample_data):
    reg = TemplateRegistry()
    gen = PPTReportGenerator()
    config = reg.get('minimal').to_config()
    with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as f:
        out = f.name
    try:
        result = gen.generate(sample_data, output_path=out, config=config)
        assert result == out
        assert os.path.getsize(out) > 0
    finally:
        if os.path.exists(out):
            os.unlink(out)


@pytest.fixture
def sample_data():
    return {
        'summary': {'positive_count': 100, 'neutral_count': 50, 'negative_count': 30,
                    'total_articles': 180, 'total_comments': 500},
        'hot_topics': [{'name': f'话题{i}', 'heat': 100 - i * 10} for i in range(5)],
        'alerts': [
            {'level': 'danger', 'title': '严重预警', 'message': '负面情感激增'},
            {'level': 'warning', 'title': '一般预警', 'message': '热度上升'},
        ],
        'trend': [
            {'date': '2026-02-01', 'count': 120},
            {'date': '2026-02-02', 'count': 150},
        ],
    }
