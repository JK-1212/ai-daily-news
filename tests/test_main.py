import os
from unittest.mock import patch, MagicMock
from src.main import run_pipeline
from src.models import NewsItem


def _make_items(n, source="Test"):
    return [
        NewsItem(id=str(i), title=f"Item {i}", description=f"Desc {i}",
                 url=f"https://example.com/{i}", source=source, published="2026-03-11")
        for i in range(n)
    ]


@patch.dict(os.environ, {"EMAIL_TO": "user@test.com", "EMAIL_FROM": "bot@test.com"})
@patch("src.main.send_email", return_value=True)
@patch("src.main.build_email_html", return_value="<p>html</p>")
@patch("src.main.build_subject", return_value="AI 日报")
@patch("src.main.process_with_ai")
@patch("src.main.deduplicate")
@patch("src.main.filter_arxiv_items")
@patch("src.main.collect_all_google_news")
@patch("src.main.collect_all_rss")
def test_run_pipeline_success(
    mock_rss, mock_gnews, mock_arxiv, mock_dedup, mock_ai,
    mock_subject, mock_html, mock_send
):
    rss_items = _make_items(10, source="TechCrunch")
    mock_rss.return_value = (rss_items, {"success": 1, "failed": 0, "details": {}})
    mock_gnews.return_value = (_make_items(5, source="Google News"), {"total_queries": 5, "total_items": 5})
    mock_arxiv.return_value = _make_items(3, source="ArXiv")
    mock_dedup.return_value = _make_items(12)
    processed = _make_items(5)
    for item in processed:
        item.category = "模型发布"
        item.summary_zh = "摘要"
    mock_ai.return_value = processed

    result = run_pipeline()
    assert result is True
    mock_send.assert_called_once()


@patch.dict(os.environ, {"EMAIL_TO": "user@test.com", "EMAIL_FROM": "bot@test.com"})
@patch("src.main.send_email", return_value=False)
@patch("src.main.build_email_html", return_value="<p>html</p>")
@patch("src.main.build_subject", return_value="AI 日报")
@patch("src.main.process_with_ai", return_value=[])
@patch("src.main.deduplicate", return_value=[])
@patch("src.main.filter_arxiv_items", return_value=[])
@patch("src.main.collect_all_google_news", return_value=([], {"total_queries": 5, "total_items": 0}))
@patch("src.main.collect_all_rss", return_value=([], {"success": 0, "failed": 13, "details": {}}))
def test_run_pipeline_no_items(mock_rss, mock_gnews, mock_arxiv, mock_dedup, mock_ai, mock_subject, mock_html, mock_send):
    result = run_pipeline()
    # No items after AI processing → returns False without sending
    assert result is False
    mock_send.assert_not_called()
