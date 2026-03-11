from src.processor.arxiv_filter import filter_arxiv_items
from src.models import NewsItem


def _make_item(title):
    return NewsItem(id="1", title=title, description="", url="https://arxiv.org", source="ArXiv", published="2026-03-11")


def test_keeps_relevant_papers():
    items = [
        _make_item("A New Approach to LLM Alignment"),
        _make_item("Transformer Architecture for Protein Folding"),
        _make_item("Chain-of-Thought Reasoning in GPT Models"),
    ]
    result = filter_arxiv_items(items)
    assert len(result) == 3


def test_filters_irrelevant_papers():
    items = [
        _make_item("Optimal Control of Robotic Arms in Zero Gravity"),
        _make_item("Statistical Analysis of Ocean Temperature Data"),
    ]
    result = filter_arxiv_items(items)
    assert len(result) == 0


def test_case_insensitive_matching():
    items = [_make_item("New llm benchmark results")]
    result = filter_arxiv_items(items)
    assert len(result) == 1


def test_empty_input():
    assert filter_arxiv_items([]) == []
