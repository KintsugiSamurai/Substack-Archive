import re
import feedparser
import html2text
from datetime import datetime
from pathlib import Path

FEED_FILE = Path("feed.xml")
README_FILE = Path("README.md")

ARCHIVE_START = "<!-- ARCHIVE START -->"
ARCHIVE_END = "<!-- ARCHIVE END -->"

def build_post(entry):
    pub_date = datetime(*entry.published_parsed[:6])
    date_str = pub_date.strftime("%Y-%m-%d")
    title = entry.title

    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.ignore_links = False

    content_html = entry.get("content", [{}])[0].get("value") or entry.get("summary", "")
    content_md = converter.handle(content_html).strip()

    return f"""# {title}

**Published:** {date_str}
**Original:** {entry.link}

---

{content_md}
"""

def main():
    if not FEED_FILE.exists():
        print(f"{FEED_FILE} not found")
        return

    feed_content = FEED_FILE.read_bytes()
    feed = feedparser.parse(feed_content)

    print(f"Number of entries: {len(feed.entries)}")

    posts = []
    for entry in feed.entries:
        posts.append(build_post(entry))

    posts.reverse()

    archive_content = "\n\n---\n\n".join(posts)

    if not README_FILE.exists():
        print("README.md not found")
        return

    readme = README_FILE.read_text(encoding="utf-8")
    block = f"{ARCHIVE_START}\n\n{archive_content}\n\n{ARCHIVE_END}"

    if ARCHIVE_START in readme and ARCHIVE_END in readme:
        pattern = re.compile(f"{re.escape(ARCHIVE_START)}.*?{re.escape(ARCHIVE_END)}", re.DOTALL)
        new_readme = pattern.sub(block, readme)
    else:
        new_readme = readme.rstrip() + f"\n\n{block}\n"

    if new_readme != readme:
        README_FILE.write_text(new_readme, encoding="utf-8")
        print("Updated README")
    else:
        print("README unchanged")

    FEED_FILE.unlink()
    print(f"Deleted {FEED_FILE}")

if __name__ == "__main__":
    main()
