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
            # Determine section type based on heading content and context
            section_type = "info"  # default
            label_lower = label.lower() if label else ""
            
            if section_index == 0 or element.name == "h1":
                section_type = "hero"
            elif any(keyword in label_lower for keyword in ["footer", "contact", "copyright"]):
                section_type = "footer"
            elif any(keyword in label_lower for keyword in ["news", "blog", "article", "post"]):
                section_type = "news"
            elif any(keyword in label_lower for keyword in ["about", "who we are", "our story"]):
                section_type = "about"
            elif any(keyword in label_lower for keyword in ["service", "what we do", "offer"]):
                section_type = "services"
            elif any(keyword in label_lower for keyword in ["team", "our team", "people"]):
                section_type = "team"
            elif any(keyword in label_lower for keyword in ["testimonial", "review", "feedback"]):
                section_type = "testimonials"
            elif any(keyword in label_lower for keyword in ["faq", "question", "help"]):
                section_type = "faq"
            
            current_section = {
                "id": f"{section_type}-{section_index}",
                "type": section_type,
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
