import hashlib
import logging
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser

from src.models import NewsItem

logger = logging.getLogger(__name__)

MAX_AGE_HOURS = 48


def _is_recent(entry: dict) -> bool:
    published = entry.get("published", "")
    if not published:
        return True
    try:
        dt = parsedate_to_datetime(published)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
        return dt >= cutoff
    except Exception:
        return True


def fetch_google_news(query_url: str) -> list[NewsItem]:
    try:
        feed = feedparser.parse(query_url)
        items = []
        for entry in feed.entries:
            if not _is_recent(entry):
                continue
            item_id = hashlib.md5(
                (entry.get("link", "") + entry.get("title", "")).encode()
            ).hexdigest()[:12]
            items.append(
                NewsItem(
                    id=item_id,
                    title=entry.get("title", "").strip(),
                    description=entry.get("summary", entry.get("description", "")).strip(),
                    url=entry.get("link", ""),
                    source="Google News",
                    published=entry.get("published", ""),
                )
            )
        logger.info(f"[Google News] fetched {len(items)} items from {query_url[:60]}...")
        return items
    except Exception as e:
        logger.warning(f"[Google News] failed for {query_url[:60]}: {e}")
        return []


def collect_all_google_news(query_urls: list[str]) -> tuple[list[NewsItem], dict]:
    all_items = []
    stats = {"total_queries": len(query_urls), "total_items": 0}
    for url in query_urls:
        items = fetch_google_news(url)
        all_items.extend(items)
    stats["total_items"] = len(all_items)
    logger.info(f"Google News collection done: {stats['total_queries']} queries, {stats['total_items']} items")
    return all_items, stats
