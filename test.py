import os
import re
import requests
import feedparser
import html2text
from datetime import datetime
from pathlib import Path

FEED_URL = os.environ.get("FEED_URL")
POSTS_DIR = Path("posts")
POSTS_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def sanitize_filename(name):
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[-\s]+', ' ', name)
    return name

def build_post(entry):
    pub_date = datetime(*entry.published_parsed[:6])
    date_str = pub_date.strftime("%Y-%m-%d")
    title = entry.title

    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.ignore_links = False

    content_html = entry.get("content", [{}])[0].get("value") or entry.get("summary", "")
    content_md = converter.handle(content_html).strip()

    header = f"""# {title}

**Published:** {date_str}
**Original:** {entry.link}

---

"""
    return date_str, title, header + content_md + "\n"

def main():
    if not FEED_URL:
        print("FEED_URL not set")
        return

    print(f"Fetching feed from: {FEED_URL}")
    response = requests.get(FEED_URL, headers=HEADERS, timeout=30)
    print(f"HTTP status: {response.status_code}")

    if response.status_code != 200:
        print(f"Failed to fetch feed: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return

    feed = feedparser.parse(response.content)
    print(f"Feed bozo: {feed.bozo}")
    if feed.bozo:
        print(f"Bozo exception: {feed.bozo_exception}")
    print(f"Number of entries: {len(feed.entries)}")

    if len(feed.entries) == 0:
        print("No entries found in feed")
        return

    for entry in feed.entries:
        print(f"Processing: {entry.get('title', 'NO TITLE')}")
        date_str, title, content = build_post(entry)
        safe_title = sanitize_filename(title)
        filename = f"{date_str} {safe_title}.md"
        filepath = POSTS_DIR / filename

        if filepath.exists():
            existing = filepath.read_text(encoding="utf-8")
            if existing == content:
                print(f"Unchanged: {filename}")
                continue
            print(f"Updated: {filename}")
        else:
            print(f"New: {filename}")

        filepath.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    main()
