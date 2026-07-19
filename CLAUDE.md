# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Hugo source for [techdebtor.io](https://techdebtor.io) — *The Tech Debtor* blog. A
hand-rolled minimal theme (no third-party Hugo theme dependency) built to match the
visual identity of the original Ghost site it's migrating from. See README.md for
current migration status and roadmap.

This site does not yet serve real traffic — techdebtor.io is currently powered by a
self-hosted Ghost instance (in the separate `homelab-infrastructure` repo). CI here
only builds and uploads an artifact for inspection; there is no deploy step yet.

## Commands

```bash
hugo server -D       # local dev server at http://localhost:1313, -D includes drafts
hugo --minify --gc   # production build (what CI runs), outputs to public/
hugo new posts/my-new-post.md   # scaffold a new post from archetypes/posts.md
```

Hugo version is pinned in `.github/workflows/build.yml` (`HUGO_VERSION`) — use the
extended edition matching that version. Older Hugo versions (e.g. distro-packaged
apt builds) can fail on `.Site.Language.Locale` in `layouts/_default/baseof.html`
with a `can't evaluate field Locale` error; this is a Hugo-version mismatch, not a
bug in the templates — install the pinned extended version instead of patching
templates around it.

There is no test suite or linter; `hugo --minify --gc` succeeding is the correctness
check, along with visually reviewing `hugo server -D` output.

## Architecture

- **Content** (`content/posts/*.md`): each post is Markdown with TOML/YAML front
  matter — `title`, `date`, `draft`, `tags`, `summary`, and `hero_image` (an image
  URL). `draft: true` posts are excluded from production builds and only show with
  `hugo server -D`.
- **Templates** (`layouts/`): `_default/baseof.html` is the shared shell (head, header
  partial, `{{ block "main" }}`, footer partial, theme-toggle script). `index.html`
  (site home) and `_default/single.html` (individual posts) both render
  `.Params.hero_image` when present — home as a card thumbnail (`post-card-image`),
  single post as a full-width header image (`post-hero-image`). `_default/list.html`
  handles taxonomy/section listing pages (e.g. `/tags/`). `_default/page.html` handles
  standalone pages like `content/about.md`.
- **Styling**: a single hand-written stylesheet at `static/css/main.css` (no CSS
  framework/preprocessor) plus `static/css/chroma.css` for syntax highlighting
  (`pygmentsUseClasses = true` in hugo.toml). Dark/light theme toggle is plain JS in
  `static/js/theme-toggle.js`.
- **Site config** (`hugo.toml`): nav menu, taxonomies (`tags`), and site-wide params
  (author, description, resume/GitHub/LinkedIn URLs used in the footer) all live here
  rather than in template code.

When adding a new front-matter field that should affect rendering (like
`hero_image`), remember there are two places posts are rendered — the home page
listing (`layouts/index.html`) and the single post view
(`layouts/_default/single.html`) — and keep both in sync unless the field is
intentionally listing-only or post-only.
