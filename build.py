"""Static-site builder.

Reads structured content from `content/`, applies Jinja2 templates from
`templates/`, writes rendered HTML to `public/`.

Usage:
    python build.py

Layout this script expects:

    content/
        home.yml            # one page worth of fields
        footer.yml          # site-wide footer data
        pages/
            about.md        # markdown body + frontmatter
            case-studies/
                emerald.md
                primark.md
        lists/
            logos.yml       # collections (each YAML is a list/dict)
            case-study-cards.yml
    templates/
        base.html.j2        # shared layout (head, nav, footer)
        home.html.j2
        about.html.j2
        case-study.html.j2  # rendered for every file in content/pages/case-studies/

The single `data` dict the templates render against ends up looking like:

    data = {
        'home':   {...},      # from content/home.yml
        'footer': {...},      # from content/footer.yml
        'pages':  {
            'about': {'frontmatter': {...}, 'body_html': '...'},
            'case_studies': {
                'emerald': {'frontmatter': {...}, 'body_html': '...'},
                ...
            },
        },
        'lists':  {
            'logos': [...],
            'case_study_cards': [...],
        },
    }

Plus, when rendering a per-item template (case-study.html.j2), an
`item` variable is bound to that single page's data.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "public"

# Templates that render once per item in a collection.
# Map: template name -> (collection key under data['pages'], output dir)
PER_ITEM_TEMPLATES = {
    "case-study.html.j2": ("case_studies", "."),  # writes to public/<slug>.html
}

# Top-level templates that render once (one HTML file each).
# Maps template name -> output filename.
SINGLE_TEMPLATES = {
    "home.html.j2": "index.html",
    "about.html.j2": "about.html",
}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_markdown(path: Path) -> dict:
    """Parse a markdown file with optional YAML front-matter (--- fenced)."""
    text = path.read_text(encoding="utf-8")
    frontmatter: dict = {}
    body = text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        frontmatter = yaml.safe_load(fm) or {}
    body_html = markdown.markdown(body.strip(), extensions=["extra", "smarty"])
    return {"frontmatter": frontmatter, "body_html": body_html, "body_md": body.strip()}


def collect_data() -> dict:
    data: dict = {"pages": {"case_studies": {}}, "lists": {}}

    # Top-level YAML files become top-level keys: home.yml -> data['home']
    for path in CONTENT.glob("*.yml"):
        data[path.stem] = load_yaml(path)

    # Standalone pages: content/pages/*.md -> data['pages'][stem]
    pages_dir = CONTENT / "pages"
    if pages_dir.exists():
        for path in pages_dir.glob("*.md"):
            data["pages"][path.stem] = load_markdown(path)

    # Case-study collection: content/pages/case-studies/*.md
    case_studies_dir = CONTENT / "pages" / "case-studies"
    if case_studies_dir.exists():
        for path in case_studies_dir.glob("*.md"):
            data["pages"]["case_studies"][path.stem] = load_markdown(path)

    # Lists: content/lists/*.yml -> data['lists'][stem]
    lists_dir = CONTENT / "lists"
    if lists_dir.exists():
        for path in lists_dir.glob("*.yml"):
            data["lists"][path.stem.replace("-", "_")] = load_yaml(path)

    return data


def render_site(data: dict) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Render inline markdown from YAML body fields (e.g. home.yml's
    # `ethos.body`). Markdown files under content/pages/ are converted
    # at load time; this filter handles the YAML case.
    env.filters["md_to_html"] = lambda text: markdown.markdown(
        (text or "").strip(), extensions=["extra", "smarty"]
    )

    # Single-output templates
    for tmpl_name, out_name in SINGLE_TEMPLATES.items():
        if not (TEMPLATES / tmpl_name).exists():
            continue
        rendered = env.get_template(tmpl_name).render(**data)
        (OUTPUT / out_name).write_text(rendered, encoding="utf-8")
        print(f"  wrote public/{out_name}")

    # Per-item templates (one HTML file per collection item)
    for tmpl_name, (collection_key, out_subdir) in PER_ITEM_TEMPLATES.items():
        if not (TEMPLATES / tmpl_name).exists():
            continue
        items = data.get("pages", {}).get(collection_key, {})
        out_dir = OUTPUT / out_subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        for slug, item in items.items():
            rendered = env.get_template(tmpl_name).render(item=item, slug=slug, **data)
            (out_dir / f"{slug}.html").write_text(rendered, encoding="utf-8")
            print(f"  wrote public/{out_subdir}/{slug}.html")


def main() -> None:
    print(f"Building site -> {OUTPUT}")
    data = collect_data()
    render_site(data)
    print("Done.")


if __name__ == "__main__":
    main()
