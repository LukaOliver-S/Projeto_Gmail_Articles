import os
import json
import re

from bs4 import BeautifulSoup

class Processing:
    @staticmethod
    def clean_email(raw_email:str) -> tuple[str,dict]:
        """
        logic: extract the subject, sender, date, and body from the raw email string.
        Return a dict with these fields. Use regex to find headers and body.
        """

        links = re.findall(r"([^(\n\r]*?)\s*\((https?://[^)]+)\)", raw_email)
        link_map = {anchor.strip()[:50]: url for anchor, url in links if anchor.strip()}

        raw_email = re.sub(r"\s*\((https?://[^)]+)\)", "", raw_email)

        # Finding junk headers and removing them
        junk_headers = ["Subscribe","Submit a tip","Delivered-To", "Received", "X-Received", "ARC-Seal", "ARC-Message-Signature", "ARC-Authentication-Results", "Return-Path", "Received-SPF", "Authentication-Results", "DKIM-Signature", "Content-Type", "MIME-Version", "View in browser", "List-Unsubscribe", "List-Id", "List-Post", "List-Help", "List-Subscribe", "X-Mailer", "X-Originating-IP", "X-Google-Smtp-Source", "X-Google-Smtp-Source", "X-Google-DKIM-Signature","The Batch top banner","The Batch footer","A MESSAGE FROM DEEPLEARNING.AI","You are receiving this email because you are subscribed to The Batch newsletter from DeepLearning.AI","To unsubscribe from The Batch, click here","To manage your subscription preferences, click here"]
        raw_email = "\n".join([line for line in raw_email.splitlines() if not any(junk in line for junk in junk_headers)])

        # Let´s take out these whitespaces
        raw_email=re.sub(r"\n{3,}", "\n\n", raw_email)
        return (raw_email.strip(),link_map)
    @staticmethod
    def extract_links(html:str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        return {a.get_text().strip(): a.get("href") for a in soup.find_all("a", href=True)}