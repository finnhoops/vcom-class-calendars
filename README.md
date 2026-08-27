# vcom-class-calendars

Copies of Anna's VCOM Block 1 calendar for her classmates, served from one Vercel
site. Each calendar:

- has the **same class schedule and exams** as Anna's (baked in at build time),
- shows the person's name in the header (`Chloe’s Calendar`),
- starts with an **empty to-do list** the person edits themselves,
- lives at its **own path** on the site, and
- saves that person's to-dos, renames, and theme in *their own browser* — copies
  never share data with each other or with Anna's calendar.

Anna's own calendar (`anna-vcom-calendar.vercel.app`) is separate and has its own
pipeline. It is not built here.

## Links

| Calendar | URL |
|---|---|
| Calendar (generic) | `https://vcom-class-calendars.vercel.app` |
| Chloe | `https://vcom-class-calendars.vercel.app/chloe` |

## How it deploys

GitHub repo `finnhoops/vcom-class-calendars` is connected to a Vercel project.
**A push to `main` deploys.** `vercel.json` sets `outputDirectory: build` and
`cleanUrls: true`, so `build/chloe.html` is served at `/chloe`. The generated
pages in `build/` are committed on purpose — Vercel does no build step, there is
no `package.json`.

## Files

| path | what it is |
|---|---|
| `derive.py` | turns Anna's built page into each classmate's page |
| `registry.json` | every calendar: slug, display name, path |
| `build/*.html` | the generated pages Vercel serves (committed) |

## Add a classmate

```
python3 derive.py --name "Maya" --slug maya
git add -A && git commit -m "Add Maya" && git push
```

`registry.json` gets the new row automatically. The page is live at
`/maya` once Vercel finishes (~30s).

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

Vercel redeploys every calendar. All links stay the same. Each classmate's
to-dos and edits survive — they live in the browser, keyed per calendar — with
the same caveats as Anna's: a class the school *moves* comes back unticked, and
hand-typed to-dos stay on the date they were written.

## One-time setup on a new Mac

- `python3 -m pip install --user pymupdf` — the PDF parser Anna's pipeline needs
- import `finnhoops/vcom-class-calendars` at vercel.com (Output Directory:
  `build`) to create the Vercel project

If `derive.py` aborts with "anchor moved", Anna's page changed shape and the
matching string in `derive.py` needs a tweak; the schedule content is fine.
