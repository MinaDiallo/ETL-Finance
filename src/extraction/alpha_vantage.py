import os
import pandas as pd
import requests
import yaml
import logging
from datetime import datetime
from pathlib import Path
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('alpha_vantage_extractor')

class AlphaVantageExtractor:
    """
    Classe pour extraire des données financières via l'API Alpha Vantage
    """
    
    def __init__(self, config_path=None):
        """
        Initialise l'extracteur Alpha Vantage avec la clé API
        
        Args:
            config_path (str, optional): Chemin vers le fichier de configuration. 
                                         Par défaut, utilise config/credentials.yml
        """
        if config_path is None:
            # Chemin par défaut vers le fichier de configuration
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                       'config', 'credentials.yml')
        
        # Charger la clé API depuis le fichier de configuration
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                self.api_key = config['api']['alpha_vantage']['api_key']
                if not self.api_key or self.api_key == "VOTRE_CLE_ALPHA_VANTAGE":
                    logger.warning("Clé API Alpha Vantage non configurée. Veuillez définir votre clé dans config/credentials.yml")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            self.api_key = None
        
        # URL de base de l'API
        self.base_url = "https://www.alphavantage.co/query"
        
        # Dossier de destination pour les données brutes
        self.raw_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                         'data', 'raw', 'alpha_vantage')
        os.makedirs(self.raw_data_dir, exist_ok=True)
    
    def get_daily_adjusted(self, symbol, outputsize="full"):
        """
        Récupère les données quotidiennes ajustées pour un symbole boursier
        
        Args:
            symbol (str): Symbole boursier (ex: AAPL, MSFT)
            outputsize (str, optional): Taille de sortie ('compact' ou 'full'). Par défaut 'full'.
        
        Returns:
            pandas.DataFrame: DataFrame contenant les données historiques
        """
        if not self.api_key:
            logger.error("Clé API Alpha Vantage non configurée")
            return None
        
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self.api_key,
            "datatype": "json"
        }
        print(params, outputsize)
        
        try:
            logger.info(f"Extraction des données quotidiennes pour {symbol}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Lève une exception si la requête a échoué
            
            data = response.json()
            print(data)
            
            # Vérifier si l'API a renvoyé une erreur
            if "Error Message" in data:
                logger.error(f"Erreur API: {data['Error Message']}")
                return None
            
            if "Time Series (Daily)" not in data:
                logger.error(f"Format de données inattendu: {data.keys()}")
                return None
            
            # Convertir les données JSON en DataFrame
            time_series = data["Time Series (Daily)"]
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Renommer les colonnes pour plus de clarté
            df.rename(columns={
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close',
                '5. adjusted close': 'adjusted_close',
                '6. volume': 'volume',
                '7. dividend amount': 'dividend',
                '8. split coefficient': 'split_coefficient'
            }, inplace=True)
            
            # Convertir les types de données
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
            
            # Ajouter le symbole comme colonne
            df['symbol'] = symbol
            
            # Convertir l'index en colonne de date
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'date'}, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            
            # Sauvegarder les données brutes
            self._save_raw_data(df, symbol, 'daily_adjusted')
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return None
    
    def get_company_overview(self, symbol):
        """
        Récupère les informations générales sur une entreprise
        
        Args:
            symbol (str): Symbole boursier (ex: AAPL, MSFT)
        
        Returns:
            pandas.DataFrame: DataFrame contenant les informations de l'entreprise
        """
        if not self.api_key:
            logger.error("Clé API Alpha Vantage non configurée")
            return None
        
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            logger.info(f"Extraction des informations de l'entreprise pour {symbol}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Vérifier si l'API a renvoyé une erreur ou un résultat vide
            if "Error Message" in data or not data:
                logger.error(f"Erreur API ou données vides pour {symbol}")
                return None
            
            # Convertir en DataFrame
            df = pd.DataFrame([data])
            
            # Sauvegarder les données brutes
            self._save_raw_data(df, symbol, 'company_overview')
            time.sleep(15)
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return None
    
    def _save_raw_data(self, df, symbol, data_type):
        """
        Sauvegarde les données brutes au format CSV
        
        Args:
            df (pandas.DataFrame): DataFrame à sauvegarder
            symbol (str): Symbole boursier
            data_type (str): Type de données ('daily_adjusted', 'company_overview', etc.)
        """
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

# Exemple d'utilisation
if __name__ == "__main__":
    extractor = AlphaVantageExtractor()
    # Extraire les données quotidiennes pour Apple et Miscrosoft
    apple_data = extractor.get_daily_adjusted("AAPL", outputsize="compact")
    

    time.sleep(15)
    #msft_data = extractor.get_daily_adjusted("MSFT", outputsize="compact")

    if apple_data is not None:
        print(apple_data.head())
    
    # Extraire les informations de l'entreprise pour Microsoft
    #aapl_overview = extractor.get_company_overview("AAPL")
    #ms_overview = extractor.get_company_overview("MSFT")
    
    #if ms_overview is not None:
     #   print(ms_overview)