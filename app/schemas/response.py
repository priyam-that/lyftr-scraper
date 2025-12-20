from pydantic import BaseModel     #importing BaseModel for creating data models schemas
from typing import List, Optional  #importing List and Optional for type hinting


class Meta(BaseModel): #metadata about the scraped page or whole page details
    title: str = ""
    description: str = ""
    language: str = ""
    canonical: Optional[str] = None


class SectionContent(BaseModel): #main content of a section
    headings: List[str] = []
    text: str = ""
    links: List[dict] = []
    images: List[dict] = []
    lists: List[list] = []
    tables: List[list] = []


class Section(BaseModel): #a section of the scraped page
    id: str
    type: str
    label: str
    sourceUrl: str
    content: SectionContent
    rawHtml: str
    truncated: bool


class Interactions(BaseModel): #user interactions during scraping
    clicks: List[str] = []
    scrolls: int = 0
    pages: List[str] = []


class ErrorItem(BaseModel): #errors encountered during scraping
    message: str
    phase: str


class ScrapeResult(BaseModel): #overall result of the scraping process
    url: str
    scrapedAt: str
    meta: Meta
    sections: List[Section]
    interactions: Interactions
    errors: List[ErrorItem]


class ScrapeResponse(BaseModel): #response model for the /scrape endpoint
    result: ScrapeResult
