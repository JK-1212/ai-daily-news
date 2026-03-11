import logging
import os
import sys

from src.config import RSS_FEEDS, GOOGLE_NEWS_QUERIES
from src.collectors.rss_collector import collect_all_rss
from src.collectors.google_news import collect_all_google_news
from src.processor.arxiv_filter import filter_arxiv_items
from src.processor.dedup import deduplicate
from src.processor.ai_summarizer import process_with_ai
from src.email.template import build_email_html, build_subject
from src.email.sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline() -> bool:
    logger.info("=== AI Daily News Pipeline Start ===")

    # Step 1: Collect from RSS
    rss_items, rss_stats = collect_all_rss(RSS_FEEDS)
    logger.info(f"RSS: {len(rss_items)} items ({rss_stats['success']} sources ok, {rss_stats['failed']} failed)")

    # Step 2: Collect from Google News
    gnews_items, gnews_stats = collect_all_google_news(GOOGLE_NEWS_QUERIES)
    logger.info(f"Google News: {gnews_stats['total_items']} items from {gnews_stats['total_queries']} queries")

    # Step 3: ArXiv pre-filter (split by source name)
    arxiv_items = [item for item in rss_items if item.source.startswith("ArXiv")]
    non_arxiv_items = [item for item in rss_items if not item.source.startswith("ArXiv")]

    filtered_arxiv = filter_arxiv_items(arxiv_items)
    logger.info(f"ArXiv filter: {len(arxiv_items)} -> {len(filtered_arxiv)}")

    # Step 4: Merge all items
    all_items = non_arxiv_items + filtered_arxiv + gnews_items
    logger.info(f"Total before dedup: {len(all_items)}")

    # Step 5: Deduplicate
    deduped = deduplicate(all_items)
    logger.info(f"After dedup: {len(deduped)}")

    # Step 6: AI processing (filter, classify, summarize)
    processed = process_with_ai(deduped)
    logger.info(f"After AI processing: {len(processed)}")

    if not processed:
        logger.warning("No items after processing, skipping email")
        return False

    # Step 7: Build and send email
    html = build_email_html(processed)
    subject = build_subject(len(processed))

    to_email = os.environ.get("EMAIL_TO", "")
    from_email = os.environ.get("EMAIL_FROM", "")

    if not to_email or not from_email:
        logger.error("EMAIL_TO or EMAIL_FROM not set")
        return False

    success = send_email(subject, html, to_email, from_email)

    # Pipeline summary
    logger.info("=== Pipeline Summary ===")
    logger.info(f"  RSS sources: {rss_stats['success']} ok, {rss_stats['failed']} failed")
    for name, count in rss_stats.get("details", {}).items():
        logger.info(f"    {name}: {count} items")
    logger.info(f"  Google News: {gnews_stats['total_items']} items from {gnews_stats['total_queries']} queries")
    logger.info(f"  ArXiv: {len(arxiv_items)} raw -> {len(filtered_arxiv)} filtered")
    logger.info(f"  Total: {len(all_items)} -> dedup {len(deduped)} -> final {len(processed)}")
    logger.info(f"  Email: {'SENT' if success else 'FAILED'}")
    logger.info(f"=== Pipeline {'SUCCESS' if success else 'FAILED'} ===")
    return success


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
