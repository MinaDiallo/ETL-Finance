-- Opérations de nettoyage et maintenance
-- Fichier: sql/maintenance/cleanup.sql

-- Supprimer les données trop anciennes (plus de 2 ans)
DELETE FROM raw.stock_prices WHERE date < CURRENT_DATE - INTERVAL '2 years';

-- Supprimer les doublons potentiels dans les données brutes
DELETE FROM raw.stock_prices
WHERE id IN (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY symbol, date ORDER BY id) as row_num
        FROM raw.stock_prices
    ) t
    WHERE t.row_num > 1
);

-- Vacuum pour récupérer l'espace disque et optimiser les tables
VACUUM ANALYZE raw.stock_prices;
VACUUM ANALYZE processed.stock_metrics;
VACUUM ANALYZE analytics.financial_kpis;










