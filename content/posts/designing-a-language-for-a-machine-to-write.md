---
title: "Designing a Language for a Machine to Write"
date: 2026-09-24
draft: true
tags: ["Home Lab", "Rust"]
---

I write about four new services a year. Claude and I write rather more than that together, and by the time I started sketching `hll` I had spent a month watching it hand me [Docker Compose](https://docs.docker.com/compose/) blocks. So I stopped asking what I wanted to type, and started asking what a model would get right on the first try.

I want to be careful here, because this is the part of the project I was most pleased with - and also the part I got most wrong.

### Grammar

The obvious moves came first, and I think they're the least interesting:

- keep the shapes close to Compose and YAML, since that's what's already dense in anything a model has read;
- name every field, so nothing depends on argument order (there is no `expose(80, "host", true)` in this language, and I'm glad of it); and finally,
- put my shared conventions in a `defaults` template anyone can open and read, instead of leaving them as things I happen to know.

Then there's the rule I wrote down and did not keep: **one canonical way to say each thing.** I believed that one. Multiple spellings of the same config give you inconsistent generations, and inconsistent generations are how I ended up with the drifting Compose files I complained about in [post 1](/posts/i-wrote-a-language-for-my-homelab/). Here I am breaking it. First the sugar:

```
service s {
  image "n"
  expose 80 as "h.example.com"
}
```

And here's the longhand, which I also kept:

```
service s {
  image "n"
  expose 80
  router {
    host: "h.example.com"
  }
}
```

Those two produce byte-identical output - I checked, and I was slightly hoping they wouldn't! I kept the sugar because I like writing it, which is an argument about my own convenience that I made while designing a language for something else to use. (I still think it was right. It's also not the only place I broke the rule - the shorthand that lets me write `image "nginx"` instead of `image { ref: "nginx" }` breaks it everywhere.)

### The loop matters more than the grammar

So which of those actually mattered? Not the grammar, as it turns out. My grammar choices are one-shot - a model either guesses the syntax or it doesn't, and I only get to influence that once, months earlier, while writing a spec. The compiler is different, because the compiler gets to answer back.

`hllc check` compiles a file, writes nothing to disk, and fails loudly if anything is wrong - that's the entire mechanism, and it turned out to be enough. Claude writes a file, `check` complains, Claude fixes it, and I never see the three bad versions in between!

I'll give my design notes credit, too. They ranked the tooling ideas above the grammar ideas at the time, under a heading that says so in as many words. What I got wrong was which tooling.

Because if the compiler is going to answer back, what it *says* starts to matter enormously. My favorite one in the whole compiler catches a comma that would change a Traefik label's meaning without telling anyone - and rather than just refusing, it tells me exactly what to write instead:

```
b.hll:6:18: `router.entrypoints` must not contain ',' — it would change the
meaning of the generated Traefik label — `entrypoints` is a list, so write
the entry points as separate items (`entrypoints web, websecure`) and let
`hllc` join them
```

I wrote that for me, on the theory that future-me would be baffled. It works just as well on a model, and I never had to change a word of it! The repair is in the message, so nobody has to go and read the spec to make progress. That's the whole trick, and I don't think it's really an AI trick.

### What I planned and didn't build

My notes are very confident that the diagnostics should be structured and machine-readable, JSON carrying a line and a field and an expected type. I never built any of it. `hllc` prints prose, and my own versioning rules say the exact wording isn't a stable contract, so nothing should be parsing it anyway. What I promise is the exit code, and the exit code is the only part the loop ever needed (a humbling result for the notes).

Two more I still haven't written: an MCP server, so Claude could call the compiler directly instead of me relaying errors by hand, and the `explain` command I keep promising, which would tell me which tier set a given value.

### Values

Field names are always checked. Values get checked where the legal set is short and closed, so I get told off for a bad router protocol or a bad `depends_on` condition. Everywhere else I'm on my own, and `restart` is the gap that bothers me most:

```
service s {
  image "n"
  restart always-on
}
```

`always-on` isn't a Docker restart policy - but it compiles clean, and `docker compose config` won't flag it either, so I find out about it when the daemon refuses the container.

Then there's a worse one, which I found by reading my own error message properly. The unknown-field hint is generic on purpose - it offers `raw` for anything it doesn't recognize, because it can't tell a Compose key I haven't modeled yet from a plain typo. So I took its advice on a typo:

```
service s {
  image "n"
  raw {
    imag: "nginx"
  }
}
```

`hllc` accepts that happily! Compose does not:

```
validating out.yaml: services.s additional properties 'imag' not allowed
```

My own compiler talked me out of a caught error and into an uncaught one. I'm oddly delighted by that, and I'd never have found it if I hadn't gone looking for something to admit.

### One more to go

The last post is the other half of this one - and the one where I have to account for myself, since that's three weeks, an agent, and 33,000 lines of Rust I did not type. The [design doc](https://github.com/travisboettcher/hl-lang/blob/main/docs/DESIGN.md) has the grammar in the meantime.

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about.*
