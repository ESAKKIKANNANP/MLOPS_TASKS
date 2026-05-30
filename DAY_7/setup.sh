#!/bin/bash

# Violence Detection AI - Quick Start Setup Script
# This script sets up the complete environment for development

echo "🚀 Violence Detection AI System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "  Found: $python_version"
else
    echo "✗ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
echo "  Virtual environment activated"

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -r requirements.txt
if [[ $? -eq 0 ]]; then
    echo "  Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Create .env file
echo ""
echo "✓ Creating environment configuration..."
if [[ ! -f ".env" ]]; then
    cp .env.example .env
    echo "  .env file created (update with your settings)"
else
    echo "  .env file already exists"
fi

# Create logs directory
echo ""
echo "✓ Setting up logging directory..."
mkdir -p logs
chmod 755 logs
echo "  Logs directory ready"

# Check for model
echo ""
echo "✓ Checking for trained model..."
if [[ -f "runs/detect/mall_yolov8/weights/best.pt" ]]; then
    echo "  ✓ Trained model found"
else
    echo "  ⚠ Trained model not found"
    echo "    The system will use pretrained YOLOv8n model"
    echo "    To use your trained model, place it at:"
    echo "    runs/detect/mall_yolov8/weights/best.pt"
fi

echo ""
echo "=========================================="
echo "✨ Setup completed successfully!"
echo ""
echo "📝 Demo Credentials:"
echo "  Username: admin / user"
echo "  Password: admin123 / user123"
echo ""
echo "🚀 To start the application:"
echo "  python app.py"
echo ""
echo "🌐 Open your browser and navigate to:"
echo "  http://localhost:5000"
echo ""
echo "📖 For more information, see README.md"
echo "=========================================="
