---
title: "Making It Fit, Then Making It Fast"
date: 2026-10-25
draft: true
tags: ["Rust", "Math", "Crosswords"]
summary: "The first 13×13 run ran out of memory. Getting from there to 12.5 minutes took a smaller state, a lookup table, and a long list of my own ideas that didn't pan out."
---

*Part 2 of a series on counting crossword grids. [Part 1](/posts/how-many-crossword-grids-are-there/)*

[Last time](/posts/how-many-crossword-grids-are-there/) I described the idea that makes counting crossword grids possible at all: build the grid a row at a time, and merge any partial grids that have the same future, keeping a count instead of the grids. It's a great idea, and the first time I pointed it at a 13×13 grid it ran out of memory and died!

This post is about the stretch between that crash and a 13×13 count in twelve and a half minutes, which is what made 15×15 look possible. It's also about the questions I asked along the way, because most of my ideas turned out to be wrong, and *why* they were wrong taught me more than the ones that worked.

### Falling over at row 3

The first British 13×13 attempt got as far as the fourth row (row 3, counting from zero) before using up the machine's memory: 49 million stored states, on a 4-core box with about 15 GB of RAM. Each state was a perfectly reasonable Rust struct, and a perfectly reasonable Rust struct in a hash map is a lot of bytes once you have 49 million of them.

The fixes that got it to fit were mostly about storing less:

- **packing each state into 16 bytes**, with 5 bits for each column's unfinished down word and 3 bits for which white squares are connected;
- **one shared table** of states for all the threads, instead of a separate copy per thread that got combined at the end;
- **storing mirror images once**: a partial grid and its left-right reflection have mirror-image futures, so one entry can stand in for both (row 3 went from 49 million states to 24.5 million); and finally,
- **doing the last row in several passes**, so it never had to hold everything at once.

Here's what the packing looks like for a single entry in the table, the state plus its count:

{{< xchart "layout13" >}}

Nothing about the state got smarter. Each column was just using a whole 16-bit number to hold a few small fields, a quarter of it empty, and the count was a 128-bit number for values that never get near 64 bits.

That last one got the first successful 13×13 count: about **two hours** and 12 GB, and it matched Keith's 162,468,835,136 exactly. Then it was time to make it fast.

### Making it fast

The biggest early speedup was embarrassingly simple. Every time the program tried a new row, it checked the row's across words by building a little list for each word and running the British rules over it. That list got allocated on the heap, in the innermost loop, millions of times a second.

But a row's across words only depend on two things: which squares are white, and which of them are checked. For an 11-wide row that's 22 bits, so there are only about four million combinations, and the answer for every one of them fits in a 512 KB table built once at start-up:

{{< xchart "rowtable" >}}

That took the 11×11 count from **67 seconds to 26**. A second filter that rejects most bad rows with a few bitwise ANDs, before doing any real work, took it to 19.

After that, the big wins were all in the last step, where the top half meets its mirror image:

- **never storing the last row at all**: each state on that row gets glued to its upside-down copy the moment it's generated, then thrown away (13×13: 2 hours to 26 minutes, 12 GB to 7);
- **a 64 KB lookup table** for checking the words that cross the middle row;
- **a branch-free filter** for the middle row that the compiler could turn into vector instructions (26 minutes to 18); and finally,
- **merging two kinds of unfinished down word that turn out to behave identically** for the rest of the grid, which cut the number of states by 10% (18 minutes to 12.5).

{{< xchart "time13" >}}

That last one deserves a picture. Remember from Part 1 that each unfinished down word is stored as a small summary: how long it is so far (counting 3 and up as just "3+"), how many unchecked letters it ends with, and how many more checked letters it has than unchecked ones. Here are two unfinished down words with different summaries:

