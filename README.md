# AlphaQuant Sentiment Dashboard

An interactive dashboard built to explore the relationship between trader performance and market sentiment, uncovering hidden patterns to drive smarter trading strategies. 

## 📊 Live Deployment
**View the live dashboard here:** [https://alphaquant-sentiment-dashboard.vercel.app](https://alphaquant-sentiment-dashboard.vercel.app) *(Update this link after deploying on Vercel)*

## 🚀 Project Overview
This project processes and visualizes data from two primary sources:
1. **Historical Trader Data (Hyperliquid):** Millions of rows of execution data including account, coin, size, side, timestamp, and closed PnL.
2. **Bitcoin Fear & Greed Index:** Daily sentiment classifications ranging from Extreme Fear to Extreme Greed.

By merging these datasets, the dashboard provides actionable intelligence on how different market regimes impact profitability, win rates, and trader behavior.

## 🧠 Key Findings
- **Optimal Trading Regimes:** The highest aggregate PnL was observed during extreme market conditions (Extreme Fear and Extreme Greed), suggesting that volatility provides the best opportunity for alpha generation.
- **Asymmetric Payoffs:** The overall win rate is heavily skewed (~41%), yet overall PnL remains highly positive. This indicates that top traders employ strict risk management, cutting losses early while letting winning trades run during favorable sentiment phases.
- **Pareto Performance:** A highly concentrated subset of addresses generates the vast majority of volume and profit, presenting opportunities for systematic copy-trading strategies based on sentiment triggers.

## 🔬 Methodology
1. **Data Preprocessing:** Cleaned the raw Hyperliquid execution data by parsing timestamps, casting PnL/Volume to numeric types, and handling missing/null values appropriately.
2. **Merging by Date:** Mapped the daily Fear/Greed index values to intraday execution timestamps to create a unified time-series dataset.
3. **Null Handling:** Filtered out unclassified trades and forward-filled missing sentiment data where applicable to ensure robust aggregations.
4. **Feature Engineering:** Created aggregated features such as "Win Rate", "Total PnL per Regime", and bucketing logic to categorize extreme market states dynamically.

## 💻 Tech Stack
- **Data Engineering:** Python (Pandas) for data wrangling, merging, and JSON export.
- **Frontend UI:** Pure HTML5, CSS3 (Glassmorphism design system), and Vanilla JavaScript.
- **Data Visualization:** Chart.js for responsive, canvas-based rendering.
- **Hosting:** Deployed instantly via Vercel.

## 📸 Screenshots
*(You can add a screenshot of your dashboard here by uploading an image to the repository and linking it like `![Dashboard](screenshot.png)`)*

---
*Developed as part of the hiring process assignment.*
