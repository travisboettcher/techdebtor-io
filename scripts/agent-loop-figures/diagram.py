"""The agent-loop diagram for "The Missing Loop", written to layouts/partials/charts/agent-loop.html
(used by the xchart shortcode: {{< xchart "agent-loop" >}}).

Run from anywhere: python3 diagram.py
Hand-placed SVG, no layout engine. The parts follow the post's "The design" section and the
plugin's docs/DESIGN.md ("The loop"). Colours live in static/css/main.css (.xc and .xd classes),
so the diagram follows the light/dark theme."""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "layouts" / "partials" / "charts"
W, H = 500, 440

TITLE = "How a caught mistake becomes a rule"
ARIA = ("A loop: in each run the lead plans the work, the implementer builds it, a tester verifies it "
        "and then a reviewer reviews it independently, and the run writes a run record of what was caught; "
        "the retro reads the run records and session transcripts, finds the mistakes that keep recurring "
        "and proposes the cheapest rule on a branch; nothing changes until I merge it at the human gate, "
        "and the merged rule and its rules ledger entry live in the repo, where the next run's lead reads them.")
CAPTION = ("Each run writes down what was caught, the retro turns the mistakes that keep coming back "
           "into proposed rules, and only the ones I merge reach the next run.")

LINE = 18  # baseline-to-baseline spacing inside a box


def text(x, y, s, cls="", anchor="middle"):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{escape(s)}</text>'


def box(x, y, w, title, lines=(), cls="xd-box"):
    """A rounded box: a bold title, then muted lines. Returns (svg, height)."""
    h = 18 + LINE * (len(lines) + 1) - 4
    s = [f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>',
         text(x + w / 2, y + 19, title, "xc-value")]
    s += [text(x + w / 2, y + 19 + LINE * (i + 1), ln) for i, ln in enumerate(lines)]
    return "".join(s), h


def arrow(points, cls="xd-arrow"):
    """A polyline through points, with a filled head at the last point."""
    (x1, y1), (x2, y2) = points[-2], points[-1]
    size = 7 if cls == "xd-arrow" else 9
    # heads only ever point along an axis here
    dx, dy = (x2 > x1) - (x2 < x1), (y2 > y1) - (y2 < y1)
    bx, by = x2 - dx * size, y2 - dy * size
    px, py = -dy * size * 0.55, dx * size * 0.55
    head = f"{x2:.1f},{y2:.1f} {bx + px:.1f},{by + py:.1f} {bx - px:.1f},{by - py:.1f}"
    # stop the line short of the tip so the stroke doesn't blunt the head
    pts = points[:-1] + [(bx, by)]
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline class="{cls}" points="{d}"/>'
            f'<polygon class="{cls}-head" points="{head}"/>')


def agent_loop():
    s = []
    lx, rx, cw = 24, 274, 202          # left and right columns
    lc, rc = lx + cw / 2, rx + cw / 2   # their centres

    # left column, top to bottom: one run, then the record it writes
    s.append(f'<rect class="xd-unused" x="10" y="44" width="230" height="230" rx="8"/>')
    s.append(text(22, 61, "One run", "", "start"))
    lead, lead_h = box(lx, 72, cw, "Lead", ["plans the work"])
    impl, impl_h = box(lx, 140, cw, "Implementer", ["builds it"])
    gap = 24
    half = (cw - gap) / 2
    test, test_h = box(lx, 214, half, "Tester", ["verifies"])
    rev, _ = box(lx + half + gap, 214, half, "Reviewer", ["reviews"])
    rec, rec_h = box(lx, 296, cw, "Run record", ["what was caught:", "category, severity,", "who caught it"])

    # right column, bottom to top: retro, human gate, rules
    retro, retro_h = box(rx, 296, cw, "Retro", ["finds what recurs,", "proposes the", "cheapest rule"])
    gate, gate_h = box(rx, 180, cw, "Human gate", ["on a branch until", "I merge it"], "xd-box xd-gate")
    rules, rules_h = box(rx, 52, cw, "Rules in the repo", ["CLAUDE.md or skills,", "checks, hooks, tests,",
                                                            "+ rules ledger entry"])
    s += [lead, impl, test, rev, rec, retro, gate, rules]
    ty = 296 + retro_h + 22             # session transcripts, a second input to the retro
    s.append(f'<rect class="xd-unused" x="{rx + 26}" y="{ty}" width="{cw - 52}" height="30" rx="6"/>')
    s.append(text(rc, ty + 20, "session transcripts"))

    # the run's arrows
    s.append(arrow([(lc, 72 + lead_h), (lc, 140)]))
    # tester first, then the reviewer's independent review
    tc = lx + half / 2
    s.append(arrow([(tc, 140 + impl_h), (tc, 214)]))
    s.append(arrow([(lx + half, 214 + test_h / 2), (lx + half + gap, 214 + test_h / 2)]))
    s.append(arrow([(lc, 274), (lc, 296)]))   # the run writes its record

    # record -> retro -> gate -> rules
    mid = 296 + rec_h / 2
    s.append(arrow([(lx + cw, mid), (rx, mid)]))
    s.append(arrow([(rc, ty), (rc, 296 + retro_h)]))
    s.append(arrow([(rc, 296), (rc, 180 + gate_h)]))
    s.append(text(rc + 8, 296 - 16, "proposals", "", "start"))
    s.append(arrow([(rc, 180), (rc, 52 + rules_h)]))
    s.append(text(rc + 8, 180 - 10, "merged", "", "start"))

    # the loop closes: the next run's lead reads the rules
    top = 24
    s.append(arrow([(rc, 52), (rc, top), (lc, top), (lc, 72)], "xd-loop"))
    s.append(text(W / 2, top - 8, "the next run reads them", "xc-value"))
    return "".join(s)


