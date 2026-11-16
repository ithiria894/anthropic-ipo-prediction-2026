"""Claude 2026-11-14：超大型 IPO 現有特徵同首日／60 日表現嘅關係（探索性，n 細，唔係定論）。"""
import re, numpy as np, pandas as pd
from scipy.stats import spearmanr, mannwhitneyu
d = pd.read_csv('data/mega_ipos.csv')
def ov(s):
    m = re.search(r'([\d.]+)\s*(倍|x|X|times)', str(s)); m2 = re.search(r'([\d.]+)%', str(s))
    if m and re.search(r'超過|more than|>', str(s)): return float(m.group(1)) + 0.01  # 「超過 10 倍」算入高一組
    return float(m.group(1)) if m else (float(m2.group(1)) / 100 if m2 and float(m2.group(1)) > 100 else np.nan)
d['超購倍數'] = d.oversubscription.map(ov)
d['加價幅度%'] = pd.to_numeric(d.offer_vs_initial_top_pct, errors='coerce')
d['有盈利'] = pd.to_numeric(d.profit, errors='coerce') > 0
d['集資USDbn'] = pd.to_numeric(d.gross_usd_bn, errors='coerce')
d['首日%'] = pd.to_numeric(d.first_close_from_offer_pct, errors='coerce')
d['首日收市→60日%'] = pd.to_numeric(d.day60_close_from_first_close_pct, errors='coerce')
for y in ['首日%', '首日收市→60日%']:
    print(f'== {y}')
    for x in ['超購倍數', '加價幅度%', '集資USDbn']:
        z = d[[x, y]].dropna(); r, p = spearmanr(z[x], z[y]); print(f'  {x}: n={len(z)} Spearman r={r:+.2f} p={p:.3f}')
    a = d.loc[d.有盈利, y].dropna(); b = d.loc[~d.有盈利, y].dropna()
    print(f'  有盈利 n={len(a)} 中位 {a.median():+.1f}% vs 虧損 n={len(b)} 中位 {b.median():+.1f}%  Mann-Whitney p={mannwhitneyu(a, b).pvalue:.3f}')
    hot = d[d['首日%'] >= 20]; mild = d[(d['首日%'] < 20)]
    if y == '首日收市→60日%':
        print(f'  首日升≥20%：之後 60 日中位 {hot[y].median():+.1f}% (n={hot[y].notna().sum()})；首日<20%：{mild[y].median():+.1f}% (n={mild[y].notna().sum()})')
d[['name','超購倍數','加價幅度%','有盈利','集資USDbn','首日%','首日收市→60日%']].to_csv('data/features_vs_returns.csv', index=False)
print('== 超購倍數分組 → 首日%')
b = pd.cut(d['超購倍數'], [0, 3, 6, 10, np.inf], labels=['<3倍', '3–6倍', '6–10倍', '>10倍'])
print(d.groupby(b, observed=True)['首日%'].agg(['count', 'median', lambda s: (s < 0).mean()]).rename(columns={'<lambda_0>': '跌比例'}).round(1).to_string())
