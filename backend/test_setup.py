# test_setup.py - Run this to test your setup
# Place this in backend/ directory

import sys
import importlib.util

def check_package(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return False
    return True

def main():
    print("🔍 Checking Python environment setup...\n")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print("-" * 50)
    
    # Packages to check
    packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("dotenv", "python-dotenv"),
        ("pydantic", "Pydantic"),
        ("google.generativeai", "Google Generative AI"),
    ]
    
    all_installed = True
    
    for package, display_name in packages:
        if check_package(package):
            print(f"✅ {display_name} is installed")
        else:
            print(f"❌ {display_name} is NOT installed")
            all_installed = False
    
    print("-" * 50)
    
    if all_installed:
        print("\n🎉 All packages are installed! You're ready to go!")
        print("\nNext steps:")
        print("1. Add your Gemini API key to .env file")
        print("2. Run: python -m uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Some packages are missing!")
        print("Try running: conda env create -f environment.yml")
        print("Then: conda activate story-generator")
    
    # Try to load config (this will fail if .env is not set up)
    print("\n📋 Checking configuration...")
    try:
        from app.config import settings
        print(f"✅ Config loaded: {settings.app_name}")
        if settings.gemini_api_key == "your_api_key_here":
            print("⚠️  Please add your actual Gemini API key to .env file")
        else:
            print("✅ Gemini API key is configured")
    except Exception as e:
        print(f"⚠️  Could not load config: {e}")
        print("   Make sure app/config.py exists and .env is set up")

if __name__ == "__main__":
    main()