---
title: "Feeding the Machine"
date: 2026-07-12
hero_image: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=400&fit=crop&auto=format&q=80"
---

*Part 2 of a series on wiring my Obsidian vault into Claude. [Part 1](/posts/teaching-my-second-brain-to-talk-back/)*

In [the first post](/posts/teaching-my-second-brain-to-talk-back/) I said the system splits into two halves: the capture-and-batch side that pulls stuff in and tidies it, and the interactive side where Claude and I work in the vault together. This post is about the first half — specifically, getting content *in*.

Here's the belief the whole thing rests on: **the moment you capture something and the moment you organize it should never be the same moment.** Every time I've made capture depend on also filing the thing correctly, capture loses. The thought evaporates while I'm deciding which folder it belongs in. So the job I handed to Claude is exactly that deciding — where a thing goes, what it's called, how it's tagged — which frees capture to be as dumb and frictionless as possible.

That means the vault needs more than one front door. Here are the three I use most.

### Front door 1: Just tell Claude

This is the one from the origin story in Part 1, except the copy-paste step is gone now. When a half-formed thought shows up — a project idea, a decision I want to remember the reasoning behind, the useful two sentences that fell out of a longer conversation — I just tell Claude to put it in the vault. It picks the folder, writes a real note with proper frontmatter, and commits it.

This has quietly become my single biggest source of new notes. It's the path I reach for whenever I'm already *in* a conversation and something worth keeping surfaces. (How Claude actually reaches into the vault to do this is the subject of the next post — here I just care that it's the fastest way in.)

### Front door 2: Voice, for when my hands are busy

Some of my best thinking happens when I absolutely cannot type — driving, or out walking the dogs on the acreage. Typing-based capture just doesn't exist in those moments, so those thoughts used to die on the vine.

The voice pipeline fixes that. I record a quick memo on my phone, and it's automatically uploaded to the homelab — no button to push after the fact, no remembering to sync it later. From there, a self-hosted [faster-whisper](https://github.com/SYSTRAN/faster-whisper) instance transcribes it (no audio ever leaving my network); Claude reads the transcript, figures out what it actually is, and structures it into a note; and it commits like everything else. Raw, rambling audio in one end — a filed, titled, tagged note out the other.

This one took the longest to get right, but it's finally working reliably, and it's the piece I didn't know I'd use as much as I do.

### Front door 3: Read-later, for other people's content

The first two doors are for *my* thoughts. This one's for everyone else's. I've long thrown interesting links into [Wallabag](https://www.wallabag.it/), my self-hosted read-later app — which, left alone, is really just a nicer-looking graveyard of tabs I meant to read.

So a [Node-RED](https://nodered.org/) pipeline watches for new saves, hands the article to Claude for a summary, and drops the result into the vault as a resource note. The saved article stops being a someday-maybe and becomes something searchable, summarized, and linkable alongside my own notes. The read-later list finally pays rent.

### The obligatory tech debt

I'd love to tell you all three of these run on one clean, unified pipeline. They do not, and the reason is very on-brand for this blog.

I got ambitious and decided I'd consolidate everything onto [n8n](https://n8n.io/) — one orchestration layer to rule them all. As part of that, I tried to be clever and merge two flows into a single workflow: articles going into the vault *and* recipes going into [Tandoor](https://tandoor.dev/), my recipe manager. They seemed similar enough — save a link, have something smart parse it, route the result somewhere. Turns out "route the result somewhere" was carrying a lot of weight in that sentence, and the combined workflow ran into enough friction that I set it down.

So for now, the read-later pipeline is still happily running on Node-RED, the n8n migration is a "someday," and I have a half-built workflow sitting in a corner judging me. Creating tech debt for future generations, as promised.

### Same shape, every door

Type it, say it, or save someone else's link — underneath, all three doors are the same shape from Part 1: *external data → Claude → GitHub commit → human review.* The front door changes; the pattern doesn't. And because Claude handles the structuring, I get to stay in capture mode without ever context-switching into librarian mode.

Next up: the other half of the brain — how Claude actually reaches into the vault to read and write it live, mid-conversation. That's where the copy-paste step went to die.

Until then — happy capturing.

---

*This post was written with the help of Claude — fittingly, using the very system it describes.*
