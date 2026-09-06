# Getting the personal name out of the desk link

The link in the signal email reads `https://trushil27.github.io/1440sports/#/brief/127`.
That is a personal GitHub username in a company artefact — fine while only the operator sees
it, wrong the moment the MD or a client does.

A custom domain (`intel.1440sports.com`) is the ideal answer but needs a DNS record, which is
not available. **Both options below need no DNS at all.** Pick one; the desk is a single
setting either way.

---

## Option A — Netlify (fastest, already built, ~5 minutes)

Result: **`https://1440-intelligence.netlify.app/127`** — or whatever name you claim.

The code for this already exists (`intel/netlify.py`), and the daily job deploys there
automatically as soon as the two secrets are present.

1. Sign up at netlify.com with the 1440 email (free tier is enough — this is a static site).
2. **Add new site → Deploy manually.** Drag any folder in, even an empty one; you just need a
   site to exist. It gets a random name.
3. **Site configuration → Change site name** → `1440-intelligence` (or `1440-signals`,
   `1440-desk` — whatever is free). This is the name that appears in the URL.
4. Copy the **Site ID** from Site configuration → General → Site information.
5. **User settings → Applications → Personal access tokens → New access token.** Copy it.
6. In GitHub → the repo → Settings → Secrets and variables → Actions:
   - **Secrets**: `NETLIFY_AUTH_TOKEN` = the token, `NETLIFY_SITE_ID` = the site ID
   - **Variables**: `APP_BASE_URL` = `https://1440-intelligence.netlify.app`

Done. The next daily run deploys the desk there and every email link points at it.

**Trade-off:** the URL says `netlify.app`. No personal name, but a hosting brand.

---

## Option B — a free GitHub organisation (no third party, best-looking URL)

Result: **`https://1440sports-intel.github.io/127`** — no personal name, no DNS, no
outside service.

This repo does **not** move. A second, site-only repo receives the built app, so nothing
about the pipeline, its secrets or its history changes.

1. GitHub → your avatar → **Your organizations → New organization → Free plan.** Name it
   something available and on-brand: `1440sports-intel`, `1440-intelligence`, `1440sports-desk`.
   (Plain `1440sports` may be taken — the org name is what appears in the URL.)
2. Inside that organisation, **New repository**, named **exactly** `<org>.github.io` — for an
   org called `1440sports-intel` that is `1440sports-intel.github.io`. Set it **Public** and
   tick "Add a README" so the repo has a first commit.
3. Create a token that may write to it: your avatar → Settings → Developer settings →
   **Personal access tokens → Fine-grained tokens → Generate new token.** Resource owner: the
   new organisation. Repository access: only the new repo. Permissions: **Contents →
   Read and write**. Generate and copy it.
4. In **this** repo → Settings → Secrets and variables → Actions:
   - **Secrets**: `SITE_REPO_TOKEN` = that token
   - **Variables**: `SITE_REPO` = `1440sports-intel/1440sports-intel.github.io`,
     `APP_BASE_URL` = `https://1440sports-intel.github.io`
5. Actions → **Pages** → Run workflow. It publishes the site into the new repo.
6. In the new repo → Settings → Pages, confirm the source is **Deploy from a branch: main /
   (root)**. GitHub usually sets this by itself for an `<org>.github.io` repo.

The Pages workflow already handles this: with `SITE_REPO` set it pushes the built site there
instead of this repo's `gh-pages`, and it fails loudly if the token is missing rather than
publishing to the wrong place.

**Trade-off:** five more minutes than Option A, and the org name has to be one nobody has
claimed.

---

## Which to choose

Option B if the link will be seen by clients — it reads as the company and depends on nobody.
Option A if you want it working in the next five minutes.

Either way the only thing the desk cares about is `APP_BASE_URL`. Set it and every future
email link changes; `intel.mail_brief.brief_url` builds the address from it.

If DNS ever becomes available, `docs/APP_DOMAIN.md` has the custom-domain route, which beats
both.

---

## How short can the link get?

`https://1440sports-intel.github.io/127` is the floor without a domain of our own.

* The **path** is already one segment: each brief is written to `site/<number>/index.html`,
  so brief 127 is `/127`. (`/brief/127/` still resolves, so any link already sent keeps
  working.)
* The **host** cannot shrink further. `https://1440sports-intel` on its own is not a valid
  web address — every public address needs a registered domain ending such as `.com` or
  `.io`, and `1440sports-intel.github.io` IS that ending, provided free by GitHub. Dropping
  `.github.io` means owning a domain, which means a DNS record. If that ever becomes
  possible, `docs/APP_DOMAIN.md` turns the link into `https://intel.1440sports.com/127`.
