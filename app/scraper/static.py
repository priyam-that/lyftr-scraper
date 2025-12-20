import requests
from bs4 import BeautifulSoup


def fetch_static_html(url: str) -> str:
    resp = requests.get(url, timeout=10) # 10 seconds timeout
    resp.raise_for_status()
    return resp.text # Return the HTML content


def extract_basic_meta(soup: BeautifulSoup) -> dict: # Extract basic metadata from static HTML
    title = ""
    description = ""
    language = ""

    if soup.title and soup.title.string: # Check if title tag exists
        title = soup.title.string.strip()

    desc_tag = soup.find("meta", attrs={"name": "description"}) # Find meta description tag
    if desc_tag and desc_tag.get("content"):
        description = desc_tag["content"].strip()

    html_tag = soup.find("html") # Find html tag to get language attribute
    if html_tag and html_tag.get("lang"):
        language = html_tag.get("lang")

    return {   # Return extracted metadata as a dictionary
        "title": title,
        "description": description,
        "language": language,
        "canonical": None,
    }
