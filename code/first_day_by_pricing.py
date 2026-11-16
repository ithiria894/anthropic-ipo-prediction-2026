"""Claude 2026-11-14：超大型 IPO 首日收市回報（由招股價計），按定價相對範圍分組，用嚟估 ANT 首日。"""
import numpy as np, pandas as pd
d = pd.read_csv('data/mega_ipos.csv')
# 用已校正嘅 first_close_from_offer_pct（處理咗拆股同貨幣）；直接 first_close ÷ offer_price 會將 Deutsche Telekom（DEM 招股、EUR 收市）計成 −41%
d['r1'] = pd.to_numeric(d.first_close_from_offer_pct, errors='coerce') / 100
# 用人手核對過嘅 pricing_group 欄（只有上限、固定價等唔算有範圍；CATL H 係「只有上限」）
GMAP = {'加價': '加價', '範圍頂': '範圍頂', '範圍內': '範圍內', '減價': '減價'}
g = d.pricing_group.map(GMAP).fillna('冇範圍')
d['組'] = g
x = d.dropna(subset=['r1'])
rng = np.random.default_rng(20261114)
for k, s in x.groupby('組').r1:
    b = [np.median(rng.choice(s.to_numpy(), len(s))) for _ in range(2000)] if len(s) > 2 else [np.nan]
    print(f"{k}: n={len(s)} 中位 {s.median():+.1%}  平均 {s.mean():+.1%}  95%CI(中位) [{np.nanpercentile(b,2.5):+.1%}, {np.nanpercentile(b,97.5):+.1%}]  跌嘅比例 {(s<0).mean():.0%}")
print('全部:', f"n={len(x)} 中位 {x.r1.median():+.1%} 平均 {x.r1.mean():+.1%} 跌 {(x.r1<0).mean():.0%}")
print(x[x.name.str.contains('SpaceX|Arm|Alibaba|Aramco|Facebook|Visa', case=False, na=False)][['name','offer_price','first_close','r1','組']].to_string())
