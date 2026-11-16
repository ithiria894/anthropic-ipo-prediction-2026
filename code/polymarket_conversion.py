"""Claude 2026-11-14（11-15 更新機率）：將 Polymarket ANT 市場嘅估值區間換算成每股價，同我哋首日預測比較。
股數來源：S-1/A 2026-11-10「to be outstanding after this offering and the concurrent private placement」：Class A 7,427,991,791；Class N 5,658,680,800；T、F 各 1。
完全攤薄：S-1/A 寫 $78 對應約 $1.405T（傳媒引用）→ 約 18.01B 股（推算）。"""
basic = 7_427_991_791 + 5_658_680_800 + 2
fd = 1.405e12 / 78
print(f'基本股數 {basic/1e9:.3f}B；$78 基本市值 {basic*78/1e12:.3f}T；完全攤薄股數約 {fd/1e9:.2f}B')
print('IPO 估值市場（完全攤薄）區間 → 招股價：')
for lo, hi, p in [(1.25, 1.5, .4615), (1.5, 1.75, .5305), (1.75, 2.0, .0025)]:  # 2026-11-15 gamma-api 快照
    print(f'  {lo}-{hi}T → ${lo*1e12/fd:.1f}–{hi*1e12/fd:.1f}  機率 {p:.1%}')
print('首日收市市值市場（股數×收市價；假設用全部類別基本股數）→ 收市價：')
for lo, hi, p in [(0, 1.25, .219), (1.25, 1.5, .4425), (1.5, 1.75, .1985), (1.75, 2.0, .091), (2.0, 2.25, .047)]:  # 2026-11-15 gamma-api 快照
    print(f'  {lo}-{hi}T → ${lo*1e12/basic:.1f}–{hi*1e12/basic:.1f}  機率 {p:.1%}')
