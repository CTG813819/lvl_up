#!/bin/bash

echo "🗄️ Running database initialization on EC2..."

cd /home/ubuntu/ai-backend-python

# Run the database initialization
python3 create_tables.py

echo "✅ Database initialization completed!" 