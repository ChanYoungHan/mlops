import psycopg2
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThresholdProcessor:
    def __init__(self, db_config, threshold=50.0):
        self.db_config = db_config
        self.threshold = threshold
        self.model_name = "threshold_v0"
        self.connection = None
    
    def connect_db(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def predict(self, data_value):
        return "HIGH" if data_value >= self.threshold else "LOW"
    
    def get_unprocessed_data(self):
        if not self.connection:
            self.connect_db()
        
        try:
            cursor = self.connection.cursor()
            query = "SELECT id, data FROM input_table WHERE processed = FALSE"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Failed to fetch unprocessed data: {e}")
            raise
    
    def update_prediction(self, record_id, data_value, prediction):
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE input_table 
                SET predicted = %s, model_used = %s, processed = TRUE 
                WHERE id = %s
            """
            cursor.execute(query, (prediction, self.model_name, record_id))
            self.connection.commit()
            cursor.close()
            logger.info(f"Updated record {record_id}: data={data_value}, prediction={prediction}")
        except Exception as e:
            logger.error(f"Failed to update prediction for record {record_id}: {e}")
            self.connection.rollback()
            raise
    
    def process_batch(self):
        unprocessed_records = self.get_unprocessed_data()
        
        if not unprocessed_records:
            logger.info("No unprocessed records found")
            return 0
        
        processed_count = 0
        for record_id, data_value in unprocessed_records:
            prediction = self.predict(data_value)
            self.update_prediction(record_id, data_value, prediction)
            processed_count += 1
        
        logger.info(f"Processed {processed_count} records")
        return processed_count
    
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
    
    processor = ThresholdProcessor(db_config, threshold=50.0)
    
    try:
        processor.process_batch()
    finally:
        processor.close()

if __name__ == "__main__":
    main()