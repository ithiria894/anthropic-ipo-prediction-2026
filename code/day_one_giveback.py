"""Day-one winners vs the rest: day-60 return from the first-day close, and the share above the first close at day 60.
Input: data/merged_features.csv (all 57 IPOs with 60 trading days of prices). Run from the repository root."""
import pandas as pd
from scipy.stats import mannwhitneyu
d = pd.read_csv('data/merged_features.csv')
y, r1 = d['Y60_第60日收市對首日收市'], d['r1_首日回報']
a, b = y[r1 >= 0.20], y[r1 < 0.20]
print(f'All 57: day-one up >=20%: n={len(a)}, median day-60 {a.median():+.1%}; others: n={len(b)}, median {b.median():+.1%}; Mann-Whitney p={mannwhitneyu(a, b).pvalue:.2f}')
h = d[d['主樣本']]
print(f"29 priced at/above the range top: {(h['Y60_第60日收市對首日收市'] > 0).sum()} of {len(h)} above their first close at day 60; "
      f"median day-60 {h['Y60_第60日收市對首日收市'].median():+.1%}; {(h['Y10_第2至10日最高對首日收市'] >= 0.05).sum()} rose at least 5% more within days 2-10")
