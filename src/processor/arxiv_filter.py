import re
import logging

from src.config import ARXIV_KEYWORDS
from src.models import NewsItem

logger = logging.getLogger(__name__)

_PATTERN = re.compile(
    "|".join(re.escape(kw) for kw in ARXIV_KEYWORDS),
    re.IGNORECASE,
)


def filter_arxiv_items(items: list[NewsItem]) -> list[NewsItem]:
    filtered = [item for item in items if _PATTERN.search(item.title)]
    logger.info(f"ArXiv filter: {len(items)} -> {len(filtered)} items")
    return filtered
