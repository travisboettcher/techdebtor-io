"""Print the grid strings used by the blog's xword shortcodes, checking each one.

Run from this directory: python3 figures.py
Strings use '#' black, 'c' checked, 'u' unchecked, '.' undecided white, '?' not yet placed."""
from grids import valid, show
from examples import frontier

# Post 1: a valid 9x9 British grid (found by examples.sample_9x9)
G9 = "cuc##ucuc/u#u###u#u/u#u###cuc/cucucuc#u/##u#u#u##/u#cucucuc/cuc###u#u/u#u###u#u/cucu##cuc"

# Post 1: three 7x7 top halves the DP merges into one state (merge_example.py)
TOPS = ["###...#/.##.#.#/.......", "###..../.##.#.#/.......", "##....#/.##.#.#/......."]
CENTERS = [".#####.", ".##.##."]

# Post 2: same last two rows, different futures (so "hash the last rows" gives wrong counts)
SAME_A, SAME_B, SAME_CENTER = "#....../.#.#.#./.......", "......./.#.#.#./.......", "##.#.##"
# SAME_A + SAME_CENTER leaves a 2-letter down word in column 0 (and its mirror in column 6)
SAME_A_BROKEN = "#....../x#.#.#./x....../##.#.##/......x/.#.#.#x/......#"


def grid(s):
    return [[ch != "#" for ch in r] for r in s.split("/")]


def full(top, center):
    rows = top.split("/")
    return "/".join(rows + [center] + [r[::-1] for r in reversed(rows)])


if __name__ == "__main__":
    assert valid(grid(G9)) and show(grid(G9)) == G9
    print("9x9:", G9)
    states = {frontier(grid(t)) for t in TOPS}
    assert len(states) == 1 and None not in states
    for t in TOPS:
        print("top:", t + "/???????" * 4)
    for t in TOPS:
        for c in CENTERS:
            g = grid(full(t, c))
            assert valid(g)
            print("full:", show(g))
    from merge_example import completions
    ca = completions([tuple(r) for r in grid(SAME_A)])
    cb = completions([tuple(r) for r in grid(SAME_B)])
    assert tuple(grid(SAME_CENTER)[0]) in cb and tuple(grid(SAME_CENTER)[0]) not in ca
    assert not valid(grid(full(SAME_A, SAME_CENTER)))
    assert full(SAME_A, SAME_CENTER) == SAME_A_BROKEN.replace("x", ".")
    print("same rows, B valid:", show(grid(full(SAME_B, SAME_CENTER))))
    print("same rows, A broken:", SAME_A_BROKEN)
