# Responsibility: pick and build the right backend based on config.
# Logic:
#   - get_email_client(cfg) → EmailClient:
#       if cfg.email_backend == "imap":
#           return ImapClient(cfg.email_address, os.environ["GMAIL_APP_PASSWORD"])
#       else:
#           return OAuthClient(cfg.gmail_credentials_path, cfg.gmail_token_path)
#   - also export EmailClient, the two client classes
# Why: ONE place decides which backend. The orchestrator asks for "an email
# client" and gets whichever config specifies — doesn't branch on auth itself.

import os
from .base import EmailClient
from .imap_client import ImapClient
from .oauth_client import OAuthClient

class EmailClientFactory:
    @staticmethod
    def get_email_client(cfg) -> EmailClient:
        if cfg.email_client == "imap":
            return ImapClient(cfg.email_address, os.environ["GMAIL_IMAP_SECRET"])
        else:
            return OAuthClient(cfg.gmail_credentials_path, cfg.gmail_token_path)
    