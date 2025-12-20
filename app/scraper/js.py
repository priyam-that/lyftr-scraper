from playwright.sync_api import sync_playwright, TimeoutError #playwright is used for js rendering where the page is heavily dependent on js and html requests fail to get the content for web scraping as opposed to static.py which uses requests and bs4 for static html pages for web scraping.


def fetch_js_with_interactions( # Fetch JS-rendered HTML with user interactions
    url: str, # Target URL to fetch
    scrolls: int = 3, # Number of scrolls to perform
    timeout: int = 15000 # in milliseconds
) -> tuple[str, dict, list]:
    interactions = { # Track user interactions
        "clicks": [],
        "scrolls": 0,
        "pages": [],
    }
    
    errors = [] # List to log errors
    with sync_playwright() as p: # Launch Playwright browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try: # Navigate to the URL with timeout
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        except TimeoutError:
            pass

        # Scroll logic - simulate user scrolling
        for i in range(scrolls):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1500)
            interactions["scrolls"] += 1

        html = page.content() # Get the rendered HTML content
        browser.close() 

    return html, interactions # Return the HTML content and interactions log
