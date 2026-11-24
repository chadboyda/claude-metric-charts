---
name: metric-charts
description: Make clean, honest, branded charts (PNG) for any metric, trend, comparison or analysis you share with people, and post them in Slack as the user. Use this whenever you report numbers to anyone, especially in Slack replies and threads (sales, orders, conversion, attribution/UTM, test results, market or traffic comparisons, "did X change around date Y", "is it recovering", "how does this compare to last year"), even if nobody asks for a chart. A chart with a takeaway title plus 2-4 lines of text beats a wall of numbers.
---

# Metric charts

People read a chart in five seconds and a table in five minutes. When you share numbers, ship one or two charts that each make one clear point, with the honest caveats on the image itself, plus a short message. The method comes from two charts that landed well with a team: "stocks vs our orders" and "untagged orders are still running high" (synthetic versions are in `assets/`).

## Process

1. **Get real data, read-only.** Query the source (warehouse, logs, APIs). Save the raw series next to the chart (`<topic>/data/*.csv|json`) so the numbers can be re-checked and the chart rebuilt. Never type numbers in by hand.
2. **Decide the one point per chart.** Write the takeaway as a sentence first ("The stock market doesn't move our orders"). If you can't, you're not ready to chart. One or two charts per message; a third only if it adds a different point.
3. **Check the claim before you draw it.** If the data doesn't support the sentence you hoped to write, change the sentence ("Untagged orders are still running high", not "it's resolving"). Look for confounders: a sale starting, weekends, holidays, deploys, partial days, small samples. Compare against a baseline (same days last year, a normal range, a control) so a bump has context.
4. **Build it with `chart_kit`** (below). Start from the closest worked example in `references/examples.md`.
5. **Verify.** Read the PNG yourself. Fix clipped or overlapping labels, check every number on the image against the data, and make sure it's readable at phone size.
6. **Deliver.** Show the user first unless they said to post. Then post (see Delivery).

## Chart rules

- **Title states the conclusion**, not the metric name. Subtitle carries the 1-2 key numbers ("About 28% … vs 21% on the same days last year").
- **Footnote is where honesty lives:** source, date range, timezone ("Central time days"), definitions ("paid orders over $0"), sample sizes or cut-offs ("days with fewer than 40 orders left out"), partial periods ("today runs to 3 PM"), and confounders ("our sale started Nov 16, so this week alone proves little").
- **Explain bumps on the chart:** shade event windows, mark single events with a dashed line, shade weekends when weekend dips could be misread, show a normal-range band, and draw last year as a dashed slate line.
- **Direct labels, no legends.** Label each series where it sits. Highlight the main series in color, keep comparisons in slate/gray.
- **Partial last period:** dashed segment plus a hollow dot labelled "today so far".
- **No chartjunk:** no gridlines, no top/right spines, no 3D, no rainbow. Round numbers, `%` and `$` formatted, thousands separators.
- **Correlation claims:** show the scatter or the lags, state the coefficient and the noise band, and don't call a pattern a cause.

## Style (built into chart_kit)

- Themes: `set_theme('neutral')` (default, no wordmark) or `set_theme('appsumo')` (AppSumo palette and wordmark). Add your own with `register_theme(name, ink=..., bad=..., brand='Acme')`.
- Palette roles: ink, grace (text), slate (comparison series), gravel (axes, quiet bars, windows), `BAD` (main series / bad), `ACCENT` (a segment), `GOOD` (normal band, good bars), `EVENT` (event lines).
- Fonts: Avenir Next bold for titles and direct labels, Helvetica Neue for the rest, with Arial and DejaVu Sans fallbacks.
- 8 in wide at 200 dpi = 1600 px, light theme, 24 pt title, 12-14 pt labels (phone readable). The theme's wordmark sits bottom right.

## chart_kit

```python
import subprocess, sys
sys.path.insert(0, subprocess.check_output(['metric-charts', 'lib']).decode().strip())
import chart_kit as ck
ck.set_theme('appsumo')               # pick the theme first; read colors as ck.BAD etc. after this

fig, ax = ck.one_panel()               # or: fig, (top, bottom) = ck.two_panel()
ck.window(ax, start_dt, end_dt, 'Nov 9–16: sessions reset', y=35)   # datetimes for half-day edges
ck.shade_weekends(ax, days)            # optional; skip where an event window already shades the area
ck.band(ax, 19, 25, 'Normal range (19–25%)', x_label=days[0])
ck.line(ax, ly_x, ly_y, color=ck.SLATE, main=False, dashed=True, markers=False)
ck.line(ax, x[:-1], y[:-1])            # main series (theme BAD color)
ck.partial_last_point(ax, x, y)
ck.direct_label(ax, x_pos, y_pos, 'This year', color=ck.BAD)
ck.pct_axis(ax, step=5); ck.date_axis(ax, every=4)
ck.header(fig, 'Takeaway as a sentence', 'Subtitle with the key numbers')
ck.foot(fig, 'Source, range, timezone.\nCaveats and confounders.')
ck.save(fig, 'screenshots/<topic>/chart.png')
```

Other helpers: `bars()` (value labels, per-bar colors to highlight a period), `event_line()`, `panel_title()`, `count_axis(money=True)`. `date - timedelta(hours=12)` silently keeps the date; use `datetime` for half-day edges. Read colors from `ck.` after `set_theme`, not with `from chart_kit import BAD` (that copies the old value).

`metric-charts examples <out_dir> [theme]` renders the worked examples; read `references/examples.md` for what each shows. Save real charts under the project's screenshots folder by topic, next to their data, not in temp dirs.

## Delivery

- **Show first** unless the user said "post it" / "send it". Put the PNG(s) and the draft text in front of them (Read the PNG, or publish a small preview artifact for several charts).
- **Post as the user, one message:** text as the `initial_comment` with all files attached in a single call. Use `metric-charts upload <channel> <thread_ts or ""> "<text>" <png...>`. It reads the user's Slack token from the Slack MCP server config in `~/.claude.json` (`mcpServers.slack.env`) and never prints it. Never use a Claude-attributed Slack plugin upload for posts made as the user.
- **Text:** 2-4 short lines in the user's own voice (load the writing-style skill), leading with the answer; the chart carries the detail. Put caveats in plain words ("not calling it fixed yet").
- If the data contradicts what the user expected or asked you to say, say that plainly before posting, and don't claim it in the message.
