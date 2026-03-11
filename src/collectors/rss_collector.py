import hashlib
import logging
from typing import Optional

import feedparser

from src.models import NewsItem

logger = logging.getLogger(__name__)


def fetch_rss_feed(name: str, url: str) -> list[NewsItem]:
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            item_id = hashlib.md5(
                (entry.get("link", "") + entry.get("title", "")).encode()
            ).hexdigest()[:12]
            items.append(
                NewsItem(
                    id=item_id,
                    title=entry.get("title", "").strip(),
                    description=entry.get("summary", entry.get("description", "")).strip(),
                    url=entry.get("link", ""),
                    source=name,
                    published=entry.get("published", ""),
                )
            )
        logger.info(f"[{name}] fetched {len(items)} items")
        return items
    except Exception as e:
        logger.warning(f"[{name}] failed: {e}")
        return []


def collect_all_rss(feeds: list[dict]) -> tuple[list[NewsItem], dict]:
    all_items = []
    stats = {"success": 0, "failed": 0, "details": {}}
    for feed in feeds:
        items = fetch_rss_feed(feed["name"], feed["url"])
        if items:
            stats["success"] += 1
            stats["details"][feed["name"]] = len(items)
        else:
            stats["failed"] += 1
            stats["details"][feed["name"]] = 0
        all_items.extend(items)
    logger.info(f"RSS collection done: {stats['success']} ok, {stats['failed']} failed, {len(all_items)} total items")
    return all_items, stats
