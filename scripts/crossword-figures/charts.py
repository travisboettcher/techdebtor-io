"""Generate the SVG charts for the crossword posts into layouts/partials/charts/.

Run from this directory: python3 charts.py
Every number comes from the counter repo's results/ records or the project log
(github.com/travisboettcher/crossword-puzzle-shape-counter). Colours live in
static/css/main.css (.xc classes), so the charts follow the light/dark theme."""
import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "layouts" / "partials" / "charts"
W = 500


def figure(name, title, svg, height, table_head, table_rows, note=None):
    rows = "".join("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in r) + "</tr>"
                   for r in table_rows)
    head = "".join(f"<th>{escape(c)}</th>" for c in table_head)
    cap = f"<figcaption>{note}</figcaption>" if note else ""
    html = (f'<figure class="xc">\n<div class="xc-title">{escape(title)}</div>\n'
            f'<svg viewBox="0 0 {W} {height}" role="img" aria-label="{escape(title)}">\n'
            f'{svg}</svg>\n{cap}\n'
            f'<details><summary>Show the numbers</summary><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{rows}</tbody></table></details>\n</figure>\n')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.html").write_text(html)


def log_dots(name, title, points, lo, hi, ticks, note=None, table_head=("", "")):
    """Dots joined by a line on a log10 y axis. points: (x label, value, short label, tooltip)."""
    left, right, top, bottom = 112, 24, 28, 40
    h = 300
    ph = h - top - bottom
    pw = W - left - right
    y = lambda v: top + ph * (1 - (math.log10(v) - lo) / (hi - lo))
    step = pw / len(points)
    x = lambda i: left + step * (i + 0.5)
    s = []
    for e, lab in ticks:
        yy = y(10 ** e)
        s.append(f'<line class="xc-grid" x1="{left}" x2="{W - right}" y1="{yy:.1f}" y2="{yy:.1f}"/>'
                 f'<text x="{left - 8}" y="{yy + 4:.1f}" text-anchor="end">{lab}</text>\n')
    s.append(f'<line class="xc-axis" x1="{left}" x2="{W - right}" y1="{top + ph}" y2="{top + ph}"/>\n')
    pts = " ".join(f"{x(i):.1f},{y(p[1]):.1f}" for i, p in enumerate(points))
    s.append(f'<polyline class="xc-line" points="{pts}"/>\n')
    for i, (xl, v, short, tip) in enumerate(points):
        cx, cy = x(i), y(v)
        s.append(f'<g class="xc-hover"><title>{escape(tip)}</title>'
                 f'<rect class="xc-hit" x="{cx - step / 2:.1f}" y="{top}" width="{step:.1f}" height="{ph}"/>'
                 f'<circle class="xc-mark xc-ring" cx="{cx:.1f}" cy="{cy:.1f}" r="5"/>'
                 f'<text class="xc-value" x="{cx + (6 if i == len(points) - 1 else 0):.1f}" y="{cy - 12:.1f}" '
                 f'text-anchor="{"end" if i == len(points) - 1 else "middle"}">{escape(short)}</text>'
                 f'</g>\n<text x="{cx:.1f}" y="{top + ph + 22}" text-anchor="middle">{escape(xl)}</text>\n')
    figure(name, title, "".join(s), h, table_head,
           [(p[0], p[3].split(": ", 1)[-1]) for p in points], note)


def hbars(name, title, bars, unit_ticks, note=None, table_head=("", ""), label_w=165):
    """Horizontal bars on a linear axis. bars: (label, value or None, value text, tooltip)."""
    left, right, top = label_w, 96, 8
    pitch, bh = 36, 20
    h = top + pitch * len(bars) + 28
    pw = W - left - right
    vmax = unit_ticks[-1][0]
    xs = lambda v: left + pw * v / vmax
    s = []
    for v, lab in unit_ticks:
        xx = xs(v)
        s.append(f'<line class="xc-grid" x1="{xx:.1f}" x2="{xx:.1f}" y1="{top}" y2="{top + pitch * len(bars)}"/>'
                 f'<text x="{xx:.1f}" y="{top + pitch * len(bars) + 18}" text-anchor="middle">{lab}</text>\n')
    s.append(f'<line class="xc-axis" x1="{left}" x2="{left}" y1="{top}" y2="{top + pitch * len(bars)}"/>\n')
    for i, (lab, v, text, tip) in enumerate(bars):
        y0 = top + pitch * i + (pitch - bh) / 2
        cy = y0 + bh / 2 + 4
        s.append(f'<g class="xc-hover"><title>{escape(tip)}</title>'
                 f'<rect class="xc-hit" x="0" y="{top + pitch * i}" width="{W}" height="{pitch}"/>'
                 f'<text x="{left - 10}" y="{cy:.1f}" text-anchor="end">{escape(lab)}</text>')
        if v is None:
            s.append(f'<text class="xc-value" x="{left + 10}" y="{cy:.1f}">{escape(text)}</text></g>\n')
            continue
        x1 = xs(v)
        r = min(4, (x1 - left) / 2)
        s.append(f'<path class="xc-mark" d="M{left},{y0:.1f} H{x1 - r:.1f} '
                 f'Q{x1:.1f},{y0:.1f} {x1:.1f},{y0 + r:.1f} V{y0 + bh - r:.1f} '
                 f'Q{x1:.1f},{y0 + bh:.1f} {x1 - r:.1f},{y0 + bh:.1f} H{left} Z"/>'
                 f'<text class="xc-value" x="{x1 + 8:.1f}" y="{cy:.1f}">{escape(text)}</text></g>\n')
    figure(name, title, "".join(s), h, table_head,
           [(b[0], b[3].split(": ", 1)[-1]) for b in bars], note)


