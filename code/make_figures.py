"""Figures for the ANT IPO prediction report. Run from the repository root.
LANG_FIG=en (default) writes English figures; LANG_FIG=zh writes Traditional Chinese figures (*_zh.png).
Inputs: data/mega_ipos.csv, data/price_features.csv, data/exit_trailing_sim.csv. Output: figures/*.png (300 dpi).
Colours: blue #2a78d6, orange #eb6834 (checked with a colour-vision-deficiency validator)."""
import glob, os, textwrap, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker

EN = os.environ.get('LANG_FIG', 'en') != 'zh'
def T(zh, en): return en if EN else zh
OUT = os.environ.get('FIG_DIR', 'figures'); os.makedirs(OUT, exist_ok=True)
BLUE, ORANGE, INK, INK2, GRID = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#d9d8d4'
for f in sorted(glob.glob('/usr/share/fonts/**/NotoSansCJK*-Regular.tt[cf]', recursive=True)): font_manager.fontManager.addfont(f)
plt.rcParams.update({'font.family': ['Noto Sans CJK JP', 'DejaVu Sans', 'sans-serif'], 'font.size': 11, 'axes.titlesize': 14, 'axes.titleweight': 'bold',
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': INK2, 'axes.linewidth': 0.8, 'axes.grid': True,
                     'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.axisbelow': True, 'text.color': INK, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'figure.facecolor': 'white', 'savefig.dpi': 300, 'savefig.bbox': 'tight'})
pct = ticker.PercentFormatter(1.0, decimals=0)
def note(fig, t, y=-0.02): fig.text(0.01, y, textwrap.fill(t, 115 if EN else 60), fontsize=8.5, color=INK2, ha='left', va='top')
def save(fig, name): fig.savefig(f'{OUT}/{name}' if EN else f'{OUT}/{name.replace(".png", "_zh.png")}'); plt.close(fig)

# Figure 1: first-day return by where the IPO priced relative to its range
d = pd.read_csv('data/mega_ipos.csv')
d['r1'] = pd.to_numeric(d.first_close_from_offer_pct, errors='coerce') / 100  # audited column: split- and currency-adjusted
d['grp'] = d.pricing_group.map({'加價': 'above', '範圍頂': 'top', '範圍內': 'within', '減價': 'below'}).fillna('none')  # hand-checked column; 'max price only' etc. count as no range
x = d.dropna(subset=['r1']); order = ['above', 'top', 'within']
GN = {'above': T('高於範圍', 'Above range'), 'top': T('範圍上限', 'At top of range'), 'within': T('範圍之內', 'Within range')}
n_clip = int((x[x.grp.isin(order)].r1 > 1.2).sum())
fig, ax = plt.subplots(figsize=(8, 4.2)); rng = np.random.default_rng(1)
for i, g in enumerate(order):
    s = x[x.grp == g].r1
    ax.scatter(s.clip(upper=1.2), i + rng.uniform(-0.12, 0.12, len(s)), s=28, color=BLUE, alpha=0.75, edgecolor='white', linewidth=0.8, zorder=3)
    m = s.median(); ax.plot([m, m], [i - 0.3, i + 0.3], color=ORANGE, lw=2.5, zorder=4)
    ax.text(m, i - 0.34, T(f'中位數 {m:+.0%}', f'median {m:+.0%}'), fontsize=10, ha='center', va='bottom')
ax.set_yticks(range(len(order)), [f'{GN[g]}（n={(x.grp == g).sum()}）' if not EN else f'{GN[g]} (n={(x.grp == g).sum()})' for g in order]); ax.set_ylim(len(order) - 0.4, -0.6)
ax.axvline(0, color=INK2, lw=0.8); ax.xaxis.set_major_formatter(pct); ax.grid(axis='y', visible=False)
ax.set_xlabel(T('首日收市價相對招股價', 'First-day close vs IPO price'))
ax.set_title(T('定價於範圍上限或以上者，首日無一收市低於招股價', 'Priced at or above the range top: none closed below the IPO price'), loc='left')
note(fig, T(f'樣本：1996–2026 年全球集資 50 億美元以上、有招股價範圍及首日收市價的 IPO（n = {x.grp.isin(order).sum()}；另有 1 宗定價低於範圍，未有顯示）。橙線為中位數；{n_clip} 宗高於 +120% 者以 +120% 顯示。',
            f'Sample: global IPOs raising US$5B or more, 1996–2026, with a price range and a first-day close (n = {x.grp.isin(order).sum()}; 1 more priced below the range is not shown). Orange line = median. {n_clip} values above +120% are drawn at +120%.'))
save(fig, 'fig1_first_day_by_pricing.png')

