import yaml
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

class DatabaseConnector:
    def __init__(self, config_path='config/db_config.yml', env='development'):
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.config = self._load_config(config_path, env)
        
    def _load_config(self, config_path, env):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                db_config = config['database']['postgres']
                env_config = config['environments'][env]
                return {**db_config, **env_config}
        except Exception as e:
            self.logger.error(f"Error loading database configuration: {e}")
            raise
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['username'],
                password=self.config['password']
            )
            self.logger.info("Database connection established")
            return self.connection
        except Exception as e:
            self.logger.error(f"Error connecting to database: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=True):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                self.connection.commit()
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            self.connection.rollback()
            raise
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")