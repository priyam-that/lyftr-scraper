from fastapi import APIRouter, HTTPException
from datetime import datetime
from bs4 import BeautifulSoup

from app.schemas.response import (
    ScrapeResponse,
    ScrapeResult,
    Meta,
    Section,
    Interactions,
)

from app.scraper.static import fetch_static_html, extract_basic_meta
from app.scraper.parser import parse_sections
from app.scraper.heuristics import needs_js_rendering
from app.scraper.js import fetch_js_with_interactions

router = APIRouter()


@router.post("/scrape", response_model=ScrapeResponse)
def scrape(payload: dict):
    # 1. Read URL
    url = payload.get("url")

    # 2. Validate input
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=400, detail="url is required")

    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="url must start with http:// or https://")

    # Default interactions (static path)
    interactions = Interactions()

    try:
        # 3. Fetch static HTML
        html = fetch_static_html(url)

        # 4. Decide JS necessity
        js_required = needs_js_rendering(html)

        # 5. JS rendering + interactions (Phase 7)
        if js_required:
            try:
                html, interaction_data = fetch_js_with_interactions(url)
                interactions = Interactions(**interaction_data)
            except Exception:
                # Graceful fallback to static HTML
                pass

        # 6. Metadata parsing
        soup = BeautifulSoup(html, "html.parser")
        meta_data = extract_basic_meta(soup)

        # 7. Section parsing
        sections_data = parse_sections(html, url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 8. Build sections
    sections = [Section(**section) for section in sections_data]

    # 9. Build result
    result = ScrapeResult(
        url=url,
        scrapedAt=datetime.utcnow().isoformat() + "Z",
        meta=Meta(**meta_data),
        sections=sections,
        interactions=interactions,
        errors=[],
    )

    return ScrapeResponse(result=result)
