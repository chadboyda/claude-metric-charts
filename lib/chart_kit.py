"""chart_kit: clean, honest metric charts for Slack and reports.

Use it from a per-chart script:

    import os, subprocess, sys
    sys.path.insert(0, subprocess.check_output(['metric-charts', 'lib']).decode().strip())
    from chart_kit import *
    set_theme('appsumo')                 # or 'neutral' (default), or your own via register_theme()
    fig, (top, bottom) = two_panel()
    ...
    header(fig, 'Takeaway as a sentence', 'Subtitle with the key numbers')
    foot(fig, 'Source, date range, timezone, caveats.')
    save(fig, 'out.png')

Every figure is 8 in wide at dpi 200 = 1600 px, light theme, phone-readable labels.
"""
import datetime as dt

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402

THEMES = {
    'neutral': {
        'ink': '#1B1B1B', 'grace': '#434D59', 'slate': '#8E9BAA', 'gravel': '#C7CED7', 'bg': '#FFFFFF',
        'event': '#E3A400', 'good': '#1E9E52', 'good_text': '#14713A', 'bad': '#C8402A', 'accent': '#2D6FE0',
        'head_font': ['Avenir Next', 'Arial', 'DejaVu Sans'], 'body_font': ['Helvetica Neue', 'Arial', 'DejaVu Sans'],
        'brand': '',
    },
    'appsumo': {
        'ink': '#1B1B1B', 'grace': '#434D59', 'slate': '#8E9BAA', 'gravel': '#C7CED7', 'bg': '#FFFFFF',
        'event': '#FFBC00', 'good': '#07C03B', 'good_text': '#0B7A2A', 'bad': '#C22F0F', 'accent': '#0E6EF4',
        'head_font': ['Avenir Next', 'Arial', 'DejaVu Sans'], 'body_font': ['Helvetica Neue', 'Arial', 'DejaVu Sans'],
        'brand': 'AppSumo',
    },
}
WIDTH_IN, DPI = 8, 200
T = {}
INK = GRACE = SLATE = GRAVEL = BG = EVENT = GOOD = GOOD_TEXT = BAD = ACCENT = None


def register_theme(name, **colors):
    """Add a theme. Missing keys fall back to 'neutral'."""
    THEMES[name] = {**THEMES['neutral'], **colors}


def set_theme(name='neutral'):
    global INK, GRACE, SLATE, GRAVEL, BG, EVENT, GOOD, GOOD_TEXT, BAD, ACCENT
    T.clear()
    T.update(THEMES[name])
    INK, GRACE, SLATE, GRAVEL, BG = T['ink'], T['grace'], T['slate'], T['gravel'], T['bg']
    EVENT, GOOD, GOOD_TEXT, BAD, ACCENT = T['event'], T['good'], T['good_text'], T['bad'], T['accent']
    plt.rcParams.update({
        'font.family': T['body_font'], 'font.size': 13, 'text.parse_math': False,
        'axes.edgecolor': GRAVEL, 'axes.labelcolor': GRACE, 'xtick.color': GRACE, 'ytick.color': GRACE,
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': 1,
        'xtick.major.size': 0, 'ytick.major.size': 0, 'xtick.labelsize': 12, 'ytick.labelsize': 12,
        'figure.facecolor': BG, 'axes.facecolor': BG, 'savefig.facecolor': BG,
    })


set_theme('neutral')


# ---------- layout ----------
def one_panel(height=5.6, rect=(0.13, 0.2, 0.82, 0.58)):
    """One chart, with room for a title block on top and a footnote below."""
    fig = plt.figure(figsize=(WIDTH_IN, height), dpi=DPI)
    return fig, fig.add_axes(list(rect))


def two_panel(height=7.4, top=(0.12, 0.50, 0.83, 0.27), bottom=(0.12, 0.14, 0.83, 0.25), sharex=True):
    """Two stacked charts sharing the x axis (cause on top, effect below)."""
    fig = plt.figure(figsize=(WIDTH_IN, height), dpi=DPI)
    a1 = fig.add_axes(list(top))
    a2 = fig.add_axes(list(bottom), sharex=a1 if sharex else None)
    a1.tick_params(labelbottom=not sharex)
    return fig, (a1, a2)


def header(fig, title, sub='', top=0.955, gap=None):
    """Title states the conclusion (not the metric name). Subtitle carries the key numbers."""
    lines = title.count('\n') + 1
    fig.text(0.06, top, title, fontsize=24, family=T['head_font'], fontweight='bold', color=INK, va='top', linespacing=1.15)
    if sub:
        g = gap if gap is not None else 0.06 * lines + 0.005
        fig.text(0.06, top - g, sub, fontsize=14, color=GRACE, va='top', linespacing=1.35)


