from email.utils import parsedate_to_datetime
import os
from .client import NotionClient

class TechnologiesNotion:
    def __init__(self, notion_client: NotionClient, tech_ds: str = None):
        self.notion_client = notion_client
        self.tech_ds = tech_ds
        self._cache = {}                             

    def get_or_create_technology(self, name: str, category: str | None = None) -> str:
        if name in self._cache:
            return self._cache[name]

        existing = self.notion_client.query_data_source(
            self.tech_ds, {"property": "Title", "title": {"equals": name}}
        )
        if existing:
            tid = existing[0]["id"]
            self._cache[name] = tid
            return tid

        props = {"Title": {"title": [{"text": {"content": name}}]}}
        if category:
            props["Category"] = {"select": {"name": category}}
        tid = self.notion_client.create_page(self.tech_ds, props)
        self._cache[name] = tid
        return tid