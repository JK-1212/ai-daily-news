from src.config import RSS_FEEDS, GOOGLE_NEWS_QUERIES, ARXIV_KEYWORDS, CATEGORIES


def test_rss_feeds_not_empty():
    assert len(RSS_FEEDS) >= 12


def test_rss_feeds_have_name_and_url():
    for feed in RSS_FEEDS:
        assert "name" in feed
        assert "url" in feed
        assert feed["url"].startswith("http")


def test_google_news_queries():
    assert len(GOOGLE_NEWS_QUERIES) == 5
    for q in GOOGLE_NEWS_QUERIES:
        assert "news.google.com" in q


def test_arxiv_keywords():
    assert "LLM" in ARXIV_KEYWORDS
    assert "agent" in ARXIV_KEYWORDS


def test_categories():
    assert len(CATEGORIES) == 6
    assert "模型发布" in CATEGORIES
    assert "公司动向" in CATEGORIES
