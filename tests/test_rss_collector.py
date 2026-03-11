import os
from unittest.mock import patch, MagicMock
from src.collectors.rss_collector import fetch_rss_feed, collect_all_rss
from src.models import NewsItem


def _load_fixture(name):
    path = os.path.join(os.path.dirname(__file__), "fixtures", name)
    with open(path, "r") as f:
        return f.read()


def test_fetch_rss_feed_parses_items(tmp_path):
    import feedparser
    xml = _load_fixture("techcrunch_sample.xml")
    parsed = feedparser.parse(xml)
    with patch("src.collectors.rss_collector.feedparser.parse") as mock_parse:
        mock_parse.return_value = parsed
        items = fetch_rss_feed("TechCrunch AI", "https://example.com/feed")
    assert len(items) == 3
    assert items[0].title == "OpenAI releases GPT-5"
    assert items[0].source == "TechCrunch AI"
    assert isinstance(items[0], NewsItem)


def test_fetch_rss_feed_returns_empty_on_error():
    with patch("src.collectors.rss_collector.feedparser.parse", side_effect=Exception("Network error")):
        items = fetch_rss_feed("Bad Feed", "https://bad.example.com/feed")
    assert items == []


def test_collect_all_rss_aggregates():
    fake_items = [
        NewsItem(id="1", title="News 1", description="Desc", url="https://a.com", source="A", published="2026-03-11"),
    ]
    with patch("src.collectors.rss_collector.fetch_rss_feed", return_value=fake_items):
        feeds = [{"name": "A", "url": "https://a.com/feed"}, {"name": "B", "url": "https://b.com/feed"}]
        all_items, stats = collect_all_rss(feeds)
    assert len(all_items) == 2
    assert stats["success"] == 2
    assert stats["failed"] == 0
