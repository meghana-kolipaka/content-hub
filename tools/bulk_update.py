"""Bulk-update a metadata field across many content files, with a safe preview mode.

Examples:
  python tools/bulk_update.py --field author --value "Meghana Kolipaka" --where-field author --where-value "Meghana K."
  python tools/bulk_update.py --field category --value "Content" --where-field tags --where-value seo --apply
Without --apply the tool only previews the changes (dry run).
"""
import argparse
import json
from pathlib import Path


def matches(article, where_field, where_value):
    if where_field is None:
        return True
    current = article.get(where_field)
    return where_value in current if isinstance(current, list) else current == where_value


def bulk_update(content_dir, field, value, where_field=None, where_value=None, apply=False):
    """Set `field` to `value` on matching files. Returns a list of (filename, old, new)."""
    changes = []
    for path in sorted(Path(content_dir).glob("*.json")):
        article = json.loads(path.read_text(encoding="utf-8"))
        if not matches(article, where_field, where_value):
            continue
        old = article.get(field)
        if old == value:
            continue
        changes.append((path.name, old, value))
        if apply:
            article[field] = value
            path.write_text(json.dumps(article, indent=2, ensure_ascii=False), encoding="utf-8")
    return changes


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", default=str(Path(__file__).parent.parent / "content"))
    p.add_argument("--field", required=True)
    p.add_argument("--value", required=True)
    p.add_argument("--where-field")
    p.add_argument("--where-value")
    p.add_argument("--apply", action="store_true", help="write changes (default is preview only)")
    a = p.parse_args()
    result = bulk_update(a.dir, a.field, a.value, a.where_field, a.where_value, a.apply)
    for name, old, new in result:
        print(f"{name}: {old!r} -> {new!r}")
    mode = "Applied" if a.apply else "Preview only (use --apply to save)"
    print(f"\n{mode}: {len(result)} file(s)")
