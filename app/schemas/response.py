from pydantic import BaseModel, Field     #importing BaseModel for creating data models schemas
from typing import List, Optional  #importing List and Optional for type hinting


class Meta(BaseModel): #metadata about the scraped page or whole page details
    title: str = ""
    description: str = ""
    language: str = ""
    canonical: Optional[str] = None


class SectionContent(BaseModel): #main content of a section
    headings: List[str] = Field(default_factory=list)
    text: str = ""
    links: List[dict] = Field(default_factory=list)
    images: List[dict] = Field(default_factory=list)
    lists: List[list] = Field(default_factory=list)
    tables: List[list] = Field(default_factory=list)


class Section(BaseModel): #a section of the scraped page
    id: str
    type: str
    label: str
    sourceUrl: str
    content: SectionContent
    rawHtml: str
    truncated: bool


class ClickItem(BaseModel): #single click interaction
    selector: str
    description: str = ""


class Interactions(BaseModel): #user interactions during scraping
    clicks: List[ClickItem] = Field(default_factory=list)
    scrolls: int = 0
    pages: List[str] = Field(default_factory=list)


class ErrorItem(BaseModel): #errors encountered during scraping
    message: str
    phase: str


class ScrapeResult(BaseModel): #overall result of the scraping process
    url: str
    scrapedAt: str
    meta: Meta
    sections: List[Section]
    interactions: Interactions
    errors: List[ErrorItem] = Field(default_factory=list)


class ScrapeResponse(BaseModel): #response model for the /scrape endpoint
    result: ScrapeResult
