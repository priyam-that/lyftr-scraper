def needs_js_rendering(html: str) -> bool:
    html_lower = html.lower()

    js_signals = [
        "react",
        "vue",
        "angular",
        "__next_data__",
        "id=\"root\"",
        "id=\"__next\""
    ]

    if any(signal in html_lower for signal in js_signals):
        return True

    # crude visible text check
    text_only = "".join(c for c in html_lower if c.isalnum())
    if len(text_only) < 200:
        return True

    return False
