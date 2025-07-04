#!/bin/bash

echo "🚀 Setting up English AI Agent Frontend Development Environment"
echo "============================================================"

echo "📦 Installing dependencies..."
npm install

echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
    echo "⚠️  Please update the environment variables in .env file"
else
    echo "✅ .env file already exists"
fi

echo "🎨 Setting up Tailwind CSS..."
npx tailwindcss init -p

echo "🧪 Running initial build test..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
else
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the development server:"
echo "  npm start"
echo ""
echo "To build for production:"
echo "  npm run build"
echo ""
echo "Don't forget to:"
echo "  1. Update environment variables in .env"
echo "  2. Configure your backend API endpoints"
echo "  3. Set up AWS credentials for production"
echo "" 