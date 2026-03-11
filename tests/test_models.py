from src.models import NewsItem


def test_news_item_creation():
    item = NewsItem(
        id="tc-001",
        title="OpenAI releases GPT-5",
        description="OpenAI announced GPT-5 with improved reasoning.",
        url="https://techcrunch.com/openai-gpt5",
        source="TechCrunch",
        published="2026-03-11T08:00:00Z",
    )
    assert item.title == "OpenAI releases GPT-5"
    assert item.source == "TechCrunch"
    assert item.category is None
    assert item.summary_zh is None


def test_news_item_with_optional_fields():
    item = NewsItem(
        id="tc-002",
        title="Meta acquires startup",
        description="Meta acquired an AI startup.",
        url="https://example.com",
        source="The Verge",
        published="2026-03-11T09:00:00Z",
        category="公司动向",
        summary_zh="Meta收购了一家AI创业公司。",
    )
    assert item.category == "公司动向"
    assert item.summary_zh == "Meta收购了一家AI创业公司。"
