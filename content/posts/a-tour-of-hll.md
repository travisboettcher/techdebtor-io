---
title: "A Tour of hll"
date: 2026-09-10
draft: true
tags: ["Home Lab", "Rust"]
---

[Last post](/posts/i-wrote-a-language-for-my-homelab/) covered why I wrote a compiler for my homelab: 33 hand-written Compose files, three broken [Traefik](https://traefik.io/traefik/) labels that nobody ever told me about, and about five different opinions on how to do the same job. This one is about what you actually write in `hll`. I'm going to stay at the level of shape rather than walk through every field, since [the user guide](https://travisboettcher.github.io/hl-lang/) already does the field-by-field job better than a blog post can.

### The shape of a service

Almost everything in `hll` is a declaration: a type, a name, and a body. Here's [BookStack](https://www.bookstackapp.com/), which is where all my long-form homelab documentation lives:

```
service bookstack {
  image "lscr.io/linuxserver/bookstack:latest"
  expose 80 as "wiki.techdebtor.io"
  env PUID = "1000"
  env PGID = "1000"
  restart unless-stopped
}
```

```yaml
services:
  bookstack:
    image: lscr.io/linuxserver/bookstack:latest
    restart: unless-stopped
    environment:
    - PUID=1000
    - PGID=1000
    expose:
    - 80
    labels:
    - traefik.http.routers.bookstack.rule=Host(`wiki.techdebtor.io`)
    - traefik.http.services.bookstack.loadbalancer.server.port=80
```

Nothing in there is a keyword, incidentally: `service`, `image`, `expose` and the rest are all ordinary identifiers that get looked up in a table while the file is being parsed, which is a detail I would have called trivia a month ago and now find genuinely interesting (next post's problem, I promise).

### expose, and when it isn't enough

`expose 80 as "wiki.techdebtor.io"` is shorthand for the common case, and it says roughly "this service listens on 80, and one hostname routes to it." That covers most of my fleet, but a service that needs more than one route gets `router` blocks, which can either replace the sugar or sit alongside it. [Vikunja](https://vikunja.io/), where my to-dos go to be ignored, wants two of them:

```
service vikunja {
  image "vikunja/vikunja:latest"
  expose 3456
  router public {
    host: "todo.techdebtor.io"
    entrypoints: web-secure
  }
  router internal {
    host: "todo.internal.techdebtor.io"
    middleware: local-ipwhitelist
  }
}
```

```yaml
    labels:
    - traefik.http.routers.vikunja-public.rule=Host(`todo.techdebtor.io`)
    - traefik.http.routers.vikunja-public.entrypoints=web-secure
    - traefik.http.routers.vikunja-internal.rule=Host(`todo.internal.techdebtor.io`)
    - traefik.http.routers.vikunja-internal.middlewares=local-ipwhitelist@file
    - traefik.http.services.vikunja.loadbalancer.server.port=3456
```

The router names get folded into the label keys, and that `@file` suffix on the middleware is a Traefik convention `hllc` knows to apply (I have left it off by hand more than once, with predictably unroutable results).

### The part that actually fixes last post's problem

Templates are the reason I built this thing. A `template` is a named bag of fields that a service can merge in, and one name is special: `defaults` gets applied to every service automatically, whether or not anybody asks for it.

```
network traefik-net {
  external
  name: "docker_default"
}

template defaults {
  networks [traefik-net]
  restart unless-stopped
}

template linuxserver_app(puid, pgid) {
  env PUID = $puid
  env PGID = $pgid
}

template authenticated {
  router {
    middleware: forwardAuth-authentik
  }
}

service paperless {
  with linuxserver_app { puid: 1000, pgid: 1000 }, authenticated
  image "paperlessngx/paperless-ngx:latest"
  expose 8000 as "paper.techdebtor.io"
}
```

```yaml
  paperless:
    image: paperlessngx/paperless-ngx:latest
    restart: unless-stopped
    environment:
    - PUID=1000
    - PGID=1000
    networks:
    - traefik-net
    expose:
    - 8000
    labels:
    - traefik.docker.network=docker_default
    - traefik.http.routers.paperless.rule=Host(`paper.techdebtor.io`)
    - traefik.http.routers.paperless.middlewares=forwardAuth-authentik@file
    - traefik.http.services.paperless.loadbalancer.server.port=8000
```

That first label is my favourite thing in this whole project. `traefik.docker.network=docker_default` is generated, because the compiler can see the service sits on an external network and knows Traefik needs the hint to disambiguate. The name itself comes from the `network` block at the top. It is also the exact label I once typed as `traefiki`, and it is now not a thing I have to type at all!

Merging runs in three tiers. `defaults` sits at the bottom, where it always loses; then come the templates listed in `with`, left to right; and finally the service's own body, which beats everything. Two templates disagreeing is the interesting case. Rather than picking a winner, the compiler just refuses:

```
p2f.hll:2:22: field `restart.policy` set by both template `a` (at p2f.hll:1:22) and template `b`—explicit templates must not conflict
```

### Generic core, specific templates

So how do I decide whether something belongs in the compiler? The test I keep coming back to is whether it would make sense on a homelab with completely different infrastructure, and most of the time the answer is no.

That's why there's no `auth` keyword. The `authenticated` template up there lives in my own files, and nothing inside `hllc` has ever heard of [Authentik](https://goauthentik.io/), or of my domain, or of the PUID that every [LinuxServer.io](https://www.linuxserver.io/) image asks for. The compiler knows Compose and Traefik, and my own conventions live in files I can edit without recompiling anything. Templates and networks can also sit in a file of their own and get pulled in by name, with one catch: `defaults` is looked up in the entry file only, so it's the one template that can't move:

```
use "common.hll" as common

service bookstack {
  with common.linuxserver_app { puid: 1000, pgid: 1000 }
  networks [common.traefik-net]
  image "lscr.io/linuxserver/bookstack:latest"
  expose 80 as "wiki.techdebtor.io"
}
```

### The escape hatch

The language doesn't model every Compose key and it never will, so `raw` passes whatever you give it straight through to the output. Here's [Jellyfin](https://jellyfin.org/) getting at the iGPU, using the built-in `devices` field for the half the grammar knows about and `raw` for the half it doesn't:

```
service jellyfin {
  image "jellyfin/jellyfin:latest"
  expose 8096 as "media.techdebtor.io"
  devices "/dev/dri" -> "/dev/dri"
  raw {
    group_add: ["video"]
  }
}
```

`group_add` lands in the generated file untouched, and hardware transcoding works without the grammar ever needing to learn what a video group is!

There is one genuinely sharp edge here, and I found it the way I find most things (the hard way, which is where this blog gets most of its material). `raw { labels: ... }` *replaces* the computed Traefik labels rather than adding to them, so a service with routers quietly loses every one of them. It warns about that now:

```
rawlabels.hll:5:5: warning: `raw { labels: ... }` replaces service `jellyfin`'s
generated Traefik labels rather than adding to them, so every label `router`,
`expose`, and `traefik` would have produced is dropped — use a `labels { ... }`
block to add labels to the computed set instead, or reproduce the ones you still
need in this list
```

Writing that warning was substantially cheaper than explaining the behaviour to myself a second time.

### Next

The next post goes inside the compiler itself: the token stream, the parser, and why the whole language has exactly one reserved word. If you'd rather read real documentation than wait around for me, [the user guide](https://travisboettcher.github.io/hl-lang/) covers every field, and the [design doc](https://github.com/travisboettcher/hl-lang/blob/main/docs/DESIGN.md) has the formal grammar behind it.

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about.*
