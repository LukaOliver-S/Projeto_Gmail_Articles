from email.utils import parsedate_to_datetime
import os
from notion_client import Client


class NotionClient:
    def __init__(self, token: str, data_source_id: str):
        self.token = token
        self.data_source_id = data_source_id
        self.client = self.get_client()

    def get_client(self):
        """Create a Notion API client."""
        try:
            return Client(auth=self.token)
        except Exception as e:
            raise RuntimeError(
                f"Error creating Notion client: {e}"
            ) from e

    def add_story_row(self, story: dict, email: dict):
        """Write one story as a row in the Notion database."""

        iso_date = None
        raw_date = email.get("Date", "")

        if raw_date:
            try:
                iso_date = parsedate_to_datetime(
                    raw_date
                ).isoformat()
            except (TypeError, ValueError, OverflowError):
                iso_date = None

        properties = {
            "Title": {
                "title": [{
                    "text": {
                        "content": story.get("title", "")[:2000]
                    }
                }]
            },
            "Sender": {
                "rich_text": [{
                    "text": {
                        "content": email.get("Sender", "")[:2000]
                    }
                }]
            },
            "Summary": {
                "rich_text": [{
                    "text": {
                        "content": story.get("innovation", "")[:2000]
                    }
                }]
            },
            "Category": {
                "select": {
                    "name": story.get("focus") or "Other"
                }
            },
            "Technologies": {
                "multi_select": [
                    {"name": t[:100]}
                    for t in story.get("technologies", [])
                    if isinstance(t, str) and t.strip()
                ]
            },
            "Date": {
                "date": {"start": iso_date}
            } if iso_date else {
                "date": None
            },
            "Id": {
                "rich_text": [{
                    "text": {
                        "content": email.get("Id", "")[:2000]
                    }
                }]
            },
            "Link": {
                "url": email.get("Link") or None
            },
        }

        return self.client.pages.create(
            parent={"data_source_id": self.data_source_id},
            properties=properties,
        )


def get_notion_client():
    token = os.environ.get("NOTION_TOKEN")
    data_source_id = os.environ.get("NOTION_DATA_SOURCE_ID")

    if not token:
        raise ValueError("NOTION_TOKEN environment variable is not set.")

    if not data_source_id:
        raise ValueError(
            "NOTION_DATA_SOURCE_ID environment variable is not set."
        )

    return NotionClient(
        token=token,
        data_source_id=data_source_id,
    )


def add_story_to_notion(story: dict, email: dict):
    notion_client = get_notion_client()
    return notion_client.add_story_row(story, email)
