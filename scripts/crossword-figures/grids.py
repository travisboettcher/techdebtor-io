"""Real British-style crossword grids for the blog figures.

A small, independent re-implementation of Keith's rules (the same ones as
`crossword-puzzle-shape-counter/src/rules.rs`), checked against the known
counts (5x5 = 17, 7x7 = 650) before anything is drawn from it.
"""
from itertools import product


def runs(line):
    """Maximal runs of white cells in a row/column: list of index lists."""
    out, cur = [], []
    for i, w in enumerate(line):
        if w:
            cur.append(i)
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def words(g):
    """(cells) for every word (maximal run >= 3) across and down; None if a 2-run exists."""
    n = len(g)
    ws = []
    for r in range(n):
        for run in runs(g[r]):
            if len(run) == 2:
                return None
            if len(run) >= 3:
                ws.append([(r, c) for c in run])
    for c in range(n):
        col = [g[r][c] for r in range(n)]
        for run in runs(col):
            if len(run) == 2:
                return None
            if len(run) >= 3:
                ws.append([(r, c) for r in run])
    return ws


def checked_cells(g):
    """Cells that belong to a word in both directions."""
    n = len(g)
    across, down = set(), set()
    for r in range(n):
        for run in runs(g[r]):
            if len(run) >= 3:
                across.update((r, c) for c in run)
    for c in range(n):
        for run in runs([g[r][c] for r in range(n)]):
            if len(run) >= 3:
                down.update((r, c) for r in run)
    return across & down


def word_ok(pattern):
    """British rules 6-8 for one word's checked/unchecked pattern."""
    k = len(pattern)
    if sum(pattern) != (k + 1) // 2:
        return False
    if not pattern[0] and not pattern[1]:
        return False
    if not pattern[-1] and not pattern[-2]:
        return False
    streak = 0
    for p in pattern:
        streak = 0 if p else streak + 1
        if streak >= 3:
            return False
    return True


def connected(g):
    n = len(g)
    whites = [(r, c) for r in range(n) for c in range(n) if g[r][c]]
    if not whites:
        return False
    seen, stack = {whites[0]}, [whites[0]]
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (r + dr, c + dc)
            if 0 <= q[0] < n and 0 <= q[1] < n and g[q[0]][q[1]] and q not in seen:
                seen.add(q)
                stack.append(q)
    return len(seen) == len(whites)


def valid(g):
    n = len(g)
    if any(g[r][c] != g[n - 1 - r][n - 1 - c] for r in range(n) for c in range(n)):
        return False
    edges = [g[0], g[n - 1], [g[r][0] for r in range(n)], [g[r][n - 1] for r in range(n)]]
    if not all(any(e) for e in edges):
        return False
    ws = words(g)
    if ws is None or not connected(g):
        return False
    chk = checked_cells(g)
    return all(word_ok([cell in chk for cell in w]) for w in ws)


def allowed_rows(n):
    return [r for r in product((0, 1), repeat=n) if all(len(x) != 2 for x in runs(r))]


def all_valid(n):
    """Every valid n x n grid: top half free (rows with no 2-runs), center a palindrome."""
    h = (n - 1) // 2
    rows = allowed_rows(n)
    centers = [r for r in rows if r == r[::-1]]
    for top in product(rows, repeat=h):
        for c in centers:
            g = [list(r) for r in top] + [list(c)] + [list(r[::-1]) for r in reversed(top)]
            if valid(g):
                yield g


def show(g):
    chk = checked_cells(g)
    return "/".join(
        "".join("#" if not g[r][c] else ("c" if (r, c) in chk else "u") for c in range(len(g)))
        for r in range(len(g))
    )


if __name__ == "__main__":
    import sys
    for n, want in ((5, 17), (7, 650)):
        got = sum(1 for _ in all_valid(n))
        print(f"{n}x{n}: {got} valid grids (Keith: {want}) {'OK' if got == want else 'MISMATCH'}")
        if got != want:
            sys.exit(1)
