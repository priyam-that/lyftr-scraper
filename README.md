
# Lyftr Scraper

FastAPI service that scrapes a URL into a simple, structured JSON shape. It starts with static HTML (Requests + BeautifulSoup) and falls back to JS rendering (Playwright/Chromium) when the page looks JS-heavy.

## Quickstart

```bash
chmod +x run.sh
./run.sh
```

Then open:

- UI: `http://localhost:8000/`
- Health: `http://localhost:8000/healthz`

## API

### `POST /scrape`

```bash
curl -sS -X POST "http://localhost:8000/scrape" \
	-H "Content-Type: application/json" \
	-d '{"url":"https://example.com/"}' | python -m json.tool
```

Response shape:

- `result.meta`: basic metadata (title/description/language)
- `result.sections[]`: grouped sections with `type`, `label`, `content`, and `rawHtml`
- `result.interactions`: JS-only interaction log (`scrolls`, `clicks`, `pages`)

## What `run.sh` does

`run.sh`:

- Ensures `python3` exists
- Creates `.venv/` (via `python3 -m venv .venv`) if missing
- Activates the venv
- Runs `pip install --upgrade pip`
- Installs dependencies from `requirements.txt`
- Starts the server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Important: `run.sh` does **not** install Playwright browser binaries.

## Environment details

- Python: works with Python 3.x (tested in this repo with a local venv)
- JS rendering: uses Playwright (Chromium)

One-time setup for JS rendering:

```bash
.venv/bin/python -m playwright install chromium
```

If Chromium launches fail due to missing OS libs (common on Linux), try:

```bash
.venv/bin/python -m playwright install --with-deps chromium
```

## Primary URLs used for testing

- https://www.ycombinator.com/ — Y Combinator homepage; tests static content extraction
- https://vercel.com/ — JS-heavy (Next.js); validates Playwright rendering + scroll + link clicks
- https://x.com/ — social media site; tests dynamic content and authentication walls
- https://www.reddit.com/  — link-dense, dynamic content; validates fallback rendering and infinite scroll handling

## Known limitations / caveats

- Some sites block plain `requests` without a browser-like `User-Agent` (e.g., Wikipedia returned HTTP 403 in local testing).
- The JS fallback decision is heuristic-based (framework markers like React/Vue/Next + a crude “visible text” check); it can over/under-trigger.
- JS interactions are best-effort: fixed number of scrolls (default 3) and up to 2 link clicks. It does not implement dedicated “Load more” buttons, tab components, or systematic pagination crawling.
- Noise filtering is minimal (currently removes `script`, `style`, and `noscript` tags). Cookie banners/overlays aren’t specifically handled.
- `rawHtml` is truncated per section (currently 3000 chars) and fallback content truncates more aggressively.

