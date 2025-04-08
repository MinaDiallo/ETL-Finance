-- Fichier: sql/maintenance/indexes.sql

-- Indexes pour raw.stock_prices
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON raw.stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON raw.stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON raw.stock_prices(symbol, date);

-- Indexes pour processed.stock_metrics
CREATE INDEX IF NOT EXISTS idx_stock_metrics_symbol ON processed.stock_metrics(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_metrics_date ON processed.stock_metrics(date);
CREATE INDEX IF NOT EXISTS idx_stock_metrics_symbol_date ON processed.stock_metrics(symbol, date);

-- Indexes pour analytics.financial_kpis
CREATE INDEX IF NOT EXISTS idx_financial_kpis_symbol ON analytics.financial_kpis(symbol);
CREATE INDEX IF NOT EXISTS idx_financial_kpis_date ON analytics.financial_kpis(date);
CREATE INDEX IF NOT EXISTS idx_financial_kpis_sector ON analytics.financial_kpis(sector);
CREATE INDEX IF NOT EXISTS idx_financial_kpis_region ON analytics.financial_kpis(region);
CREATE INDEX IF NOT EXISTS idx_financial_kpis_symbol_date ON analytics.financial_kpis(symbol, date);

-- Index pour recherche par secteur et région
CREATE INDEX IF NOT EXISTS idx_financial_kpis_sector_region ON analytics.financial_kpis(sector, region);

-- Index pour tri par risk_score
CREATE INDEX IF NOT EXISTS idx_financial_kpis_risk_score ON analytics.financial_kpis(risk_score DESC);

-- Index pour tri par profit_margin
CREATE INDEX IF NOT EXISTS idx_financial_kpis_profit_margin ON analytics.financial_kpis(profit_margin DESC);