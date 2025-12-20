from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parse_sections(html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    sections = [] # List to hold parsed sections
    current_section = None # Current section being processed
    section_index = 0 # Index for section IDs

    for element in soup.body.descendants:
        if element.name in ["h1", "h2", "h3"]:
            # Start a new section
            if current_section:
                sections.append(current_section)

            label = element.get_text(strip=True) # Extract heading text as label
            raw_html = str(element.parent)
            MAX_HTML = 3000
            current_section = {
                "id": f"section-{section_index}",
                "type": "section",
                "label": label if label else "Untitled Section",
                "sourceUrl": base_url,
                "content": {
                    "headings": [label],
                    "text": "",
                    "links": [],
                    "images": [],
                    "lists": [],
                    "tables": [],
                },
                "rawHtml": raw_html[:MAX_HTML],
                "truncated": len(raw_html) > MAX_HTML,
            }

            section_index += 1

        elif current_section:
            # Collect text
            if element.string:
                current_section["content"]["text"] += element.string.strip() + " "

            # Collect links
            if element.name == "a" and element.get("href"):
                current_section["content"]["links"].append({
                    "text": element.get_text(strip=True),
                    "href": urljoin(base_url, element["href"]),
                })

    if current_section:
        sections.append(current_section)

    # Fallback if no headings found
    if not sections: # No sections were created
        sections.append({
            "id": "section-0",
            "type": "section",
            "label": "Main Content",
            "sourceUrl": base_url,
            "content": {
                "headings": [],
                "text": soup.get_text(separator=" ", strip=True)[:2000],
                "links": [],
                "images": [],
                "lists": [],
                "tables": [],
            },
            "rawHtml": str(soup)[:2000],
            "truncated": True,
        })

    return sections # Return the list of parsed sections
