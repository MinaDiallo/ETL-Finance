import os
import pandas as pd
import yfinance as yf
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('yahoo_finance_extractor')

class YahooFinanceExtractor:
    """
    Classe pour extraire des données financières via Yahoo Finance (yfinance)
    """
    
    def __init__(self):
        """
        Initialise l'extracteur Yahoo Finance
        """
        # Dossier de destination pour les données brutes
        self.raw_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                         'data', 'raw', 'yahoo_finance')
        os.makedirs(self.raw_data_dir, exist_ok=True)
    
    def get_historical_data(self, symbol, period="max", interval="1d"):
        """
        Récupère les données historiques pour un symbole boursier
        
        Args:
            symbol (str): Symbole boursier (ex: AAPL, MSFT)
            period (str, optional): Période ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval (str, optional): Intervalle ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            pandas.DataFrame: DataFrame contenant les données historiques
        """
        try:
            logger.info(f"Extraction des données historiques pour {symbol} (période: {period}, intervalle: {interval})")
            
            # Télécharger les données historiques
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            # Vérifier si des données ont été récupérées
            if df.empty:
                logger.warning(f"Aucune donnée récupérée pour {symbol}")
                return None
            
            # Réinitialiser l'index pour avoir la date comme colonne
            df.reset_index(inplace=True)
            
            # Ajouter le symbole comme colonne
            df['Symbol'] = symbol
            
            # Renommer les colonnes pour plus de clarté
            df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Dividends': 'dividends',
                'Stock Splits': 'stock_splits',
                'Symbol': 'symbol'
            }, inplace=True)
            
            # Sauvegarder les données brutes
            self._save_raw_data(df, symbol, f"historical_{period}_{interval}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données pour {symbol}: {e}")
            return None
    
    def get_company_info(self, symbol):
        """
        Récupère les informations générales sur une entreprise
        
        Args:
            symbol (str): Symbole boursier (ex: AAPL, MSFT)
        
        Returns:
            dict: Dictionnaire contenant les informations de l'entreprise
        """
        try:
            logger.info(f"Extraction des informations de l'entreprise pour {symbol}")
            
            # Récupérer les informations de l'entreprise
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Convertir en DataFrame pour la sauvegarde
            df = pd.DataFrame([info])
            
            # Sauvegarder les données brutes
            self._save_raw_data(df, symbol, "company_info")
            
            return info
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des informations pour {symbol}: {e}")
            return None
    
    def get_financials(self, symbol):
        """
        Récupère les données financières d'une entreprise
        
        Args:
            symbol (str): Symbole boursier (ex: AAPL, MSFT)
        
        Returns:
            dict: Dictionnaire contenant les différents états financiers
        """
        try:
            logger.info(f"Extraction des données financières pour {symbol}")
            
            # Récupérer les données financières
            ticker = yf.Ticker(symbol)
            
            # Récupérer les différents états financiers
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            # Sauvegarder les données brutes
            if not income_stmt.empty:
                self._save_raw_data(income_stmt.reset_index(), symbol, "income_statement")
            
            if not balance_sheet.empty:
                self._save_raw_data(balance_sheet.reset_index(), symbol, "balance_sheet")
            
            if not cash_flow.empty:
                self._save_raw_data(cash_flow.reset_index(), symbol, "cash_flow")
            
            return {
                'income_statement': income_stmt,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données financières pour {symbol}: {e}")
            return None
    
    def _save_raw_data(self, df, symbol, data_type):
    
        try:
            # Créer un nom de fichier avec horodatage
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{data_type}_{timestamp}.csv"
            filepath = os.path.join(self.raw_data_dir, filename)
            
            # Sauvegarder en CSV
            df.to_csv(filepath, index=False)
            logger.info(f"Données sauvegardées dans {filepath}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données: {e}")
    
    def get_multiple_tickers_data(self, symbols, start_date=None, end_date=None):
        """
        Récupère les données historiques pour plusieurs symboles boursiers
        
        Args:
            symbols (list): Liste des symboles boursiers
            start_date (str, optional): Date de début au format 'YYYY-MM-DD'
            end_date (str, optional): Date de fin au format 'YYYY-MM-DD'
        
        Returns:
            pandas.DataFrame: DataFrame contenant les données historiques pour tous les symboles
            """
        try:
            logger.info(f"Extraction des données pour plusieurs symboles: {symbols}")
            
            # Vérifier si les dates sont spécifiées
            if start_date is None or end_date is None:
                # Si les dates ne sont pas spécifiées, utiliser yfinance avec period
                data = yf.download(
                    tickers=symbols,
                    period="1y",  # Par défaut, récupérer les données de la dernière année
                    group_by='ticker',
                    auto_adjust=True,
                    threads=True
                )
            else:
                # Si les dates sont spécifiées, les utiliser
                data = yf.download(
                    tickers=symbols,
                    start=start_date,
                    end=end_date,
                    group_by='ticker',
                    auto_adjust=True,
                    threads=True
                )
            
            # Vérifier si des données ont été récupérées
            if data.empty:
                logger.warning(f"Aucune donnée récupérée pour les symboles {symbols}")
                return None
            
            # Traitement des données pour un seul symbole (cas particulier)
            if len(symbols) == 1:
                symbol = symbols[0]
                data['Symbol'] = symbol
                df = data.reset_index()
                
                # Renommer les colonnes
                df.rename(columns={
                    'Date': 'date',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume',
                    'Symbol': 'symbol'
                }, inplace=True)
                
                # Sauvegarder les données brutes
                self._save_raw_data(df, symbol, "historical_multiple")
                return df
            
            # Traitement pour plusieurs symboles
            all_data = []
            
            for symbol in symbols:
                if symbol in data.columns.levels[0]:
                    # Extraire les données pour ce symbole
                    symbol_data = data[symbol].copy()
                    symbol_data['symbol'] = symbol
                    symbol_data = symbol_data.reset_index()
                    
                    # Renommer les colonnes
                    symbol_data.rename(columns={
                        'Date': 'date',
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    }, inplace=True)
                    
                    all_data.append(symbol_data)
        
            if not all_data:
                logger.warning("Aucune donnée valide récupérée")
                return None
            
            # Combiner tous les DataFrames
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Sauvegarder les données brutes
            symbols_str = "_".join(symbols)
            self._save_raw_data(combined_df, symbols_str, "historical_multiple")
            
            return combined_df
        
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données pour plusieurs symboles: {e}")
            return None
            
# Exemple d'utilisation
if __name__ == "__main__":
    extractor = YahooFinanceExtractor()
    
    # Extraire les données historiques pour Apple
    apple_data = extractor.get_historical_data("AAPL", period="1y", interval="1d")
    if apple_data is not None:
        print(f"Données historiques pour AAPL: {len(apple_data)} entrées")
        print(apple_data.head())
    
    # Extraire les informations de l'entreprise pour Microsoft
    msft_info = extractor.get_company_info("MSFT")
    if msft_info is not None:
        print(f"Informations sur MSFT récupérées")
    
    # Extraire les données financières pour Google
    googl_financials = extractor.get_financials("GOOGL")
    if googl_financials is not None:
        print("États financiers pour GOOGL récupérés")
    
    # Extraire les données pour plusieurs symboles
    multi_data = extractor.get_multiple_tickers_data(
        ["AAPL", "MSFT", "GOOGL"], 
        start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        end_date=datetime.now().strftime("%Y-%m-%d")
    )
    if multi_data is not None:
        print(f"Données multi-symboles récupérées")