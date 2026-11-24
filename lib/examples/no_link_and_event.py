"""Example: (1) a scatter that shows no relationship, with a flat trend line and the correlation called out;
(2) a two-panel 'outside shock vs our numbers' view with an event line. Synthetic data (seeded).

Usage: python3 no_link_and_event.py [out_dir] [theme]
"""
import datetime as dt
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import chart_kit as ck  # noqa: E402

out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
ck.set_theme(sys.argv[2] if len(sys.argv) > 2 else 'neutral')
rnd = random.Random(11)

# 1. scatter: daily market move vs orders vs a normal day
x = [rnd.gauss(0, 1.1) for _ in range(494)]
y = [rnd.gauss(2, 18) for _ in x]
rho = st.correlation(x, y)
fig, ax = ck.one_panel()
ax.axhline(0, color=ck.GRAVEL, lw=1, zorder=1)
ax.axvline(0, color=ck.GRAVEL, lw=1, zorder=1)
ax.scatter(x, y, s=22, color=ck.ACCENT, alpha=0.38, linewidths=0, zorder=2)
mx, my = st.mean(x), st.mean(y)
b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
xs = [min(x), max(x)]
ax.plot(xs, [my + b * (v - mx) for v in xs], color=ck.INK, lw=2.4, zorder=3)
ax.set_xlabel('Stock index that day', fontsize=14, labelpad=8)
ax.set_ylabel('Orders vs a normal day', fontsize=14, labelpad=8)
ck.pct_axis(ax, signed=True)
ax.xaxis.set_major_formatter(ck.mticker.FuncFormatter(lambda v, _: f'{v:+.0f}%' if v else '0%'))
ax.annotate(f'Trend line is flat\ncorrelation {rho:+.2f}', xy=(xs[1] * 0.7, my + b * (xs[1] * 0.7 - mx)),
            xytext=(xs[1] * 0.25, 55), fontsize=14, family=ck.T['head_font'], fontweight='bold', color=ck.INK,
            arrowprops=dict(arrowstyle='-', color=ck.INK, lw=1.2))
ck.header(fig, "The stock market doesn't move our orders", f'Each dot is one trading day, {len(x)} days')
ck.foot(fig, 'Synthetic example data. Orders vs normal = orders vs the median of the same weekday\nover the prior 4 weeks.')
print(ck.save(fig, os.path.join(out_dir, 'no-link.png')))

# 2. two panels: index drawdown above, our daily orders below, sale start marked
days = [dt.date(2026, 11, 10) + dt.timedelta(d) for d in range(14)]
idx = [0, 0.8, 0.4, 0, -1.9, -2.9, -3.1, -5.1, -8.6, -4.3, -4.0, -3.5, -3.2, -3.0]
orders = [790, 970, 750, 800, 480, 630, 1090, 1190, 1330, 1200, 1270, 780, 1045, 1410]
fig, (a1, a2) = ck.two_panel(height=7.2, top=(0.13, 0.53, 0.82, 0.22), bottom=(0.13, 0.15, 0.82, 0.29))
a1.axhline(0, color=ck.GRAVEL, lw=1)
ck.line(a1, days, idx, color=ck.BAD)
a1.annotate('Index −8.6%', xy=(days[8], idx[8]), xytext=(-12, 0), textcoords='offset points', fontsize=13,
            family=ck.T['head_font'], fontweight='bold', color=ck.BAD, va='center', ha='right')
a1.set_ylim(-12, 3)
ck.pct_axis(a1, signed=True)
ck.panel_title(a1, 'Stocks, change since Nov 13')
colors = [ck.GOOD if d >= dt.date(2026, 11, 16) else ck.GRAVEL for d in days]
ck.bars(a2, days, orders, colors=colors)
a2.set_ylim(0, 1650)
ck.count_axis(a2)
ck.panel_title(a2, 'Our orders per day')
ck.date_axis(a2, every=2)
ck.event_line(a2, dt.datetime(2026, 11, 15, 12), 'Sale starts', 1560)
ck.header(fig, 'Stocks fell almost 9% last week.\nOur orders kept climbing.', '')
ck.foot(fig, 'Synthetic example data. The sale started Nov 16, so this week alone proves little;\n'
             'the long-run scatter is the real test.')
print(ck.save(fig, os.path.join(out_dir, 'shock-vs-orders.png')))
