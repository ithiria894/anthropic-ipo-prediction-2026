"""What if you did NOT get IPO shares and bought on the market instead? Buy at the first-day open, or at the first-day close,
then measure the return to the day-10 and day-60 close. Sample: the 29 IPOs priced at or above the range top with 60 days of prices.
Input: data/daily_prices_first70.csv, data/price_features.csv. Run from the repository root."""
import pandas as pd
b = pd.read_csv('data/daily_prices_first70.csv'); px = pd.read_csv('data/price_features.csv')
t = px.loc[px['主樣本'], 'ticker']
c = b[b.ticker.isin(t)].pivot(index='ticker', columns='session', values='close_ipo_basis')
o1 = b[b.ticker.isin(t) & (b.session == 1)].set_index('ticker').open_ipo_basis.reindex(c.index)
for name, entry in (('first-day open', o1), ('first-day close', c[1])):
    for d in (1, 10, 60):
        if name == 'first-day close' and d == 1: continue
        r = c[d] / entry - 1
        print(f'Buy at {name}, sell at day-{d} close: n={r.notna().sum()}, median {r.median():+.1%}, lower than entry in {(r < 0).sum()} of {r.notna().sum()}, worst {r.min():+.0%}, best {r.max():+.0%}')
r1o = o1 / b[b.ticker.isin(t) & (b.session == 1)].set_index('ticker').offer_price.reindex(c.index) - 1
print(f'First-day open vs IPO price: median {r1o.median():+.1%} (n={r1o.notna().sum()})')

# Day one, bought at the open: how far above the open did the price go at its best moment, and where did it close?
d1 = b[b.ticker.isin(t) & (b.session == 1)].set_index('ticker')
up = d1.high_ipo_basis / d1.open_ipo_basis - 1; cl = d1.close_ipo_basis / d1.open_ipo_basis - 1
print(f'Day one, from the open: best moment median {up.median():+.1%} (at least +5% in {(up >= 0.05).sum()} of {up.notna().sum()}); close median {cl.median():+.1%}, lower than the open in {(cl < 0).sum()} of {cl.notna().sum()}')
