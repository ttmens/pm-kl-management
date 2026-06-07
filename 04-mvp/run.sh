#!/bin/bash
set -e

echo "=== 产品知识平台 MVP ==="
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Initialize database
echo "Initializing database..."
python -c "import models; models.init_db()"

# Seed data
echo "Seeding database..."
python seed_data.py

# Start server
echo "Starting server..."
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
