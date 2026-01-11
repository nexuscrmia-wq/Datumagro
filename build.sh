#!/usr/bin/env bash
# Build script for Render.com deployment
# This script runs during the build phase on Render

set -o errexit

echo "🔧 Starting build process for DatumAgro..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!"