# Figure 2: trading day of the 60-day high (29 IPOs priced at or above the range top)
px = pd.read_csv('data/price_features.csv'); h = px[px['主樣本']]
p = np.sort(h['60日最高喺第幾日'].to_numpy()); n = len(p)
days = np.arange(1, 61); cum = np.array([(p <= k).mean() for k in days])
fig, ax = plt.subplots(figsize=(8, 4.2)); ax.step(days, cum, where='post', color=BLUE, lw=2)
for k in (1, 3, 10):
    c = (p <= k).mean(); ax.plot(k, c, 'o', ms=8, color=BLUE, mec='white', mew=2, zorder=4)
    ax.annotate(T(f'第 {k} 日或之前：{(p <= k).sum()}／{n}', f'By day {k}: {(p <= k).sum()} of {n}'), (k, c), xytext=(12, -6), textcoords='offset points', fontsize=10, va='top', bbox=dict(fc='white', ec='none', pad=1), zorder=5)
med = int(np.median(p)); ax.axvline(med, color=ORANGE, lw=1.5, ls='--'); ax.text(med + 0.8, 0.95, T(f'中位數：第 {med} 日', f'Median: day {med}'), fontsize=10, va='top')
ax.set_xlim(1, 61); ax.set_ylim(0, 1.02); ax.yaxis.set_major_formatter(pct)
ax.set_xlabel(T('上市後第幾個交易日', 'Trading day after listing (day 1 = listing day)')); ax.set_ylabel(T('已出現 60 日最高價的比例', 'Share whose 60-day high had come'))
ax.set_title(T(f'60 日最高價何時出現：{(p <= 10).sum()}／{n} 宗在 10 個交易日內', f'{(p <= 10).sum()} of {n} comparable IPOs made their 60-day high by trading day 10'), loc='left')
note(fig, T(f'樣本：定價於範圍上限或以上、有 60 個交易日價格的超大型 IPO（n = {n}）。60 日最高價為第 1 至 60 個交易日的最高成交價；同價出現多日取最早一日。',
            f'Sample: mega-IPOs priced at or above the range top with 60 trading days of prices (n = {n}). The 60-day high is the highest intraday price on trading days 1–60; ties go to the earliest day.'))
save(fig, 'fig2_when_peak.png')

# Figure 3: further gains in days 2-10 vs the day-60 close, both relative to the first-day close
X, Y = h['Y10_第2至10日最高對首日收市'], h['Y60_第60日收市對首日收市']
fig, ax = plt.subplots(figsize=(8, 5.2)); ax.axhline(0, color=INK2, lw=0.8); ax.axvline(0, color=INK2, lw=0.8)
ax.scatter(X, Y, s=40, color=BLUE, alpha=0.8, edgecolor='white', linewidth=1, zorder=3)
lab = {'Facebook': (35, 25), 'PetroChina A': (-15, -32), 'Huatai Securities H': (95, 8), 'Visa': (25, -5), 'Alibaba': (-15, 30), 'Rivian': (-60, 30),
       'Arm': (40, 35), 'Saudi Aramco': (45, -25), 'Kuaishou': (25, 20), 'General Motors': (40, 25)}
for _, r in h[h.name.isin(lab)].iterrows():
    ax.annotate(r['name'], (r['Y10_第2至10日最高對首日收市'], r['Y60_第60日收市對首日收市']), xytext=lab[r['name']], textcoords='offset points', fontsize=9.5,
                ha='center', va='center', arrowprops=dict(arrowstyle='-', color=INK2, lw=0.7, shrinkA=2, shrinkB=4), bbox=dict(fc='white', ec='none', pad=1))
ax.xaxis.set_major_formatter(pct); ax.yaxis.set_major_formatter(pct)
ax.set_xlabel(T('第 2 至 10 個交易日最高價相對首日收市價', 'Highest price on trading days 2–10 vs first-day close'))
ax.set_ylabel(T('第 60 個交易日收市價相對首日收市價', 'Day-60 close vs first-day close'))
ax.set_title(T('首兩週是否續升，與第 60 日表現關係不大', 'Further gains in the first two weeks said little about day 60'), loc='left')
note(fig, T(f'每點代表一宗 IPO，樣本為同樣 29 宗熱門 IPO（n = {len(h)}）。例如 Rivian 首日後 5 日內再升 78%，第 60 日收市卻比首日收市低 40%；Alibaba 首 10 日未有再升，第 60 日收市比首日收市高 12%。',
            f'Each dot is one IPO; the same 29 hot IPOs (n = {len(h)}). Rivian rose another 78% within five days of its first close, then ended day 60 40% below it. Alibaba went nowhere for ten days and ended day 60 up 12%.'))
save(fig, 'fig3_day10_vs_day60.png')

