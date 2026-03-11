import os
from unittest.mock import patch
from src.collectors.google_news import fetch_google_news, collect_all_google_news
from src.models import NewsItem


def _load_fixture(name):
    path = os.path.join(os.path.dirname(__file__), "fixtures", name)
    with open(path, "r") as f:
        return f.read()


def test_fetch_google_news_parses_items():
    import feedparser
    xml = _load_fixture("google_news_sample.xml")
    parsed = feedparser.parse(xml)
    with patch("src.collectors.google_news.feedparser.parse") as mock_parse:
        mock_parse.return_value = parsed
        items = fetch_google_news("https://news.google.com/rss/search?q=AI")
    assert len(items) == 2
    assert items[0].source == "Google News"
    assert isinstance(items[0], NewsItem)


def test_fetch_google_news_returns_empty_on_error():
    with patch("src.collectors.google_news.feedparser.parse", side_effect=Exception("fail")):
        items = fetch_google_news("https://bad.url")
    assert items == []


def test_collect_all_google_news_aggregates():
    fake = [NewsItem(id="1", title="T", description="D", url="https://x.com", source="Google News", published="2026-03-11")]
    with patch("src.collectors.google_news.fetch_google_news", return_value=fake):
        items, stats = collect_all_google_news(["https://q1", "https://q2"])
    assert len(items) == 2
    assert stats["total_queries"] == 2
