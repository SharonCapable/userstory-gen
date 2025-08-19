#!/bin/bash

# setup_conda.sh - Setup script for Conda users

echo "🚀 Setting up User Story Generator with Conda..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    exit 1
fi

echo "✅ Conda found!"

# Create project structure
echo "📁 Creating project structure..."
mkdir -p user-story-generator/backend/app/{models,api,services,schemas}
mkdir -p user-story-generator/frontend

cd user-story-generator/backend

# Create __init__.py files
touch app/__init__.py
touch app/models/__init__.py
touch app/api/__init__.py
touch app/services/__init__.py
touch app/schemas/__init__.py

# Create environment.yml
echo "📝 Creating environment.yml..."
cat > environment.yml << 'EOL'
name: story-generator
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - pip:
    - fastapi==0.104.1
    - uvicorn[standard]==0.24.0
    - sqlalchemy==2.0.23
    - python-dotenv==1.0.0
    - pydantic==2.5.0
    - pydantic-settings==2.1.0
    - google-generativeai==0.3.0
    - python-multipart==0.0.6
EOL

# Create requirements.txt as backup
echo "📝 Creating requirements.txt..."
cat > requirements.txt << 'EOL'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
google-generativeai==0.3.0
python-multipart==0.0.6
EOL

# Create .env template
echo "📝 Creating .env template..."
cat > .env << 'EOL'
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///./user_stories.db
EOL

# Create conda environment
echo "🔧 Creating Conda environment..."
conda env create -f environment.yml -y

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. cd user-story-generator/backend"
echo "2. conda activate story-generator"
echo "3. Add your Gemini API key to the .env file"
echo "4. Copy the Python files from the artifacts above into their respective locations"
echo "5. Run: python -m uvicorn app.main:app --reload"
echo ""
echo "💡 To test if everything works:"
echo "   - API endpoint: http://localhost:8000"
echo "   - Gemini test: http://localhost:8000/api/test-gemini"