#!/bin/bash
# Setup script for local development

set -e

echo "🚀 Setting up Eloquent Transformers..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install it first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "📦 Installing dependencies..."
poetry install

# Create directories
echo "📁 Creating storage directories..."
mkdir -p storage/audio storage/chroma models

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
poetry run pre-commit install

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update .env with your configuration"
echo "  2. Start services: docker-compose up -d"
echo "  3. Run migrations: poetry run alembic upgrade head"
echo "  4. Start API: poetry run uvicorn src.presentation.api.main:app --reload"
echo ""
echo "Access the API at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
