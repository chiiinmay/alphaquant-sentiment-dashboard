
import pandas as pd
import json
from collections import defaultdict
import re

# ── Load Data ────────────────────────────────────────────────────────────────
print("Loading datasets...")
trades = pd.read_csv(r"c:\Users\User\Downloads\historical_data.csv")
fg = pd.read_csv(r"c:\Users\User\Downloads\fear_greed_index.csv")

print(f"Trades rows: {len(trades):,}")
print(f"Fear/Greed rows: {len(fg):,}")
print("\nTrades columns:", list(trades.columns))
print("F/G columns:", list(fg.columns))

# ── Clean Trades ─────────────────────────────────────────────────────────────
trades.columns = [c.strip() for c in trades.columns]

# Parse date from "Timestamp IST" column (format: DD-MM-YYYY HH:MM)
trades['date_str'] = trades['Timestamp IST'].astype(str).str.extract(r'(\d{2}-\d{2}-\d{4})', expand=False)
trades['trade_date'] = pd.to_datetime(trades['date_str'], format='%d-%m-%Y', errors='coerce')

# Clean PnL
trades['Closed PnL'] = pd.to_numeric(trades['Closed PnL'], errors='coerce').fillna(0)
trades['Size USD'] = pd.to_numeric(trades['Size USD'], errors='coerce').fillna(0)
trades['Fee'] = pd.to_numeric(trades['Fee'], errors='coerce').fillna(0)

# ── Clean Fear/Greed ──────────────────────────────────────────────────────────
fg['date'] = pd.to_datetime(fg['date'], errors='coerce')
fg['value'] = pd.to_numeric(fg['value'], errors='coerce')

# ── Merge ─────────────────────────────────────────────────────────────────────
merged = trades.merge(fg[['date','value','classification']], 
                      left_on='trade_date', right_on='date', how='left')
merged = merged.dropna(subset=['classification'])

print(f"\nMerged rows (with sentiment match): {len(merged):,}")
print("Sentiment distribution:\n", merged['classification'].value_counts())

# ── Analysis 1: PnL by Sentiment ─────────────────────────────────────────────
pnl_by_sentiment = merged.groupby('classification').agg(
    total_pnl=('Closed PnL', 'sum'),
    avg_pnl=('Closed PnL', 'mean'),
    trade_count=('Closed PnL', 'count'),
    profitable_trades=('Closed PnL', lambda x: (x > 0).sum()),
    losing_trades=('Closed PnL', lambda x: (x < 0).sum()),
    total_volume=('Size USD', 'sum'),
    avg_volume=('Size USD', 'mean'),
).reset_index()
pnl_by_sentiment['win_rate'] = (pnl_by_sentiment['profitable_trades'] / pnl_by_sentiment['trade_count'] * 100).round(2)
pnl_by_sentiment['avg_pnl'] = pnl_by_sentiment['avg_pnl'].round(4)
pnl_by_sentiment['total_pnl'] = pnl_by_sentiment['total_pnl'].round(2)
pnl_by_sentiment['total_volume'] = pnl_by_sentiment['total_volume'].round(2)

print("\n=== PnL by Sentiment ===")
print(pnl_by_sentiment[['classification','total_pnl','avg_pnl','trade_count','win_rate','total_volume']])

# ── Analysis 2: Buy vs Sell by Sentiment ─────────────────────────────────────
side_sentiment = merged.groupby(['classification', 'Side']).size().reset_index(name='count')
side_pivot = side_sentiment.pivot(index='classification', columns='Side', values='count').fillna(0)
print("\n=== Buy/Sell by Sentiment ===")
print(side_pivot)

