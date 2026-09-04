# 1440 Intelligence — web app

The MD-facing app for the 1440 Intelligence Platform (build brief §8). Next.js 15 (App
Router, TypeScript, Tailwind v4), installable as a PWA, talking to the FastAPI service in
`../api`.

## Environment

| Variable                   | Default                 | Meaning                                                                 |
| -------------------------- | ----------------------- | ----------------------------------------------------------------------- |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Origin of the API. Read at **build time** by `next.config.ts` rewrites. |

Copy `.env.example` to `.env.local` to override it locally.

The browser never calls the API origin directly. `next.config.ts` rewrites `/api/*` and
`/auth/*` to `NEXT_PUBLIC_API_BASE_URL`, so the API's httpOnly `intel_session` cookie is
first-party to the web origin (required for WebAuthn and for SameSite=Lax cookies).
`src/lib/api.ts` therefore uses relative URLs in the browser and the absolute base only on
the server.

## Run locally

```bash
# terminal 1 — the API on :8000 (see ../api)
# terminal 2
cd web
npm install
npm run dev          # http://localhost:3000
```

API-side settings that must match for auth to work in dev: `APP_ORIGIN=http://localhost:3000`,
`APP_RP_ID=localhost`, `APP_USERS=<the two allow-listed addresses>`, and
`API_BASE_URL=http://localhost:3000` so the emailed magic link lands on the web origin.

Checks:

```bash
npm run lint
npm run build        # must pass with NEXT_PUBLIC_API_BASE_URL unset
```

## Auth flow

1. **Passkey (primary).** `/signin` → `POST /auth/passkey/login/options` →
   `startAuthentication` (`@simplewebauthn/browser`) → `POST /auth/passkey/login/verify`
   with `{credential}`. The API sets the 90-day session cookie; the app routes to `next`.
2. **Magic link (first device / recovery only).** The "Use a sign-in link instead" form posts
   to `POST /auth/magic-link`. The response is always 204 and the UI always says "If that
   address is on the list, a link is on its way"; it never reveals whether an address is
   allowed.
3. **Landing from the email.** The API builds the link as
   `{API_BASE_URL}/auth/magic-link/verify?token=…`. With the API's `API_BASE_URL` set to the
   web origin, the browser navigation hits `next.config.ts`, which redirects document
   requests (`Accept: text/html`) to `/signin/verify?token=…`. That page calls the same
   endpoint with `Accept: application/json` (rewritten to the API, cookie set) and routes
   to the returned `next` (`/enrol` when the account has no passkey yet, else `/`).
4. **Enrol.** `/enrol` → `POST /auth/passkey/register/options` → `startRegistration` →
   `POST /auth/passkey/register/verify` with `{credential, device_name}` → home.
5. `src/middleware.ts` redirects to `/signin` when the session cookie is absent; the API
   remains the authority (a 401 from any call also redirects, see `src/lib/api.ts`).

## Layout of `src`

- `app/(app)/` — the shell (top bar + history panel): `/` Today, `/brief/[number]`,
  `/brief/[number]/people`, `/ops` (operator only, role from `GET /auth/me`).
- `app/(auth)/` — bare screens: `/signin`, `/signin/verify`, `/enrol`.
- `components/` — `TopBar`, `SidePanel` (cursor-paginated history + search/filters),
  `TodayView`, `brief/*` (pdf.js viewer, verification, score, audit, actions, people,
  outreach), `ops/*`, `auth/*`.
- `lib/api.ts` (typed client), `lib/types.ts` (mirrors `api/intel_api/serializers.py`),
  `lib/fonts.ts`, `lib/format.ts`, `lib/theme.ts`.

## Design

Brand tokens from `pipeline/intel/templates/brief.html.j2` (navy `#191a48`, gold `#d1ae7a`,
ink, muted, hairline, panel) live in `src/app/globals.css` as CSS variables mapped into
Tailwind v4's `@theme`. Lora (display) and Poppins (UI) are self-hosted via
`next/font/local` from the vendored OFL TTFs in `public/fonts` (the same files the PDF
renderer uses), so builds and the installed app never depend on Google Fonts.

Theme: `data-theme` on `<html>`, set before hydration by an inline script — stored
choice in `localStorage`, otherwise dark on phone-sized viewports and light on desktop.
Toggle in the menu.

## PWA

- `public/manifest.webmanifest` (name "1440 Intelligence", short name "1440", standalone,
  navy). Icons in `public/icon-*.png` / `apple-touch-icon.png` were generated with Pillow
  from `pipeline/intel/assets/1440_logo.png` on a navy square (`logo-gold.png` is the
  keyed-out gold wordmark used in the top bar).
- `public/sw.js`, registered by `components/RegisterSW.tsx`: cache-first for the app shell
  and static assets; network-first with cache fallback for `/api/*` GETs (JSON and PDFs),
  so briefs already opened remain readable offline. Auth routes and non-GET requests are
  never cached; only 2xx responses are stored. Sign out clears the caches.
- iOS meta tags (`apple-mobile-web-app-capable`, black-translucent status bar,
  apple-touch-icon) are set in `app/layout.tsx`.

## Deploying to Vercel

Set `NEXT_PUBLIC_API_BASE_URL` to the API's public origin **in the project's build
environment** — the rewrites are compiled into the build, so changing it requires a
redeploy. On the API side set `APP_ORIGIN` to the Vercel origin, `APP_RP_ID` to its host,
`APP_COOKIE_SECURE=true`, and `API_BASE_URL` to the web origin so magic links open in the
app. Passkeys require HTTPS (Vercel provides it) and the RP ID must equal the web host.
