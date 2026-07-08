---
title: "Teaching My Second Brain to Talk Back"
date: 2026-07-06
---

*Part 1 of a series on wiring my Obsidian vault into Claude.*

A while back I wrote about [falling down the homelab rabbit hole](/posts/home-sweet-homelab/) — one Raspberry Pi turning into a dedicated server turning into fifty-some Docker containers. I'd like to report that the rabbit hole has a bottom. It does not. It just moved up the stack, from containers to something closer to cognition.

This is the first post in a short series about how my Obsidian vault — my "second brain" — stopped being a static pile of Markdown files and started reading and writing itself, with Claude as the intelligence layer in the middle. This post is the map: the *why*, and where the series is headed.

### The embarrassing origin story

I'll be honest about how this started, because the honest version is more useful than the tidy one: I was bad at keeping my vault updated.

Not bad at *capturing* — I'm great at capturing. I was bad at the part where a half-formed thought becomes an actual, well-structured note that future-me can find. What I found myself doing instead was brain-dumping into Claude on my phone, letting it clean the mess into tidy Markdown, and then... manually copying that Markdown into my vault. Every time.

Two things bugged me about that loop:

- **On the way in**, there was a dumb manual copy-paste step standing between "Claude produced a clean note" and "the note is in my vault."
- **On the way out**, all the durable context I was building up in the vault was completely invisible to Claude. Every conversation started from zero.

So the goal formed itself: let Claude write to the vault directly, and let it read from the vault too — with me still in the loop to review what it does. That's the whole thesis. Everything else is plumbing.

### The foundation: PARA in plain Markdown

Before any of the automation, there's the vault itself. I organize it with [PARA](https://fortelabs.com/blog/para/) — four top-level folders:

- `1-Projects` — things with a finish line
- `2-Areas` — ongoing responsibilities
- `3-Resources` — reference material
- `4-Archives` — done and dusted

The important part for this series is that the structure isn't only for me. A few boring conventions — kebab-case filenames, tags as arrays in the frontmatter, consistent `summary` / `status` / `created` / `updated` fields, and Map-of-Content notes to tie related things together — turn the vault into something with a *schema*. And a schema is exactly what you want when a language model is going to be reading and writing your notes. The tidiness I used to skip is the thing that makes the automation possible.

### The one pattern underneath everything

Every piece of this system, no matter how different it looks on the surface, is the same shape:
> **external data → Claude → GitHub commit → human review**

Something comes in (a voice memo, a saved article, a chat). Claude classifies, structures, or summarizes it. The result lands as a commit to the vault's Git repo. And I get to look at the diff before it becomes permanent.

That GitHub step is doing a lot of quiet work. Because every change is a commit, every change is a reviewable, revertable diff — nothing the machine does is a black box, and nothing is unrecoverable. (This is also why I eventually moved the vault's Git hosting off my self-hosted Gitea and onto GitHub — less for anything clever and more because I didn't want a homelab hiccup to be the thing that lost my second brain. More on that later in the series.) Human-in-the-loop isn't a safety bolt-on here; it's the default posture.

### Two halves of the same brain

The system splits neatly into two channels, and those channels are basically the outline for the rest of this series:

- **Capture and batch** — stuff flowing *in* and getting tidied up, sometimes on a schedule while I'm asleep.
- **Interactive** — Claude reading and writing the vault *live*, in the middle of a conversation.

One half tidies while I sleep. The other thinks alongside me while I'm awake. Upcoming posts dig into each: how content gets captured (voice notes, read-later articles), how Claude talks to the vault directly, and the agent that quietly grooms everything on a weekly cadence.

### What it actually buys me

An abstract "AI second brain" is easy to be cynical about, so let me ground it in something real that happened.

This past June I took a 3,000-mile EV road trip — North Dakota, Yellowstone, the Badlands, home. Afterward I wanted a proper trip note. The problem: my calendar had almost nothing. Just the skeleton — the trip's start and end, and the reminders to drop the dogs off at boarding and pick them back up. None of the actual stops.

So the reconstruction became a stitching job: charging receipts out of Gmail, the drive history from the Kia Connect app, timestamps off photos. And it was genuinely messy — a Rivian charging stop's energy had to be *estimated* because the receipt didn't break it out, there was an early odometer gap I couldn't close until I pulled the app data, and one stray Electrify America session refused to line up with the rest. This wasn't magic. It was me and Claude working through scattered exhaust data together.

But what came out the other end was a single, durable `1-Projects` note with the whole trip's charging picture: 23 sessions across three networks, $603.98 all-in, 2.90 miles per kWh, 19.4 cents a mile. Numbers I'll actually reference the next time I plan a trip.

That's the pitch, right there. Not "the AI knows everything," but: *turn scattered, forgettable exhaust into durable, queryable structure* — and make that structure something I can hand back to Claude later. My vault stopped being a filing cabinet and became a collaborator.

I'm aware that's exactly the kind of thing a person fully aboard the second-brain hype train would say. Reader, I have a ticket and a window seat.

Next up: **getting content in** — the many front doors to the vault (a quick word to Claude, a voice memo, a saved article), and the one consolidation I tried to be clever about that isn't working yet.

Until then — happy building.

---

*This post was written with the help of Claude — fittingly, using the very system it describes.*
