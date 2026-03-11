import json
from unittest.mock import patch, MagicMock
from src.processor.ai_summarizer import filter_and_classify, generate_summaries, process_with_ai
from src.models import NewsItem


def _make_items(n):
    return [
        NewsItem(
            id=str(i),
            title=f"News item {i}",
            description=f"Description for item {i}",
            url=f"https://example.com/{i}",
            source="Test",
            published="2026-03-11",
        )
        for i in range(n)
    ]


def test_filter_and_classify_returns_selected_ids():
    items = _make_items(5)
    mock_response = json.dumps({
        "selected": [
            {"id": "0", "category": "模型发布"},
            {"id": "2", "category": "公司动向"},
        ]
    })
    with patch("src.processor.ai_summarizer._call_gemini", return_value=mock_response):
        selected = filter_and_classify(items)
    assert len(selected) == 2
    assert selected[0]["id"] == "0"
    assert selected[0]["category"] == "模型发布"


def test_generate_summaries_returns_structured_data():
    items = _make_items(2)
    mock_response = json.dumps({
        "items": [
            {"id": "0", "title_zh": "新闻0中文标题", "summary_zh": "这是新闻0的中文摘要。"},
            {"id": "1", "title_zh": "新闻1中文标题", "summary_zh": "这是新闻1的中文摘要。"},
        ]
    })
    with patch("src.processor.ai_summarizer._call_gemini", return_value=mock_response):
        summaries = generate_summaries(items)
    assert len(summaries) == 2
    assert summaries[0]["title_zh"] == "新闻0中文标题"


def test_process_with_ai_end_to_end():
    items = _make_items(5)
    filter_response = json.dumps({
        "selected": [{"id": "0", "category": "模型发布"}, {"id": "1", "category": "工具产品"}]
    })
    summary_response = json.dumps({
        "items": [
            {"id": "0", "title_zh": "标题0", "summary_zh": "摘要0"},
            {"id": "1", "title_zh": "标题1", "summary_zh": "摘要1"},
        ]
    })
    with patch("src.processor.ai_summarizer._call_gemini", side_effect=[filter_response, summary_response]):
        result = process_with_ai(items)
    assert len(result) == 2
    assert result[0].category == "模型发布"
    assert result[0].summary_zh == "摘要0"


def test_process_with_ai_handles_malformed_json():
    items = _make_items(3)
    with patch("src.processor.ai_summarizer._call_gemini", return_value="not json at all"):
        result = process_with_ai(items)
    # Fallback: returns original items without AI processing
    assert len(result) == 3
    assert result[0].category is None


def test_parse_json_from_code_fence():
    from src.processor.ai_summarizer import _parse_json
    text = '```json\n{"selected": [{"id": "1", "category": "模型发布"}]}\n```'
    result = _parse_json(text)
    assert result is not None
    assert result["selected"][0]["id"] == "1"


def test_parse_json_from_surrounding_text():
    from src.processor.ai_summarizer import _parse_json
    text = 'Here is the result:\n{"selected": [{"id": "2", "category": "其他"}]}\nDone.'
    result = _parse_json(text)
    assert result is not None
    assert result["selected"][0]["id"] == "2"


def test_parse_json_returns_none_for_garbage():
    from src.processor.ai_summarizer import _parse_json
    assert _parse_json("completely invalid") is None
    assert _parse_json("") is None
