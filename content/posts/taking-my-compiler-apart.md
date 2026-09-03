---
title: "Taking My Compiler Apart"
date: 2026-09-17
draft: true
tags: ["Home Lab", "Rust"]
---

Two posts in and I still owe you a reserved word. This one is about everything that happens between the file I write and the YAML I deploy, which is the half of the project I had the most fun with.

### Five stages, and you can watch the first two

I built `hllc` as a transpiler, so there's no evaluation and no runtime in it anywhere. Text goes in, my lexer turns it into tokens, the parser turns those into a tree, the linker resolves any `use` imports across files, the tree gets merged with whatever templates apply, and codegen walks the result and writes YAML. The first two stages have subcommands of their own, mostly because I wanted to stare at them while I was building.

Start with seven lines of `hll`:

```
service jellyfin {
  image "jellyfin/jellyfin:latest"
  expose 8096 as "media.techdebtor.io"
  volume "/mnt/media" -> "/data"
  env PUID = "1000"
  restart unless-stopped
}
```

`hllc tokens` gives me what the lexer made of that, which is 21 tokens carrying a line and column each:

```
1:1 Ident "service"
1:9 Ident "jellyfin"
1:18 LBrace "{"
2:3 Ident "image"
2:9 Str "jellyfin/jellyfin:latest"
3:3 Ident "expose"
3:10 Number "8096"
3:15 Ident "as"
3:18 Str "media.techdebtor.io"
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

Look at what my lexer makes of `service`, `image`, `expose` and `restart` - they're all just `Ident`, and so are `as` and `unless-stopped`. At this stage the compiler has no idea it's looking at a service at all. (My lexer is not a clever piece of software, and that is very much the point.)

`hllc parse` runs the same file through the parser and prints the tree. Here are the first eleven lines, and there are 242 more:

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

Most of that bulk is spans. Every node carries the byte offsets, line, column and file it came from, which is what lets a diagnostic point at the exact thing you got wrong instead of shrugging vaguely about line 4. (253 lines to describe one container named jellyfin. worth it, i promise.)

Then `hllc build` walks that tree and writes the 15 lines of Compose YAML I showed you two posts ago. Seven lines in, 21 tokens, 253 lines of tree, 15 lines back out, and the whole round trip runs in about three milliseconds!

### The one reserved word

Here's the thing I've been promising since post 1. The entire language reserves exactly one word, and it's `template`. Everything else you might take for a keyword is an ordinary identifier the parser looks up in a table, which means you can name your own things after them:

```
network service {}
network image {}
network expose {}
network with {}
network as {}

service router {
  image "nginx"
  networks [service, image, expose, with, as]
}
```

That compiles without a complaint, and here's the proof - a service called `router`, sitting on five networks named after the language!

```yaml
services:
  router:
    image: nginx
    networks:
    - service
    - image
    - expose
    - with
    - as
```

Try it with the one real keyword, though, and you get told off:

```
res.hll: 1:9: expected an identifier, found `template`
```

`with`, `as`, `use` and `external` only mean anything in the grammar position where they're expected, which is the same trick C# plays with `var` and `async`. It cost me nothing to do it this way - and it means I never have to break one of my own files just because I wanted a new field name.

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

`primary_field` is what makes `image "nginx"` work without a body - a bare value after the type name sets that one field. `map_separator` is why `volume` uses `->` and `env` uses `=`.

I'd love to tell you that adding a field to the language is just adding a row here. It mostly isn't. A new field is a row in this table, plus an arm that lowers it into the tree, plus a slot in the merge code so templates know what to do with it, plus an arm in codegen, plus quite a lot of tests. What the table buys me is that none of those is a new *parsing* function - the block parser never changes. (Exactly one field in the whole language still gets bespoke parser code, and it's the `as` in `expose 8096 as "..."`. I have made my peace with it.)

### What writing the grammar down actually caught

I wrote the formal grammar before I wrote the parser, which felt at the time like procrastinating (it wasn't). Three things fell out of it:

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
