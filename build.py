#!/usr/bin/env python3
"""
build.py — generate sophia-zhang.com from the latest CV.

Pipeline:
  1. Find the newest CV .docx in the Box folder (see config.py).
  2. If it is unchanged since the last build, exit (unless --force).
  3. Extract text from the .docx (stdlib only), parse it into sections.
  4. Render the static site into docs/ from the templates.
  5. Copy the matching CV PDF to docs/cv.pdf.
  6. If configured, commit + push so GitHub Pages redeploys.

Run manually:   python3 build.py            (build only if CV changed)
                python3 build.py --force    (always rebuild)
                python3 build.py --no-push  (build but don't git push)

Requires only the Python 3 standard library.
"""

import argparse
import datetime as _dt
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import zipfile

import config
import content


# ---------------------------------------------------------------------------
# 1. Locate the newest CV
# ---------------------------------------------------------------------------
_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _date_from_name(name):
    """Best-effort parse of a date embedded in a CV filename, e.g.
    RongenZhang_CV_May7_2026.docx -> date(2026, 5, 7). Falls back to (0,0,0)."""
    m = re.search(r"([A-Za-z]{3,9})\s*_?\s*(\d{1,2})[_\-, ]+(\d{4})", name)
    if m:
        mon = _MONTHS.get(m.group(1)[:3].lower())
        if mon:
            return (int(m.group(3)), mon, int(m.group(2)))
    m = re.search(r"([A-Za-z]{3,9})[_\- ]+(\d{4})", name)   # Month + Year only
    if m:
        mon = _MONTHS.get(m.group(1)[:3].lower())
        if mon:
            return (int(m.group(2)), mon, 1)
    return (0, 0, 0)


def find_latest_cv():
    import glob
    pattern = os.path.join(config.CV_FOLDER, config.CV_GLOB)
    candidates = []
    for path in glob.glob(pattern):
        base = os.path.basename(path)
        if any(x.lower() in base.lower() for x in config.CV_EXCLUDE):
            continue
        candidates.append(path)
    if not candidates:
        raise SystemExit(
            f"No CV matched {config.CV_GLOB!r} in {config.CV_FOLDER!r}")
    # Rank by (filename date, file mtime) so the newest wins either way.
    candidates.sort(
        key=lambda p: (_date_from_name(os.path.basename(p)),
                       os.path.getmtime(p)))
    return candidates[-1]


def _soffice_bin():
    """Locate the LibreOffice CLI, or return None."""
    cand = getattr(config, "LIBREOFFICE_PATH", "") or \
        "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.exists(cand):
        return cand
    from shutil import which
    return which("soffice")


def export_pdf_with_libreoffice(docx_path, out_path):
    """Headless docx -> pdf via LibreOffice. Works unattended (no GUI/prompts).
    Returns True on success. Never raises."""
    soffice = _soffice_bin()
    if not soffice:
        return False
    outdir = os.path.dirname(out_path)
    try:
        r = subprocess.run(
            [soffice, "--headless",
             "-env:UserInstallation=file:///tmp/sophia_libreoffice",
             "--convert-to", "pdf", "--outdir", outdir, docx_path],
            capture_output=True, text=True, timeout=240)
    except Exception as e:
        print(f"  LibreOffice export failed ({e}).")
        return False
    # LibreOffice writes <docx-stem>.pdf into outdir, which equals out_path.
    if os.path.exists(out_path):
        print(f"  Exported PDF via LibreOffice: {os.path.basename(out_path)}")
        return True
    print(f"  LibreOffice export did not produce a PDF "
          f"({(r.stderr or r.stdout or '').strip()[:120]}).")
    return False


def export_pdf_with_word(docx_path, out_path):
    """Fallback: export via Microsoft Word (AppleScript). Reliable only in an
    interactive session with automation permission granted; not for the
    unattended scheduler. Returns True on success. Never raises."""
    script = os.path.join(config.REPO_DIR, "export_pdf.applescript")
    if not os.path.exists(script):
        return False
    try:
        r = subprocess.run(
            ["osascript", script, docx_path, out_path],
            capture_output=True, text=True, timeout=180)
    except Exception as e:
        print(f"  Word export failed ({e}).")
        return False
    if r.returncode == 0 and os.path.exists(out_path):
        print(f"  Exported PDF via Word: {os.path.basename(out_path)}")
        return True
    return False


