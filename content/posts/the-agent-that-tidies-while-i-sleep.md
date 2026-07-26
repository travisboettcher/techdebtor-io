---
title: "The Agent That Tidies While I Sleep"
date: 2026-07-26
draft: false
hero_image: "https://images.unsplash.com/photo-1667264501379-c1537934c7ab?w=800&h=400&fit=crop&auto=format&q=80"
---

*Part 4 of a series on wiring my Obsidian vault into Claude. [Part 1](/posts/teaching-my-second-brain-to-talk-back/) · [Part 2](/posts/feeding-the-machine/) · [Part 3](/posts/a-vault-that-talks-back/)*

[Last post](/posts/a-vault-that-talks-back/) was about the interactive side — Claude in the vault while I'm sitting right there, driving. This final post is about the opposite: the part of the system that runs when I'm *not* there. The agent that quietly grooms the whole vault on a schedule, and the guardrails that let me sleep while it does.

### The maintenance I'd never actually do

Here's the dirty secret of every second brain: capturing notes is the fun part, and maintaining them is the part that quietly rots. Links go stale. A note gets written and never connected to the three related notes it obviously belongs with. Summaries drift out of date. Half-finished thoughts sit in `1-Projects` long after the project finished. None of this is hard to fix — it's just tedious enough that I will, reliably, never do it.

So I don't. The Vault Agent does. On a regular cadence it works through the vault: enriching notes, tightening summaries, surfacing connections between things that should be linked, and flagging the stuff that's gone stale. It's the boring librarian work I was never going to get to, running on its own while I'm asleep or at my actual job.

### Running on n8n

The scheduling and glue for this lives in [n8n](https://n8n.io/), which has quietly become the orchestration backbone for most of my vault automation. (The weekly agent actually started life as a GitHub Actions workflow; consolidating it onto n8n alongside everything else is part of why I keep reaching for n8n as the one place all these jobs live.) n8n handles the *when* and the *plumbing*; Claude handles the *thinking*; and — as always — GitHub handles the *record*.

### I dispose, it proposes

This is the part that matters most, so I'll say it plainly: the agent does not silently rewrite my brain overnight.

It follows the same core pattern as everything else in this series — *external data → Claude → GitHub commit → human review.* The agent's work shows up as commits I can read as diffs. Where I've built up enough trust in a particular kind of change, I let it flow through automatically; everything else waits for me to glance at it and approve. So "while I sleep" the agent *proposes*, and in the morning I *dispose*. My vault never changes in a way I can't see and can't undo.

### The guardrails

Now the eyebrow-raiser I promised in Part 3. Two things about this system should make a careful person nervous, and they compound:

1. I've given an AI **write access to my second brain.**
2. I'm feeding that same system **untrusted content from the open internet** — saved articles, and eventually email.

That second one is the real hazard. A read-later article isn't just data; it's text, and text can contain instructions. A malicious page could try to smuggle a "ignore your previous task and do this instead" into the pipeline — a prompt-injection attack aimed squarely at the thing with commit access to my notes.

The defenses are boring, which is how I like them. Untrusted content gets **pre-summarized** before it goes anywhere near a step that can act, and it gets **wrapped in an envelope** that clearly marks it as data to be processed, not instructions to be followed. And behind all of that sits the same backstop as everywhere else: nothing the machine does reaches my vault without passing through a commit I can review and revert. Defense in depth, with the human as the last layer.

I won't pretend it's airtight — no one honestly can — but the combination of treating external text as radioactive-until-summarized and keeping every write reviewable is what lets me point automation at my notes and still sleep fine.

### Still plenty of tech debt

In the spirit of this blog, the honest status: this is not finished, and it never will be. The next thing on the list is hardening the write path for adding notes from my phone — the auth around it needs to be tighter before I fully trust it out in the world. There's always another rough edge. That's sort of the point of the whole enterprise.

### The whole brain, end to end

That's the series. Four posts, one system:

- **Capture** — many frictionless front doors in: a quick word to Claude, a voice memo, a saved article ([Part 2](/posts/feeding-the-machine/)).
- **Interactive** — Claude reading, writing, and answering questions in the vault live ([Part 3](/posts/a-vault-that-talks-back/)).
- **Batch** — the agent grooming it all on a schedule, safely (this post).

Underneath every one of them: *external data → Claude → GitHub commit → human review.* One pattern, wearing four different outfits.

When I started, I just wanted to stop copy-pasting Markdown into Obsidian. What I ended up with is a vault that reads itself, writes itself, tidies itself, and hands me back my own context whenever I ask for it. It stopped being a place I store things and became a place I think. I remain, as established, fully aboard the hype train — and now the train maintains its own tracks.

Thanks for reading along. Until next time — happy note-taking.

---

*This post was written with the help of Claude — fittingly, using the very system it describes.*
