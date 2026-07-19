# One-time setup: go live on sophia-zhang.com (free)

Everything is already built locally in this folder. These steps put it online at
your existing domain and turn on the automatic rebuilds. You do the account/DNS
parts (they need your logins); I can help run the terminal commands.

---

## Step 1 — Create the GitHub repo (free account)

1. Sign up / sign in at <https://github.com>.
2. Create a new **public** repository named `sophia-website` (no README, no
   .gitignore — leave it empty).
3. Copy the repo URL, e.g. `https://github.com/<username>/sophia-website.git`.

## Step 2 — Push this folder to GitHub

In Terminal (replace `<username>`):

```bash
cd ~/sophia-website
git branch -M main
git remote add origin https://github.com/<username>/sophia-website.git
git push -u origin main
```

(This folder is already a git repo with your first commit.)

## Step 3 — Turn on GitHub Pages

1. In the repo on GitHub: **Settings → Pages**.
2. **Source:** *Deploy from a branch*.
3. **Branch:** `main`, **Folder:** `/docs`. Save.
4. Wait ~1 minute; a temporary URL appears:
   `https://<username>.github.io/sophia-website/` — confirm the site loads.

## Step 4 — Point sophia-zhang.com at GitHub Pages

**First, find out where the domain is *registered*.** In your Wix account:
Settings → Domains. If it says the domain is registered through Wix, you can keep
*just the domain* (cancel only the premium **site** plan) or transfer it to a
cheaper registrar (Cloudflare ≈ $10/yr, Namecheap similar). Either way you only
need to edit its **DNS records**:

Set these records at whoever manages the DNS:

| Type  | Host / Name | Value                        |
|-------|-------------|------------------------------|
| A     | @           | `185.199.108.153`            |
| A     | @           | `185.199.109.153`            |
| A     | @           | `185.199.110.153`            |
| A     | @           | `185.199.111.153`            |
| CNAME | www         | `<username>.github.io`       |

Then in **Settings → Pages** on GitHub:
- **Custom domain:** `sophia-zhang.com` → Save (a `CNAME` file is already in
  `docs/`, so this should verify).
- Tick **Enforce HTTPS** once it becomes available (can take up to a few hours
  after DNS propagates).

## Step 5 — Turn on the automatic rebuilds

Once the push in Step 2 works (so the site can deploy itself):

```bash
cd ~/sophia-website
bash install_scheduler.sh
```

This installs a macOS LaunchAgent that:
- rebuilds **daily at noon**, and
- rebuilds **within seconds of the CV folder changing**.

`build.py` does nothing when the CV is unchanged, so it's cheap to run often.
It only runs while your Mac is on; if the Mac was asleep at noon, it runs at the
next wake. To stop it later:
`launchctl unload ~/Library/LaunchAgents/com.sophia.website.plist`.

## Step 6 — Verify, then cancel Wix

- Visit <https://sophia-zhang.com> and confirm it shows the new site with a
  padlock (HTTPS).
- Test the loop: save a new CV into the folder, wait a minute, refresh — the
  Publications/Awards/Service should reflect it.
- Once you're happy, cancel the **paid Wix plan** (keep only the domain
  registration if the domain lives at Wix).

---

## Notes & options

- **Auto-PDF export:** if a new CV `.docx` has no matching `.pdf`, the build
  generates one automatically with LibreOffice (headless, works in the scheduled
  job). It's already installed; if you ever move machines, run
  `brew install --cask libreoffice`. Toggle with `AUTO_EXPORT_PDF` in `config.py`.
- **Contact form:** the Contact section currently shows an *Email me* button. To
  get a real submit form (free), create a form at <https://formspree.io>, then
  put its endpoint in `content.py` → `CONTACT["formspree_endpoint"]` and rebuild.
- **Change the schedule:** edit the `Hour`/`Minute` in
  `com.sophia.website.plist` and re-run `bash install_scheduler.sh`.
- **Which CV is used:** newest `RongenZhang_CV_*.docx` in the folder, excluding
  `forwebsite` / `Tenure` / `larger font` variants. Change `CV_GLOB` /
  `CV_EXCLUDE` in `config.py` to retarget.
- **Logs:** `build.log` (build output), `launchd.out.log` / `launchd.err.log`
  (scheduler).
- **Troubleshooting a push from the scheduler:** if pushes need credentials, run
  one manual `git push` in Terminal first so macOS stores the GitHub credential;
  the scheduler reuses it afterward.
