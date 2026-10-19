import base64
import json
import os.path
import quopri

from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from abc import ABC, abstractmethod

# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.errors import HttpError
# from googleapiclient.discovery import build

class EmailClient:
    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service, self.creds = self.get_service()

    @abstractmethod
    def get_service(self):
        pass

    @abstractmethod
    def fetch_emails(self, query: str, max_results: int = 10):
        pass

    @abstractmethod
    def get_body(self, raw_bytes):
        pass