if __name__ == "__main__":
    # Post 1: Keith's #Total for n = 5..13, and the new 15x15 count
    totals = [(5, 17, "17"), (7, 650, "650"), (9, 68_956, "68,956"),
              (11, 60_384_181, "60 million"), (13, 162_468_835_136, "162 billion"),
              (15, 2_393_670_267_515_481, "2.39 quadrillion")]
    log_dots("growth", "Valid British-style grids, by grid size",
             [(f"{n}×{n}", v, s, f"{n}×{n}: {v:,}") for n, v, s in totals],
             0, 16, [(0, "1"), (3, "1,000"), (6, "1 million"), (9, "1 billion"),
                     (12, "1 trillion"), (15, "1 quadrillion")],
             note="Log scale: each gridline is 1,000× the one below it. 5×5 to 13×13 are "
                  "Michael Keith's counts; 15×15 is new.",
             table_head=("Grid", "Valid grids"))

    # Post 2: the British 13x13 count on a 4-core machine (project log)
    hbars("time13", "Time to count every 13×13 British grid (4-core machine)", [
        ("First attempt", None, "ran out of memory",
         "First attempt: ran out of memory at row 3 (49 million states)"),
        ("Last row in passes", 120, "~2 h", "Last row in passes: about 2 hours, 12 GB"),
        ("Fused last row", 26, "26 min", "Fused last row: 26 minutes, 7 GB"),
        ("Branch-free filter", 18, "18 min", "Branch-free center filter: 18 minutes"),
        ("Merged summaries", 12.5, "12.5 min", "Merged column summaries: 12.5 minutes, 7.3 GB"),
    ], [(0, "0"), (30, "30 min"), (60, "1 h"), (90, "1.5 h"), (120, "2 h")],
        table_head=("Version", "Time"))

    # Post 3: the 15x15 run (results/15x15-2026-10-01)
    states = [(0, 5_451, "5,451", "0.1 MB"), (1, 864_641, "865K", "13 MB"),
              (2, 17_782_460, "17.8M", "267 MB"), (3, 386_108_733, "386M", "5.8 GB"),
              (4, 4_485_359_212, "4.49B", "68 GB"), (5, 16_610_709_547, "16.6B", "262 GB")]
    log_dots("states15", "15×15: states stored after each row",
             [(f"row {r}", v, s, f"row {r}: {v:,} states ({d} on disk)") for r, v, s, d in states],
             3, 11, [(3, "1,000"), (6, "1 million"), (9, "1 billion")],
             note="Log scale. Row 6 (the last row of the top half) is glued to its mirror image "
                  "as it's generated, so it's never stored.",
             table_head=("Row", "States"))

    hbars("run15", "15×15: where the 11 hours 17 minutes went (32 threads)", [
        ("Rows 0–3", 29 / 3600, "29 s", "Rows 0–3: 29 seconds"),
        ("Row 4", 1940 / 3600, "32 min", "Row 4: 32 minutes (4.49 billion states)"),
        ("Row 5", 24035 / 3600, "6 h 41 min", "Row 5: 6 hours 41 minutes (16.6 billion states)"),
        ("Last row + glue", 14602 / 3600, "4 h 3 min", "Last row + glue: 4 hours 3 minutes"),
    ], [(0, "0"), (2, "2 h"), (4, "4 h"), (6, "6 h"), (8, "8 h")],
        table_head=("Stage", "Time"), label_w=165)

    hbars("smoke13", "13×13 smoke test on the 32-thread server", [
        ("Before the fix", 488, "488 s", "Before the fix: 488 seconds (row 4 alone: 394 s)"),
        ("After the fix", 126, "126 s", "After the fix: 126 seconds (row 4 alone: 45 s)"),
    ], [(0, "0"), (100, "100 s"), (200, "200 s"), (300, "300 s"), (400, "400 s"), (500, "500 s")],
        table_head=("Build", "Time"), label_w=165)
    print("wrote", sorted(p.name for p in OUT.iterdir()))
