# Content Hub

A small content-publishing project: articles are stored as structured JSON (metadata + body), rendered into a
consistent static website from HTML templates, and protected by automated quality checks and a safe bulk-update tool.
It mirrors a real content-delivery workflow: template-based page building, metadata management, bulk updates, QA and testing.

Built with Python (standard library only), HTML, CSS and JavaScript.

## Features
- **Template-based pages:** one base layout, an index template and an article template give every page the same look.
- **Metadata per article:** title, slug, category, author, date, status (published or draft), summary, tags and image alt text.
  The build adds a meta description and keywords to each page.
- **Internal links:** write `{{slug}}` in the body and the build turns it into a link using the target article's title.
- **Draft handling:** only articles with status `published` are built.
- **Accessible, responsive design:** skip link, breadcrumb, alt text, semantic HTML, light and dark mode, mobile layout.
- **Category filter:** a small JavaScript file filters the cards on the home page without reloading.
- **Quality checker (`tools/check_content.py`):** flags missing fields, long titles, wrong summary length, bad dates, bad slugs,
  weak alt text and broken internal links.
- **Bulk update tool (`tools/bulk_update.py`):** changes a metadata field across many files. It previews by default and writes only with `--apply`.
- **Tests:** 10 pytest tests covering the checker, the bulk tool and the build output (including HTML escaping).

## Usage
```bash
python build.py                      # generates the site into docs/
python tools/check_content.py        # run quality checks (exit code 1 if any file fails)
python tools/bulk_update.py --field author --value "Meghana Kolipaka" --where-field author --where-value "Meghana K."
python tools/bulk_update.py --field author --value "Meghana Kolipaka" --where-field author --where-value "Meghana K." --apply
pip install pytest && python -m pytest tests
```

## Add an article
Copy any file in `content/`, change the fields, make sure the file name matches `slug`, then run the checker and the build.

## Publish on GitHub Pages
Push the repository, then in Settings > Pages choose the `main` branch and the `/docs` folder.

## Structure
```
content/    article JSON files (content and metadata)
templates/  base, index and article HTML templates
static/     CSS and JavaScript
tools/      check_content.py, bulk_update.py
tests/      pytest tests
docs/       generated site (GitHub Pages)
build.py    site generator
```
