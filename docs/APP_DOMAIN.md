# Putting the desk on a 1440 address (needs DNS)

> **DNS is not available (operator, 6 Sep 2026).** Use `docs/APP_URL.md` instead — it has
> two routes that remove the personal name with no DNS record at all. Keep this page for
> the day a DNS change becomes possible: a custom domain still beats both.

The links in the signal email currently read
`https://trushil27.github.io/1440sports/#/brief/127`. That is a personal GitHub username in
a company artefact — fine while only the operator sees it, wrong the moment the MD or a
client does (operator decision, 6 Sep 2026).

The target address is **`intel.1440sports.com`**, which is already the default in
`Settings.app_base_url`. Two steps and one switch make it live.

## 1. DNS (at whoever hosts 1440sports.com)

Add one record:

| Type | Name | Value |
|---|---|---|
| CNAME | `intel` | `trushil27.github.io` |

If the DNS provider will not CNAME that name, four A records work instead, pointing `intel`
at GitHub Pages: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.

Give it a few minutes, then check: `dig +short intel.1440sports.com` should answer.

## 2. Tell the publisher — only after step 1 resolves

GitHub → the repo → Settings → Secrets and variables → Actions → Variables:

| Variable | Value |
|---|---|
| `APP_DOMAIN` | `intel.1440sports.com` |
| `APP_BASE_URL` | `https://intel.1440sports.com` |

`APP_DOMAIN` makes the Pages workflow write the `CNAME` file into the published site.
`APP_BASE_URL` is what the daily job puts in the email link.

**Order matters.** Setting `APP_DOMAIN` before the DNS record exists takes the live site
down: GitHub will redirect the `github.io` address to a domain that does not resolve. The
workflow only writes the file when the variable is set, so until you set it nothing changes.

Then re-run the **Pages** workflow once (Actions → Pages → Run workflow). GitHub issues the
HTTPS certificate automatically within a few minutes.

## Why not the alternatives

- **A GitHub organisation** (`1440sports.github.io`) also removes the personal name, but it
  means transferring the repository and re-pointing every secret and workflow. More work,
  same result.
- **Netlify** (`something.netlify.app`) is quick and the repo already supports it
  (`intel/netlify.py`, `netlify.toml`), but it swaps a personal name for a hosting brand
  rather than the company's own.

The custom domain is the only option that ends with a link reading 1440 Sports and nothing
else, and it costs one DNS record.

## What the link looks like

The app is a hash-routed single page, so a brief lives at `<base>/#/brief/<number>`:

    https://intel.1440sports.com/#/brief/127

`intel.mail_brief.brief_url` builds that from `APP_BASE_URL`, so changing the variable
changes every future email. (The old body built `<base>/brief/127` — a double slash and no
`#` — which opened the front page rather than the brief. Fixed 6 Sep 2026, with a test.)