LADDER_TITLE = "The promotion ladder"
LADDER_ARIA = ("The promotion ladder: a mistake seen once is a note that stays in the run record; seen twice, "
               "or once at critical severity, it becomes an instruction in CLAUDE.md, a skill or memory; if it "
               "keeps coming back it moves to whichever fits how it can be detected: a check, a procedure a "
               "verifier follows, when spotting it needs judgment; a hook that blocks it, when a script can spot it; "
               "or a test that fails on it, when the mistake is in the code's behavior.")
LADDER_CAPTION = ("Every rule starts as an instruction; one that keeps coming back moves to the kind of "
                  "enforcement that fits how the mistake can be detected.")


def ladder():
    s = []
    cw = 202
    note, h = box(24, 12, cw, "note", ["seen once:", "stays in the", "run record"], "xd-unused")
    inst, _ = box(274, 12, cw, "instruction", ["seen twice, or once", "at critical severity:",
                                               "CLAUDE.md, a skill", "or memory"])
    nh = 18 + LINE * 5 - 4                 # both top boxes as tall as the instruction box
    note = note.replace(f'height="{h}"', f'height="{nh}"')
    s += [note, inst]
    s.append(arrow([(24 + cw, 12 + nh / 2), (274, 12 + nh / 2)]))

    lab, bus, top = 12 + nh + 24, 12 + nh + 62, 12 + nh + 84
    s.append(text(24, lab, "keeps coming back:", "xc-value", "start"))
    s.append(text(24, lab + LINE, "by how it can be detected", "", "start"))
    w3, g3 = 144, (500 - 48 - 3 * 144) / 2
    xs = [24 + k * (w3 + g3) for k in range(3)]
    cs = [x + w3 / 2 for x in xs]
    ic = 274 + cw / 2
    s.append(f'<polyline class="xd-arrow" points="{ic:.1f},{12 + nh:.1f} {ic:.1f},{bus:.1f}"/>')
    s.append(f'<polyline class="xd-arrow" points="{cs[0]:.1f},{bus:.1f} {cs[2]:.1f},{bus:.1f}"/>')
    rungs = [("check", ["needs judgment:", "a procedure a", "verifier follows"]),
             ("hook", ["a script can", "spot it: a hook", "blocks it"]),
             ("test", ["in the code's", "behavior: a test", "fails on it"])]
    for x, c, (name, lines) in zip(xs, cs, rungs):
        b, _ = box(x, top, w3, name, lines)
        s.append(b)
        s.append(arrow([(c, bus), (c, top)]))
    return "".join(s), top + 18 + LINE * 4 - 4 + 8


