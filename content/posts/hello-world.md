---
title: "Hello World"
date: 2026-04-18
draft: false
tags: ["meta"]
summary: "Welcome to the new techdebtor.io — now powered by plain markdown and nginx."
---

# Hello World

Welcome to the new Tech Debtor! This site has been rebuilt from the ground up as a static, client-rendered blog.

## What changed?

Previously this site ran on [Ghost](https://ghost.org/), a full-featured publishing platform. Ghost is great software, but for a low-traffic personal blog it was overkill — a Node.js CMS backed by MySQL, with features like newsletters and memberships that I never used.

The new site is radically simpler:

- **Posts are markdown files** committed to a git repository.
- **The browser does the rendering** using [marked](https://marked.js.org/) and [highlight.js](https://highlightjs.org/).
- **Nginx serves the files** from a Docker container on my homelab.
- **No database, no CMS, no build step.**

## Why?

Three reasons:

1. **Simplicity.** The entire site is a handful of HTML, CSS, and JS files plus markdown posts. Nothing to patch, no database to back up, no admin panel to secure.

2. **Portability.** Everything is in version control. The site can be served from any static file host.

3. **Writing workflow.** I can author posts in any text editor, preview them locally, and publish by pushing a commit.

## What's next?

More posts about homelab adventures, software engineering, and whatever else catches my interest. Stay tuned.
