import time
import psycopg2
from collector import DataCollector
from processor import ThresholdProcessor

def test_pipeline():
    db_config = {
        'host': 'localhost',
        'database': 'pipeline_db',
        'user': 'pipeline_user',
        'password': 'pipeline_pass',
        'port': 5432
    }
    
    print("=== Pipeline v0 Test ===")
    
    # Test 1: Data Collection
    print("\n1. Testing data collection...")
    collector = DataCollector(db_config)
    try:
        collector.run_batch(batch_size=3)
        print("✓ Data collection completed")
    except Exception as e:
        print(f"✗ Data collection failed: {e}")
        return
    finally:
        collector.close()
    
    # Wait a moment
    time.sleep(1)
    
    # Test 2: Data Processing
    print("\n2. Testing data processing...")
    processor = ThresholdProcessor(db_config, threshold=50.0)
    try:
        processed_count = processor.process_batch()
        print(f"✓ Data processing completed. Processed {processed_count} records")
    except Exception as e:
        print(f"✗ Data processing failed: {e}")
        return
    finally:
        processor.close()
    
    # Test 3: Verify Results
    print("\n3. Verifying results...")
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM input_table WHERE processed = TRUE")
        processed_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT data, predicted, model_used 
            FROM input_table 
            WHERE processed = TRUE 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        results = cursor.fetchall()
        
        print(f"✓ Total processed records: {processed_count}")
        print("✓ Recent predictions:")
        for data, prediction, model in results:
            print(f"   Data: {data:.2f} → Prediction: {prediction} (Model: {model})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Result verification failed: {e}")
        return
    
    print("\n=== Pipeline Test Complete ===")
    print("All components working correctly!")

if __name__ == "__main__":
    test_pipeline()