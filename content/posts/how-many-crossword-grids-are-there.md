---
title: "How Many Crossword Grids Are There?"
date: 2026-10-18
draft: true
tags: ["Rust", "Math", "Crosswords"]
summary: "A voice memo, an open question from a 2026 paper, and the idea that turned 'list every grid' into 'count them without looking': there are 2,393,670,267,515,481 valid 15×15 British-style crossword grids."
---

*Part 1 of a series on counting crossword grids. [Part 2](/posts/making-it-fit-then-making-it-fast/) · [Part 3](/posts/an-eleven-hour-run-on-a-rented-server/)*

Back in July I left myself a voice memo with a question in it: how many unique shapes are there for a 15×15 crossword? Not the clues, not the words, just the pattern of black and white squares. I figured it was a fun weekend puzzle. My first instinct was to write something that generates grids by mutating them and searches the space with a DFS or BFS, and just count what falls out.

That instinct was wrong by about fifteen orders of magnitude. So let me skip to the end, because I've been sitting on this for a couple of weeks and I'm excited about it:

**There are 2,393,670,267,515,481 valid 15×15 British-style crossword grids.**

That's about 2.4 quadrillion, and as far as I can tell nobody had counted them before. This post is about what a "valid grid" means, why you can't find that number by listing grids, and the one idea that let me find it anyway. The next two posts cover making that idea fit in memory and then actually running it.

### What counts as a grid

There are two big families of crossword. American-style grids (the New York Times kind) have every white square in both an across word and a down word. British-style grids, the kind you see in cryptic crosswords, are much more open: lots of squares are only in one word. Here's a 9×9 British-style grid:

{{< xword rows="cuc##ucuc/u#u###u#u/u#u###cuc/cucucuc#u/##u#u#u##/u#cucucuc/cuc###u#u/u#u###u#u/cucu##cuc" legend="true" label="A valid 9 by 9 British-style crossword grid with checked and unchecked squares marked" caption="A valid 9×9 British-style grid. Shaded squares with a dot are *unchecked*: they belong to only one word." >}}

The rules I used come from Michael Keith's paper for the 16th Gathering 4 Gardner, *How many n×n British-style crossword grids are there?* (which is a great read, and the reason this project exists). Some of them apply to every crossword:

- the grid looks the same when you turn it upside down (180° symmetry);
- every white square is connected to every other one;
- there are no two-letter words, so every across or down run of white squares is either one square long or at least three;
- every edge of the grid has at least one white square on it; and finally,
- (the British part) every word has to be *checked* in a particular way.

A square is **checked** if it's in both an across word and a down word, so solving one word gives you a letter in another. In a British grid each word needs exactly half its letters checked (rounding up), it can't have three unchecked letters in a row, and it can't start or end with two unchecked letters. Here's what that means for a seven-letter word:

{{< xword-group caption="Four 7-letter words. Only the first follows the British rules. The highlighted squares are what break the others." >}}
{{< xword size="sm" rows="cucucuc" label="checked, unchecked, alternating" caption="✓ 4 of 7 checked" >}}
{{< xword size="sm" rows="ccccccc" label="all seven checked" caption="✗ 7 of 7 checked" >}}
{{< xword size="sm" rows="cxxxccc" label="three unchecked in a row" caption="✗ three unchecked in a row" >}}
{{< xword size="sm" rows="xxccucc" label="starts with two unchecked" caption="✗ starts with two unchecked" >}}
{{< /xword-group >}}

That second one surprised me: a fully checked word, which is the whole point of an American grid, is *illegal* here. So the two families barely overlap, and they're two different counting problems.

### The triage surprise

