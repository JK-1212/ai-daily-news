from __future__ import annotations

from datetime import datetime, timezone, timedelta

from src.config import CATEGORIES
from src.models import NewsItem

BEIJING_TZ = timezone(timedelta(hours=8))

CATEGORY_ICONS = {
    "模型发布": "🚀",
    "公司动向": "🏢",
    "研究论文": "📄",
    "工具产品": "🛠️",
    "行业政策": "📜",
    "其他": "📌",
}


def build_subject(count: int) -> str:
    now = datetime.now(BEIJING_TZ)
    date_str = now.strftime("%Y年%m月%d日")
    return f"AI 日报 - {date_str} ({count}条)"


def build_email_html(items: list[NewsItem]) -> str:
    now = datetime.now(BEIJING_TZ)
    date_str = now.strftime("%Y年%m月%d日")

    # Group by category
    grouped: dict[str, list[NewsItem]] = {cat: [] for cat in CATEGORIES}
    for item in items:
        cat = item.category if item.category in CATEGORIES else "其他"
        grouped[cat].append(item)

    sections = []
    for cat in CATEGORIES:
        cat_items = grouped[cat]
        if not cat_items:
            continue
        icon = CATEGORY_ICONS.get(cat, "📌")
        section_html = f'<h2 style="color:#1a1a1a;border-bottom:2px solid #e0e0e0;padding-bottom:8px;">{icon} {cat} ({len(cat_items)}条)</h2>'
        for i, item in enumerate(cat_items, 1):
            sources = item.source
            if item.extra_sources:
                sources += " / " + " / ".join(item.extra_sources)
            summary = item.summary_zh or item.description
            display_title = item.title_zh or item.title
            section_html += f'''
<div style="margin-bottom:16px;padding:12px;background:#f9f9f9;border-radius:8px;">
  <div style="font-size:16px;font-weight:bold;color:#1a1a1a;">{i}. {display_title}</div>
  <div style="font-size:14px;color:#444;margin-top:6px;line-height:1.6;">{summary}</div>
  <div style="font-size:12px;color:#888;margin-top:6px;">来源：{sources} | <a href="{item.url}" style="color:#1a73e8;">原文链接</a></div>
</div>'''
        sections.append(section_html)

    body = "\n".join(sections)

    html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:680px;margin:0 auto;padding:20px;background:#ffffff;">
  <h1 style="text-align:center;color:#1a1a1a;margin-bottom:4px;">AI 日报</h1>
  <p style="text-align:center;color:#888;font-size:14px;">{date_str}</p>
  <hr style="border:none;border-top:1px solid #e0e0e0;margin:20px 0;">
  {body}
  <hr style="border:none;border-top:1px solid #e0e0e0;margin:20px 0;">
  <p style="text-align:center;color:#888;font-size:12px;">共 {len(items)} 条 | 数据来源：12个RSS + Google News</p>
</body>
</html>'''
    return html
