import requests
from bs4 import BeautifulSoup

class WebFetcher:
    @staticmethod
    def fetch_web_content(url: str) -> str:
        """
        Fetches the content of a web page and returns the text content.
        """
        try:
            response = requests.get(url,allow_redirects=True,headers={"User-Agent":"Mozilla/5.0"}, timeout=30)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.content, 'lxml')
            for t in soup(['script', 'style']):
                t.decompose()  # Remove script and style elements
            content = soup.get_text(separator="\n")
            return content
        except requests.RequestException as e:
            print(f"An error occurred while fetching the web page: {e}")
            return ""