def foot(fig, text):
    """Footnote: source, date range, timezone, sample sizes, confounders. Brand wordmark bottom right."""
    fig.text(0.06, 0.025, text, fontsize=10.5, color=SLATE, va='bottom', linespacing=1.4)
    if T['brand']:
        fig.text(0.95, 0.025, T['brand'], fontsize=12, family=T['head_font'], fontweight='bold', color=INK,
                 ha='right', va='bottom')


def panel_title(ax, text):
    ax.set_title(text, loc='left', fontsize=13.5, color=GRACE, pad=6)


# ---------- marks ----------
def line(ax, x, y, color=None, main=True, dashed=False, markers=True, **kw):
    """Main series: thick, colored, dots. Comparison series: thinner slate, dashed."""
    style = dict(color=color or (BAD if main else SLATE), lw=3 if main else 2, zorder=3 if main else 2,
                 solid_capstyle='round')
    if markers:
        style.update(marker='o', ms=4.5 if main else 3.5)
    if dashed:
        style['ls'] = (0, (4, 3))
    style.update(kw)
    return ax.plot(x, y, **style)


def partial_last_point(ax, x, y, color=None, label='today so far'):
    """Show an incomplete last period as a dashed segment plus a hollow dot, labelled."""
    color = color or BAD
    ax.plot(x[-2:], y[-2:], color=color, lw=3, ls=(0, (2, 2)), zorder=3)
    ax.plot(x[-1], y[-1], 'o', ms=6, mfc=BG, mec=color, mew=2, zorder=4)
    if label:
        ax.annotate(label, xy=(x[-1], y[-1]), xytext=(0, -20), textcoords='offset points', fontsize=10,
                    color=GRACE, ha='right')


def bars(ax, x, y, colors=None, width=0.72, value_labels=True, fmt='{:,.0f}', pad=None):
    """Bars with small value labels on top. Pass a list of colors to highlight a period."""
    ax.bar(x, y, width=width, color=colors or GRAVEL, zorder=2)
    if value_labels:
        off = pad if pad is not None else max(y) * 0.015
        for xi, yi in zip(x, y):
            ax.text(xi, yi + off, fmt.format(yi), ha='center', va='bottom', fontsize=9.5, color=GRACE)


def band(ax, lo, hi, label=None, x_label=None):
    """Normal-range band, labelled directly."""
    ax.axhspan(lo, hi, color=GOOD, alpha=0.10, lw=0, zorder=0)
    if label and x_label is not None:
        ax.text(x_label, hi, label, fontsize=10.5, color=GOOD_TEXT, va='bottom')


def window(ax, start, end, label=None, y=None):
    """Shade an event window (outage, bug, campaign) that explains a bump. Use datetimes for half-day edges."""
    ax.axvspan(start, end, color=GRAVEL, alpha=0.28, lw=0, zorder=0)
    if label and y is not None:
        ax.text(start + (end - start) / 2, y, label, fontsize=10, color=GRACE, ha='center', va='top', linespacing=1.2)


def event_line(ax, x, label, y, ymin=0.72, ymax=0.97):
    """Dashed marker for a single event (sale start, deploy)."""
    ax.axvline(x, ymin=ymin, ymax=ymax, color=EVENT, lw=2.2, ls=(0, (3, 3)), zorder=1)
    ax.text(x, y, label, fontsize=11.5, color=INK, family=T['head_font'], fontweight='bold')


def shade_weekends(ax, days, alpha=0.32):
    """Shade Saturdays and Sundays so weekend dips are not read as trends.
    Skip it where an event window already shades the same area."""
    for d in days:
        if d.weekday() >= 5:
            mid = dt.datetime(d.year, d.month, d.day)  # date - timedelta(hours) silently drops the hours
            ax.axvspan(mid - dt.timedelta(hours=12), mid + dt.timedelta(hours=12), color=GRAVEL, alpha=alpha, lw=0, zorder=0)


def direct_label(ax, x, y, text, color=None, bold=True, size=12.5, **kw):
    """Label a series where it sits instead of using a legend."""
    ax.text(x, y, text, fontsize=size, color=color or INK, family=T['head_font'] if bold else T['body_font'],
            fontweight='bold' if bold else 'normal', **kw)


# ---------- axes ----------
def pct_axis(ax, signed=False, step=None, decimals=0):
    if signed:
        f = lambda v, _: (f'{v:+.{decimals}f}%' if v else '0%')  # noqa: E731
    else:
        f = lambda v, _: f'{v:.{decimals}f}%'  # noqa: E731
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(f))
    if step:
        ax.yaxis.set_major_locator(mticker.MultipleLocator(step))


def count_axis(ax, money=False):
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: (f'${v:,.0f}' if money else f'{v:,.0f}')))


def date_axis(ax, every=2, days=None, fmt='%b %-d'):
    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=days) if days else mdates.DayLocator(interval=every))
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))


def save(fig, path):
    fig.savefig(path)
    plt.close(fig)
    return path