# ── Analysis 3: Coin/Asset by Sentiment ──────────────────────────────────────
coin_sentiment = merged.groupby(['classification', 'Coin']).agg(
    total_pnl=('Closed PnL','sum'),
    trade_count=('Closed PnL','count')
).reset_index()
top_coins_pnl = coin_sentiment.groupby('Coin')['total_pnl'].sum().nlargest(10).index.tolist()
coin_sentiment_top = coin_sentiment[coin_sentiment['Coin'].isin(top_coins_pnl)]
print("\n=== Top Coins by Sentiment ===")
print(coin_sentiment_top)

# ── Analysis 4: Monthly Trend ─────────────────────────────────────────────────
merged['month'] = merged['trade_date'].dt.to_period('M').astype(str)
monthly = merged.groupby(['month','classification']).agg(
    total_pnl=('Closed PnL','sum'),
    trade_count=('Closed PnL','count')
).reset_index()

# ── Analysis 5: Overall Stats ─────────────────────────────────────────────────
total_pnl = merged['Closed PnL'].sum()
total_trades = len(merged)
total_volume = merged['Size USD'].sum()
profitable = (merged['Closed PnL'] > 0).sum()
losing = (merged['Closed PnL'] < 0).sum()
overall_win_rate = profitable / total_trades * 100
unique_accounts = merged['Account'].nunique()
unique_coins = merged['Coin'].nunique()

print(f"\n=== Overall Stats ===")
print(f"Total PnL: ${total_pnl:,.2f}")
print(f"Total Trades: {total_trades:,}")
print(f"Total Volume: ${total_volume:,.2f}")
print(f"Win Rate: {overall_win_rate:.2f}%")
print(f"Unique Accounts: {unique_accounts}")
print(f"Unique Coins: {unique_coins}")

# ── Analysis 6: Sentiment distribution of profitable trades ──────────────────
profitable_by_sentiment = merged[merged['Closed PnL'] > 0].groupby('classification').size()
losing_by_sentiment = merged[merged['Closed PnL'] < 0].groupby('classification').size()

# ── Analysis 7: Fear/Greed value bucketed ────────────────────────────────────
merged['fg_bucket'] = pd.cut(merged['value'], 
                              bins=[0,25,45,55,75,100], 
                              labels=['Extreme Fear\n(0-25)', 'Fear\n(26-45)', 'Neutral\n(46-55)', 'Greed\n(56-75)', 'Extreme Greed\n(76-100)'])
bucket_pnl = merged.groupby('fg_bucket', observed=True).agg(
    total_pnl=('Closed PnL','sum'),
    avg_pnl=('Closed PnL','mean'),
    trade_count=('Closed PnL','count'),
    win_rate=('Closed PnL', lambda x: (x>0).mean()*100)
).reset_index()
print("\n=== PnL by FG Bucket ===")
print(bucket_pnl)

# ── Analysis 8: Top traders ───────────────────────────────────────────────────
trader_perf = merged.groupby('Account').agg(
    total_pnl=('Closed PnL','sum'),
    trade_count=('Closed PnL','count'),
    total_volume=('Size USD','sum'),
    win_rate=('Closed PnL', lambda x: (x>0).mean()*100)
).reset_index().sort_values('total_pnl', ascending=False)
print("\n=== Top Traders ===")
print(trader_perf.head(10))

# ── Analysis 9: Direction analysis ───────────────────────────────────────────
direction_sentiment = merged.groupby(['classification','Direction']).agg(
    total_pnl=('Closed PnL','sum'),
    count=('Closed PnL','count')
).reset_index()

# ── Build JSON for dashboard ──────────────────────────────────────────────────
SENTIMENT_ORDER = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']

def safe_dict(df, key_col, val_col):
    return dict(zip(df[key_col].tolist(), df[val_col].tolist()))

pnl_by_s = pnl_by_sentiment.set_index('classification')
monthly_data = {}
for _, row in monthly.iterrows():
    m = row['month']
    if m not in monthly_data:
        monthly_data[m] = {}
    monthly_data[m][row['classification']] = round(row['total_pnl'], 2)