# The "Layers" table of the pip-world readiness audit (22 November 2026), cell for cell.
AUDIT_LAYERS = [
    ("Tests", "yes", "yes", "partial", "yes"),
    ("Types", "no", "no", "no", "no"),
    ("Lint / format", "no", "no", "no", "no"),
    ("Coverage", "partial", "no", "no", "no"),
    ("Unit/integration split", "no", "no", "no", "no"),
    ("Mutation", "yes", "no", "no", "partial"),
    ("API fuzzing / property", "no", "no", "no", "no"),
    ("Contract", "no", "no", "no", "no"),
    ("Smoke", "partial", "no", "no", "no"),
    ("SAST", "no", "no", "no", "no"),
    ("Dependency scan", "no", "no", "no", "no"),
    ("Secret scan", "no", "no", "no", "no"),
    ("Intent", "partial", "n/a", "n/a", "no"),
    ("Flow metrics", "no", "no", "no", "partial"),
    ("Dev environment", "partial", "n/a", "n/a", "n/a"),
    ("Context", "yes", "n/a", "n/a", "partial"),
    ("Agent configuration", "partial", "n/a", "n/a", "n/a"),
    ("Codegen", "partial", "yes", "partial", "n/a"),
]
QUESTIONS = [("Exists", ""), ("In CI", ""), ("Blocks", "merge"), ("Measured", "")]
# value -> (symbol, cell class, symbol class)
CELL = {"yes": ("✓", "xd-yes", "xd-on-fill"), "partial": ("~", "xd-partial", "xd-on-fill"),
        "no": ("✗", "xd-no", ""), "n/a": ("–", "", "")}

LAYERS_TITLE = "pip-world against the four questions"
LAYERS_CAPTION = ("Each layer the audit checked in pip-world, against its four questions, "
                  "as it found them on 22 November.")


def layers_aria():
    def say(v):
        return {"n/a": "not applicable"}.get(v, v)
    parts = [f"{name}: exists {say(a)}, in CI {say(b)}, blocks merge {say(c)}, measured {say(d)}"
             for name, a, b, c, d in AUDIT_LAYERS]
    return "Grid of pip-world's layers against the audit's four questions. " + "; ".join(parts) + "."


def layers():
    s = []
    x0, cw, ch, rh = 186, 76, 18, 23        # first column x, column pitch, cell height, row pitch
    hy = 30                                  # header baseline
    # legend
    for lx, (v, label) in zip((24, 112, 226, 306), (("yes", "yes"), ("partial", "partial"), ("no", "no"),
                                                     ("n/a", "n/a"))):
        sym, cls, scls = CELL[v]
        if cls:
            s.append(f'<rect class="{cls}" x="{lx}" y="2" width="22" height="{ch}" rx="3"/>')
        s.append(text(lx + 11, 17, sym, f"xc-value xd-sym {scls}".strip()))
        s.append(text(lx + 28, 16, label, "", "start"))
    y0 = hy + 34
    for k, (q1, q2) in enumerate(QUESTIONS):
        cx = x0 + k * cw + cw / 2
        if q2:
            s.append(text(cx, y0 - 26, q1, "xc-value"))
            s.append(text(cx, y0 - 10, q2, "xc-value"))
        else:
            s.append(text(cx, y0 - 10, q1, "xc-value"))
    s.append(f'<line class="xc-grid" x1="24" y1="{y0 - 3}" x2="{x0 + 4 * cw}" y2="{y0 - 3}"/>')
    for r, (name, *vals) in enumerate(AUDIT_LAYERS):
        y = y0 + 2 + r * rh
        s.append(text(24, y + 14, name, "", "start"))
        for k, v in enumerate(vals):
            sym, cls, scls = CELL[v]
            x = x0 + k * cw + (cw - 40) / 2
            if cls:
                s.append(f'<rect class="{cls}" x="{x}" y="{y}" width="40" height="{ch}" rx="3"/>')
            s.append(text(x + 20, y + 14, sym, f"xc-value xd-sym {scls}".strip()))
    return "".join(s), y0 + 2 + len(AUDIT_LAYERS) * rh + 4


def figure(name, title, aria, body, height, caption):
    html = (f'<figure class="xc xd">\n<div class="xc-title">{escape(title)}</div>\n'
            f'<svg viewBox="0 0 {W} {height:.0f}" role="img" aria-label="{escape(aria)}">\n{body}</svg>\n'
            f'<figcaption>{escape(caption)}</figcaption>\n</figure>\n')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.html").write_text(html)


if __name__ == "__main__":
    figure("agent-loop", TITLE, ARIA, agent_loop(), H, CAPTION)
    figure("promotion-ladder", LADDER_TITLE, LADDER_ARIA, *ladder(), LADDER_CAPTION)
    figure("pip-world-layers", LAYERS_TITLE, layers_aria(), *layers(), LAYERS_CAPTION)
    print("wrote agent-loop.html, promotion-ladder.html, pip-world-layers.html")
