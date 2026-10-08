import os
import re
import feedparser
import html2text
from datetime import datetime
from pathlib import Path

FEED_FILE = Path("feed.xml")
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
    if not FEED_FILE.exists():
        print(f"{FEED_FILE} not found")
        return

    feed_content = FEED_FILE.read_bytes()
    feed = feedparser.parse(feed_content)

    print(f"Number of entries: {len(feed.entries)}")

    for entry in feed.entries:
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

    FEED_FILE.unlink()
    print(f"Deleted {FEED_FILE}")

if __name__ == "__main__":
    main()
