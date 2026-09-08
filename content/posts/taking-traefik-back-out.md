---
title: "Taking Traefik Back Out"
date: 2026-10-01
draft: true
tags: ["Home Lab", "Rust"]
---

Two posts ago I said routing wasn't part of my language - and that it hadn't always been true. This is that story. The question sat in my issue tracker for three weeks; the deletion itself took four days, and to get it out I had to ship five features that had nothing to do with it.

### The test, run backwards

I ask one question of everything I'm tempted to build in: would it still make sense to somebody whose homelab looks nothing like mine? `image`, `expose`, `volume`, `depends_on` - those all pass, because they're Compose and everybody has Compose. `router { host: "web.techdebtor.io" }` doesn't. I only get anything out of it because I chose [Traefik](https://traefik.io/traefik/) years ago - so what I had really done was write one vendor's data model into my grammar.

Easy enough to say. Much less comfortable when I ran it backwards, over a feature that already worked and that my own documentation already taught. I had been perfectly happy with it a month earlier!

### The plugin I didn't have to build

The question I wrote down back in August was whether `hll` had a backend abstraction at all - some flag or opt-in that would let me pick my proxy. I sketched two designs for it, and quite liked both of them.

I built neither. There's no extension point in my compiler, no registry, no plugin API. Routing is templates over labels. That's the same mechanism my own files were already using for the [Authentik](https://goauthentik.io/) middleware and the PUID pairs - for weeks, in front of me. I had asked for a plugin architecture, and my answer was that I'd already written one. It just had a hard-wired competitor standing in front of it, which is exactly why I couldn't see it was enough.

### What the deletion turned up

Here's the part I'd actually tell someone else about - and I did not see it coming.

Nothing about my `router` was self-contained. It had been leaning on things my generic core couldn't do - without ever mentioning it - so I had to build every one of them before I could delete the thing I was aiming at:

- putting a parameter inside a string, rather than filling a whole value;
- `use "std:traefik"` for modules that ship in the binary;
- reading a value back out of a declaration, so a template can ask a network what its real Docker name is;
- passing a list to a template; and finally,
- the list-valued label rule I showed you two posts ago.

Deleting the specific feature is what forced the general ones to exist. My Traefik integration had been acting as a shim over five gaps in my own language, and I couldn't see a single one of them while the shim sat there!

So that's my argument, and I think it holds well past little homelab languages. A vendor integration in your core doesn't only couple you to the vendor. It hides the general features you should have built instead, because the specific one is already covering for them. All five of mine are open to anybody's templates now (for infrastructure I've never run and my compiler has never seen).

### The one the documentation found

Interpolation used to cover a service's own name and nothing else. So both of the spellings I'd reach for to put a hostname in a rule failed, and they failed differently. `{{host}}` gave me an error, which is fine. This one was worse:

```
template t(host) {
  labels { "traefik.http.routers.{{name}}.rule": "Host(`$host`)" }
}
```

That compiled, and wrote ``Host(`$host`)`` straight into the label, which Traefik reads as a router matching a machine literally named `$host`. A rule that looks right, compiles clean, and never matches a single thing for the rest of its life!

It was harmless while my `router` existed, since nobody hand-writes a rule when a built-in will do it for them. The moment my templates became the only way to write one, it turned into a live footgun - so I had to fix it before anything else could move. It still compiles today (breaking everybody's old files over it struck me as rude), but now it tells you:

```
rule.hll:2:50: warning: `$host` inside a string is not a parameter reference — it is
emitted verbatim; write `{{host}}` to interpolate template `t`'s `host` here
```

I found that while writing the documentation, not while testing it. That keeps happening to me on this project. My docs have caught more design smells than my test suite has (a sentence I'd rather not examine closely).

The migration nearly took something out with it, too. Composing two middleware templates onto one service used to work, and written as plain labels both of them set the same key and collide. I caught that by moving my own files over and watching it break, which I'd now call a decent argument for migrating something real before calling a feature finished.

### The bill

The removal landed as one commit - 1,898 lines added, 11,166 taken away, across a hundred files. My label-computing module went from about 2,570 lines down to 195. The whole workspace is smaller than it was a month ago, which is not a shape I ever expected a month of my own work to have!

It cost me something real, and I've already owned up to that - my compiler used to understand what a routing rule meant, and now it just sees a string. I would make the trade again tomorrow, and I expect I'd make it faster. But the thing I'd actually tell you is the other one. I learned more about what my language was missing by taking one feature out than I did from putting any of them in.

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about.*
