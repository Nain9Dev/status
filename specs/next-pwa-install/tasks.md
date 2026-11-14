# Tasks: Installable status page (Android and iOS)

One task at a time, test first. Stop after each task. Update the `Session state` block in `spec.md` after closing each one.

- [x] **T01** `[A]` Write `tests/test_pwa_install.py`.
  - **Covers**: INS-007
  - **Done when**: `python -m unittest discover -s tests -v` fails on the current tree because the manifest,
    the icons and the tags are missing.
  - **Result**: `FAILED (errors=3)`: the three new test classes stopped at `FileNotFoundError` for
    `manifest.webmanifest` while the 18 existing tests passed. With the manifest alone in place, its three
    tests passed and the other six did not: the icon files and the head tags were still missing.
- [x] **T02** `[A]` Render the install icons from the NainDev mark.
  - **Covers**: INS-003, INS-004
  - **Done when**: the four files exist in `icons/`, the mark is crisp, centred and uncropped in each, and the
    maskable icon is opaque with its mark inside the safe zone.
  - **Result**: command and measurements in `plan.md`. `icon-192.png` and `icon-512.png` are pixel for pixel
    the icons of the portfolio; the maskable mark ends at 36.5% of the width from the centre.
- [x] **T03** `[A]` Add `manifest.webmanifest` and the head tags, in the generator and in the committed page.
  - **Covers**: INS-001, INS-002, INS-005, INS-006
  - **Done when**: `python -m unittest discover -s tests -v` passes.
  - **Result**: 27 tests pass, 9 of them new, on Windows (CPython 3.12.10) and on Linux (CPython 3.12.14, the
    version the workflow sets up). The committed `index.html` equals what the generator writes for the
    committed `data/status.json`. The PNG reader of the test returned the same pixels as `sharp` on 17 files
    covering the five filter types, with and without alpha. In a scratch copy, 40 changes that each break one
    rule (icons, manifest members, head tags) all made the suite fail.
- [x] **T04** `[A]` Ask Chrome for installability errors on the folder that gets published.
  - **Covers**: acceptance criteria
  - **Done when**: `Page.getInstallabilityErrors` returns an empty list for `/`.
  - **Result**: the steps of the workflow were run in order on a clean copy, on Linux: the test suite,
    `python scripts/monitor.py` (17 of 17 services operational) and the archive with the flags of
    `upload-pages-artifact`. The archive holds `manifest.webmanifest` and the four icons, and the page the
    monitor wrote carries the tags. Headless Chrome 157 on a loopback copy of that archive: manifest parsed,
    no error, application id at the root of the origin. The same probe on the live site before the change
    answers `no-manifest`.
- [ ] **T05** `[M]` Verify the live site after the deploy.
  - **Covers**: acceptance criteria
  - **Done when**: the live manifest answers 200 with a manifest media type, the four icons answer 200, and the
    owner has installed the site on Android and on iOS.
  - **Needs from owner**: merge the pull request, then install from Chrome on Android and from Safari on an
    iPhone and confirm icon, label and window.
