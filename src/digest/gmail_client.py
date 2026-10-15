import base64
import json
import os.path
import quopri

from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class GmailClient:
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
        logic: call messages.list(q=query) → get list of message ids →
        for each, messages.get(id) → pull subject + sender + date from
        headers, body from payload. Return list of dicts:
        {id, subject, sender, date, body}.

        """
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

    # def get_body(self,payload:dict):
    #     """
    #     logic: recurse the payload parts; find the text/plain part;
    #     base64-decode it. (Handles multipart emails.)
    #     """
    #     if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
    #         return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        
    #     if "parts" in payload:
    #         for part in payload["parts"]:
    #             body = self.get_body(part)
    #             if body:
    #                 return body

    #     return ""


    def get_body(self, payload):
        html_body = None
        text_body = None
        def walk(part):
            nonlocal html_body, text_body
            data = part.get("body", {}).get("data")
            if not data:
                for sub in part.get("parts", []):
                    walk(sub)
                return
            decoded = base64.urlsafe_b64decode(data)
            text = quopri.decodestring(decoded).decode("utf-8", errors="ignore")
            if part.get("mimeType") == "text/plain":
                text_body = text
            elif part.get("mimeType") == "text/html":
                html_body = text
            for sub in part.get("parts", []):
                walk(sub)
        walk(payload)
        text = ""
        if html_body:
            
            text =  BeautifulSoup(html_body, "lxml").get_text(separator="\n")
        elif text_body:
            
            text = text_body
        return text_body, (html_body or "")

    def extract_links(self,html:str):
        soup = BeautifulSoup(html, "lxml")
        return {a.get_text().strip(): a.get("href") for a in soup.find_all("a", href=True)}



def get_service():
    client = GmailClient("credentials/GmailManagement.json", "token.json")
    return client.service

def fetch_emails(service, query, max_results=10):
    client = GmailClient("credentials/GmailManagement.json", "token.json")
    return client.fetch_emails(query, max_results)

def get_body(payload):
    client = GmailClient("credentials/GmailManagement.json", "token.json")
    return client.get_body(payload)

def show_parts(payload, depth=0):
    client = GmailClient("credentials/GmailManagement.json", "token.json")
    client.show_parts(payload, depth)

# def extract_links(html):
#     client = GmailClient("credentials/GmailManagement.json", "token.json")
#     return client.extract_links(html)