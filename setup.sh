#!/bin/bash

# Set the FLASK_APP environment variable to the correct location
export FLASK_APP=src.app

# Run database setup and Flyway migrations
python3 ./scripts/database.py

echo "Running Flyway clean..."
python3 ./scripts/flyway.py clean

echo "Running Flyway migrate..."
python3 ./scripts/flyway.py migrate

# Start Flask app
echo "Starting Flask app..."
flask run --host=0.0.0.0 --port=8080