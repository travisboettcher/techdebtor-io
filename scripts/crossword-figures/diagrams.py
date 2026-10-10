"""Explanatory SVG diagrams for post 2, written to layouts/partials/charts/ (xchart shortcode).

Run from this directory: python3 diagrams.py
The memory layouts are the counter's `Key`/`u128` and `Packed`/`u64` map entries
(crossword-puzzle-shape-counter commit 7275ee1, src/british.rs). The row-table
examples are checked against grids.word_ok before anything is written."""
from html import escape
from grids import word_ok, runs
from charts import OUT

W = 500


def svg_figure(name, title, body, height, caption):
    html = (f'<figure class="xc xd">\n<div class="xc-title">{escape(title)}</div>\n'
            f'<svg viewBox="0 0 {W} {height}" role="img" aria-label="{escape(title)}">\n{body}</svg>\n'
            f'<figcaption>{caption}</figcaption>\n</figure>\n')
    (OUT / f"{name}.html").write_text(html)


def text(x, y, s, cls="", anchor="start"):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{escape(s)}</text>'


def memory_layout():
    bw, x0, h = 9.5, 24, 22
    s = []

    def bar(y, label, segs):
        s.append(text(x0, y - 8, label, "xc-value"))
        x = x0
        for nbytes, cls, under in segs:
            for b in range(nbytes):
                s.append(f'<rect class="{cls}" x="{x + b * bw:.1f}" y="{y}" width="{bw - 1.5:.1f}" height="{h}" rx="1.5"/>')
            s.append(text(x + nbytes * bw / 2, y + h + 15, under, "", "middle"))
            x += nbytes * bw + 6

    bar(28, "Before: 48 bytes per entry", [(32, "xc-mark", "state: 32 bytes"), (16, "xd-count", "count: 16 bytes")])
    bar(106, "After: 24 bytes per entry", [(16, "xc-mark", "state: 16 bytes"), (8, "xd-count", "count: 8 bytes")])

    # zoom in on one column
    s.append(text(x0, 186, "One column of the state, bit by bit", "xc-value"))
    bitw = 24

    def bits(y, label, fields):
        s.append(text(x0, y + 15, label, "", "start"))
        x = x0 + 64
        for nb, cls, name in fields:
            for b in range(nb):
                s.append(f'<rect class="{cls}" x="{x + b * bitw:.1f}" y="{y}" width="{bitw - 2}" height="{h}" rx="1.5"/>')
            s.append(text(x + nb * bitw / 2 - 1, y + h + 15, name, "", "middle"))
            x += nb * bitw + 4

    bits(200, "Before", [(2, "xc-mark", "length"), (2, "xc-mark", "trail"), (4, "xc-mark", "balance"),
                         (4, "xd-label", "group"), (4, "xd-unused", "unused")])
    bits(262, "After", [(5, "xc-mark", "summary code"), (3, "xd-label", "group")])
    svg_figure("layout13", "One hash-map entry, before and after packing", "".join(s), 318,
               "Same information, half the bytes. A state has one column per square across (plus a few flags), and each column stores its unfinished down word\'s length, trailing unchecked letters, and balance (checked minus unchecked), plus which group of connected white squares it belongs to. "
               "Those summaries only ever take fewer than 32 different values, so they fit in a 5-bit code, and a row has at most 8 separate groups of white "
               "squares, so 3 bits name the group. The count shrinks from 128 bits to 64, still far more "
               "than the biggest count stored.")


def row_table():
    n = 11
    good, bad = "cuc#cucucuc", "cuc#ccuuucc"

    def verdict(row):
        return all(word_ok([ch == "c" for ch in w]) for w in row.split("#") if len(w) >= 3) and \
            all(len(w) != 2 for w in row.split("#"))

    assert verdict(good) and not verdict(bad)

    def index(row):
        white = sum(1 << j for j, ch in enumerate(row) if ch != "#")
        checked = sum(1 << j for j, ch in enumerate(row) if ch == "c")
        return (white << n) | checked, white, checked

    cw, h, x0 = 22, 22, 24
    s = []
    for k, (row, ok) in enumerate([(good, True), (bad, False)]):
        y = 18 + k * 128
        for j, ch in enumerate(row):
            x = x0 + j * cw
            cls = {"#": "xd-black", "c": "xd-white", "u": "xd-unch"}[ch]
            s.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{cw - 1}" height="{h}"/>')
            if ch == "u":
                s.append(f'<circle class="xd-dot" cx="{x + (cw - 1) / 2}" cy="{y + h / 2}" r="2.5"/>')
        i, white, checked = index(row)
        wb = "".join("1" if ch != "#" else "0" for ch in row)
        cb = "".join("1" if ch == "c" else "0" for ch in row)
        tx = x0 + n * cw + 18
        s.append(text(tx, y + 9, f"white:   {wb}", "xd-mono"))
        s.append(text(tx, y + 25, f"checked: {cb}", "xd-mono"))
        s.append(text(x0, y + h + 30, f"→ table entry #{i:,}", ""))
        s.append(text(x0, y + h + 52, "1: every across word is legal" if ok else
                      "0: three unchecked letters in a row", "xc-value"))
    svg_figure("rowtable", "Checking a row: one lookup instead of a list per word", "".join(s), 262,
               "Which squares are white, and which are checked, together make a 22-bit number for an "
               "11-wide row. A table built once at start-up holds the answer for every possible pair, "
               "so checking a row's across words is one read instead of building a list for each word.")


if __name__ == "__main__":
    memory_layout()
    row_table()
    print("wrote layout13.html, rowtable.html")
