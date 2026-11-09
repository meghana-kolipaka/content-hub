"""Build the Content Hub static site from JSON content files and HTML templates."""
import html
import json
import re
from pathlib import Path
from string import Template

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
SITE = ROOT / "docs"
COLORS = {"Technology": "#2e2e38", "Web": "#0b5cad", "Content": "#1f7a5a", "AI": "#7a3fa0"}
LINK_RE = re.compile(r"\{\{([a-z0-9-]+)\}\}")


def load_articles(content_dir=CONTENT):
    """Read every JSON file and return a list of article dicts sorted by date (newest first)."""
    articles = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(content_dir).glob("*.json"))]
    return sorted(articles, key=lambda a: a["date"], reverse=True)


def tpl(name):
    return Template((TEMPLATES / f"{name}.html").read_text(encoding="utf-8"))


def render_body(paragraphs, titles, root):
    """Turn paragraphs into HTML and replace {{slug}} markers with internal links."""
    out = []
    for text in paragraphs:
        safe = html.escape(text, quote=False)
        def link(m):
            slug = m.group(1)
            label = html.escape(titles.get(slug, slug))
            return f'<a href="{root}/article/{slug}.html">{label}</a>'
        out.append("<p>" + LINK_RE.sub(link, safe) + "</p>")
    return "\n".join(out)


def make_svg(category, title):
    color = COLORS.get(category, "#444")
    t = html.escape(title)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 240"><rect width="720" height="240" fill="{color}"/>'
            f'<rect y="200" width="720" height="40" fill="#ffc800"/>'
            f'<text x="36" y="120" fill="#fff" font-family="Arial,sans-serif" font-size="26" font-weight="bold">{t}</text></svg>')


def build(content_dir=CONTENT, site_dir=SITE):
    site_dir = Path(site_dir)
    (site_dir / "article").mkdir(parents=True, exist_ok=True)
    (site_dir / "static" / "images").mkdir(parents=True, exist_ok=True)
    articles = [a for a in load_articles(content_dir) if a["status"] == "published"]
    titles = {a["slug"]: a["title"] for a in load_articles(content_dir)}
    base, art_t, idx_t = tpl("base"), tpl("article"), tpl("index")
    for name in ("style.css", "filter.js"):
        (site_dir / "static" / name).write_text((ROOT / "static" / name).read_text(encoding="utf-8"), encoding="utf-8")

    for a in articles:
        (site_dir / "static" / "images" / f"{a['slug']}.svg").write_text(make_svg(a["category"], a["title"]), encoding="utf-8")
        body = art_t.substitute(
            root="../", category=html.escape(a["category"]), title=html.escape(a["title"]),
            author=html.escape(a["author"]), date=a["date"], slug=a["slug"],
            image_alt=html.escape(a["image_alt"], quote=True), summary=html.escape(a["summary"]),
            body=render_body(a["body"], titles, ".."), tags=", ".join(html.escape(t) for t in a["tags"]))
        page = base.substitute(root="..", title=html.escape(a["title"]), description=html.escape(a["summary"], quote=True),
                               keywords=html.escape(", ".join(a["tags"]), quote=True), content=body, scripts="")
        (site_dir / "article" / f"{a['slug']}.html").write_text(page, encoding="utf-8")

    cats = sorted({a["category"] for a in articles})
    chips = "".join(f'<button class="chip" data-cat="{html.escape(c)}">{html.escape(c)}</button>' for c in cats)
    cards = "\n".join(
        f'<li data-cat="{html.escape(a["category"])}"><span class="badge">{html.escape(a["category"])}</span>'
        f'<h2><a href="article/{a["slug"]}.html">{html.escape(a["title"])}</a></h2>'
        f'<p>{html.escape(a["summary"])}</p><p class="meta">{a["date"]}</p></li>' for a in articles)
    index_body = idx_t.substitute(chips=chips, cards=cards)
    index = base.substitute(root=".", title="Articles", description="Short guides on technology, web and content practices.",
                            keywords="content, web, technology", content=index_body,
                            scripts='<script src="static/filter.js"></script>')
    (site_dir / "index.html").write_text(index, encoding="utf-8")
    return len(articles)


if __name__ == "__main__":
    print(f"Built {build()} published pages into {SITE}")
