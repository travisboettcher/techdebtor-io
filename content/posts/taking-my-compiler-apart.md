---
title: "Taking My Compiler Apart"
date: 2026-09-17
draft: true
tags: ["Home Lab", "Rust"]
---

The last two posts covered why I wrote `hll` and what you write in it. This one is the part I actually enjoyed, which is everything that happens in between. I promised you a reserved word, too, and I'll get to that.

### Four stages, and you can watch all of them

`hllc` is a transpiler, so there's no evaluation and no runtime anywhere in it. Text goes in, a lexer turns it into tokens, a parser turns those into a tree, the tree gets merged with whatever templates apply, and codegen walks the result and writes YAML. Two of those stages have their own subcommands, mostly because I wanted to look at them while I was building.

Start with six lines of `hll`:

```
service jellyfin {
  image "jellyfin/jellyfin:latest"
  expose 8096 as "media.techdebtor.io"
  volume "/mnt/media" -> "/data"
  env PUID = "1000"
  restart unless-stopped
}
```

`hllc tokens` gives you what the lexer made of it, which is 21 tokens with a line and column on each:

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

Look at what the lexer makes of `service`, `image`, `expose` and `restart` - they're all just `Ident`, and so are `as` and `unless-stopped`. At this stage the compiler has no idea it's looking at a service at all.

`hllc parse` runs that through the parser and prints the tree. Here's the top of it, and I'll warn you now that the full thing is 253 lines for those six lines of input:

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
### ...and 240 more lines of this
```

Most of that bulk is spans - every node carries the byte offsets, line, column and file it came from, which is what lets a diagnostic point at the exact thing you got wrong instead of shrugging vaguely about line 4.

And then `hllc build` walks that tree and writes the 15 lines of Compose YAML I showed you two posts ago. Six lines in, 21 tokens, 253 lines of tree, 15 lines back out, and the whole round trip runs in about three milliseconds!

### The one reserved word

Here's the bit I've been promising since post 1. The entire language reserves exactly one word, and it's `template`. Everything else you might take for a keyword is an ordinary identifier that the parser looks up in a table, which means you can name things after them:

```
network service {}
network image {}
network expose {}
network with {}
network as {}
network use {}
network raw {}
```

That compiles, and you can go on to reference those networks by name without `hllc` blinking once. Try it with the one real keyword, though, and you get told off:

```
res.hll: 1:9: expected an identifier, found `template`
```

`with`, `as`, `use` and `external` only mean anything in the grammar position where they're expected, which is the same trick C# plays with `var` and `async`. It cost nothing to do it this way and it means I'll never have to break somebody's file because I wanted a new field name.

### A table, not a function per keyword

So how does the parser know what `image` means, if the lexer handed it a bare identifier? It looks it up. That table is the actual design of the parser - it's the one thing I'd pass along to anyone else writing a small language - and there is no `parse_image()` and no `parse_expose()` anywhere in it. There's one generic block parser and a static table describing each type, and a row looks like this:

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

`primary_field` is what makes `image "nginx"` work without a body - a bare value after the type name sets that one field. `map_separator` is why `volume` uses `->` and `env` uses `=`. Adding a new field to the language means adding a row here rather than writing new parsing code - most of the features I added last month are a row in this table, a matching arm in codegen, and then quite a lot of tests.

### What writing the grammar down actually caught

I wrote a formal grammar before I wrote the parser, which felt like procrastinating and wasn't. Three things came out of it:

- `as` never needed to be reserved, because looking up each field's shape in that table resolves the one real ambiguity;
- three bits of syntax I'd been treating as separate features - `{ port }` shorthand, a bare `external` flag, and invoking a template with no arguments - turn out to be one grammar rule with a table lookup behind it; and finally,
- a single value and a one-element list were never two different things, which deleted a rule I'd already written down twice.

The part I got wrong was separators. I convinced myself the grammar needed no separator token between fields at all, and the compiler I actually shipped disagrees:

```
oneline.hll: 1:27: expected a newline before the next field, found an identifier "restart"
```

Fields in a struct body are newline-separated, and that's a rule I wrote into the spec later, after discovering that "no separator" made a couple of shapes ambiguous to read. So much for the grammar catching everything up front!

### Next

Next post is the one I find most interesting to talk about - `hll` was designed on the assumption that Claude would write most of the `.hll` files, and a few things in here exist purely because of that. The [design doc](https://github.com/travisboettcher/hl-lang/blob/main/docs/DESIGN.md) has the real grammar if you want it, and the code is at [github.com/travisboettcher/hl-lang](https://github.com/travisboettcher/hl-lang), still just as questionable as it was two posts ago.

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about.*