top_trader_list = []
for _, row in trader_perf.head(10).iterrows():
    acct = str(row['Account'])
    short = acct[:6]+"..."+acct[-4:] if len(acct)>12 else acct
    top_trader_list.append({
        'account': short,
        'total_pnl': round(row['total_pnl'], 2),
        'trade_count': int(row['trade_count']),
        'total_volume': round(row['total_volume'], 2),
        'win_rate': round(row['win_rate'], 2)
    })

coin_pnl = merged.groupby('Coin')['Closed PnL'].sum().sort_values(ascending=False).head(10)
coin_volume = merged.groupby('Coin')['Size USD'].sum().sort_values(ascending=False).head(10)

# Distribution data for fear/greed index over the trading period
fg_dist = fg.groupby('classification').size().reset_index(name='count')
fg_dist_dict = dict(zip(fg_dist['classification'], fg_dist['count']))

# Time series: daily PnL & sentiment
daily_pnl = merged.groupby('trade_date').agg(
    daily_pnl=('Closed PnL','sum'),
    fg_value=('value','mean'),
    classification=('classification','first')
).reset_index().sort_values('trade_date')

time_series = []
for _, row in daily_pnl.iterrows():
    if pd.notna(row['trade_date']):
        time_series.append({
            'date': str(row['trade_date'].date()),
            'pnl': round(row['daily_pnl'], 2),
            'fg': round(row['fg_value'], 1) if pd.notna(row['fg_value']) else None,
            'sentiment': row['classification']
        })

data = {
    "overall": {
        "total_pnl": round(total_pnl, 2),
        "total_trades": int(total_trades),
        "total_volume": round(total_volume, 2),
        "win_rate": round(overall_win_rate, 2),
        "unique_accounts": int(unique_accounts),
        "unique_coins": int(unique_coins),
        "profitable": int(profitable),
        "losing": int(losing)
    },
    "sentiment_pnl": {
        s: {
            "total_pnl": round(float(pnl_by_s.loc[s,'total_pnl']), 2) if s in pnl_by_s.index else 0,
            "avg_pnl": round(float(pnl_by_s.loc[s,'avg_pnl']), 4) if s in pnl_by_s.index else 0,
            "trade_count": int(pnl_by_s.loc[s,'trade_count']) if s in pnl_by_s.index else 0,
            "win_rate": round(float(pnl_by_s.loc[s,'win_rate']), 2) if s in pnl_by_s.index else 0,
            "total_volume": round(float(pnl_by_s.loc[s,'total_volume']), 2) if s in pnl_by_s.index else 0,
        }
        for s in SENTIMENT_ORDER if s in pnl_by_s.index
    },
    "side_by_sentiment": {
        s: {
            "BUY": int(side_pivot.loc[s,'BUY']) if s in side_pivot.index and 'BUY' in side_pivot.columns else 0,
            "SELL": int(side_pivot.loc[s,'SELL']) if s in side_pivot.index and 'SELL' in side_pivot.columns else 0
        }
        for s in SENTIMENT_ORDER if s in side_pivot.index
    },
    "coin_pnl": {str(k): round(float(v), 2) for k, v in coin_pnl.items()},
    "coin_volume": {str(k): round(float(v), 2) for k, v in coin_volume.items()},
    "top_traders": top_trader_list,
    "time_series": time_series,
    "fg_distribution": fg_dist_dict,
    "monthly_pnl": monthly_data,
    "bucket_pnl": {
        str(row['fg_bucket']): {
            "total_pnl": round(float(row['total_pnl']), 2),
            "avg_pnl": round(float(row['avg_pnl']), 4),
            "trade_count": int(row['trade_count']),
            "win_rate": round(float(row['win_rate']), 2)
        }
        for _, row in bucket_pnl.iterrows()
    }
}

with open(r"c:\Users\User\OneDrive\Desktop\anything.ai\analysis_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("\n✅ analysis_data.json written successfully!")
print(json.dumps(data['overall'], indent=2))
