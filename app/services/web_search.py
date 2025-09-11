# retriever/websearch.py
import requests
from bs4 import BeautifulSoup

def simple_web_search(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    snippets = [s.get_text() for s in soup.select("span")[:5]]
    return snippets
