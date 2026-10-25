from digest.state import State
from digest.notion.client import NotionClient
from digest.notion.rendering import NotionRenderer
from digest.processing import Processing
from digest.agent import extract_stories
from digest.config import Config   # adjust import path
from digest.email_clients import EmailClientFactory


import os
import json
from dotenv import load_dotenv
load_dotenv()

cfg = Config("config.yaml").parse_config()


state = State("data/processed.json")
notion = NotionClient(token=cfg.notion_api_token)
notion_render = NotionRenderer(notion_client=notion, issues_ds=cfg.notion_issues_ds, news_ds=cfg.notion_news_ds, tech_ds=cfg.notion_tech_ds)
email_client = EmailClientFactory.get_email_client(cfg)
for sender in cfg.gmail_query_list:
    print(f"Processing emails from: {sender}")
    emails = email_client.fetch_emails(sender, 1)
    for email in emails:
        if state.is_processed(email["Id"]):
            print(f"skip: {email['Subject'][:40]}")
            continue
        raw_date = email.get("Date", "")
        clean_text, _ = Processing.clean_email(email["Body"])
        result = extract_stories(clean_text)
        issues_id = notion_render.create_issue(email, result.get("overall_summary", ""))
        for story in result["stories"]:
           tech_ids = []
           for item in story.get("technologies", []):
                if isinstance(item, dict):
                    name, cat = item.get("name"), item.get("category")
                else:
                    name, cat = item, None
                if name:
                    tech_ids.append(notion_render.get_or_create_technology(name, category=cat))          
           notion_render.create_news(story, issues_id, tech_ids, date=raw_date)
        state.mark_processed(email["Id"])
        print(f"done: {email['Subject'][:40]} ({len(result['stories'])} stories)")