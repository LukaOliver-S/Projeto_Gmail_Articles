from digest.state import State
from digest.gmail_client import fetch_emails, get_service
from digest.notion_client import NotionClient
from digest.processing import Processing
from digest.agent import extract_stories
from digest.config import Config   # adjust import path

import os
import json
from dotenv import load_dotenv
load_dotenv()

cfg = Config("config.yaml").parse_config()

query = "from:(" + " OR ".join(cfg.gmail_query_list) + ")"

state = State("data/processed.json")
notion = NotionClient(token=cfg.notion_api_token, data_source_id=cfg.notion_database_id)

for sender in cfg.gmail_query_list:
    print(f"Processing emails from: {sender}")
    emails = fetch_emails(get_service(), query, 10)
    for email in emails:
        if state.is_processed(email["Id"]):
            print(f"skip: {email['Subject'][:40]}")
            continue
        clean_text, _ = Processing.clean_email(email["Body"])
        result = extract_stories(clean_text)
        for story in result["stories"]:
            notion.add_story_row(story, email)
        state.mark_processed(email["Id"])
        print(f"done: {email['Subject'][:40]} ({len(result['stories'])} stories)")