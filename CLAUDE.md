# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Hugo source for [techdebtor.io](https://techdebtor.io) — *The Tech Debtor* blog. A
hand-rolled minimal theme (no third-party Hugo theme dependency) built to match the
visual identity of the Ghost site it replaced.

This site serves techdebtor.io. The serving half lives in the separate
`homelab-infrastructure` repo: nginx serves the built site from a volume, and a
small deploy receiver swaps in new builds. n8n polls this repo's GitHub Actions
for the latest successful build artifact and hands it to that receiver, so a green
CI build is what goes live; there is no deploy step or webhook in this repo. Drafts
(`draft: true`) are left out of that build.

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

There is no site test suite; `hugo --minify --gc` succeeding is the correctness
check, along with visually reviewing `hugo server -D` output. Prose is linted with
Vale (next section).

## Prose linting

`.github/workflows/prose.yml` runs [Vale](https://vale.sh) 3.28.1 with two configs.

- **`.vale.ini`, the lenient config**, covers every tracked Markdown file and picks the
  rules by path: posts, pages and READMEs get Vale core, the core of Voices and
  proselint, tuned for this blog's casual first-person voice (exclamations,
  contractions, " - " asides and opening "But"s are fine); `CLAUDE.md` gets the
  model-facing rules (Prompts, Voices, `Repo.SentenceLength`). Only its errors fail CI,
  and the only error on posts is a repeated word. On a pull request, added or changed
  Markdown files are annotated with its warnings; the rest is checked for errors only.
  It passes agent-written prose clean: it is tuned not to fight a person's voice.
- **`.github/vale/new-posts.ini`, the strict config**, looks only for AI-writing
  tells: the `Repo.AITells*` rules (`.github/vale/styles/Repo/`) for the habits of
  agent-written drafts (bold lead-in paragraphs, "Here's the ...", "That's the ...",
  ", which is rather the point", colon reveals, "So the ...", clipped "Fixed."
  sentences, "rather than", "not X" endings, "quietly", "turned out to be") and a few
  package rules for blunter ones (chat openers and closers, throat-clearing, puffery,
  hedges). Each rule was measured against agent-written drafts and the blog's pre-AI
  posts and kept only where it fires on the first and almost never on the second; the
  table is at the top of the config. On a pull request it runs on new posts (posts
  under `content/posts/` the PR adds, and posts that were `draft: true` on the base
  branch), and **any warning from it fails the job**. Published posts are never
  checked with it.

Never reword an old post to satisfy either config: the archive is history. Fix real
typos only.

### Linting a draft

Lint every draft with **both** configs before you call it done. `vale <post>` alone
uses the lenient config and reports nothing for a draft full of AI tells.

Install Vale from its
[3.28.1 release](https://github.com/vale-cli/vale/releases/tag/v3.28.1): check the
archive against `vale_3.28.1_checksums.txt` and unpack it outside the repository.
Then, from the repository root (paths must be relative: the rules are chosen by path):

```bash
python3 .github/scripts/vale_packages.py      # installs the pinned packages; a no-op when current
vale --config=.github/vale/new-posts.ini content/posts/my-new-post.md   # AI tells: CI fails on any
vale content/posts/my-new-post.md             # spelling, typos and style: errors, warnings, suggestions
git ls-files -z '*.md' | xargs -0 vale --minAlertLevel=error   # the whole site, as CI checks it
python -m pytest -q .github/scripts/tests     # the scripts' tests (pytest 9.2.0; Vale on PATH)
vale test --coverage .github/vale/styles/Repo # each Repo rule's own cases
```

Fix a strict-config alert by rewriting the sentence the way its message says, not by
swapping in a synonym: "rather than" becoming "instead of" keeps the tell. When a
flagged phrase is deliberate (a quote, a title, the one place a contrast is the
point), wrap just that passage, each comment on its own line with blank lines around
it:

```markdown
<!-- vale Repo.AITellsRatherThan = NO -->

The paragraph that means it.

<!-- vale Repo.AITellsRatherThan = YES -->
```

### Tuning it

- **Add vocabulary.** When `Vale.Spelling` flags a correct word (a place, a person,
  a tool), add it to `.github/vale/styles/config/vocabularies/Repo/accept.txt`, one
  regular expression per line, in alphabetical order: `[Hh]ealthchecks?` accepts the
  capitalised and plural forms. A case-sensitive entry such as `Traefik` also makes
  `Vale.Terms` warn about other casings; use `(?i)` where any casing is right.
- **Turn a rule off** with `Package.Rule = NO` (or change its level with
  `= suggestion`) in the matching section of `.vale.ini`, with a one-line comment
  saying why. For one passage, use the `<!-- vale Package.Rule = NO -->` and
  `<!-- vale Package.Rule = YES -->` comments shown above.
- **Change an AI-tell rule** in `.github/vale/styles/Repo/AITells*.yml`. Keep each
  regular expression linear-time (bounded repeats, no nested quantifiers), keep its
  `tests:` cases (one sentence it must flag, one from the blog's own posts it must
  pass), and re-measure it against agent-written drafts and the pre-AI posts before
  you widen it: a rule the blog's own voice trips belongs nowhere. Never set one to
  `NO` or `suggestion` in the strict config; `test_strict_config.py` fails if any
  rule it enables stops firing on `.github/vale/fixtures/ai-tells.md`, or one fires on
  `.github/vale/fixtures/human.md`.
- **The packages** (Voices, with its Human, Direct and other voices; proselint;
  Prompts; Std) are pinned in `.github/vale/packages.json` to versioned release zips
  and their sha256, and installed into `.github/vale/styles/`, which is gitignored
  except `Repo/` and the vocabulary. Never run `vale sync` or edit a package's files.
  Every proselint rule ships as an error, so `.vale.ini` sets a level for each one:
  when an upgrade adds a rule, give it a level there too, and run Vale over the site
  before and after.

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
