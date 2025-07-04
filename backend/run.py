#!/usr/bin/env python3
import os
import sys

if __name__ == '__main__':
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found. Please create it from env.example")
        print("cp env.example .env")
        print("Then edit .env with your AWS credentials")
        sys.exit(1)
    
    from app import app
    app.run() 