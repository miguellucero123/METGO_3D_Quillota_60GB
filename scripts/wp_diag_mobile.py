"""Diagnose mobile render issues on metgo3d.com home."""
from __future__ import annotations

import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from wp_rest import request  # noqa: E402


def fetch(url: str, ua: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def main() -> None:
    mobile_ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

    for label, ua in (("mobile", mobile_ua), ("desktop", desktop_ua)):
        html = fetch("https://metgo3d.com/", ua)
        print("===", label, "len=", len(html))
        print("viewport", bool(re.search(r'name=["\']viewport["\']', html, re.I)))
        print("hero", "Evita" in html)
        print("wp-site-blocks", "wp-site-blocks" in html)
        print("post-content", "wp-block-post-content" in html or "entry-content" in html)
        body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.S | re.I)
        if body_m:
            text = re.sub(r"<[^>]+>", " ", body_m.group(1))
            text = re.sub(r"\s+", " ", text).strip()
            print("visible_text_len", len(text))
            print("sample:", text[:280])
        theme = re.search(r"/themes/([^/\"']+)", html)
        print("theme", theme.group(1) if theme else "?")

    page = request("GET", "/wp/v2/pages/211?context=edit")
    raw = (page.get("content") or {}).get("raw") or ""
    print("=== raw home chars", len(raw))
    # nested <p> bugs from old content?
    print("nested_p", raw.count("<p class=\"has-text") and "<p><p" in raw.replace(" ", ""))
    print("unclosed_group_open", raw.count("<!-- wp:group"), "close", raw.count("<!-- /wp:group -->"))
    print("columns_open", raw.count("<!-- wp:columns"), "close", raw.count("<!-- /wp:columns -->"))
    print("has_template_part_footer", "wp:template-part" in raw)
    # check if theme expects light background and our full-bleed fails
    print("alignfull count", raw.count("alignfull"))


if __name__ == "__main__":
    main()
