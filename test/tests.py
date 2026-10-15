from dotenv import load_dotenv

from digest.config import Config
load_dotenv()

cfg = Config("config.yaml").parse_config()
print("senders:", cfg.gmail_query_list)      # both newsletters
print("model:", cfg.gen_model)
print("notion token present?", bool(cfg.notion_api_token))   # True (from .env) — don't print the token