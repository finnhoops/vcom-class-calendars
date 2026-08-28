# vcom-class-calendars

Copies of Anna's VCOM Block 1 calendar for her classmates, served from one
GitHub Pages site. Each calendar:

- has the **same class schedule and exams** as Anna's (baked in at build time),
- shows the person's name in the header (`Chloe’s Calendar`),
- starts with an **empty to-do list** the person edits themselves,
- lives at its **own folder** on the site, and
- saves that person's to-dos, renames, and theme in *their own browser* — copies
  never share data with each other or with Anna's calendar.

Anna's own calendar (`anna-vcom-calendar.vercel.app`) is separate and has its own
pipeline. It is not built here.

## Links

| Calendar | URL |
|---|---|
| Calendar (generic) | https://finnhoops.github.io/vcom-class-calendars/ |
| Chloe | https://finnhoops.github.io/vcom-class-calendars/chloe/ |

## How it deploys

GitHub Pages serves this repo from the **`main` branch, `/docs` folder**
(Settings → Pages). **A push to `main` redeploys** — Pages does no build step,
there is no Jekyll (`docs/.nojekyll`). The generated pages in `docs/` are
committed on purpose. The repo is public because Pages on a private repo needs a
paid GitHub plan.

Each calendar is its own folder (`docs/chloe/index.html`) so the URL is clean:
`…/chloe/`. Every page is a single self-contained HTML file — all assets are
inlined — so it doesn't matter what path it's served from.

## Files

| path | what it is |
|---|---|
| `derive.py` | turns Anna's built page into each classmate's page |
| `registry.json` | every calendar: slug, display name, path |
| `docs/**/index.html` | the generated pages Pages serves (committed) |

## Add a classmate

```
python3 derive.py --name "Maya" --slug maya
git add -A && git commit -m "Add Maya" && git push
```

`registry.json` gets the new row automatically. The page is live at
`…/maya/` a minute or two after the push.

## When a new schedule PDF comes out

The schedule is baked into each page, so these do not update themselves.

**The easy way — one command, from the `Claude/` folder:**

```
./update-calendars.sh /path/to/new-schedule.pdf
```

That runs Anna's pipeline (parse → safety gate → build → push) and, only if it
passes, runs `sync.sh` here to rebuild and push every classmate calendar. You
normally trigger this by telling Claude "update the calendars" after dropping the
PDF in the Drive folder — the `update-calendars` skill fetches the PDF and runs
this script.

**By hand, if you ever need to run just this half:**

```
./sync.sh                    # after Anna's build/index.html is already updated
```

Pages redeploys every calendar. All links stay the same. Each classmate's to-dos
and edits survive — they live in the browser, keyed per calendar — with the same
caveats as Anna's: a class the school *moves* comes back unticked, and hand-typed
to-dos stay on the date they were written.

## One-time setup on a new Mac

- `python3 -m pip install --user pymupdf` — the PDF parser Anna's pipeline needs

If `derive.py` aborts with "anchor moved", Anna's page changed shape and the
matching string in `derive.py` needs a tweak; the schedule content is fine.
