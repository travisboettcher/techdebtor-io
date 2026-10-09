---
title: "Making It Fit, Then Making It Fast"
date: 2026-10-25
draft: true
tags: ["Rust", "Math", "Crosswords"]
summary: "The first 13×13 run ran out of memory. Getting from there to 12.5 minutes took a smaller state, a lookup table, and a long list of my own ideas that didn't pan out."
---

*Part 2 of a series on counting crossword grids. [Part 1](/posts/how-many-crossword-grids-are-there/) · [Part 3](/posts/an-eleven-hour-run-on-a-rented-server/)*

[Last time](/posts/how-many-crossword-grids-are-there/) I described the idea that makes counting crossword grids possible at all: build the grid a row at a time, and merge any partial grids that have the same future, keeping a count instead of the grids. It's a great idea, and the first time I pointed it at a 13×13 grid it ran out of memory and died!

This post is about the stretch between that crash and a 13×13 count in twelve and a half minutes, which is what made 15×15 look possible. It's also about the questions I asked along the way, because most of my ideas turned out to be wrong, and *why* they were wrong taught me more than the ones that worked.

### Falling over at row 3

The first British 13×13 attempt got as far as the fourth row (row 3, counting from zero) before using up the machine's memory: 49 million stored states, on a 4-core box with about 15 GB of RAM. Each state was a perfectly reasonable Rust struct, and a perfectly reasonable Rust struct in a hash map is a lot of bytes once you have 49 million of them.

The fixes that got it to fit were mostly about storing less:

- **packing each state into 16 bytes**, with 5 bits for each column's unfinished down word and 3 bits for which white squares are connected;
- **storing mirror images once**: a partial grid and its left-right reflection have mirror-image futures, so one entry can stand in for both (row 3 went from 49 million states to 24.5 million); and finally,
- **doing the last row in several passes**, so it never had to hold everything at once.

That last one got the first successful 13×13 count: about **two hours** and 12 GB, and it matched Keith's 162,468,835,136 exactly. Then it was time to make it fast.

### Making it fast

The biggest early speedup was embarrassingly simple. Every candidate row was being checked for valid words by building a little list of words on the heap, and that allocation sat in the innermost loop. Replacing it with a lookup table (every possible row of a given width, checked once up front) took the 11×11 count from **67 seconds to 26**. A bitmask filter that rejects bad rows with a few AND operations took it to 19.

After that, the big wins were all in the last step, where the top half meets its mirror image:

- **never storing the last row at all**: each state on that row gets glued to its upside-down copy the moment it's generated, then thrown away (13×13: 2 hours to 26 minutes, 12 GB to 7);
- **a 64 KB lookup table** for checking the words that cross the middle row;
- **a branch-free filter** for the middle row that the compiler could turn into vector instructions (26 minutes to 18); and finally,
- **merging two kinds of unfinished down word that turn out to behave identically** for the rest of the grid, which cut the number of states by 10% (18 minutes to 12.5).

{{< xchart "time13" >}}

That last one deserves a sentence. A down word of three or more letters that ends on a checked letter, with two more checked than unchecked letters so far, can do exactly the same things from here on as a two-letter one in the same condition. Convincing myself it was safe took a lot longer than the change itself, which is usually how these go.

The tests also earned their keep. The fast versions of every step are checked against the original, slow, obviously correct versions on every state, every row and every middle row up to 9×9. That comparison caught a real bug in the gluing code (a region in the top half and its mirror image are *different* squares, and the fast version briefly forgot that).

The real lesson of this stretch, though: the memory wall was the way states were stored, not the algorithm. I'd assumed I needed a cleverer idea. I needed a smaller struct.

### My ideas that went nowhere

I asked a lot of questions during this part of the project, and I want to show some of the ones that didn't work, because they all sounded reasonable to me at the time (and maybe to you too).

**"Can we hash a row and reuse the results?"** The idea: if two partial grids end in the same row, surely they have the same futures? They don't, and here's a real 7×7 example. These two top halves have the same last *two* rows:

