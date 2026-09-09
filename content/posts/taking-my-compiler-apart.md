---
title: "Taking My Compiler Apart"
date: 2026-09-17
draft: true
tags: ["Home Lab", "Rust"]
---

Two posts in and I still owe you the inside of the thing. This one is about everything that happens between the file I write and the YAML I deploy, which is the half of the project I had the most fun with.

### Five stages, and you can watch the first two

I built `hllc` as a transpiler, so there's no evaluation and no runtime in it anywhere. Text goes in, my lexer turns it into tokens, the parser turns those into a tree, the linker resolves any `use` imports across files, the tree gets merged with whatever templates apply, and codegen walks the result and writes YAML. The first two stages have subcommands of their own, mostly because I wanted to stare at them while I was building.

Start with seven lines of `hll`:

```
service jellyfin {
  image "jellyfin/jellyfin:latest"
  expose 8096
  volume "/mnt/media" -> "/data"
  env PUID = "1000"
  restart unless-stopped
}
```

`hllc tokens` gives me what the lexer made of that, which is 19 tokens carrying a line and column each:

```
1:1 Ident "service"
1:9 Ident "jellyfin"
1:18 LBrace "{"
2:3 Ident "image"
2:9 Str "jellyfin/jellyfin:latest"
3:3 Ident "expose"
3:10 Number "8096"
4:3 Ident "volume"
4:10 Str "/mnt/media"
4:23 Arrow "->"
4:26 Str "/data"
5:3 Ident "env"
5:7 Ident "PUID"
5:12 Equals "="
5:14 Str "1000"
6:3 Ident "restart"
6:11 Ident "unless-stopped"
7:1 RBrace "}"
8:1 Eof ""
```

Look at what my lexer makes of `service`, `image`, `expose` and `restart` - they're all just `Ident`, and so is `unless-stopped`. At this stage the compiler has no idea it's looking at a service at all. (My lexer is not a clever piece of software, and that is very much the point.)

`hllc parse` runs the same file through the parser and prints the tree. Here are the first eleven lines, and there are 206 more:

```
Program {
    decls: [
        Service(
            Service {
                name: Ident {
                    name: "jellyfin",
                    span: Span {
                        start: 8,
                        end: 16,
                        line: 1,
                        col: 9,
```

Most of that bulk is spans. Every node carries the byte offsets, line, column and file it came from, which is what lets a diagnostic point at the exact thing you got wrong instead of shrugging vaguely about line 4. (217 lines to describe one container named jellyfin. worth it, i promise.)

Then `hllc build` walks that tree and writes twelve lines of Compose YAML. Seven lines in, 19 tokens, 217 lines of tree, twelve lines back out, and the whole round trip runs in about three milliseconds!

### The word that held out longest

Here's the thing I've been promising since post 1. My language reserves **no words at all**. Everything you might take for a keyword is an ordinary identifier the parser looks up in a table, so I can name my own things after any of them:

```
network service {}
network image {}
network expose {}
network with {}
network template {}

template template {
  restart unless-stopped
}

service router {
  image "nginx"
  networks [service, image, expose, with, template]
  with template
}
```

That compiles without a complaint. Here's the proof - a service called `router`, sitting on five networks named after the language, picking up a template called `template`:

```yaml
services:
  router:
    image: nginx
    restart: unless-stopped
    networks:
    - service
    - image
    - expose
    - with
    - template
networks:
  service: {}
  image: {}
  expose: {}
  with: {}
  template: {}
```

`with`, `as`, `use`, `external` and `template` only mean anything in the grammar position where they're expected, which is the same trick C# plays with `var` and `async`. It cost me nothing to do it this way - and it means I never have to break one of my own files just because I wanted a new field name.

`template` is the one that held out, right up until I sat down to write this series. It survived that long on a reason that sounds fine and isn't. It sits at the front of a top-level declaration - the point where my parser decides what it's about to parse at all - rather than inside a rule the parser has already committed to. So the table would have been picking the production instead of checking one, and I told myself that was different enough to be worth a word.

What killed it was having to write the sentence down. My syntax chapter came out as "there are no keywords, except this one," and I couldn't make that read like a decision rather than an accident. Dispatch was already guarded by the lexeme anyway, so making it contextual touched five places and left every diagnostic byte-identical. The rule holds without a footnote now, which is what I should have wanted all along :)

### The table

So how does the parser know what `image` means, when the lexer handed it a bare identifier? It looks it up. There's no `parse_image()` in my parser and no `parse_expose()` either, just one generic block parser and a static table describing each type. A row looks like this:

```rust
pub static IMAGE: TypeSchema = TypeSchema {
    type_name: "image",
    kind: SchemaKind::Struct,
    fields: &[FieldSchema {
        name: "ref",
        kind: FieldKind::Scalar,
    }],
    primary_field: Some("ref"),
    map_separator: None,
    uniqueness: None,
    key_may_be_reference: false,
    needs_name: false,
    schema_free: false,
};
```

`primary_field` is what makes `image "nginx"` work without a body - a bare value after the type name sets that one field. `map_separator` is the other one worth knowing about - it's why `volume` uses `->` and `env` uses `=`.

I'd love to tell you that adding a field to the language is just adding a row here. It mostly isn't. A new field is a row in this table, plus an arm that lowers it into the tree, plus a slot in the merge code so templates know what to do with it, plus an arm in codegen, plus quite a lot of tests. What the table buys me is that none of those is a new *parsing* function - the block parser never changes. (Two fields still get bespoke parser code. One is `labels`, which earned it by being the only map field whose values are allowed to be lists. The other is `expose`, and its special case now exists purely to spot a piece of sugar I deleted and say where it went - a production whose entire job is to be a good error message for a syntax that isn't in the language any more.)

### What writing the grammar down actually caught

I wrote the formal grammar before the parser, and not out of discipline. Claude was going to write the parser, and I wanted it working from a written spec rather than from whatever I'd managed to describe in a prompt that morning. Three things fell out of writing it down:

- `as` never needed to be reserved, since it's only ever looked at in one grammar position and can be an ordinary identifier everywhere else;
- two bits of syntax I'd been treating as separate features - a bare `external` flag, and invoking a template with no arguments - turn out to be the same grammar rule, told apart only by a schema lookup; and finally,
- for reference lists like `networks`, a single value and a one-element list were never two different things, which deleted a rule I had written down twice.

Where I got it wrong was separators. I had convinced myself the grammar needed no separator token between fields at all, and the compiler I actually shipped disagrees with me:

```
$ cat oneline.hll
service j { image "nginx" restart unless-stopped }

$ hllc build oneline.hll
oneline.hll: 1:27: expected a newline before the next field, found an identifier "restart"
```

Fields in a struct body are newline-separated. That rule lives beside the grammar rather than in it, because it's a layout question a context-free grammar can't really express - which is a tidy way of saying the grammar did not, in fact, catch everything up front.

### Coming up

The next one is the post I've been looking forward to. `hll` was designed on the assumption that Claude would write most of the `.hll` files, and several things in here exist purely because of that. Until then, the formal grammar is written out in [docs/DESIGN.md](https://github.com/travisboettcher/hl-lang/blob/main/docs/DESIGN.md), and the code is at [github.com/travisboettcher/hl-lang](https://github.com/travisboettcher/hl-lang).

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about.*
