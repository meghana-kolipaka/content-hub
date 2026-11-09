import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build
from check_content import check_article, check_all
from bulk_update import bulk_update


def good():
    return {"slug": "a-b", "title": "A good title", "category": "Web", "author": "X", "date": "2026-10-01",
            "status": "published", "summary": "A summary that is long enough to pass the fifty character minimum rule.",
            "image_alt": "Illustration of a page", "tags": ["x"], "body": ["Hello"]}


def test_valid_article_passes():
    assert check_article(good(), "a-b.json", {"a-b"}) == []


def test_missing_field_detected():
    a = good(); del a["image_alt"]
    assert any("image_alt" in p for p in check_article(a, "a-b.json", {"a-b"}))


def test_long_title_and_bad_date():
    a = good(); a["title"] = "x" * 61; a["date"] = "01/10/2026"
    probs = check_article(a, "a-b.json", {"a-b"})
    assert any("title" in p for p in probs) and any("date" in p for p in probs)


def test_broken_internal_link():
    a = good(); a["body"] = ["See {{nope}}"]
    assert any("broken internal link" in p for p in check_article(a, "a-b.json", {"a-b"}))


def test_slug_must_match_filename():
    assert any("file name" in p for p in check_article(good(), "other.json", {"a-b"}))


def test_alt_text_wording():
    a = good(); a["image_alt"] = "Image of a page"
    assert any("alt text" in p for p in check_article(a, "a-b.json", {"a-b"}))


def test_real_content_is_clean():
    report = check_all(ROOT / "content")
    assert all(not v for v in report.values()), report


def test_bulk_update_preview_and_apply(tmp_path):
    d = tmp_path / "c"; shutil.copytree(ROOT / "content", d)
    before = (d / "metadata-matters.json").read_text()
    preview = bulk_update(d, "author", "New Name", "author", "Meghana K.")
    assert len(preview) == 2 and (d / "metadata-matters.json").read_text() == before
    bulk_update(d, "author", "New Name", "author", "Meghana K.", apply=True)
    assert json.loads((d / "metadata-matters.json").read_text())["author"] == "New Name"


def test_build_skips_drafts_and_links_pages(tmp_path):
    n = build.build(ROOT / "content", tmp_path)
    assert n == 5 and not (tmp_path / "article" / "bulk-updates-safely.html").exists()
    page = (tmp_path / "article" / "what-is-an-api.html").read_text()
    assert 'href="../article/how-websites-load.html"' in page and 'alt="Illustration' in page
    assert '<meta name="description"' in page


def test_html_is_escaped(tmp_path):
    d = tmp_path / "c"; d.mkdir()
    a = good(); a["title"] = "Tom & <b>Jerry</b>"; a["slug"] = "a-b"
    (d / "a-b.json").write_text(json.dumps(a))
    build.build(d, tmp_path / "s")
    assert "<b>Jerry" not in (tmp_path / "s" / "article" / "a-b.html").read_text()
