# Agent-loop figure

The diagram in `content/posts/the-missing-loop.md` (the "The design" section).

- `diagram.py`: writes `layouts/partials/charts/agent-loop.html`, used by the
  `xchart` shortcode (`{{< xchart "agent-loop" >}}`). Stdlib only, hand-placed SVG,
  so the output is the same on every run. The parts follow the post and the
  `agent-loop` plugin's `docs/DESIGN.md` ("The loop"): one run (lead, implementer,
  tester, reviewer) writes a run record; the retro reads run records and session
  transcripts and proposes rules; the human gate; rules in the repo with a rules
  ledger entry, which the next run's lead reads.

Run it from anywhere with `python3 diagram.py`, then commit the regenerated partial
with the script. Styles are the `.xc`/`.xd` classes at the end of
`static/css/main.css` (the flow-diagram rules are under "Flow diagrams"), so the
figure follows the light/dark theme.
