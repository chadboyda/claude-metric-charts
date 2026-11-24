# Worked examples

Both run on synthetic, seeded data: `metric-charts examples <out_dir> [neutral|appsumo]`.
Source: `lib/examples/`. Rendered copies (appsumo theme): `assets/`.

## trend_vs_last_year.py → trend-vs-last-year.png
Question it answers: "did this metric change around date X, and is it recovering?"
- Top panel: daily share this year (main color) vs the same days last year (dashed slate), a
  labelled normal-range band from a clean baseline period, a shaded incident window, and a
  partial last day (dashed segment, hollow dot, "today so far").
- Bottom panel: the segment that explains the jump (accent color) against everyone else (slate),
  so the reader sees which group drives it and whether it is fading.
- Title states the verdict ("still running high"), not the metric. When the data doesn't show a
  recovery, the title says so.

## no_link_and_event.py → no-link.png, shock-vs-orders.png
Question it answers: "does outside factor X drive our numbers?"
- no-link.png: one dot per day, a least-squares trend line, and the correlation called out on the
  chart. This is the real test, so it comes first.
- shock-vs-orders.png: the outside series (top) above our daily bars (bottom) for the week in
  question, with an event line for the confounder (a sale starting). The footnote says the week
  alone proves little and points to the long-run chart.

## Checklist before sending
- Title = conclusion; subtitle = the 1-2 numbers behind it.
- Footnote = source, range, timezone, definitions, cut-offs, partial periods, confounders.
- Every number on the image matches the saved data. No clipped or overlapping labels (Read the PNG).
- Readable on a phone: nothing below ~10 pt, one point per chart.
