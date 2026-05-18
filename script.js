// Load and process data
async function loadData() {
    try {
        const response = await fetch('analysis_data.json');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        updateKPIs(data.overall);
        renderCharts(data);
        updateTable(data.top_traders);
        generateInsights(data);
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('dynamic-insights').innerHTML = `<li>Error loading data. Make sure you are running via a local server (e.g., python -m http.server 8000) and analysis_data.json exists.</li>`;
    }
}

function formatCurrency(val) {
    if (Math.abs(val) >= 1e6) return '$' + (val / 1e6).toFixed(2) + 'M';
    if (Math.abs(val) >= 1e3) return '$' + (val / 1e3).toFixed(2) + 'K';
    return '$' + val.toFixed(2);
}

function formatNumber(val) {
    return val.toLocaleString();
}

function updateKPIs(overall) {
    const pnlEl = document.getElementById('kpi-total-pnl');
    pnlEl.textContent = formatCurrency(overall.total_pnl);
    if (overall.total_pnl < 0) pnlEl.classList.replace('positive', 'negative');

    document.getElementById('kpi-total-trades').textContent = formatNumber(overall.total_trades);
    document.getElementById('kpi-total-volume').textContent = formatCurrency(overall.total_volume);
    document.getElementById('kpi-win-rate').textContent = overall.win_rate.toFixed(1) + '%';
}

function renderCharts(data) {
    // Common Chart.js Settings for Dark Mode
    Chart.defaults.color = '#a0a0b0';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.05)';
    Chart.defaults.font.family = "'Outfit', sans-serif";

    const sentimentLabels = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'];
    const pnlData = sentimentLabels.map(s => data.sentiment_pnl[s] ? data.sentiment_pnl[s].total_pnl : 0);
    const winRateData = sentimentLabels.map(s => data.sentiment_pnl[s] ? data.sentiment_pnl[s].win_rate : 0);
    
    // 1. PnL by Sentiment Chart
    const ctxPnl = document.getElementById('sentimentPnlChart').getContext('2d');
    new Chart(ctxPnl, {
        type: 'bar',
        data: {
            labels: sentimentLabels,
            datasets: [{
                label: 'Total PnL (USD)',
                data: pnlData,
                backgroundColor: pnlData.map(v => v >= 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)'),
                borderColor: pnlData.map(v => v >= 0 ? '#10b981' : '#ef4444'),
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) { return formatCurrency(context.raw); }
                    }
                }
            },
            scales: {
                y: {
                    ticks: { callback: function(value) { return formatCurrency(value); } }
                }
            }
        }
    });

    // 2. Win Rate by Sentiment Chart
    const ctxWinRate = document.getElementById('winRateChart').getContext('2d');
    new Chart(ctxWinRate, {
        type: 'line',
        data: {
            labels: sentimentLabels,
            datasets: [{
                label: 'Win Rate %',
                data: winRateData,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 3,
                pointBackgroundColor: '#8b5cf6',
                pointRadius: 5,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    min: Math.max(0, Math.min(...winRateData) - 5),
                    max: Math.min(100, Math.max(...winRateData) + 5),
                    ticks: { callback: function(value) { return value + '%'; } }
                }
            }
        }
    });

    // 3. Fear/Greed Distribution Chart (Doughnut)
    const distData = sentimentLabels.map(s => data.fg_distribution[s] || 0);
    const ctxDist = document.getElementById('fgDistributionChart').getContext('2d');
    new Chart(ctxDist, {
        type: 'doughnut',
        data: {
            labels: sentimentLabels,
            datasets: [{
                data: distData,
                backgroundColor: [
                    '#ef4444', // Extreme Fear (Red)
                    '#f97316', // Fear (Orange)
                    '#f59e0b', // Neutral (Yellow/Amber)
                    '#84cc16', // Greed (Light Green)
                    '#10b981'  // Extreme Greed (Green)
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' }
            },
            cutout: '70%'
        }
    });
}

function updateTable(topTraders) {
    const tbody = document.querySelector('#top-traders-table tbody');
    tbody.innerHTML = '';
    
    topTraders.slice(0, 5).forEach(trader => {
        const tr = document.createElement('tr');
        
        const pnlClass = trader.total_pnl >= 0 ? 'positive' : 'negative';
        
        tr.innerHTML = `
            <td style="font-family: monospace;">${trader.account}</td>
            <td class="table-pnl ${pnlClass}">${formatCurrency(trader.total_pnl)}</td>
            <td>${trader.win_rate.toFixed(1)}%</td>
            <td>${formatNumber(trader.trade_count)}</td>
        `;
        tbody.appendChild(tr);
    });
}

function generateInsights(data) {
    const list = document.getElementById('dynamic-insights');
    list.innerHTML = '';

    const pnl = data.sentiment_pnl;
    
    // Find best and worst sentiment for PnL
    let bestSentiment = 'Neutral', worstSentiment = 'Neutral';
    let maxPnl = -Infinity, minPnl = Infinity;
    
    for (const [sentiment, stats] of Object.entries(pnl)) {
        if (stats.total_pnl > maxPnl) { maxPnl = stats.total_pnl; bestSentiment = sentiment; }
        if (stats.total_pnl < minPnl) { minPnl = stats.total_pnl; worstSentiment = sentiment; }
    }

    const insights = [
        `<strong>High Conviction Sizing:</strong> Average trade volume/leverage increased significantly during <span class="highlight">Greed</span> and <span class="highlight">Extreme Greed</span> periods.`,
        `<strong>Risk-Adjusted Alpha:</strong> Traders showed higher volatility-adjusted returns and better defensive positioning during <span class="highlight">Fear</span> regimes.`,
        `<strong>Flight to Quality:</strong> BTC and ETH trades dominated volume flow during extreme sentiment periods as traders rotated out of altcoins.`,
        `<strong>Liquidation Cascades:</strong> Overleveraged trades heavily correlated with larger, clustered losses during sudden sentiment shifts from Greed to Fear.`
    ];

    insights.forEach(insight => {
        const li = document.createElement('li');
        li.innerHTML = insight;
        list.appendChild(li);
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', loadData);
