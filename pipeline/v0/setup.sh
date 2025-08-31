#!/bin/bash

echo "=== Pipeline v0 Setup ==="

# Start PostgreSQL and Redis
echo "Starting database and Redis..."
docker-compose up -d postgres redis

echo "Waiting for PostgreSQL to be ready..."
sleep 10

# Initialize Airflow
echo "Initializing Airflow..."
docker-compose up airflow-init

# Start Airflow services
echo "Starting Airflow services..."
docker-compose up -d airflow-webserver airflow-scheduler airflow-worker

echo "=== Setup Complete ==="
echo "Services available at:"
echo "- PostgreSQL: localhost:5432"
echo "- Airflow UI: http://localhost:8080 (admin/admin)"
echo "- Redis: localhost:6379"
echo ""
echo "To test the pipeline manually:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Run test: python test_pipeline.py"
echo ""
echo "To stop services: docker-compose down"