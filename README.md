# AlphaQuant Sentiment Dashboard

**Live Demo:** [https://alphaquant-sentiment-dashboard.vercel.app/](https://alphaquant-sentiment-dashboard.vercel.app/)

## 📌 Problem Statement
The objective of this assignment is to explore the relationship between trader performance and market sentiment, uncover hidden patterns, and deliver data-driven insights that can drive smarter trading strategies. This is achieved by analyzing two primary datasets: a Bitcoin Market Sentiment Dataset (tracking daily Fear/Greed index classifications) and a massive Historical Trader Dataset from Hyperliquid (containing granular execution data including accounts, sizes, execution prices, sides, and closed PnL).

## ⚙️ Data Pipeline
To extract meaningful signals, the raw data was processed through a robust quantitative pipeline:
* **Preprocessing:** Cleaned raw Hyperliquid execution data by casting PnL, Volume (Size USD), and Fees to numeric types. Removed corrupted or incomplete transaction records to maintain data integrity.
* **Date Normalization:** Parsed complex intraday timestamps from the execution data into standardized datetime formats (`trade_date`), ensuring exact synchronization across both datasets.
* **Merging Datasets:** Performed a time-series left-join, aligning the daily Bitcoin Fear & Greed index values to the exact intraday trade execution timestamps. This connected every individual trade to the broader market regime of that day.
* **Sentiment Mapping:** Mapped raw continuous sentiment values into 5 discrete categorical buckets: *Extreme Fear (0-25)*, *Fear (26-45)*, *Neutral (46-55)*, *Greed (56-75)*, and *Extreme Greed (76-100)*. Applied forward-filling (ffill) logic to handle missing sentiment indices over weekends.

## ❓ Analytical Questions Addressed
The dashboard was built to quantitatively answer key strategic questions:
* **Does trader profitability increase during greed?** (Analyzed via *PnL by Market Sentiment*)
* **Are shorts more profitable during extreme greed or extreme fear?** (Analyzed via *Long vs Short Performance by Sentiment*)
* **Which market regime yields the highest win rate?** (Analyzed via the *Win Rate vs Sentiment* trendline)
* **Does volume conviction (sizing) increase with sentiment intensity?** (Analyzed by aggregating total volume against index classifications)

## 💡 Key Insights
* **Asymmetric Payoffs in Extreme Regimes:** The highest aggregate PnL was generated during extreme market conditions (Extreme Fear and Extreme Greed), suggesting that high volatility environments provide the optimal backdrop for alpha generation.
* **Directional Edge (Long vs Short):** Directional bias plays a massive role in profitability; trade-side aggregations reveal shifting success rates for Longs vs Shorts depending on whether the market is fearful or greedy.
* **High Conviction Sizing:** Average trade volume and sizing increased significantly during periods of Greed and Extreme Greed as traders leaned into momentum.
* **Risk-Adjusted Defense:** Despite fluctuating win rates, top decile traders maintained strict risk management (cutting losses early) allowing them to generate highly positive returns even in choppy, neutral markets.
* **Flight to Quality:** Large volume flows heavily correlated with BTC and ETH pairs during sudden sentiment downswings as capital rotated away from altcoins.

## 💻 Tech Stack
* **Data Engineering & Analysis:** Python (Pandas) for data wrangling, merging, aggregation, and JSON generation.
* **Frontend UI:** HTML5, CSS3 (Custom Glassmorphism Design System), Vanilla JavaScript.
* **Data Visualization:** Chart.js for rendering dynamic, responsive canvas charts.
* **Deployment & Hosting:** Deployed on Vercel with continuous integration via GitHub.
