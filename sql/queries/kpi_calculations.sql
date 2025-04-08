-- Calcul des KPIs financiers
-- Ce script est exécuté périodiquement pour mettre à jour les KPIs

-- Mise à jour des indicateurs de volatilité
INSERT INTO analytics.financial_kpis (symbol, sector, region, date, revenue, profit_margin, risk_score)
SELECT 
    s.symbol,
    COALESCE(c.sector, 'Unknown') as sector,
    COALESCE(c.region, 'Global') as region,
    s.date,
    NULL as revenue, -- À remplir avec des données réelles
    NULL as profit_margin, -- À remplir avec des données réelles
    s.volatility as risk_score
FROM processed.stock_metrics s
LEFT JOIN (
    -- Sous-requête simulant une table de classification des entreprises
    VALUES 
        ('AAPL', 'Technology', 'US'),
        ('MSFT', 'Technology', 'US'),
        ('GOOGL', 'Technology', 'US'),
        ('AMZN', 'Retail', 'US')
) as c(symbol, sector, region) ON s.symbol = c.symbol
WHERE NOT EXISTS (
    SELECT 1 FROM analytics.financial_kpis k
    WHERE k.symbol = s.symbol AND k.date = s.date
);

-- Calcul des moyennes mobiles pour les symboles qui n'en ont pas encore
UPDATE processed.stock_metrics sm
SET 
    ma_20 = subquery.ma_20,
    ma_50 = subquery.ma_50,
    ma_200 = subquery.ma_200
FROM (
    SELECT 
        symbol,
        date,
        AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as ma_20,
        AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as ma_50,
        AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) as ma_200
    FROM raw.stock_prices
) as subquery
WHERE sm.symbol = subquery.symbol 
  AND sm.date = subquery.date
  AND (sm.ma_20 IS NULL OR sm.ma_50 IS NULL OR sm.ma_200 IS NULL);