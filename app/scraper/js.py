from __future__ import annotations

from playwright.sync_api import sync_playwright, TimeoutError
from urllib.parse import urljoin


def _should_skip_href(href: str) -> bool:
    href_lower = href.strip().lower()
    return (
        not href_lower
        or href_lower.startswith("#")
        or href_lower.startswith("javascript:")
        or href_lower.startswith("mailto:")
        or href_lower.startswith("tel:")
    )


def _record_page(pages: list[str], url: str | None) -> None:
    if not url:
        return
    if url.startswith("about:"):
        return
    if url not in pages:
        pages.append(url)


def fetch_js_with_interactions( # Fetch JS-rendered HTML with user interactions
    url: str, # Target URL to fetch
    scrolls: int = 3, # Number of scrolls to perform
    timeout: int = 15000 # in milliseconds
) -> tuple[str, dict]:
    interactions = { # Track user interactions
        "clicks": [],
        "scrolls": 0,
        "pages": [],
    }

    with sync_playwright() as p: # Launch Playwright browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try: # Navigate to the URL with timeout
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        except TimeoutError:
            pass

        _record_page(interactions["pages"], page.url)

        # Scroll logic - simulate user scrolling
        for i in range(scrolls):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1500)
            interactions["scrolls"] += 1

        # Keep HTML from the original (scrolled) page for scraping.
        html = page.content()

        # Try to perform up to 2 meaningful clicks to collect:
        # - at least 1 click (selector+description)
        # - at least 3 visited page URLs (depth >= 3) when possible
        visited = set(interactions["pages"])
        max_clicks = 2
        for _ in range(max_clicks):
            if len(interactions["pages"]) >= 3 and len(interactions["clicks"]) >= 1:
                break

            candidates = page.query_selector_all("a[href]")
            target = None
            target_selector = None
            target_description = None
            target_abs_url = None

            for handle in candidates:
                try:
                    if not handle.is_visible():
                        continue
                    href = handle.get_attribute("href") or ""
                    if _should_skip_href(href):
                        continue
                    abs_url = urljoin(page.url, href)
                    if abs_url in visited:
                        continue

                    link_text = (handle.inner_text() or "").strip()
                    if not link_text:
                        link_text = (handle.get_attribute("aria-label") or "").strip()
                    if not link_text:
                        link_text = href.strip()

                    # Best-effort selector for logging (not guaranteed unique).
                    safe_href = href.replace('"', "\\\"")
                    target = handle
                    target_selector = f'a[href="{safe_href}"]'
                    target_description = f'Click link: {link_text[:80]}'
                    target_abs_url = abs_url
                    visited.add(abs_url)
                    break
                except Exception:
                    continue

            if not target:
                break

            url_before = page.url

            try:
                try:
                    target.scroll_into_view_if_needed(timeout=2000)
                except Exception:
                    pass

                # Some links open popups; handle both popup and same-tab navigation.
                popup = None
                try:
                    with page.expect_popup(timeout=1200) as popup_info:
                        target.click(timeout=4000)
                    popup = popup_info.value
                except TimeoutError:
                    # No popup: click already performed.
                    pass

                if popup is not None:
                    try:
                        popup.wait_for_load_state("domcontentloaded", timeout=timeout)
                    except TimeoutError:
                        pass
                    url_after = popup.url
                else:
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=timeout)
                    except TimeoutError:
                        pass
                    page.wait_for_timeout(800)
                    url_after = page.url

                    # If the click didn't navigate (common with JS handlers),
                    # try visiting the link target directly to capture depth.
                    if target_abs_url and url_after == url_before:
                        try:
                            page.goto(target_abs_url, timeout=timeout, wait_until="domcontentloaded")
                            page.wait_for_timeout(600)
                            url_after = page.url
                        except TimeoutError:
                            pass
                        except Exception:
                            pass

                _record_page(interactions["pages"], url_after)

                interactions["clicks"].append(
                    {
                        "selector": target_selector or "",
                        "description": target_description or "",
                    }
                )
            except Exception:
                # If clicking fails, keep whatever we've already captured.
                continue
        browser.close() 

    return html, interactions # Return the HTML content and interactions log
