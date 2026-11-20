"""Score other public, numeric forecasts of ANT's first trading day against the actual result.
Actual: IPO price $83.00 (SEC 424B4), Nasdaq first-day close $97.17, so +17.07%.
Groups: A = analysts and this forecast, before $83 was public (cutoff 2026-11-18 22:11 UTC, when an r/wallstreetbets post titled
"Company said to price stock at $83" went up); B = market prices before the same cutoff; C = after $83 was public, before the open; D = analysts who gave a direction but no number (listed, not scored).
Scoring: a range is a HIT if the actual is inside it; a single number is CLOSE if it is within 5 percentage points
of the actual (the 5pp threshold is my choice, not an industry standard). Only calls that state a first-day close or
first-day return are included. Conditional statements, calls that say they are "not a forecast", unclear time frames
and opening-price calls are left out. Sources: predictions.csv (verbatim quote and URL for each). Random social-media comments are left out on purpose. The list covers what I could find, not every call made.
Usage: python3 score.py"""
import polars as pl

IPO, CLOSE = 83.00, 97.17
ACT = (CLOSE / IPO - 1) * 100
df = pl.read_csv('predictions.csv', infer_schema_length=0).with_columns(
    pl.col('pred_low_pct').cast(pl.Float64), pl.col('pred_high_pct').cast(pl.Float64))
# 價格 → 升幅（%，以 $83 計）
to_pct = lambda c: pl.when(pl.col('kind').str.starts_with('close')).then((pl.col(c) / IPO - 1) * 100).otherwise(pl.col(c))
df = df.filter(pl.col('kind') != 'direction')
df = df.with_columns(lo=to_pct('pred_low_pct'), hi=to_pct('pred_high_pct'))
is_range = pl.col('kind').str.contains('range')
df = df.with_columns(
    err_pp=pl.when(is_range).then(None).otherwise(pl.col('lo') - ACT),
    verdict=pl.when(is_range & (pl.col('lo') <= ACT) & (ACT <= pl.col('hi'))).then(pl.lit('HIT (inside range)'))
             .when(is_range).then(pl.lit('MISS (outside range)'))
             .when((pl.col('lo') - ACT).abs() <= 5).then(pl.lit('CLOSE (within 5pp)'))
             .otherwise(pl.lit('MISS')))
print(f'Actual: ${CLOSE} / ${IPO} - 1 = {ACT:+.2f}%  (n={df.height} calls)\n')
for g, sub in df.group_by('group', maintain_order=True):
    print(f'## {g[0]}  (n={sub.height})')
    for r in sub.iter_rows(named=True):
        e = '' if r['err_pp'] is None else f"  off by {r['err_pp']:+.1f}pp"
        print(f"  {r['time_utc']}  {r['who'][:42]:42}  pred {r['lo']:+.1f}%{'' if r['hi'] is None or r['hi']==r['lo'] else f' to {r[chr(104)+chr(105)]:+.1f}%'}  → {r['verdict']}{e}")
    print('  tally:', dict(sub['verdict'].value_counts().iter_rows()), '\n')
df.write_csv('scored.csv')
