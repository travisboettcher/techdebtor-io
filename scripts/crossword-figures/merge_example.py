"""Find 7x7 top halves that the DP merges, and check they complete identically."""
from collections import defaultdict
from itertools import product
from grids import valid, allowed_rows, show
from examples import frontier

n, h = 7, 3
rows = allowed_rows(n)
centers = [r for r in rows if r == r[::-1]]


def completions(top):
    return [c for c in centers
            if valid([list(r) for r in top] + [list(c)] + [list(r[::-1]) for r in reversed(top)])]


if __name__ == "__main__":
    classes = defaultdict(list)
    for top in product(rows, repeat=h):
        f = frontier([list(r) for r in top])
        if f is not None:
            classes[f].append(top)

    # every class: do all members complete with the same centers? (the DP's core claim)
    bad = 0
    best = []
    for f, members in classes.items():
        comps = [tuple(completions(m)) for m in members]
        if len(set(comps)) != 1:
            bad += 1
        elif comps[0] and 3 <= len(members) <= 5:
            whites = sum(sum(r) for m in members for r in m) / len(members)
            best.append((whites, members, comps[0]))
    print(f"{len(classes)} classes; classes whose members complete differently: {bad}")
    best.sort(key=lambda t: -t[0])
    for whites, members, comp in best[:3]:
        print(f"\n{len(members)} members, {len(comp)} shared completions, avg whites {whites:.1f}")
        for m in members:
            print("  top:", "/".join("".join("." if v else "#" for v in r) for r in m))
        for c in comp:
            print("  center:", "".join("." if v else "#" for v in c))
