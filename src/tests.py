import os
from dotenv import load_dotenv
from digest.config import Config
from digest.notion.rendering import NotionRenderer
load_dotenv()
cfg = Config("config.yaml").parse_config()

nc = NotionRenderer(
    token=cfg.notion_api_token,
    issues_ds=cfg.notion_issues_ds,
    news_ds=cfg.notion_news_ds,
    tech_ds=cfg.notion_tech_ds,
)

# fake data mimicking what the pipeline produces
fake_email = {
    "Id": "test-email-001",
    "Subject": "Test Newsletter: Issue 1",
    "Sender": "test@newsletter.com",
    "Date": "Tue, 20 Oct 2026 19:00:00 -0300",
    "Link": "https://example.com/email/1",
}
fake_summary = "A test newsletter covering RAG and agents."
fake_story = {
    "title": "A New RAG Technique",
    "focus": "Research",
    "innovation": "This story introduces a novel retrieval method combining dense and sparse search.",
    "technologies": ["RAG", "Vision-Language Models"],
}

print("=" * 50)

# 1. Create the issue
print("1. Creating issue...")
issue_id = nc.create_issue(fake_email, fake_summary)
print("   issue_id:", issue_id)

# 2. Resolve technologies (entity resolution)
print("2. Resolving technologies...")
tech_ids = [nc.find_or_create_tech(t) for t in fake_story["technologies"]]
print("   tech_ids:", tech_ids)

# 3. Create the news story, linked to issue + techs
print("3. Creating news story...")
news_id = nc.create_news(fake_story, issue_id, tech_ids)
print("   news_id:", news_id)

print("=" * 50)
print("✅ All created. Now check Notion:")
print("  - Issues DB: one 'Test Newsletter: Issue 1' row")
print("  - News DB: one 'A New RAG Technique' row, linked to that issue + 2 techs")
print("  - Technologies DB: 'RAG' and 'Vision-Language Models' pages")
print("  - Open the issue → it should show the story under it (relation works)")
print("  - Open a tech → it should show the story (relation works)")

# 4. Test idempotency of tech resolution — re-resolve, should reuse (no duplicates)
print("\n4. Re-resolving 'RAG' (should return SAME id, not create duplicate)...")
nc._tech_cache.clear()                              # force a real query, not cache
rag_again = nc.find_or_create_tech("RAG")
print("   RAG id (1st):", tech_ids[0])
print("   RAG id (2nd):", rag_again)
print("   SAME?", tech_ids[0] == rag_again, "← must be True (no duplicate)")