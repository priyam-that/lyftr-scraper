# Lyftr Scraper — User Guide (Phase-Based)

This guide explains how to use the Lyftr Scraper API and what each phase of the implementation added.  
(Installation/setup intentionally omitted.)

---

## Phase 0 — Health Checking & Service Contract

### Health check
Use this to verify the server is up and responding.

```bash
curl -s http://localhost:8000/health
```


Expected: a small JSON confirming the service is healthy (exact shape may vary).

### API discovery (FastAPI)
FastAPI auto-generates:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Phase 1 — Static HTML Scraping (Default Path)

**Goal:** Scrape server rendered pages quickly and cheaply using http requests.

**What happens:**
1. Fetch HTML with a lightweight HTTP client.
2. Parse with BeautifulSoup.
3. Extract:
   - basic metadata (title/description/language when available)
   - structured sections (see Phase 4)

**Best for:** Wikipedia/MDN/blogs/docs where content is present in initial HTML.

---

## Phase 2 — JS Rendering Heuristic (Fallback Trigger)

**Goal:** Avoid browser rendering unless needed.

**Decision rule (high level):**
- Try static first.
- Escalate to JS rendering only if the HTML looks “empty/incomplete” (e.g., very little visible text, placeholder/app-shell markup, script-heavy structures like SPA roots).

---

## Phase 3 — Structured Response Schema (Stable JSON)

**Goal:** Return predictable output that downstream systems can rely on.

**Response includes (conceptually):**
- `meta` (page metadata)
- `sections[]` (grouped content)
- `interactions` (scroll/click/page history)
- `errors[]` (non-fatal issues, if any)

---

## Phase 4 — Section Parsing & Grouping (Readable Output)

**Goal:** Convert raw DOM into meaningful sections.

**How sections are formed:**
- Walk the DOM and split sections at headings (`h1`, `h2`, `h3`).
- Each heading starts a new section.
- If no headings exist, return one fallback section (e.g., “Main Content”).

**Per-section content typically contains:**
- `text` (visible textual content)
- `links` (anchors with href)
- `rawHtml` (truncated for safety)

---

## Phase 5 — Semantic Section Types (Human-Friendly Labels)

**Goal:** Make sections easier to interpret.

**How:**
- `label` comes from heading text (or a fallback like “Untitled Section”).
- `type` uses simple keyword heuristics (e.g., hero/footer/about/services/team/faq; otherwise info).
- IDs are derived from type and index (example: `hero-0`, `info-1`).

---

## Phase 6 — JS Rendering via Playwright (SPA Support)

**Goal:** Scrape content that only appears after JavaScript runs.

**What happens (when triggered):**
- Launch headless Chromium via Playwright.
- Navigate with `domcontentloaded`.
- Wait using a simple fixed-delay strategy (predictable across sites).
- Extract the post-rendered HTML for parsing.

**Good for:** Next.js docs, Vercel-like marketing sites, other SPA/app-shell pages.

---

## Phase 7 — Interaction Tracking (Scroll + Limited Clicks)

**Goal:** Capture content revealed by simple user behavior.

**Interactions performed (best-effort):**
- Scroll: fixed number of wheel scrolls (default is small and capped).
- Clicks: attempt a small number of visible `a[href]` clicks, skipping:
  - `#`, `mailto:`, `tel:`, `javascript:`
- Track visited page URLs and interaction counts.

**Safety limits:**
- capped scroll depth
- capped click count
- no form submission/auth flows

---

## Phase 8 — Noise Filtering & Truncation (Clean + Bounded)

**Noise removed before extracting text:**
- `<script>`, `<style>`, `<noscript>`

**Size control:**
- `rawHtml` is truncated to a fixed maximum length.
- A `truncated` flag indicates when truncation occurred.

---

# How to Use the API

## Scrape a URL
```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## What you get back
- metadata about the page
- logically grouped sections with text/links (+ truncated raw HTML)
- interaction history (scroll/click/pages)
- errors (if something partially failed)

---

# Known Limitations
- no login/auth handling
- no form filling/submission
- clicks are conservative by design
- no full infinite-scroll crawling loop
- some extractors (images/lists/tables) may be minimal or stubbed depending on site

---