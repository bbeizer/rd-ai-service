#!/bin/bash

echo "🚀 Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

echo "✅ Virtual environment activated!"

echo "⚡ Running Flask server..."
python server.py