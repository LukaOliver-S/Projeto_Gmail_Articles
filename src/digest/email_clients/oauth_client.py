"""
Responsibility: fetch emails via the Gmail API, return the standard dict shape.
Logic:
  - class OAuthClient(EmailClient)
  - __init__: takes credentials_path, token_path; does the OAuth dance
    (your existing get_service logic)
  - fetch_emails(query, max_results):
      messages.list(q=query) → ids → messages.get(full) per id
      → parse each via parsing.get_body
      → build and return the standard {Id, Subject, Sender, Date, Body, Html} dicts
Why: your existing code, reorganized to FIT the interface. Same behavior,
now returns the contract shape so it's swappable.
"""

import base64
import json
import os
import quopri

from bs4 import BeautifulSoup

from .base import EmailClient
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class OAuthClient(EmailClient):
   
    def __init__(self,credentials_path:str,token_path:str):
            self.credentials_path = credentials_path
            self.token_path = token_path
            self.service,self.creds = self.get_service()
    
    def get_service(self):
          """
      logic: OAuth dance — load token.json if it exists; else run the
      browser flow from credentials.json; cache the token. Return the
      Gmail service object. (COPY from Google's quickstart.)
          """
          try:
              creds = None
              if os.path.exists(self.token_path) and os.path.getsize(self.token_path) > 0:
                  try:
                      creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                  except (ValueError, json.JSONDecodeError):
                      creds = None
              if not creds or not creds.valid:
                  if creds and creds.expired and creds.refresh_token:
                      creds.refresh(Request())
                  else:
                      flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                      creds = flow.run_local_server(port=0)
                  with open(self.token_path, "w") as token:
                      token.write(creds.to_json())
              service = build("gmail", "v1", credentials=creds)
              return service,creds
          except HttpError as error:
              print(f"An error occurred: {error}")
              return None,None
  
    def fetch_emails(self,query:str,max_results:int=10):
          """
          OAuth backend: list message ids via Gmail API, fetch each as RAW bytes,
          and delegate parsing to the shared parse_email(). Returns standard dicts.
          """
          query = "from:(" + " OR ".join(query) + ")"
          msgs = self.service.users().messages().list(userId="me",q=query,maxResults=max_results).execute()
          all_msgs = []
          for msg_info in msgs.get("messages",[]):
              msg_id = msg_info["id"]
              msg_data = self.service.users().messages().get(userId="me",id=msg_id).execute()
              headers = msg_data["payload"].get("headers", [])
              body_text, body_html = self.get_body(msg_data["payload"])
              msg = {
                  "Id": msg_id,
                  "Link": f"https://mail.google.com/mail/u/0/#inbox/{msg_id}",
                  "Subject": next((h["value"] for h in headers if h["name"] == "Subject"), ""),
                  "Sender": next((h["value"] for h in headers if h["name"] == "From"), ""),
                  "Date": next((h["value"] for h in headers if h["name"] == "Date"), ""),
                  "Body": body_text,
                  'Html': body_html,
              }
              all_msgs.append(msg)
          return all_msgs
      
    def show_parts(self,payload, depth=0):
          print("  "*depth, payload.get("mimeType"), "| size:", payload.get("body", {}).get("size"))
          for part in payload.get("parts", []):
              self.show_parts(part, depth+1)

    