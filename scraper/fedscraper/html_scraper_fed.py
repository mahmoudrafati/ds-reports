import sys
import requests
from bs4 import BeautifulSoup

def clean_url(url):
    try:
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)

        for script in soup(["script", "style"]):
            script.decompose()

        for div in soup.find_all("div", {'class': 'footer', 'class': 'header', 'class': 'attendees'}):
            div.decompose()
        cleaned_text = soup.get_text(strip=True)

        return cleaned_text
    except requests.exceptions.RequestException as e:
        print(f"An error while fetching url: {e}")


if __name__ == "__main__": 
    if len(sys.argv) != 2:
        print("Usage: python script.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    cleaned_content = clean_url(url)

    if cleaned_content:
        print(cleaned_content)
