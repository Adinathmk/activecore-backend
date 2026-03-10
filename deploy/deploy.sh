#!/bin/bash

set -e

cd /home/ubuntu/activecore-backend

echo "Pulling latest code..."
git pull origin main

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Restarting Daphne..."
sudo systemctl restart daphne

echo "Deployment finished."