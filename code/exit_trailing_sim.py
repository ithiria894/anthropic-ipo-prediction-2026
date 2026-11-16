"""Claude 2026-11-14：模擬「首日賣一半＋餘下跟蹤止盈、最遲第 10 日清」入面「餘下一半」嘅回報（由首日收市計）。規則見 spec_分析.md 附加段。
輸入：data/daily_prices_first70.csv、data/price_features.csv（攞樣本）；輸出：data/exit_trailing_sim.csv"""
import numpy as np, pandas as pd
bars = pd.read_csv('data/daily_prices_first70.csv')
px = pd.read_csv('data/price_features.csv')[['name', 'ticker', '主樣本']]
b = bars[bars.ticker.isin(px.ticker) & (bars.session <= 10)].pivot(index='ticker', columns='session')
O, H, L, C = (b[f'{k}_ipo_basis'].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
c1 = C[:, 0]
L = np.where(np.isnan(L), np.fmin(O, C), L)  # 冇 low（例如 Porsche 首日）用開收較低者
prev_peak = np.maximum.accumulate(np.column_stack([c1, H[:, 1:]]), axis=1)[:, :-1]  # 第 2..10 日「之前」嘅高位（第 2 日 = 首日收市）
res = {'ticker': b.index, '首日全賣': 0.0, '揸到第10日收市': C[:, 9] / c1 - 1}
for t in (0.05, 0.08, 0.10, 0.15, 0.20):
    stop = prev_peak * (1 - t)                       # shape (n, 9)：第 2..10 日嘅止盈價
    hit = L[:, 1:] <= stop
    first = np.where(hit.any(axis=1), hit.argmax(axis=1), -1)
    idx = np.arange(len(c1))
    fill = np.fmin(O[:, 1:], stop)[idx, np.maximum(first, 0)]
    exitp = np.where(first >= 0, fill, C[:, 9])
    res[f'跟蹤{int(t*100)}%'] = exitp / c1 - 1
    res[f'跟蹤{int(t*100)}%_出場日'] = np.where(first >= 0, first + 2, 10)
out = px.merge(pd.DataFrame(res), on='ticker'); out.to_csv('data/exit_trailing_sim.csv', index=False)
cols = ['首日全賣', '揸到第10日收市'] + [f'跟蹤{k}%' for k in (5, 8, 10, 15, 20)]
for tag, s in (('主樣本29', out[out.主樣本]), ('全部', out)):
    print(f'== {tag} n={len(s)}')
    print(pd.DataFrame({'中位': s[cols].median(), '平均': s[cols].mean(), '最差': s[cols].min(), '最好': s[cols].max(), '贏首日全賣比例': (s[cols] > 0).mean()}).round(3).to_string())
print(out[out.主樣本].sort_values('揸到第10日收市')[['name'] + cols].round(3).to_string())
