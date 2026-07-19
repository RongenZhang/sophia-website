"""
Configuration for the sophia-zhang.com site builder.

Edit the values here to change WHERE the CV comes from, WHICH CV file is used,
and HOW the site is deployed. You normally never need to touch build.py itself.
"""

import os

# --- Where your CV files live (the Box folder) -----------------------------
# The builder reads the *newest* CV matching CV_GLOB from this folder.
CV_FOLDER = (
    "/Users/rongenzhang/Library/CloudStorage/Box-Box/"
    "Personal/Personal Documents/CV"
)

# Which files count as "your CV". Default: the standard dated CVs like
# RongenZhang_CV_May7_2026.docx. The variants below are ignored so the site
# always tracks your main CV. To drive the site from the "forwebsite" versions
# instead, change CV_GLOB to "RongenZhang_CV_forwebsite_*.docx".
CV_GLOB = "RongenZhang_CV_*.docx"
CV_EXCLUDE = ("forwebsite", "Tenure", "larger font", "~$")

# --- Repo / output paths (do not usually need changing) --------------------
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(REPO_DIR, "docs")            # GitHub Pages serves this
DATA_DIR = os.path.join(REPO_DIR, "data")
TEMPLATE_DIR = os.path.join(REPO_DIR, "templates")
ASSETS_DIR = os.path.join(REPO_DIR, "assets")

# --- Deployment ------------------------------------------------------------
# When True, a successful build that changed the site is committed and pushed
# so GitHub Pages redeploys. Set False to build locally without pushing.
GIT_AUTO_PUSH = True
GIT_COMMIT_PREFIX = "Auto-update site from"

# The custom domain written into docs/CNAME (kept identical to your Wix domain).
CUSTOM_DOMAIN = "sophia-zhang.com"
