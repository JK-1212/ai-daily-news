import json
import logging
import os
import re
from typing import Optional

from google import genai

from src.config import CATEGORIES
from src.models import NewsItem

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
    return _client


def _call_gemini(prompt: str, retries: int = 1) -> str:
    client = _get_client()
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.warning(f"Gemini API call failed (attempt {attempt + 1}): {e}")
            if attempt == retries:
                raise
    return ""


def _parse_json(text: str) -> Optional[dict]:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def filter_and_classify(items: list) -> list:
    items_text = "\n".join(
        f"[{item.id}] {item.title} | {item.description[:100]}"
        for item in items
    )
    categories_str = ", ".join(CATEGORIES)

    prompt = f"""你是一个 AI 资讯编辑。以下是今日收集的 {len(items)} 条 AI 相关资讯。

请完成以下任务：
1. 过滤掉非 AI 核心内容（股票推荐、营销软文、重复报道等）
2. 跨语言去重（如果中英文报道是同一事件，只保留一条）
3. 按重要性和影响力排序，选出最有价值的 30 条（如果总数不足 30 条则全部保留）
4. 为每条分配一个类别：{categories_str}

请严格以 JSON 格式返回，不要添加任何其他文字：
{{"selected": [{{"id": "xxx", "category": "类别名"}}]}}

资讯列表：
{items_text}"""

    try:
        response = _call_gemini(prompt)
    except Exception:
        return []
    parsed = _parse_json(response)
    if parsed and "selected" in parsed:
        return parsed["selected"]
    # Retry with stricter prompt on JSON parse failure
    logger.warning("First filter call returned invalid JSON, retrying with stricter prompt")
    try:
        response = _call_gemini(prompt + "\n\n重要：请只返回纯 JSON，不要包含任何其他文字或 markdown 标记。")
    except Exception:
        return []
    parsed = _parse_json(response)
    if parsed and "selected" in parsed:
        return parsed["selected"]
    return []


def generate_summaries(items: list) -> list:
    items_text = "\n".join(
        f"[{item.id}] 标题: {item.title}\n描述: {item.description}\n来源: {item.source}\n链接: {item.url}"
        for item in items
    )

    prompt = f"""你是一个 AI 资讯编辑。请为以下 {len(items)} 条资讯生成中文摘要。

对每条资讯：
1. 生成一个简洁的中文标题（如果原标题是英文则翻译，中文则保留或优化）
2. 写 2-3 句中文摘要，概括核心内容

请严格以 JSON 格式返回，不要添加任何其他文字：
{{"items": [{{"id": "xxx", "title_zh": "中文标题", "summary_zh": "2-3句中文摘要"}}]}}

资讯列表：
{items_text}"""

    try:
        response = _call_gemini(prompt)
    except Exception:
        return []
    parsed = _parse_json(response)
    if parsed and "items" in parsed:
        return parsed["items"]
    logger.warning("Summary call returned invalid JSON, retrying")
    try:
        response = _call_gemini(prompt + "\n\n重要：请只返回纯 JSON，不要包含任何其他文字或 markdown 标记。")
    except Exception:
        return []
    parsed = _parse_json(response)
    if parsed and "items" in parsed:
        return parsed["items"]
    return []


def process_with_ai(items: list) -> list:
    if not items:
        return []

    # Pass 1: filter and classify
    selected = filter_and_classify(items)
    if not selected:
        logger.warning("AI filter returned empty, returning original items as fallback")
        return items

    # Build lookup
    items_by_id = {item.id: item for item in items}
    selected_items = []
    category_map = {}
    for s in selected:
        item = items_by_id.get(s["id"])
        if item:
            category_map[s["id"]] = s.get("category", "其他")
            selected_items.append(item)

    if not selected_items:
        logger.warning("No matching items after filter, returning original items")
        return items

    # Pass 2: generate summaries
    summaries = generate_summaries(selected_items)
    summary_map = {s["id"]: s for s in summaries}

    # Merge results
    for item in selected_items:
        item.category = category_map.get(item.id, "其他")
        if item.id in summary_map:
            s = summary_map[item.id]
            item.title_zh = s.get("title_zh", item.title)
            item.summary_zh = s.get("summary_zh")

    logger.info(f"AI processing done: {len(items)} -> {len(selected_items)} items")
    return selected_items
