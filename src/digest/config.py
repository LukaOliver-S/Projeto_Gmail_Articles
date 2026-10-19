from dataclasses import dataclass, field, asdict
import json
import os
import yaml
import toml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Application:
    """Configuration for the application."""

    # # Google API configuration
    # google_api_client_id: str
    # google_api_client_secret: str
    # google_api_redirect_uri: str

    # Notion API configuration
    # notion_api_token: str
    notion_database_id: str

    # Additional configuration options
    gmail_query_list: list[str] 
    categories: list[str]

    #___GEMINI____
    gen_model: str


    #___GENERATOR BACKEND____

    generator: str = "gemini"
    fallback_chain: list[str] = field(default_factory=list)
    max_output_tokens: int = 1024

    # ____LOCAL____
    local_base_url: str = "http://localhost:11434/v1"
    local_model: str = "llama3.1"
    local_fallback: list[str] = field(default_factory=list)   # e.g. ["llama3.1", "qwen2.5"]


    #___SCHEDULER____
    scheduler_time: str = "01:00"  # Default time for the scheduler

    #____EMAIL CLIENT____
    email_client: str = "imap"  # Options: "imap" or "oauth
    email_address: str = ""
    @property
    def google_api_client_id(self) -> str:
        return os.environ.get("GOOGLE_CLIENT_ID", "")

    @property
    def google_api_client_secret(self) -> str:
        return os.environ.get("GOOGLE_CLIENT_SECRET", "")

    @property
    def notion_api_token(self) -> str:
        return os.environ.get("NOTION_TOKEN", "")
    @property
    def gmail_address(self) -> str:
        return os.environ.get("GMAIL_ADDRESS", "")
    @property
    def gmail_imap_secret(self) -> str:
        return os.environ.get("GMAIL_IMAP_SECRET", "")


class Config:
    def __init__(self, target_file: str):
        self.target_file = Path(target_file)
        
        ext = self.target_file.suffix.lower()
        self.is_yaml = ext in ['.yaml', '.yml']
        self.is_json = ext == '.json'
        self.is_toml = ext == '.toml'
        
        if self.is_yaml:
            self.config = self._load_yaml_config()
        elif self.is_json:
            self.config = self._load_json_config()
        elif self.is_toml:
            self.config = self._load_toml_config()
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
   
    def _load_yaml_config(self):
        with open(self.target_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}

    def _load_json_config(self):
        with open(self.target_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _load_toml_config(self):
        with open(self.target_file, 'r', encoding='utf-8') as file:
            return toml.load(file)

    def parse_config(self) -> Application:
        return Application(**self.config)

    def print_config(self):
        print(json.dumps(self.config, indent=4))

    def add_application(self, application: Application):
        self.config = asdict(application)
        self._save_config()

    def update_application(self, application: Application):
        self.config.update(asdict(application))
        self._save_config()

    def _save_config(self):
        if self.is_yaml:
            with open(self.target_file, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file)
        elif self.is_json:
            with open(self.target_file, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=4)
        elif self.is_toml:
            with open(self.target_file, 'w', encoding='utf-8') as file:
                toml.dump(self.config, file)