{{< xword-group caption="Two 7×7 top halves with identical second and third rows. Only the first row differs." >}}
{{< xword size="sm" rows="#....../.#.#.#./......./???????/???????/???????/???????" label="Top half A, first square black" caption="A" >}}
{{< xword size="sm" rows="......./.#.#.#./......./???????/???????/???????/???????" label="Top half B, first row all white" caption="B" >}}
{{< /xword-group >}}

Now put the same middle row under both:

{{< xword-group caption="With the middle row `##.#.##`, B is a valid grid, but A has a two-letter down word in the first column (and, by symmetry, in the last). The black square way up in row 0 changed what row 3 is allowed to be." >}}
{{< xword size="sm" rows="#....../x#.#.#./x....../##.#.##/......x/.#.#.#x/......#" label="Grid from A, broken by two-letter down words" caption="✗ A" >}}
{{< xword size="sm" rows="cucucuc/u#u#u#u/cucucuc/##u#u##/cucucuc/u#u#u#u/cucucuc" label="Valid grid from B" caption="✓ B" >}}
{{< /xword-group >}}

A down word can start anywhere above you, so no fixed number of recent rows is enough. That's exactly why the state keeps a summary of every unfinished down word instead.

**"Can we vectorize it, like in machine learning?"** I tried compiling for the newest vector instructions (AVX-512) and measured no gain at all. The work is branchy and spends its time waiting on memory, not doing arithmetic. The one place vectorizing did help was that branch-free middle-row filter, and only because the compiler did it for me.

**"What if each partial grid were just a bitmap?"** Six rows of a 13×13 grid is 78 bits, which is tiny! But two different bitmaps can never merge, and merging is the whole trick: at row 4 of a 13×13 grid, one state stands in for 107 partial grids, so bitmaps would mean about 107 times as many entries (roughly 65 times the memory, even at the smaller size).

**"Can we reuse the 13×13 answer inside the 15×15?"** Sadly no. Words and connections cross every boundary you could draw, and the cost is set by how *wide* the grid is, not its area. The one split that does pay off (fold the grid in half along its symmetry) was already in.

**"Can symmetry cut it further?"** Only a little. Mirror merging already gets the left-right reflection. Rotating by 90° swaps rows with columns, which a row-by-row sweep just can't use.

### Experiments that failed (with receipts)

Some ideas were good enough to build, measure and throw away:

- **Building cell by cell instead of row by row.** This is the textbook refinement, and it produced identical states, but it was **6.6 times slower**. The row filter already avoids building dead rows, which is the waste cell-by-cell is meant to cut.
- **Sorting instead of hashing** to merge states: 6% slower and 14% more memory. (It came back later as the format for writing states to disk, which is Part 3's problem.)
- **A cache for the last row.** The first version had a hit rate of 0.02%, which turned out to be a bug: it picked cache slots using the *low* bits of a hash whose good bits are at the top. Fixed, the hit rate went up to 32-47%, and the last row got *slower* anyway (3.4 seconds to 4.8-5.3 at 11×11). By then, gluing a state directly was cheaper than looking it up.

Every one of these went into the project log with its numbers, so I never had to wonder twice. When code is this cheap to write, ideas are cheap to try, and the bottleneck becomes remembering what you already ruled out!

### Where that left things

By the end of this stretch, 11×11 went from 73 seconds to about 3, and 13×13 went from crashing to 12.5 minutes in 7.3 GB. But 15×15 was a different animal. Row 3 alone has 386 million states, and the measurements said rows 4 and 5 would run to billions, far more than any machine I have would hold in memory. So the next step was to put the rows on disk and rent a big server, which is [Part 3](/posts/an-eleven-hour-run-on-a-rented-server/) :)

---

*This post was written with the help of Claude, which also wrote most of the code it's about. The example grids were generated and checked by a small independent rules checker in this blog's repo.*
