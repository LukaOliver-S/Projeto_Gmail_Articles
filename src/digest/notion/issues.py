from email.utils import parsedate_to_datetime
import os
from .client import NotionClient

class IssuesNotion:
    def __init__(self, notion_client: NotionClient, issues_ds: str = None):
        self.notion_client = notion_client
        self.issues_ds = issues_ds


    
    def create_issue(self, email: dict, summary: str) -> str:
        """Return page id"""
        iso_date = None
        if email.get("Date"):
            try:
                iso_date = parsedate_to_datetime(email["Date"]).isoformat()
            except (TypeError, ValueError, OverflowError):
                iso_date = None

        properties = {
            "Title": {"title": [{"text": {"content": email.get("Subject", "")[:2000]}}]},
            "Source Email ID": {"rich_text": [{"text": {"content": email.get("Id", "")}}]},
            "Sender": {"rich_text": [{"text": {"content": email.get("Sender", "")[:2000]}}]},
            "Date": {"date": {"start": iso_date}} if iso_date else {"date": None},
            "Link": {"url": email.get("Link") or None},
            "Overall Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
        }
        return self.notion_client.create_page(self.issues_ds, properties)

    