# techdebtor-io

Hugo source for [techdebtor.io](https://techdebtor.io) — *The Tech Debtor* blog.

## Status

This repo holds the full real content archive (10 posts + About page,
migrated from a Ghost export) on a hand-rolled Hugo theme built to match the
original Ghost site's style guide (nav, read time, tag badges, dark/light
toggle). It does not yet:

- Serve any real traffic — techdebtor.io is currently powered by Ghost
  (self-hosted, in the `homelab-infrastructure` repo). A separate,
  abandoned side project (`techdebtor-site`) also exists but never replaced
  Ghost in production and isn't authoritative for content or design.
- Deploy anywhere. CI only builds and uploads an artifact for inspection.

Known gaps: no images were part of the export, so bracketed placeholders
(e.g. `*(embedded Spotify podcast episode)*`) remain as literal text rather
than real embeds/photos. No LinkedIn URL is set in `hugo.toml` — only GitHub
was confirmed, so the footer omits it until a real URL is supplied.

### Roadmap

- [x] Hugo site scaffolded with a minimal custom theme
- [x] CI build-check workflow
- [x] Migrate the real Ghost archive (10 posts + About page)
- [x] Theme parity with the Ghost "Smart" theme's style guide (nav, read
      time, tag badges, dark/light toggle)
- [ ] Deployment pipeline (build + deploy to the homelab, replacing Ghost) —
      will live in `homelab-infrastructure`, in a future task

## Local development

```bash
hugo server -D
```

Visit http://localhost:1313. `-D` includes draft posts.

## Adding a post

```bash
hugo new posts/my-new-post.md
```

Fill in `title`, `tags`, and `summary` in the frontmatter, then flip
`draft: false` when ready to publish.

## Prerequisites

- [Hugo](https://gohugo.io/) extended, version pinned in
  `.github/workflows/build.yml` (`HUGO_VERSION`).

## CI

`.github/workflows/build.yml` runs on every push and on PRs to `main`: it
installs the pinned Hugo version, runs `hugo --minify --gc`, and uploads the
built `public/` directory as a workflow artifact. This is a build-check
only — it does not deploy anywhere yet.
