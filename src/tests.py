import os
from dotenv import load_dotenv
from digest.config import Config
from digest.email_clients.imap_client import ImapClient
from digest.processing import Processing        # adjust to your actual module/class
from digest.agent import extract_stories
load_dotenv()
cfg = Config("config.yaml").parse_config()

email_address = cfg.email_address                    # from config.yaml
app_password = os.getenv("GMAIL_IMAP_SECRET")         # from .env (secret)

if not email_address or not app_password:
    raise RuntimeError("Missing email_address (config) or GMAIL_IMAP_SECRET (.env)")

client = ImapClient(email_address=email_address, app_password=app_password)
emails = client.fetch_emails("thebatch@deeplearning.ai", 1)
print("Fetched:", len(emails))
# ---- STAGE 1: fetch ----
emails = client.fetch_emails("thebatch@deeplearning.ai", 1)
print("=" * 50)
print("STAGE 1 — FETCH")
print("Fetched:", len(emails))
if not emails:
    print("❌ No emails fetched — IMAP query returns nothing. Check search syntax.")
    raise SystemExit

email = emails[0]
print("Keys:", list(email.keys()))
print("Subject:", email.get("Subject"))
print("Sender:", email.get("Sender"))
print("Date:", email.get("Date"), "| type:", type(email.get("Date")).__name__)
body = email.get("Body") or ""
print("Body length:", len(body))
print("Full content?", len(body) > 5000)

# ---- STAGE 2: clean ----
print("=" * 50)
print("STAGE 2 — CLEAN")
clean_text, _ = Processing.clean_email(email["Body"])   # adjust call to yours
print("Clean text length:", len(clean_text))
print("Contains 'GPT' or a model name?", "GPT" in clean_text or "Gemini" in clean_text)

# ---- STAGE 3: extract ----
print("=" * 50)
print("STAGE 3 — EXTRACT")
result = extract_stories(clean_text)
print("overall_summary present?", bool(result.get("overall_summary")))
print("Number of stories:", len(result.get("stories", [])))
for s in result.get("stories", []):
    print(f"  - {s.get('title','?')[:45]} | {s.get('focus','?')} | tech={len(s.get('technologies',[]))}")

# ---- STAGE 4: Notion (dry run — don't write, just show what WOULD be written) ----
print("=" * 50)
print("STAGE 4 — NOTION (dry run)")
if not result.get("stories"):
    print("❌ 0 stories → nothing would be written to Notion. Problem is upstream (stages 1-3).")
else:
    print(f"✅ Would write {len(result['stories'])} rows to Notion.")
    print("   (If the real run writes nothing but this shows stories, the issue is")
    print("    in add_story_row, the data_source_id, or state marking it already-done.)")