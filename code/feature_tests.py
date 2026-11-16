"""The 14 feature tests behind "no reliable signal after day one". Run from the repository root.
Input: data/merged_features.csv (one row per IPO; price-based features computed from data/daily_prices_first70.csv,
deal features collected from prospectuses and allotment announcements). Output: data/feature_tests.csv.
Outcomes: Y10 = highest price on trading days 2-10 vs first-day close; Y60 = day-60 close vs first-day close.
Samples: '主樣本29' = the 29 IPOs priced at or above the range top; '全部' = all 57 IPOs with 60 days of prices.
Spearman correlation for numeric features, Mann-Whitney U for yes/no features; Benjamini-Hochberg q within each sample."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr, mannwhitneyu
d = pd.read_csv('data/merged_features.csv')
Y = ['Y10_第2至10日最高對首日收市', 'Y60_第60日收市對首日收市']
CONT = ['加價幅度%', '超購倍數', '舊股東賣貨%', '散戶%', '營收增長%', '市銷率', '大市_上市前63日回報', '大市_上市前20日年化波幅',
        'r1_首日回報', '首日收市位置', '首日收對開', '首日換手']
BIN = ['加股數', '有盈利']
def run(sample, tag):
    res = []
    for y in Y:
        for x in CONT:
            z = sample[[x, y]].replace([np.inf], 1e9).dropna()
            if len(z) < 5: res.append({'樣本': tag, '結果': y, '特徵': x, 'n': len(z)}); continue
            r, p = spearmanr(z[x], z[y]); zz = z.drop([z[y].idxmax(), z[y].idxmin()]); r2, p2 = spearmanr(zz[x], zz[y])
            res.append({'樣本': tag, '結果': y, '特徵': x, 'n': len(z), 'Spearman_r': r, 'p': p, '剔2宗後_r': r2, '剔2宗後_p': p2})
        for x in BIN:
            z = sample[[x, y]].dropna(); a = z[z[x] == 1][y]; b = z[z[x] == 0][y]
            if min(len(a), len(b)) < 3: res.append({'樣本': tag, '結果': y, '特徵': x, 'n': len(z), 'n_是': len(a), 'n_否': len(b)}); continue
            res.append({'樣本': tag, '結果': y, '特徵': x, 'n': len(z), 'n_是': len(a), 'n_否': len(b), '中位_是': a.median(), '中位_否': b.median(), 'p': mannwhitneyu(a, b).pvalue})
    r = pd.DataFrame(res); ok = r.p.notna() & (r.n >= 10); m = ok.sum(); ps = r.loc[ok, 'p'].sort_values()
    r.loc[ps.index, 'BH_q'] = (ps * m / np.arange(1, m + 1))[::-1].cummin()[::-1].clip(upper=1)
    return r
out = pd.concat([run(d[d['主樣本']], '主樣本29'), run(d, '全部')])
out.to_csv('data/feature_tests.csv', index=False)
for tag in ('主樣本29', '全部'):
    s = out[out['樣本'] == tag]
    print(f'{tag}: {s.p.notna().sum()} tests, smallest p = {s.p.min():.3f}, smallest BH q = {s.BH_q.min():.2f}')
