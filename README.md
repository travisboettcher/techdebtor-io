# techdebtor-io

Hugo source for [techdebtor.io](https://techdebtor.io) — *The Tech Debtor* blog.

## Status

This repo currently holds a Hugo scaffold with a small custom theme (no
external theme dependency) and a CI build-check workflow. It does not yet:

- Serve any real traffic — techdebtor.io is currently powered by Ghost
  (self-hosted, in the `homelab-infrastructure` repo). A separate,
  abandoned side project (`techdebtor-site`) also exists but never replaced
  Ghost in production and isn't authoritative for content or design.
- Contain the real blog archive. Only one post is migrated so far
  (`content/posts/hello-world.md`), carried over from `techdebtor-site`'s
  Ghost-export attempt as a placeholder/starting point. Its body still
  describes that earlier (non-live) migration attempt and will need an
  editorial pass once the real Ghost content is available.
- Deploy anywhere. CI only builds and uploads an artifact for inspection.

### Roadmap

- [x] Hugo site scaffolded with a minimal custom theme
- [x] CI build-check workflow
- [ ] Migrate the real Ghost archive (blocked on getting the actual export
      or content — not reachable from this environment)
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
