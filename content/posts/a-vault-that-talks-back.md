---
title: "A Vault That Talks Back"
date: 2026-07-07
draft: true
hero_image: "https://images.unsplash.com/photo-1519337265831-281ec6cc8514?w=800&h=400&fit=crop&auto=format&q=80"
---

*Part 3 of a series on wiring my Obsidian vault into Claude. [Part 1](/posts/teaching-my-second-brain-to-talk-back/) · [Part 2](/posts/feeding-the-machine/)*

The last two posts covered the capture side — the various front doors that get content *into* the vault. This one is about the other half of the brain: Claude reaching into the vault directly, reading and writing it live, in the middle of a conversation. This is the half that finally solved both halves of the problem I complained about back in [Part 1](/posts/teaching-my-second-brain-to-talk-back/).

The whole thing runs on a small [MCP](https://modelcontextprotocol.io/) server I built and host at `mcp.techdebtor.io/vault`. I'm going to stay concept-level here and assume you already know roughly what MCP is; if not, the short version is that it's the plumbing that lets Claude call out to tools I define. In this case, the tools all point at one thing: my vault.

It does three things.

### It can read

The first thing the connector buys me is the thing I said was missing in Part 1: my durable context is no longer invisible to Claude. It can list folders and pull up specific notes, which means a conversation can start from what I already know instead of from nothing. I can reference "the road trip note" or "my homelab infrastructure area" and Claude can actually go read it, rather than me re-explaining my own life every single time.

That sounds small. It is not small. It's the difference between talking to a very smart stranger and talking to someone who's read your notebook.

### It can write

The second thing is where the copy-paste step went to die.

When Claude writes a note now, it doesn't hand me Markdown to file myself — it creates the note in the right folder, with real frontmatter, and commits it straight to the vault's GitHub repo. The manual "copy this into Obsidian" step from the origin story is just... gone. This is the single change that made the whole system feel less like a clever demo and more like infrastructure I actually rely on.

A fun and slightly recursive detail: the drafts of this very series went into my vault through this exact connector. I'd be describing the write path in a conversation, and the description itself would get filed as a note by the thing it was describing.

### It can be asked

The third capability is my favorite, because it's the least mechanical. Reading a note requires me to know which note I want. But often I don't — I just have a question. *What do I know about X?*

For that, the connector exposes a semantic-search path backed by [Khoj](https://khoj.dev/), which does retrieval across the whole vault rather than fetching a single file by name. I can ask a fuzzy question and get an answer synthesized from whatever notes are actually relevant, wherever they happen to live. It turns the vault from a filing cabinet I retrieve *from* into something I can genuinely *ask*.

### Still my vault, still my call

It's worth being clear about one thing, because "I gave an AI write access to my second brain" is a sentence that should raise an eyebrow: none of this removes me from the loop.

Every write is a commit. Every commit is a diff I can look at, and revert if I don't like it. The connector makes Claude a very capable collaborator in the vault, but it's still my vault and still my call — the review step from the [core pattern](/posts/teaching-my-second-brain-to-talk-back/) is doing exactly as much work here as it does everywhere else in the system. Handing something this much reach into your notes deserves some real guardrails, and those guardrails are most of what the *next* post is about.

### Both problems, one connector

Back in Part 1 I had two complaints: on the way *out*, my context was invisible to Claude; on the way *in*, filing was a manual chore. One connector closed both: the vault can now be read, written, and asked — three things it could never do before it learned to talk back.

Next up, the last post in the series: the batch side — the agent that grooms the whole vault on a schedule while I'm asleep — and the guardrails that make me comfortable letting any of this near my notes in the first place.

Until then — happy asking.

---

*This post was written with the help of Claude — fittingly, using the very system it describes.*
