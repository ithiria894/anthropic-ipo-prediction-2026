"""Claude 2026-11-14：用真交易日序號（session）重計 60 日最高位幾時出現，取代 ../claude_高位幾時出現.py 嘅平日估算。輸出畫面。"""
import pandas as pd
d = pd.read_csv('data/price_features.csv')
for tag, s in (('主樣本29', d[d.主樣本]), ('全部', d)):
    p = s['60日最高喺第幾日']
    print(f'{tag}: n={len(s)} 第1日 {(p<=1).mean():.0%}（{(p<=1).sum()}）、頭3日 {(p<=3).mean():.0%}（{(p<=3).sum()}）、頭10日 {(p<=10).mean():.0%}（{(p<=10).sum()}）、中位第 {p.median():.0f} 日')
