import random
import time
import psycopg2
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
    
    def connect_db(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def generate_data(self):
        return random.uniform(0, 100)
    
    def insert_data(self, data_value):
        if not self.connection:
            self.connect_db()
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO input_table (created_at, data, processed) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (datetime.now(), data_value, False))
            self.connection.commit()
            cursor.close()
            logger.info(f"Inserted data: {data_value}")
        except Exception as e:
            logger.error(f"Data insertion failed: {e}")
            self.connection.rollback()
            raise
    
    def run_batch(self, batch_size=10):
        for i in range(batch_size):
            data_value = self.generate_data()
            self.insert_data(data_value)
            time.sleep(1)
    
    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

def main():
    db_config = {
        'host': 'localhost',
        'database': 'pipeline_db',
        'user': 'pipeline_user',
        'password': 'pipeline_pass',
        'port': 5432
    }
    
    collector = DataCollector(db_config)
    
    try:
        collector.run_batch(batch_size=5)
    finally:
        collector.close()

if __name__ == "__main__":
    main()