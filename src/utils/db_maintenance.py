import os
import logging
from src.utils.db_connection import DatabaseConnector

logger = logging.getLogger(__name__)

class DatabaseMaintenance:
    def __init__(self):
        self.db = DatabaseConnector()
        self.conn = None
        self.sql_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sql')
    
    def connect(self):
        """Établit une connexion à la base de données"""
        self.conn = self.db.connect()
        return self.conn
    
    def close(self):
        """Ferme la connexion à la base de données"""
        self.db.close()
    
    def create_indexes(self):
        """Crée les index définis dans le fichier indexes.sql"""
        try:
            if self.conn is None:
                self.connect()
            
            indexes_sql_path = os.path.join(self.sql_dir, 'maintenance', 'indexes.sql')
            
            with open(indexes_sql_path, 'r') as f:
                indexes_sql = f.read()
            
            # Exécuter la création d'index
            with self.conn.cursor() as cursor:
                cursor.execute(indexes_sql)
                self.conn.commit()
            
            logger.info("Successfully created database indexes")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")
            if self.conn:
                self.conn.rollback()
                
def cleanup_database(self):
  try:
    if self.conn is None:
      self.connect()
        
      cleanup_sql_path = os.path.join(self.sql_dir, 'maintenance', 'cleanup.sql')
        
      with open(cleanup_sql_path, 'r') as f:
            cleanup_sql = f.read()
        
      # Exécuter les opérations de nettoyage
      with self.conn.cursor() as cursor:
        cursor.execute(cleanup_sql)
        self.conn.commit()
        
        logger.info("Successfully cleaned up database")
        return True
        
  except Exception as e:
    logger.error(f"Error cleaning up database: {e}")
    if self.conn:
      self.conn.rollback()
      return False
                
    