---
title: "33,000 Lines I Didn't Type"
date: 2026-10-01
draft: true
tags: ["Home Lab", "Rust"]
---

I owe you an accounting, so here it is. I started `hll` in the middle of August, and by the end of the month I had a working compiler, 34 tagged releases, and a repository I had mostly reviewed rather than written - which is a strange thing to be able to say about your own side project. I'd like to explain why that worked, and then show you the bill.

### The numbers

The workspace is five crates and about 33,000 lines of Rust. Split by what it's for:

- 18,000 lines of compiler;
- 15,000 lines of tests; and finally,
- roughly two hundred issues and pull requests to get there.

I didn't type most of it - I read nearly all of it, which is a different job and, it turns out, the one that mattered.

### Why I think it held together

So why did this work when I'd expect it not to? My honest answer is that a compiler is an unusually forgiving thing to build with an agent - and not because compilers are easy (they are not, and I have the mutation-testing logs to prove it). It's because a compiler has a right answer a machine can check. Feed it a file, look at the YAML, compare the two, and there's no taste involved anywhere - no "well, it depends what the user meant."

So I spent my effort on the checking rather than the writing, and every pull request into `main` has to get past all of this:

- `cargo fmt`, clippy with warnings denied, and the whole test suite;
- a coverage gate that fails the build under 80% of workspace lines;
- fuzzing on the lexer, the parser and the full pipeline;
- mutation testing, which fails on any mutant the tests didn't catch;
- an MSRV job that builds against the oldest Rust I claim to support;
- `cargo deny` for advisories and licenses;
- a prose linter, because my documentation drifts too; and finally,
- a differential test that hands every document I generate to Docker Compose's own parser.

That last one is the one I'd keep if I could only keep one. My snapshots prove the compiler still agrees with expectations I wrote myself - a lovely closed loop that proves almost nothing! Asking Compose is the only check in this whole project whose answer I don't get to control, and it has caught me twice.

I made it fail rather than skip when Docker isn't installed, and I left myself a note in the file explaining why (it reads a bit sternly to me now):

```
//! than skipping. That is deliberate and it is the most important
//! ... "skipped and return" reads in a CI log as a green test that ran —
//! which is precisely the "skip that looks like a pass" the issue calls
```

A skipped test in a green CI log is worse than no test at all, because it sells you confidence you never earned!

### The bill

Now the part I'd rather not write. Working at that speed cost me two things - and I only found either of them while fact-checking this series, which is its own small indictment.

**My own design notes went stale without my noticing.** While fact-checking these posts I found four places where the document I designed the language from no longer describes the language I shipped. It says `depends_on` defaults to health-gating; it doesn't. It says a statement needs no separator; the parser wants a newline. It recommends always emitting `container_name`; the implementation goes out of its way to do the opposite. It lists path-based routing and TCP routers as deferred, and both shipped weeks ago. I decided every one of those properly, in a pull request, with a good reason written into the commit message. The notes just never heard about it. At four merges a day my design document was the slowest-moving thing in the project, and I never once went back to reconcile it.

**And the artifact has fingerprints.** This blog has one absolute rule, which is that I never type an em dash. Not once in thirteen years and three blogs. So I went looking, and `hllc` contains **1,477 of them, across 42 files** - 160 in strings that get printed to my terminal. Every diagnostic I quoted in the last four posts has one in it. The comment-to-code ratio sits at 0.56. That's six lines of explanation for every eleven lines of Rust, and I have never documented anything that thoroughly in my life.

None of that is wrong, exactly. The diagnostics are good, the comments are useful, and I read and approved every line of it. But it doesn't read like me, and if you know my writing at all you can see the seams. I mind that less about the code than I expected to, and more about the prose than I want to admit (this blog is the one thing I thought was safely mine).

### What I'd tell someone else

Build the thing whose correctness a machine can check, and then spend your whole budget on the checking rather than the building. Read the diffs - all of them - because reviewing is the job now and it doesn't compress! Keep one test whose answer you don't control. Then go back and re-read your own design document, because it is lying to you and it has been for weeks.

### That's the series

Five posts: why I built [the thing in the first place](/posts/i-wrote-a-language-for-my-homelab/), [what you write in it](/posts/writing-services-in-hll/), [what's inside it](/posts/taking-my-compiler-apart/), [how I designed it for a model to write](/posts/designing-a-language-for-a-machine-to-write/), and this. It's still version 0.34 and it still only runs on one architecture. I also still haven't migrated the 33 files that started all of this.

Which is roughly the correct amount of finished for a blog called The Tech Debtor. Until next time - happy compiling!

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about - as the em dashes may have suggested.*
