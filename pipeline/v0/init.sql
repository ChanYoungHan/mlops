-- Database initialization script for pipeline v0

-- Create input_table for data collection and processing
CREATE TABLE IF NOT EXISTS input_table (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data FLOAT NOT NULL,
    predicted VARCHAR(10),
    model_used VARCHAR(50),
    processed BOOLEAN DEFAULT FALSE
);

-- Create index on processed column for efficient queries
CREATE INDEX IF NOT EXISTS idx_input_table_processed ON input_table(processed);

-- Create index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_input_table_created_at ON input_table(created_at);

-- Insert some sample data for testing
INSERT INTO input_table (data, processed) VALUES 
(25.5, FALSE),
(78.2, FALSE),
(45.1, FALSE),
(92.8, FALSE),
(15.3, FALSE);

-- Display table structure
\d input_table;

-- Show initial data
SELECT * FROM input_table;