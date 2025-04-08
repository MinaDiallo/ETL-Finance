-- Requêtes pour les rapports financiers

-- BEGIN DAILY_REPORT
SELECT 
    symbol,
    date,
    close,
    ma_20,
    ma_50,
    CASE 
        WHEN ma_20 > ma_50 THEN 'BULLISH'
        WHEN ma_20 < ma_50 THEN 'BEARISH'
        ELSE 'NEUTRAL'
    END as trend_signal,
    volatility as daily_risk
FROM processed.stock_metrics
WHERE date = (SELECT MAX(date) FROM processed.stock_metrics)
ORDER BY symbol;
-- END DAILY_REPORT

-- BEGIN WEEKLY_REPORT
WITH latest_dates AS (
    SELECT 
        symbol,
        MAX(date) as latest_date,
        date_trunc('week', MAX(date)) as week_start
    FROM processed.stock_metrics
    GROUP BY symbol, date_trunc('week', date)
)
SELECT 
    sm.symbol,
    ld.week_start,
    FIRST_VALUE(sm.close) OVER (PARTITION BY sm.symbol ORDER BY sm.date) as week_open,
    LAST_VALUE(sm.close) OVER (PARTITION BY sm.symbol ORDER BY sm.date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as week_close,
    MAX(sm.close) OVER (PARTITION BY sm.symbol) as week_high,
    MIN(sm.close) OVER (PARTITION BY sm.symbol) as week_low,
    AVG(sm.volatility) OVER (PARTITION BY sm.symbol) as avg_volatility
FROM processed.stock_metrics sm
JOIN latest_dates ld ON sm.symbol = ld.symbol AND sm.date BETWEEN ld.week_start AND ld.latest_date
ORDER BY sm.symbol, ld.week_start;
-- END WEEKLY_REPORT

-- BEGIN MONTHLY_REPORT
SELECT 
    symbol,
    date_trunc('month', date) as month,
    AVG(close) as avg_price,
    MAX(close) as max_price,
    MIN(close) as min_price,
    FIRST_VALUE(close) OVER (PARTITION BY symbol, date_trunc('month', date) ORDER BY date) as month_open,
    LAST_VALUE(close) OVER (PARTITION BY symbol, date_trunc('month', date) ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as month_close,
    (LAST_VALUE(close) OVER (PARTITION BY symbol, date_trunc('month', date) ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) - 
     FIRST_VALUE(close) OVER (PARTITION BY symbol, date_trunc('month', date) ORDER BY date)) / 
     NULLIF(FIRST_VALUE(close) OVER (PARTITION BY symbol, date_trunc('month', date) ORDER BY date), 0) * 100 as monthly_return_pct
FROM processed.stock_metrics
WHERE date >= date_trunc('month', current_date - interval '3 months')
GROUP BY symbol, date_trunc('month', date), date
ORDER BY symbol, month;
-- END MONTHLY_REPORT