def export_pdf(docx_path, out_path):
    """Try LibreOffice (unattended-friendly) first, then Word as a fallback."""
    return (export_pdf_with_libreoffice(docx_path, out_path)
            or export_pdf_with_word(docx_path, out_path))


def matching_pdf(docx_path):
    """PDF with the same basename as the CV, else the newest matching PDF.
    If none matches and AUTO_EXPORT_PDF is on, generate one from the docx."""
    stem = os.path.splitext(docx_path)[0]
    if os.path.exists(stem + ".pdf"):
        return stem + ".pdf"
    if getattr(config, "AUTO_EXPORT_PDF", False):
        if export_pdf(docx_path, stem + ".pdf"):
            return stem + ".pdf"
    import glob
    pdfs = [p for p in glob.glob(os.path.join(config.CV_FOLDER, "*.pdf"))
            if not any(x.lower() in os.path.basename(p).lower()
                       for x in config.CV_EXCLUDE)]
    if not pdfs:
        return None
    pdfs.sort(key=lambda p: (_date_from_name(os.path.basename(p)),
                             os.path.getmtime(p)))
    return pdfs[-1]


# ---------------------------------------------------------------------------
# 2. Extract text from the .docx
# ---------------------------------------------------------------------------
def extract_docx_text(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = xml.replace("</w:p>", "\n")          # paragraph -> newline
    xml = xml.replace("<w:tab/>", "\t")        # real tab char -> tab
    text = re.sub(r"<[^>]+>", "", xml)         # drop remaining tags
    text = html.unescape(text)
    lines = [ln.rstrip() for ln in text.split("\n")]
    return [ln for ln in lines if ln.strip()]


# ---------------------------------------------------------------------------
# 3. Parse the CV into structured sections
# ---------------------------------------------------------------------------
# (canonical key, uppercase prefix that identifies the heading line)
_HEADINGS = [
    ("research_interests", "RESEARCH INTEREST"),
    ("employment",         "EMPLOYMENT"),
    ("education",          "EDUCATION"),
    ("journal",            "JOURNAL PUBLICATION"),
    ("proceedings",        "PEER-REVIEWED CONFERENCE PROCEEDINGS"),
    ("book",               "BOOK CHAPTER"),
    ("presentations",      "CONFERENCE PRESENTATIONS"),
    ("working",            "WORKING PAPER"),
    ("in_progress",        "RESEARCH IN PROGRESS"),
    ("invited",            "INVITED TALK"),
    ("teaching",           "TEACHING"),
    ("awards",             "AWARD"),
    ("service",            "PROFESSIONAL SERVICE"),
    ("skills",             "TECHNICAL SKILL"),
    ("membership",         "PROFESSIONAL MEMBERSHIP"),
]

_SERVICE_SUBHEADS = {
    "university service", "invited panels", "invited speaker",
    "graduate student thesis committee", "invited reviewer",
    "associate editor", "board member", "coordinator", "volunteer",
}


def _heading_key(line):
    norm = re.sub(r"\s+", " ", line.strip()).upper()
    for key, prefix in _HEADINGS:
        if norm.startswith(prefix) and len(norm) <= len(prefix) + 30:
            return key
    return None


def split_sections(lines):
    sections, cur, buf = {}, None, []
    for ln in lines:
        key = _heading_key(ln)
        if key:
            if cur:
                sections[cur] = buf
            cur, buf = key, []
        elif cur:
            buf.append(ln)
    if cur:
        sections[cur] = buf
    return sections


_YEAR_PAREN = re.compile(r"\((?:19|20)\d{2}[a-z]?\)")


def _has_quote(s):
    return "“" in s or "”" in s or '"' in s


def _group_pubs(lines, require_year):
    """Group citation lines (each followed by 0+ description paragraphs)."""
    entries, cur = [], None
    for ln in lines:
        is_new = _has_quote(ln) and (not require_year or _YEAR_PAREN.search(ln))
        if is_new or cur is None:
            cur = {"citation": ln, "notes": []}
            entries.append(cur)
        else:
            cur["notes"].append(ln)
    return entries


def _pairs(lines):
    """Employment/education: pair an org line with its detail line."""
    def cut(s):
        if "\t" in s:
            a, b = s.split("\t", 1)
        else:
            m = re.split(r"\s{2,}", s, 1)
            a, b = (m[0], m[1]) if len(m) == 2 else (s, "")
        return a.strip(), b.strip()

    out = []
    i = 0
    while i < len(lines):
        org, loc = cut(lines[i])
        role, date = ("", "")
        if i + 1 < len(lines):
            role, date = cut(lines[i + 1])
        out.append({"org": org, "location": loc, "role": role, "date": date})
        i += 2
    return out


def _parse_service(lines):
    groups, cur = [], None
    for ln in lines:
        label = re.sub(r"\s+", " ", ln.strip())
        if label.lower() in _SERVICE_SUBHEADS:
            cur = {"label": label, "items": []}
            groups.append(cur)
        elif cur:
            cur["items"].append(ln.strip())
        else:  # items before any sub-heading
            cur = {"label": "", "items": [ln.strip()]}
            groups.append(cur)
    return groups


def parse_cv(lines):
    sec = split_sections(lines)
    data = {}
    data["research_interests"] = " ".join(sec.get("research_interests", []))
    data["employment"] = _pairs(sec.get("employment", []))
    data["education"] = _pairs(sec.get("education", []))
    data["journal"] = _group_pubs(sec.get("journal", []), require_year=True)
    data["working"] = _group_pubs(sec.get("working", []), require_year=False)
    for key in ("proceedings", "book", "presentations", "in_progress",
                "invited"):
        data[key] = [{"citation": ln, "notes": []} for ln in sec.get(key, [])]
    data["awards"] = [ln.strip() for ln in sec.get("awards", [])]
    data["service"] = _parse_service(sec.get("service", []))
    data["skills"] = [ln.strip() for ln in sec.get("skills", [])]
    data["membership"] = [ln.strip() for ln in sec.get("membership", [])]
    return data


# ---------------------------------------------------------------------------
# 4. Render HTML
# ---------------------------------------------------------------------------
def esc(s):
    return html.escape(s, quote=False)


def _pub_html(entries, show_notes=True):
    out = []
    for e in entries:
        notes = ""
        if show_notes and e["notes"]:
            notes = "".join(
                f'<p class="pub-note">{esc(n)}</p>' for n in e["notes"])
        out.append(
            f'<li class="pub"><p class="pub-cite">{esc(e["citation"])}</p>'
            f'{notes}</li>')
    return "\n".join(out)


def _pub_section(title, entries, show_notes=True, anchor=None):
    if not entries:
        return ""
    aid = f' id="{anchor}"' if anchor else ""
    return (f'<section class="pubgroup"{aid}><h3>{esc(title)} '
            f'<span class="count">{len(entries)}</span></h3>'
            f'<ol class="publist">{_pub_html(entries, show_notes)}</ol>'
            f'</section>')


def render(data, meta):
    tpl = _load_templates()
    site = content.SITE
    ctx = {
        "NAME": esc(site["name"]),
        "TITLE": esc(site["title"]),
        "AFFILIATION": esc(site["affiliation"]),
        "EMAIL": esc(site["email"]),
        "EMAIL_RAW": site["email"],
        "BAYLOR": site["baylor_profile"],
        "LINKEDIN": site["linkedin"],
        "SCHOLAR": site.get("scholar", ""),
        "YEAR": str(_dt.date.today().year),
        "CV_DATE": esc(meta["cv_date_label"]),
        "RESEARCH_INTERESTS": esc(data["research_interests"]),
        "ABOUT": "".join(f"<p>{esc(p)}</p>" for p in content.ABOUT),
        "STREAMS": _streams_html(),
        "TEACHING": _teaching_html(),
        "AWARDS": "".join(f"<li>{esc(a)}</li>" for a in data["awards"]),
        "SERVICE": _service_html(data["service"]),
        "SKILLS": "".join(f"<li>{esc(s)}</li>" for s in data["skills"]),
        "MEMBERSHIP": "".join(f"<li>{esc(m)}</li>"
                              for m in data["membership"]),
        "EDUCATION": _edu_html(data["education"]),
        "CONTACT_QUOTE": esc(content.CONTACT["quote"]),
        "CONTACT_AUTHOR": esc(content.CONTACT["quote_author"]),
        "CONTACT_ACTION": _contact_action(),
    }
    # Publications page body
    pubs = []
    pubs.append(_pub_section("Refereed Journal Articles", data["journal"]))
    pubs.append(_pub_section("Peer-Reviewed Conference Proceedings",
                             data["proceedings"], show_notes=False))
    pubs.append(_pub_section("Book Chapters", data["book"], show_notes=False))
    pubs.append(_pub_section("Working Papers", data["working"]))
    pubs.append(_pub_section("Research in Progress", data["in_progress"],
                             show_notes=False))
    pubs.append(_pub_section("Conference Presentations & Workshops",
                             data["presentations"], show_notes=False))
    pubs.append(_pub_section("Invited Talks & Presentations",
                             data["invited"], show_notes=False))
    ctx["PUBLICATIONS"] = "\n".join(p for p in pubs if p)

    index = _fill(tpl["index"], ctx)
    pubs_page = _fill(tpl["publications"], ctx)
    return {"index.html": index, "publications.html": pubs_page}


def _streams_html():
    out = []
    for s in content.RESEARCH_STREAMS:
        img = ""
        if s.get("image"):
            img = (f'<div class="stream-img">'
                   f'<img src="assets/img/{s["image"]}" alt="" loading="lazy">'
                   f'</div>')
        out.append(
            f'<article class="stream">{img}'
            f'<div class="stream-body"><h3>{esc(s["title"])}</h3>'
            f'<p>{esc(s["body"])}</p></div></article>')
    return "\n".join(out)


def _teaching_html():
    out = []
    for c in content.TEACHING:
        out.append(
            f'<article class="course"><h3>{esc(c["code"])} — '
            f'{esc(c["name"])}</h3>'
            f'<p class="course-inst">{esc(c["institution"])}</p>'
            f'<p>{esc(c["body"])}</p></article>')
    return "\n".join(out)


def _service_html(groups):
    out = []
    for g in groups:
        head = f"<h3>{esc(g['label'])}</h3>" if g["label"] else ""
        items = "".join(f"<li>{esc(i)}</li>" for i in g["items"])
        out.append(f'<div class="svc-group">{head}<ul>{items}</ul></div>')
    return "\n".join(out)


def _edu_html(entries):
    out = []
    for e in entries:
        out.append(
            f'<li><span class="edu-org">{esc(e["org"])}</span>'
            f'<span class="edu-meta">{esc(e["location"])}</span>'
            f'<span class="edu-role">{esc(e["role"])}</span>'
            f'<span class="edu-meta">{esc(e["date"])}</span></li>')
    return "\n".join(out)


def _contact_action():
    ep = content.CONTACT.get("formspree_endpoint", "").strip()
    email = content.SITE["email"]
    if ep:
        return (
            f'<form class="contact-form" action="{ep}" method="POST">'
            f'<input type="text" name="name" placeholder="Your name" required>'
            f'<input type="email" name="email" placeholder="Your email" '
            f'required>'
            f'<textarea name="message" placeholder="Your message" rows="5" '
            f'required></textarea>'
            f'<button type="submit">Send</button></form>')
    return (f'<a class="btn" href="mailto:{email}">Email me</a>')


def _load_templates():
    out = {}
    for name in ("index", "publications"):
        with open(os.path.join(config.TEMPLATE_DIR, name + ".html"),
                  encoding="utf-8") as f:
            out[name] = f.read()
    return out


def _fill(tpl, ctx):
    for k, v in ctx.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    return tpl


# ---------------------------------------------------------------------------
# 5 & 6. Write output, copy assets/PDF, deploy
# ---------------------------------------------------------------------------
def write_site(pages, cv_docx):
    import shutil
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    # assets
    dst_assets = os.path.join(config.DOCS_DIR, "assets")
    if os.path.isdir(dst_assets):
        shutil.rmtree(dst_assets)
    shutil.copytree(os.path.join(config.ASSETS_DIR), dst_assets)
    # pages
    for name, body in pages.items():
        with open(os.path.join(config.DOCS_DIR, name), "w",
                  encoding="utf-8") as f:
            f.write(body)
    # CNAME + .nojekyll
    with open(os.path.join(config.DOCS_DIR, "CNAME"), "w") as f:
        f.write(config.CUSTOM_DOMAIN + "\n")
    open(os.path.join(config.DOCS_DIR, ".nojekyll"), "w").close()
    # CV pdf
    pdf = matching_pdf(cv_docx)
    if pdf:
        shutil.copyfile(pdf, os.path.join(config.DOCS_DIR, "cv.pdf"))


def git_deploy(msg):
    def git(*args):
        return subprocess.run(["git", "-C", config.REPO_DIR, *args],
                              capture_output=True, text=True)
    if git("rev-parse", "--is-inside-work-tree").returncode != 0:
        print("  (not a git repo yet — skipping push)")
        return
    if "origin" not in git("remote").stdout.split():
        print("  (no 'origin' remote yet — committed nothing, skipping push)")
        return
    git("add", "-A")
    if not git("status", "--porcelain").stdout.strip():
        print("  (no changes to commit)")
        return
    git("commit", "-m", msg)
    r = git("push")
    print("  pushed." if r.returncode == 0 else f"  push failed: {r.stderr}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="rebuild even if the CV is unchanged")
    ap.add_argument("--no-push", action="store_true",
                    help="build but do not git commit/push")
    args = ap.parse_args()

    cv = find_latest_cv()
    base = os.path.basename(cv)
    # Signature covers the .docx AND a same-named .pdf (your Word export), so
    # replacing just the PDF also triggers a rebuild.
    h = hashlib.sha256()
    h.update(open(cv, "rb").read())
    stem_pdf = os.path.splitext(cv)[0] + ".pdf"
    if os.path.exists(stem_pdf):
        h.update(b"|pdf|")
        h.update(open(stem_pdf, "rb").read())
    digest = h.hexdigest()
    stamp_path = os.path.join(config.DATA_DIR, ".last_build")
    os.makedirs(config.DATA_DIR, exist_ok=True)

    last = ""
    if os.path.exists(stamp_path):
        last = open(stamp_path).read().strip()
    if not args.force and last == f"{base}\t{digest}":
        print(f"No change (latest CV: {base}). Nothing to do.")
        return

    print(f"Building from: {base}")
    lines = extract_docx_text(cv)
    data = parse_cv(lines)

    y, m, d = _date_from_name(base)
    label = (f"{_dt.date(y, m, d):%B %d, %Y}" if y
             else _dt.date.today().strftime("%B %d, %Y"))
    meta = {"cv_file": base, "cv_date_label": label}

    with open(os.path.join(config.DATA_DIR, "cv.json"), "w",
              encoding="utf-8") as f:
        json.dump({"meta": meta, "data": data}, f, indent=2, ensure_ascii=False)

    pages = render(data, meta)
    write_site(pages, cv)
    with open(stamp_path, "w") as f:
        f.write(f"{base}\t{digest}")

    n = sum(len(data[k]) for k in ("journal", "proceedings", "book",
            "working", "in_progress", "presentations", "invited"))
    print(f"  Parsed {n} publications/entries, {len(data['awards'])} awards, "
          f"{len(data['service'])} service groups.")
    print(f"  Wrote site to {config.DOCS_DIR}")

    if config.GIT_AUTO_PUSH and not args.no_push:
        git_deploy(f"{config.GIT_COMMIT_PREFIX} {base}")


if __name__ == "__main__":
    main()
