"""Quality checks for content files (metadata, accessibility and link checks)."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED = ["slug", "title", "category", "author", "date", "status", "summary", "image_alt", "tags", "body"]
STATUSES = {"published", "draft"}
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\{\{([a-z0-9-]+)\}\}")


def check_article(article, filename, all_slugs):
    """Return a list of problem descriptions for one article."""
    problems = []
    for f in REQUIRED:
        if f not in article or article[f] in ("", [], None):
            problems.append(f"missing or empty field: {f}")
    slug = article.get("slug", "")
    if slug and not SLUG_RE.match(slug):
        problems.append("slug must be lowercase words joined by hyphens")
    if slug and slug != Path(filename).stem:
        problems.append("slug does not match file name")
    title = article.get("title", "")
    if len(title) > 60:
        problems.append(f"title is {len(title)} characters (max 60)")
    summary = article.get("summary", "")
    if summary and not 50 <= len(summary) <= 160:
        problems.append(f"summary is {len(summary)} characters (should be 50-160)")
    if article.get("status") and article["status"] not in STATUSES:
        problems.append("status must be 'published' or 'draft'")
    try:
        datetime.strptime(article.get("date", ""), "%Y-%m-%d")
    except ValueError:
        problems.append("date must use YYYY-MM-DD")
    alt = article.get("image_alt", "")
    if alt and alt.lower().startswith(("image of", "picture of")):
        problems.append("alt text should not start with 'image of' or 'picture of'")
    for text in article.get("body", []):
        for target in LINK_RE.findall(text):
            if target not in all_slugs:
                problems.append(f"broken internal link: {{{{{target}}}}}")
    return problems


def check_all(content_dir):
    files = sorted(Path(content_dir).glob("*.json"))
    articles = {f: json.loads(f.read_text(encoding="utf-8")) for f in files}
    slugs = {a.get("slug") for a in articles.values()}
    return {f.name: check_article(a, f.name, slugs) for f, a in articles.items()}


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "content"
    report = check_all(folder)
    bad = {k: v for k, v in report.items() if v}
    for name, probs in bad.items():
        print(f"FAIL {name}")
        for p in probs:
            print(f"   - {p}")
    print(f"\n{len(report) - len(bad)} of {len(report)} files passed")
    sys.exit(1 if bad else 0)
