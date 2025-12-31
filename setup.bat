@echo off
REM Cortex Server Setup Script for Windows

echo 🚀 Setting up Cortex Server...

REM Check Python version
python --version
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.9+
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo ⚠️  .env file not found. Copying from .env.example...
    copy .env.example .env
    echo ⚠️  Please update .env with your credentials!
    echo.
    echo Required:
    echo   - MONGODB_URL (MongoDB Atlas connection string^)
    echo   - GEMINI_API_KEY (Google Gemini API key^)
    echo   - SECRET_KEY (Random secure string for JWT^)
    echo.
) else (
    echo ✓ .env file found
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo   1. Update .env file with your credentials
echo   2. Run: python seed_data.py (to populate initial data^)
echo   3. Run: python main.py (to start the server^)
echo.
echo Documentation: http://localhost:8000/docs

pause