{{< xword-group class="xw-align-end" caption="Two unfinished down words, read top to bottom. Left: 4 letters, ends checked, 3 checked and 1 unchecked. Right: 2 letters, both checked. Both end on a checked letter with two more checked than unchecked." >}}
{{< xword rows="c/u/c/c" label="Down word: checked, unchecked, checked, checked" caption="3+ letters" >}}
{{< xword rows="c/c" label="Down word: checked, checked" caption="2 letters" >}}
{{< /xword-group >}}

Now try finishing both words with the same letters below them:

| Letters added below | 4-letter word | 2-letter word |
|---|---|---|
| none (the word ends here) | ✗ too many checked | ✗ two-letter word |
| unchecked | ✓ | ✓ |
| unchecked, unchecked | ✗ ends with two unchecked | ✗ ends with two unchecked |
| unchecked, checked | ✗ too many checked | ✗ too many checked |
| unchecked, unchecked, checked | ✓ | ✓ |

They always agree. (The checker behind these posts tries every ending up to six more letters, and there isn't one where they differ.) So the program can treat them as the same summary, and every partial grid that differs only in which of the two it has merges into one state. Convincing myself it was safe took a lot longer than the change itself, which is usually how these go.

The tests also earned their keep. The fast versions of every step are checked against the original, slow, obviously correct versions on every state, every row and every middle row up to 9×9. That comparison caught a real bug in the gluing code (a region in the top half and its mirror image are *different* squares, and the fast version briefly forgot that).

The real lesson of this stretch, though: the memory wall was the way states were stored, not the algorithm. I'd assumed I needed a cleverer idea. I needed a smaller struct.

### My ideas that went nowhere

I asked a lot of questions during this part of the project, and most of them didn't pan out. I want to walk through them properly, because they all sounded reasonable to me at the time (and maybe to you too). The thing that ties them together is that the program's speed comes from **merging**: the fewer different states there are, the less work and memory it needs. An idea that throws away merging loses, even if it makes each state smaller or faster to handle.

**"Can we hash a row and reuse the results?"** The idea: if two partial grids end in the same row, surely whatever can go below one can go below the other, so you could key everything on the last row (or its hash) instead of a big complicated state. It's a nice idea, and it gives the wrong answer. Here's a real 7×7 example. These two top halves have the same last *two* rows:

{{< xword-group caption="Two 7×7 top halves with identical second and third rows. Only the first row differs." >}}
{{< xword size="sm" rows="#....../.#.#.#./......./???????/???????/???????/???????" label="Top half A, first square black" caption="A" >}}
{{< xword size="sm" rows="......./.#.#.#./......./???????/???????/???????/???????" label="Top half B, first row all white" caption="B" >}}
{{< /xword-group >}}

Now put the same middle row under both:

{{< xword-group caption="With the middle row `##.#.##`, B is a valid grid, but A has a two-letter down word in the first column (and, by symmetry, in the last). The black square way up in row 0 changed what row 3 is allowed to be." >}}
{{< xword size="sm" rows="#....../x#.#.#./x....../##.#.##/......x/.#.#.#x/......#" label="Grid from A, broken by two-letter down words" caption="✗ A" >}}
{{< xword size="sm" rows="cucucuc/u#u#u#u/cucucuc/##u#u##/cucucuc/u#u#u#u/cucucuc" label="Valid grid from B" caption="✓ B" >}}
{{< /xword-group >}}

What went wrong is that the first column of A has a down word that started in row 1, so it's only two letters long when the black square in row 3 ends it. In B, the same column's word started in row 0, so it's three letters long and fine. The last two rows look identical, but they don't tell you where the words running through them *started*, and a down word can start any number of rows up. So no fixed number of recent rows is enough. The state has to carry a summary of every unfinished down word (plus which white squares are connected through the rows above), and once it does, that summary already *is* the smallest key that gives the right answer. Hashing it would only add the risk of two different states colliding and silently corrupting the count.

**"Can we vectorize it, like in machine learning?"** Vector instructions (SIMD) speed things up by doing the same arithmetic on 8 or 16 numbers at once, which is perfect for the big, regular grids of numbers in machine learning. This program doesn't look like that. For each state, it works out which rows can follow, and the answer is different for every state: one state might have a handful of possible next rows and the next one dozens, each needs its own checks, and each result has to be looked up in a hash table with hundreds of millions of entries scattered across memory. Most of the time goes to waiting on those lookups, not on arithmetic. I tried it anyway, compiling for the newest vector instructions (AVX-512), and measured no gain at all. The one place vectorizing did help was the middle-row filter above, which really is the same check on every column, and the compiler did that one for me once it was written without branches.

**"What if each partial grid were just a bitmap?"** Six rows of a 13×13 grid is 78 bits, about 10 bytes, which is smaller than a 16-byte state! The catch is that a bitmap remembers exactly where every black square is, so two partial grids only share an entry if they are *identical*. Part 1's three 7×7 top halves (A, B and C) would be three entries instead of one. At row 4 of a 13×13 grid, one state stands in for 107 different partial grids on average, so bitmaps would mean about 107 times as many entries. Each one being a bit smaller doesn't come close to making up for that: it works out to about 65 times the memory.

**"Can we reuse the 13×13 answer inside the 15×15?"** The hope was that a 15×15 grid is "a 13×13 grid plus a border", so the hard part could be reused. But the 13×13 count is the number of *finished, valid* 13×13 grids, and the middle 13×13 of a valid 15×15 grid usually isn't one: its words run off the edges into the border, so they can be the wrong length or checked the wrong way when you cut them off; its white squares can be connected only by going around through the border; and the edge rule is about a different edge. None of the 13×13 grids we counted are the pieces a 15×15 grid is made from. The program's cost is also set by how *wide* the grid is (how much each state has to remember about a row), not its area, and every 15×15 state is 15 columns wide no matter how you slice it. The one split that does pay off, folding the grid in half along its symmetry and only building the top half, was already in.

**"Can symmetry cut it further?"** First, symmetry can't shrink the *answer*: Keith's count includes mirror images and rotations as separate grids, and so does mine. It can only save work, by computing one thing and using it for several. Mirroring left to right works because the mirror image of "the top four rows of a grid" is still "the top four rows of a grid", so the program stores one and knows the other. Turning a grid upside down is the fold, already used. But rotating a quarter turn turns "the top four rows" into "the left four columns", and the program never builds partial grids column by column, so there's nothing stored for the rotated version to match. Using rotation would mean a completely different method, not a tweak to this one.

### Experiments that failed (with receipts)

Some ideas were good enough to build, measure and throw away:

- **Building cell by cell instead of row by row.** This is the textbook refinement, and it produced identical states, but it was **6.6 times slower**. The row filter already avoids building dead rows, which is the waste cell-by-cell is meant to cut.
- **Sorting instead of hashing** to merge states: 6% slower and 14% more memory. (It came back later as the format for writing states to disk, which is Part 3's problem.)
- **A cache for the last row.** The first version had a hit rate of 0.02%, which turned out to be a bug: it picked cache slots using the *low* bits of a hash whose good bits are at the top. Fixed, the hit rate went up to 32-47%, and the last row got *slower* anyway (3.4 seconds to 4.8-5.3 at 11×11). By then, gluing a state directly was cheaper than looking it up.

Every one of these went into the project log with its numbers, so I never had to wonder twice. When code is this cheap to write, ideas are cheap to try, and the bottleneck becomes remembering what you already ruled out!

### Where that left things

By the end of this stretch, 11×11 went from 73 seconds to about 3, and 13×13 went from crashing to 12.5 minutes in 7.3 GB. But 15×15 was a different animal. Row 3 alone has 386 million states, and the measurements said rows 4 and 5 would run to billions, far more than any machine I have would hold in memory. So the next step was to put the rows on disk and rent a big server, which is Part 3 :)

---

*This post was written with the help of Claude, which also wrote most of the code it's about. The example grids were generated and checked by a small independent rules checker in this blog's repo.*
