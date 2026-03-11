import logging
import re
import unicodedata
from difflib import SequenceMatcher

from src.models import NewsItem

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.75


def _normalize_title(title: str) -> str:
    title = unicodedata.normalize("NFKC", title)
    title = title.lower()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def _is_similar(a: str, b: str) -> bool:
    return SequenceMatcher(None, a, b).ratio() > SIMILARITY_THRESHOLD


def deduplicate(items: list[NewsItem]) -> list[NewsItem]:
    if not items:
        return []

    kept: list[NewsItem] = []
    normalized_titles: list[str] = []

    for item in items:
        norm = _normalize_title(item.title)
        is_dup = False
        for i, existing_norm in enumerate(normalized_titles):
            if _is_similar(norm, existing_norm):
                kept[i].extra_sources.append(item.source)
                is_dup = True
                break
        if not is_dup:
            kept.append(item)
            normalized_titles.append(norm)

    logger.info(f"Dedup: {len(items)} -> {len(kept)} items")
    return kept
