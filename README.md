# sophia-zhang.com

A free, self-updating personal academic website. The site is generated from the
**newest CV** in your Box CV folder and redeploys itself whenever you save a new
CV version.

## How it works

```
Box CV folder → build.py (parse newest CV) → docs/ (static site) → GitHub Pages → sophia-zhang.com
```

- `config.py` — where the CV lives, which files count as "your CV", the domain.
- `content.py` — hand-written copy (About bio, research-stream blurbs, teaching
  descriptions, contact). Edit freely; a CV rebuild never overwrites it.
- `build.py` — reads the newest CV, parses it, and regenerates `docs/`.
- `templates/`, `assets/` — the page skeletons and styling.
- `docs/` — the generated site GitHub Pages serves (don't edit by hand).
- `com.sophia.website.plist` — the macOS scheduler that runs the rebuild.

## Everyday use

Just save a new CV into the folder (e.g. `RongenZhang_CV_Aug1_2026.docx`).
The scheduler notices, rebuilds, and pushes — the live site updates on its own.

The site's **Download CV** button needs a PDF. If you save a `.docx` without a
matching `.pdf`, `build.py` **auto-exports one** (via LibreOffice, headless) next
to the `.docx` and reuses it thereafter. You can still export your own PDF with
the same name to override the auto-generated one. Auto-export needs LibreOffice
installed (`brew install --cask libreoffice`); toggle it with `AUTO_EXPORT_PDF`
in `config.py`.

## Manual commands

```bash
python3 build.py            # rebuild only if the CV changed, then push
python3 build.py --force    # always rebuild
python3 build.py --no-push  # build locally without pushing
```

## Editing the site text

- Bio / research streams / teaching / contact → edit `content.py`, then
  `python3 build.py --force`.
- Change which CV drives the site, or the schedule → see `config.py` and
  `com.sophia.website.plist`.

First-time hosting setup (GitHub + domain) is in **SETUP.md**.
