from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NewsItem:
    id: str
    title: str
    description: str
    url: str
    source: str
    published: str
    category: Optional[str] = None
    summary_zh: Optional[str] = None
    title_zh: Optional[str] = None
    extra_sources: list[str] = field(default_factory=list)
