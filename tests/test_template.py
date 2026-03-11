from src.email.template import build_email_html, build_subject
from src.models import NewsItem


def _make_categorized_items():
    return [
        NewsItem(id="1", title="GPT-5发布", description="", url="https://a.com",
                 source="TechCrunch", published="2026-03-11", category="模型发布",
                 summary_zh="OpenAI发布了GPT-5，支持自主操作电脑。"),
        NewsItem(id="2", title="Meta收购Moltbook", description="", url="https://b.com",
                 source="The Verge", published="2026-03-11", category="公司动向",
                 summary_zh="Meta收购了AI社交平台Moltbook。", extra_sources=["36氪"]),
        NewsItem(id="3", title="新论文：LLM推理", description="", url="https://c.com",
                 source="ArXiv", published="2026-03-11", category="研究论文",
                 summary_zh="一篇关于LLM推理能力的新论文。"),
    ]


def test_build_email_html_contains_categories():
    items = _make_categorized_items()
    html = build_email_html(items)
    assert "模型发布" in html
    assert "公司动向" in html
    assert "研究论文" in html
    assert "GPT-5发布" in html
    assert "Meta收购Moltbook" in html


def test_build_email_html_contains_sources_and_links():
    items = _make_categorized_items()
    html = build_email_html(items)
    assert "https://a.com" in html
    assert "TechCrunch" in html
    assert "36氪" in html  # extra source


def test_build_email_html_contains_summary():
    items = _make_categorized_items()
    html = build_email_html(items)
    assert "OpenAI发布了GPT-5" in html


def test_build_email_html_has_footer():
    items = _make_categorized_items()
    html = build_email_html(items)
    assert "共 3 条" in html


def test_build_subject():
    subject = build_subject(30)
    assert "AI 日报" in subject
    assert "(30条)" in subject
