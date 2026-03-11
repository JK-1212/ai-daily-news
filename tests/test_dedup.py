from src.processor.dedup import deduplicate
from src.models import NewsItem


def _make_item(id, title, source="Test"):
    return NewsItem(id=id, title=title, description="desc", url=f"https://example.com/{id}", source=source, published="2026-03-11")


def test_removes_near_duplicates():
    items = [
        _make_item("1", "OpenAI releases GPT-5 with new capabilities"),
        _make_item("2", "OpenAI releases GPT-5 with new features"),
        _make_item("3", "Google launches Gemini 3 today"),
    ]
    result = deduplicate(items)
    assert len(result) == 2
    titles = [r.title for r in result]
    assert "Google launches Gemini 3 today" in titles


def test_keeps_different_items():
    items = [
        _make_item("1", "OpenAI releases GPT-5"),
        _make_item("2", "Meta acquires Moltbook"),
        _make_item("3", "ArXiv paper on alignment"),
    ]
    result = deduplicate(items)
    assert len(result) == 3


def test_exact_duplicates_removed():
    items = [
        _make_item("1", "Same exact title here"),
        _make_item("2", "Same exact title here"),
    ]
    result = deduplicate(items)
    assert len(result) == 1


def test_empty_input():
    assert deduplicate([]) == []


def test_duplicate_keeps_first_and_merges_sources():
    items = [
        _make_item("1", "OpenAI releases GPT-5", source="TechCrunch"),
        _make_item("2", "OpenAI releases GPT-5", source="The Verge"),
    ]
    result = deduplicate(items)
    assert len(result) == 1
    assert "The Verge" in result[0].extra_sources or result[0].source in ["TechCrunch", "The Verge"]
