---
title: "Designing a Language for a Machine to Write"
date: 2026-09-24
draft: true
tags: ["Home Lab", "Rust"]
---

When I started sketching `hll` I already knew I wasn't going to be the one writing most of the `.hll` files. I write about four services a year - Claude and I write rather more than that together, and I had just spent a month watching it hand me Compose blocks, so the design question I actually had was not "what do I want to type" but "what will a model get right on the first try."

That turns out to change a few things, and not the ones I expected.

### What it changed in the grammar

So what does designing for a model actually change? The obvious moves came first, and they're the least interesting. Keep the shapes close to Compose and YAML, since that's what's already dense in anything a model has read. Prefer named fields over positional ones, so nothing depends on argument order (there is no `expose(80, "host", true)` anywhere in this language, and there never will be). Put the shared conventions in a `defaults` template that anybody can open and read, rather than leaving them as things I happen to know (one per entry file, as post 2 covers - it's the one template imports can't share).

Then there was the rule I wrote down and did not keep - **one canonical way to say each thing.** Multiple valid spellings of the same config produce inconsistent generations, and inconsistent generations are how I end up back at my drifting Compose files from post 1. Good rule. Here's `hll` failing it:

```
service s {
  image "n"
  expose 80 as "h.example.com"
}
```

```
service s {
  image "n"
  expose 80
  router {
    host: "h.example.com"
  }
}
```

Those two produce byte-identical output. I kept the `as` sugar because it's much nicer to write in the common case - which is an argument about my own convenience, made while writing a language for something else to use. (I still think it was the right call. It's also not the only place I broke that rule - the shorthand that lets me write `image "nginx"` instead of `image { ref: "nginx" }` breaks it everywhere else.)

### The loop matters more than the grammar

Here's the part I got right for the wrong reasons. Grammar choices are one-shot - the model either guesses your syntax or it doesn't - while the compiler running in a loop corrects a wrong guess in seconds, before it ever reaches my homelab. My notes did rank tooling above grammar at the time, under a heading that says so in as many words. What they got wrong was which tooling.

`hllc check` runs the whole pipeline, writes nothing, and exits non-zero when anything is wrong. That's the whole mechanism. Something writes an `.hll` file, `check` says what's wrong, it tries again.

Which makes the wording of a diagnostic load-bearing in a way it isn't when only a person reads it. Misspell a field and `hllc` doesn't just refuse, it points at a way out:

```
a.hll: 2:3: unknown field "imag" on `service` — if `imag` is a Compose key
with no `hll` field yet, pass it through with `raw { imag: ... }`
```

Better still, put a comma somewhere Traefik would misread it and you get told exactly what to write instead:

```
b.hll:6:18: `router.entrypoints` must not contain ',' — it would change the
meaning of the generated Traefik label — `entrypoints` is a list, so write
the entry points as separate items (`entrypoints web, websecure`) and let
`hllc` join them
```

I wrote both of those hints for me, on the theory that future-me would be confused. They work just as well for a model, and for the same reason - the fix is in the message, so nobody has to go read the spec to make progress. That's the whole trick, and it turns out not to be an AI trick at all!

### What I planned and didn't build

My design notes are very confident that the errors should be structured and machine-readable - JSON with a line, a field, an expected type. None of that exists. `hllc` emits prose, and the project's own versioning rules say the exact wording is explicitly *not* a stable contract, so nothing should be parsing it anyway. What is stable is the exit code - which turns out to be the only part the loop actually needs (a humbling result for the design notes).

Two more from the same notes, both still just notes:

- an MCP server wrapping `validate_config` and `generate_compose`, so Claude could call the compiler directly instead of me relaying errors by hand; and finally,
- the `explain` command from post 1, which would answer "which tier set this value" for any field in the output.

### Where it still can't help

Field names are always checked. Values get checked where the legal set is short and closed, so I get told off for a bad router protocol, a bad `depends_on` condition, or anything that turns into a Traefik label. Everything else I am on my own for. `restart` is the gap that bothers me most:

```
service s {
  image "n"
  restart always-on
}
```

`always-on` is not a Docker restart policy. It compiles clean, and `docker compose config` won't flag it either - you find out when the daemon refuses to start the container.

There's a worse version of this, and I found it by reading my own error message properly. That unknown-field hint is generic on purpose: it suggests `raw` for every field it doesn't recognize, because it can't tell a Compose key I haven't modelled yet from a plain typo. So take its advice literally on `imag`, and this is what you get:

```
service s {
  image "n"
  raw {
    imag: "nginx"
  }
}
```

`hllc` accepts that. Compose does not:

```
validating out.yaml: services.s additional properties 'imag' not allowed
```

My own compiler talked me out of a caught error and into an uncaught one! That's the honest shape of `hll` right now - solid on "that field doesn't exist", weak on "that value is wrong", and weakest exactly where the escape hatch meets a model that will cheerfully invent a plausible-looking value.

### One more to go

Next post is the other half of this, and the one with the numbers in it - what building 33,000 lines of Rust with an agent in under three weeks actually looked like, including the parts I'd rather not have written down. There's also an `init` command I keep sketching, which would generate the Traefik configuration itself rather than just the services behind it, but that one can wait until it exists.

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about.*
