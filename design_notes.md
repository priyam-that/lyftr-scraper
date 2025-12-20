
# Design Notes

## Static vs JS Fallback
- Static scraping is used first by default. The scraper initially fetches the page using a lightweight HTTP request (requests) and parses it with BeautifulSoup. If the HTML already contains meaningful text, headings, links, and metadata, the page is treated as a static page. This approach is fast, resource-efficient, and works well for documentation sites, blogs, and content-heavy pages like Wikipedia or MDN, where most content is available directly in the server-rendered HTML.

- JavaScript rendering is triggered only when it is needed. If the static HTML appears empty or incomplete such as having very little visible text, placeholder messages, or script-heavy markup the heuristic determines that client side rendering is required. In this case, the scraper falls back to Playwright to load the page in a real browser, allowing JavaScript to execute. This enables scraping of modern SPA or marketing sites (X, Vercel, Next.js docs) where content loads dynamically via JavaScript after the initial HTML response.

## Wait Strategy for JS
- [ ] Network idle
- [x] Fixed sleep
- [ ] Wait for selectors

The scraper uses a fixed sleep-based wait strategy after JavaScript rendering. Once the page is loaded using Playwright (`wait_until="domcontentloaded"`), the scraper performs controlled delays (`page.wait_for_timeout`) during scrolling and after navigation. This ensures that client-side JavaScript has enough time to render visible content before HTML is captured.

Network-idle and selector-based waits were intentionally avoided to keep the system simple and predictable across different websites.

## Click & Scroll Strategy
- **Click flows implemented**: Best-effort link clicking on visible `a[href]` elements (skipping `#`, `mailto:`, `tel:`, `javascript:`). Up to 2 clicks are attempted, with basic popup handling and a fallback `goto()` when a click doesn't navigate.
- **Scroll / pagination approach**: Fixed number of mouse-wheel scrolls (default `scrolls=3`, each `wheel(0, 2000)`). No dedicated infinite-scroll loop and no systematic "next page" pagination crawl.
- **Stop conditions**: Stops after the configured scroll count and at most 2 clicks, or earlier when it has recorded at least 3 distinct page URLs and at least 1 click.

## Section Grouping & Labels
- **How you group DOM into sections**: Sections are split on `h1`/`h2`/`h3` headings while walking `soup.body.descendants`. Each heading starts a new section.
- **How you derive section `type` and `label`**: `label` is the heading text (or `Untitled Section`). `type` is derived from simple keyword matching on the heading (e.g., `hero` for the first section/`h1`, `footer`, `news`, `about`, `services`, `team`, `testimonials`, `faq`; otherwise `info`). If no headings exist, a single fallback "Main Content" section is produced.

## Noise Filtering & Truncation
- **Noise filtering**:
    - `<script>`, `<style>`, and `<noscript>` elements are removed
    - This reduces irrelevant content and improves text quality

- **HTML truncation**:
    - `rawHtml` is truncated to a fixed length for safety
    - The `truncated` flag is set to `true` when truncation occurs
    - Prevents oversized responses and memory issues

