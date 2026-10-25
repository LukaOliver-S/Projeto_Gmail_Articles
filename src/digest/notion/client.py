"""Responsibility: own the Notion connection and low-level page operations. 
Everything database-specific uses this; it knows nothing about Issues/News/Tech 
semantics — just "create a page here," "query this data source."

Holds (state):
  - the Notion Client (authenticated with token)
  - the three data source IDs (issues_ds, news_ds, tech_ds)
  - a within-run tech cache {name: page_id} (avoid re-searching same tech)

Generic methods:
  - create_page(data_source_id, properties, children=None) → page_id
      wraps client.pages.create; returns the new page's id
  - query_data_source(data_source_id, filter) → list of pages
      wraps the query API; used for dedup/entity lookups
  - (these are the primitives the database modules build on)

Why: one place owns "how to talk to Notion." If the API changes, you fix it here."""

from email.utils import parsedate_to_datetime
import os
from notion_client import Client     

class NotionClient:
    def __init__(self, token: str):
        self.token = token
        self.client = self.get_client()

    def get_client(self):
        """Create a Notion API client."""
        try:
            return Client(auth=self.token)
        except Exception as e:
            raise RuntimeError(
                f"Error creating Notion client: {e}"
            ) from e
            


    def create_page(self, data_source_id: str, properties: dict, children: list = None) -> str:
        """Create a page in the specified data source and return its ID."""
        try:
            page = self.client.pages.create(
                parent={"data_source_id": data_source_id},
                properties=properties,
                children=children or []
            )
            return page["id"]
        except Exception as e:
            raise RuntimeError(
                f"Error creating page in Notion: {e}"
            ) from e

    
    def query_data_source(self, data_source_id: str, filter: dict) -> list:
        """Query a data source with the given filter and return a list of pages."""
        try:
            results = self.client.data_sources.query(
                data_source_id=data_source_id,
                filter=filter
            )
            return results.get("results", [])
        except Exception as e:
            raise RuntimeError(
                f"Error querying Notion data source: {e}"
            ) from e
        
    
    # def add_story_row(self, story: dict, email: dict):
    #     """Write one story as a row in the Notion database."""

    #     iso_date = None
    #     raw_date = email.get("Date", "")

    #     if raw_date:
    #         try:
    #             iso_date = parsedate_to_datetime(
    #                 raw_date
    #             ).isoformat()
    #         except (TypeError, ValueError, OverflowError):
    #             iso_date = None

    #     properties = {
    #         "Title": {
    #             "title": [{
    #                 "text": {
    #                     "content": story.get("title", "")[:2000]
    #                 }
    #             }]
    #         },
    #         "Sender": {
    #             "rich_text": [{
    #                 "text": {
    #                     "content": email.get("Sender", "")[:2000]
    #                 }
    #             }]
    #         },
    #         "Summary": {
    #             "rich_text": [{
    #                 "text": {
    #                     "content": story.get("innovation", "")[:2000]
    #                 }
    #             }]
    #         },
    #         "Category": {
    #             "select": {
    #                 "name": story.get("focus") or "Other"
    #             }
    #         },
    #         "Technologies": {
    #             "multi_select": [
    #                 {"name": t[:100]}
    #                 for t in story.get("technologies", [])
    #                 if isinstance(t, str) and t.strip()
    #             ]
    #         },
    #         "Date": {
    #             "date": {"start": iso_date}
    #         } if iso_date else {
    #             "date": None
    #         },
    #         "Id": {
    #             "rich_text": [{
    #                 "text": {
    #                     "content": email.get("Id", "")[:2000]
    #                 }
    #             }]
    #         },
    #         "Link": {
    #             "url": email.get("Link") or None
    #         },
    #     }

    #     return self.client.pages.create(
    #         parent={"data_source_id": self.data_source_id},
    #         properties=properties,
    #     )




# def add_story_to_notion(story: dict, email: dict):
#     notion_client = get_notion_client()
#     return notion_client.add_story_row(story, email)



