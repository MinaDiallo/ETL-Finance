-- Création des schémas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS processed;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Tables pour les données brutes (raw)
CREATE TABLE IF NOT EXISTS raw.stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tables pour les données transformées (processed)
CREATE TABLE IF NOT EXISTS processed.stock_metrics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    close NUMERIC,
    ma_20 NUMERIC,
    ma_50 NUMERIC,
    ma_200 NUMERIC,
    rsi NUMERIC,
    volatility NUMERIC,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tables pour les données analytiques (analytics)
CREATE TABLE IF NOT EXISTS analytics.financial_kpis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    sector VARCHAR(100),
    region VARCHAR(50),
    date DATE NOT NULL,
    revenue NUMERIC,
    profit_margin NUMERIC,
    risk_score NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);