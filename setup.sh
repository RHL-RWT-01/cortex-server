#!/bin/bash

# Cortex Server Setup Script

echo "🚀 Setting up Cortex Server..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your credentials!"
    echo ""
    echo "Required:"
    echo "  - MONGODB_URL (MongoDB Atlas connection string)"
    echo "  - GEMINI_API_KEY (Google Gemini API key)"
    echo "  - SECRET_KEY (Random secure string for JWT)"
    echo ""
else
    echo "✓ .env file found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update .env file with your credentials"
echo "  2. Run: python seed_data.py (to populate initial data)"
echo "  3. Run: python main.py (to start the server)"
echo ""
echo "Documentation: http://localhost:8000/docs"
