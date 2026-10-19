"""
 Responsibility: fetch emails via IMAP + app password, return the SAME dict shape.
Logic:
  - class ImapClient(EmailClient)
  - __init__: takes email_address, app_password
  - fetch_emails(query, max_results):
      1. imaplib.IMAP4_SSL("imap.gmail.com"), login with app password
      2. select inbox
      3. for each sender in the query: IMAP search FROM that sender
         (IMAP search syntax differs from Gmail's — search per-sender, combine)
      4. take the most recent max_results message ids
      5. fetch each (RFC822 = raw email), parse with Python's email library
         (email.message_from_bytes) — this auto-decodes quoted-printable
      6. pull Subject/From/Date from headers, body via parsing.get_body
      7. build and return the standard dicts
      8. logout
Why: the new unattended-friendly path. No token, no expiry. Returns the
SAME shape as OAuthClient so downstream is unaffected.   
"""

from bs4 import BeautifulSoup

from imap_tools import MailBox, AND, OR
import os
from .base import EmailClient


class ImapClient(EmailClient):
    def __init__(self,email_address:str,app_password:str,domain:str="imap.gmail.com"):
        self.email_address = email_address
        self.app_password = app_password
        self.domain = domain

    def get_service(self):
           if os.path.exists(self.email_address) and os.path.getsize(self.email_address) > 0:
               with open(self.email_address, "r") as f:
                   self.email_address = f.read().strip()
           else:
               raise FileNotFoundError(f"Email address file not found or empty: {self.email_address}")
          
           if os.path.exists(self.app_password) and os.path.getsize(self.app_password) > 0:
               with open(self.app_password, "r") as f:
                   self.app_password = f.read().strip()
           else:
               raise FileNotFoundError(f"App password file not found or empty: {self.app_password}")
           
  
    def fetch_emails(self,query:str,max_results:int=10):
        with MailBox(self.domain).login(self.email_address, self.app_password,"inbox") as mb:
            all_msgs = []
            criteria = OR(from_=query)
            for msg in mb.fetch(criteria,limit = max_results,reverse = True):
                  
                  html_body = msg.html
                  soup = BeautifulSoup(html_body, "lxml")
                  for t in soup(["script","style"]): t.decompose()
                  html_text = soup.get_text(separator="\n")
                  msg_dict = {
                     "Id": msg.uid,
                     "Link": f"https://mail.google.com/mail/u/0/#inbox/{msg.uid}",
                     "Subject": msg.subject,
                     "Sender": msg.from_,
                     "Date": msg.date.strftime("%a, %d %b %Y %H:%M:%S %z"),
                     "Body": msg.text,
                     'Html': html_text,
                  }
                  all_msgs.append(msg_dict)
        return all_msgs
