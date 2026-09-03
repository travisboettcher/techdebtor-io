---
title: "Designing a Language for a Machine to Write"
date: 2026-09-24
draft: true
tags: ["Home Lab", "Rust"]
---

When I started sketching `hll` I already knew I wasn't going to be the one writing most of the `.hll` files. I write about four services a year - Claude and I write rather more than that together, and I had just spent a month watching it hand me Compose blocks, so the design question I actually had was not "what do I want to type" but "what will a model get right on the first try."

That turns out to change a few things, and not the ones I expected.

### What it changed in the grammar

So what does designing for a model actually change? The obvious moves came first, and they're the least interesting. Keep the shapes close to Compose and YAML, since that's what's already dense in anything a model has read. Prefer named fields over positional ones, so nothing depends on argument order (there is no `expose(80, "host", true)` anywhere in this language, and there never will be). Put the fleet-wide conventions in a `defaults` template that anybody can open and read, rather than leaving them as things I happen to know.

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

Those two produce byte-identical output. I kept the `as` sugar because it's much nicer to write in the common case - which is an argument about my own convenience, made while writing a language for something else to use. (I still think it was the right call. I also notice it's the first rule I broke.)

### The loop matters more than the grammar

Here's what I underrated. Grammar choices are one-shot - the model either guesses your syntax or it doesn't. The compiler running in a loop is worth far more, because a wrong guess gets corrected in seconds instead of surviving into my homelab.

`hllc check` runs the whole pipeline, writes nothing, and exits non-zero. That's the whole mechanism. Something writes an `.hll` file, `check` says what's wrong, it tries again.

Which makes the wording of a diagnostic load-bearing in a way it isn't when only a person reads it. Misspell a field and `hllc` doesn't just refuse, it names the repair:

```
a.hll: 2:3: unknown field "imag" on `service` — if `imag` is a Compose key
with no `hll` field yet, pass it through with `raw { imag: ... }`
```

Put a comma somewhere Traefik would misread it, and you get told what to write instead:

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

Field names are checked. Values mostly aren't, and that's a real gap:

```
service s {
  image "n"
  restart always-on
}
```

`always-on` is not a Docker restart policy. It compiles clean, and the nonsense goes straight through into the YAML for Compose to complain about later! A model inventing a plausible-looking value is exactly the failure I should be catching, and right now the field-name checking that caught `imag` does nothing here at all.

That, plus `raw` and `labels` from post 2, is the honest shape of it: `hll` is good at "that field doesn't exist" and bad at "that value is wrong."

### One more to go

Next post is the other half of this, and the one with the numbers in it - what building 33,000 lines of Rust with an agent in under three weeks actually looked like, including the parts I'd rather not have written down. There's also an `init` command I keep sketching, which would generate the Traefik configuration itself rather than just the services behind it, but that one can wait until it exists.

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about.*
