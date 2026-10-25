from email.utils import parsedate_to_datetime
import os
from .client import NotionClient

class NewsNotion:
    def __init__(self, notion_client: NotionClient, news_ds: str = None):
        self.news_ds = news_ds
        self.notion_client = notion_client

    def create_news(self, story: dict, issue_id: str, tech_ids: list[str],date:str = None) -> str:
        """Return page id"""
        iso_date = None
        if date:
            try:
                iso_date = parsedate_to_datetime(date).isoformat()
            except (TypeError, ValueError, OverflowError):
                iso_date = None
        properties = {
            "Title": {"title": [{"text": {"content": story.get("title", "")[:2000]}}]},
            "Category": {"select": {"name": story.get("focus") or "Other"}},
            "Summary": {"rich_text": [{"text": {"content": story.get("innovation", "")[:2000]}}]},
            "Issues": {"relation": [{"id": issue_id}]},
            "Technologies": {"relation": [{"id": tid} for tid in tech_ids]},
            "Date": {"date": {"start": iso_date}} if iso_date else {"date": None},
        }
        return self.notion_client.create_page(self.news_ds, properties)