Before writing any code, I went looking for whether this was already solved, and it half was. The American count is in the On-Line Encyclopedia of Integer Sequences ([A323839](https://oeis.org/A323839)), worked out all the way up to 21×21. There are 404,139,015,237,875 American 15×15 grids, so somebody had already done the hard work there.

The British count was different. Keith's paper counts the British grids for 5×5 through 13×13, and stops: 15×15 is listed as an open question.
<!-- TODO(Travis): check the "84 days on one core" and "roughly a thousand times" figures against the paper before publishing. -->
By the paper's account, the 13×13 count alone took his program about 84 days on a single core, and each step up in size has been roughly a thousand times the work of the one before. So the size every newspaper actually uses was out of reach. That was the moment a weekend puzzle turned into a project!

{{< xchart "growth" >}}

### You can't list them, so don't

Here's the problem with my DFS idea. Even at a billion grids a second, listing 2.4 quadrillion grids takes about a month, and that's assuming you only ever generate the valid ones (you don't; the invalid ones outnumber them enormously). And I didn't know the answer was 2.4 quadrillion yet. For all I knew it was a thousand times bigger.

The trick is that you don't need to *see* a grid to count it. Build the grid one row at a time, top to bottom, and think about what the rows you haven't placed yet actually need to know about the rows you have. It turns out to be very little:

- what the most recent row looks like;
- which of its white squares are already connected to each other (through the rows above); and finally,
- for each column, the state of the down word that's still being built there: how long it is so far, and how many of its letters are checked and unchecked.

That last part only works because of a lovely observation in Keith's paper. Since two-letter words aren't allowed, a white square is checked exactly when it has a white neighbour in the other direction. So you can tell whether every letter of an unfinished down word is checked as you go, and you only need a small summary of it, not the whole history.

Everything else about the rows above (where exactly the black squares were, which words they made, what order things happened in) can't affect what's allowed below. So two partial grids that agree on that short list have exactly the same futures. You can merge them into one entry and just remember *how many* partial grids it stands for.

Here's a real example from the 7×7 case. These three ways of filling in the top three rows look different, but they end the same way:

{{< xword-group caption="Three different top halves of a 7×7 grid. The faded rows are where they differ; the last row, and everything the rows below care about, is identical. The grey rows aren't placed yet." >}}
{{< xword size="sm" rows="###...#/.##.#.#/......./???????/???????/???????/???????" dim="0,1" label="Top half A" caption="A" >}}
{{< xword size="sm" rows="###..../.##.#.#/......./???????/???????/???????/???????" dim="0,1" label="Top half B" caption="B" >}}
{{< xword size="sm" rows="##....#/.##.#.#/......./???????/???????/???????/???????" dim="0,1" label="Top half C" caption="C" >}}
{{< /xword-group >}}

So the program stores them as **one** entry with a count of 3, works out what can go underneath it **once**, and multiplies. In a 7×7 grid, once the top three rows are down, the middle row is the only free choice left (symmetry fills in the bottom), and exactly two middle rows work. The same two work for all three, so this one entry is worth six finished grids:

{{< xword-group cols="2" caption="The six valid grids those three top halves become: each row of this figure is one top half (A, B, C), and each column is one of the two middle rows that work." >}}
{{< xword size="sm" rows="###cuc#/u##u#u#/cuucucc/u#####u/ccucuuc/#u#u##u/#cuc###" label="Grid A1" caption="A1" >}}
{{< xword size="sm" rows="###cuc#/u##u#u#/cuucucc/u##u##u/ccucuuc/#u#u##u/#cuc###" label="Grid A2" caption="A2" >}}
{{< xword size="sm" rows="###cucu/u##u#u#/cuucucc/u#####u/ccucuuc/#u#u##u/ucuc###" label="Grid B1" caption="B1" >}}
{{< xword size="sm" rows="###cucu/u##u#u#/cuucucc/u##u##u/ccucuuc/#u#u##u/ucuc###" label="Grid B2" caption="B2" >}}
{{< xword size="sm" rows="##ucuc#/u##u#u#/cuucucc/u#####u/ccucuuc/#u#u##u/#cucu##" label="Grid C1" caption="C1" >}}
{{< xword size="sm" rows="##ucuc#/u##u#u#/cuucucc/u##u##u/ccucuuc/#u#u##u/#cucu##" label="Grid C2" caption="C2" >}}
{{< /xword-group >}}

At 7×7 this barely matters: 2,371 top halves that can still become valid grids collapse to 1,823 entries, and they make up all 650 valid 7×7 grids. It's when the grids get big that it pays off. At 13×13, after the fifth row, each stored entry stands for 107 different partial grids on average, and by the end it's about 500. The program never builds the grids it's counting. It just carries the multiplier forward.

There's one more saving from the symmetry rule. Since the bottom half is just the top half turned upside down, you only ever build the top half, then check each one against its own rotation through the middle row.

If you'd like the full version, with the exact state and the argument for why merging is safe, it's all written up in the [methods doc](https://github.com/travisboettcher/crossword-puzzle-shape-counter/blob/main/docs/METHODS.md) in the (now public!) [repository](https://github.com/travisboettcher/crossword-puzzle-shape-counter).

### How I know it's right

A big number nobody can check isn't worth much, so here's why I believe this one:

- the program reproduces every one of Keith's counts from 5×5 to 13×13 exactly (17; 650; 68,956; 60,384,181; and 162,468,835,136);
- a brute-force checker in the repo, which tries every grid and knows nothing about merging, agrees at 5×5 and 7×7;
- a second, completely separate rules checker I wrote for this post (it's what produced and checked every grid shown here) gets the same 17 and 650;
- the same code reproduces the American counts from the OEIS, a completely different set of rules; and finally,
- the 15×15 run was done twice, with different memory settings so the partial counts were combined in a different order, and with a build that stops on any arithmetic overflow. Both runs agreed on the total and on all 1,024 partial sums along the way.

I also sent the result to Keith before posting it here, since it's his question.

### What's next

The idea above is a good one, but the first time I pointed it at 13×13 it ran out of memory and fell over. [Part 2](/posts/making-it-fit-then-making-it-fast/) is about getting it to fit, then getting it fast, including a pile of my own ideas that went nowhere. [Part 3](/posts/an-eleven-hour-run-on-a-rented-server/) is the run itself: 16.6 billion stored states, 262 GB on disk, and eleven hours on a rented server.

Not bad for a voice memo :)

---

*This post was written with the help of Claude, which also wrote most of the code it's about. The grids shown here were generated and checked by a small independent rules checker, which lives in this blog's repo.*
