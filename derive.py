#!/usr/bin/env python3
"""
Derive the classmate VCOM calendars from Anna's freshly-built page.

Each classmate calendar is Anna's `repo/build/index.html` with four things
changed:

  1. the page name (title + <h1>) -> "<Name>'s Calendar", or a verbatim label
  2. the localStorage key            -> per-person, so nothing collides
  3. the STUDY 1.0 to-do engine      -> disabled; the to-do column starts empty
                                        and carries only what the viewer adds
  4. the footer / theme-note copy    -> de-personalised

The schedule itself is whatever is baked into Anna's build at the moment this
runs. Output is a full standalone HTML file per calendar under docs/, which
GitHub Pages serves (main branch, /docs folder):

    docs/index.html        -> <site>/           (generic)
    docs/calendar/index.html -> <site>/calendar/ (generic)
    docs/chloe/index.html  -> <site>/chloe/

<site> is https://finnhoops.github.io/vcom-class-calendars

Update flow when a new PDF comes out:
  1. update Anna's calendar the normal way (regenerates repo/build/index.html)
  2. python3 derive.py --all
  3. git commit + push   ->  Pages redeploys every calendar, links unchanged

Usage:
  python3 derive.py --name "Chloe" --slug chloe
  python3 derive.py --label "Calendar" --slug calendar
  python3 derive.py --all
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "ANNA VCOM calendar" / "repo" / "build" / "index.html"
# The build id lives next to Anna's build; each derived calendar gets a copy in
# its own folder so the page's freshness check can fetch <folder>/version.json
# and reload itself when a newer build is published.
VERSION_SRC = SOURCE.parent / "version.json"
REGISTRY = HERE / "registry.json"
# GitHub Pages serves this repo from main:/docs. Each calendar is its own
# folder so the URL is clean: docs/chloe/index.html -> <site>/chloe/
DOCS = HERE / "docs"

APOS = "’"  # the curly apostrophe the page's typography uses


def must_replace(text, old, new, label):
    """Replace exactly once; abort loudly if the anchor moved or vanished."""
    n = text.count(old)
    if n != 1:
        sys.exit(f"derive.py: expected exactly one '{label}' anchor, found {n}.\n"
                 f"  Anna's build/index.html has changed shape -- update derive.py.")
    return text.replace(old, new)


def derive(slug: str, name: str = None, label: str = None) -> str:
    if not SOURCE.exists():
        sys.exit(f"derive.py: can't find Anna's build at {SOURCE}")
    html = SOURCE.read_text(encoding="utf-8")
    page_name = label if label else f"{name}{APOS}s Calendar"

    # 1. page name --------------------------------------------------------
    html = must_replace(
        html,
        "<title>Anna's Calendar — Block 1</title>",
        f"<title>{page_name}</title>",
        "title",
    )
    html = must_replace(
        html,
        f"<h1>Anna{APOS}s Calendar</h1>",
        f"<h1>{page_name}</h1>",
        "h1",
    )
    # keep the <meta description> honest (it names Anna)
    html = must_replace(
        html,
        '<meta name="description" content="Block 1 schedule and to-do list, '
        '2026-09-02 to 2027-01-15.">',
        f'<meta name="description" content="{page_name} — VCOM Block 1 '
        f'schedule and a personal to-do list.">',
        "description meta",
    )

    # 2. per-person storage key -----------------------------------------
    html = must_replace(
        html,
        'const KEY = "anna-vcom-cal-v1";',
        f'const KEY = "vcom-cal-{slug}-v1";',
        "storage key",
    )

    # 3. disable the STUDY 1.0 to-do engine ---------------------------
    html = must_replace(
        html,
        "function studyBlock(dateStr){\n  const lectures = studyLectures(dateStr);",
        "function studyBlock(dateStr){\n"
        "  /* Classmate calendar: the to-do engine is off. The to-do column\n"
        "     starts empty every day and holds only what the viewer adds. */\n"
        "  return null;\n"
        "  const lectures = studyLectures(dateStr);",
        "studyBlock",
    )

    # 4. de-personalise the visible copy ---------------------------
    html = must_replace(
        html,
        'document.getElementById("foot").textContent =\n'
        '  `Built from “${DATA.meta.source_pdf}” · parsed '
        '${DATA.meta.parsed_at.replace("T"," ")} · your edits are saved in this browser`;',
        'document.getElementById("foot").textContent =\n'
        '  `Your schedule edits and to-dos are saved in this browser, on this device`;',
        "footer copy",
    )
    html = must_replace(
        html,
        '"note":"Anna\'s swatch as Finn re-sent it (assets/floral-light.webp, '
        'from background.jpeg): pale blue roses on a near-white ground. Ground '
        '#feffff and hue 210 are sampled from that file, not chosen. This pack '
        'is deliberately SINGLE-COLOURWAY -- see noDark. Text is blue rather '
        'than near-black, at Finn\'s request."',
        '"note":"Pale blue roses on a near-white ground."',
        "floral theme note",
    )
    return html


def load_registry():
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"calendars": []}


def write_calendar(slug, name, label):
    html = derive(slug, name, label)
    # Each calendar is served from its own folder as index.html, so the URL is
    # <site>/chloe/ with no file extension.
    targets = [DOCS / slug / "index.html"]
    # The generic one is also the site root.
    if slug == "calendar":
        targets.append(DOCS / "index.html")
    version_json = VERSION_SRC.read_text(encoding="utf-8") if VERSION_SRC.exists() else None
    for t in targets:
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(html, encoding="utf-8")
        rel = t.relative_to(HERE)
        print(f"wrote {rel}  ({t.stat().st_size / 1024:.0f} KB)")
        if version_json is not None:
            (t.parent / "version.json").write_text(version_json, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help='first name, e.g. "Chloe" -> "Chloe’s Calendar"')
    ap.add_argument("--label", help='verbatim page name, e.g. "Calendar"')
    ap.add_argument("--slug", help="url-safe id, e.g. chloe")
    ap.add_argument("--all", action="store_true",
                    help="rebuild every calendar listed in registry.json")
    args = ap.parse_args()

    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").touch()  # serve files as-is, skip Jekyll processing
    reg = load_registry()

    if args.all:
        targets = [(c["slug"], c.get("name"), c.get("label")) for c in reg["calendars"]]
        if not targets:
            sys.exit("registry.json has no calendars yet.")
    else:
        if not (args.slug and (args.name or args.label)):
            sys.exit("give --slug plus --name or --label, or use --all")
        targets = [(args.slug, args.name, args.label)]

    for slug, name, label in targets:
        write_calendar(slug, name, label)

    if not args.all:
        known = {c["slug"] for c in reg["calendars"]}
        if args.slug not in known:
            entry = {"slug": args.slug}
            if args.label:
                entry["label"] = args.label
            else:
                entry["name"] = args.name
            entry["path"] = "/" if args.slug == "calendar" else f"/{args.slug}/"
            reg["calendars"].append(entry)
            REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
            print(f"added {args.slug} to registry.json")


if __name__ == "__main__":
    main()
