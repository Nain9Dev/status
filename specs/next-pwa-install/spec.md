# Specification: Installable status page (Android and iOS)

Status: Implemented on `feat/pwa-install-status`, not merged

## Objective

A visitor on a phone can install `status.naindev.com` from the browser and open it like an app: its own icon
and name on the home screen and a window with no browser bar. Android Chrome and iOS Safari are the targets.

This is the status page's share of one change applied to every public product site of the ecosystem
(`*.naindev.com`). The shared contract and the app names were set in the install spec of the portfolio
repository (`Nain9Dev/nain9dev.github.io`); the part that binds this repository is repeated below.

## Shared contract

Verified against the published criteria on 2026-11-13 (web.dev "install criteria", MDN "Making PWAs
installable", WebKit "Web Push for Web Apps on iOS and iPadOS"):

- Chrome on Android offers the install when the page is served over HTTPS and links a manifest with `name` or
  `short_name`, a 192 px and a 512 px icon, `start_url`, and `display` set to `standalone`, `fullscreen` or
  `minimal-ui`. A service worker is not a requirement.
- iOS opens the site as an app when the manifest `display` is `standalone`. It takes the icon from
  `apple-touch-icon` before the manifest icons and the label from `apple-mobile-web-app-title`.
- A maskable icon keeps its mark inside a centred circle whose radius is 40% of the icon width. Icons with
  purpose `any` and `maskable` are separate files.

Names approved by the owner on 2026-11-13 for this host: `short_name` is `NainStatus`, the label under the
icon, within the 12 characters no launcher truncates; `name` is `NainDev Status`, what the install dialog shows.

## Functional requirements (EARS)

- **INS-001**: The site shall publish `manifest.webmanifest` at its root. When `scripts/monitor.py` writes the
  page, the page shall link it exactly once with `<link rel="manifest" href="./manifest.webmanifest">`.
- **INS-002**: The manifest shall declare `id`, `start_url` and `scope` as `./`, `display` as `standalone`,
  `dir` as `ltr`, `name` as `NainDev Status`, `short_name` as `NainStatus`, the language of the page (`en`) as
  `lang`, the meta description of the page as `description`, and the background the page paints first
  (`#07090e`) as `theme_color` and `background_color`. It shall not declare `prefer_related_applications`.
- **INS-003**: The manifest shall declare three PNG icons that exist in `icons/` at the declared size:
  `icon-192.png` and `icon-512.png` with purpose `any`, and `icon-maskable-512.png` with purpose `maskable`.
  Each entry shall carry one purpose.
- **INS-004**: The maskable icon and the Apple touch icon shall be opaque edge to edge, and the maskable icon
  shall keep every pixel of the mark inside the centred circle whose radius is 40% of the icon width.
- **INS-005**: When `scripts/monitor.py` writes the page, the page shall carry the iOS tags: one
  `apple-touch-icon` link to `./icons/apple-touch-icon.png` (180 px), an `apple-mobile-web-app-title` equal to
  the manifest `short_name`, `mobile-web-app-capable` and `apple-mobile-web-app-capable` set to `yes`, and
  `apple-mobile-web-app-status-bar-style` set to `black`.
- **INS-006**: When `scripts/monitor.py` writes the page, the page shall carry one `theme-color` meta equal to
  the manifest `theme_color` and to the `--bg` colour of its own stylesheet.
- **INS-007**: `python -m unittest discover -s tests`, the command the deploy workflow runs before it
  publishes, shall fail if INS-001 to INS-006 regress.

## Edge cases and error handling

- The workflow rewrites `index.html` on every run, so the tags live in the generator
  (`generate_html_dashboard`). A tag added only to the committed `index.html` would be lost on the next run.
- The committed `index.html` is a snapshot the workflow overwrites and commits itself. This change updates it
  by hand to what the generator writes for the committed `data/status.json`, so the repository root can be
  checked as it stands.
- The workflow publishes the whole repository root (`upload-pages-artifact` with `path: "."`), so the manifest
  and `icons/` are served with no change to the workflow. For the same reason `specs/`, `tests/` and
  `scripts/` are public files of the site, as `README.md` already is.
- The workflow runs on pushes to `main`, on its schedule and on manual dispatch, not on pull requests. The
  first CI run of the install test happens on `main` after the merge. A failing test stops the job before the
  probe and the deploy, and the site keeps its last published version.
- The page declares no Content-Security-Policy and the host sends none with a 200 answer (measured on
  2026-11-13). Nothing blocks the same-origin manifest or its icons.
- One document, relative paths: the page already links `data/status.json` relatively, and the manifest follows
  with `./`. Chrome resolves the identity of the app to the root of the origin (`Page.getAppId` on a loopback
  copy).
- Offline: the site registers no service worker, so an installed window without network shows the browser's
  own offline screen and never an old reading of the services.
- The page background and the manifest colours are literals in two files. The test fails when the `--bg`
  colour of the page, its `theme-color` meta and the manifest stop agreeing.
- The install icon is the NainDev mark, the one the page already uses as favicon. Next to the installed
  portfolio the two icons are identical and only the label tells them apart.
- Caching, measured on 2026-11-13: this host answers `Cache-Control: max-age=14400` for static files such as
  images and `max-age=600` for the page. Two sibling hosts on the same Cloudflare and GitHub Pages chain
  (`3d.naindev.com`, `order.naindev.com`) serve `manifest.webmanifest` as `application/manifest+json` with
  `max-age=600`. No answer is cached for longer than four hours, so a redrawn mark needs no new file name.

## Out of scope

- A service worker, offline pages or any cache (owner decision of 2026-11-13: installable only, in this round).
- An in-page install button or iOS instructions; the browser's own install entry is the way in.
- Screenshots for the richer Android install dialog.
- A store package (Trusted Web Activity or a native shell).
- The favicon link of the page, which keeps pointing to `https://www.naindev.com/favicon.ico`, and the letter
  badge of its header.

## Acceptance criteria

- `python -m unittest discover -s tests -v` passes with `tests/test_pwa_install.py` in the run.
- Chrome reports no installability error for the published folder (DevTools protocol
  `Page.getInstallabilityErrors` on a loopback copy).
- After the deploy, the live manifest answers 200 with a manifest media type, and the owner installs the site
  on an Android phone and on an iPhone: the icon shows the mark uncropped, the label reads `NainStatus` and the
  window opens with no browser bar.

## Session state

<!-- Session handoff: keep current. What is done, what is verified, what is next, what is blocked. -->
- Last updated: 2026-11-13, session pwa-install
- Done: T01 to T04.
- Verified: `python -m unittest discover -s tests -v` passes (27 tests, 9 of them new) on Windows and on Linux
  with CPython 3.12; Chrome reports no installability error on a copy of the published folder; the live site
  before the change answers `no-manifest`.
- Next: T05 after the merge (live manifest media type, install on Android and iOS).
- Blocked: nothing. T05 needs the owner's phones.
