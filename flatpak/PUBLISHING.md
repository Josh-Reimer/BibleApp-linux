# Publishing BibleApp

Notes on whether to put this app on Flathub, and what it takes.

## Do you need Flathub?

Flathub matters only if you want *other people* to get updates automatically.
There are three realistic end states:

| Option | Install | Auto-updates | Cost |
|---|---|---|---|
| Source (`git clone`) | User needs `python3-tk` | None | Nothing |
| CI `.flatpak` bundles | Download, `flatpak install --user` | **None** | Nothing (already working) |
| A repo — Flathub or self-hosted | One click / `remote-add` | Yes | Review queue, or run your own repo |

The bundles produced by CI today solve *easy install*, not *automatic updates*.
A bundle is a one-shot artifact with no remote behind it, and updates only
arrive from a remote the client polls.

Self-hosting a repo (ostree + GPG signing on GitHub Pages) is more ongoing work
than Flathub's one-time review, and asks every user to trust a URL they have
never heard of. So if updates matter, Flathub is the sensible target.

**The real cost is not submission — it is the standing obligation.** Runtimes go
EOL roughly annually. When `org.freedesktop.Platform//24.08` is retired you are
expected to bump it or the app goes stale, and strangers will file issues. If
that sounds tiresome for a personal Bible reader, stopping at the CI bundles
with a README link is a perfectly respectable place to land.

## Blocking work, in order

- [ ] **Add a LICENSE file.** Genuinely blocking. `project_license` in the
      metainfo currently reads `LicenseRef-proprietary`, which is what having no
      LICENSE legally means. Pick a license (MIT, GPL-3.0-only, …), commit it,
      and set `project_license` to the matching SPDX id.

- [ ] **Settle the app ID.** The biggest review risk. Flathub wants
      `io.github.<user>.<repo>`; the repo is `BibleApp-linux` but the manifest
      says `io.github.josh_reimer.BibleApp`. Cleanest fix is renaming the repo
      to `BibleApp` — the `-linux` suffix is inaccurate now that it runs on
      macOS too. **Do this before publishing; the ID is permanent afterwards.**
      A rename means updating the ID in four filenames plus the manifest,
      desktop entry, metainfo, and CI workflow.

- [ ] **Tag a release and pin it.**

      ```
      git tag -a v1.0.0 -m "First release"
      git push origin v1.0.0
      git rev-parse v1.0.0
      ```

      The Flathub manifest may not build a working tree. Replace the app
      module's source with the pinned revision:

      ```yaml
      sources:
        - type: git
          url: https://github.com/Josh-Reimer/BibleApp-linux.git
          tag: v1.0.0
          commit: <sha from git rev-parse>
      ```

- [ ] **Check the screenshot resolves.** The metainfo points at a
      `user-attachments` URL from the README. If Flathub's bot cannot fetch it,
      commit the PNG to the repo and use its `raw.githubusercontent.com` URL.

## Lint before submitting

Flathub runs `flatpak-builder-lint` on every submission. Run the same linter
yourself and fix what it reports — far cheaper than waiting on a human:

```
flatpak install -y flathub org.flatpak.Builder
flatpak run --command=flatpak-builder-lint org.flatpak.Builder \
    manifest flatpak/io.github.josh_reimer.BibleApp.yml
flatpak run --command=flatpak-builder-lint org.flatpak.Builder \
    appstream flatpak/io.github.josh_reimer.BibleApp.metainfo.xml
```

## Submitting

1. Fork <https://github.com/flathub/flathub>.
2. Create a branch named after the app ID, containing the manifest (with the
   pinned git source) and the metainfo.
3. Open a PR **against the `new-pr` branch**, not `master`.
4. A bot builds it for x86_64 and aarch64.
5. A volunteer reviews it. Expect days to weeks — this is unpaid work.
6. On merge you get your own `flathub/io.github.josh_reimer.BibleApp` repo with
   commit access; pushes there publish automatically.
7. Optionally verify ownership so the listing shows the checkmark linking it to
   your GitHub account.

## Known review risks

- **`--socket=x11`.** The linter nudges submissions toward `fallback-x11`, but
  Tk 8.6 is X11-only with no Wayland backend, so plain `x11` is correct here.
  Be ready to say so in the review thread.
- **Building Tcl, Tk, and CPython in the manifest.** Reviewers prefer runtime
  dependencies where they exist. There is no Tk in the freedesktop runtime and
  Python's `_tkinter` cannot be built without it, so this is unavoidable —
  see the notes in `CLAUDE.md`.

## Links

- Flathub submission docs: <https://docs.flathub.org/docs/for-app-authors/submission>
- App ID requirements: <https://docs.flathub.org/docs/for-app-authors/requirements>
- AppStream metainfo guide: <https://docs.flathub.org/docs/for-app-authors/metainfo-guidelines/>