# Figure 4: selling the half not sold at the first-day close
sim = pd.read_csv('data/exit_trailing_sim.csv'); s = sim[sim['主樣本']]
cols = ['揸到第10日收市', '跟蹤5%', '跟蹤8%', '跟蹤10%', '跟蹤15%', '跟蹤20%']
names = [T('持有至第 10 日收市', 'Hold to day-10 close')] + [T(f'自高位回落 {k}% 即沽出', f'Sell on a {k}% drop from the high') for k in (5, 8, 10, 15, 20)]
fig, ax = plt.subplots(figsize=(8, 4.4))
for i, c in enumerate(cols):
    v = s[c]; ax.plot([v.min(), v.max()], [i, i], color=GRID, lw=6, solid_capstyle='round', zorder=2)
    ax.plot(v.median(), i, 'o', ms=9, color=BLUE, mec='white', mew=2, zorder=4)
    ax.text(v.max() + 0.02, i, T(f'中位數 {v.median():+.1%}｜最差 {v.min():+.0%}｜最佳 {v.max():+.0%}', f'median {v.median():+.1%} | worst {v.min():+.0%} | best {v.max():+.0%}'), va='center', fontsize=9.5)
ax.axvline(0, color=ORANGE, lw=1.5); ax.text(0.01, -0.62, T('← 0% = 於首日收市沽出餘下一半', '← 0% = selling the second half at the first-day close'), fontsize=9, va='bottom')
ax.set_yticks(range(len(cols)), names); ax.set_ylim(len(cols) - 0.5, -0.8); ax.xaxis.set_major_formatter(pct); ax.grid(axis='y', visible=False)
ax.set_xlim(-0.35, 0.95); ax.set_xlabel(T('首日收市未沽出的一半之回報（相對首日收市價）', 'Return on the half not sold at the first-day close'))
ax.set_title(T('追蹤出場：中位數變化不大，但最差情況明顯改善', 'A trailing exit barely moved the median but cut the worst case'), loc='left')
note(fig, T(f'歷史模擬，樣本為同樣 29 宗熱門 IPO（n = {len(s)}），最遲第 10 日沽出。出場價以前一日為止的最高價計（由首日收市價起）；當日最低價觸及即以出場價成交，若開市已低於出場價則以開市價成交。只用日線，不知盤中先後。灰條為最差至最佳（各為單一 IPO），藍點為中位數。',
            f'Historical simulation, the same 29 hot IPOs (n = {len(s)}), out by day 10 at the latest. The stop is set from the highest price up to the previous day; it fills at the stop when the day\'s low touches it, or at the open if the stock gaps below. Daily prices only, so intraday order is unknown. Grey bar = worst to best (each a single IPO); blue dot = median.'))
save(fig, 'fig4_exit_methods.png')

# Figure 5: buying at the first trade (not at the IPO price): result at the day-one close and at day 60
b = pd.read_csv('data/daily_prices_first70.csv'); tk = h['ticker']
c = b[b.ticker.isin(tk)].pivot(index='ticker', columns='session', values='close_ipo_basis')
o1 = b[b.ticker.isin(tk) & (b.session == 1)].set_index('ticker').open_ipo_basis.reindex(c.index)
rows = [(T('首日收市', 'At the day-one close'), c[1] / o1 - 1), (T('第 60 個交易日收市', 'At the day-60 close'), c[60] / o1 - 1)]
fig, ax = plt.subplots(figsize=(8, 3.6)); rng = np.random.default_rng(2)
for i, (lab_, r) in enumerate(rows):
    r = r.dropna(); col = np.where(r < 0, ORANGE, BLUE)
    ax.scatter(r.clip(-0.6, 0.6), i + rng.uniform(-0.12, 0.12, len(r)), s=34, c=col, alpha=0.85, edgecolor='white', linewidth=0.8, zorder=3)
    ax.text(0.62, i, T(f'{(r < 0).sum()}／{len(r)} 宗虧損', f'{(r < 0).sum()} of {len(r)} lower'), va='center', fontsize=10.5, fontweight='bold')
ax.axvline(0, color=INK2, lw=0.8); ax.set_yticks(range(len(rows)), [r[0] for r in rows]); ax.set_ylim(len(rows) - 0.5, -0.6)
ax.set_xlim(-0.65, 0.85); ax.xaxis.set_major_formatter(pct); ax.grid(axis='y', visible=False)
ax.set_xlabel(T('相對首次成交價的回報（橙色 = 虧損）', 'Return vs the first trade on day one (orange = lost money)'))
ax.set_title(T('首日開市即追入：多數虧損', 'Bought at the very first trade on day one? Most lost money'), loc='left')
note(fig, T(f'同類熱門 IPO（n = {len(c)}）。首次成交價一般已比招股價高 17%。低於 −60% 或高於 +60% 者以 ±60% 顯示。',
            f'The same 29 hot IPOs. The first trade was typically already 17% above the IPO price. Values beyond ±60% are drawn at ±60%.'), y=-0.07)
save(fig, 'fig5_buying_on_day_one.png')
print('[make_figures]', 'en' if EN else 'zh', sorted(os.listdir(OUT)))
