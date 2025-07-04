#!/bin/bash

echo "🚀 Starting Bedrock Agent Application..."

if [ ! -f "backend/.env" ]; then
    echo "⚠️  Backend .env file not found. Please copy backend/env.example to backend/.env and configure your AWS credentials."
    exit 1
fi

echo "📦 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "🌍 Setting up environment variables..."
export $(cat .env | grep -v '^#' | xargs)

echo "🔧 Starting backend server..."
python app.py &
BACKEND_PID=$!

cd ../frontend

echo "📦 Installing frontend dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "🎨 Starting frontend development server..."
npm start &
FRONTEND_PID=$!

echo "✅ Application started successfully!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "🤖 Agent Chat: http://localhost:3000/agent-chat"
echo ""
echo "Press Ctrl+C to stop all services"

wait $BACKEND_PID $FRONTEND_PID 