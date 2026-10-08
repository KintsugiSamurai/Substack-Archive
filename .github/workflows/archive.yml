import os
import re
import feedparser
import html2text
from datetime import datetime
from pathlib import Path

FEED_URL = os.environ.get("FEED_URL")
POSTS_DIR = Path("posts")
POSTS_DIR.mkdir(exist_ok=True)

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

    feed = feedparser.parse(FEED_URL)

    for entry in feed.entries:
        date_str, title, content = build_post(entry)
        safe_title = sanitize_filename(title)
        filename = f"{date_str} {safe_title}.md"
        filepath = POSTS_DIR / filename

        if filepath.exists():
            existing = filepath.read_text(encoding="utf-8")
            if existing == content:
                continue
            print(f"Updated: {filename}")
        else:
            print(f"New: {filename}")

        filepath.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    main()
