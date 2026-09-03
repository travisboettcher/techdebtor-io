---
title: "33,000 Lines I Didn't Type"
date: 2026-10-01
draft: true
tags: ["Home Lab", "Rust"]
---

That's five posts and about three weeks, so here's where it all landed. I started `hll` in the middle of August. By the end of the month I had a working compiler, 58 tagged releases, and a repository I had mostly reviewed instead of written - which is a strange thing to say about your own side project! Let me explain why I think it worked, and then show you the bill.

### The numbers

The workspace is five crates and about 33,000 lines of Rust - 18,000 of compiler to 15,000 of tests. It took roughly two hundred and fifty issues and pull requests to get there, which works out at eight merges a day.

I didn't type most of it. I read nearly all of it, which is a different job and, as it happens, the one that mattered.

### Why I think it held together

So why did this work when I'd expect it not to? My honest answer is that a compiler is an unusually forgiving thing to build with an agent - and not because compilers are easy (they are not, and I have the mutation-testing logs to prove it). It's because a compiler has a right answer a machine can check. Feed it a file, look at the YAML, compare the two. No taste involved anywhere, and no "well, it depends what the user meant."

So I put my effort into checking the thing instead of writing it, and every pull request into `main` has to get past all of this:

- `cargo fmt`, clippy with warnings denied, and the whole test suite;
- a coverage gate that fails the build under 80% of workspace lines;
- fuzzing on the lexer, the parser and the full pipeline;
- mutation testing, which fails on any mutant my tests didn't catch;
- an MSRV job that builds against the oldest Rust I claim to support;
- `cargo deny` for advisories and licenses;
- a prose linter, because my documentation drifts too; and finally,
- a differential test that hands every document I generate to Docker Compose's own parser.

That last one is the one I'd keep if I could only keep one, and I'm still a bit pleased with it! My snapshots prove the compiler agrees with expectations I wrote myself, which is a lovely closed loop that proves almost nothing. Asking Compose is the only check here whose answer I don't get to control - and it has already caught one thing every other test in the repo waved straight through!

I made it fail rather than skip when Docker isn't installed - and the comment I left explaining that runs on for a while. Here's the part that matters:

```
//! skipped and return" reads in a CI log as a green test that ran —
//! which is precisely the "skip that looks like a pass" the issue calls
//! worse than having no test at all.
```

Past-me was in a mood. Past-me was also right.

### The bill

Now the part I'd rather not write. Working at that speed cost me two things, and I only noticed either of them while fact-checking this series.

**My design notes went stale, and I didn't catch it for weeks.** The document I designed the language from stopped describing the language I shipped. It says `depends_on` defaults to health-gating; it doesn't. Its grammar has no separator token at all; the parser wants a newline between fields. It leans toward always emitting `container_name`; the implementation goes out of its way not to. It lists path-based routing and TCP routers as deferred - both shipped weeks ago. I decided all of those properly, in pull requests, with reasons written into the commit messages. The notes have since heard about half of them, because I sat down and wrote a corrections section while fact-checking these posts. Nothing in how I work did that on its own, though, and the other half is still only recorded here. At eight merges a day my design doc was the slowest-moving thing in the project.

**And the artifact has fingerprints.** I have one absolute rule on this blog, which is that I don't type em dashes (the ones you've seen in this series were all pasted out of `hllc`). So I went looking, and `hllc` contains 1,477 of them across 42 files. Twelve hundred of those sit in doc comments - the explanations the model wrote about its own code! Most of the diagnostics I quoted in the last four posts have one in them too. In the compiler source the comment-to-code ratio sits at 0.56, or five lines of explanation for every nine lines of Rust, and I have never documented anything that thoroughly in my life.

None of that is wrong, exactly - the diagnostics are good, the comments are useful, and I read and approved every line. But it doesn't read like me, and if you know my writing at all you can see the seams. I mind that less about the code than I expected to. I mind it more about the prose than I want to admit, this blog being the one thing I thought was safely mine.

### What I'd keep

If I started something else this way, three things I'd do again:

- build the thing whose correctness a machine can check, then spend the whole budget on the checking;
- read the diffs - all of them - since reviewing is the job now and it doesn't compress the way typing does; and finally,
- keep at least one test whose answer I don't get to control.

And then re-read my own design doc, which I clearly should have been doing all along.

### That's the series

Five posts: why I built [the thing in the first place](/posts/i-wrote-a-language-for-my-homelab/), [what you write in it](/posts/writing-services-in-hll/), [what's inside it](/posts/taking-my-compiler-apart/), [how I designed it for a model to write](/posts/designing-a-language-for-a-machine-to-write/), and this.

It's still version 0.34, it still runs on one architecture only, and I still haven't migrated the 33 files that started all of this. Two months in and the actual point of the exercise is the one thing I haven't done, which feels about right :)

---

*This post was written with the help of Claude, which also wrote a good deal of the compiler it's about - as the em dashes may have suggested.*
