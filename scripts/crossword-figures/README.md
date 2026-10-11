# Crossword figures

Data and checks behind the figures in the crossword-grids series
(`content/posts/how-many-crossword-grids-are-there.md` and its two follow-ups).

- `grids.py`: an independent British-rules checker (no merging, no DP). Running it
  enumerates every 5×5 and 7×7 grid and checks the totals against Keith's 17 and 650
  (takes about 2 minutes).
- `examples.py`: random 9×9 sampling, plus `frontier()`, a Python mirror of the
  counter's row-transfer state.
- `merge_example.py`: groups 7×7 top halves by state and checks that every group
  completes identically (1,823 groups, none inconsistent).
- `figures.py`: the exact grid strings used in the posts' `xword` shortcodes, each
  re-checked when it runs.
- `charts.py`: writes the SVG charts to `layouts/partials/charts/` (used by the
  `xchart` shortcode). Numbers come from the counter repo's `results/` records.

Shortcodes: `xword` (one grid; `#` black, `c` checked, `u` unchecked, `.` white,
`?` not placed, `x` rule-breaking; `dim`, `legend`, `size="sm"`), `xword-group`
(a row of small grids with one caption; optional `cols`), and `xchart "<name>"`.
Styles are at the end of `static/css/main.css`.
