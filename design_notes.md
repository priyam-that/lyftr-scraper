# Design Notes

## Static vs JS Fallback

The scraper follows a **static-first approach**. For every request, it initially fetches the page using a lightweight HTTP client (`requests`) and parses the response using BeautifulSoup. If the returned HTML already contains meaningful visible content—such as headings, paragraphs, links, and metadata—the page is treated as static. This approach is fast, resource-efficient, and well-suited for documentation sites, blogs, and content-heavy pages like Wikipedia or MDN, where most content is available directly in server-rendered HTML.

JavaScript rendering is used **only when necessary**. If the static HTML appears empty or incomplete—for example, when it contains very little visible text, placeholder messages, or script-heavy markup—the heuristic determines that client-side rendering is required. In such cases, the scraper falls back to Playwright and loads the page in a real browser environment, allowing JavaScript to execute fully. This enables scraping of modern SPAs and marketing sites (e.g., X, Vercel, Next.js Docs) where content is dynamically injected after the initial HTML response.

---

## Wait Strategy for JS

- [ ] Network idle  
- [x] Fixed sleep  
- [ ] Wait for selectors  

The scraper uses a **fixed sleep-based wait strategy** during JavaScript rendering. Pages are loaded with Playwright using `wait_until="domcontentloaded"`, followed by controlled delays (`page.wait_for_timeout`) during scrolling and navigation. This provides sufficient time for client-side JavaScript to render visible content before capturing the HTML.

Network-idle and selector-based waits were intentionally avoided to keep the system simple, predictable, and resilient across a wide range of websites with varying loading behaviors.

---

## Click & Scroll Strategy

- **Click flows implemented**:  
  Best-effort clicking on visible `a[href]` elements, excluding non-navigational links such as `#`, `mailto:`, `tel:`, and `javascript:`. Up to two clicks are attempted per page, with basic popup handling and a fallback `goto()` when a click does not trigger navigation.

- **Scroll / pagination approach**:  
  A fixed number of mouse-wheel scrolls is performed (default: `scrolls = 3`, each using `wheel(0, 2000)`). There is no unbounded infinite-scroll loop and no deep recursive pagination crawl.

- **Stop conditions**:  
  Interaction stops after the configured scroll count and a maximum of two clicks, or earlier if at least three distinct page URLs and one successful click have already been recorded.

---

## Section Grouping & Labels

- **How DOM is grouped into sections**:  
  The DOM is traversed sequentially, and new sections are created whenever an `h1`, `h2`, or `h3` heading is encountered. Each heading starts a new logical section.

- **How section `type` and `label` are derived**:  
  The `label` is taken directly from the heading text (or defaults to `Untitled Section` if missing).  
  The `type` is derived using simple keyword-based heuristics on the heading text (e.g., `hero`, `footer`, `news`, `about`, `services`, `team`, `testimonials`, `faq`). If no semantic match is found, the section is classified as `info`.  
  If no headings exist on the page, a single fallback section labeled **“Main Content”** is produced.

---

## Noise Filtering & Truncation

- **Noise filtering**:
  - `<script>`, `<style>`, and `<noscript>` elements are removed before parsing
  - This reduces irrelevant markup and improves extracted text quality

- **HTML truncation**:
  - `rawHtml` is truncated to a fixed maximum length
  - The `truncated` flag is set to `true` when truncation occurs
  - This prevents oversized responses and avoids unnecessary memory usage
