from .client import NotionClient
from .news import NewsNotion
from .technologies import TechnologiesNotion
from .issues import IssuesNotion

class NotionRenderer:
    def __init__(self, notion_client: NotionClient,issues_ds: str = None,news_ds: str = None, tech_ds : str = None):
        self.notion_client = notion_client
        self.issues_ds = issues_ds
        self.news_ds = news_ds
        self.tech_ds = tech_ds
        self.issues_notion = IssuesNotion(notion_client,self.issues_ds)
        self.news_notion = NewsNotion(notion_client,self.news_ds)
        self.tech_notion = TechnologiesNotion(notion_client,self.tech_ds)

    def create_issue(self, email: dict, summary: str) -> str:
        """Create an issue in Notion and return its page ID."""
        return self.issues_notion.create_issue(email, summary)

    def create_news(self, story: dict, issue_id: str, tech_ids: list[str],date:str = None) -> str:
        """Create a news story in Notion and return its page ID."""
        return self.news_notion.create_news(story, issue_id, tech_ids, date=date)

    def get_or_create_technology(self, name: str,category:str = None) -> str:
        """Get or create a technology in Notion and return its page ID."""
        return self.tech_notion.get_or_create_technology(name,category=category)

    def create_page(self, data_source_id: str, properties: dict, children: list = None) -> str:
        """Create a page in the specified data source and return its ID."""
        return self.notion_client.create_page(data_source_id, properties, children)

    def query_data_source(self, data_source_id: str, filter: dict) -> list:
        """Query a data source with the given filter and return a list of pages."""
        return self.notion_client.query_data_source(data_source_id, filter)
    