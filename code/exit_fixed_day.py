"""Claude 2026-11-15：驗證「散戶最好頭一至三日內走」呢個講法。比較固定喺第 N 日收市賣（N = 1,2,3,5,10）嘅回報（由招股價計，即係抽中新股嘅人嘅回報），
同埋由首日收市計（首日已經賣咗一半之後，餘下一半嘅回報）。主樣本 29 宗；全部 57 宗做敏感度。輸出畫面同 data/exit_fixed_day.csv"""
import numpy as np, pandas as pd
bars = pd.read_csv('data/daily_prices_first70.csv'); px = pd.read_csv('data/price_features.csv')[['name', 'ticker', '主樣本']]
c = bars[bars.ticker.isin(px.ticker) & (bars.session <= 10)].pivot(index='ticker', columns='session', values='close_ipo_basis')
off = bars[bars.session == 1].set_index('ticker').offer_price.reindex(c.index)
out = px.set_index('ticker').join(pd.DataFrame({f'第{n}日收市_對招股價': c[n] / off - 1 for n in (1, 2, 3, 5, 10)}))
out = out.join(pd.DataFrame({f'第{n}日收市_對首日收市': c[n] / c[1] - 1 for n in (2, 3, 5, 10)}))
out.to_csv('data/exit_fixed_day.csv')
for tag, s in (('主樣本29', out[out.主樣本]), ('全部', out)):
    print(f'== {tag} n={len(s)}')
    cols = [k for k in out.columns if k.startswith('第')]
    print(pd.DataFrame({'中位': s[cols].median(), '平均': s[cols].mean(), '低過招股價或首日收市嘅比例': (s[cols] < 0).mean(), '最差': s[cols].min(), '最好': s[cols].max()}).round(3).to_string())
