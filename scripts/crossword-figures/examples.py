"""Pick example grids for the blog: a 9x9 grid, and partial grids that merge."""
import random
from collections import defaultdict
from itertools import product
from grids import valid, allowed_rows, runs, show, word_ok


def sample_9x9(seed, tries=400000):
    rng = random.Random(seed)
    n, h = 9, 4
    rows = allowed_rows(n)
    centers = [r for r in rows if r == r[::-1]]
    found = []
    for _ in range(tries):
        top = [rng.choice(rows) for _ in range(h)]
        c = rng.choice(centers)
        g = [list(r) for r in top] + [list(c)] + [list(r[::-1]) for r in reversed(top)]
        if valid(g):
            found.append(g)
    return found


def frontier(rows_placed):
    """The DP's state after placing these rows (top of a grid), or None if dead.

    Mirrors crossword-puzzle-shape-counter `step`: horizontal words of every row
    except the last are complete and judged; closed vertical runs are judged;
    open vertical runs keep (len capped at 3, trailing unchecked, checked-unchecked);
    components must all reach the last row; edge flags for Rule 4."""
    n = len(rows_placed[0])
    R = len(rows_placed)
    g = rows_placed
    if not any(g[0]):
        return None
    for r in range(R):
        if any(len(x) == 2 for x in runs(g[r])):
            return None
    def hchecked(r, c):  # cell has a white horizontal neighbour -> in an across word
        return (c > 0 and g[r][c - 1]) or (c + 1 < n and g[r][c + 1])
    def vchecked(r, c):  # white vertical neighbour (only rows placed so far)
        return (r > 0 and g[r - 1][c]) or (r + 1 < R and g[r + 1][c])
    # complete horizontal words: rows 0..R-2 (their lower neighbours are known)
    for r in range(R - 1):
        for run in runs(g[r]):
            pat = [vchecked(r, c) for c in run]
            if len(run) == 1:
                if not pat[0]:
                    return None
            elif not word_ok(pat):
                return None
    # vertical runs
    state = []
    for c in range(n):
        col = [g[r][c] for r in range(R)]
        for run in runs(col):
            pat = [hchecked(r, c) for r in run]
            closed = run[-1] < R - 1
            # growth rules (Rule 7, Rule 8 start) apply to every run
            streak = 0
            for i, p in enumerate(pat):
                streak = 0 if p else streak + 1
                if streak >= 3 or (i == 1 and not pat[0] and not p):
                    return None
            if closed:
                if len(pat) == 2:
                    return None  # a 2-letter down word (Rule 3)
                if len(pat) == 1:
                    if not pat[0]:
                        return None
                elif not word_ok(pat):
                    return None
        if col[-1]:
            run = runs(col)[-1]
            pat = [hchecked(r, c) for r in run]
            trail = 0
            for p in pat:
                trail = 0 if p else trail + 1
            d = sum(pat) - (len(pat) - sum(pat))
            state.append((min(len(pat), 3), trail, d))
        else:
            state.append(None)
    # connectivity: union-find over white cells
    parent = {}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for r in range(R):
        for c in range(n):
            if g[r][c]:
                parent[(r, c)] = (r, c)
    for (r, c) in list(parent):
        for q in ((r + 1, c), (r, c + 1)):
            if q in parent:
                parent[find((r, c))] = find(q)
    roots_last = {find((R - 1, c)) for c in range(n) if g[R - 1][c]}
    if any(find(x) not in roots_last for x in parent):
        return None  # a component sealed off above the frontier
    labels, out = {}, []
    for c in range(n):
        if g[R - 1][c]:
            labels.setdefault(find((R - 1, c)), len(labels) + 1)
            out.append((state[c], labels[find((R - 1, c))]))
        else:
            out.append(None)
    e0 = any(g[r][0] for r in range(R))
    eN = any(g[r][n - 1] for r in range(R))
    return tuple(out), e0, eN


def merge_classes(n, R):
    rows = allowed_rows(n)
    classes = defaultdict(list)
    total = 0
    for partial in product(rows, repeat=R):
        f = frontier([list(r) for r in partial])
        if f is not None:
            total += 1
            classes[f].append(partial)
    return total, classes


if __name__ == "__main__":
    import json, sys
    which = sys.argv[1]
    if which == "9x9":
        gs = sample_9x9(1)
        # prefer open-looking grids: fewest black squares
        gs.sort(key=lambda g: sum(1 - v for row in g for v in row))
        for g in gs[:6]:
            print(sum(1 - v for row in g for v in row), show(g))
    else:
        n, R = 7, 3
        total, classes = merge_classes(n, R)
        print(f"{total} valid {R}-row partials of width {n} -> {len(classes)} states")
        big = sorted(classes.values(), key=len, reverse=True)
        sizes = [len(v) for v in big]
        print("largest classes:", sizes[:10])
        # a mid-sized class whose members differ visibly (not only mirror images)
        for members in big:
            if 3 <= len(members) <= 6 and len({m[-1] for m in members}) == 1:
                print(len(members), json.dumps(["/".join("".join("." if v else "#" for v in r) for r in m) for m in members]))
                break
