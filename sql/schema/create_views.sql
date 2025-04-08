-- Création des vues pour analyses financières
-- Fichier: sql/schema/create_views.sql

-- Vue pour l'analyse des tendances de prix
CREATE OR REPLACE VIEW analytics.price_trends AS
SELECT 
    symbol,
    date,
    close,
    LAG(close, 1) OVER (PARTITION BY symbol ORDER BY date) AS prev_day_close,
    (close - LAG(close, 1) OVER (PARTITION BY symbol ORDER BY date)) / 
        NULLIF(LAG(close, 1) OVER (PARTITION BY symbol ORDER BY date), 0) * 100 AS daily_return_pct,
    AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS ma_20,
    AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS ma_50,
    AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS ma_200
FROM raw.stock_prices;

-- Vue pour les signaux de trading
CREATE OR REPLACE VIEW analytics.trading_signals AS
SELECT 
    symbol,
    date,
    close,
    ma_20,
    ma_50,
    ma_200,
    CASE 
        WHEN ma_20 > ma_50 AND LAG(ma_20, 1) OVER (PARTITION BY symbol ORDER BY date) <= LAG(ma_50, 1) OVER (PARTITION BY symbol ORDER BY date) 
        THEN 'GOLDEN_CROSS'
        WHEN ma_20 < ma_50 AND LAG(ma_20, 1) OVER (PARTITION BY symbol ORDER BY date) >= LAG(ma_50, 1) OVER (PARTITION BY symbol ORDER BY date) 
        THEN 'DEATH_CROSS'
        WHEN ma_20 > ma_50 THEN 'BULLISH'
        WHEN ma_20 < ma_50 THEN 'BEARISH'
        ELSE 'NEUTRAL'
    END AS trend_signal,
    CASE 
        WHEN close > ma_200 THEN 'ABOVE_200MA'
        ELSE 'BELOW_200MA'
    END AS long_term_trend
FROM analytics.price_trends;

-- Vue pour l'analyse de la volatilité
CREATE OR REPLACE VIEW analytics.volatility_analysis AS
SELECT 
    symbol,
    date,
    close,
    daily_return_pct,
    STDDEV(daily_return_pct) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS volatility_20d,
    STDDEV(daily_return_pct) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS volatility_60d,
    AVG(ABS(daily_return_pct)) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS avg_daily_movement
FROM analytics.price_trends;

-- Vue pour le tableau de bord des KPIs financiers
CREATE OR REPLACE VIEW analytics.financial_dashboard AS
SELECT 
    k.symbol,
    k.sector,
    k.region,
    k.date,
    k.revenue,
    k.profit_margin,
    k.risk_score,
    t.trend_signal,
    t.long_term_trend,
    v.volatility_20d,
    v.avg_daily_movement,
    RANK() OVER (PARTITION BY k.sector ORDER BY k.profit_margin DESC) AS sector_rank,
    PERCENT_RANK() OVER (ORDER BY v.volatility_20d) AS volatility_percentile
FROM analytics.financial_kpis k
JOIN analytics.trading_signals t ON k.symbol = t.symbol AND k.date = t.date
JOIN analytics.volatility_analysis v ON k.symbol = v.symbol AND k.date = v.date
WHERE k.date = (SELECT MAX(date) FROM analytics.financial_kpis);

-- Vue pour l'analyse comparative sectorielle
CREATE OR REPLACE VIEW analytics.sector_comparison AS
SELECT 
    sector,
    date,
    COUNT(DISTINCT symbol) AS num_companies,
    AVG(revenue) AS avg_revenue,
    AVG(profit_margin) AS avg_profit_margin,
    AVG(risk_score) AS avg_risk_score,
    STDDEV(profit_margin) AS profit_margin_dispersion
FROM analytics.financial_kpis
GROUP BY sector, date
ORDER BY date DESC, avg_profit_margin DESC;