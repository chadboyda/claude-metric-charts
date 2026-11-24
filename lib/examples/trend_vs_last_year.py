"""Example: a share-over-time metric vs the same days last year, with a normal band, an incident window,
a partial last day, and a segment breakdown below. Synthetic data (seeded) so it runs anywhere.

Usage: python3 trend_vs_last_year.py [out.png] [theme]
"""
import datetime as dt
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from chart_kit import (GRACE, SLATE, band, date_axis, direct_label, foot, header,  # noqa: E402
                       line, panel_title, partial_last_point, pct_axis, save, set_theme, two_panel, window)
import chart_kit as ck  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else 'trend_vs_last_year.png'
set_theme(sys.argv[2] if len(sys.argv) > 2 else 'neutral')
rnd = random.Random(7)

days = [dt.date(2026, 11, 1) + dt.timedelta(d) for d in range(24)]
this = [22 + rnd.uniform(-3, 3) if d.day < 17 else 29 + rnd.uniform(-1.5, 3) for d in days]
this[-1] = 26.1
last = [22 + rnd.uniform(-3, 3) if d.day < 17 else 20 + rnd.uniform(-1.5, 2) for d in days]
everyone = [8 + rnd.uniform(-3, 3) for _ in days]
reset = [(d, 22 - max(0, (d.day - 20)) * 3.2 + rnd.uniform(-1, 1)) for d in days if d.day >= 17]

fig, (a1, a2) = two_panel(height=7.8, top=(0.11, 0.48, 0.84, 0.29), bottom=(0.11, 0.165, 0.84, 0.21))
for a in (a1, a2):
    window(a, dt.datetime(2026, 11, 8, 12), dt.datetime(2026, 11, 16, 12))
a1.text(dt.datetime(2026, 11, 12, 12), 35.2, 'Nov 9–16: saved\nsources reset', fontsize=10, color=GRACE, ha='center', va='top')
band(a1, 19, 25, 'Normal range (Nov 1–8: 19–25%)', x_label=days[0])
line(a1, days, last, color=SLATE, main=False, dashed=True, markers=False)
line(a1, days[:-1], this[:-1], color=ck.BAD)
partial_last_point(a1, days, this)
direct_label(a1, dt.date(2026, 11, 20), 33.6, 'This year', color=ck.BAD)
direct_label(a1, dt.date(2026, 11, 18), 15.2, 'Same days last year', color=GRACE, bold=False, size=12)
a1.set_ylim(14, 36)
pct_axis(a1, step=5)
panel_title(a1, 'Orders with no source')

line(a2, days, everyone, color=SLATE, main=False)
line(a2, [d for d, _ in reset], [v for _, v in reset], color=ck.ACCENT)
direct_label(a2, dt.date(2026, 11, 17), 26.2, 'Last visit Nov 9–16', color=ck.ACCENT, size=11.5)
direct_label(a2, dt.date(2026, 11, 1), 18.5, 'Everyone else', color=GRACE, bold=False, size=11)
a2.set_ylim(0, 30)
pct_axis(a2, step=10)
panel_title(a2, 'Repeat buyers whose source went missing')
date_axis(a2, days=[1, 5, 9, 13, 17, 21, 24])

header(fig, 'Untagged orders are still running high',
       'About 28% of orders since Nov 17 have no source, vs 21% on the same days\n'
       'last year. Buyers whose session was reset Nov 9–16 lose theirs most.', gap=0.06)
foot(fig, 'Synthetic example data. Central time days; today runs to 3 PM.\n'
          'Bottom panel: buyers whose previous order had a source;\n'
          'days with fewer than 40 such orders left out.')
print(save(fig, out))
