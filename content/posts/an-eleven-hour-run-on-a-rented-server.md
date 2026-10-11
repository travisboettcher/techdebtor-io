---
title: "An Eleven-Hour Run on a Rented Server"
date: 2026-11-01
draft: true
tags: ["Rust", "Math", "Crosswords"]
summary: "Sizing a job from a 1/1024 sample, finding 30 idle threads, and running 16.6 billion states through 262 GB of disk to count every 15×15 British crossword grid. Twice."
---

*Part 3 of a series on counting crossword grids. [Part 1](/posts/how-many-crossword-grids-are-there/) · [Part 2](/posts/making-it-fit-then-making-it-fast/)*

At the end of [Part 2](/posts/making-it-fit-then-making-it-fast/), I could count every 13×13 British crossword grid in twelve and a half minutes on a little 4-core box. 15×15 was the real goal, though, and the first measurement was not encouraging: the fourth row alone has 386 million states, and every row after that would be bigger. This post is about how I sized the job, what went wrong before I spent any real money, and the run itself.

### How big is it, actually?

When I first saw 11×11 take ten seconds and 13×13 take two hours, my gut said 15×15 would take *weeks*. So the first job was replacing that gut feeling with measurements.

The nice thing about this problem is that it grows very predictably. The number of states each row adds is almost the same multiple at 11×11, 13×13 and 15×15, so after measuring the first four rows of 15×15 on a small 4-core machine I could project the rest. The projection said row 4 would have about 4.7 billion states (it had 4.49 billion), and row 5 about 25 billion (it came in under that, at 16.6 billion).

{{< xchart "states15" >}}

That many states don't fit in memory anywhere I can afford, so the rows go to disk: 1,024 files per row, each built in memory up to a budget and then spilled and merged into its file. The stored row 5 was 262 GB, written while row 4's 68 GB was still around to read from.

For time, I built a **rehearsal** mode. It runs the full 15×15 job on a random 1/1024 sample of the states, all the way through the last row, so you can measure the cost per state without paying for the whole thing. The estimates went:

- "weeks" (my gut);
- 700-1,700 CPU-hours (the first rehearsal, on that 4-core machine);
- 230-370 CPU-hours, or 11-18 hours on a 32-thread server (once it turned out part of that rehearsal had run on a single thread); and finally,
- 10-20 hours, most likely about 14 (after the bug below was fixed).

It took 11 hours and 17 minutes.

### The rehearsal earned its keep

The very first rehearsal was also the first time the 15×15 last row had ever run, and it promptly ran out of memory. The memory budget was only checked *between* batches of work, and at 15×15 a single batch could blow straight through it. That's a bug you really want to find on a sample, rather than eight hours into the real run.

### Thirty idle threads

I rented a server on Vultr: an AMD EPYC Turin with 32 threads, 244 GB of RAM, and 1.7 TB of free disk. Before the real run, the script does a smoke test (count 13×13 and check it's Keith's number) and a scaling test (run the same thing at different thread counts).

The smoke test passed. The scaling test is where it got interesting. Building row 4 of a 13×13 grid took about 400 seconds on **4 threads, and also about 400 seconds on 32**. Thirty of the threads were sitting there doing nothing!

The cause was the fix for the out-of-memory bug. Shrinking each batch to a single file meant that, at the fixed chunk size used to split the work, a batch only had two pieces of work to hand out. Sizing the chunks from the batch instead fixed it, and the 13×13 smoke test went from 488 seconds to 126:

{{< xchart "smoke13" >}}

I'd like to say I spotted that, but the honest version is that the scaling test spotted it, and that test was only there because checking scaling was part of the plan before committing to the big run. (I also tore down that first server while the fix was in progress, so I got to set the whole thing up twice!)

### The run

On October 1st I kicked it off for real. Here's where the time went:

{{< xchart "run15" >}}

The first four rows are almost free. Row 5 is the big one: 4.49 billion states in, 16.6 billion out. (Over the whole run, the program spilled to disk 154 times.) The last row is never stored at all (each state is glued to its own upside-down copy as it's generated, as described in [Part 1](/posts/how-many-crossword-grids-are-there/)) so it costs time but no disk. The answer came out at about 2 AM UTC:

**2,393,670,267,515,481**

The program also saves a partial sum for each of the 1,024 files, so that last number is really 1,024 numbers added up. They were all non-zero, and all within about 2% of each other, which is what you'd expect when states are spread across files by a hash. A damaged file would likely stand out.

### Doing it again

One run of a brand-new program isn't proof of anything, so I ran the whole thing again, changed in ways that should change *how* it gets the answer without changing the answer:

- **half the memory budget**, so states got merged in a completely different order (571 spills instead of 154);
- **a build that stops on any integer overflow**, instead of quietly wrapping around; and finally,
- **an interruption**: the run was stopped partway through row 4 and resumed from its last checkpoint.

It matched exactly: the same total, the same 1,024 partial sums, and the same number of states at every row.

It also took almost 25 hours instead of 11, which was avoidable. Halving the memory budget meant about four times as much merging on disk, and row 5 alone took 19 hours. (At one point I was worried it had stalled. It hadn't.) The run script now changes the batch size for the verify run instead of the budget.

### Building it with Claude

I've been fairly matter-of-fact about the AI part of this series, so let me be specific about how it actually worked. I asked the questions (most of Part 2's dead ends were mine!), decided what to try, rented and ran the server, and uploaded the logs back. Claude wrote and tested the code, ran the experiments, kept the log of what worked and what didn't, and wrote the [methods doc](https://github.com/travisboettcher/crossword-puzzle-shape-counter/blob/main/docs/METHODS.md).

It also got things wrong, and I think that's worth saying out loud:

- the chunk size that left thirty threads idle;
- the slow verify run's memory budget;
- the cache with the 0.02% hit rate from Part 2; and finally,
- a first draft of the methods doc that claimed more testing than had actually been done (Claude caught that one itself while checking it, and fixed it).

None of those reached the answer, and that's not luck. Every fast path is checked against a slow, obviously correct version; every size up to 13×13 has to match Keith's published counts; and the 15×15 number had to come out the same twice, by two different routes. The tests are what let me trust code I didn't write line by line, and that's the same conclusion I came to with [my last project](/posts/33000-lines-i-didnt-type/).

### That's the series

A voice memo in July turned into a new number, about 2.39 quadrillion grids, that answers an open question from a paper published this year. The code, the methods write-up, and the full records of both runs are all in the [repository](https://github.com/travisboettcher/crossword-puzzle-shape-counter) if you want to check my work (please do!).

There's more that could be done, like counting the grids up to rotation and reflection, or pushing on to 17×17. For now, though, I'm going to go do an actual crossword :)

---

*This post was written with the help of Claude, which also wrote most of the code it's about.*
